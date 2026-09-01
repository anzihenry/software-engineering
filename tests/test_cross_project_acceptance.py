from __future__ import annotations

import itertools
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import call, patch

import yaml

from scripts.github_lifecycle.adapters import load_adapter, run_adapter
from scripts.github_lifecycle.adoption import (
    apply_install,
    inspect_local_install,
    plan_install,
)
from scripts.github_lifecycle.common import load_policy
from scripts.github_lifecycle.package import (
    SUPPORTED_PROFILES,
    detect_installed_profile,
    package_bundle,
)
from scripts.github_lifecycle.repository import (
    CheckEvidence,
    RepositorySnapshot,
    build_bootstrap_plan,
)

ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "tests/fixtures/github-lifecycle-acceptance-matrix.json"
MANIFEST = Path("automation/github-lifecycle-manifest.json")
ADAPTER_CATALOG = ROOT / "automation/github-lifecycle-adapters.json"
POLICY = load_policy(ROOT / ".github/lifecycle-policy.json")
REPOSITORY = "example/acceptance-service"
APP_ID = 15368
PINNED_ACTION_LINE = re.compile(r"uses: [^@\s]+@[0-9a-f]{40} # v\d+\.\d+\.\d+")


def load_json_object(path: Path) -> dict[str, object]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    return raw


def create_required_paths(target: Path, adapter_case: dict[str, object]) -> None:
    raw_paths = adapter_case["required_paths"]
    if not isinstance(raw_paths, list):
        raise AssertionError("required_paths must be an array")
    for raw_path in raw_paths:
        if not isinstance(raw_path, dict):
            raise AssertionError("required path entry must be an object")
        relative = raw_path.get("path")
        kind = raw_path.get("kind")
        if not isinstance(relative, str) or kind not in {"file", "directory"}:
            raise AssertionError("required path entry is invalid")
        destination = target / relative
        if kind == "directory":
            destination.mkdir(parents=True)
            continue
        content = raw_path.get("content")
        if not isinstance(content, str):
            raise AssertionError("required file content must be a string")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")


def unconfigured_snapshot() -> RepositorySnapshot:
    evidence = CheckEvidence(
        pull_request_number=42,
        pull_request_url=f"https://github.com/{REPOSITORY}/pull/42",
        state="OPEN",
        base_branch="main",
        head_sha="a" * 40,
        successful_integrations={
            "validate": frozenset({APP_ID}),
            "lifecycle-policy": frozenset({APP_ID}),
        },
    )
    return RepositorySnapshot(
        repository=REPOSITORY,
        default_branch="main",
        viewer_permission="ADMIN",
        delete_branch_on_merge=False,
        actions_default_permission="write",
        actions_can_approve=True,
        private_vulnerability_reporting=False,
        labels=frozenset(),
        rulesets=(),
        effective_rules=(),
        branch_protected=False,
        evidence=evidence,
    )


class CrossProjectAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = load_json_object(MATRIX_PATH)
        cls.adapters = cls.matrix["adapters"]
        cls.profiles = cls.matrix["profiles"]
        cls.cases = cls.matrix["cases"]
        if not isinstance(cls.adapters, dict):
            raise AssertionError("matrix adapters must be an object")
        if not isinstance(cls.profiles, dict):
            raise AssertionError("matrix profiles must be an object")
        if not isinstance(cls.cases, list):
            raise AssertionError("matrix cases must be an array")

    def test_matrix_is_the_complete_adapter_profile_product(self) -> None:
        catalog = load_json_object(ADAPTER_CATALOG)
        catalog_adapters = catalog.get("adapters")
        self.assertIsInstance(catalog_adapters, dict)
        self.assertEqual(self.matrix.get("schema_version"), 1)
        self.assertEqual(set(self.adapters), set(catalog_adapters))
        self.assertEqual(set(self.profiles), set(SUPPORTED_PROFILES))

        actual_cases = []
        for raw_case in self.cases:
            self.assertIsInstance(raw_case, dict)
            self.assertEqual(set(raw_case), {"adapter", "profile"})
            actual_cases.append((raw_case["adapter"], raw_case["profile"]))
        expected_cases = list(itertools.product(sorted(self.adapters), sorted(self.profiles)))
        self.assertEqual(actual_cases, expected_cases)

    def test_all_adapter_profile_combinations_pass_the_adoption_contract(self) -> None:
        for raw_case in self.cases:
            adapter_name = raw_case["adapter"]
            profile_name = raw_case["profile"]
            adapter_case = self.adapters[adapter_name]
            profile_case = self.profiles[profile_name]
            self.assertIsInstance(adapter_case, dict)
            self.assertIsInstance(profile_case, dict)
            with (
                self.subTest(adapter=adapter_name, profile=profile_name),
                tempfile.TemporaryDirectory() as directory,
            ):
                target = Path(directory)
                create_required_paths(target, adapter_case)

                plan, files = plan_install(
                    ROOT,
                    MANIFEST,
                    target,
                    repository=REPOSITORY,
                    default_branch="main",
                    profile=profile_name,
                    adapter=adapter_name,
                )
                self.assertEqual(plan.adapter, adapter_name)
                self.assertEqual(plan.profile, profile_name)
                self.assertTrue(all(entry.action == "create" for entry in plan.entries))

                contents = dict(files)
                workflow_names = {
                    Path(path).name for path in contents if path.startswith(".github/workflows/")
                }
                self.assertEqual(workflow_names, set(profile_case["workflow_names"]))
                for path, content in contents.items():
                    if path.endswith((".yml", ".yaml")):
                        self.assertIsNotNone(yaml.safe_load(content), path)

                validate_text = contents[".github/workflows/validate.yml"].decode()
                validate = yaml.safe_load(validate_text)
                self.assertEqual(validate["jobs"]["validate"]["runs-on"], adapter_case["runner"])
                action_lines = [
                    line.strip() for line in validate_text.splitlines() if "uses:" in line
                ]
                self.assertTrue(action_lines)
                self.assertTrue(all(PINNED_ACTION_LINE.fullmatch(line) for line in action_lines))

                dependabot = yaml.safe_load(contents[".github/dependabot.yml"])
                ecosystems = {update["package-ecosystem"] for update in dependabot["updates"]}
                self.assertEqual(
                    ecosystems,
                    {adapter_case["dependabot_ecosystem"], "github-actions"},
                )

                apply_install(plan, files, confirmation=f"install:{REPOSITORY}")
                self.assertEqual(detect_installed_profile(target, target / MANIFEST), profile_name)
                self.assertEqual(
                    inspect_local_install(
                        target,
                        MANIFEST,
                        repository=REPOSITORY,
                        expected_default_branch="main",
                        profile=profile_name,
                    ),
                    (),
                )

                second_plan, _ = plan_install(
                    ROOT,
                    MANIFEST,
                    target,
                    repository=REPOSITORY,
                    default_branch="main",
                    profile=profile_name,
                    adapter="auto",
                )
                self.assertEqual(second_plan.adapter, adapter_name)
                self.assertTrue(all(entry.action == "unchanged" for entry in second_plan.entries))

                adapter_config = target / ".github/lifecycle-adapter.json"
                adapter = load_adapter(adapter_config)
                with patch("scripts.github_lifecycle.adapters.subprocess.run") as execute:
                    execute.return_value.returncode = 0
                    run_adapter(adapter_config, target)
                self.assertEqual(
                    execute.call_args_list,
                    [
                        call(command, cwd=target.resolve(), check=False)
                        for command in adapter.check_commands
                    ],
                )

                bootstrap = build_bootstrap_plan(
                    unconfigured_snapshot(), POLICY, profile=profile_name
                )
                self.assertEqual(bootstrap.blockers, ())
                self.assertEqual(
                    {action.kind for action in bootstrap.actions},
                    set(profile_case["bootstrap_action_kinds"]),
                )

                first_required = adapter.required_files[0]
                (target / first_required).unlink()
                validate_path = target / ".github/workflows/validate.yml"
                validate_path.write_text(
                    validate_path.read_text(encoding="utf-8") + "# acceptance drift\n",
                    encoding="utf-8",
                )
                finding_codes = {
                    finding.code
                    for finding in inspect_local_install(
                        target,
                        MANIFEST,
                        repository=REPOSITORY,
                        expected_default_branch="main",
                        profile=profile_name,
                    )
                }
                self.assertIn("adapter-required-path-missing", finding_codes)
                self.assertIn("adapter-file-drift", finding_codes)

    def test_each_profile_package_is_deterministic(self) -> None:
        for profile_name in sorted(self.profiles):
            with self.subTest(profile=profile_name), tempfile.TemporaryDirectory() as directory:
                output_root = Path(directory)
                first = package_bundle(
                    ROOT,
                    MANIFEST,
                    output_root / "first.zip",
                    profile=profile_name,
                )
                second = package_bundle(
                    ROOT,
                    MANIFEST,
                    output_root / "second.zip",
                    profile=profile_name,
                )
                self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
