"""Check requirement-source coverage and execution mappings; never certify semantics."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import subprocess
import tarfile
from pathlib import Path

CORE_SOURCES = (
    "README.md",
    "docs/getting-started.md",
    "AGENTS.md",
    "SECURITY.md",
    "UPGRADING.md",
    "docs/software-development-lifecycle.md",
    "docs/coding-standards.md",
    "docs/git-branch-workflow.md",
    "docs/github-repository-defaults.md",
    "docs/documentation-standard.md",
    "docs/documentation-integration.md",
    "docs/documentation-tooling.md",
    "docs/content-governance.md",
    "docs/project-boundaries.md",
    "docs/github-lifecycle-automation.md",
    "docs/version-compatibility.md",
    "docs/cross-project-acceptance.md",
    "docs/github-canary-validation.md",
    "docs/local-development.md",
    "docs/harness-requirements.md",
    "docs/quality-gates.md",
    "docs/evidence-trust.md",
    "docs/harness-adoption.md",
)


def source_paths(root: Path) -> list[str]:
    return sorted(
        set(CORE_SOURCES)
        | {
            path.relative_to(root).as_posix()
            for folder in ("skills", "docs/workflows", "templates")
            for path in (root / folder).rglob("*.md")
            if not path.name.endswith(".en.md")
        }
    )


def units(text: str) -> list[tuple[int, str, str]]:
    """Inventory all prose lines, not just obligation keywords; skip example fences."""
    lines = text.splitlines()
    start = lines.index("---", 1) + 1 if lines and lines[0] == "---" else 0
    section, fenced = "入口", False
    result = []
    for number, line in enumerate(lines[start:], start + 1):
        value = line.strip()
        if value.startswith("```"):
            fenced = not fenced
        elif not fenced and value.startswith("#"):
            section = value.lstrip("# ").strip()
        elif not fenced and value and not re.fullmatch(r"\|[\s:|\-]+", value):
            result.append((number, section, value))
    return result


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def identifier(path: str, section: str, text: str) -> str:
    return "REQ-" + sha(path + "\0" + section + "\0" + text)[:16]


def _validate(root: Path, data: dict) -> list[str]:
    errors = []
    if data.get("schema_version") != 1 or not re.fullmatch(
        "[a-f0-9]{40}", data.get("baseline", "")
    ):
        return ["invalid catalog schema/baseline"]
    commit = subprocess.run(
        ["git", "rev-parse", "--verify", data["baseline"] + "^{commit}"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if commit.returncode or commit.stdout.strip() != data["baseline"]:
        errors.append("baseline is not an existing commit")
    expected = source_paths(root)
    sources = data.get("sources", [])
    if data.get("scope") != expected or sorted(s["path"] for s in sources) != expected:
        errors.append("source scope incomplete or duplicated")
    rows = data.get("requirements", [])
    indexed = {row["id"]: row for row in rows}
    if len(indexed) != len(rows):
        errors.append("duplicate requirement ID")
    if not isinstance(data.get("retired"), list):
        errors.append("retired relationships required")
    else:
        retired_ids = set()
        for item in data["retired"]:
            old = item.get("id")
            replacements = item.get("replacements")
            if (
                not isinstance(old, str)
                or not re.fullmatch(r"REQ-[a-f0-9]{16}", old)
                or old in indexed
                or old in retired_ids
                or not item.get("reason")
                or not item.get("owner")
                or not isinstance(replacements, list)
                or not set(replacements) <= set(indexed)
                or item.get("disposition") not in {"replaced", "retired"}
                or not item.get("decision")
                or (item.get("disposition") == "replaced" and not replacements)
                or (item.get("disposition") == "retired" and replacements)
            ):
                errors.append("invalid retirement/replacement relationship")
            retired_ids.add(old)
        if not commit.returncode:
            historic = set()
            previous = subprocess.run(
                ["git", "show", "HEAD:docs/harness-requirements.json"],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            previous_ids = set()
            if not previous.returncode:
                previous_data = json.loads(previous.stdout)
                if data["baseline"] != previous_data["baseline"]:
                    errors.append("catalog baseline changed; explicit migration required")
                previous_ids = {r["id"] for r in previous_data["requirements"]}
                previous_ids.update(r["id"] for r in previous_data["retired"])
            archive = subprocess.run(
                ["git", "archive", data["baseline"]], cwd=root, capture_output=True, check=True
            )
            with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tree:
                for member in tree:
                    path = member.name
                    included = path in CORE_SOURCES or (
                        path.startswith(("skills/", "docs/workflows/", "templates/"))
                        and path.endswith(".md")
                        and not path.endswith(".en.md")
                    )
                    if not included or not member.isfile():
                        continue
                    stream = tree.extractfile(member)
                    if stream is not None:
                        historic.update(
                            identifier(path, section, value)
                            for _, section, value in units(stream.read().decode("utf-8"))
                        )
            historic.update(previous_ids)
            if not historic - set(indexed) <= retired_ids:
                errors.append("baseline clauses removed without retirement relationship")
            if not retired_ids <= historic:
                errors.append("unknown retired clauses")
    observed = set()
    for source in sources:
        path = source["path"]
        if path not in expected:
            continue
        target = root / path
        if not target.is_file() or target.is_symlink():
            errors.append(f"{path}: source missing or symlink")
            continue
        text = target.read_text(encoding="utf-8")
        if sha(text) != source.get("sha256"):
            errors.append(f"{path}: source changed; update inventory and obtain new review")
        for number, section, value in units(text):
            key = identifier(path, section, value)
            if key in observed:
                continue
            observed.add(key)
            row = indexed.get(key)
            if row is None:
                errors.append(f"{path}:{number}: uncovered prose unit")
                continue
            if (row.get("source"), row.get("line"), row.get("section"), row.get("text_sha256")) != (
                path,
                number,
                section,
                sha(value),
            ):
                errors.append(f"{key}: invalid source binding")
            if set(row) != {
                "id",
                "source",
                "execution_asset",
                "applicability",
                "line",
                "section",
                "summary",
                "text_sha256",
                "kind",
                "controls",
                "capability",
                "adoption",
                "gaps",
            }:
                errors.append(f"{key}: invalid requirement fields")
            if row.get("kind") not in {"mandatory", "instruction", "recommendation", "context"}:
                errors.append(f"{key}: invalid normativity")
            names = row.get("controls")
            if not isinstance(names, list) or not names or len(names) != len(set(names)):
                errors.append(f"{key}: execution controls required")
                names = []
            allowed_executors = {
                "coding": (
                    "skills/04-implementation-and-self-test/language-coding-standards/SKILL.md"
                ),
                "branch": "skills/04-implementation-and-self-test/git-branch-management/SKILL.md",
                "documentation": "scripts/documentation_check.py",
                "governance": "scripts/github_lifecycle/repository_inspection.py",
                "content": "scripts/check_repository.py",
                "automation": "scripts/github_lifecycle/__main__.py",
                "lifecycle": "docs/software-development-lifecycle.md",
                "trust": "scripts/trusted_review.py",
            }
            for name in names:
                control = data.get("controls", {}).get(name, {})
                if (
                    name not in allowed_executors
                    or not all(
                        isinstance(control.get(k), str) and control[k].strip()
                        for k in (
                            "trigger",
                            "owner",
                            "method",
                            "evidence",
                            "executor",
                            "gap",
                            "failure",
                            "positive",
                            "negative",
                        )
                    )
                    or control.get("executor") != allowed_executors.get(name)
                    or not (root / control.get("executor", "")).is_file()
                ):
                    errors.append(f"{key}: execution mapping incomplete")
                if control.get("gap") not in {"GAP-01", "GAP-02", "GAP-03", "GAP-04"}:
                    errors.append(f"{key}: invalid gap")
            gaps = row.get("gaps")
            if gaps != sorted({data.get("controls", {}).get(n, {}).get("gap") for n in names}):
                errors.append(f"{key}: gap binding inconsistent")
            asset = row.get("execution_asset", "")
            if (
                not isinstance(asset, str)
                or asset.startswith("/")
                or ".." in Path(asset).parts
                or not (root / asset).is_file()
            ):
                errors.append(f"{key}: missing local execution asset")
            if path.startswith("skills/"):
                parent_skill = next(
                    (p / "SKILL.md" for p in (root / path).parents if (p / "SKILL.md").is_file()),
                    None,
                )
                if parent_skill and asset != parent_skill.relative_to(root).as_posix():
                    errors.append(f"{key}: skill execution must bind its local responsibility")
            expected_capability = (
                "manual-executable"
                if row.get("kind") in {"mandatory", "instruction"}
                else "reference"
            )
            if row.get("capability") != expected_capability:
                errors.append(f"{key}: invalid capability claim")
            if row.get("adoption") != "unverified":
                errors.append(f"{key}: catalog must not certify target adoption")
            if not row.get("applicability"):
                errors.append(f"{key}: missing applicability")
            if not row.get("summary"):
                errors.append(f"{key}: missing summary")
    if set(indexed) != observed:
        errors.append("unknown/removed prose units need explicit retirement and remapping")
    return errors


def validate(root: Path, data: dict) -> list[str]:
    try:
        return _validate(root, data)
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        return [f"invalid catalog structure: {error}"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    errors = validate(
        args.root,
        json.loads((args.root / "docs/harness-requirements.json").read_text(encoding="utf-8")),
    )
    print(
        "\n".join(errors)
        if errors
        else "Source coverage and mappings passed; semantics/adoption unproven."
    )
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
