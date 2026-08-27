from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

from .adoption import (
    apply_install,
    inspect_local_install,
    plan_install,
    render_install_plan,
)
from .common import LifecycleError, load_policy
from .incident import (
    build_transition_request,
    transition_incident,
    write_transition_outputs,
)
from .package import package_bundle, render_package_result
from .pr import validate_pr_event
from .release import build_release_request, prepare_release, validate_release_inputs
from .repository import (
    GhClient,
    apply_bootstrap,
    build_bootstrap_plan,
    discover_repository,
    inspect_remote_repository,
    render_bootstrap_plan,
    render_findings,
)
from .retrospective import (
    audit_records,
    build_retrospective_request,
    render_retrospective,
    write_audit_outputs,
    write_retrospective_outputs,
)


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


def _write_output(path: Path | None, content: str) -> None:
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content + "\n", encoding="utf-8")
    print(content)


def install_command(args: argparse.Namespace) -> int:
    plan, files = plan_install(
        args.root,
        args.manifest,
        args.target,
        repository=args.repository,
        default_branch=args.default_branch,
    )
    if not args.dry_run:
        apply_install(plan, files, confirmation=args.confirmation)
    _write_output(args.output, render_install_plan(plan, dry_run=args.dry_run))
    return 1 if plan.conflicts else 0


def doctor_command(args: argparse.Namespace) -> int:
    client = GhClient()
    snapshot = discover_repository(client, args.repository, evidence_pr=args.evidence_pr)
    policy = load_policy(args.root / ".github/lifecycle-policy.json")
    findings = (
        *inspect_local_install(
            args.root,
            args.manifest,
            repository=args.repository,
            expected_default_branch=snapshot.default_branch,
        ),
        *inspect_remote_repository(snapshot, policy),
    )
    _write_output(args.output, render_findings(findings))
    return 1 if findings else 0


def bootstrap_command(args: argparse.Namespace) -> int:
    client = GhClient()
    snapshot = discover_repository(client, args.repository, evidence_pr=args.evidence_pr)
    policy = load_policy(args.root / ".github/lifecycle-policy.json")
    local_findings = inspect_local_install(
        args.root,
        args.manifest,
        repository=args.repository,
        expected_default_branch=snapshot.default_branch,
    )
    if local_findings:
        raise LifecycleError(
            "bootstrap local installation is invalid: "
            + "; ".join(finding.detail for finding in local_findings)
        )
    plan = build_bootstrap_plan(snapshot, policy)
    plan_output = render_bootstrap_plan(plan, dry_run=args.dry_run)
    if args.dry_run or plan.blockers:
        _write_output(args.output, plan_output)
        return 1 if plan.blockers else 0
    apply_bootstrap(client, plan, confirmation=args.confirmation)
    verified = discover_repository(client, args.repository, evidence_pr=args.evidence_pr)
    findings = inspect_remote_repository(verified, policy)
    result = json.dumps(
        {
            "schema_version": 1,
            "mode": "apply",
            "repository": args.repository,
            "applied_actions": [
                {"kind": action.kind, "detail": action.detail} for action in plan.actions
            ],
            "verified": not findings,
            "findings": [
                {"scope": item.scope, "code": item.code, "detail": item.detail} for item in findings
            ],
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    _write_output(args.output, result)
    return 1 if findings else 0


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


def transition_incident_command(args: argparse.Namespace) -> int:
    policy = load_policy(args.policy)
    request = build_transition_request(
        issue_number=args.issue_number,
        target_status=args.target_status,
        decision=args.decision,
        evidence_links=args.evidence_links,
        actor=args.actor,
        occurred_at=args.occurred_at,
        security_or_privacy_risk=args.security_risk == "true",
        restricted_event_id=args.restricted_event_id,
        apply=args.apply == "true",
        confirmation=args.confirmation,
        operation_id=args.operation_id,
        policy=policy,
    )
    if args.validate_only:
        print("incident transition inputs are valid")
        return 0
    if args.issue is None or args.output_dir is None:
        raise LifecycleError("incident transition requires issue and output-dir")
    result = transition_incident(args.issue, request, policy)
    plan_path, comment_path = write_transition_outputs(result, args.output_dir, args.github_output)
    status = "no-op" if result.noop else "planned"
    lines = [
        "## Incident transition",
        "",
        f"Status: **{status}**",
        f"Issue: `#{result.issue_number}`",
        f"Transition: `{result.current_status} -> {result.target_status}`",
        f"Plan: `{plan_path}`",
    ]
    if not result.noop:
        lines.append(f"Comment: `{comment_path}`")
    if result.security_escalation:
        lines.extend(
            [
                "",
                "Restricted security/privacy response boundary is active; "
                "public details are omitted.",
            ]
        )
    write_summary(lines)
    print("\n".join(lines))
    return 0


def render_retrospective_command(args: argparse.Namespace) -> int:
    policy = load_policy(args.policy)
    request = build_retrospective_request(
        source=args.source,
        stability_confirmed=args.stability_confirmed == "true",
        timeline=args.timeline,
        visible_information=args.visible_information,
        contributing_factors=args.contributing_factors,
        guard_effectiveness=args.guard_effectiveness,
        uncertainties=args.uncertainties,
        action_links=args.action_links,
        actor=args.actor,
        occurred_at=args.occurred_at,
        apply=args.apply == "true",
        confirmation=args.confirmation,
    )
    if args.validate_only:
        print("retrospective inputs are valid")
        return 0
    if args.source_data is None or args.existing is None or args.output_dir is None:
        raise LifecycleError(
            "retrospective rendering requires source-data, existing, and output-dir"
        )
    result = render_retrospective(request, args.source_data, args.existing, policy)
    plan_path, body_path = write_retrospective_outputs(result, args.output_dir, args.github_output)
    status = "duplicate" if result.duplicate else "ready"
    lines = [
        "## Lifecycle retrospective",
        "",
        f"Status: **{status}**",
        f"Source: `{result.source_key}`",
        f"Due date: `{result.due_date.isoformat() if result.due_date else 'none'}`",
        f"Plan: `{plan_path}`",
        f"Body: `{body_path}`",
    ]
    if result.duplicate:
        lines.extend(["", f"Existing retrospective: {result.duplicate_url}"])
    write_summary(lines)
    print("\n".join(lines))
    return 0


def audit_records_command(args: argparse.Namespace) -> int:
    policy = load_policy(args.policy)
    try:
        as_of = date.fromisoformat(args.as_of)
    except ValueError as error:
        raise LifecycleError("audit as-of must be an ISO date") from error
    findings = audit_records(args.issues, args.releases, policy, as_of, args.comments)
    write_audit_outputs(findings, args.output)
    lines = [
        "## Lifecycle record audit",
        "",
        f"As of: `{as_of.isoformat()}`",
        f"Overdue findings: **{len(findings)}**",
    ]
    if findings:
        lines.extend(
            [
                "",
                "| Kind | Record | Due | Detail |",
                "| --- | --- | --- | --- |",
                *(
                    f"| {item.kind} | [{item.record}]({item.url}) | "
                    f"{item.due_date.isoformat() if item.due_date else 'n/a'} | {item.detail} |"
                    for item in findings
                ),
            ]
        )
    else:
        lines.extend(["", "No overdue retrospective or improvement-action records found."])
    write_summary(lines)
    print("\n".join(lines))
    return 1 if findings else 0


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

    install_parser = subparsers.add_parser(
        "install", help="plan or install the lifecycle automation in another repository"
    )
    install_parser.add_argument("--root", type=Path, default=Path.cwd())
    install_parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("automation/github-lifecycle-manifest.json"),
    )
    install_parser.add_argument("--target", type=Path, required=True)
    install_parser.add_argument("--repository", required=True)
    install_parser.add_argument("--default-branch", required=True)
    install_parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    install_parser.add_argument("--confirmation", default="")
    install_parser.add_argument("--output", type=Path)
    install_parser.set_defaults(handler=install_command)

    doctor_parser = subparsers.add_parser(
        "doctor", help="inspect a local lifecycle installation and GitHub repository"
    )
    doctor_parser.add_argument("--root", type=Path, default=Path.cwd())
    doctor_parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("automation/github-lifecycle-manifest.json"),
    )
    doctor_parser.add_argument("--repository", required=True)
    doctor_parser.add_argument("--evidence-pr", type=int)
    doctor_parser.add_argument("--output", type=Path)
    doctor_parser.set_defaults(handler=doctor_command)

    bootstrap_parser = subparsers.add_parser(
        "bootstrap", help="plan or apply lifecycle GitHub repository settings"
    )
    bootstrap_parser.add_argument("--root", type=Path, default=Path.cwd())
    bootstrap_parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("automation/github-lifecycle-manifest.json"),
    )
    bootstrap_parser.add_argument("--repository", required=True)
    bootstrap_parser.add_argument("--evidence-pr", type=int, required=True)
    bootstrap_parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    bootstrap_parser.add_argument("--confirmation", default="")
    bootstrap_parser.add_argument("--output", type=Path)
    bootstrap_parser.set_defaults(handler=bootstrap_command)

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

    incident_parser = subparsers.add_parser(
        "transition-incident", help="validate and render an incident state transition"
    )
    incident_parser.add_argument("--policy", type=Path, required=True)
    incident_parser.add_argument("--issue-number", required=True)
    incident_parser.add_argument("--target-status", required=True)
    incident_parser.add_argument("--decision", default="")
    incident_parser.add_argument("--evidence-links", default="")
    incident_parser.add_argument("--actor", required=True)
    incident_parser.add_argument("--occurred-at", required=True)
    incident_parser.add_argument("--security-risk", choices=("true", "false"), required=True)
    incident_parser.add_argument("--restricted-event-id", default="")
    incident_parser.add_argument("--apply", choices=("true", "false"), required=True)
    incident_parser.add_argument("--confirmation", default="")
    incident_parser.add_argument("--operation-id", required=True)
    incident_parser.add_argument("--validate-only", action="store_true")
    incident_parser.add_argument("--issue", type=Path)
    incident_parser.add_argument("--output-dir", type=Path)
    incident_parser.add_argument("--github-output", type=Path)
    incident_parser.set_defaults(handler=transition_incident_command)

    retrospective_parser = subparsers.add_parser(
        "render-retrospective", help="validate and render an incident or release retrospective"
    )
    retrospective_parser.add_argument("--policy", type=Path, required=True)
    retrospective_parser.add_argument("--source", required=True)
    retrospective_parser.add_argument(
        "--stability-confirmed", choices=("true", "false"), required=True
    )
    retrospective_parser.add_argument("--timeline", required=True)
    retrospective_parser.add_argument("--visible-information", required=True)
    retrospective_parser.add_argument("--contributing-factors", required=True)
    retrospective_parser.add_argument("--guard-effectiveness", required=True)
    retrospective_parser.add_argument("--uncertainties", required=True)
    retrospective_parser.add_argument("--action-links", required=True)
    retrospective_parser.add_argument("--actor", required=True)
    retrospective_parser.add_argument("--occurred-at", required=True)
    retrospective_parser.add_argument("--apply", choices=("true", "false"), required=True)
    retrospective_parser.add_argument("--confirmation", default="")
    retrospective_parser.add_argument("--validate-only", action="store_true")
    retrospective_parser.add_argument("--source-data", type=Path)
    retrospective_parser.add_argument("--existing", type=Path)
    retrospective_parser.add_argument("--output-dir", type=Path)
    retrospective_parser.add_argument("--github-output", type=Path)
    retrospective_parser.set_defaults(handler=render_retrospective_command)

    audit_parser = subparsers.add_parser(
        "audit-records", help="report overdue retrospective and improvement records"
    )
    audit_parser.add_argument("--policy", type=Path, required=True)
    audit_parser.add_argument("--issues", type=Path, required=True)
    audit_parser.add_argument("--releases", type=Path, required=True)
    audit_parser.add_argument("--comments", type=Path)
    audit_parser.add_argument("--as-of", required=True)
    audit_parser.add_argument("--output", type=Path, required=True)
    audit_parser.set_defaults(handler=audit_records_command)
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
