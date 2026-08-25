from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.check_repository import (
    PHASES,
    check_links,
    check_markdown_format,
    check_navigation,
    check_skill_structure,
    check_yaml,
)


class RepositoryCheckTests(unittest.TestCase):
    def test_invalid_yaml_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "invalid.yaml").write_text("key: [unclosed\n", encoding="utf-8")

            issues = check_yaml(root)

            self.assertEqual(len(issues), 1)
            self.assertIn("invalid YAML", issues[0].message)

    def test_broken_local_link_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("# Title\n\n[missing](missing.md)\n", encoding="utf-8")

            issues = check_links(root)

            self.assertEqual(len(issues), 1)
            self.assertIn("broken local link", issues[0].message)

    def test_markdown_format_errors_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("# Title  \n\n### Skipped", encoding="utf-8")

            messages = {issue.message for issue in check_markdown_format(root)}

            self.assertIn("file must end with a newline", messages)
            self.assertIn("trailing whitespace", messages)
            self.assertIn("heading levels must not be skipped", messages)

    def test_invalid_skill_frontmatter_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skills = root / "skills"
            for phase in (
                "01-demand-and-opportunity",
                "02-refinement-and-initiation",
                "03-solution-and-planning",
                "04-implementation-and-self-test",
                "05-integration-validation",
                "06-release-and-change-management",
                "07-operations-and-support",
                "08-measurement-and-retrospective",
            ):
                (skills / phase).mkdir(parents=True)
            skill = skills / "01-demand-and-opportunity" / "example-skill"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: wrong-name\ndescription: Example\n---\n# Example\n",
                encoding="utf-8",
            )

            issues = check_skill_structure(root)

            self.assertTrue(any("frontmatter name" in issue.message for issue in issues))

    def test_missing_navigation_entries_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for phase in PHASES.values():
                (root / "skills" / phase).mkdir(parents=True)
                workflow = root / "docs" / "workflows" / f"{phase}.md"
                workflow.parent.mkdir(parents=True, exist_ok=True)
                workflow.write_text(f"# {phase}\n", encoding="utf-8")
            (root / "skills" / "README.md").write_text("# Skills\n", encoding="utf-8")
            skill = root / "skills" / PHASES[1] / "example" / "SKILL.md"
            skill.parent.mkdir()
            skill.write_text("# Example\n", encoding="utf-8")

            messages = {issue.message for issue in check_navigation(root)}

            self.assertTrue(any("missing from navigation" in message for message in messages))
            self.assertTrue(any("missing from workflow" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
