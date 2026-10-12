from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.domain_validation import DOMAINS
from scripts.harness_metrics import TRIGGERS, capture, digest, summarize


class HarnessMetricsTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.write("raw.json", {"status": 200})
        self.policy = {
            "schema_version": 1,
            "source_version": "a" * 40,
            "authors": ["author"],
            "environment": {"kind": "test"},
            "support": {"scope": "test"},
            "domains": {
                d: {"applicable": d == "contract", "reason": "test scope"} for d in DOMAINS
            },
            "admission": [
                {
                    "id": "REQ-0000000000000001",
                    "applicable": True,
                    "source": "test",
                    "owner": "owner",
                    "trigger": "HTTP",
                    "reason": "HTTP",
                    "failure_action": "fix",
                    "cases": ["HTTP"],
                }
            ],
            "cases": {
                "HTTP": {
                    "requirements": ["REQ-0000000000000001"],
                    "domain": "contract",
                    "equals": 200,
                }
            },
        }
        self.report = {
            k: copy.deepcopy(self.policy[k])
            for k in ("schema_version", "source_version", "environment", "support")
        }
        self.report["cases"] = {
            "HTTP": {
                "state": "passed",
                "execution": "real",
                "observed": 200,
                "evidence": [self.ref("raw.json")],
            }
        }
        self.write("policy.json", self.policy)
        self.write("report.json", self.report)
        self.config = {
            "schema_version": 1,
            "owner": "owner",
            "from": "2020-01-01T00:00:00Z",
            "until": "2100-01-01T00:00:00Z",
        }

    def write(self, name: str, data: dict) -> None:
        (self.root / name).write_text(json.dumps(data), encoding="utf-8")

    def ref(self, name: str) -> dict:
        return {"path": name, "sha256": digest(self.root / name)}

    def event(self, attempt: int = 1) -> dict:
        return capture(self.root, self.root / "policy.json", self.root / "report.json", attempt)

    @staticmethod
    def rebind(event: dict) -> None:
        payload = {k: v for k, v in event.items() if k != "id"}
        event["id"] = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    def test_actual_capture_dedup_and_rerun(self) -> None:
        first, second = self.event(), self.event(2)
        result = summarize(self.root, [first, first, second], self.config)
        self.assertEqual(result["state"], "observed")
        self.assertEqual(result["duplicates"], 1)
        cohort = next(iter(result["cohorts"].values()))
        self.assertEqual(cohort["reruns"], 1)
        self.assertEqual(cohort["samples"][0]["coverage"]["fraction"], 1)
        self.assertEqual(result["false_block_sample"]["fraction"], None)

    def test_no_data_and_zero_population(self) -> None:
        self.assertEqual(summarize(self.root, [], self.config)["state"], "no-data")
        self.policy["admission"][0].update(applicable=False, cases=[])
        self.policy["cases"] = {}
        self.write("policy.json", self.policy)
        result = summarize(self.root, [self.event()], self.config)
        sample = next(iter(result["cohorts"].values()))["samples"][0]
        self.assertEqual(sample["coverage"]["fraction"], None)
        self.assertEqual(sample["state"], "blocked")

    def test_raw_tampering_and_event_conflict(self) -> None:
        event = self.event()
        altered = copy.deepcopy(event)
        altered["duration_ms"] = 0
        self.assertEqual(summarize(self.root, [event, altered], self.config)["state"], "blocked")
        self.write("raw.json", {"status": 401})
        self.assertEqual(summarize(self.root, [event], self.config)["state"], "blocked")

    def test_partial_review_sample_and_author_rejection(self) -> None:
        self.report["cases"]["HTTP"]["observed"] = 503
        self.write("report.json", self.report)
        first, second = self.event(), self.event(2)
        review = {
            "event_id": first["id"],
            "reviewer": "independent",
            "classification": "correct-block",
            "reason": "HTTP status mismatch",
            "reviewed_at": "2099-01-01T00:00:00Z",
        }
        self.write("review.json", review)
        self.config["block_reviews"] = [self.ref("review.json")]
        result = summarize(self.root, [first, second], self.config)
        self.assertEqual(
            result["false_block_sample"], {"numerator": 0, "denominator": 1, "fraction": 0}
        )
        self.assertEqual(result["blocked_unreviewed"], 1)
        review["reviewer"] = "author"
        self.write("review.json", review)
        self.config["block_reviews"] = [self.ref("review.json")]
        self.assertEqual(summarize(self.root, [first], self.config)["state"], "blocked")

    def test_cohorts_do_not_combine_versions(self) -> None:
        first = self.event()
        # Preserve the original raw files and references; a second candidate is another cohort.
        for name in ("policy.json", "report.json"):
            (self.root / ("old-" + name)).write_bytes((self.root / name).read_bytes())
        first["raw"] = [self.ref("old-policy.json"), self.ref("old-report.json")]
        self.rebind(first)
        self.policy["source_version"] = self.report["source_version"] = "b" * 40
        self.write("policy.json", self.policy)
        self.write("report.json", self.report)
        result = summarize(self.root, [first, self.event()], self.config)
        self.assertEqual(len(result["cohorts"]), 2)

    def test_timezone_window_attempt_and_gap_validation(self) -> None:
        first = self.event()
        self.config["from"] = "2020-01-01"
        self.assertEqual(summarize(self.root, [first], self.config)["state"], "blocked")
        self.config["from"] = "2020-01-01T00:00:00Z"
        self.config["until"] = first["finished_at"]
        self.assertEqual(summarize(self.root, [first], self.config)["state"], "no-data")
        self.config["until"] = "2100-01-01T00:00:00Z"
        self.assertEqual(
            summarize(self.root, [first, self.event()], self.config)["state"], "blocked"
        )
        self.config["collection_gaps"] = [{"state": "passed"}]
        self.assertEqual(summarize(self.root, [], self.config)["state"], "blocked")

    def test_malformed_events_paths_and_duration(self) -> None:
        for mutate in (
            lambda e: e.update(schema_version=True),
            lambda e: e.update(duration_ms=float("nan")),
            lambda e: e.update(attempt=True),
            lambda e: e["raw"][0].update(path="../outside"),
        ):
            event = self.event()
            mutate(event)
            self.rebind(event)
            self.assertEqual(summarize(self.root, [event], self.config)["state"], "blocked")

    def test_drift_due_closure_and_old_evidence(self) -> None:
        baseline = dict.fromkeys(TRIGGERS, "v1")
        current = baseline | {"permissions": "v2", "knowledge": "v2"}
        obj = {
            "id": "adoption",
            "owner": "owner",
            "authors": ["author"],
            "baseline": baseline,
            "current": current,
            "remedy": "revalidate affected paths",
            "effect": "fresh current-scope evidence",
            "current_since": "2098-01-01T00:00:00Z",
            "due_at": "2099-01-01T00:00:00Z",
            "review_by": "2099-01-01T00:00:00Z",
        }
        self.config["revalidation"] = [obj]
        result = summarize(self.root, [], self.config)["revalidation"][0]
        self.assertEqual(result["reasons"], ["knowledge", "permissions", "review-due"])
        self.assertTrue(result["overdue"])
        closure = {
            "state": "passed",
            "reviewer": "independent",
            "fingerprint": current,
            "verified_at": "2099-02-01T00:00:00Z",
            "evidence": [self.ref("raw.json")],
        }
        self.write("closure.json", closure)
        obj["closure"] = self.ref("closure.json")
        self.assertEqual(
            summarize(self.root, [], self.config)["revalidation"][0]["state"], "closed"
        )
        closure["fingerprint"] = baseline
        self.write("closure.json", closure)
        obj["closure"] = self.ref("closure.json")
        self.assertEqual(
            summarize(self.root, [], self.config)["revalidation"][0]["state"], "required"
        )

    def test_every_required_case_and_every_drift_trigger(self) -> None:
        self.policy["cases"]["second"] = copy.deepcopy(self.policy["cases"]["HTTP"])
        self.policy["admission"][0]["cases"].append("second")
        self.report["cases"]["second"] = copy.deepcopy(self.report["cases"]["HTTP"])
        self.report["cases"]["second"]["observed"] = 503
        self.write("policy.json", self.policy)
        self.write("report.json", self.report)
        result = summarize(self.root, [self.event()], self.config)
        sample = next(iter(result["cohorts"].values()))["samples"][0]
        self.assertEqual(sample["coverage"]["numerator"], 0)
        for trigger in TRIGGERS:
            obj = {
                "id": "reference",
                "owner": "owner",
                "authors": ["author"],
                "baseline": dict.fromkeys(TRIGGERS, "v1"),
                "current": dict.fromkeys(TRIGGERS, "v1") | {trigger: "v2"},
                "current_since": "2098-01-01T00:00:00Z",
                "due_at": "2099-01-01T00:00:00Z",
                "review_by": "2101-01-01T00:00:00Z",
                "remedy": "test",
                "effect": "test",
            }
            self.config["revalidation"] = [obj]
            self.assertEqual(
                summarize(self.root, [], self.config)["revalidation"][0]["reasons"], [trigger]
            )

    def test_future_review_and_gap_cannot_rewrite_early_observation(self) -> None:
        self.report["cases"]["HTTP"]["observed"] = 503
        self.write("report.json", self.report)
        event = self.event()
        self.config["until"] = "2099-01-01T00:00:00Z"
        self.write(
            "review.json",
            {
                "event_id": event["id"],
                "reviewer": "independent",
                "classification": "correct-block",
                "reason": "status",
                "reviewed_at": "2100-01-01T00:00:00Z",
            },
        )
        self.config["block_reviews"] = [self.ref("review.json")]
        self.assertEqual(summarize(self.root, [event], self.config)["state"], "blocked")
        self.config["block_reviews"] = []
        self.config["collection_gaps"] = [
            {
                "id": "gap",
                "owner": "owner",
                "source_version": "a" * 40,
                "state": "collection-failed",
                "reason": "missing",
                "recorded_at": "2100-01-01T00:00:00Z",
                "evidence": [self.ref("raw.json")],
            }
        ]
        self.assertEqual(summarize(self.root, [event], self.config)["state"], "blocked")


if __name__ == "__main__":
    unittest.main()
