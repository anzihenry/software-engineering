"""Read-only harness observations; consistency is not execution authentication."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from scripts.documentation_check import local, read_json
from scripts.domain_validation import evaluate

TRIGGERS = frozenset(
    {
        "entry",
        "knowledge",
        "requirements",
        "commands",
        "dependencies",
        "environment",
        "support",
        "roles",
        "permissions",
        "rules",
    }
)


def timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("timezone required")
    return parsed.astimezone(UTC)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reference(root: Path, value: dict) -> Path:
    path = local(root, value["path"])
    if not path.is_file() or digest(path) != value["sha256"]:
        raise ValueError("missing or changed raw observation")
    return path


def capture(root: Path, policy_path: Path, report_path: Path, attempt: int) -> dict:
    """Actually time the domain reader; never label it CI or product latency."""
    if type(attempt) is not int or attempt < 1:
        raise ValueError("positive attempt required")
    paths = (policy_path, report_path)
    before = [digest(p) for p in paths]
    policy, report = (read_json(p) for p in paths)
    started = datetime.now(UTC).isoformat()
    timer = time.perf_counter()
    result = evaluate(root, report, policy)
    elapsed = (time.perf_counter() - timer) * 1000
    finished = datetime.now(UTC).isoformat()
    if before != [digest(p) for p in paths]:
        raise ValueError("input changed during observation")
    raw = [
        {"path": p.resolve().relative_to(root.resolve()).as_posix(), "sha256": sha}
        for p, sha in zip(paths, before, strict=True)
    ]
    event = {
        "schema_version": 1,
        "kind": "domain-reader",
        "attempt": attempt,
        "started_at": started,
        "finished_at": finished,
        "duration_ms": elapsed,
        "source_version": policy.get("source_version"),
        "policy_sha256": before[0],
        "raw": raw,
        "result": result,
    }
    event["id"] = hashlib.sha256(json.dumps(event, sort_keys=True).encode()).hexdigest()
    return event


def _summarize(root: Path, events: list, config: dict) -> dict:
    if type(config.get("schema_version")) is not int or config["schema_version"] != 1:
        raise ValueError("unsupported metrics schema")
    start, end = (timestamp(config[k]) for k in ("from", "until"))
    if start >= end:
        raise ValueError("empty or inverted window")
    if not config.get("owner"):
        raise ValueError("actual metric owner required")
    seen, attempts, cohorts = {}, set(), {}
    duplicates = outside = 0
    for event in events:
        if type(event.get("schema_version")) is not int or event["schema_version"] != 1:
            raise ValueError("unsupported event schema")
        identifier = event["id"]
        if identifier in seen:
            if event != seen[identifier]:
                raise ValueError("conflicting duplicate event")
            duplicates += 1
            continue
        seen[identifier] = event
        payload = {k: v for k, v in event.items() if k != "id"}
        if hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest() != identifier:
            raise ValueError("event identity mismatch")
        began, ended = (timestamp(event[k]) for k in ("started_at", "finished_at"))
        elapsed = event["duration_ms"]
        if (
            event["kind"] != "domain-reader"
            or type(event["attempt"]) is not int
            or event["attempt"] < 1
            or ended < began
            or isinstance(elapsed, bool)
            or not isinstance(elapsed, (int, float))
            or (isinstance(elapsed, float) and not math.isfinite(elapsed))
            or elapsed < 0
        ):
            raise ValueError("invalid execution timing or attempt")
        policy_path, report_path = (reference(root, r) for r in event["raw"])
        policy, report = read_json(policy_path), read_json(report_path)
        if event["policy_sha256"] != digest(policy_path):
            raise ValueError("policy binding mismatch")
        if event["source_version"] != policy.get("source_version"):
            raise ValueError("source binding mismatch")
        result = evaluate(root, report, policy)
        if event["result"] != result:
            raise ValueError("observation cannot be reproduced")
        applicable = {r["id"] for r in policy["admission"] if r["applicable"]}
        if any(not re.fullmatch(r"REQ-[a-f0-9]{16}", r) for r in applicable):
            raise ValueError("invalid requirement population")
        valid = {
            row["id"]
            for row in policy["admission"]
            if row["applicable"]
            and row["cases"]
            and all(result["cases"].get(name) == "passed" for name in row["cases"])
        }
        if result["errors"]:
            valid = set()
        if not start <= ended < end:
            outside += 1
            continue
        key = event["policy_sha256"]
        attempt_key = (key, event["attempt"])
        if attempt_key in attempts:
            raise ValueError("different events reuse an attempt within a policy cohort")
        attempts.add(attempt_key)
        row = cohorts.setdefault(key, {"source_version": event["source_version"], "samples": []})
        row["samples"].append(
            {
                "id": identifier,
                "attempt": event["attempt"],
                "finished_at": ended.isoformat(),
                "state": result["state"],
                "duration_ms": elapsed,
                "coverage": {
                    "numerator": len(valid),
                    "denominator": len(applicable),
                    "fraction": len(valid) / len(applicable) if applicable else None,
                },
                "blocked_cases": sorted(k for k, v in result["cases"].items() if v != "passed"),
                "errors": result["errors"],
                "authors": policy["authors"],
            }
        )
    included = {s["id"]: s for c in cohorts.values() for s in c["samples"]}
    reviews, reviewed = [], set()
    for item in config.get("block_reviews", []):
        record = read_json(reference(root, item))
        sample = included.get(record["event_id"])
        if (
            not sample
            or sample["state"] not in {"blocked", "failed"}
            or record["event_id"] in reviewed
            or not record.get("reviewer")
            or record["reviewer"] in sample["authors"]
            or record.get("classification") not in {"false-block", "correct-block"}
            or not record.get("reason")
        ):
            raise ValueError("invalid independent blocked-sample review")
        if not timestamp(sample["finished_at"]) <= timestamp(record["reviewed_at"]) <= end:
            raise ValueError("review predates sample or exceeds observation cutoff")
        reviewed.add(record["event_id"])
        reviews.append(record)
    for row in cohorts.values():
        row["samples"].sort(key=lambda s: s["finished_at"])
        row["reruns"] = max(0, len(row["samples"]) - 1)
        row["states"] = dict(Counter(s["state"] for s in row["samples"]))
    false = sum(r["classification"] == "false-block" for r in reviews)
    gaps = config.get("collection_gaps", [])
    gap_ids = set()
    for gap in gaps:
        if gap.get("state") not in {"cancelled", "collection-failed", "unknown"} or not all(
            gap.get(k) for k in ("id", "reason", "owner", "source_version", "recorded_at")
        ):
            raise ValueError("explicit classified collection gap required")
        if gap["id"] in gap_ids or not gap.get("evidence"):
            raise ValueError("unique collection gap with raw evidence required")
        gap_ids.add(gap["id"])
        if not start <= timestamp(gap["recorded_at"]) < end:
            raise ValueError("collection gap outside observation window")
        for evidence in gap["evidence"]:
            reference(root, evidence)
    return {
        "state": "observed" if included else "no-data",
        "schema_version": 1,
        "owner": config["owner"],
        "window": {"from": start.isoformat(), "until": end.isoformat()},
        "cohorts": cohorts,
        "duplicates": duplicates,
        "outside_window": outside,
        "false_block_sample": {
            "numerator": false,
            "denominator": len(reviews),
            "fraction": false / len(reviews) if reviews else None,
        },
        "blocked_unreviewed": sum(
            s["state"] != "passed" and k not in reviewed for k, s in included.items()
        ),
        "reviewed_block_reasons": dict(Counter(r["reason"] for r in reviews)),
        "revalidation": revalidation(root, config.get("revalidation", []), end),
        "limitations": [
            "reader consistency timing only; no CI/product SLO or causal improvement",
            "separate policy cohorts; reviewed sample is not population false-block rate",
            "hashes and reviewer labels do not authenticate origin; independent review required",
            "cancelled or collection failure has no domain-reader event; record a collection gap",
        ],
        "collection_gaps": gaps,
    }


def revalidation(root: Path, objects: list, at: datetime) -> list[dict]:
    results, identifiers = [], set()
    for obj in objects:
        if obj["id"] in identifiers or not all(obj.get(k) for k in ("owner", "remedy", "effect")):
            raise ValueError("unique revalidation object, owner, remedy and effect required")
        identifiers.add(obj["id"])
        if set(obj["baseline"]) != TRIGGERS or set(obj["current"]) != TRIGGERS:
            raise ValueError("complete controlled revalidation fingerprint required")
        if any(
            not isinstance(v, str) or not v
            for d in (obj["baseline"], obj["current"])
            for v in d.values()
        ):
            raise ValueError("empty fingerprint")
        due, review_by = timestamp(obj["due_at"]), timestamp(obj["review_by"])
        current_since = timestamp(obj["current_since"])
        if current_since > at or due < current_since:
            raise ValueError("future fingerprint or due before change")
        if not isinstance(obj["authors"], list) or not obj["authors"]:
            raise ValueError("actual revalidation authors required")
        reasons = sorted(k for k in TRIGGERS if obj["baseline"][k] != obj["current"][k])
        if review_by <= at:
            reasons.append("review-due")
        closed = False
        if obj.get("closure"):
            closure = read_json(reference(root, obj["closure"]))
            closed = (
                closure.get("state") == "passed"
                and closure.get("fingerprint") == obj["current"]
                and bool(closure.get("reviewer"))
                and closure["reviewer"] not in obj["authors"]
                and timestamp(closure["verified_at"]) >= current_since
                and (review_by > at or timestamp(closure["verified_at"]) >= review_by)
                and timestamp(closure["verified_at"]) <= at
                and bool(closure.get("evidence"))
            )
            for evidence in closure.get("evidence", []):
                reference(root, evidence)
        results.append(
            {
                "id": obj["id"],
                "owner": obj["owner"],
                "reasons": reasons,
                "state": "closed" if closed else ("required" if reasons else "current"),
                "overdue": bool(reasons and not closed and due < at),
                "due_at": due.isoformat(),
                "remedy": obj["remedy"],
                "effect": obj["effect"],
            }
        )
    return results


def summarize(root: Path, events: list, config: dict) -> dict:
    try:
        return _summarize(root.resolve(), events, config)
    except (ValueError, TypeError, KeyError, OSError, AttributeError) as error:
        return {"state": "blocked", "errors": [str(error)]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    collect = sub.add_parser("capture")
    collect.add_argument("--root", type=Path, required=True)
    collect.add_argument("--policy", type=Path, required=True)
    collect.add_argument("--report", type=Path, required=True)
    collect.add_argument("--attempt", type=int, required=True)
    report = sub.add_parser("summarize")
    report.add_argument("--root", type=Path, required=True)
    report.add_argument("--config", type=Path, required=True)
    report.add_argument("--events", type=Path, nargs="+", required=True)
    args = parser.parse_args()
    try:
        result = (
            capture(args.root, args.policy, args.report, args.attempt)
            if args.command == "capture"
            else summarize(args.root, [read_json(p) for p in args.events], read_json(args.config))
        )
    except (ValueError, TypeError, KeyError, OSError, AttributeError) as error:
        result = {"state": "blocked", "errors": [str(error)]}
    print(json.dumps(result, ensure_ascii=False))
    return 1 if result.get("state") == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
