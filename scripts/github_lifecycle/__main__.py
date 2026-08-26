from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .common import LifecycleError, load_policy
from .package import package_bundle, render_package_result
from .pr import validate_pr_event


def write_summary(lines: list[str]) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with Path(summary_path).open("a", encoding="utf-8") as summary:
            summary.write("\n".join(lines) + "\n")


def validate_pr(args: argparse.Namespace) -> int:
    result = validate_pr_event(args.event, load_policy(args.policy))
    status = (
        "warning" if result.draft and result.issues else "failed" if result.issues else "passed"
    )
    lines = ["## Lifecycle PR policy", "", f"Status: **{status}**"]
    if result.risk_level:
        lines.append(f"Risk level: `{result.risk_level}`")
    if result.issues:
        lines.extend(["", "Issues:", *(f"- {issue}" for issue in result.issues)])
    else:
        lines.extend(["", "The PR record satisfies the structural lifecycle contract."])
    write_summary(lines)
    print("\n".join(lines))
    return 1 if result.blocks else 0


def package(args: argparse.Namespace) -> int:
    digest = package_bundle(args.root, args.manifest, args.output)
    print(render_package_result(args.output, digest))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    pr_parser = subparsers.add_parser("validate-pr", help="validate a pull request event")
    pr_parser.add_argument("--event", type=Path, required=True)
    pr_parser.add_argument("--policy", type=Path, required=True)
    pr_parser.set_defaults(handler=validate_pr)

    package_parser = subparsers.add_parser("package", help="build a deterministic copy bundle")
    package_parser.add_argument("--root", type=Path, default=Path.cwd())
    package_parser.add_argument("--manifest", type=Path, required=True)
    package_parser.add_argument("--output", type=Path, required=True)
    package_parser.set_defaults(handler=package)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        return int(args.handler(args))
    except LifecycleError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
