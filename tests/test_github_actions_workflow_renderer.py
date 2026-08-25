from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import ModuleType

import yaml

MODULE_PATH = (
    Path(__file__).parents[1]
    / "skills/05-integration-validation/github-actions-bootstrap/scripts/render_workflow.py"
)


def load_renderer() -> ModuleType:
    spec = importlib.util.spec_from_file_location("github_actions_workflow_renderer", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load renderer from {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


renderer = load_renderer()


class WorkflowRendererTests(unittest.TestCase):
    def valid_plan(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "workflow_name": "CI",
            "default_branch": "main",
            "runner": "ubuntu-latest",
            "timeout_minutes": 15,
            "merge_group": False,
            "steps": [
                {
                    "name": "Check out repository",
                    "uses": "actions/checkout@0123456789abcdef0123456789abcdef01234567",
                },
                {"name": "Run project checks", "run": "./scripts/check"},
            ],
        }

    def test_rendered_workflow_has_stable_ci_contract(self) -> None:
        plan = renderer.validate_plan(self.valid_plan())

        content = renderer.render_workflow(plan)
        workflow = yaml.safe_load(content)

        self.assertEqual(workflow["on"]["push"]["branches"], ["main"])
        self.assertIsNone(workflow["on"]["pull_request"])
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        self.assertEqual(workflow["jobs"]["validate"]["name"], "validate")
        self.assertTrue(workflow["concurrency"]["cancel-in-progress"])

    def test_unpinned_remote_action_is_rejected(self) -> None:
        plan = self.valid_plan()
        plan["steps"][0]["uses"] = "actions/checkout@v7"

        with self.assertRaisesRegex(renderer.PlanError, "full 40-character SHA"):
            renderer.validate_plan(plan)

    def test_existing_output_is_not_overwritten_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "ci.yml"
            output.write_text("existing\n", encoding="utf-8")

            with self.assertRaisesRegex(renderer.PlanError, "already exists"):
                renderer.write_workflow(output, "replacement\n", force=False)

            self.assertEqual(output.read_text(encoding="utf-8"), "existing\n")


if __name__ == "__main__":
    unittest.main()
