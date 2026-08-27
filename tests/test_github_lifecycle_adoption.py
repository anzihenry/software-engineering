from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.github_lifecycle.adoption import (
    apply_install,
    inspect_local_install,
    plan_install,
)
from scripts.github_lifecycle.common import LifecycleError, load_policy
from scripts.github_lifecycle.repository import (
    CheckEvidence,
    RepositorySnapshot,
    apply_bootstrap,
    build_bootstrap_plan,
    inspect_remote_repository,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path("automation/github-lifecycle-manifest.json")
POLICY = load_policy(ROOT / ".github/lifecycle-policy.json")
REPOSITORY = "example/service"
APP_ID = 15368


def evidence(**changes: object) -> CheckEvidence:
    values: dict[str, object] = {
        "pull_request_number": 42,
        "pull_request_url": "https://github.com/example/service/pull/42",
        "state": "OPEN",
        "base_branch": "main",
        "head_sha": "a" * 40,
        "successful_integrations": {
            "validate": frozenset({APP_ID}),
            "lifecycle-policy": frozenset({APP_ID}),
        },
    }
    values.update(changes)
    return CheckEvidence(**values)


def managed_ruleset() -> dict[str, object]:
    return {
        "id": 123,
        "name": "main required checks",
        "target": "branch",
        "enforcement": "active",
        "bypass_actors": [],
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        "rules": [
            {
                "type": "required_status_checks",
                "parameters": {
                    "required_status_checks": [
                        {"context": "validate", "integration_id": APP_ID},
                        {"context": "lifecycle-policy", "integration_id": APP_ID},
                    ],
                    "strict_required_status_checks_policy": True,
                    "do_not_enforce_on_create": True,
                },
            },
            {"type": "deletion"},
            {"type": "non_fast_forward"},
            {
                "type": "pull_request",
                "parameters": {
                    "allowed_merge_methods": ["squash"],
                    "dismiss_stale_reviews_on_push": False,
                    "require_code_owner_review": False,
                    "require_last_push_approval": False,
                    "required_approving_review_count": 0,
                    "required_review_thread_resolution": True,
                },
            },
        ],
    }


def snapshot(*, configured: bool = True, **changes: object) -> RepositorySnapshot:
    ruleset = managed_ruleset()
    values: dict[str, object] = {
        "repository": REPOSITORY,
        "default_branch": "main",
        "viewer_permission": "ADMIN",
        "delete_branch_on_merge": configured,
        "actions_default_permission": "read" if configured else "write",
        "actions_can_approve": not configured,
        "private_vulnerability_reporting": configured,
        "labels": frozenset(POLICY.labels) if configured else frozenset(),
        "rulesets": (ruleset,) if configured else (),
        "effective_rules": tuple(ruleset["rules"]) if configured else (),
        "branch_protected": configured,
        "evidence": evidence(),
    }
    values.update(changes)
    return RepositorySnapshot(**values)


class RecordingGh:
    def __init__(self) -> None:
        self.calls: list[tuple[tuple[str, ...], str | None]] = []

    def execute(self, arguments: list[str], input_text: str | None = None) -> str:
        self.calls.append((tuple(arguments), input_text))
        return ""

    def json(self, arguments: list[str]) -> object:
        raise AssertionError(f"unexpected read: {arguments}")


class InstallTests(unittest.TestCase):
    def test_install_renders_target_values_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            plan, files = plan_install(
                ROOT,
                MANIFEST,
                target,
                repository=REPOSITORY,
                default_branch="trunk",
            )
            self.assertTrue(plan.entries)
            self.assertTrue(all(entry.action == "create" for entry in plan.entries))

            apply_install(plan, files, confirmation=f"install:{REPOSITORY}")
            policy = json.loads(
                (target / ".github/lifecycle-policy.json").read_text(encoding="utf-8")
            )
            self.assertEqual(policy["default_branch"], "trunk")
            self.assertIn(
                f"https://github.com/{REPOSITORY}/security/advisories/new",
                (target / "SECURITY.md").read_text(encoding="utf-8"),
            )
            release_workflow = (target / ".github/workflows/prepare-release.yml").read_text(
                encoding="utf-8"
            )
            self.assertEqual(release_workflow.count("DEFAULT_BRANCH: trunk"), 2)
            self.assertEqual(
                inspect_local_install(
                    target,
                    MANIFEST,
                    repository=REPOSITORY,
                    expected_default_branch="trunk",
                ),
                (),
            )

            second_plan, _ = plan_install(
                ROOT,
                MANIFEST,
                target,
                repository=REPOSITORY,
                default_branch="trunk",
            )
            self.assertTrue(all(entry.action == "unchanged" for entry in second_plan.entries))

    def test_install_refuses_conflict_and_wrong_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            conflict = target / ".github/lifecycle-policy.json"
            conflict.parent.mkdir(parents=True)
            conflict.write_text("do not replace\n", encoding="utf-8")
            plan, files = plan_install(
                ROOT,
                MANIFEST,
                target,
                repository=REPOSITORY,
                default_branch="main",
            )
            self.assertIn(".github/lifecycle-policy.json", plan.conflicts)
            with self.assertRaisesRegex(LifecycleError, "confirmation"):
                apply_install(plan, files, confirmation="")
            with self.assertRaisesRegex(LifecycleError, "refuses to overwrite"):
                apply_install(plan, files, confirmation=f"install:{REPOSITORY}")
            self.assertEqual(conflict.read_text(encoding="utf-8"), "do not replace\n")

    def test_install_treats_symlink_parent_as_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            target = Path(directory)
            (target / ".github").symlink_to(Path(outside), target_is_directory=True)
            plan, _ = plan_install(
                ROOT,
                MANIFEST,
                target,
                repository=REPOSITORY,
                default_branch="main",
            )
            self.assertTrue(any(path.startswith(".github/") for path in plan.conflicts))
            self.assertEqual(list(Path(outside).iterdir()), [])

    def test_install_rejects_invalid_repository_and_source_target(self) -> None:
        with (
            tempfile.TemporaryDirectory() as directory,
            self.assertRaisesRegex(LifecycleError, "owner/name"),
        ):
            plan_install(
                ROOT,
                MANIFEST,
                Path(directory),
                repository="not-a-repository",
                default_branch="main",
            )
        with self.assertRaisesRegex(LifecycleError, "must differ"):
            plan_install(
                ROOT,
                MANIFEST,
                ROOT,
                repository=REPOSITORY,
                default_branch="main",
            )

    def test_install_rejects_path_like_repository_and_unsafe_branch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            with self.assertRaisesRegex(LifecycleError, "owner/name"):
                plan_install(
                    ROOT,
                    MANIFEST,
                    target,
                    repository="../service",
                    default_branch="main",
                )
            with self.assertRaisesRegex(LifecycleError, "safe Git branch"):
                plan_install(
                    ROOT,
                    MANIFEST,
                    target,
                    repository=REPOSITORY,
                    default_branch="main\npermissions: write-all",
                )


class DoctorAndBootstrapTests(unittest.TestCase):
    def test_doctor_accepts_healthy_repository(self) -> None:
        self.assertEqual(inspect_remote_repository(snapshot(), POLICY), ())

    def test_doctor_reports_remote_drift(self) -> None:
        findings = inspect_remote_repository(snapshot(configured=False), POLICY)
        codes = {finding.code for finding in findings}
        self.assertTrue(
            {
                "actions-permissions",
                "delete-branch-disabled",
                "pvr-disabled",
                "labels-missing",
                "required-checks-missing",
                "managed-ruleset-missing",
                "branch-not-protected",
            }.issubset(codes)
        )

    def test_bootstrap_fresh_repository_builds_explicit_plan(self) -> None:
        plan = build_bootstrap_plan(snapshot(configured=False), POLICY)
        self.assertEqual(plan.blockers, ())
        self.assertEqual(plan.ruleset_method, "create")
        self.assertEqual(plan.missing_labels, tuple(sorted(POLICY.labels)))
        self.assertTrue(plan.update_actions_permissions)
        self.assertTrue(plan.enable_private_vulnerability_reporting)
        self.assertTrue(plan.update_delete_branch_on_merge)
        status_rule = next(
            rule
            for rule in plan.ruleset_payload["rules"]
            if rule["type"] == "required_status_checks"
        )
        self.assertEqual(
            status_rule["parameters"]["required_status_checks"],
            [
                {"context": "lifecycle-policy", "integration_id": APP_ID},
                {"context": "validate", "integration_id": APP_ID},
            ],
        )

    def test_bootstrap_is_idempotent_for_matching_ruleset(self) -> None:
        plan = build_bootstrap_plan(snapshot(), POLICY)
        self.assertEqual(plan.blockers, ())
        self.assertEqual(plan.actions, ())
        self.assertIsNone(plan.ruleset_method)

    def test_bootstrap_requires_open_unambiguous_evidence(self) -> None:
        invalid_evidence = evidence(
            state="CLOSED",
            successful_integrations={
                "validate": frozenset({APP_ID, 99}),
                "lifecycle-policy": frozenset(),
            },
        )
        plan = build_bootstrap_plan(snapshot(configured=False, evidence=invalid_evidence), POLICY)
        self.assertIn("bootstrap evidence PR must still be open", plan.blockers)
        self.assertTrue(any("exactly one" in blocker for blocker in plan.blockers))
        self.assertIsNone(plan.ruleset_payload)

    def test_bootstrap_blocks_bypass_and_overlapping_ruleset(self) -> None:
        existing = managed_ruleset()
        existing["bypass_actors"] = [{"actor_id": 1, "actor_type": "Team"}]
        other = {
            "id": 456,
            "name": "other",
            "enforcement": "active",
            "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
            "rules": [{"type": "deletion"}],
        }
        plan = build_bootstrap_plan(snapshot(rulesets=(existing, other)), POLICY)
        self.assertTrue(any("bypass" in blocker for blocker in plan.blockers))
        self.assertTrue(any("another active ruleset" in blocker for blocker in plan.blockers))

    def test_bootstrap_preserves_stronger_review_and_unknown_rule(self) -> None:
        existing = managed_ruleset()
        pull_request = next(rule for rule in existing["rules"] if rule["type"] == "pull_request")
        pull_request["parameters"]["required_approving_review_count"] = 2
        existing["rules"].append({"type": "required_signatures"})
        plan = build_bootstrap_plan(snapshot(rulesets=(existing,)), POLICY)
        self.assertEqual(plan.blockers, ())
        self.assertIsNone(plan.ruleset_method)
        rules = plan.ruleset_payload["rules"]
        rendered_pr = next(rule for rule in rules if rule["type"] == "pull_request")
        self.assertEqual(rendered_pr["parameters"]["required_approving_review_count"], 2)
        self.assertIn({"type": "required_signatures"}, rules)

    def test_bootstrap_apply_uses_parameterized_gh_calls(self) -> None:
        plan = build_bootstrap_plan(snapshot(configured=False), POLICY)
        client = RecordingGh()
        with self.assertRaisesRegex(LifecycleError, "confirmation"):
            apply_bootstrap(client, plan, confirmation="bootstrap:wrong/repository")
        self.assertEqual(client.calls, [])

        apply_bootstrap(client, plan, confirmation=f"bootstrap:{REPOSITORY}")
        arguments = [call[0] for call in client.calls]
        self.assertEqual(arguments[0][0:3], ("api", "--method", "PUT"))
        self.assertEqual(
            sum(args[0:2] == ("label", "create") for args in arguments),
            len(POLICY.labels),
        )
        self.assertIn(
            ("api", "--method", "POST", f"repos/{REPOSITORY}/rulesets", "--input", "-"),
            arguments,
        )
        for arguments_list, input_text in client.calls:
            self.assertNotIn(";", arguments_list)
            if input_text is not None:
                json.loads(input_text)

    def test_bootstrap_rejects_non_admin_apply(self) -> None:
        plan = build_bootstrap_plan(
            snapshot(configured=False, viewer_permission="MAINTAIN"), POLICY
        )
        self.assertIn("bootstrap apply requires ADMIN repository permission", plan.blockers)
        with self.assertRaisesRegex(LifecycleError, "blocked"):
            apply_bootstrap(RecordingGh(), plan, confirmation=f"bootstrap:{REPOSITORY}")


if __name__ == "__main__":
    unittest.main()
