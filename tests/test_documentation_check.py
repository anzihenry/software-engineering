"""Behavior tests for target-project documentation delivery gates."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import documentation_check as checker


class DocumentationGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")
        (self.root / "code.py").write_text("print('first')\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "baseline")
        self.base = self.git("rev-parse", "HEAD").strip()
        self.name = "docs/documentation-check.json"
        docs = {
            path: "knowledge"
            for path in (
                "README.md",
                "CHANGELOG.md",
                "docs/README.md",
                "docs/documentation.md",
            )
        }
        self.data = {
            "schema_version": 1,
            "required_checks": ["unit-tests"],
            "standard_version": "0.1.0",
            "owners": {"maintainer": "Fixture team"},
            "documents": docs,
            "legacy": {},
            "raw": {},
        }
        for primary in docs:
            for path, peer in (
                (primary, checker.english(primary)),
                (checker.english(primary), primary),
            ):
                target = self.root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                content = (
                    '---\ntitle: "Entry"\nstatus: current\nowner: maintainer\n'
                    'updated: "2026-01-01"\n---\n\n# Entry\n\n'
                )
                content += f"[Translation]({Path(peer).name})\n"
                if target.name.startswith("README"):
                    related = [
                        p for p in docs if Path(p).parent == Path(primary).parent and p != primary
                    ]
                    for other in related:
                        name = checker.english(other) if ".en.md" in path else other
                        content += f"[Related]({Path(name).name})\n"
                target.write_text(content, encoding="utf-8")
        (self.root / "verification.txt").write_text("Actual fixture verification evidence\n")
        self.write_config()

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(self.root), *args], check=True, capture_output=True, text=True
        ).stdout

    def write_config(self) -> None:
        (self.root / self.name).write_text(json.dumps(self.data), encoding="utf-8")

    def review(self, saved: dict) -> dict:
        return {
            "schema_version": 1,
            "snapshot_digest": saved["digest"],
            "reviewer": "independent-fixture-reviewer",
            "reviewer_role": "fixture reviewer",
            "reviewed_at": "2026-01-01T00:00:00+00:00",
            "independent": True,
            "context": "separate-fixture-context",
            "verdict": "passed",
            "inspected_files": list(saved["files"]),
            "checks": {
                key: {"result": "passed", "evidence": "verification.txt"}
                for key in checker.REVIEW_CHECKS
            },
            "impacts": {
                key: {"result": "reviewed-no-change", "reason": "Fixture scope", "files": []}
                for key in checker.DOMAINS
            },
            "evidence_files": ["verification.txt"],
            "findings": [],
            "required_checks": {"unit-tests": {"result": "passed", "evidence": "verification.txt"}},
        }

    def test_complete_project_and_review_pass(self) -> None:
        saved = checker.snapshot(self.root, self.name, self.base, ["author"])
        self.assertEqual(
            checker.gate(self.root, self.name, saved, self.review(saved))["status"], "passed"
        )

    def test_missing_translation_blocks(self) -> None:
        (self.root / "README.en.md").unlink()
        with self.assertRaises(checker.InvalidDocumentation):
            checker.check(self.root, self.name)

    def test_broken_local_heading_blocks(self) -> None:
        with (self.root / "README.md").open("a") as output:
            output.write("[Missing](#missing)\n")
        with self.assertRaises(checker.InvalidDocumentation):
            checker.check(self.root, self.name)

    def test_valid_local_heading_passes(self) -> None:
        with (self.root / "README.md").open("a") as output:
            output.write("[Entry](#entry)\n")
        checker.check(self.root, self.name)

    def test_implementation_change_invalidates_review(self) -> None:
        saved = checker.snapshot(self.root, self.name, self.base, ["author"])
        (self.root / "code.py").write_text("print('changed')\n")
        with self.assertRaisesRegex(checker.InvalidDocumentation, "stale"):
            checker.gate(self.root, self.name, saved, self.review(saved))

    def test_new_untracked_file_invalidates_review(self) -> None:
        saved = checker.snapshot(self.root, self.name, self.base, ["author"])
        (self.root / "new-code.py").write_text("pass\n")
        with self.assertRaisesRegex(checker.InvalidDocumentation, "stale"):
            checker.gate(self.root, self.name, saved, self.review(saved))

    def test_self_review_and_missing_inspection_block(self) -> None:
        saved = checker.snapshot(self.root, self.name, self.base, ["author"])
        for change in (
            {"reviewer": "author"},
            {"inspected_files": ["verification.txt"]},
            {"findings": [{"status": "open"}]},
            {"impacts": {}},
            {"evidence_files": ["absent.txt"]},
        ):
            with self.subTest(change=change), self.assertRaises(checker.InvalidDocumentation):
                checker.gate(self.root, self.name, saved, {**self.review(saved), **change})

    def test_unknown_markdown_and_changed_legacy_block(self) -> None:
        old = self.root / "old.md"
        old.write_text("Legacy\n")
        with self.assertRaisesRegex(checker.InvalidDocumentation, "unregistered"):
            checker.check(self.root, self.name)
        self.data["legacy"]["old.md"] = {
            "owner": "maintainer",
            "reason": "Migration",
            "due": "2099-01-01",
            "evidence": "verification.txt",
        }
        self.write_config()
        checker.check(self.root, self.name)
        with self.assertRaisesRegex(checker.InvalidDocumentation, "legacy"):
            checker.snapshot(self.root, self.name, self.base, ["author"])

    def test_duplicate_json_and_symlink_block(self) -> None:
        (self.root / self.name).write_text('{"schema_version":1,"schema_version":1}')
        with self.assertRaisesRegex(checker.InvalidDocumentation, "duplicate"):
            checker.check(self.root, self.name)
        self.write_config()
        (self.root / "README.en.md").unlink()
        (self.root / "README.en.md").symlink_to(self.root / "README.md")
        with self.assertRaisesRegex(checker.InvalidDocumentation, "symlink"):
            checker.check(self.root, self.name)

    def test_deleted_source_invalidates_and_mode_change_invalidates(self) -> None:
        saved = checker.snapshot(self.root, self.name, self.base, ["author"])
        (self.root / "code.py").unlink()
        with self.assertRaises(checker.InvalidDocumentation):
            checker.gate(self.root, self.name, saved, self.review(saved))

    def test_english_navigation_and_missing_ci_evidence_block(self) -> None:
        path = self.root / "docs/README.en.md"
        original = path.read_text()
        path.write_text(original.replace("[Related](documentation.en.md)\n", ""))
        with self.assertRaises(checker.InvalidDocumentation):
            checker.check(self.root, self.name)
        path.write_text(original)
        saved = checker.snapshot(self.root, self.name, self.base, ["author"])
        review = self.review(saved)
        review["required_checks"]["unit-tests"]["result"] = "failed"
        with self.assertRaises(checker.InvalidDocumentation):
            checker.gate(self.root, self.name, saved, review)
        review = self.review(saved)
        review["checks"]["bilingual"]["evidence"] = "nonexistent.txt"
        with self.assertRaises(checker.InvalidDocumentation):
            checker.gate(self.root, self.name, saved, review)

    def test_examples_are_not_links_or_anchors(self) -> None:
        self.assertEqual(checker.links("`[example](missing.md)`"), [])
        self.assertNotIn("fake", checker.anchors('```html\n<a id="fake"></a>\n```'))

    def test_permission_and_deleted_diff_require_new_review(self) -> None:
        saved = checker.snapshot(self.root, self.name, self.base, ["author"])
        (self.root / "code.py").chmod(0o755)
        with self.assertRaises(checker.InvalidDocumentation):
            checker.gate(self.root, self.name, saved, self.review(saved))
        (self.root / "code.py").unlink()
        saved = checker.snapshot(self.root, self.name, self.base, ["author"])
        review = self.review(saved)
        review["inspected_files"].remove("code.py")
        with self.assertRaisesRegex(checker.InvalidDocumentation, "unread"):
            checker.gate(self.root, self.name, saved, review)

    def test_date_and_inline_html_examples(self) -> None:
        self.assertNotIn("fake", checker.anchors('Example: `<a id="fake"></a>`'))
        path = self.root / "README.md"
        path.write_text(path.read_text().replace("2026-01-01", "20260101"))
        with self.assertRaisesRegex(checker.InvalidDocumentation, "YYYY-MM-DD"):
            checker.check(self.root, self.name)

    def test_base_cannot_be_git_option(self) -> None:
        with self.assertRaises(checker.InvalidDocumentation):
            checker.check(self.root, self.name, "--output=unexpected-file")
        self.assertFalse((self.root / "unexpected-file").exists())

    def test_optional_translation_is_registered_and_required(self) -> None:
        self.data["translations"] = {"README.md": ["ja"]}
        self.write_config()
        with self.assertRaises(checker.InvalidDocumentation):
            checker.check(self.root, self.name)
        content = (self.root / "README.en.md").read_text()
        content = content.replace("[Related](CHANGELOG.en.md)\n", "")
        (self.root / "README.ja.md").write_text(content)
        with (self.root / "README.md").open("a") as output:
            output.write("[Japanese](README.ja.md)\n")
        checker.check(self.root, self.name)

    def test_legacy_date_is_canonical(self) -> None:
        (self.root / "old.md").write_text("Historical raw text")
        self.data["legacy"]["old.md"] = {
            "owner": "maintainer",
            "reason": "Migration",
            "due": "20990101",
            "evidence": "verification.txt",
        }
        self.write_config()
        with self.assertRaisesRegex(checker.InvalidDocumentation, "YYYY-MM-DD"):
            checker.check(self.root, self.name)

    def test_subdirectory_can_use_domain_index(self) -> None:
        index = "docs/engineering/README.md"
        decision = "docs/engineering/decisions/0001-choice.md"
        for primary in (index, decision):
            self.data["documents"][primary] = "knowledge"
            for path, peer in (
                (primary, checker.english(primary)),
                (checker.english(primary), primary),
            ):
                target = self.root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                text = (self.root / "CHANGELOG.md").read_text()
                text = text.replace("CHANGELOG.en.md", Path(peer).name)
                if primary == index:
                    name = "0001-choice.en.md" if ".en.md" in path else "0001-choice.md"
                    text += f"[Decision](decisions/{name})\n"
                target.write_text(text)
        self.write_config()
        checker.check(self.root, self.name)
        self.assertFalse((self.root / "docs/engineering/decisions/README.md").exists())

    def test_cli_reports_blocked_without_false_success(self) -> None:
        (self.root / "README.en.md").unlink()
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.documentation_check",
                "check",
                "--root",
                str(self.root),
            ],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
