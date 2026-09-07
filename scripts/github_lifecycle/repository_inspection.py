from __future__ import annotations

import json
from collections.abc import Mapping, Sequence

from .adoption import DoctorFinding
from .common import LifecyclePolicy
from .package import validate_profile
from .repository_ruleset import (
    RULESET_NAME,
    effective_rule,
    required_check_names,
    ruleset_applies_to_default,
)
from .repository_state import RepositorySnapshot


def inspect_remote_repository(
    snapshot: RepositorySnapshot,
    policy: LifecyclePolicy,
    *,
    profile: str = "full",
) -> tuple[DoctorFinding, ...]:
    profile = validate_profile(profile)
    manages_governance = profile in {"governance", "full"}
    manages_incident = profile in {"incident", "full"}
    findings: list[DoctorFinding] = []
    if snapshot.viewer_permission not in {"ADMIN", "MAINTAIN"}:
        findings.append(
            DoctorFinding(
                "remote", "insufficient-permission", "repository requires ADMIN or MAINTAIN access"
            )
        )
    if policy.default_branch != snapshot.default_branch:
        findings.append(
            DoctorFinding(
                "remote",
                "default-branch-mismatch",
                f"policy uses {policy.default_branch!r}; GitHub uses {snapshot.default_branch!r}",
            )
        )
    if snapshot.actions_default_permission != "read" or snapshot.actions_can_approve:
        findings.append(
            DoctorFinding(
                "remote",
                "actions-permissions",
                "Actions defaults must be read-only and unable to approve pull requests",
            )
        )
    if manages_governance and not snapshot.delete_branch_on_merge:
        findings.append(
            DoctorFinding(
                "remote", "delete-branch-disabled", "delete_branch_on_merge must be enabled"
            )
        )
    if manages_incident and not snapshot.private_vulnerability_reporting:
        findings.append(
            DoctorFinding(
                "remote", "pvr-disabled", "Private Vulnerability Reporting must be enabled"
            )
        )
    missing_labels = sorted(set(policy.labels) - snapshot.labels) if manages_incident else []
    if missing_labels:
        findings.append(
            DoctorFinding(
                "remote",
                "labels-missing",
                "missing lifecycle labels: " + ", ".join(missing_labels),
            )
        )

    if not manages_governance:
        return tuple(findings)

    status_rule = effective_rule(snapshot, "required_status_checks")
    if status_rule is None:
        findings.append(
            DoctorFinding("remote", "required-checks-missing", "required checks are not active")
        )
    else:
        parameters = status_rule.get("parameters")
        parameters = parameters if isinstance(parameters, Mapping) else {}
        checks = parameters.get("required_status_checks")
        checks = checks if isinstance(checks, list) else []
        contexts = {
            str(check.get("context"))
            for check in checks
            if isinstance(check, Mapping) and isinstance(check.get("context"), str)
        }
        missing_checks = sorted(set(required_check_names(policy)) - contexts)
        if missing_checks:
            findings.append(
                DoctorFinding(
                    "remote",
                    "required-checks-missing",
                    "missing required checks: " + ", ".join(missing_checks),
                )
            )
        if parameters.get("strict_required_status_checks_policy") is not True:
            findings.append(
                DoctorFinding("remote", "strict-disabled", "required checks must be strict")
            )

    for rule_type, code, detail in (
        ("deletion", "deletion-rule-missing", "default branch deletion must be blocked"),
        (
            "non_fast_forward",
            "force-push-rule-missing",
            "default branch force pushes must be blocked",
        ),
    ):
        if effective_rule(snapshot, rule_type) is None:
            findings.append(DoctorFinding("remote", code, detail))

    pull_request_rule = effective_rule(snapshot, "pull_request")
    if pull_request_rule is None:
        findings.append(
            DoctorFinding("remote", "pull-request-rule-missing", "default branch must require PRs")
        )
    else:
        parameters = pull_request_rule.get("parameters")
        parameters = parameters if isinstance(parameters, Mapping) else {}
        if parameters.get("required_review_thread_resolution") is not True:
            findings.append(
                DoctorFinding(
                    "remote", "review-resolution-disabled", "PR conversations must be resolved"
                )
            )
        if parameters.get("allowed_merge_methods") != ["squash"]:
            findings.append(
                DoctorFinding(
                    "remote", "merge-methods-mismatch", "only squash merge must be allowed"
                )
            )

    matching_rulesets = [
        ruleset
        for ruleset in snapshot.rulesets
        if ruleset.get("name") == RULESET_NAME
        and ruleset.get("enforcement") == "active"
        and ruleset_applies_to_default(ruleset)
    ]
    if len(matching_rulesets) != 1:
        findings.append(
            DoctorFinding(
                "remote",
                "managed-ruleset-missing",
                f"expected one active {RULESET_NAME!r} ruleset",
            )
        )
    elif matching_rulesets[0].get("bypass_actors") not in ([], None):
        findings.append(
            DoctorFinding("remote", "ruleset-bypass", "managed ruleset must not allow bypass")
        )
    if not snapshot.branch_protected:
        findings.append(
            DoctorFinding("remote", "branch-not-protected", "default branch is not protected")
        )

    evidence = snapshot.evidence
    if evidence is not None:
        if evidence.base_branch != snapshot.default_branch:
            findings.append(
                DoctorFinding(
                    "evidence", "base-branch-mismatch", "evidence PR targets another branch"
                )
            )
        if evidence.state not in {"OPEN", "MERGED"}:
            findings.append(
                DoctorFinding("evidence", "pr-state-invalid", "evidence PR must be open or merged")
            )
        for name in required_check_names(policy):
            integrations = evidence.successful_integrations.get(name, frozenset())
            if len(integrations) != 1:
                findings.append(
                    DoctorFinding(
                        "evidence",
                        "check-evidence-invalid",
                        f"check {name!r} must have one successful GitHub App identity",
                    )
                )
    return tuple(findings)


def render_findings(findings: Sequence[DoctorFinding], *, profile: str = "full") -> str:
    return json.dumps(
        {
            "schema_version": 2,
            "profile": validate_profile(profile),
            "healthy": not findings,
            "findings": [
                {"scope": item.scope, "code": item.code, "detail": item.detail} for item in findings
            ],
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
