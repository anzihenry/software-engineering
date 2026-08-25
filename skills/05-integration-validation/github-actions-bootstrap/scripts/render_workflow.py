#!/usr/bin/env python3
"""Render a stable GitHub Actions CI workflow from a validated JSON plan."""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

ACTION_SHA_PATTERN = re.compile(r"^[^@\s]+@[0-9a-fA-F]{40}$")
SAFE_BRANCH_PATTERN = re.compile(r"^[A-Za-z0-9._/-]+$")
ALLOWED_PLAN_KEYS = {
    "schema_version",
    "workflow_name",
    "default_branch",
    "runner",
    "timeout_minutes",
    "merge_group",
    "steps",
}
ALLOWED_STEP_KEYS = {"name", "uses", "run", "with", "env"}


class PlanError(ValueError):
    """Raised when a workflow plan violates the renderer contract."""


def yaml_string(value: str) -> str:
    """Return a JSON-quoted string, which is also a valid YAML scalar."""
    return json.dumps(value, ensure_ascii=False)


def require_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PlanError(f"{field} must be a non-empty string")
    return value


def require_string_mapping(value: object, field: str) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise PlanError(f"{field} must be an object")
    result: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise PlanError(f"{field} keys must be non-empty strings")
        if not isinstance(item, str):
            raise PlanError(f"{field}.{key} must be a string")
        result[key] = item
    return result


def validate_step(raw_step: object, index: int) -> dict[str, Any]:
    field = f"steps[{index}]"
    if not isinstance(raw_step, Mapping):
        raise PlanError(f"{field} must be an object")
    unknown = set(raw_step) - ALLOWED_STEP_KEYS
    if unknown:
        raise PlanError(f"{field} contains unknown keys: {', '.join(sorted(unknown))}")

    step: dict[str, Any] = {"name": require_string(raw_step.get("name"), f"{field}.name")}
    has_uses = "uses" in raw_step
    has_run = "run" in raw_step
    if has_uses == has_run:
        raise PlanError(f"{field} must contain exactly one of uses or run")
    if has_uses:
        uses = require_string(raw_step["uses"], f"{field}.uses")
        if not uses.startswith("./") and not ACTION_SHA_PATTERN.fullmatch(uses):
            raise PlanError(f"{field}.uses must be local or pinned to a full 40-character SHA")
        step["uses"] = uses
    else:
        step["run"] = require_string(raw_step["run"], f"{field}.run")

    if "with" in raw_step:
        if not has_uses:
            raise PlanError(f"{field}.with is only valid for action steps")
        step["with"] = require_string_mapping(raw_step["with"], f"{field}.with")
    if "env" in raw_step:
        step["env"] = require_string_mapping(raw_step["env"], f"{field}.env")
    return step


def validate_plan(raw_plan: object) -> dict[str, Any]:
    if not isinstance(raw_plan, Mapping):
        raise PlanError("plan must be a JSON object")
    unknown = set(raw_plan) - ALLOWED_PLAN_KEYS
    if unknown:
        raise PlanError(f"plan contains unknown keys: {', '.join(sorted(unknown))}")
    if raw_plan.get("schema_version") != 1:
        raise PlanError("schema_version must be 1")

    default_branch = require_string(raw_plan.get("default_branch"), "default_branch")
    if not SAFE_BRANCH_PATTERN.fullmatch(default_branch) or ".." in default_branch:
        raise PlanError("default_branch contains unsupported characters")
    timeout = raw_plan.get("timeout_minutes", 15)
    if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 360:
        raise PlanError("timeout_minutes must be an integer between 1 and 360")
    merge_group = raw_plan.get("merge_group", False)
    if not isinstance(merge_group, bool):
        raise PlanError("merge_group must be a boolean")
    raw_steps = raw_plan.get("steps")
    if not isinstance(raw_steps, Sequence) or isinstance(raw_steps, (str, bytes)) or not raw_steps:
        raise PlanError("steps must be a non-empty array")

    return {
        "workflow_name": require_string(raw_plan.get("workflow_name", "CI"), "workflow_name"),
        "default_branch": default_branch,
        "runner": require_string(raw_plan.get("runner", "ubuntu-latest"), "runner"),
        "timeout_minutes": timeout,
        "merge_group": merge_group,
        "steps": [validate_step(step, index) for index, step in enumerate(raw_steps)],
    }


def render_mapping(lines: list[str], key: str, values: Mapping[str, str], indent: int) -> None:
    prefix = " " * indent
    lines.append(f"{prefix}{key}:")
    for item_key in sorted(values):
        lines.append(f"{prefix}  {item_key}: {yaml_string(values[item_key])}")


def render_workflow(plan: Mapping[str, Any]) -> str:
    lines = [
        f"name: {yaml_string(plan['workflow_name'])}",
        "",
        '"on":',
        "  pull_request:",
        "  push:",
        "    branches:",
        f"      - {yaml_string(plan['default_branch'])}",
    ]
    if plan["merge_group"]:
        lines.append("  merge_group:")
    lines.extend(
        [
            "",
            "permissions:",
            "  contents: read",
            "",
            "concurrency:",
            '  group: "ci-${{ github.event.pull_request.number || github.ref }}"',
            "  cancel-in-progress: true",
            "",
            "jobs:",
            "  validate:",
            '    name: "validate"',
            f"    runs-on: {yaml_string(plan['runner'])}",
            f"    timeout-minutes: {plan['timeout_minutes']}",
            "    steps:",
        ]
    )
    for step in plan["steps"]:
        lines.append(f"      - name: {yaml_string(step['name'])}")
        if "uses" in step:
            lines.append(f"        uses: {yaml_string(step['uses'])}")
        else:
            command_lines = step["run"].splitlines()
            if len(command_lines) == 1:
                lines.append(f"        run: {yaml_string(command_lines[0])}")
            else:
                lines.append("        run: |")
                lines.extend(f"          {command_line}" for command_line in command_lines)
        if "with" in step:
            render_mapping(lines, "with", step["with"], 8)
        if "env" in step:
            render_mapping(lines, "env", step["env"], 8)
    return "\n".join(lines) + "\n"


def load_plan(path: Path) -> dict[str, Any]:
    try:
        raw_plan = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PlanError(f"cannot read plan: {error}") from error
    return validate_plan(raw_plan)


def write_workflow(path: Path, content: str, *, force: bool) -> None:
    if path.exists() and not force:
        raise PlanError(f"output already exists: {path}; pass --force only after reviewing it")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True, help="JSON plan path")
    parser.add_argument("--output", type=Path, required=True, help="workflow output path")
    parser.add_argument("--force", action="store_true", help="overwrite an existing output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        plan = load_plan(args.plan)
        write_workflow(args.output, render_workflow(plan), force=args.force)
    except PlanError as error:
        raise SystemExit(f"error: {error}") from error
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
