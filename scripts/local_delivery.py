"""Isolated local-channel rehearsal; not a production deployment adapter."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import os
import re
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
import zipfile
from contextlib import contextmanager, suppress
from datetime import UTC, datetime
from http.server import ThreadingHTTPServer
from pathlib import Path

from scripts.documentation_check import read_json

FILES = {
    "server.py": "tests/fixtures/domain-reference/server.py",
    "index.html": "tests/fixtures/domain-reference/index.html",
}
LIMIT = 256 * 1024


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build(repository: Path, source: str, output: Path) -> dict:
    if not re.fullmatch(r"[a-f0-9]{40}", source):
        raise ValueError("full approved source commit required")
    kind = subprocess.run(
        ["git", "cat-file", "-t", source],
        cwd=repository,
        capture_output=True,
        text=True,
        check=True,
        timeout=5,
    ).stdout.strip()
    if kind != "commit":
        raise ValueError("source must be a commit")
    began = datetime.now(UTC).isoformat()
    contents = {
        name: subprocess.run(
            ["git", "show", f"{source}:{path}"],
            cwd=repository,
            capture_output=True,
            check=True,
            timeout=5,
        ).stdout
        for name, path in FILES.items()
    }
    if sum(map(len, contents.values())) > LIMIT:
        raise ValueError("reference artifact too large")
    compile(contents["server.py"], "server.py", "exec")
    manifest = {
        "schema_version": 1,
        "source_version": source,
        "files": {name: sha(data) for name, data in contents.items()},
        "python": list(sys.version_info[:2]),
        "dependencies": "Python standard library",
        "scope": "isolated loopback backend/Web reference",
    }
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as package:
        for name, data in sorted(
            contents.items()
            | {"manifest.json": json.dumps(manifest, sort_keys=True).encode()}.items()
        ):
            info = zipfile.ZipInfo(name)
            info.external_attr = 0o100644 << 16
            package.writestr(info, data)
    payload = archive.getvalue()
    artifact_sha = sha(payload)
    output.mkdir(parents=True, exist_ok=True)
    path = output / f"{artifact_sha}.zip"
    if path.exists():
        if path.is_symlink() or path.read_bytes() != payload:
            raise ValueError("immutable artifact changed")
    else:
        with path.open("xb") as handle:
            handle.write(payload)
    return {
        "artifact": str(path.resolve()),
        "sha256": artifact_sha,
        "manifest": manifest,
        "started_at": began,
        "finished_at": datetime.now(UTC).isoformat(),
        "tool": sys.version,
        "validation": "actual Python compile; fixed committed files",
        "retention": "caller retains local evidence; no expiry cleanup task configured",
    }


def unpack(artifact: Path, expected: str, destination: Path) -> dict:
    if artifact.is_symlink() or artifact.stat().st_size > LIMIT + 8192:
        raise ValueError("invalid artifact path or size")
    payload = artifact.read_bytes()
    if not re.fullmatch(r"[a-f0-9]{64}", expected) or sha(payload) != expected:
        raise ValueError("artifact digest mismatch")
    with zipfile.ZipFile(io.BytesIO(payload)) as package:
        if sorted(package.namelist()) != ["index.html", "manifest.json", "server.py"]:
            raise ValueError("unexpected, duplicate or traversing artifact members")
        if sum(i.file_size for i in package.infolist()) > LIMIT:
            raise ValueError("expanded artifact too large")
        manifest = json.loads(package.read("manifest.json"))
        if (
            type(manifest.get("schema_version")) is not int
            or manifest["schema_version"] != 1
            or manifest.get("python") != list(sys.version_info[:2])
            or not re.fullmatch(r"[a-f0-9]{40}", manifest.get("source_version", ""))
            or set(manifest.get("files", {})) != set(FILES)
        ):
            raise ValueError("unsupported artifact manifest/runtime")
        contents = {name: package.read(name) for name in FILES}
        if any(sha(data) != manifest["files"][name] for name, data in contents.items()):
            raise ValueError("manifest file digest mismatch")
    destination.mkdir(exist_ok=False)
    for name, data in contents.items():
        with (destination / name).open("xb") as handle:
            handle.write(data)
    return manifest


def serve(artifact: Path, expected: str, run: Path, config_path: Path) -> None:
    config = read_json(config_path)
    if (
        config["owner_uid"] != os.getuid()
        or config["role"] not in {"backend", "web"}
        or not re.fullmatch(r"local-[a-f0-9]{32}", config["target_id"])
        or not re.fullmatch(r"[a-f0-9]{32}", config["nonce"])
        or type(config["unhealthy"]) is not bool
        or not isinstance(config["health_delay"], (int, float))
        or isinstance(config["health_delay"], bool)
        or not 0 <= config["health_delay"] <= 0.5
        or config.get("runtime_sha256") != sha(Path(__file__).read_bytes())
    ):
        raise ValueError("invalid local identity or fault configuration")
    manifest = unpack(artifact, expected, run / "application")
    spec = importlib.util.spec_from_file_location(
        "reference_application", run / "application/server.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    identity = {
        "target_id": config["target_id"],
        "role": config["role"],
        "artifact_sha256": expected,
        "source_version": manifest["source_version"],
        "owner_uid": os.getuid(),
        "nonce": config["nonce"],
        "pid": os.getpid(),
        "runtime_sha256": config["runtime_sha256"],
    }

    class Handler(module.Handler):
        def do_GET(self) -> None:
            if self.path == "/health":
                time.sleep(config["health_delay"])
                data = json.dumps(identity | {"healthy": not config["unhealthy"]}).encode()
                self.send_response(503 if config["unhealthy"] else 200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            else:
                super().do_GET()

        def end_headers(self) -> None:
            self.send_header("X-Reference-Artifact", expected)
            super().end_headers()

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        ready = identity | {"port": server.server_port, "host": "127.0.0.1"}
        with (run / "ready.json").open("x") as handle:
            json.dump(ready, handle)
        server.serve_forever()


def request(url: str, path: str, headers: dict | None = None, timeout: float = 1) -> dict:
    started = time.perf_counter()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        response = opener.open(
            urllib.request.Request(url + path, headers=headers or {}), timeout=timeout
        )
    except urllib.error.HTTPError as error:
        response = error
    with response:
        body = response.read().decode()
        return {
            "path": path,
            "status": response.status,
            "body": body,
            "artifact": response.headers.get("X-Reference-Artifact"),
            "duration_ms": (time.perf_counter() - started) * 1000,
            "observed_at": datetime.now(UTC).isoformat(),
        }


@contextmanager
def process(
    artifact: dict,
    target: dict,
    directory: Path,
    *,
    unhealthy: bool = False,
    health_delay: float = 0,
):
    if target["owner_uid"] != os.getuid() or target["role"] not in {"backend", "web"}:
        raise ValueError("unauthorized target owner/role")
    directory.mkdir(exist_ok=False)
    config = target | {
        "nonce": uuid.uuid4().hex,
        "unhealthy": unhealthy,
        "health_delay": health_delay,
        "runtime_sha256": sha(Path(__file__).read_bytes()),
    }
    (directory / "config.json").write_text(json.dumps(config), encoding="utf-8")
    command = [
        sys.executable,
        "-m",
        "scripts.local_delivery",
        "serve",
        "--artifact",
        artifact["artifact"],
        "--expected",
        artifact["sha256"],
        "--run",
        str(directory),
        "--config",
        str(directory / "config.json"),
    ]
    with (directory / "process.log").open("xb") as log:
        child = subprocess.Popen(
            command, stdout=log, stderr=subprocess.STDOUT, cwd=Path(__file__).resolve().parents[1]
        )
        try:
            deadline = time.monotonic() + 3
            while not (directory / "ready.json").is_file():
                if child.poll() is not None or time.monotonic() >= deadline:
                    raise ValueError("child failed readiness; inspect retained process.log")
                time.sleep(0.02)
            ready = read_json(directory / "ready.json")
            expected_identity = {k: config[k] for k in ("owner_uid", "role", "target_id", "nonce")}
            if any(ready.get(k) != v for k, v in expected_identity.items()) or (
                ready.get("pid") != child.pid
                or ready.get("host") != "127.0.0.1"
                or ready.get("artifact_sha256") != artifact["sha256"]
                or ready.get("source_version") != artifact["manifest"]["source_version"]
                or ready.get("runtime_sha256") != config["runtime_sha256"]
            ):
                raise ValueError("actual child identity mismatch")
            yield ready
        finally:
            if child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=2)
            (directory / "stopped.json").write_text(
                json.dumps(
                    {
                        "pid": child.pid,
                        "returncode": child.returncode,
                        "stopped_at": datetime.now(UTC).isoformat(),
                        "ownership": "only this context's Popen child",
                    }
                ),
                encoding="utf-8",
            )


def record_request(url: str, path: str, observations: list, headers: dict | None = None) -> dict:
    started = time.perf_counter()
    try:
        result = request(url, path, headers)
    except (urllib.error.URLError, TimeoutError) as error:
        observations.append(
            {
                "path": path,
                "state": "request-failed",
                "error": str(error),
                "duration_ms": (time.perf_counter() - started) * 1000,
                "observed_at": datetime.now(UTC).isoformat(),
            }
        )
        raise ValueError("actual request failed; raw exception retained") from error
    observations.append(result)
    return result


def observe(ready: dict, expected: dict, observations: list | None = None) -> list[dict]:
    if any(ready[k] != expected[k] for k in ("target_id", "role", "owner_uid")):
        raise ValueError("target mismatch before health request")
    url = f"http://127.0.0.1:{ready['port']}"
    observations = [] if observations is None else observations
    for _ in range(3):
        result = record_request(url, "/health", observations)
        health = json.loads(result["body"])
        if (
            result["status"] != 200
            or not health.get("healthy")
            or any(health.get(k) != ready[k] for k in ready if k not in {"port", "host"})
        ):
            raise ValueError("health or deployment identity failed")
        time.sleep(0.03)
    for path, headers in (
        ("/api/item", {"X-Reference-Actor": "actor-a"}),
        ("/api/item", None),
        ("/", None),
    ):
        record_request(url, path, observations, headers)
    if (
        [r["status"] for r in observations[-3:]] != [200, 401, 200]
        or json.loads(observations[-3]["body"]).get("value") != "Reference item"
        or "Load item" not in observations[-1]["body"]
        or any(r["artifact"] != ready["artifact_sha256"] for r in observations)
    ):
        raise ValueError("application path or same-artifact verification failed")
    return observations


@contextmanager
def target_lock(root: Path):
    root.mkdir(parents=True, exist_ok=True)
    lock = root / "target.lock"
    with lock.open("x") as handle:
        handle.write(str(os.getpid()))
    try:
        yield
    finally:
        lock.unlink()


def run_browser(command: list[str], environment: dict, timeout: float = 40) -> dict:
    """Own the collector; interrupt so Playwright closes its detached browser group."""
    if isinstance(timeout, bool) or not 0 < timeout <= 40:
        raise ValueError("bounded browser timeout required")
    child = subprocess.Popen(
        command,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    state = "completed"
    stdout = stderr = ""
    forced = False
    try:
        stdout, stderr = child.communicate(timeout=timeout)
    except (subprocess.TimeoutExpired, KeyboardInterrupt) as error:
        state = "cancelled" if isinstance(error, KeyboardInterrupt) else "timeout"
    finally:
        if child.poll() is None:
            # Exit can race the poll; communicate still collects and waits.
            with suppress(ProcessLookupError):
                child.send_signal(signal.SIGINT)
            try:
                stdout, stderr = child.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                child.send_signal(signal.SIGINT)
                try:
                    stdout, stderr = child.communicate(timeout=2)
                except subprocess.TimeoutExpired:
                    forced = True
                    os.killpg(child.pid, signal.SIGKILL)
                    stdout, stderr = child.communicate(timeout=2)
        elif state != "completed":
            stdout, stderr = child.communicate(timeout=2)
    return {
        "state": state,
        "pid": child.pid,
        "returncode": child.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "timeout_seconds": timeout,
        "forced_group_stop": forced,
        "stopped_at": datetime.now(UTC).isoformat(),
        "ownership": "Popen child and its newly created process group",
    }


def exercise(
    root: Path,
    current: dict,
    previous: dict,
    browser_command: list[str] | None = None,
    *,
    cancel_after_ready: bool = False,
    browser_timeout: float = 40,
) -> dict:
    """Own all children for the exercise, retaining every failed observation."""
    result = {
        "scope": "actual isolated local processes; no production/cloud approval",
        "started_at": datetime.now(UTC).isoformat(),
        "artifacts": [previous, current],
        "roles": {},
        "owner_uid": os.getuid(),
        "runtime_sha256": sha(Path(__file__).read_bytes()),
    }
    with target_lock(root):
        for role in ("backend", "web"):
            target = {
                "target_id": "local-" + uuid.uuid4().hex,
                "role": role,
                "owner_uid": os.getuid(),
            }
            stages = []
            for label, artifact, fault in (
                ("baseline", previous, False),
                ("candidate", current, False),
                ("failed", current, True),
                ("restored", previous, False),
            ):
                directory = root / f"{role}-{label}"
                with process(artifact, target, directory, unhealthy=fault) as ready:
                    stage = {
                        "stage": label,
                        "identity": ready,
                        "config": read_json(directory / "config.json"),
                        "observations": [],
                    }
                    try:
                        if cancel_after_ready and label == "candidate":
                            raise InterruptedError(
                                "controlled cancellation after actual child readiness"
                            )
                        if fault:
                            raw = record_request(
                                f"http://127.0.0.1:{ready['port']}",
                                "/health",
                                stage["observations"],
                            )
                            if raw["status"] != 503:
                                raise ValueError("failure rehearsal did not actually fail")
                            stage["state"] = "paused"
                        else:
                            observe(ready, target, stage["observations"])
                            stage["state"] = "healthy"
                            if (
                                browser_command
                                and role == "web"
                                and label in {"candidate", "restored"}
                            ):
                                env = os.environ | {
                                    "REFERENCE_URL": f"http://127.0.0.1:{ready['port']}"
                                }
                                browser_source = sha(Path(browser_command[1]).read_bytes())
                                stage["browser"] = run_browser(
                                    browser_command + [str(directory / "browser")],
                                    env,
                                    browser_timeout,
                                ) | {"script_sha256": browser_source}
                                if stage["browser"]["state"] == "cancelled":
                                    raise InterruptedError("actual browser collector cancelled")
                                if (
                                    stage["browser"]["returncode"] != 0
                                    or stage["browser"]["state"] != "completed"
                                    or browser_source != sha(Path(browser_command[1]).read_bytes())
                                ):
                                    raise ValueError("real browser verification failed")
                        stages.append(stage)
                    except (
                        ValueError,
                        OSError,
                        subprocess.SubprocessError,
                        KeyboardInterrupt,
                    ) as error:
                        stage["state"] = (
                            "cancelled"
                            if isinstance(error, (InterruptedError, KeyboardInterrupt))
                            else "blocked"
                        )
                        stage["error"] = str(error)
                        raise
                    finally:
                        with (directory / "stage.json").open("x") as handle:
                            json.dump(stage, handle, indent=2)
                stage["stopped"] = read_json(directory / "stopped.json")
            result["roles"][role] = {"target": target, "stages": stages, "state": "restored"}
        result["finished_at"] = datetime.now(UTC).isoformat()
        result["state"] = "restored"
        with (root / "exercise.json").open("x") as handle:
            json.dump(result, handle, indent=2)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    service = sub.add_parser("serve")
    for arg in ("artifact", "run", "config"):
        service.add_argument("--" + arg, type=Path, required=True)
    service.add_argument("--expected", required=True)
    run = sub.add_parser("exercise")
    run.add_argument("--root", type=Path, required=True)
    run.add_argument("--current", required=True)
    run.add_argument("--previous", required=True)
    run.add_argument("--browser-script", type=Path)
    run.add_argument("--cancel-after-ready", action="store_true")
    run.add_argument("--browser-timeout", type=float, default=40)
    args = parser.parse_args()
    try:
        if args.command == "serve":
            serve(args.artifact, args.expected, args.run, args.config)
            return 0
        repository = Path(__file__).resolve().parents[1]
        current = build(repository, args.current, args.root / "artifacts")
        previous = build(repository, args.previous, args.root / "artifacts")
        result = exercise(
            args.root,
            current,
            previous,
            ["node", str(args.browser_script.resolve())] if args.browser_script else None,
            cancel_after_ready=args.cancel_after_ready,
            browser_timeout=args.browser_timeout,
        )
    except (InterruptedError, KeyboardInterrupt) as error:
        result = {"state": "cancelled", "error": str(error)}
    except (
        ValueError,
        OSError,
        KeyError,
        TypeError,
        zipfile.BadZipFile,
        subprocess.SubprocessError,
    ) as error:
        result = {"state": "blocked", "error": str(error)}
    print(json.dumps(result))
    return 0 if result["state"] == "restored" else 1


if __name__ == "__main__":
    raise SystemExit(main())
