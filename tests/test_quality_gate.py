from __future__ import annotations

import copy
import unittest
from datetime import UTC, datetime

from scripts.quality_gate import evaluate

NOW = datetime(2026, 10, 11, tzinfo=UTC)


class QualityGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = {
            "node": "review",
            "checks": {"ci": "ci", "translation": "translation", "limit": "optional"},
            "exception_rules": {"limit": ["maintainer"]},
        }
        self.record = {
            "node": "review",
            "scope": "trial",
            "source_version": "a" * 40,
            "checks": {name: {"state": "passed"} for name in self.policy["checks"]},
            "exceptions": {},
        }
        self.exception = {
            "authority": "maintainer",
            "authority_kind": "human",
            "node": "review",
            "scope": "trial",
            "source_version": "a" * 40,
            "revoked": False,
            "decided_at": "2026-10-10T00:00:00+00:00",
            "expires_at": "2026-10-12T00:00:00+00:00",
            **{
                key: "recorded"
                for key in [
                    "rule_id",
                    "basis",
                    "reason",
                    "risk",
                    "remediation",
                    "revoke_when",
                    "recheck_when",
                ]
            },
        }

    def test_all_pass_is_readiness_without_authorization(self) -> None:
        result = evaluate(self.record, self.policy, NOW)
        self.assertEqual(result["readiness"], "passed")
        self.assertTrue(result["may_advance"])
        self.assertIn("required", result["authorization"])

    def test_required_failure_cannot_be_waived(self) -> None:
        for category in [
            "required",
            "ci",
            "documentation",
            "translation",
            "evidence",
            "independence",
            "authorization",
        ]:
            with self.subTest(category=category):
                self.policy["checks"]["limit"] = category
                self.record["checks"]["limit"]["state"] = "failed"
                self.record["exceptions"]["limit"] = self.exception
                self.assertFalse(evaluate(self.record, self.policy, NOW)["may_advance"])

    def test_unknown_or_expired_or_revoked_exception_is_blocked(self) -> None:
        self.record["checks"]["limit"]["state"] = "failed"
        for field, value in [
            ("authority", "author"),
            ("authority_kind", "agent"),
            ("expires_at", "2026-10-11T00:00:00+00:00"),
            ("revoked", True),
            ("scope", "other"),
            ("source_version", "b" * 40),
            ("remediation", ""),
            ("remediation", "  "),
            ("basis", {"unverified": True}),
        ]:
            with self.subTest(field=field):
                exception = copy.deepcopy(self.exception)
                exception[field] = value
                self.record["exceptions"]["limit"] = exception
                self.assertFalse(evaluate(self.record, self.policy, NOW)["may_advance"])

    def test_valid_conditional_result_has_limited_progression(self) -> None:
        self.record["checks"]["limit"]["state"] = "failed"
        self.record["exceptions"]["limit"] = self.exception
        for node in [
            "local",
            "review",
            "merge",
            "initiative",
            "candidate",
            "production",
            "batch",
            "closure",
        ]:
            with self.subTest(node=node):
                self.record["node"] = self.policy["node"] = self.exception["node"] = node
                result = evaluate(self.record, self.policy, NOW)
                self.assertEqual(result["readiness"], "conditional")
                self.assertEqual(result["may_advance"], node in {"local", "review", "batch"})
                self.assertEqual(result["checks"]["limit"]["state"], "failed")

    def test_unrun_stale_or_blocked_cannot_be_excepted(self) -> None:
        for state in ["not-run", "stale", "blocked"]:
            self.record["checks"]["limit"]["state"] = state
            self.record["exceptions"]["limit"] = self.exception
            self.assertFalse(evaluate(self.record, self.policy, NOW)["may_advance"])

    def test_missing_check_and_na_without_basis_rejected(self) -> None:
        del self.record["checks"]["ci"]
        with self.assertRaises(ValueError):
            evaluate(self.record, self.policy, NOW)
        self.record["checks"]["ci"] = {"state": "not-applicable", "reason": "tool unavailable"}
        self.assertFalse(evaluate(self.record, self.policy, NOW)["may_advance"])

    def test_recovery_does_not_close_unfinished_delivery(self) -> None:
        self.policy = {
            "node": "closure",
            "checks": {"recovery": "required", "revalidation": "required"},
        }
        self.record.update(
            node="closure",
            checks={"recovery": {"state": "passed"}, "revalidation": {"state": "not-run"}},
        )
        self.assertFalse(evaluate(self.record, self.policy, NOW)["may_advance"])

    def test_malformed_policy_cannot_accept_authority_substrings(self) -> None:
        self.record["checks"]["limit"]["state"] = "failed"
        self.record["exceptions"]["limit"] = self.exception
        for field, value in [
            ("exception_rules", {"limit": "not-maintainer"}),
            ("exception_rules", {"limit": [True]}),
            ("not_applicable", "limit"),
            ("checks", ["limit"]),
        ]:
            with self.subTest(field=field):
                policy = copy.deepcopy(self.policy)
                policy[field] = value
                with self.assertRaises(ValueError):
                    evaluate(self.record, policy, NOW)

    def test_required_ci_cannot_be_declared_not_applicable(self) -> None:
        self.policy["not_applicable"] = ["ci"]
        self.record["checks"]["ci"] = {"state": "not-applicable", "reason": "not needed"}
        self.assertFalse(evaluate(self.record, self.policy, NOW)["may_advance"])
