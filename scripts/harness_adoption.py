"""Inspect pinned harness availability/entrypoints and optionally execute project checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

if __package__:
    from .documentation_check import git, inventory, local, read_json, require
else:
    from documentation_check import git, inventory, local, read_json, require

PREREQUISITES = {
    "skills/04-implementation-and-self-test/git-branch-management/SKILL.md",
    "skills/04-implementation-and-self-test/language-coding-standards/SKILL.md",
    "skills/04-implementation-and-self-test/language-coding-standards/references/common.md",
    "skills/04-implementation-and-self-test/documentation-maintenance/SKILL.md",
    "skills/05-integration-validation/documentation-delivery-validation/SKILL.md",
    "docs/git-branch-workflow.md",
    "docs/coding-standards.md",
    "docs/documentation-standard.md",
    "docs/quality-gates.md",
    "docs/evidence-trust.md",
    "templates/documentation/delivery-check.md",
}
GITHUB_PREREQUISITES = {
    "docs/github-repository-defaults.md",
    "skills/05-integration-validation/github-actions-bootstrap/SKILL.md",
    "skills/05-integration-validation/github-repository-bootstrap/SKILL.md",
}
LANGUAGES = {"python", "typescript", "arkts", "swift", "kotlin", "go", "sql", "zsh", "cpp"}
COMMANDS = {"format", "lint", "build", "test", "documentation"}


def target_binding(root: Path) -> dict:
    files = {
        path: {
            "sha256": hashlib.sha256(local(root, path).read_bytes()).hexdigest(),
            "executable": bool(local(root, path).stat().st_mode & 0o111),
        }
        for path in sorted(inventory(root))
    }
    return {
        "head": git(root, "rev-parse", "HEAD").strip(),
        "branch": git(root, "branch", "--show-current").strip(),
        "working_tree_dirty": bool(git(root, "status", "--porcelain").strip()),
        "files": files,
    }


def inspect(root: Path, harness: Path, manifest: dict, base: str) -> dict:
    require(manifest.get("schema_version") == 1, "adoption schema mismatch")
    revision = manifest["harness_revision"]
    require(git(harness, "rev-parse", "HEAD").strip() == revision, "harness revision mismatch")
    require(not git(harness, "status", "--porcelain").strip(), "harness checkout dirty")
    require(manifest.get("scope") in {"github", "offline", "non-github"}, "scope required")
    paths = PREREQUISITES | (GITHUB_PREREQUISITES if manifest["scope"] == "github" else set())
    languages = manifest["language_references"]
    require(isinstance(languages, list) and languages, "matching language references required")
    require(
        all(isinstance(language, str) and language in LANGUAGES for language in languages)
        and len(languages) == len(set(languages)),
        "invalid language references",
    )
    paths |= {
        "skills/04-implementation-and-self-test/language-coding-standards/references/"
        + language
        + ".md"
        for language in languages
    }
    for path in paths:
        require(
            local(harness, path).is_file(),
            f"missing prerequisite: {path}",
        )
    observed = {path for path in inventory(root) if Path(path).name == "AGENTS.md"}
    entries = manifest["entrypoints"]
    require(
        isinstance(entries, dict) and set(entries) == observed and "AGENTS.md" in entries,
        "entrypoint overrides not completely inventoried",
    )
    for path, digest in entries.items():
        require(
            hashlib.sha256(local(root, path).read_bytes()).hexdigest() == digest,
            f"entrypoint changed: {path}",
        )
    protected = manifest["protected_branches"]
    require(
        isinstance(protected, list)
        and protected
        and all(isinstance(x, str) and x.strip() for x in protected),
        "protected branch list required",
    )
    if manifest["scope"] == "github":
        default = git(root, "symbolic-ref", "--short", "refs/remotes/origin/HEAD").strip()
        require(default.removeprefix("origin/") in protected, "actual default branch omitted")
    require(
        all(
            name in local(root, "AGENTS.md").read_text(encoding="utf-8")
            for name in [
                "git-branch-management",
                "language-coding-standards",
                "documentation-maintenance",
                "documentation-delivery-validation",
            ]
        ),
        "entrypoint routing missing",
    )
    require(
        isinstance(manifest.get("unresolved_overrides"), list)
        and not manifest["unresolved_overrides"],
        "unresolved global/project/directory override",
    )
    require(
        isinstance(manifest.get("global_context"), str) and manifest["global_context"].strip(),
        "global instruction scope assessment required",
    )
    commands = manifest["commands"]
    require(
        isinstance(commands, dict) and set(commands) == COMMANDS,
        "complete actual command set required",
    )
    for args in commands.values():
        require(
            isinstance(args, list) and args and all(isinstance(x, str) and x.strip() for x in args),
            "actual argument lists required",
        )
    owners = manifest.get("owners")
    require(
        isinstance(owners, dict)
        and owners
        and all(
            isinstance(k, str) and k.strip() and isinstance(v, str) and v.strip()
            for k, v in owners.items()
        ),
        "owners must map actual roles to identities",
    )
    for key in ["task_facts", "independent_review"]:
        require(isinstance(manifest.get(key), str) and manifest[key].strip(), f"{key} required")
    require(git(root, "rev-parse", "--verify", base + "^{commit}").strip() == base, "base invalid")
    branch = git(root, "branch", "--show-current").strip()
    require(
        bool(branch) and branch not in manifest["protected_branches"],
        "task feature branch required",
    )
    return {
        "status": "available",
        "harness_revision": revision,
        "base": base,
        "target_binding": target_binding(root),
        "head": git(root, "rev-parse", "HEAD").strip(),
        "branch": branch,
        "prerequisites": sorted(paths),
        "entrypoints": entries,
        "behavior": "requires actual independent Agent task; availability is not loading proof",
        "remote_enforcement": "requires separate GitHub evidence",
    }


def run_checks(root: Path, harness: Path, manifest: dict, base: str) -> dict:
    result = inspect(root, harness, manifest, base)
    substitutions = {
        "harness": str(harness),
        "project": str(root),
        "python": sys.executable,
        "ruff": str(Path(sys.executable).parent / "ruff"),
        "base": base,
    }
    reports = {}
    for name in sorted(COMMANDS):
        args = [
            re.sub(
                r"\{(harness|project|python|ruff|base)\}",
                lambda match: substitutions[match[1]],
                arg,
            )
            for arg in manifest["commands"][name]
        ]
        try:
            process = subprocess.run(
                args, cwd=root, capture_output=True, text=True, timeout=60, check=False
            )
        except (OSError, subprocess.TimeoutExpired) as error:

            def decoded(value: str | bytes | None) -> str:
                return (
                    value.decode("utf-8", errors="replace")
                    if isinstance(value, bytes)
                    else value or ""
                )

            reports[name] = {
                "arguments": args,
                "returncode": None,
                "error": str(error),
                "stdout": decoded(getattr(error, "stdout", None)),
                "stderr": decoded(getattr(error, "stderr", None)),
            }
            return {**result, "status": "blocked", "failed_check": name, "reports": reports}
        reports[name] = {
            "arguments": args,
            "returncode": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
        }
        if process.returncode:
            return {**result, "status": "blocked", "failed_check": name, "reports": reports}
    try:
        final = target_binding(root)
        changed = (
            final != result["target_binding"]
            or git(harness, "rev-parse", "HEAD").strip() != manifest["harness_revision"]
            or bool(git(harness, "status", "--porcelain").strip())
        )
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        return {
            **result,
            "status": "blocked",
            "reason": "final binding unavailable",
            "error": str(error),
            "reports": reports,
        }
    if changed:
        return {
            **result,
            "status": "blocked",
            "reason": "target or knowledge changed during checks",
            "final_target_binding": final,
            "reports": reports,
        }
    return {**result, "status": "checks-passed", "reports": reports}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--harness", type=Path, required=True)
    parser.add_argument("--manifest", default="docs/harness-adoption.json")
    parser.add_argument("--base", required=True)
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    try:
        root, harness = args.root.resolve(), args.harness.resolve()
        manifest = read_json(local(root, args.manifest))
        operation = run_checks if args.run else inspect
        result = operation(root, harness, manifest, args.base)
    except (OSError, KeyError, TypeError, ValueError, subprocess.SubprocessError) as error:
        print(json.dumps({"status": "blocked", "error": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(result["status"] == "blocked")


if __name__ == "__main__":
    raise SystemExit(main())
