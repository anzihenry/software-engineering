from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.github_lifecycle.adapters import load_adapter, run_adapter
from scripts.github_lifecycle.adoption import (
    apply_install,
    inspect_local_install,
    plan_install,
)
from scripts.github_lifecycle.common import LifecycleError, load_policy
from scripts.github_lifecycle.package import detect_installed_profile
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
    def test_builtin_language_adapters_generate_stable_validation_and_dependabot(self) -> None:
        expectations = {
            "python": ("ubuntu-latest", 'package-ecosystem: "pip"'),
            "node": ("ubuntu-latest", 'package-ecosystem: "npm"'),
            "swift": ("macos-15", 'package-ecosystem: "swift"'),
            "go": ("ubuntu-latest", 'package-ecosystem: "gomod"'),
        }
        for adapter_name, (runner, ecosystem) in expectations.items():
            with self.subTest(adapter=adapter_name), tempfile.TemporaryDirectory() as directory:
                plan, files = plan_install(
                    ROOT,
                    MANIFEST,
                    Path(directory),
                    repository=REPOSITORY,
                    default_branch="trunk",
                    profile="full",
                    adapter=adapter_name,
                )
                contents = dict(files)
                self.assertEqual(plan.adapter, adapter_name)
                self.assertIn(".github/lifecycle-adapter.json", contents)
                workflow = contents[".github/workflows/validate.yml"].decode()
                self.assertIn("  validate:\n", workflow)
                self.assertIn(f"runs-on: {runner}", workflow)
                self.assertIn("      - trunk", workflow)
                self.assertIn("permissions: {}", workflow)
                self.assertNotIn("pull_request_target", workflow)
                action_lines = [line.strip() for line in workflow.splitlines() if "uses:" in line]
                self.assertTrue(action_lines)
                self.assertTrue(
                    all(
                        re.fullmatch(r"uses: [^@\s]+@[0-9a-f]{40} # v\d+\.\d+\.\d+", line)
                        for line in action_lines
                    )
                )
                self.assertIn(ecosystem, contents[".github/dependabot.yml"].decode())
                self.assertIn(
                    'package-ecosystem: "github-actions"',
                    contents[".github/dependabot.yml"].decode(),
                )

    def test_custom_adapter_controls_commands_and_release_retention(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "target"
            target.mkdir()
            config = Path(directory) / "adapter.json"
            config.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "name": "node-monorepo",
                        "runner": "ubuntu-24.04",
                        "toolchain": {"kind": "node", "version_file": ".nvmrc"},
                        "required_files": ["package.json", ".nvmrc"],
                        "check_commands": [["npm", "ci"], ["npm", "run", "ci"]],
                        "dependabot_ecosystems": ["npm", "github-actions"],
                        "release_artifact_retention_days": 7,
                    }
                ),
                encoding="utf-8",
            )
            plan, files = plan_install(
                ROOT,
                MANIFEST,
                target,
                repository=REPOSITORY,
                default_branch="main",
                adapter="custom",
                adapter_config=config,
            )
            self.assertEqual(plan.adapter, "node-monorepo")
            release = dict(files)[".github/workflows/prepare-release.yml"].decode()
            self.assertEqual(release.count("retention-days: 7"), 1)
            workflow = dict(files)[".github/workflows/validate.yml"].decode()
            self.assertIn('node-version-file: ".nvmrc"', workflow)

    def test_adapter_install_is_idempotent_and_doctor_detects_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "go.mod").write_text("module example.test/service\n", encoding="utf-8")
            plan, files = plan_install(
                ROOT,
                MANIFEST,
                target,
                repository=REPOSITORY,
                default_branch="main",
                profile="governance",
                adapter="go",
            )
            apply_install(plan, files, confirmation=f"install:{REPOSITORY}")
            second, _ = plan_install(
                ROOT,
                MANIFEST,
                target,
                repository=REPOSITORY,
                default_branch="main",
                profile="governance",
            )
            self.assertEqual(second.adapter, "go")
            self.assertTrue(all(entry.action == "unchanged" for entry in second.entries))
            self.assertEqual(
                inspect_local_install(
                    target,
                    MANIFEST,
                    repository=REPOSITORY,
                    expected_default_branch="main",
                    profile="governance",
                ),
                (),
            )
            validate = target / ".github/workflows/validate.yml"
            validate.write_text(
                validate.read_text(encoding="utf-8").replace(
                    "actions/setup-go@b7ad1dad31e06c5925ef5d2fc7ad053ef454303e # v7.0.0",
                    "actions/setup-go@" + "f" * 40 + " # v7.1.0",
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                inspect_local_install(
                    target,
                    MANIFEST,
                    repository=REPOSITORY,
                    expected_default_branch="main",
                    profile="governance",
                ),
                (),
            )
            (target / ".github/workflows/validate.yml").write_text("changed\n", encoding="utf-8")
            codes = {
                finding.code
                for finding in inspect_local_install(
                    target,
                    MANIFEST,
                    repository=REPOSITORY,
                    expected_default_branch="main",
                    profile="governance",
                )
            }
            self.assertIn("adapter-file-drift", codes)

    def test_adapter_rejects_unsafe_runner_and_executes_argument_arrays(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marker = root / "go.mod"
            marker.write_text("module example.test/service\n", encoding="utf-8")
            config = root / "adapter.json"
            raw = {
                "schema_version": 1,
                "name": "custom-go",
                "runner": "ubuntu-latest",
                "toolchain": {"kind": "go", "version_file": "go.mod"},
                "required_files": ["go.mod"],
                "check_commands": [["go", "test", "./..."]],
                "dependabot_ecosystems": ["gomod", "github-actions"],
                "release_artifact_retention_days": 30,
            }
            config.write_text(json.dumps(raw), encoding="utf-8")
            with patch("scripts.github_lifecycle.adapters.subprocess.run") as execute:
                execute.return_value.returncode = 0
                run_adapter(config, root)
            execute.assert_called_once_with(
                ("go", "test", "./..."), cwd=root.resolve(), check=False
            )

            raw["runner"] = "ubuntu-latest\npermissions: write-all"
            config.write_text(json.dumps(raw), encoding="utf-8")
            with self.assertRaisesRegex(LifecycleError, "runner contains unsafe"):
                load_adapter(config)

    def test_release_profile_can_upgrade_to_full_without_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            release_plan, release_files = plan_install(
                ROOT,
                MANIFEST,
                target,
                repository=REPOSITORY,
                default_branch="main",
                profile="release",
            )
            apply_install(
                release_plan,
                release_files,
                confirmation=f"install:{REPOSITORY}",
            )
            self.assertEqual(detect_installed_profile(target, target / MANIFEST), "release")

            full_plan, full_files = plan_install(
                ROOT,
                MANIFEST,
                target,
                repository=REPOSITORY,
                default_branch="main",
                profile="full",
            )
            self.assertEqual(full_plan.conflicts, ())
            self.assertTrue(any(entry.action == "create" for entry in full_plan.entries))
            apply_install(full_plan, full_files, confirmation=f"install:{REPOSITORY}")
            self.assertEqual(detect_installed_profile(target, target / MANIFEST), "full")

            release_again, _ = plan_install(
                ROOT,
                MANIFEST,
                target,
                repository=REPOSITORY,
                default_branch="main",
                profile="release",
            )
            self.assertEqual(release_again.conflicts, ())
            self.assertTrue(all(entry.action == "unchanged" for entry in release_again.entries))

            (target / ".github/PULL_REQUEST_TEMPLATE.md").unlink()
            with self.assertRaisesRegex(LifecycleError, "partial or mixed installation"):
                detect_installed_profile(target, target / MANIFEST)

    def test_profiles_install_only_their_declared_assets(self) -> None:
        expected_workflows = {
            "governance": {"lifecycle-policy.yml"},
            "incident": {
                "audit-lifecycle-records.yml",
                "open-retrospective.yml",
                "transition-incident.yml",
            },
            "release": {"prepare-release.yml"},
            "full": {
                "audit-lifecycle-records.yml",
                "lifecycle-policy.yml",
                "open-retrospective.yml",
                "prepare-release.yml",
                "transition-incident.yml",
            },
        }
        for profile, workflows in expected_workflows.items():
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as directory:
                plan, files = plan_install(
                    ROOT,
                    MANIFEST,
                    Path(directory),
                    repository=REPOSITORY,
                    default_branch="main",
                    profile=profile,
                )
                paths = {entry.path for entry in plan.entries}
                actual_workflows = {
                    Path(path).name for path in paths if path.startswith(".github/workflows/")
                }
                self.assertEqual(plan.profile, profile)
                self.assertEqual(actual_workflows, workflows)
                apply_install(plan, files, confirmation=f"install:{REPOSITORY}")
                self.assertEqual(
                    inspect_local_install(
                        Path(directory),
                        MANIFEST,
                        repository=REPOSITORY,
                        expected_default_branch="main",
                        profile=profile,
                    ),
                    (),
                )

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
    def test_doctor_scopes_remote_findings_to_profile(self) -> None:
        unconfigured = snapshot(configured=False, evidence=None)

        release_codes = {
            finding.code
            for finding in inspect_remote_repository(unconfigured, POLICY, profile="release")
        }
        incident_codes = {
            finding.code
            for finding in inspect_remote_repository(unconfigured, POLICY, profile="incident")
        }
        governance_codes = {
            finding.code
            for finding in inspect_remote_repository(unconfigured, POLICY, profile="governance")
        }

        self.assertEqual(release_codes, {"actions-permissions"})
        self.assertEqual(incident_codes, {"actions-permissions", "labels-missing", "pvr-disabled"})
        self.assertNotIn("labels-missing", governance_codes)
        self.assertNotIn("pvr-disabled", governance_codes)
        self.assertIn("managed-ruleset-missing", governance_codes)

    def test_bootstrap_scopes_actions_and_evidence_to_profile(self) -> None:
        unconfigured = snapshot(configured=False, evidence=None)

        release_plan = build_bootstrap_plan(unconfigured, POLICY, profile="release")
        incident_plan = build_bootstrap_plan(unconfigured, POLICY, profile="incident")
        governance_plan = build_bootstrap_plan(unconfigured, POLICY, profile="governance")

        self.assertEqual(release_plan.blockers, ())
        self.assertEqual({action.kind for action in release_plan.actions}, {"actions-permissions"})
        self.assertEqual(incident_plan.blockers, ())
        self.assertEqual(
            {action.kind for action in incident_plan.actions},
            {"actions-permissions", "label", "private-vulnerability-reporting"},
        )
        self.assertIn("bootstrap requires an evidence PR", governance_plan.blockers)

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
