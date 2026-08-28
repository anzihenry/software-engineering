from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .common import LifecycleError, LifecyclePolicy, load_json_mapping

METADATA_PATTERN = re.compile(r"<!--\s*lifecycle-metadata\s*\n(?P<body>.*?)\n\s*-->", re.DOTALL)
HEADING_PATTERN = re.compile(r"^##\s+(?P<name>[^\n]+?)\s*$", re.MULTILINE)
CHANGE_ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")
PLACEHOLDERS = {"", "-", "...", "n/a", "na", "none", "tbd", "todo"}
BASE_SECTIONS = (
    "Purpose",
    "Scope and non-goals",
    "Validation evidence",
    "Release impact",
    "Recovery plan",
    "Related records",
)
MEDIUM_SECTIONS = ("Independent review", "Integration/system evidence")
HIGH_SECTIONS = (
    "Design record",
    "Specialist review",
    "Data recovery",
    "Human Go/No-Go owner",
)
DEPENDABOT_LOGIN = "dependabot[bot]"
DEPENDABOT_BRANCH_PREFIX = "dependabot/"
DEPENDENCY_FILE_NAMES = {
    "Pipfile",
    "Pipfile.lock",
    "Package.resolved",
    "Package.swift",
    "go.mod",
    "go.sum",
    "npm-shrinkwrap.json",
    "package-lock.json",
    "package.json",
    "pnpm-lock.yaml",
    "poetry.lock",
    "pyproject.toml",
    "setup.cfg",
    "setup.py",
    "uv.lock",
    "yarn.lock",
}
REQUIREMENTS_FILE_PATTERN = re.compile(r"^requirements(?:[-_.][A-Za-z0-9_.-]+)?\.txt$")
CONSTRAINTS_FILE_PATTERN = re.compile(r"^constraints(?:[-_.][A-Za-z0-9_.-]+)?\.txt$")
PINNED_ACTION_CHANGE_PATTERN = re.compile(
    r"^(?:-\s+)?uses:\s*(?P<action>[^\s@]+)@[0-9a-f]{40}"
    r"\s+#\s+v\d+\.\d+\.\d+$"
)


@dataclass(frozen=True)
class PullRequestValidation:
    draft: bool
    risk_level: str | None
    issues: tuple[str, ...]
    record_source: str = "declared"

    @property
    def blocks(self) -> bool:
        return bool(self.issues) and not self.draft


def parse_metadata(body: str) -> tuple[dict[str, str], list[str]]:
    matches = list(METADATA_PATTERN.finditer(body))
    if len(matches) != 1:
        return {}, ["PR body must contain exactly one lifecycle-metadata block"]
    values: dict[str, str] = {}
    issues: list[str] = []
    for line in matches[0].group("body").splitlines():
        if not line.strip():
            continue
        key, separator, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if not separator or not key:
            issues.append(f"invalid lifecycle metadata line: {line.strip()!r}")
            continue
        if key in values:
            issues.append(f"duplicate lifecycle metadata key: {key}")
            continue
        values[key] = value
    expected = {"schema-version", "change-id", "risk-level"}
    unknown = set(values) - expected
    missing = expected - set(values)
    if unknown:
        issues.append(f"unknown lifecycle metadata keys: {', '.join(sorted(unknown))}")
    if missing:
        issues.append(f"missing lifecycle metadata keys: {', '.join(sorted(missing))}")
    return values, issues


def parse_sections(body: str) -> tuple[dict[str, str], list[str]]:
    matches = list(HEADING_PATTERN.finditer(body))
    sections: dict[str, str] = {}
    issues: list[str] = []
    for index, match in enumerate(matches):
        name = match.group("name").strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        if name in sections:
            issues.append(f"duplicate PR section: {name}")
            continue
        sections[name] = body[start:end].strip()
    return sections, issues


def has_meaningful_content(value: str | None) -> bool:
    if value is None:
        return False
    normalized = " ".join(value.split()).strip().lower()
    return normalized not in PLACEHOLDERS and "replace-me" not in normalized


def validate_pr_body(body: str, draft: bool, policy: LifecyclePolicy) -> PullRequestValidation:
    metadata, issues = parse_metadata(body)
    sections, section_issues = parse_sections(body)
    issues.extend(section_issues)

    if metadata.get("schema-version") != "1":
        issues.append("lifecycle metadata schema-version must be 1")
    change_id = metadata.get("change-id", "")
    if not CHANGE_ID_PATTERN.fullmatch(change_id) or "REPLACE" in change_id:
        issues.append("change-id must be a concrete uppercase hyphenated identifier")
    risk_level = metadata.get("risk-level")
    if risk_level not in policy.risk_levels:
        issues.append(f"risk-level must be one of: {', '.join(policy.risk_levels)}")

    required_sections = list(BASE_SECTIONS)
    if risk_level in {"medium", "high"}:
        required_sections.extend(MEDIUM_SECTIONS)
    if risk_level == "high":
        required_sections.extend(HIGH_SECTIONS)
    for section in required_sections:
        if not has_meaningful_content(sections.get(section)):
            issues.append(f"required PR section is missing or incomplete: {section}")

    return PullRequestValidation(draft=draft, risk_level=risk_level, issues=tuple(issues))


def _load_pull_request_files(path: Path) -> tuple[Mapping[str, object], ...]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise LifecycleError(f"cannot read pull request files: {error}") from error
    if not isinstance(raw, list):
        raise LifecycleError("pull request files must be an array")
    pages = raw if all(isinstance(item, list) for item in raw) else [raw]
    records: list[Mapping[str, object]] = []
    for page in pages:
        if not isinstance(page, list):
            raise LifecycleError("pull request file page must be an array")
        for record in page:
            if not isinstance(record, Mapping):
                raise LifecycleError("pull request file record must be an object")
            records.append(record)
    if not records:
        raise LifecycleError("pull request files must not be empty")
    return tuple(records)


def _is_dependency_file(filename: str) -> bool:
    path = PurePosixPath(filename)
    name = path.name
    return (
        name in DEPENDENCY_FILE_NAMES
        or REQUIREMENTS_FILE_PATTERN.fullmatch(name) is not None
        or CONSTRAINTS_FILE_PATTERN.fullmatch(name) is not None
        or ("requirements" in path.parts[:-1] and path.suffix == ".txt")
    )


def _validate_action_update(record: Mapping[str, object], filename: str) -> list[str]:
    issues: list[str] = []
    if record.get("status") != "modified":
        return [f"Dependabot workflow update must modify an existing file: {filename}"]
    patch = record.get("patch")
    if not isinstance(patch, str) or not patch:
        return [f"Dependabot workflow update requires a complete patch: {filename}"]

    removed: list[str] = []
    added: list[str] = []
    for line in patch.splitlines():
        destination = added if line.startswith("+") else removed if line.startswith("-") else None
        if destination is None or line.startswith(("+++", "---")):
            continue
        changed = line[1:].strip()
        match = PINNED_ACTION_CHANGE_PATTERN.fullmatch(changed)
        if match is None:
            issues.append(
                f"Dependabot workflow update changes more than a pinned Action: {filename}"
            )
            continue
        destination.append(match.group("action"))

    if not added or not removed or Counter(added) != Counter(removed):
        issues.append(
            f"Dependabot workflow update must replace the same pinned Actions: {filename}"
        )
    additions = record.get("additions")
    deletions = record.get("deletions")
    if (
        not isinstance(additions, int)
        or isinstance(additions, bool)
        or not isinstance(deletions, int)
        or isinstance(deletions, bool)
        or additions != len(added)
        or deletions != len(removed)
    ):
        issues.append(f"Dependabot workflow patch is incomplete: {filename}")
    return issues


def _validate_dependabot_files(
    files: tuple[Mapping[str, object], ...], expected_count: object
) -> list[str]:
    issues: list[str] = []
    if (
        not isinstance(expected_count, int)
        or isinstance(expected_count, bool)
        or expected_count != len(files)
    ):
        issues.append("Dependabot changed_files does not match the fetched file list")
    for record in files:
        filename = record.get("filename")
        if not isinstance(filename, str) or not filename:
            issues.append("Dependabot file record requires a filename")
            continue
        path = PurePosixPath(filename)
        if path.is_absolute() or ".." in path.parts or str(path) != filename:
            issues.append(f"Dependabot file path is unsafe: {filename}")
            continue
        if record.get("previous_filename") is not None:
            issues.append(f"Dependabot must not rename files: {filename}")
            continue
        if path.parent == PurePosixPath(".github/workflows") and path.suffix in {
            ".yml",
            ".yaml",
        }:
            issues.extend(_validate_action_update(record, filename))
        elif _is_dependency_file(filename):
            if record.get("status") not in {"added", "modified"}:
                issues.append(f"Dependabot dependency file has disallowed status: {filename}")
        else:
            issues.append(f"Dependabot changed a file outside the dependency allowlist: {filename}")
    return issues


def _repository_name(reference: object) -> str | None:
    if not isinstance(reference, Mapping):
        return None
    repository = reference.get("repo")
    if not isinstance(repository, Mapping):
        return None
    full_name = repository.get("full_name")
    return full_name if isinstance(full_name, str) and full_name else None


def validate_dependabot_pr(
    pull_request: Mapping[str, object],
    files_path: Path | None,
    policy: LifecyclePolicy,
) -> PullRequestValidation:
    draft = pull_request.get("draft")
    if not isinstance(draft, bool):
        raise LifecycleError("pull_request.draft must be a boolean")
    issues: list[str] = []
    user = pull_request.get("user")
    if not isinstance(user, Mapping) or user.get("type") != "Bot":
        issues.append("Dependabot PR author must have GitHub user type Bot")
    head = pull_request.get("head")
    base = pull_request.get("base")
    head_ref = head.get("ref") if isinstance(head, Mapping) else None
    base_ref = base.get("ref") if isinstance(base, Mapping) else None
    if not isinstance(head_ref, str) or not head_ref.startswith(DEPENDABOT_BRANCH_PREFIX):
        issues.append("Dependabot PR head branch must use the dependabot/ prefix")
    if base_ref != policy.default_branch:
        issues.append("Dependabot PR must target the lifecycle policy default branch")
    head_repository = _repository_name(head)
    base_repository = _repository_name(base)
    if head_repository is None or head_repository != base_repository:
        issues.append("Dependabot PR must originate from the base repository")

    if files_path is None:
        issues.append("Dependabot PR validation requires the complete changed-file list")
    else:
        files = _load_pull_request_files(files_path)
        issues.extend(_validate_dependabot_files(files, pull_request.get("changed_files")))
    return PullRequestValidation(
        draft=draft,
        risk_level="low",
        issues=tuple(issues),
        record_source="dependabot-restricted",
    )


def validate_pr_event(
    path: Path, policy: LifecyclePolicy, files_path: Path | None = None
) -> PullRequestValidation:
    event = load_json_mapping(path, "GitHub event")
    pull_request = event.get("pull_request")
    if not isinstance(pull_request, Mapping):
        raise LifecycleError("GitHub event must contain a pull_request object")
    user = pull_request.get("user")
    if isinstance(user, Mapping) and user.get("login") == DEPENDABOT_LOGIN:
        return validate_dependabot_pr(pull_request, files_path, policy)
    body = pull_request.get("body")
    draft = pull_request.get("draft")
    if body is None:
        body = ""
    if not isinstance(body, str):
        raise LifecycleError("pull_request.body must be a string or null")
    if not isinstance(draft, bool):
        raise LifecycleError("pull_request.draft must be a boolean")
    return validate_pr_body(body, draft, policy)
