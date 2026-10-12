"""Evaluate gate readiness against caller-controlled policy; do not grant authority."""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path

NODES = {"local", "review", "merge", "initiative", "candidate", "production", "batch", "closure"}
CATEGORIES = {
    "required",
    "ci",
    "documentation",
    "translation",
    "evidence",
    "independence",
    "authorization",
    "optional",
}
STATES = {"passed", "failed", "not-run", "blocked", "stale", "not-applicable"}
CONDITIONAL_NODES = {"local", "review", "batch"}


def timestamp(value: str) -> datetime:
    result = datetime.fromisoformat(value)
    if result.utcoffset() is None:
        raise ValueError("timezone required")
    return result


def evaluate(record: dict, policy: dict, now: datetime) -> dict:
    """Policy must come from a trusted maintainer, never a candidate declaration."""
    if not isinstance(record, dict) or not isinstance(policy, dict):
        raise ValueError("record and policy must be objects")
    blockers = []
    if not isinstance(record.get("scope"), str) or not record["scope"].strip():
        raise ValueError("scope required")
    if not re.fullmatch(r"[a-f0-9]{40}|[a-f0-9]{64}", record.get("source_version", "")):
        raise ValueError("immutable source version required")
    if now.utcoffset() is None:
        raise ValueError("timezone required for evaluation")
    node = policy.get("node")
    if node not in NODES or record.get("node") != node:
        raise ValueError("gate node mismatch")
    expected = policy["checks"]
    checks = record["checks"]
    if (
        not isinstance(expected, dict)
        or not isinstance(checks, dict)
        or not expected
        or set(checks) != set(expected)
        or not all(isinstance(k, str) and k.strip() for k in expected)
    ):
        raise ValueError("complete policy check set required")
    rules = policy.get("exception_rules", {})
    na = policy.get("not_applicable", [])
    if (
        not isinstance(rules, dict)
        or not set(rules) <= set(expected)
        or not isinstance(na, list)
        or not all(isinstance(k, str) and k in expected for k in na)
        or not all(
            isinstance(people, list)
            and people
            and all(isinstance(p, str) and p.strip() for p in people)
            for people in rules.values()
        )
    ):
        raise ValueError("invalid controlled applicability/authority policy")
    exceptions = record.get("exceptions", {})
    if not isinstance(exceptions, dict) or not set(exceptions) <= set(expected):
        raise ValueError("unknown exception")
    conditional = False
    for name, category in expected.items():
        if not isinstance(checks[name], dict) or not isinstance(exceptions.get(name, {}), dict):
            raise ValueError("check and exception must be objects")
        state = checks[name]["state"]
        if not isinstance(category, str) or not isinstance(state, str):
            raise ValueError("category and state must be strings")
        if category not in CATEGORIES or state not in STATES:
            raise ValueError("invalid category or result")
        if state == "not-applicable":
            if (
                category == "ci"
                or not isinstance(checks[name].get("reason"), str)
                or not checks[name]["reason"].strip()
                or not isinstance(checks[name].get("basis"), str)
                or not checks[name]["basis"].strip()
                or name not in na
                or name in exceptions
            ):
                blockers.append(name + ": applicability not established")
            continue
        if state == "passed":
            if name in exceptions:
                blockers.append(name + ": exception contradicts passed result")
            continue
        exception = exceptions.get(name, {})
        allowed = rules.get(name, [])
        valid = False
        if category == "optional" and allowed and state == "failed" and exception:
            try:
                valid = (
                    exception["authority"] in allowed
                    and exception["authority_kind"] == "human"
                    and exception["node"] == node
                    and exception["scope"] == record["scope"]
                    and exception["source_version"] == record["source_version"]
                    and exception["revoked"] is False
                    and timestamp(exception["decided_at"])
                    <= now
                    < timestamp(exception["expires_at"])
                    and all(
                        isinstance(exception.get(k), str) and exception[k].strip()
                        for k in (
                            "rule_id",
                            "basis",
                            "reason",
                            "risk",
                            "remediation",
                            "revoke_when",
                            "recheck_when",
                        )
                    )
                )
            except KeyError, TypeError, ValueError:
                valid = False
        if valid:
            conditional = True
        else:
            blockers.append(name + ": " + state + "; no valid permitted exception")
    readiness = "blocked" if blockers else "conditional" if conditional else "passed"
    may_advance = readiness == "passed" or (
        readiness == "conditional" and node in CONDITIONAL_NODES
    )
    return {
        "node": node,
        "checks": checks,
        "readiness": readiness,
        "may_advance": may_advance,
        "advance_scope": record.get("scope") if may_advance else None,
        "authorization": "separate trusted decision required",
        "blockers": blockers,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = evaluate(
            json.loads(args.record.read_text(encoding="utf-8")),
            json.loads(args.policy.read_text(encoding="utf-8")),
            datetime.now(UTC),
        )
    except (OSError, KeyError, TypeError, ValueError) as error:
        print(json.dumps({"readiness": "blocked", "error": str(error)}))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(not result["may_advance"])


if __name__ == "__main__":
    raise SystemExit(main())
