from __future__ import annotations

import subprocess
import unittest
from unittest.mock import patch

from scripts.github_lifecycle import repository
from scripts.github_lifecycle.common import LifecycleError
from scripts.github_lifecycle.github import GhClient
from scripts.github_lifecycle.repository_bootstrap import (
    LABEL_PRESENTATION,
    apply_bootstrap,
    build_bootstrap_plan,
    render_bootstrap_plan,
)
from scripts.github_lifecycle.repository_inspection import (
    inspect_remote_repository,
    render_findings,
)
from scripts.github_lifecycle.repository_ruleset import MANAGED_RULE_TYPES, RULESET_NAME
from scripts.github_lifecycle.repository_state import discover_repository


class RepositoryFacadeTests(unittest.TestCase):
    def test_compatibility_facade_reexports_split_responsibilities(self) -> None:
        self.assertIs(repository.GhClient, GhClient)
        self.assertIs(repository.LABEL_PRESENTATION, LABEL_PRESENTATION)
        self.assertIs(repository.MANAGED_RULE_TYPES, MANAGED_RULE_TYPES)
        self.assertEqual(repository.RULESET_NAME, RULESET_NAME)
        self.assertIs(repository.discover_repository, discover_repository)
        self.assertIs(repository.inspect_remote_repository, inspect_remote_repository)
        self.assertIs(repository.render_findings, render_findings)
        self.assertIs(repository.build_bootstrap_plan, build_bootstrap_plan)
        self.assertIs(repository.apply_bootstrap, apply_bootstrap)
        self.assertIs(repository.render_bootstrap_plan, render_bootstrap_plan)


class GhClientTests(unittest.TestCase):
    @patch("scripts.github_lifecycle.github.shutil.which", return_value="/usr/bin/gh")
    @patch("scripts.github_lifecycle.github.subprocess.run")
    def test_json_uses_an_argument_array_and_parses_output(self, run, _which) -> None:
        run.return_value = subprocess.CompletedProcess(
            ["gh", "api", "repos/example/service"], 0, '{"name":"service"}', ""
        )

        result = GhClient(timeout_seconds=7).json(["api", "repos/example/service"])

        self.assertEqual(result, {"name": "service"})
        run.assert_called_once_with(
            ["gh", "api", "repos/example/service"],
            input=None,
            text=True,
            capture_output=True,
            check=False,
            timeout=7,
        )

    @patch("scripts.github_lifecycle.github.shutil.which", return_value="/usr/bin/gh")
    @patch("scripts.github_lifecycle.github.subprocess.run")
    def test_command_failure_is_not_reported_as_success(self, run, _which) -> None:
        run.return_value = subprocess.CompletedProcess(["gh", "api"], 1, "", "denied")

        with self.assertRaisesRegex(LifecycleError, "gh command failed: denied"):
            GhClient().execute(["api"])

    @patch("scripts.github_lifecycle.github.shutil.which", return_value="/usr/bin/gh")
    @patch("scripts.github_lifecycle.github.subprocess.run")
    def test_invalid_json_is_rejected(self, run, _which) -> None:
        run.return_value = subprocess.CompletedProcess(["gh", "api"], 0, "not-json", "")

        with self.assertRaisesRegex(LifecycleError, "gh returned invalid JSON"):
            GhClient().json(["api"])


if __name__ == "__main__":
    unittest.main()
