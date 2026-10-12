"""Validate domain evidence against an independently controlled project policy."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

from scripts.documentation_check import local, read_json

DOMAINS = frozenset(
    {
        "contract",
        "data",
        "concurrency",
        "recovery",
        "authorization",
        "browser",
        "visual-accessibility",
        "web-performance",
        "system",
    }
)


def json_equal(observed: object, expected: object) -> bool:
    """JSON booleans are distinct from numbers, including inside containers."""
    if isinstance(observed, bool) or isinstance(expected, bool):
        return type(observed) is type(expected) and observed == expected
    if isinstance(expected, dict):
        return (
            isinstance(observed, dict)
            and observed.keys() == expected.keys()
            and all(json_equal(observed[k], v) for k, v in expected.items())
        )
    if isinstance(expected, list):
        return (
            isinstance(observed, list)
            and len(observed) == len(expected)
            and all(json_equal(a, b) for a, b in zip(observed, expected, strict=True))
        )
    return observed == expected


def _evaluate(root: Path, report: dict, policy: dict) -> dict:
    """Check consistency, never authenticate execution, policy ownership or approval."""
    if not isinstance(report, dict) or not isinstance(policy, dict):
        raise ValueError("object report and policy required")
    root = root.resolve()
    errors: list[str] = []
    results: dict[str, str] = {}
    if any(
        type(d.get("schema_version")) is not int or d["schema_version"] != 1
        for d in (report, policy)
    ):
        return {"state": "blocked", "errors": ["unsupported domain schema"], "cases": {}}
    if not re.fullmatch(r"[a-f0-9]{40}|[a-f0-9]{64}", str(policy.get("source_version", ""))):
        errors.append("complete source identity required")
    if not isinstance(policy.get("authors"), list) or not policy["authors"]:
        errors.append("actual authors required")
    for key in ("source_version", "environment", "support"):
        if not policy.get(key) or report.get(key) != policy[key]:
            errors.append(f"stale or missing {key}")
    domains = policy.get("domains", {})
    if not isinstance(domains, dict):
        raise ValueError("domain inventory must be an object")
    if set(domains) != DOMAINS:
        errors.append("complete domain admission inventory required")
    for name, admission in domains.items():
        if (
            not isinstance(admission, dict)
            or not isinstance(admission.get("applicable"), bool)
            or not admission.get("reason")
        ):
            errors.append(f"invalid applicability: {name}")
    expected = policy.get("cases", {})
    observed = report.get("cases", {})
    if not isinstance(expected, dict) or not expected or not isinstance(observed, dict):
        return {"state": "blocked", "errors": errors + ["cases required"], "cases": {}}
    if any(not isinstance(c, dict) for c in expected.values()):
        raise ValueError("policy cases must be objects")
    admission = policy.get("admission", [])
    if not isinstance(admission, list) or not admission:
        raise ValueError("clause-level admission inventory required")
    indexed = {}
    for row in admission:
        if not isinstance(row, dict) or not isinstance(row.get("applicable"), bool):
            raise ValueError("invalid clause applicability")
        identifier = row.get("id")
        if not isinstance(identifier, str) or identifier in indexed:
            raise ValueError("unique clause IDs required")
        if not all(row.get(k) for k in ("trigger", "reason", "owner", "failure_action", "source")):
            raise ValueError("clause facts, ownership, source and failure action required")
        cases = row.get("cases")
        if not isinstance(cases, list) or not set(cases) <= set(expected):
            raise ValueError("invalid clause scenario mapping")
        if row["applicable"] and not cases:
            raise ValueError("applicable clause has no scenario")
        if not row["applicable"] and cases:
            raise ValueError("inapplicable clause cannot claim execution")
        indexed[identifier] = row
    for name, requirement in expected.items():
        for identifier in requirement.get("requirements", []):
            row = indexed.get(identifier)
            if not row or not row["applicable"] or name not in row["cases"]:
                raise ValueError("case is not admitted by source clause")
    for identifier, row in indexed.items():
        if row["applicable"] and any(
            identifier not in expected[name].get("requirements", []) for name in row["cases"]
        ):
            raise ValueError("clause mapping is not bidirectional")
    if set(expected) != set(observed):
        errors.append("missing or unexpected cases")
    for domain, admission in domains.items():
        if (
            isinstance(admission, dict)
            and admission.get("applicable")
            and not any(c.get("domain") == domain for c in expected.values())
        ):
            errors.append(f"applicable domain has no cases: {domain}")
    for name, requirement in expected.items():
        case = observed.get(name, {})
        if not isinstance(requirement, dict) or not isinstance(case, dict):
            errors.append(f"invalid case: {name}")
            results[name] = "blocked"
            continue
        state = "passed"
        if (
            not isinstance(requirement.get("requirements"), list)
            or not requirement["requirements"]
            or any(
                not re.fullmatch(r"REQ-[a-f0-9]{16}", str(i)) for i in requirement["requirements"]
            )
            or requirement.get("domain") not in DOMAINS
            or sum(k in requirement for k in ("equals", "maximum")) != 1
        ):
            errors.append(f"invalid policy case: {name}")
            results[name] = "blocked"
            continue
        if case.get("state") != "passed" or case.get("execution") != "real":
            state = "blocked"
        evidence = case.get("evidence", [])
        if not isinstance(evidence, list):
            raise ValueError("evidence must be a list")
        if not evidence:
            state = "blocked"
        for item in evidence:
            try:
                path = local(root, item["path"])
                if (
                    not path.is_file()
                    or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]
                ):
                    state = "blocked"
            except ValueError, KeyError, TypeError, OSError:
                state = "blocked"
        if "equals" in requirement and not json_equal(case.get("observed"), requirement["equals"]):
            state = "failed"
        if "maximum" in requirement:
            value = case.get("observed")
            limit = requirement["maximum"]
            if (
                any(
                    isinstance(v, bool)
                    or not isinstance(v, (int, float))
                    or (isinstance(v, float) and not math.isfinite(v))
                    or v < 0
                    for v in (value, limit)
                )
                or value > limit
            ):
                state = "failed"
        if requirement.get("review_required"):
            review = case.get("review", {})
            if not isinstance(review, dict):
                raise ValueError("review must be an object")
            if (
                review.get("state") != "passed"
                or not review.get("reviewer")
                or review.get("reviewer") in policy.get("authors", [])
                or review.get("source_version") != policy.get("source_version")
            ):
                state = "blocked"
        results[name] = state
    state = (
        "blocked"
        if errors or "blocked" in results.values()
        else ("failed" if "failed" in results.values() else "passed")
    )
    return {"state": state, "errors": errors, "cases": results}


def evaluate(root: Path, report: dict, policy: dict) -> dict:
    """Return a blocking result for unsupported or malformed boundary inputs."""
    try:
        return _evaluate(root, report, policy)
    except (ValueError, TypeError, KeyError, OSError) as error:
        return {"state": "blocked", "errors": [str(error)], "cases": {}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = evaluate(args.root.resolve(), read_json(args.report), read_json(args.policy))
    except (ValueError, OSError) as error:
        result = {"state": "blocked", "errors": [str(error)], "cases": {}}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["state"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
