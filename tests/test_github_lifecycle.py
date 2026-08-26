from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.github_lifecycle.common import LifecycleError, load_policy
from scripts.github_lifecycle.package import load_manifest, package_bundle
from scripts.github_lifecycle.pr import validate_pr_body
from scripts.github_lifecycle.release import (
    ReleaseRequest,
    prepare_release,
    validate_release_inputs,
)

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / ".github" / "lifecycle-policy.json"


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


if __name__ == "__main__":
    unittest.main()
