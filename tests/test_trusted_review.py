"""Synthetic API fixtures test rejection boundaries, not actual GitHub enforcement."""

from __future__ import annotations

import base64
import copy
import hashlib
import json
import unittest

from scripts import documentation_check as checker
from scripts.trusted_review import HARNESS_ROOT, verify
from tests import test_documentation_check as fixtures


class TrustedReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = fixtures.DocumentationGateTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.data["standard_version"] = "a" * 40
        self.fixture.write_config()
        self.fixture.git("add", ".")
        self.fixture.git("commit", "-qm", "candidate")
        self.head = self.fixture.git("rev-parse", "HEAD").strip()
        self.merge = "b" * 40
        self.source = "c" * 40
        self.repo = "owner/canary"
        self.policy = {
            "repository": self.repo,
            "publishers": ["owner"],
            "context": "harness-independent-review",
            "required_checks": {"unit-tests": 15368},
            "harness_revision": "a" * 40,
        }
        saved = checker.snapshot(self.fixture.root, self.fixture.name, self.fixture.base, ["owner"])
        report = "Synthetic independent review report; fixture only."
        self.payload = {
            "schema_version": 1,
            "publisher": "owner",
            "binding": {
                "repository": self.repo,
                "pull_request": 1,
                "head_sha": self.head,
                "base_sha": self.fixture.base,
                "merge_sha": self.merge,
            },
            "snapshot": saved,
            "review": self.fixture.review(saved),
            "reports": [{"text": report, "sha256": hashlib.sha256(report.encode()).hexdigest()}],
            "requirements": [
                json.loads((HARNESS_ROOT / "docs/harness-requirements.json").read_text())[
                    "requirements"
                ][0]["id"]
            ],
        }
        prefix = "repos/" + self.repo
        self.endpoints = {
            f"{prefix}/compare/{self.source}...{self.head}": {"status": "diverged"},
            f"{prefix}/collaborators?per_page=100": [
                {"login": "owner", "permissions": {"admin": True, "push": True}}
            ],
            f"{prefix}/actions/permissions/workflow": {
                "default_workflow_permissions": "read",
                "can_approve_pull_request_reviews": False,
            },
            f"{prefix}/pulls/1": {
                "state": "open",
                "commits": 1,
                "user": {"login": "owner"},
                "head": {"sha": self.head},
                "base": {"sha": self.fixture.base},
                "merge_commit_sha": self.merge,
            },
            f"{prefix}/commits/{self.head}/statuses?per_page=100": [
                {
                    "state": "success",
                    "context": "harness-independent-review",
                    "creator": {"login": "owner"},
                    "target_url": f"https://github.com/{self.repo}/blob/{self.source}/review-evidence.json",
                }
            ],
            f"{prefix}/pulls/1/commits?per_page=100": [
                {"author": {"login": "owner"}, "committer": {"login": "owner"}}
            ],
            f"{prefix}/commits/{self.head}/check-runs?per_page=100": {
                "check_runs": [
                    {
                        "id": 1,
                        "name": "unit-tests",
                        "status": "completed",
                        "conclusion": "success",
                        "head_sha": self.head,
                        "app": {"id": 15368},
                        "html_url": "https://example.invalid/fixture",
                    }
                ]
            },
        }

    def api(self, endpoint: str) -> object:
        if "/contents/" in endpoint:
            return {
                "encoding": "base64",
                "content": base64.b64encode(json.dumps(self.payload).encode()).decode(),
            }
        return copy.deepcopy(self.endpoints[endpoint])

    def run_verify(self) -> dict:
        return verify(self.fixture.root, self.policy, 1, self.api)

    def test_controlled_record_and_real_observation_contract(self) -> None:
        self.assertEqual(self.run_verify()["status"], "passed")
        self.assertEqual(self.run_verify()["observed_ci"]["unit-tests"]["id"], 1)

    def test_self_review_unread_snapshot_and_missing_report(self) -> None:
        original = copy.deepcopy(self.payload)
        mutations = [
            lambda p: p["review"].update(reviewer="owner"),
            lambda p: p["review"].update(inspected_files=[]),
            lambda p: p["review"].update(snapshot_digest="0" * 64),
            lambda p: p.update(reports=[]),
            lambda p: p["reports"][0].update(sha256="0" * 64),
            lambda p: p["binding"].update(merge_sha="e" * 40),
            lambda p: p["binding"].update(head_sha="e" * 40),
            lambda p: p["snapshot"].update(authors=["unrelated"]),
        ]
        for mutate in mutations:
            self.payload = copy.deepcopy(original)
            mutate(self.payload)
            with self.assertRaises(ValueError):
                self.run_verify()

    def test_author_editable_or_untrusted_status_cannot_approve(self) -> None:
        statuses = next(v for k, v in self.endpoints.items() if "/statuses?" in k)
        original = copy.deepcopy(statuses[0])
        for field, value in [
            ("creator", {"login": "author"}),
            ("target_url", f"https://github.com/{self.repo}/blob/main/review-evidence.json"),
            ("target_url", "file:///tmp/passed.json"),
            ("state", "pending"),
        ]:
            statuses[0] = {**original, field: value}
            with self.assertRaises(ValueError):
                self.run_verify()

    def test_ci_claims_must_be_corroborated(self) -> None:
        runs = next(v["check_runs"] for k, v in self.endpoints.items() if "/check-runs?" in k)
        original = copy.deepcopy(runs[0])
        for field, value in [
            ("status", "in_progress"),
            ("conclusion", "failure"),
            ("conclusion", "skipped"),
            ("app", {"id": 1}),
            ("head_sha", "f" * 40),
        ]:
            runs[0] = {**original, field: value}
            with self.assertRaises(ValueError):
                self.run_verify()
        runs[:] = [original, {**original, "id": 2, "conclusion": "failure"}]
        with self.assertRaises(ValueError):
            self.run_verify()

    def test_candidate_change_during_verification(self) -> None:
        calls = 0

        def changing_api(endpoint: str) -> object:
            nonlocal calls
            result = self.api(endpoint)
            if endpoint.endswith("/pulls/1"):
                calls += 1
                if calls > 1:
                    result["base"]["sha"] = "e" * 40
            return result

        with self.assertRaises(ValueError):
            verify(self.fixture.root, self.policy, 1, changing_api)

    def test_correction_can_be_verified_again(self) -> None:
        self.payload["reports"][0]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            self.run_verify()
        self.payload["reports"][0]["sha256"] = hashlib.sha256(
            self.payload["reports"][0]["text"].encode()
        ).hexdigest()
        self.assertEqual(self.run_verify()["status"], "passed")

    def test_permission_and_policy_drift_blocked(self) -> None:
        self.endpoints[f"repos/{self.repo}/collaborators?per_page=100"].append(
            {"login": "untrusted-writer", "permissions": {"push": True}}
        )
        with self.assertRaises(ValueError):
            self.run_verify()
        self.endpoints[f"repos/{self.repo}/collaborators?per_page=100"].pop()
        self.policy["required_checks"]["missing"] = 15368
        with self.assertRaisesRegex(ValueError, "adoption/CI policy"):
            self.run_verify()

    def test_approval_in_candidate_history_is_rejected(self) -> None:
        self.endpoints[f"repos/{self.repo}/compare/{self.source}...{self.head}"]["status"] = "ahead"
        with self.assertRaises(ValueError):
            self.run_verify()

    def test_revoked_publisher_and_closed_pr_are_rejected(self) -> None:
        collaborators = self.endpoints[f"repos/{self.repo}/collaborators?per_page=100"]
        collaborators[0]["permissions"] = {"push": False, "admin": False}
        with self.assertRaises(ValueError):
            self.run_verify()
        collaborators[0]["permissions"] = {"push": True, "admin": True}
        calls = 0

        def closing_api(endpoint: str) -> object:
            nonlocal calls
            response = self.api(endpoint)
            if endpoint.endswith("/pulls/1"):
                calls += 1
                if calls > 1:
                    response["state"] = "closed"
            return response

        with self.assertRaises(ValueError):
            verify(self.fixture.root, self.policy, 1, closing_api)

    def test_incomplete_or_large_contributor_audit_is_blocked(self) -> None:
        for count in [2, 251, True]:
            self.endpoints[f"repos/{self.repo}/pulls/1"]["commits"] = count
            with self.assertRaises(ValueError):
                self.run_verify()
