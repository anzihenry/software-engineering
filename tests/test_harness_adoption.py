from __future__ import annotations

import copy
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.harness_adoption import COMMANDS, PREREQUISITES, inspect, run_checks


class AdoptionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / "project"
        self.harness = Path(self.temp.name).resolve() / "harness"
        for root in [self.root, self.harness]:
            root.mkdir()
            self.git(root, "init", "-b", "main")
            self.git(root, "config", "user.name", "Fixture")
            self.git(root, "config", "user.email", "fixture@example.invalid")
        for path in PREREQUISITES | {
            "skills/04-implementation-and-self-test/language-coding-standards/references/python.md"
        }:
            target = self.harness / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("Fixture prerequisite\n", encoding="utf-8")
        self.git(self.harness, "add", ".")
        self.git(self.harness, "commit", "-m", "knowledge")
        entry = self.root / "AGENTS.md"
        entry.write_text(
            "git-branch-management language-coding-standards "
            "documentation-maintenance documentation-delivery-validation\n",
            encoding="utf-8",
        )
        self.git(self.root, "add", ".")
        self.git(self.root, "commit", "-m", "baseline")
        self.base = self.git(self.root, "rev-parse", "HEAD").strip()
        self.git(self.root, "checkout", "-b", "codex/trial")
        self.manifest = {
            "schema_version": 1,
            "harness_revision": self.git(self.harness, "rev-parse", "HEAD").strip(),
            "scope": "offline",
            "language_references": ["python"],
            "entrypoints": {"AGENTS.md": hashlib.sha256(entry.read_bytes()).hexdigest()},
            "protected_branches": ["main"],
            "global_context": "isolated fixture",
            "unresolved_overrides": [],
            "owners": {"maintainer": "Fixture"},
            "task_facts": "fixture task",
            "independent_review": "separate fixture reviewer",
            "commands": {
                name: [sys.executable, "-c", "print('actual fixture command')"] for name in COMMANDS
            },
        }

    @staticmethod
    def git(root: Path, *args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
        ).stdout

    def inspect(self, manifest: dict | None = None) -> dict:
        return inspect(self.root, self.harness, manifest or self.manifest, self.base)

    def test_available_is_separate_from_behavior_and_remote(self) -> None:
        result = self.inspect()
        self.assertEqual(result["status"], "available")
        self.assertIn("not loading proof", result["behavior"])
        self.assertIn("separate GitHub evidence", result["remote_enforcement"])

    def test_missing_prerequisite_and_wrong_pin_block(self) -> None:
        with self.subTest("pin"):
            self.manifest["harness_revision"] = "0" * 40
            with self.assertRaisesRegex(ValueError, "revision mismatch"):
                self.inspect()
        self.manifest["harness_revision"] = self.git(self.harness, "rev-parse", "HEAD").strip()
        path = self.harness / "docs/evidence-trust.md"
        path.unlink()
        self.git(self.harness, "add", ".")
        self.git(self.harness, "commit", "-m", "missing")
        self.manifest["harness_revision"] = self.git(self.harness, "rev-parse", "HEAD").strip()
        with self.assertRaisesRegex(ValueError, "missing prerequisite"):
            self.inspect()

    def test_local_override_inventory_and_stale_digest_block(self) -> None:
        (self.root / "nested").mkdir()
        (self.root / "nested/AGENTS.md").write_text("local override", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "completely inventoried"):
            self.inspect()
        (self.root / "nested/AGENTS.md").unlink()
        (self.root / "AGENTS.md").write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "entrypoint changed"):
            self.inspect()

    def test_false_prerequisites_and_authority_configuration_block(self) -> None:
        cases = [
            ("language_references", ["common"]),
            ("language_references", [["python"]]),
            ("owners", True),
            ("owners", {"maintainer": " "}),
            ("task_facts", True),
            ("independent_review", " "),
            ("unresolved_overrides", ["conflict"]),
            ("unresolved_overrides", None),
        ]
        for key, value in cases:
            with self.subTest(key=key, value=value):
                manifest = copy.deepcopy(self.manifest)
                manifest[key] = value
                with self.assertRaises(ValueError):
                    self.inspect(manifest)

    def test_protected_branch_and_incomplete_commands_block(self) -> None:
        self.git(self.root, "checkout", "main")
        with self.assertRaisesRegex(ValueError, "feature branch"):
            self.inspect()
        self.git(self.root, "checkout", "codex/trial")
        del self.manifest["commands"]["test"]
        with self.assertRaisesRegex(ValueError, "command set"):
            self.inspect()

    def test_actual_failed_command_retains_original_output(self) -> None:
        self.manifest["commands"]["documentation"] = [
            sys.executable,
            "-c",
            "import sys; print('failed detail'); sys.exit(3)",
        ]
        result = run_checks(self.root, self.harness, self.manifest, self.base)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["failed_check"], "documentation")
        self.assertEqual(result["reports"]["documentation"]["returncode"], 3)
        self.assertIn("failed detail", result["reports"]["documentation"]["stdout"])
        self.assertIn("build", result["reports"])
        self.assertNotIn("test", result["reports"])

    def test_command_literal_braces_are_preserved(self) -> None:
        self.manifest["commands"]["test"] = [
            "{python}",
            "-c",
            "print({'literal': '{unknown}'}); print(1 < 2)",
        ]
        result = run_checks(self.root, self.harness, self.manifest, self.base)
        self.assertEqual(result["status"], "checks-passed")
        self.assertIn("{'literal': '{unknown}'}", result["reports"]["test"]["stdout"])
        self.assertIn("True", result["reports"]["test"]["stdout"])

    def test_commands_cannot_claim_old_source_after_mutation(self) -> None:
        self.manifest["commands"]["test"] = [
            sys.executable,
            "-c",
            "from pathlib import Path; Path('AGENTS.md').write_text('changed', encoding='utf-8')",
        ]
        result = run_checks(self.root, self.harness, self.manifest, self.base)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason"], "target or knowledge changed during checks")
        self.assertNotEqual(result["target_binding"], result["final_target_binding"])
        self.assertEqual(result["reports"]["test"]["returncode"], 0)

    def test_deleted_tracked_file_preserves_reports_when_binding_unreadable(self) -> None:
        self.manifest["commands"]["test"] = [
            sys.executable,
            "-c",
            "from pathlib import Path; Path('AGENTS.md').unlink(); print('actual deletion')",
        ]
        result = run_checks(self.root, self.harness, self.manifest, self.base)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason"], "final binding unavailable")
        self.assertEqual(result["reports"]["test"]["returncode"], 0)
        self.assertIn("actual deletion", result["reports"]["test"]["stdout"])
        self.assertIn("AGENTS.md", result["error"])
        self.assertIn("AGENTS.md", result["target_binding"]["files"])
        self.assertEqual(set(result["reports"]), COMMANDS)

    def test_symlink_replacement_cannot_hide_behind_same_bytes_and_dirty_tree(self) -> None:
        (self.root / "note.txt").write_text("ordinary uncommitted work", encoding="utf-8")
        outside = Path(self.temp.name).resolve() / "outside.txt"
        outside.write_text((self.root / "AGENTS.md").read_text(encoding="utf-8"), encoding="utf-8")
        self.manifest["commands"]["test"] = [
            sys.executable,
            "-c",
            "from pathlib import Path; p=Path('AGENTS.md'); p.unlink(); p.symlink_to("
            + repr(str(outside))
            + ")",
        ]
        result = run_checks(self.root, self.harness, self.manifest, self.base)
        self.assertTrue(result["target_binding"]["working_tree_dirty"])
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason"], "final binding unavailable")
        self.assertRegex(result["error"], "symlink|escapes")
        self.assertEqual(result["reports"]["test"]["returncode"], 0)

    def test_timeout_retains_partial_output_and_prior_reports(self) -> None:
        completed = subprocess.CompletedProcess([], 0, "first report", "")
        timeout = subprocess.TimeoutExpired(["tool"], 60, output=b"partial", stderr=b"detail")
        with (
            patch("scripts.harness_adoption.inspect", return_value={"status": "available"}),
            patch("scripts.harness_adoption.subprocess.run", side_effect=[completed, timeout]),
        ):
            result = run_checks(self.root, self.harness, self.manifest, self.base)
        self.assertEqual(result["failed_check"], "documentation")
        self.assertEqual(result["reports"]["build"]["stdout"], "first report")
        self.assertEqual(result["reports"]["documentation"]["stdout"], "partial")
        self.assertEqual(result["reports"]["documentation"]["stderr"], "detail")
        self.assertNotIn("test", result["reports"])

    def test_nonexistent_executable_retains_blocked_report(self) -> None:
        self.manifest["commands"]["build"] = [str(self.root / "missing-tool")]
        result = run_checks(self.root, self.harness, self.manifest, self.base)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("error", result["reports"]["build"])


if __name__ == "__main__":
    unittest.main()
