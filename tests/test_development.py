from __future__ import annotations

import unittest
from unittest.mock import call, patch

from scripts.development import QUALITY_PATHS, command_groups, run_commands


class DevelopmentCommandTests(unittest.TestCase):
    def test_check_uses_the_repository_commands_in_order(self) -> None:
        commands = command_groups("/example/python")["check"]

        self.assertEqual(
            commands,
            (
                ("/example/python", "-m", "ruff", "check", *QUALITY_PATHS),
                (
                    "/example/python",
                    "-m",
                    "ruff",
                    "format",
                    "--check",
                    *QUALITY_PATHS,
                ),
                (
                    "/example/python",
                    "-m",
                    "unittest",
                    "discover",
                    "--start-directory",
                    "tests",
                ),
                ("/example/python", "scripts/check_repository.py"),
            ),
        )

    @patch("scripts.development.subprocess.run")
    def test_runner_stops_at_the_first_failure(self, run: object) -> None:
        run.side_effect = [
            type("Result", (), {"returncode": 0})(),
            type("Result", (), {"returncode": 7})(),
        ]

        result = run_commands((("first",), ("second",), ("third",)))

        self.assertEqual(result, 7)
        self.assertEqual(run.call_count, 2)

    @patch("scripts.development.subprocess.run")
    def test_runner_uses_argument_arrays_and_repository_root(self, run: object) -> None:
        run.return_value = type("Result", (), {"returncode": 0})()

        result = run_commands((("tool", "argument with spaces", "; unsafe"),))

        self.assertEqual(result, 0)
        self.assertEqual(
            run.call_args,
            call(("tool", "argument with spaces", "; unsafe"), cwd=unittest.mock.ANY, check=False),
        )


if __name__ == "__main__":
    unittest.main()
