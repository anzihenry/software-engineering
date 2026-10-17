from __future__ import annotations

import io
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import unittest
import uuid
import zipfile
from pathlib import Path

from scripts.local_delivery import (
    build,
    exercise,
    observe,
    process,
    request,
    run_browser,
    sha,
    target_lock,
    unpack,
)


class LocalDeliveryTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repository = Path(__file__).resolve().parents[1]
        self.source = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=self.repository, text=True
        ).strip()
        self.artifact = build(self.repository, self.source, self.root / "artifacts")
        self.target = {
            "target_id": "local-" + uuid.uuid4().hex,
            "role": "backend",
            "owner_uid": os.getuid(),
        }

    def test_immutable_build_and_fixed_source(self) -> None:
        path = Path(self.artifact["artifact"])
        before = path.stat().st_mtime_ns
        again = build(self.repository, self.source, self.root / "artifacts")
        self.assertEqual(again["sha256"], self.artifact["sha256"])
        self.assertEqual(path.stat().st_mtime_ns, before)
        with self.assertRaises(ValueError):
            build(self.repository, "HEAD", self.root)
        manifest = unpack(path, self.artifact["sha256"], self.root / "unpacked")
        self.assertEqual(manifest["source_version"], self.source)

    def test_tampering_unknown_members_and_schema(self) -> None:
        original = Path(self.artifact["artifact"])
        corrupted = self.root / "corrupted.zip"
        corrupted.write_bytes(original.read_bytes() + b"tampered")
        with self.assertRaises(ValueError):
            unpack(corrupted, self.artifact["sha256"], self.root / "should-not-exist")
        self.assertFalse((self.root / "should-not-exist").exists())
        for variant in ("../escape", "schema"):
            payload = io.BytesIO()
            with zipfile.ZipFile(original) as source, zipfile.ZipFile(payload, "w") as out:
                for name in source.namelist():
                    data = source.read(name)
                    if variant == "schema" and name == "manifest.json":
                        manifest = json.loads(data)
                        manifest["schema_version"] = True
                        data = json.dumps(manifest).encode()
                    out.writestr(name, data)
                if variant != "schema":
                    out.writestr(variant, b"bad")
            path = self.root / ("escape.zip" if variant != "schema" else "schema.zip")
            path.write_bytes(payload.getvalue())
            with self.assertRaises(ValueError):
                unpack(path, sha(payload.getvalue()), self.root / variant.replace("/", "-"))

    def test_wrong_owner_and_role_do_not_start(self) -> None:
        for target in (self.target | {"owner_uid": -1}, self.target | {"role": "production"}):
            with (
                self.assertRaises(ValueError),
                process(self.artifact, target, self.root / "invalid"),
            ):
                self.fail("unauthorized child started")
            self.assertFalse((self.root / "invalid").exists())

    def test_real_processes_failure_and_recovery(self) -> None:
        result = exercise(self.root / "channel", self.artifact, self.artifact)
        self.assertEqual(result["state"], "restored")
        for row in result["roles"].values():
            self.assertEqual(
                [s["state"] for s in row["stages"]], ["healthy", "healthy", "paused", "healthy"]
            )
            self.assertEqual(row["stages"][2]["observations"][0]["status"], 503)
            self.assertTrue(all(s["stopped"]["returncode"] is not None for s in row["stages"]))
            self.assertTrue(
                all(
                    s["identity"]["artifact_sha256"] == self.artifact["sha256"]
                    for s in row["stages"]
                )
            )
        with self.assertRaises(FileExistsError):
            exercise(self.root / "channel", self.artifact, self.artifact)

    def test_actual_cancellation_cleans_owned_child(self) -> None:
        root = self.root / "cancel"
        with self.assertRaises(InterruptedError):
            exercise(root, self.artifact, self.artifact, cancel_after_ready=True)
        stage = json.loads((root / "backend-candidate/stage.json").read_text())
        stopped = json.loads((root / "backend-candidate/stopped.json").read_text())
        self.assertEqual(stage["state"], "cancelled")
        self.assertIsNotNone(stopped["returncode"])
        self.assertFalse((root / "target.lock").exists())

    def test_actual_timeout_and_target_mismatch(self) -> None:
        directory = self.root / "slow"
        with process(self.artifact, self.target, directory, health_delay=0.2) as ready:
            with self.assertRaises(ValueError):
                observe(ready, self.target | {"target_id": "wrong"})
            with self.assertRaises(TimeoutError):
                request(f"http://127.0.0.1:{ready['port']}", "/health", timeout=0.05)
        self.assertTrue((directory / "stopped.json").is_file())

    def test_concurrent_target_is_rejected_without_removing_lock(self) -> None:
        with target_lock(self.root):
            with self.assertRaises(FileExistsError), target_lock(self.root):
                self.fail("concurrent lock acquired")
            self.assertTrue((self.root / "target.lock").is_file())
        self.assertFalse((self.root / "target.lock").exists())

    def test_failed_health_preserves_actual_response(self) -> None:
        raw = []
        with (
            process(self.artifact, self.target, self.root / "unhealthy", unhealthy=True) as ready,
            self.assertRaises(ValueError),
        ):
            observe(ready, self.target, raw)
        self.assertEqual(raw[0]["status"], 503)
        self.assertFalse(json.loads(raw[0]["body"])["healthy"])

    def test_owned_collector_timeout_and_interrupt_retain_partial_output(self) -> None:
        script = self.root / "owned-collector.py"
        script.write_text(
            'import time\nprint("partial-raw", flush=True)\ntime.sleep(10)\n', encoding="utf-8"
        )
        result = run_browser([sys.executable, str(script)], dict(os.environ), timeout=0.1)
        self.assertEqual(result["state"], "timeout")
        self.assertIn("partial-raw", result["stdout"])
        self.assertIsNotNone(result["returncode"])
        timer = threading.Timer(0.2, lambda: os.kill(os.getpid(), signal.SIGINT))
        timer.start()
        try:
            cancelled = run_browser([sys.executable, str(script)], dict(os.environ), timeout=5)
        finally:
            timer.join()
        self.assertEqual(cancelled["state"], "cancelled")
        self.assertIn("partial-raw", cancelled["stdout"])
        self.assertIsNotNone(cancelled["returncode"])


if __name__ == "__main__":
    unittest.main()
