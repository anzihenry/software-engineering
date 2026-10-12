from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.domain_validation import DOMAINS, evaluate


class DomainValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        raw = self.root / "raw.json"
        raw.write_text('{"status":200}', encoding="utf-8")
        self.policy = {
            "schema_version": 1,
            "source_version": "a" * 40,
            "environment": {"identity": "loopback"},
            "support": {"browser": "reference"},
            "authors": ["author"],
            "domains": {
                name: {"applicable": name == "contract", "reason": "fixture scope"}
                for name in DOMAINS
            },
            "cases": {
                "contract": {
                    "domain": "contract",
                    "requirements": ["REQ-0000000000000001"],
                    "equals": 200,
                }
            },
        }
        self.policy["admission"] = [
            {
                "id": "REQ-0000000000000001",
                "source": "fixture clause",
                "applicable": True,
                "trigger": "contract boundary",
                "reason": "actual fixture",
                "owner": "fixture-owner",
                "failure_action": "return to implementation",
                "cases": ["contract"],
            }
        ]
        self.report = {
            **{
                key: copy.deepcopy(self.policy[key])
                for key in ("schema_version", "source_version", "environment", "support")
            },
            "cases": {
                "contract": {
                    "state": "passed",
                    "execution": "real",
                    "observed": 200,
                    "evidence": [
                        {"path": "raw.json", "sha256": hashlib.sha256(raw.read_bytes()).hexdigest()}
                    ],
                }
            },
        }

    def test_current_evidence_and_observation(self) -> None:
        self.assertEqual(evaluate(self.root, self.report, self.policy)["state"], "passed")
        self.report["cases"]["contract"]["observed"] = 401
        self.assertEqual(evaluate(self.root, self.report, self.policy)["state"], "failed")

    def test_missing_stale_substitute_and_tampered_evidence(self) -> None:
        mutations = [
            lambda r: r["cases"].clear(),
            lambda r: r.update(source_version="b" * 40),
            lambda r: r.update(environment={}),
            lambda r: r["cases"]["contract"].update(execution="substitute"),
            lambda r: r["cases"]["contract"].update(evidence=[]),
            lambda r: r["cases"]["contract"]["evidence"][0].update(sha256="0" * 64),
            lambda r: r["cases"]["contract"]["evidence"][0].update(path="../outside"),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                report = copy.deepcopy(self.report)
                mutate(report)
                self.assertEqual(evaluate(self.root, report, self.policy)["state"], "blocked")

    def test_domain_omission_cannot_pass(self) -> None:
        self.policy["domains"]["browser"]["applicable"] = True
        self.assertEqual(evaluate(self.root, self.report, self.policy)["state"], "blocked")

    def test_unapproved_visual_review_and_author_review_block(self) -> None:
        self.policy["cases"]["contract"]["review_required"] = True
        case = self.report["cases"]["contract"]
        for reviewer in (None, "author", "independent"):
            case["review"] = {"reviewer": reviewer, "state": "passed", "source_version": "a" * 40}
            self.assertEqual(
                evaluate(self.root, self.report, self.policy)["state"],
                "passed" if reviewer == "independent" else "blocked",
            )
        case["review"]["source_version"] = "b" * 40
        self.assertEqual(evaluate(self.root, self.report, self.policy)["state"], "blocked")

    def test_budget_rejects_overrun_nan_bool_and_unknown_schema(self) -> None:
        self.policy["cases"]["contract"] = {
            "domain": "contract",
            "requirements": ["REQ-0000000000000001"],
            "maximum": 2,
        }
        for value in (3, float("nan"), True, None, -1):
            self.report["cases"]["contract"]["observed"] = value
            self.assertEqual(evaluate(self.root, self.report, self.policy)["state"], "failed")
        self.report["schema_version"] = 2
        self.assertEqual(evaluate(self.root, self.report, self.policy)["state"], "blocked")

    def test_malformed_policy_and_unasserted_case_block(self) -> None:
        for mutation in (
            lambda p: p.update(domains=[]),
            lambda p: p.update(schema_version=True),
            lambda p: p["cases"].update(contract=None),
            lambda p: p["cases"]["contract"].pop("equals"),
        ):
            policy = copy.deepcopy(self.policy)
            mutation(policy)
            self.assertEqual(evaluate(self.root, self.report, policy)["state"], "blocked")
        self.report["cases"]["contract"]["evidence"] = None
        self.assertEqual(evaluate(self.root, self.report, self.policy)["state"], "blocked")

    def test_admission_cannot_drop_clause_or_claim_unmapped_case(self) -> None:
        for mutate in (
            lambda p: p.pop("admission"),
            lambda p: p["admission"][0].update(cases=[]),
            lambda p: p["admission"][0].update(applicable=False),
            lambda p: p["admission"][0].update(owner=""),
        ):
            policy = copy.deepcopy(self.policy)
            mutate(policy)
            self.assertEqual(evaluate(self.root, self.report, policy)["state"], "blocked")

    def test_cli_missing_or_invalid_json_is_structured_blocked(self) -> None:
        policy = self.root / "policy.json"
        policy.write_text(json.dumps(self.policy), encoding="utf-8")
        report = self.root / "report.json"
        for content in (None, "{", '{"schema_version":1,"schema_version":1}'):
            if content is not None:
                report.write_text(content, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "scripts.domain_validation",
                    "--root",
                    str(self.root),
                    "--policy",
                    str(policy),
                    "--report",
                    str(report),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["state"], "blocked")
            self.assertEqual(result.stderr, "")

    def test_json_boolean_is_not_number_in_nested_observations(self) -> None:
        for expected, observed in ((True, 1), ({"allowed": True}, {"allowed": 1}), ([True], [1])):
            self.policy["cases"]["contract"]["equals"] = expected
            self.report["cases"]["contract"]["observed"] = observed
            self.assertEqual(evaluate(self.root, self.report, self.policy)["state"], "failed")
