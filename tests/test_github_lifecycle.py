from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, date, datetime
from pathlib import Path
from unittest.mock import patch

from scripts.github_lifecycle.__main__ import main
from scripts.github_lifecycle.common import LifecycleError, load_policy
from scripts.github_lifecycle.incident import (
    build_transition_request,
    transition_incident,
    write_transition_outputs,
)
from scripts.github_lifecycle.package import load_manifest, package_bundle
from scripts.github_lifecycle.pr import validate_pr_body
from scripts.github_lifecycle.release import (
    ReleaseRequest,
    prepare_release,
    validate_release_inputs,
)
from scripts.github_lifecycle.retrospective import (
    audit_records,
    build_retrospective_request,
    calculate_due_date,
    render_retrospective,
)

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / ".github" / "lifecycle-policy.json"


class LifecycleCliTests(unittest.TestCase):
    def test_release_validate_only_cli(self) -> None:
        arguments = [
            "github-lifecycle",
            "prepare-release",
            "--policy",
            str(POLICY_PATH),
            "--version",
            "v1.2.3",
            "--source-sha",
            "a" * 40,
            "--risk-level",
            "low",
            "--change-records",
            "PR #1",
            "--summary",
            "Candidate",
            "--repository",
            "example/repository",
            "--actor",
            "maintainer",
            "--run-url",
            "https://example.test/runs/1",
            "--created-at",
            "2026-08-27T00:00:00Z",
            "--validate-only",
        ]

        with patch("sys.argv", arguments):
            self.assertEqual(main(), 0)

    def test_incident_validate_only_cli_accepts_operation_id(self) -> None:
        arguments = [
            "github-lifecycle",
            "transition-incident",
            "--policy",
            str(POLICY_PATH),
            "--issue-number",
            "42",
            "--target-status",
            "mitigating",
            "--decision",
            "Proceed",
            "--evidence-links",
            "https://example.test/evidence",
            "--actor",
            "maintainer",
            "--occurred-at",
            "2026-08-27T00:00:00Z",
            "--security-risk",
            "false",
            "--apply",
            "false",
            "--operation-id",
            "gh-123456",
            "--validate-only",
        ]

        with patch("sys.argv", arguments):
            self.assertEqual(main(), 0)


def pr_body(risk: str, omitted_section: str | None = None) -> str:
    sections = {
        "Purpose": "Improve the lifecycle automation baseline.",
        "Scope and non-goals": "Includes validation; excludes deployment.",
        "Validation evidence": "python -m unittest for the current head SHA.",
        "Release impact": "No runtime release; repository workflow only.",
        "Recovery plan": "Revert the change and remove the required check.",
        "Related records": "Task 5 milestone 1.",
        "Independent review": "Fresh-context review is required.",
        "Integration/system evidence": "GitHub pull_request check run.",
        "Design record": "Task 5 approved plan.",
        "Specialist review": "Security boundary reviewed in the plan.",
        "Data recovery": "No data mutation; revert workflow and ruleset entry.",
        "Human Go/No-Go owner": "Repository maintainer.",
    }
    if omitted_section:
        sections.pop(omitted_section)
    metadata = (
        "<!-- lifecycle-metadata\n"
        "schema-version: 1\n"
        "change-id: CHG-AUTOMATION-001\n"
        f"risk-level: {risk}\n"
        "-->\n"
    )
    return metadata + "\n".join(f"## {name}\n\n{value}\n" for name, value in sections.items())


class LifecyclePolicyTests(unittest.TestCase):
    def test_repository_policy_is_valid(self) -> None:
        policy = load_policy(POLICY_PATH)

        self.assertEqual(policy.schema_version, 1)
        self.assertEqual(policy.pr_check_name, "lifecycle-policy")

    def test_unknown_policy_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "policy.json"
            raw = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
            raw["unexpected"] = True
            path.write_text(json.dumps(raw), encoding="utf-8")

            with self.assertRaisesRegex(LifecycleError, "unknown keys"):
                load_policy(path)


class PullRequestPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_policy(POLICY_PATH)

    def test_low_medium_and_high_records_are_accepted(self) -> None:
        for risk in self.policy.risk_levels:
            with self.subTest(risk=risk):
                result = validate_pr_body(pr_body(risk), draft=False, policy=self.policy)
                self.assertEqual(result.issues, ())
                self.assertFalse(result.blocks)

    def test_draft_reports_incomplete_record_without_blocking(self) -> None:
        result = validate_pr_body("", draft=True, policy=self.policy)

        self.assertTrue(result.issues)
        self.assertFalse(result.blocks)

    def test_ready_pr_blocks_when_medium_evidence_is_missing(self) -> None:
        result = validate_pr_body(
            pr_body("medium", omitted_section="Independent review"),
            draft=False,
            policy=self.policy,
        )

        self.assertTrue(result.blocks)
        self.assertIn(
            "required PR section is missing or incomplete: Independent review", result.issues
        )

    def test_high_risk_requires_human_go_no_go_owner(self) -> None:
        result = validate_pr_body(
            pr_body("high", omitted_section="Human Go/No-Go owner"),
            draft=False,
            policy=self.policy,
        )

        self.assertTrue(result.blocks)

    def test_duplicate_heading_is_rejected(self) -> None:
        body = pr_body("low") + "\n## Purpose\n\nA second purpose.\n"

        result = validate_pr_body(body, draft=False, policy=self.policy)

        self.assertIn("duplicate PR section: Purpose", result.issues)

    def test_old_schema_is_rejected(self) -> None:
        body = pr_body("low").replace("schema-version: 1", "schema-version: 0")

        result = validate_pr_body(body, draft=False, policy=self.policy)

        self.assertIn("lifecycle metadata schema-version must be 1", result.issues)

    def test_injected_second_metadata_block_is_rejected(self) -> None:
        injected = (
            pr_body("low") + "\n<!-- lifecycle-metadata\n"
            "schema-version: 1\nchange-id: CHG-INJECTED-999\n"
            "risk-level: low\n-->\n"
        )

        result = validate_pr_body(injected, draft=False, policy=self.policy)

        self.assertIn("PR body must contain exactly one lifecycle-metadata block", result.issues)


class AutomationPackageTests(unittest.TestCase):
    def test_bundle_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "one.txt").write_text("one\n", encoding="utf-8")
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps({"schema_version": 1, "files": ["one.txt"]}), encoding="utf-8"
            )

            first = package_bundle(root, manifest, root / "first.zip")
            second = package_bundle(root, manifest, root / "second.zip")

            self.assertEqual(first, second)

    def test_manifest_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.json"
            manifest.write_text(
                json.dumps({"schema_version": 1, "files": ["../secret"]}), encoding="utf-8"
            )

            with self.assertRaisesRegex(LifecycleError, "unsafe path"):
                load_manifest(manifest)

    def test_manifest_rejects_duplicate_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.json"
            manifest.write_text(
                json.dumps({"schema_version": 1, "files": ["one", "one"]}), encoding="utf-8"
            )

            with self.assertRaisesRegex(LifecycleError, "duplicate"):
                load_manifest(manifest)


class ReleasePreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_policy(POLICY_PATH)

    def request(self, version: str = "v1.2.3") -> ReleaseRequest:
        return ReleaseRequest(
            version=version,
            source_sha="a" * 40,
            risk_level="medium",
            change_records="PR #9",
            summary="Prepare lifecycle automation candidate.",
            repository="example/software-engineering",
            actor="maintainer",
            run_url="https://github.example/actions/runs/1",
            created_at="2026-08-26T00:00:00Z",
        )

    def github_state(
        self,
        root: Path,
        *,
        comparison_status: str = "ahead",
        check_conclusion: str = "success",
        tags: list[object] | None = None,
        releases: list[object] | None = None,
    ) -> tuple[Path, Path, Path, Path]:
        paths = tuple(
            root / name for name in ("compare.json", "checks.json", "tags.json", "releases.json")
        )
        values = (
            {"status": comparison_status, "base_commit": {"sha": "a" * 40}},
            {
                "check_runs": [
                    {
                        "name": "validate",
                        "status": "completed",
                        "conclusion": check_conclusion,
                    }
                ]
            },
            tags or [],
            releases or [],
        )
        for path, value in zip(paths, values, strict=True):
            path.write_text(json.dumps(value), encoding="utf-8")
        return paths

    def test_release_inputs_require_semantic_version_and_full_sha(self) -> None:
        request = self.request(version="1.2.3")

        with self.assertRaisesRegex(LifecycleError, "vMAJOR.MINOR.PATCH"):
            validate_release_inputs(
                request.version,
                request.source_sha,
                request.risk_level,
                self.policy,
                dry_run=True,
                confirmation="",
            )

        with self.assertRaisesRegex(LifecycleError, "40 lowercase"):
            validate_release_inputs(
                "v1.2.3",
                "abc123",
                request.risk_level,
                self.policy,
                dry_run=True,
                confirmation="",
            )

    def test_real_draft_requires_exact_version_confirmation(self) -> None:
        request = self.request()

        with self.assertRaisesRegex(LifecycleError, "exactly match"):
            validate_release_inputs(
                request.version,
                request.source_sha,
                request.risk_level,
                self.policy,
                dry_run=False,
                confirmation="v1.2.4",
            )

    def test_release_candidate_is_rendered_from_successful_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            comparison, checks, tags, releases = self.github_state(root)

            result = prepare_release(
                self.request(),
                self.policy,
                comparison,
                checks,
                tags,
                releases,
                root / "output",
            )

            self.assertTrue(result.record.is_file())
            manifest = json.loads(result.manifest.read_text(encoding="utf-8"))
            self.assertEqual(manifest["required_checks"], {"validate": "success"})

    def test_paginated_check_runs_are_merged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            comparison, checks, tags, releases = self.github_state(root)
            checks.write_text(
                json.dumps(
                    [
                        {"total_count": 1, "check_runs": []},
                        {
                            "total_count": 1,
                            "check_runs": [
                                {
                                    "name": "validate",
                                    "status": "completed",
                                    "conclusion": "success",
                                }
                            ],
                        },
                    ]
                ),
                encoding="utf-8",
            )

            result = prepare_release(
                self.request(),
                self.policy,
                comparison,
                checks,
                tags,
                releases,
                root / "output",
            )

            self.assertTrue(result.manifest.is_file())

    def test_unreachable_sha_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = self.github_state(root, comparison_status="diverged")

            with self.assertRaisesRegex(LifecycleError, "not reachable"):
                prepare_release(self.request(), self.policy, *state, root / "output")

    def test_comparison_sha_must_match_request(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            comparison, checks, tags, releases = self.github_state(root)
            comparison.write_text(
                json.dumps({"status": "ahead", "base_commit": {"sha": "b" * 40}}),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(LifecycleError, "does not match"):
                prepare_release(
                    self.request(),
                    self.policy,
                    comparison,
                    checks,
                    tags,
                    releases,
                    root / "output",
                )

    def test_failed_required_check_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = self.github_state(root, check_conclusion="failure")

            with self.assertRaisesRegex(LifecycleError, "validate=failure"):
                prepare_release(self.request(), self.policy, *state, root / "output")

    def test_existing_tag_or_release_is_rejected(self) -> None:
        cases = (
            ({"ref": "refs/tags/v1.2.3"}, None, "tag already exists"),
            (None, {"tagName": "v1.2.3"}, "Release already exists"),
            (None, {"tag_name": "v1.2.3"}, "Release already exists"),
        )
        for tag, release, message in cases:
            with self.subTest(message=message), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                state = self.github_state(
                    root,
                    tags=[tag] if tag else [],
                    releases=[release] if release else [],
                )

                with self.assertRaisesRegex(LifecycleError, message):
                    prepare_release(self.request(), self.policy, *state, root / "output")


class IncidentTransitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_policy(POLICY_PATH)

    def request(
        self,
        target: str,
        *,
        security_risk: bool = False,
        apply: bool = False,
    ):
        return build_transition_request(
            issue_number="42",
            target_status=target,
            decision="Evidence supports the next response state.",
            evidence_links="https://example.test/evidence/42",
            actor="maintainer",
            occurred_at="2026-08-26T08:00:00Z",
            security_or_privacy_risk=security_risk,
            restricted_event_id="SEC-RESTRICTED-42" if security_risk else "",
            apply=apply,
            confirmation="incident-42" if apply else "",
            operation_id="gh-123456",
            policy=self.policy,
        )

    def issue(
        self,
        root: Path,
        status: str,
        *,
        state: str | None = None,
        severity: str = "SEV2",
        comments: list[dict[str, str]] | None = None,
    ) -> Path:
        path = root / "issue.json"
        path.write_text(
            json.dumps(
                {
                    "number": 42,
                    "state": state or ("CLOSED" if status == "closed" else "OPEN"),
                    "body": f"### Severity\n\n{severity}\n",
                    "labels": [
                        {"name": "type:incident"},
                        {"name": f"status:{status}"},
                    ],
                    "comments": comments or [],
                }
            ),
            encoding="utf-8",
        )
        return path

    def test_all_allowed_incident_transitions(self) -> None:
        allowed = (
            ("investigating", "mitigating"),
            ("investigating", "recovered"),
            ("investigating", "escalated"),
            ("mitigating", "recovered"),
            ("mitigating", "escalated"),
            ("recovered", "closed"),
            ("closed", "investigating"),
        )
        for current, target in allowed:
            with (
                self.subTest(current=current, target=target),
                tempfile.TemporaryDirectory() as directory,
            ):
                root = Path(directory)
                result = transition_incident(
                    self.issue(root, current), self.request(target), self.policy
                )

                self.assertEqual(result.target_status, target)
                self.assertFalse(result.noop)

    def test_illegal_transition_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            with self.assertRaisesRegex(LifecycleError, "illegal incident transition"):
                transition_incident(
                    self.issue(root, "investigating"),
                    self.request("closed"),
                    self.policy,
                )

    def test_security_escalation_omits_public_decision_and_evidence(self) -> None:
        request = build_transition_request(
            issue_number="42",
            target_status="escalated",
            decision="private person@example.test",
            evidence_links="not a public URL and must be ignored",
            actor="maintainer",
            occurred_at="2026-08-26T08:00:00Z",
            security_or_privacy_risk=True,
            restricted_event_id="PRIV-RESTRICTED-42",
            apply=False,
            confirmation="",
            operation_id="gh-123456",
            policy=self.policy,
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            result = transition_incident(self.issue(root, "investigating"), request, self.policy)

            self.assertIn("PRIV-RESTRICTED-42", result.comment)
            self.assertNotIn("person@example.test", result.comment)
            self.assertNotIn("not a public URL", result.comment)

    def test_security_escalation_requires_restricted_id(self) -> None:
        with self.assertRaisesRegex(LifecycleError, "restricted event ID"):
            build_transition_request(
                issue_number="42",
                target_status="escalated",
                decision="",
                evidence_links="",
                actor="maintainer",
                occurred_at="2026-08-26T08:00:00Z",
                security_or_privacy_risk=True,
                restricted_event_id="",
                apply=False,
                confirmation="",
                operation_id="gh-123456",
                policy=self.policy,
            )

    def test_applied_transition_requires_issue_confirmation(self) -> None:
        with self.assertRaisesRegex(LifecycleError, "incident-42"):
            build_transition_request(
                issue_number="42",
                target_status="mitigating",
                decision="Proceed with mitigation.",
                evidence_links="https://example.test/evidence/42",
                actor="maintainer",
                occurred_at="2026-08-26T08:00:00Z",
                security_or_privacy_risk=False,
                restricted_event_id="",
                apply=True,
                confirmation="wrong",
                operation_id="gh-123456",
                policy=self.policy,
            )

    def test_retry_at_target_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = transition_incident(
                self.issue(root, "recovered"), self.request("recovered"), self.policy
            )

            self.assertTrue(result.noop)
            self.assertEqual(result.comment, "")

    def test_retry_after_comment_only_skips_duplicate_comment(self) -> None:
        marker = (
            "<!-- lifecycle-transition operation-id=gh-123456 "
            "issue=42 from=investigating to=mitigating -->"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = transition_incident(
                self.issue(root, "investigating", comments=[{"body": marker}]),
                self.request("mitigating"),
                self.policy,
            )

            self.assertFalse(result.comment_required)
            self.assertTrue(result.label_update_required)
            self.assertEqual(result.issue_action, "none")
            self.assertFalse(result.noop)

    def test_retry_after_close_label_repairs_open_state(self) -> None:
        marker = (
            "<!-- lifecycle-transition operation-id=gh-123456 issue=42 from=recovered to=closed -->"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = transition_incident(
                self.issue(
                    root,
                    "closed",
                    state="OPEN",
                    comments=[{"body": marker}],
                ),
                self.request("closed"),
                self.policy,
            )

            self.assertFalse(result.comment_required)
            self.assertFalse(result.label_update_required)
            self.assertEqual(result.issue_action, "close")
            self.assertFalse(result.noop)

    def test_inconsistent_target_without_marker_gets_reconciliation_record(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = transition_incident(
                self.issue(root, "closed", state="OPEN"),
                self.request("closed"),
                self.policy,
            )

            self.assertTrue(result.comment_required)
            self.assertFalse(result.label_update_required)
            self.assertEqual(result.issue_action, "close")
            self.assertIn("state reconciliation", result.comment)

    def test_transition_outputs_contain_one_current_and_target_label(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = transition_incident(
                self.issue(root, "investigating"),
                self.request("mitigating"),
                self.policy,
            )

            plan_path, comment_path = write_transition_outputs(result, root / "output", None)

            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertEqual(plan["current_label"], "status:investigating")
            self.assertEqual(plan["target_label"], "status:mitigating")
            self.assertTrue(plan["comment_required"])
            self.assertTrue(plan["label_update_required"])
            self.assertIn("severity:sev2", plan["severity_label"])
            self.assertIn("Incident state transition", comment_path.read_text(encoding="utf-8"))


class RetrospectiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_policy(POLICY_PATH)

    def request(
        self,
        source: str = "incident:42",
        *,
        stable: bool = False,
        apply: bool = False,
    ):
        confirmation = f"retrospective-{source.replace(':', '-', 1)}" if apply else ""
        return build_retrospective_request(
            source=source,
            stability_confirmed=stable,
            timeline="The alert fired, responders mitigated impact, and health recovered.",
            visible_information="Responders saw elevated errors and the latest release record.",
            contributing_factors="A dependency failure and insufficient fallback capacity.",
            guard_effectiveness="Alerting worked; fallback capacity was insufficient.",
            uncertainties="The initial dependency trigger remains uncertain.",
            action_links="Pending creation through the improvement action form.",
            actor="maintainer",
            occurred_at="2026-08-26T08:00:00Z",
            apply=apply,
            confirmation=confirmation,
        )

    def write_json(self, root: Path, name: str, value: object) -> Path:
        path = root / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def incident_source(
        self,
        root: Path,
        *,
        status: str = "recovered",
        severity: str = "sev1",
    ) -> Path:
        return self.write_json(
            root,
            "source.json",
            {
                "number": 42,
                "state": "OPEN",
                "url": "https://example.test/issues/42",
                "updatedAt": "2026-08-26T08:00:00Z",
                "body": f"### Severity\n\n{severity.upper()}\n",
                "labels": [
                    {"name": "type:incident"},
                    {"name": f"status:{status}"},
                    {"name": f"severity:{severity}"},
                ],
                "comments": [
                    {"body": "- Current status: `recovered`\n- Time: `2026-08-26T08:00:00Z`"}
                ],
            },
        )

    def test_deadline_boundaries_cover_severities_and_release(self) -> None:
        anchor = datetime(2026, 8, 26, tzinfo=UTC)
        expected = {
            "sev1": date(2026, 9, 2),
            "sev2": date(2026, 9, 9),
            "sev3": date(2026, 9, 25),
            "sev4": None,
            "release": date(2026, 9, 25),
        }

        for source_type, due in expected.items():
            with self.subTest(source_type=source_type):
                self.assertEqual(calculate_due_date(anchor, source_type, self.policy), due)

    def test_incident_retrospective_renders_required_sections(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.incident_source(root)
            existing = self.write_json(root, "existing.json", [])

            result = render_retrospective(self.request(), source, existing, self.policy)

            self.assertEqual(result.due_date, date(2026, 9, 2))
            self.assertIn("<!-- lifecycle-source:incident:42 -->", result.body)
            self.assertIn("## Information visible at the time", result.body)
            self.assertIn("## Guard effectiveness", result.body)

    def test_unstable_incident_requires_explicit_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.incident_source(root, status="investigating")
            existing = self.write_json(root, "existing.json", [])

            with self.assertRaisesRegex(LifecycleError, "explicitly confirmed stable"):
                render_retrospective(self.request(), source, existing, self.policy)

            result = render_retrospective(self.request(stable=True), source, existing, self.policy)
            self.assertEqual(result.due_date, date(2026, 9, 2))

    def test_recovered_incident_without_transition_time_requires_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.incident_source(root)
            raw = json.loads(source.read_text(encoding="utf-8"))
            raw["comments"] = []
            source.write_text(json.dumps(raw), encoding="utf-8")
            existing = self.write_json(root, "existing.json", [])

            with self.assertRaisesRegex(LifecycleError, "no recovery transition timestamp"):
                render_retrospective(self.request(), source, existing, self.policy)

            result = render_retrospective(self.request(stable=True), source, existing, self.policy)
            self.assertEqual(result.due_date, date(2026, 9, 2))

    def test_duplicate_retrospective_returns_existing_issue(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.incident_source(root)
            existing = self.write_json(
                root,
                "existing.json",
                [
                    {
                        "number": 99,
                        "url": "https://example.test/issues/99",
                        "body": "<!-- lifecycle-source:incident:42 -->",
                    }
                ],
            )

            result = render_retrospective(self.request(), source, existing, self.policy)

            self.assertTrue(result.duplicate)
            self.assertEqual(result.duplicate_number, 99)

    def test_release_retrospective_requires_published_non_prerelease(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            existing = self.write_json(root, "existing.json", [])
            source = self.write_json(
                root,
                "release.json",
                {
                    "tagName": "v1.2.3",
                    "url": "https://example.test/releases/v1.2.3",
                    "isDraft": False,
                    "isPrerelease": False,
                    "publishedAt": "2026-08-26T08:00:00Z",
                },
            )

            result = render_retrospective(
                self.request("release:v1.2.3"), source, existing, self.policy
            )
            self.assertEqual(result.due_date, date(2026, 9, 25))

            raw = json.loads(source.read_text(encoding="utf-8"))
            raw["isDraft"] = True
            source.write_text(json.dumps(raw), encoding="utf-8")
            with self.assertRaisesRegex(LifecycleError, "published non-prerelease"):
                render_retrospective(self.request("release:v1.2.3"), source, existing, self.policy)

    def test_applied_retrospective_requires_source_confirmation(self) -> None:
        with self.assertRaisesRegex(LifecycleError, "retrospective-incident-42"):
            build_retrospective_request(
                source="incident:42",
                stability_confirmed=False,
                timeline="Timeline",
                visible_information="Visible information",
                contributing_factors="Contributing factors",
                guard_effectiveness="Guard effectiveness",
                uncertainties="Uncertainty",
                action_links="Pending action",
                actor="maintainer",
                occurred_at="2026-08-26T08:00:00Z",
                apply=True,
                confirmation="wrong",
            )

    def test_audit_reports_missing_retrospective_and_overdue_action(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            issues = self.write_json(
                root,
                "issues.json",
                [
                    {
                        "number": 42,
                        "state": "OPEN",
                        "url": "https://example.test/issues/42",
                        "updatedAt": "2026-08-01T00:00:00Z",
                        "body": "### Severity\n\nSEV1\n",
                        "labels": [
                            {"name": "type:incident"},
                            {"name": "status:recovered"},
                            {"name": "severity:sev1"},
                        ],
                        "comments": [
                            {
                                "body": "- Current status: `recovered`\n"
                                "- Time: `2026-08-01T00:00:00Z`"
                            }
                        ],
                    },
                    {
                        "number": 43,
                        "state": "OPEN",
                        "url": "https://example.test/issues/43",
                        "updatedAt": "2026-08-01T00:00:00Z",
                        "body": "### Due date\n\n2026-08-10\n",
                        "labels": [{"name": "type:improvement-action"}],
                    },
                ],
            )
            releases = self.write_json(root, "releases.json", [])

            findings = audit_records(issues, releases, self.policy, date(2026, 8, 26))

            self.assertEqual(
                {finding.kind for finding in findings},
                {"retrospective-missing", "improvement-action-overdue"},
            )

    def test_audit_uses_recovery_transition_instead_of_updated_at(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            issues = self.write_json(
                root,
                "issues.json",
                [
                    {
                        "number": 42,
                        "state": "OPEN",
                        "html_url": "https://example.test/issues/42",
                        "updated_at": "2026-08-25T00:00:00Z",
                        "body": "### Severity\n\nSEV1\n",
                        "labels": [
                            {"name": "type:incident"},
                            {"name": "status:recovered"},
                            {"name": "severity:sev1"},
                        ],
                    }
                ],
            )
            comments = self.write_json(
                root,
                "comments.json",
                [
                    [
                        {
                            "issue_url": "https://api.github.test/repos/example/issues/42",
                            "body": "- Current status: `recovered`\n- Time: `2026-08-01T00:00:00Z`",
                        }
                    ]
                ],
            )
            releases = self.write_json(root, "releases.json", [])

            findings = audit_records(
                issues,
                releases,
                self.policy,
                date(2026, 8, 26),
                comments,
            )

            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].kind, "retrospective-missing")
            self.assertEqual(findings[0].due_date, date(2026, 8, 8))

    def test_audit_reports_invalid_record_and_continues(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            issues = self.write_json(
                root,
                "issues.json",
                [
                    {
                        "number": 43,
                        "state": "OPEN",
                        "html_url": "https://example.test/issues/43",
                        "body": "### Due date\n\nnot-a-date\n",
                        "labels": [{"name": "type:improvement-action"}],
                    },
                    {
                        "number": 44,
                        "state": "OPEN",
                        "html_url": "https://example.test/issues/44",
                        "body": "### Due date\n\n2026-08-01\n",
                        "labels": [{"name": "type:improvement-action"}],
                    },
                ],
            )
            releases = self.write_json(root, "releases.json", [])

            findings = audit_records(issues, releases, self.policy, date(2026, 8, 26))

            self.assertEqual(
                {finding.kind for finding in findings},
                {"record-invalid", "improvement-action-overdue"},
            )
            invalid = next(finding for finding in findings if finding.kind == "record-invalid")
            self.assertIsNone(invalid.due_date)

    def test_audit_reports_missing_recovery_timestamp_as_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            issues = self.write_json(
                root,
                "issues.json",
                [
                    {
                        "number": 42,
                        "state": "open",
                        "html_url": "https://example.test/issues/42",
                        "updated_at": "2026-08-01T00:00:00Z",
                        "body": "### Severity\n\nSEV1\n",
                        "labels": [
                            {"name": "type:incident"},
                            {"name": "status:recovered"},
                            {"name": "severity:sev1"},
                        ],
                    }
                ],
            )
            releases = self.write_json(root, "releases.json", [])

            findings = audit_records(issues, releases, self.policy, date(2026, 8, 26))

            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].kind, "record-invalid")
            self.assertIn("no recovery transition timestamp", findings[0].detail)

    def test_audit_reports_duplicate_retrospective_sources(self) -> None:
        body = (
            "<!-- lifecycle-retrospective\n"
            "schema-version: 1\nsource: incident:42\ndue-date: 2026-08-08\n-->"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            issues = self.write_json(
                root,
                "issues.json",
                [
                    {
                        "number": number,
                        "state": "CLOSED",
                        "html_url": f"https://example.test/issues/{number}",
                        "body": body,
                        "labels": [{"name": "type:retrospective"}],
                    }
                    for number in (99, 100)
                ],
            )
            releases = self.write_json(root, "releases.json", [])

            findings = audit_records(issues, releases, self.policy, date(2026, 8, 26))

            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].kind, "retrospective-duplicate")

    def test_invalid_retrospective_does_not_satisfy_incident_requirement(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            issues = self.write_json(
                root,
                "issues.json",
                [
                    {
                        "number": 42,
                        "state": "closed",
                        "html_url": "https://example.test/issues/42",
                        "body": "### Severity\n\nSEV1\n",
                        "labels": [
                            {"name": "type:incident"},
                            {"name": "status:closed"},
                            {"name": "severity:sev1"},
                        ],
                        "comments": [
                            {
                                "body": "- Current status: `recovered`\n"
                                "- Time: `2026-08-01T00:00:00Z`"
                            }
                        ],
                    },
                    {
                        "number": 99,
                        "state": "closed",
                        "html_url": "https://example.test/issues/99",
                        "body": "<!-- lifecycle-retrospective\n"
                        "schema-version: 1\nsource: incident:42\n"
                        "due-date: invalid\n-->",
                        "labels": [{"name": "type:retrospective"}],
                    },
                ],
            )
            releases = self.write_json(root, "releases.json", [])

            findings = audit_records(issues, releases, self.policy, date(2026, 8, 26))

            self.assertEqual(
                {finding.kind for finding in findings},
                {"record-invalid", "retrospective-missing"},
            )

    def test_audit_does_not_duplicate_linked_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            issues = self.write_json(
                root,
                "issues.json",
                [
                    {
                        "number": 42,
                        "state": "CLOSED",
                        "url": "https://example.test/issues/42",
                        "updatedAt": "2026-08-01T00:00:00Z",
                        "body": "### Severity\n\nSEV1\n",
                        "labels": [
                            {"name": "type:incident"},
                            {"name": "status:closed"},
                            {"name": "severity:sev1"},
                        ],
                        "comments": [
                            {
                                "body": "- Current status: `recovered`\n"
                                "- Time: `2026-08-01T00:00:00Z`"
                            }
                        ],
                    },
                    {
                        "number": 99,
                        "state": "CLOSED",
                        "url": "https://example.test/issues/99",
                        "body": "<!-- lifecycle-retrospective\n"
                        "schema-version: 1\nsource: incident:42\n"
                        "due-date: 2026-08-08\n-->",
                        "labels": [{"name": "type:retrospective"}],
                    },
                ],
            )
            releases = self.write_json(root, "releases.json", [])

            findings = audit_records(issues, releases, self.policy, date(2026, 8, 26))

            self.assertEqual(findings, ())

    def test_audit_reports_published_release_without_retrospective(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            issues = self.write_json(root, "issues.json", [])
            releases = self.write_json(
                root,
                "releases.json",
                [
                    [
                        {
                            "tag_name": "v1.2.3",
                            "html_url": "https://example.test/releases/v1.2.3",
                            "draft": False,
                            "prerelease": False,
                            "published_at": "2026-07-01T00:00:00Z",
                        }
                    ]
                ],
            )

            findings = audit_records(issues, releases, self.policy, date(2026, 8, 26))

            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].record, "Release v1.2.3")


if __name__ == "__main__":
    unittest.main()
