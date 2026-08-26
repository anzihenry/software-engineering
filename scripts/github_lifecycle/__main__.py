from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .common import LifecycleError, load_policy
from .package import package_bundle, render_package_result
from .pr import validate_pr_event
from .release import build_release_request, prepare_release, validate_release_inputs


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


def prepare_release_command(args: argparse.Namespace) -> int:
    policy = load_policy(args.policy)
    request = build_release_request(
        version=args.version,
        source_sha=args.source_sha,
        risk_level=args.risk_level,
        change_records=args.change_records,
        summary=args.summary,
        repository=args.repository,
        actor=args.actor,
        run_url=args.run_url,
        created_at=args.created_at,
    )
    validate_release_inputs(
        request.version,
        request.source_sha,
        request.risk_level,
        policy,
        dry_run=args.dry_run,
        confirmation=args.confirmation,
    )
    if args.validate_only:
        print("release inputs are valid")
        return 0
    github_paths = (
        args.comparison,
        args.check_runs,
        args.tag_refs,
        args.releases,
        args.output_dir,
    )
    if any(path is None for path in github_paths):
        raise LifecycleError(
            "full release preparation requires comparison, check-runs, tag-refs, "
            "releases, and output-dir"
        )
    result = prepare_release(
        request,
        policy,
        args.comparison,
        args.check_runs,
        args.tag_refs,
        args.releases,
        args.output_dir,
    )
    lines = [
        "## Draft Release candidate",
        "",
        f"Version: `{request.version}`",
        f"Source SHA: `{request.source_sha}`",
        f"Mode: `{'dry-run' if args.dry_run else 'create-draft'}`",
        "",
        f"Release record: `{result.record}`",
        f"Candidate checklist: `{result.checklist}`",
        f"Candidate manifest: `{result.manifest}`",
    ]
    write_summary(lines)
    print("\n".join(lines))
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

    release_parser = subparsers.add_parser(
        "prepare-release", help="validate and render a Draft Release candidate"
    )
    release_parser.add_argument("--policy", type=Path, required=True)
    release_parser.add_argument("--version", required=True)
    release_parser.add_argument("--source-sha", required=True)
    release_parser.add_argument("--risk-level", required=True)
    release_parser.add_argument("--change-records", required=True)
    release_parser.add_argument("--summary", required=True)
    release_parser.add_argument("--repository", required=True)
    release_parser.add_argument("--actor", required=True)
    release_parser.add_argument("--run-url", required=True)
    release_parser.add_argument("--created-at", required=True)
    release_parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    release_parser.add_argument("--confirmation", default="")
    release_parser.add_argument("--validate-only", action="store_true")
    release_parser.add_argument("--comparison", type=Path)
    release_parser.add_argument("--check-runs", type=Path)
    release_parser.add_argument("--tag-refs", type=Path)
    release_parser.add_argument("--releases", type=Path)
    release_parser.add_argument("--output-dir", type=Path)
    release_parser.set_defaults(handler=prepare_release_command)
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
