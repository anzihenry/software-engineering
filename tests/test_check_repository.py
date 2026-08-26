from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.check_repository import (
    DELIVERY_TEMPLATES,
    END_TO_END_EXERCISES,
    PHASES,
    TRACEABILITY_FIELDS,
    WORKFLOW_DELIVERY_TEMPLATES,
    check_delivery_templates,
    check_end_to_end_exercises,
    check_links,
    check_markdown_format,
    check_navigation,
    check_skill_structure,
    check_yaml,
)


def write_valid_delivery_templates(root: Path) -> None:
    templates_root = root / "templates" / "delivery"
    templates_root.mkdir(parents=True)
    navigation_links = "\n".join(f"[{name}]({name})" for name in DELIVERY_TEMPLATES)
    (templates_root / "README.md").write_text(
        f"# Templates\n\n{navigation_links}\n", encoding="utf-8"
    )
    for name, lifecycle_stages in DELIVERY_TEMPLATES.items():
        metadata = {
            "template_name": Path(name).stem,
            "template_version": 1,
            "lifecycle_stages": list(lifecycle_stages),
            "traceability_fields": list(TRACEABILITY_FIELDS),
        }
        frontmatter = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False)
        traceability_lines = "\n".join(
            (
                "- 记录 ID：",
                "- 记录类型：",
                "- 状态：",
                "- 所有者：",
                "- 决策权限：",
                "- 风险等级：",
                "- 关联记录：",
                "- 源码/制品版本：",
                "- 环境与适用范围：",
                "- 证据：",
                "- 创建时间及时区：",
                "- 更新时间及时区：",
            )
        )
        (templates_root / name).write_text(
            f"---\n{frontmatter}---\n# Template\n\n## 追溯信息\n\n{traceability_lines}\n",
            encoding="utf-8",
        )

    workflows_root = root / "docs" / "workflows"
    workflows_root.mkdir(parents=True)
    for phase, template_names in WORKFLOW_DELIVERY_TEMPLATES.items():
        links = "\n".join(f"[{name}](../../templates/delivery/{name})" for name in template_names)
        (workflows_root / f"{PHASES[phase]}.md").write_text(
            f"# Workflow\n\n{links}\n", encoding="utf-8"
        )


def write_valid_end_to_end_exercises(root: Path) -> None:
    exercises_root = root / "docs" / "exercises"
    exercises_root.mkdir(parents=True)
    navigation_links = "\n".join(f"[{name}]({name})" for name in END_TO_END_EXERCISES)
    (exercises_root / "README.md").write_text(
        f"# Exercises\n\n{navigation_links}\n", encoding="utf-8"
    )
    required_templates = list(DELIVERY_TEMPLATES)
    template_links = "\n".join(
        f"[{name}](../../templates/delivery/{name})" for name in required_templates
    )
    stage_sections = "\n".join(f"## 阶段 {stage}：Example\n" for stage in PHASES)
    for name, (risk_level, scenario_type) in END_TO_END_EXERCISES.items():
        metadata = {
            "exercise_name": Path(name).stem,
            "exercise_version": 1,
            "risk_level": risk_level,
            "scenario_type": scenario_type,
            "lifecycle_stages": list(PHASES),
            "required_templates": required_templates,
        }
        frontmatter = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False)
        (exercises_root / name).write_text(
            f"---\n{frontmatter}---\n# Exercise\n\n{stage_sections}\n"
            f"{template_links}\n\n## 演练通过条件\n",
            encoding="utf-8",
        )

    lifecycle = root / "docs" / "software-development-lifecycle.md"
    lifecycle.write_text("# Lifecycle\n\n[Exercises](exercises/README.md)\n", encoding="utf-8")


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

    def test_standard_skill_resource_directories_are_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skills = root / "skills"
            for phase in PHASES.values():
                (skills / phase).mkdir(parents=True)
            skill = skills / PHASES[1] / "example-skill"
            (skill / "agents").mkdir(parents=True)
            (skill / "assets").mkdir()
            (skill / "references").mkdir()
            (skill / "scripts").mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: example-skill\ndescription: Example\n---\n# Example\n",
                encoding="utf-8",
            )
            (skill / "agents" / "openai.yaml").write_text(
                "interface:\n"
                '  display_name: "Example"\n'
                '  short_description: "Example skill metadata description"\n',
                encoding="utf-8",
            )

            issues = check_skill_structure(root)

            self.assertFalse(any("unexpected entry" in issue.message for issue in issues))

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

    def test_valid_delivery_templates_are_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_valid_delivery_templates(root)

            issues = check_delivery_templates(root)

            self.assertEqual(issues, [])

    def test_incomplete_traceability_contract_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_valid_delivery_templates(root)
            template = root / "templates" / "delivery" / "opportunity-record.md"
            content = template.read_text(encoding="utf-8")
            template.write_text(content.replace("- updated_at\n", ""), encoding="utf-8")

            messages = {issue.message for issue in check_delivery_templates(root)}

            self.assertIn(
                "traceability_fields must equal the shared traceability contract", messages
            )

    def test_missing_workflow_template_link_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_valid_delivery_templates(root)
            workflow = root / "docs" / "workflows" / f"{PHASES[1]}.md"
            workflow.write_text("# Workflow\n", encoding="utf-8")

            messages = {issue.message for issue in check_delivery_templates(root)}

            self.assertTrue(
                any("workflow is missing delivery template" in item for item in messages)
            )

    def test_missing_visible_traceability_field_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_valid_delivery_templates(root)
            template = root / "templates" / "delivery" / "opportunity-record.md"
            content = template.read_text(encoding="utf-8")
            template.write_text(content.replace("- 决策权限：\n", ""), encoding="utf-8")

            messages = {issue.message for issue in check_delivery_templates(root)}

            self.assertIn("missing visible traceability field: decision_authority", messages)

    def test_valid_end_to_end_exercises_are_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_valid_end_to_end_exercises(root)

            issues = check_end_to_end_exercises(root)

            self.assertEqual(issues, [])

    def test_incomplete_exercise_lifecycle_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_valid_end_to_end_exercises(root)
            exercise = root / "docs" / "exercises" / "low-risk-copy-change.md"
            content = exercise.read_text(encoding="utf-8")
            exercise.write_text(content.replace("## 阶段 8：Example\n", ""), encoding="utf-8")

            messages = {issue.message for issue in check_end_to_end_exercises(root)}

            self.assertIn("missing lifecycle stage section: 8", messages)

    def test_wrong_exercise_risk_level_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_valid_end_to_end_exercises(root)
            exercise = root / "docs" / "exercises" / "high-risk-data-permission-change.md"
            content = exercise.read_text(encoding="utf-8")
            exercise.write_text(
                content.replace("risk_level: high\n", "risk_level: medium\n"),
                encoding="utf-8",
            )

            messages = {issue.message for issue in check_end_to_end_exercises(root)}

            self.assertIn("risk_level must equal 'high'", messages)


if __name__ == "__main__":
    unittest.main()
