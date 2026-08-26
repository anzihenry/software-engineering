from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


class LifecycleError(ValueError):
    """Raised when lifecycle automation input violates the public contract."""


@dataclass(frozen=True)
class LifecyclePolicy:
    schema_version: int
    default_branch: str
    pr_check_name: str
    release_required_checks: tuple[str, ...]
    risk_levels: tuple[str, ...]
    incident_severities: tuple[str, ...]
    retrospective_deadlines_days: Mapping[str, int | None]
    labels: tuple[str, ...]


POLICY_KEYS = {
    "schema_version",
    "default_branch",
    "pr_check_name",
    "release_required_checks",
    "risk_levels",
    "incident_severities",
    "retrospective_deadlines_days",
    "labels",
}


def load_json_mapping(path: Path, label: str) -> Mapping[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise LifecycleError(f"cannot read {label}: {error}") from error
    if not isinstance(value, Mapping):
        raise LifecycleError(f"{label} must be a JSON object")
    return value


def require_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LifecycleError(f"{field} must be a non-empty string")
    return value


def require_unique_strings(value: object, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise LifecycleError(f"{field} must be a non-empty array")
    items = tuple(require_string(item, f"{field} item") for item in value)
    if len(items) != len(set(items)):
        raise LifecycleError(f"{field} must not contain duplicates")
    return items


def load_policy(path: Path) -> LifecyclePolicy:
    raw = load_json_mapping(path, "lifecycle policy")
    unknown = set(raw) - POLICY_KEYS
    missing = POLICY_KEYS - set(raw)
    if unknown:
        raise LifecycleError(
            f"lifecycle policy contains unknown keys: {', '.join(sorted(unknown))}"
        )
    if missing:
        raise LifecycleError(f"lifecycle policy is missing keys: {', '.join(sorted(missing))}")
    if raw["schema_version"] != 1:
        raise LifecycleError("lifecycle policy schema_version must be 1")

    risk_levels = require_unique_strings(raw["risk_levels"], "risk_levels")
    if set(risk_levels) != {"low", "medium", "high"}:
        raise LifecycleError("risk_levels must contain low, medium, and high")
    severities = require_unique_strings(raw["incident_severities"], "incident_severities")
    if set(severities) != {"sev1", "sev2", "sev3", "sev4"}:
        raise LifecycleError("incident_severities must contain sev1 through sev4")

    raw_deadlines = raw["retrospective_deadlines_days"]
    if not isinstance(raw_deadlines, Mapping):
        raise LifecycleError("retrospective_deadlines_days must be an object")
    if set(raw_deadlines) != {*severities, "release"}:
        raise LifecycleError("retrospective_deadlines_days must cover every severity and release")
    deadlines: dict[str, int | None] = {}
    for key, value in raw_deadlines.items():
        if value is not None and (
            not isinstance(value, int) or isinstance(value, bool) or value < 1
        ):
            raise LifecycleError(f"retrospective_deadlines_days.{key} must be positive or null")
        deadlines[str(key)] = value

    return LifecyclePolicy(
        schema_version=1,
        default_branch=require_string(raw["default_branch"], "default_branch"),
        pr_check_name=require_string(raw["pr_check_name"], "pr_check_name"),
        release_required_checks=require_unique_strings(
            raw["release_required_checks"], "release_required_checks"
        ),
        risk_levels=risk_levels,
        incident_severities=severities,
        retrospective_deadlines_days=deadlines,
        labels=require_unique_strings(raw["labels"], "labels"),
    )
