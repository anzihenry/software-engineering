"""Reproduce local P1 adoption and upgrade probes in newly owned fixture directories."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import shutil
import subprocess
import tarfile
from dataclasses import asdict
from pathlib import Path

from scripts.github_lifecycle.adoption import apply_install, plan_install
from scripts.github_lifecycle.common import LifecycleError
from scripts.github_lifecycle.installation import content_source_ref
from scripts.github_lifecycle.upgrade import apply_upgrade, plan_upgrade

MANIFEST = Path("automation/github-lifecycle-manifest.json")


def command(arguments: list[str], cwd: Path) -> dict:
    result = subprocess.run(arguments, cwd=cwd, capture_output=True, text=True, timeout=60)
    record = {
        "arguments": arguments,
        "cwd": str(cwd),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    if result.returncode:
        raise ValueError(json.dumps(record))
    return record


def fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(repository: Path, revision: str, destination: Path) -> None:
    actual = command(["git", "rev-parse", "--verify", revision + "^{commit}"], repository)[
        "stdout"
    ].strip()
    if actual != revision:
        raise ValueError("complete fixed source identity required")
    data = subprocess.run(
        ["git", "archive", revision], cwd=repository, capture_output=True, check=True, timeout=30
    ).stdout
    destination.mkdir()
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        archive.extractall(destination, filter="data")


def write_project_docs(target: Path, pin: str, *, scope: str, mature: bool) -> None:
    """Minimal bilingual actual configuration; upstream Markdown remains raw."""
    entries = {
        "README.md": "knowledge",
        "CHANGELOG.md": "knowledge",
        "docs/README.md": "knowledge",
        "docs/documentation.md": "knowledge",
    }
    if mature:
        entries["docs/user-guide.md"] = "knowledge"
    titles = {
        "README.md": ("合成领域参考", "Synthetic domain reference"),
        "CHANGELOG.md": ("采用变更记录", "Adoption change record"),
        "docs/README.md": ("文档地图", "Documentation map"),
        "docs/documentation.md": ("实际文档采用配置", "Actual documentation adoption"),
    }
    for file, pair in titles.items():
        primary = Path(file)
        for english in (False, True):
            path = primary.with_name(primary.stem + (".en" if english else "") + ".md")
            alternate = primary.name if english else primary.stem + ".en.md"
            title = pair[int(english)]
            body = (
                f"Fixed harness `{pin}`; maintainer is anzihenry; scope `{scope}`. "
                "This is a synthetic trial, not a release or production deployment. "
                "Actual command lists are in the adoption configuration. "
                "A separate non-author reads the pinned rules and executes the task; "
                "availability and hashes alone do not prove adoption. "
                + (
                    "Entry/knowledge/command/environment/role"
                    "s/permission or rule drift requires reva"
                    "lidation."
                )
                if english
                else f"固定harness `{pin}`，maintainer对应anzihenry，范围 `{scope}`。"
                "这是合成试点，不是正式发布或生产部署；真实命令清单在采用配置。"
                "另起非作者上下文实际读取固定规范并执行任务；可访问与摘要不能证明采用。"
                "入口/知识/命令/环境/责任/权限或规则变化后复验。"
            )
            links = (
                (
                    "[Project](../README.en.md) · [Adoption](documentation.en.md)"
                    if english
                    else "[项目](../README.md) · [采用](documentation.md)"
                )
                if file.startswith("docs/")
                else ("[Documentation](docs/README.en.md)" if english else "[文档](docs/README.md)")
            )
            text = (
                f'---\ntitle: "{title}"\nstatus: current\n'
                'owner: maintainer\nupdated: "2026-10-12"\n---\n\n'
                f"# {title}\n\n[{'中文' if english else 'English'}]({alternate})\n\n"
                f"{body}\n\n{links}\n"
            )
            if file == "README.md":
                text += "\n[Changes](CHANGELOG.en.md)\n" if english else "\n[变更](CHANGELOG.md)\n"
                text += (
                    "\n```text\npython -m unittest discover --s"
                    "tart-directory tests\npython tests/fixtur"
                    "es/domain-reference/server.py --port 876"
                    "5\n```\n"
                )
            if file == "docs/documentation.md":
                text += (
                    "\n[documentation-check.json](documentatio"
                    "n-check.json) · [harness-adoption.json]("
                    "harness-adoption.json) · [raw verificati"
                    "on](../verification.txt)\n"
                )
            if file == "docs/README.md" and mature:
                text += (
                    "\n[Existing guide](user-guide.en.md)\n"
                    if english
                    else "\n[既有指南](user-guide.md)\n"
                )
                text += (
                    (
                        "\nUpstream PR template and automation gui"
                        "de are unmodified raw harness inputs; "
                    )
                    + (
                        "the installer does not distribute first-"
                        "layer rules. CI is required only in GitH"
                        "ub scope; "
                    )
                    + "local checks do not prove platform enforcement.\n"
                    if english
                    else (
                        "\n上游PR模板与自动化指南保留原文原始字节，"
                        "安装器不分发第一层规范；仅GitHub范围要求真实CI，"
                        "本地检查不证明平台强制。\n"
                    )
                )
            destination = target / path
            destination.parent.mkdir(exist_ok=True)
            destination.write_text(text, encoding="utf-8")
    raw = {
        path: {
            "owner": "maintainer",
            "reason": (
                "Original fixed harness/runtime input; bilingual adoption guide explains its scope"
            ),
            "evidence": "verification.txt",
        }
        for path in (
            "AGENTS.md",
            ".github/PULL_REQUEST_TEMPLATE.md",
            "docs/github-lifecycle-automation.md",
        )
    }
    config = {
        "schema_version": 1,
        "standard_version": pin,
        "owners": {"maintainer": "anzihenry"},
        "required_checks": ["validate", "lifecycle-policy"] if scope == "github" else [],
        "documents": entries,
        "raw": raw,
        "legacy": {},
    }
    (target / "docs/documentation-check.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )


def prepare(target: Path, harness: Path, pin: str, *, mature: bool, repository: str) -> dict:
    target.mkdir()
    command(["git", "init", "-b", "main"], target)
    command(["git", "config", "user.name", "Harness synthetic fixture"], target)
    command(["git", "config", "user.email", "fixture@example.invalid"], target)
    command(["git", "commit", "--allow-empty", "-m", "fixture baseline"], target)
    base = command(["git", "rev-parse", "HEAD"], target)["stdout"].strip()
    command(["git", "switch", "-c", "codex/p1-adoption"], target)
    protected = {}
    if mature:
        fixture_files = {
            "AGENTS.md": (
                "# Fixture local rules\nPreserve fixture-l"
                "ocal.txt and the existing project-local "
                "workflow.\n"
            ),
            "fixture-local.txt": "fixture user-owned content\n",
            ".github/workflows/project-local.yml": (
                "name: Existing project\non: workflow_disp"
                "atch\npermissions: {}\njobs:\n  existing:\n "
                "   runs-on: ubuntu-latest\n    steps:\n   "
                "   - run: echo fixture-existing\n"
            ),
        }
        for name, content in fixture_files.items():
            p = target / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            protected[name] = content
        for suffix, title, text in [
            ("", "既有使用指南", "保留合成项目既有用户说明。"),
            (".en", "Existing user guide", "Retain the fixture's existing user guidance."),
        ]:
            p = target / f"docs/user-guide{suffix}.md"
            p.parent.mkdir(exist_ok=True)
            other = "user-guide.md" if suffix else "user-guide.en.md"
            p.write_text(
                f'---\ntitle: "{title}"\nstatus: current\n'
                'owner: maintainer\nupdated: "2026-10-12"\n---\n\n'
                f"# {title}\n\n[Translation]({other})\n\n{text}\n",
                encoding="utf-8",
            )
            protected[p.relative_to(target).as_posix()] = p.read_text()
        command(["git", "add", "."], target)
        command(["git", "commit", "-m", "fixture existing entry CI and guidance"], target)
    (target / ".gitignore").write_text("__pycache__/\n*.py[cod]\n", encoding="utf-8")
    for name in (
        "pyproject.toml",
        "requirements-dev.txt",
        "tests/test_domain_reference.py",
        "tests/fixtures/domain-reference/server.py",
        "tests/fixtures/domain-reference/index.html",
    ):
        p = target / name
        p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(harness / name, p)
    command(["git", "add", "."], target)
    command(["git", "commit", "-m", "fixture immutable application baseline"], target)
    application_base = command(["git", "rev-parse", "HEAD"], target)["stdout"].strip()
    adapter = {
        "schema_version": 1,
        "name": "p1-reference",
        "runner": "ubuntu-latest",
        "toolchain": {"kind": "python", "version": "3.14"},
        "required_files": [
            "pyproject.toml",
            "requirements-dev.txt",
            "tests/test_domain_reference.py",
        ],
        "check_commands": [
            ["python", "-m", "ruff", "check", "tests"],
            ["python", "-m", "ruff", "format", "--check", "tests"],
            ["python", "-m", "compileall", "-q", "tests"],
            ["python", "-m", "unittest", "discover", "--start-directory", "tests"],
        ],
        "dependabot_ecosystems": ["pip", "github-actions"],
        "release_artifact_retention_days": 7,
    }
    adapter_path = target.parent / (target.name + "-adapter.json")
    adapter_path.write_text(json.dumps(adapter, indent=2), encoding="utf-8")
    plan, files = plan_install(
        harness,
        MANIFEST,
        target,
        repository=repository,
        default_branch="main",
        profile="governance",
        adapter="custom",
        adapter_config=adapter_path,
        source_ref=pin,
    )
    apply_install(plan, files, confirmation=f"install:{repository}")
    prefix = (target / "AGENTS.md").read_text() if mature else "# Synthetic project input\n"
    (target / "AGENTS.md").write_text(
        prefix
        + f"\nUse pinned harness {pin} at {harness}.\n"
        + (
            "Use git-branch-management before edits; "
            "language-coding-standards/common/Python "
            "before code.\n"
        )
        + (
            "Use documentation-maintenance and separa"
            "te documentation-delivery-validation; no"
            " author approval.\n"
        )
        + (
            "Read domain-validation/harness-observati"
            "on/local-delivery-channel for this backe"
            "nd/Web scope.\n"
        )
        + (
            "Actual commands and owner mapping: docs/"
            "harness-adoption.json. Missing evidence "
            "or drift blocks.\n"
        ),
        encoding="utf-8",
    )
    (target / "verification.txt").write_text(
        f"Actual fixed knowledge {pin}; synthetic local fixture setup.\n", encoding="utf-8"
    )
    write_project_docs(target, pin, scope="non-github", mature=mature)
    args = {
        "format": ["{python}", "-m", "ruff", "format", "--check", "tests"],
        "lint": ["{python}", "-m", "ruff", "check", "tests"],
        "build": ["{python}", "-m", "compileall", "-q", "tests"],
        "test": ["{python}", "-m", "unittest", "discover", "--start-directory", "tests"],
        "documentation": [
            "{python}",
            "{harness}/scripts/documentation_check.py",
            "check",
            "--root",
            "{project}",
            "--base",
            "{base}",
        ],
    }
    adopted = {
        "schema_version": 1,
        "harness_revision": pin,
        "scope": "non-github",
        "language_references": ["python"],
        "entrypoints": {"AGENTS.md": fingerprint(target / "AGENTS.md")},
        "global_context": (
            "Controlled synthetic task runtime; root "
            "instructions and this project input. Ind"
            "ependent observer must inspect actual ta"
            "sk context."
        ),
        "unresolved_overrides": [],
        "protected_branches": ["main"],
        "owners": {"maintainer": "anzihenry"},
        "task_facts": "external current trial report",
        "independent_review": "separate Agent actual task and frozen evidence",
        "commands": args,
    }
    (target / "docs/harness-adoption.json").write_text(
        json.dumps(adopted, indent=2), encoding="utf-8"
    )
    for name, text in protected.items():
        actual = (target / name).read_text()
        if (not actual.startswith(text)) if name == "AGENTS.md" else actual != text:
            raise ValueError("fixture local content lost")
    command(["git", "add", "."], target)
    command(
        ["git", "commit", "-m", "adopt fixed harness without overwriting local content"], target
    )
    return {
        "root": str(target),
        "base": base,
        "application_base": application_base,
        "head": command(["git", "rev-parse", "HEAD"], target)["stdout"].strip(),
        "protected": {k: hashlib.sha256(v.encode()).hexdigest() for k, v in protected.items()},
        "installation": asdict(plan),
    }


def upgrade_probe(
    target: Path, old: Path, new: Path, old_ref: str, new_ref: str, repository: str
) -> dict:
    target.mkdir()
    unknown = target / "fixture-local.txt"
    unknown.write_text("preserve unknown local content\n", encoding="utf-8")
    before = fingerprint(unknown)
    initial, files = plan_install(
        old,
        MANIFEST,
        target,
        repository=repository,
        default_branch="main",
        profile="governance",
        adapter="external",
        source_ref=old_ref,
    )
    apply_install(initial, files, confirmation=f"install:{repository}")
    kwargs = {
        "repository": repository,
        "default_branch": "main",
        "from_profile": "governance",
        "profile": "governance",
        "manifest": MANIFEST,
    }
    plan, files = plan_upgrade(old, new, target, from_ref=old_ref, to_ref=new_ref, **kwargs)
    if plan.blockers:
        raise ValueError("fixed upgrade blocked: " + str(plan.blockers))
    apply_upgrade(plan, files, confirmation=plan.confirmation)
    repeat, _ = plan_upgrade(new, new, target, from_ref=new_ref, to_ref=new_ref, **kwargs)
    if repeat.blockers:
        raise ValueError("same-version repeat blocked")
    managed = next(target / e.path for e in plan.entries if e.path.endswith(".py"))
    saved = managed.read_bytes()
    managed.write_bytes(saved + b"\n# controlled fixture local change\n")
    changed = managed.read_bytes()
    drift, pending = plan_upgrade(new, new, target, from_ref=new_ref, to_ref=new_ref, **kwargs)
    rejected = False
    try:
        apply_upgrade(drift, pending, confirmation=drift.confirmation)
    except LifecycleError:
        rejected = True
    if not rejected or managed.read_bytes() != changed:
        raise ValueError("local modification overwritten")
    managed.write_bytes(
        saved
    )  # Undo only this probe's known injection, retaining its raw bytes below.
    rollback, files = plan_upgrade(new, old, target, from_ref=new_ref, to_ref=old_ref, **kwargs)
    apply_upgrade(rollback, files, confirmation=rollback.confirmation)
    if fingerprint(unknown) != before:
        raise ValueError("unknown file overwritten")
    return {
        "upgrade": asdict(plan),
        "repeat": asdict(repeat),
        "drift": asdict(drift),
        "rollback": asdict(rollback),
        "modified_path": str(managed),
        "modified_raw": changed.decode(),
        "unknown_sha256": before,
        "unknown_preserved": True,
        "drift_apply_rejected": rejected,
    }


def removed_upstream_probe(root: Path) -> dict:
    """Synthetic immutable package data exercises upstream-deletion preservation."""
    old, new, target = root / "old", root / "new", root / "target"
    versions = []
    for directory, files in (
        (old, {"kept.txt": b"old\n", "removed.txt": b"preserve\n"}),
        (new, {"kept.txt": b"new\n"}),
    ):
        (directory / "automation").mkdir(parents=True)
        (directory / MANIFEST).write_text(
            json.dumps({"schema_version": 1, "files": sorted(files)}), encoding="utf-8"
        )
        for name, data in files.items():
            (directory / name).write_bytes(data)
        versions.append(content_source_ref(list(files.items())))
    target.mkdir()
    initial, files = plan_install(
        old,
        MANIFEST,
        target,
        repository="example/p1-removal",
        default_branch="main",
        profile="full",
        adapter="external",
        source_ref=versions[0],
    )
    apply_install(initial, files, confirmation="install:example/p1-removal")
    plan, files = plan_upgrade(
        old,
        new,
        target,
        repository="example/p1-removal",
        default_branch="main",
        from_ref=versions[0],
        to_ref=versions[1],
        from_profile="full",
        profile="full",
        manifest=MANIFEST,
    )
    apply_upgrade(plan, files, confirmation=plan.confirmation)
    if (target / "removed.txt").read_bytes() != b"preserve\n":
        raise ValueError("upstream deletion removed local content")
    return {
        "scope": "controlled package data, not a released upstream deletion",
        "versions": versions,
        "plan": asdict(plan),
        "removed_preserved": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--harness", type=Path, required=True)
    parser.add_argument("--old-ref", required=True)
    parser.add_argument("--new-ref", required=True)
    args = parser.parse_args()
    if (
        command(["git", "rev-parse", "HEAD"], args.harness)["stdout"].strip() != args.new_ref
        or command(["git", "status", "--porcelain"], args.harness)["stdout"].strip()
    ):
        raise ValueError("clean fixed knowledge checkout required")
    args.root.mkdir(parents=True, exist_ok=False)
    old, new = args.root / "old-source", args.root / "new-source"
    source(args.harness, args.old_ref, old)
    source(args.harness, args.new_ref, new)
    result = {
        "old_ref": args.old_ref,
        "new_ref": args.new_ref,
        "scope": "controlled local synthetic projects",
        "removed_upstream": removed_upstream_probe(args.root / "removed-upstream"),
        "projects": [],
        "upgrade": upgrade_probe(
            args.root / "upgrade-target", old, new, args.old_ref, args.new_ref, "example/p1-upgrade"
        ),
    }
    for name, mature in (("new-backend", False), ("mature-web", True)):
        result["projects"].append(
            prepare(
                args.root / name,
                args.harness,
                args.new_ref,
                mature=mature,
                repository="example/" + name,
            )
        )
    with (args.root / "setup.json").open("x") as handle:
        json.dump(result, handle, indent=2, default=str)
    print(json.dumps(result, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
