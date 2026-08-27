"""Run the repository's canonical local development commands."""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUALITY_PATHS = (
    "scripts",
    "tests",
    "skills/05-integration-validation/github-actions-bootstrap/scripts",
)


def command_groups(python: str) -> dict[str, tuple[tuple[str, ...], ...]]:
    lint = ((python, "-m", "ruff", "check", *QUALITY_PATHS),)
    format_check = ((python, "-m", "ruff", "format", "--check", *QUALITY_PATHS),)
    tests = ((python, "-m", "unittest", "discover", "--start-directory", "tests"),)
    repository = ((python, "scripts/check_repository.py"),)
    return {
        "setup": ((python, "-m", "pip", "install", "--requirement", "requirements-dev.txt"),),
        "lint": lint,
        "format-check": format_check,
        "format": ((python, "-m", "ruff", "format", *QUALITY_PATHS),),
        "test": tests,
        "repository": repository,
        "check": (*lint, *format_check, *tests, *repository),
    }


def run_commands(commands: Sequence[Sequence[str]]) -> int:
    for command in commands:
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode != 0:
            return result.returncode
    return 0


def parse_args(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("setup", "lint", "format-check", "format", "test", "repository", "check"),
    )
    return parser.parse_args(arguments)


def main(arguments: Sequence[str] | None = None) -> int:
    args = parse_args(arguments)
    return run_commands(command_groups(sys.executable)[args.command])


if __name__ == "__main__":
    raise SystemExit(main())
