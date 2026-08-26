from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

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


@dataclass(frozen=True)
class PullRequestValidation:
    draft: bool
    risk_level: str | None
    issues: tuple[str, ...]

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


def validate_pr_event(path: Path, policy: LifecyclePolicy) -> PullRequestValidation:
    event = load_json_mapping(path, "GitHub event")
    pull_request = event.get("pull_request")
    if not isinstance(pull_request, Mapping):
        raise LifecycleError("GitHub event must contain a pull_request object")
    body = pull_request.get("body")
    draft = pull_request.get("draft")
    if body is None:
        body = ""
    if not isinstance(body, str):
        raise LifecycleError("pull_request.body must be a string or null")
    if not isinstance(draft, bool):
        raise LifecycleError("pull_request.draft must be a boolean")
    return validate_pr_body(body, draft, policy)
