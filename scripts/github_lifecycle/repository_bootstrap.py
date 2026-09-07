from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass

from .common import LifecycleError, LifecyclePolicy
from .github import Gh
from .package import validate_profile
from .repository_ruleset import (
    MANAGED_RULE_TYPES,
    RULESET_NAME,
    build_ruleset_payload,
    canonical_ruleset,
    ruleset_applies_to_default,
)
from .repository_state import RepositorySnapshot

LABEL_PRESENTATION = {
    "type:incident": ("B60205", "Ordinary lifecycle incident"),
    "type:retrospective": ("5319E7", "Lifecycle retrospective"),
    "type:improvement-action": ("1D76DB", "Retrospective improvement action"),
    "severity:sev1": ("B60205", "Severity 1"),
    "severity:sev2": ("D93F0B", "Severity 2"),
    "severity:sev3": ("FBCA04", "Severity 3"),
    "severity:sev4": ("0E8A16", "Severity 4"),
    "status:investigating": ("D4C5F9", "Incident is being investigated"),
    "status:mitigating": ("FBCA04", "Incident mitigation is in progress"),
    "status:recovered": ("0E8A16", "Service has recovered"),
    "status:escalated": ("B60205", "Incident moved to a restricted process"),
    "status:closed": ("6E7781", "Incident record is closed"),
    "automation:smoke": ("C5DEF5", "Synthetic automation smoke record"),
}


@dataclass(frozen=True)
class BootstrapAction:
    kind: str
    detail: str


@dataclass(frozen=True)
class BootstrapPlan:
    repository: str
    evidence_pr: int
    actions: tuple[BootstrapAction, ...]
    blockers: tuple[str, ...]
    missing_labels: tuple[str, ...]
    update_actions_permissions: bool
    enable_private_vulnerability_reporting: bool
    update_delete_branch_on_merge: bool
    ruleset_method: str | None
    ruleset_id: int | None
    ruleset_payload: Mapping[str, object] | None


def build_bootstrap_plan(
    snapshot: RepositorySnapshot,
    policy: LifecyclePolicy,
    *,
    profile: str = "full",
) -> BootstrapPlan:
    profile = validate_profile(profile)
    manages_governance = profile in {"governance", "full"}
    manages_incident = profile in {"incident", "full"}
    blockers: list[str] = []
    evidence = snapshot.evidence
    if snapshot.viewer_permission != "ADMIN":
        blockers.append("bootstrap apply requires ADMIN repository permission")
    if policy.default_branch != snapshot.default_branch:
        blockers.append("policy default branch does not match GitHub")
    if manages_governance and evidence is None:
        blockers.append("bootstrap requires an evidence PR")
        evidence_pr = 0
    elif evidence is not None:
        evidence_pr = evidence.pull_request_number
        if manages_governance and evidence.state != "OPEN":
            blockers.append("bootstrap evidence PR must still be open")
        if manages_governance and evidence.base_branch != snapshot.default_branch:
            blockers.append("bootstrap evidence PR targets another branch")
    else:
        evidence_pr = 0

    existing: Mapping[str, object] | None = None
    payload: Mapping[str, object] | None = None
    if manages_governance:
        matching = [ruleset for ruleset in snapshot.rulesets if ruleset.get("name") == RULESET_NAME]
        if len(matching) > 1:
            blockers.append(f"multiple rulesets are named {RULESET_NAME!r}")
        existing = matching[0] if len(matching) == 1 else None
        for ruleset in snapshot.rulesets:
            if ruleset is existing or ruleset.get("enforcement") != "active":
                continue
            if not ruleset_applies_to_default(ruleset):
                continue
            raw_rules = ruleset.get("rules")
            if isinstance(raw_rules, list) and any(
                isinstance(rule, Mapping) and rule.get("type") in MANAGED_RULE_TYPES
                for rule in raw_rules
            ):
                blockers.append(
                    f"another active ruleset manages the default branch: {ruleset.get('name')}"
                )

        payload, payload_blockers = build_ruleset_payload(snapshot, policy, existing)
        blockers.extend(payload_blockers)
    missing_labels = tuple(sorted(set(policy.labels) - snapshot.labels)) if manages_incident else ()
    update_actions = snapshot.actions_default_permission != "read" or snapshot.actions_can_approve
    enable_pvr = manages_incident and not snapshot.private_vulnerability_reporting
    update_delete_branch = manages_governance and not snapshot.delete_branch_on_merge

    ruleset_method: str | None = None
    ruleset_id: int | None = None
    if payload is not None:
        if existing is None:
            ruleset_method = "create"
        else:
            raw_id = existing.get("id")
            if not isinstance(raw_id, int):
                blockers.append("existing managed ruleset has no integer id")
            else:
                ruleset_id = raw_id
                if canonical_ruleset(existing) != canonical_ruleset(payload):
                    ruleset_method = "update"

    actions: list[BootstrapAction] = []
    if update_actions:
        actions.append(BootstrapAction("actions-permissions", "set workflow token to read-only"))
    for label in missing_labels:
        actions.append(BootstrapAction("label", f"create {label}"))
    if enable_pvr:
        actions.append(
            BootstrapAction("private-vulnerability-reporting", "enable private reporting")
        )
    if ruleset_method is not None:
        actions.append(BootstrapAction("ruleset", f"{ruleset_method} {RULESET_NAME!r}"))
    if update_delete_branch:
        actions.append(BootstrapAction("repository", "enable delete_branch_on_merge"))
    return BootstrapPlan(
        repository=snapshot.repository,
        evidence_pr=evidence_pr,
        actions=tuple(actions),
        blockers=tuple(dict.fromkeys(blockers)),
        missing_labels=missing_labels,
        update_actions_permissions=update_actions,
        enable_private_vulnerability_reporting=enable_pvr,
        update_delete_branch_on_merge=update_delete_branch,
        ruleset_method=ruleset_method,
        ruleset_id=ruleset_id,
        ruleset_payload=payload,
    )


def apply_bootstrap(client: Gh, plan: BootstrapPlan, *, confirmation: str) -> None:
    expected = f"bootstrap:{plan.repository}"
    if confirmation != expected:
        raise LifecycleError(f"bootstrap confirmation must exactly match {expected}")
    if plan.blockers:
        raise LifecycleError("bootstrap is blocked: " + "; ".join(plan.blockers))
    repository = plan.repository
    if plan.update_actions_permissions:
        client.execute(
            [
                "api",
                "--method",
                "PUT",
                f"repos/{repository}/actions/permissions/workflow",
                "--input",
                "-",
            ],
            json.dumps(
                {
                    "default_workflow_permissions": "read",
                    "can_approve_pull_request_reviews": False,
                }
            ),
        )
    for label in plan.missing_labels:
        color, description = LABEL_PRESENTATION.get(label, ("D4C5F9", "Lifecycle label"))
        client.execute(
            [
                "label",
                "create",
                label,
                "--repo",
                repository,
                "--color",
                color,
                "--description",
                description,
            ]
        )
    if plan.enable_private_vulnerability_reporting:
        client.execute(
            ["api", "--method", "PUT", f"repos/{repository}/private-vulnerability-reporting"]
        )
    if plan.ruleset_method is not None and plan.ruleset_payload is not None:
        if plan.ruleset_method == "create":
            endpoint = f"repos/{repository}/rulesets"
            method = "POST"
        else:
            if plan.ruleset_id is None:
                raise LifecycleError("ruleset update requires an existing ruleset id")
            endpoint = f"repos/{repository}/rulesets/{plan.ruleset_id}"
            method = "PUT"
        client.execute(
            ["api", "--method", method, endpoint, "--input", "-"],
            json.dumps(plan.ruleset_payload),
        )
    if plan.update_delete_branch_on_merge:
        client.execute(
            ["api", "--method", "PATCH", f"repos/{repository}", "--input", "-"],
            json.dumps({"delete_branch_on_merge": True}),
        )


def render_bootstrap_plan(plan: BootstrapPlan, *, dry_run: bool, profile: str = "full") -> str:
    return json.dumps(
        {
            "schema_version": 2,
            "mode": "dry-run" if dry_run else "apply",
            "repository": plan.repository,
            "profile": validate_profile(profile),
            "evidence_pr": plan.evidence_pr,
            "healthy": not plan.blockers,
            "blockers": list(plan.blockers),
            "actions": [{"kind": action.kind, "detail": action.detail} for action in plan.actions],
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
