from __future__ import annotations

import json
import shutil
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol

from .adoption import DoctorFinding, validate_repository_name
from .common import LifecycleError, LifecyclePolicy
from .package import validate_profile

RULESET_NAME = "main required checks"
MANAGED_RULE_TYPES = {
    "deletion",
    "non_fast_forward",
    "pull_request",
    "required_status_checks",
}
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


class Gh(Protocol):
    def json(self, arguments: Sequence[str]) -> object: ...

    def execute(self, arguments: Sequence[str], input_text: str | None = None) -> str: ...


class GhClient:
    def __init__(self, *, timeout_seconds: int = 30) -> None:
        if shutil.which("gh") is None:
            raise LifecycleError("GitHub CLI (gh) is required")
        self.timeout_seconds = timeout_seconds

    def execute(self, arguments: Sequence[str], input_text: str | None = None) -> str:
        try:
            result = subprocess.run(
                ["gh", *arguments],
                input=input_text,
                text=True,
                capture_output=True,
                check=False,
                timeout=self.timeout_seconds,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise LifecycleError(f"cannot execute gh: {error}") from error
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or "unknown gh error"
            raise LifecycleError(f"gh command failed: {detail}")
        return result.stdout

    def json(self, arguments: Sequence[str]) -> object:
        output = self.execute(arguments)
        try:
            return json.loads(output)
        except json.JSONDecodeError as error:
            raise LifecycleError(f"gh returned invalid JSON: {error}") from error


@dataclass(frozen=True)
class CheckEvidence:
    pull_request_number: int
    pull_request_url: str
    state: str
    base_branch: str
    head_sha: str
    successful_integrations: Mapping[str, frozenset[int]]


@dataclass(frozen=True)
class RepositorySnapshot:
    repository: str
    default_branch: str
    viewer_permission: str
    delete_branch_on_merge: bool
    actions_default_permission: str
    actions_can_approve: bool
    private_vulnerability_reporting: bool
    labels: frozenset[str]
    rulesets: tuple[Mapping[str, object], ...]
    effective_rules: tuple[Mapping[str, object], ...]
    branch_protected: bool
    evidence: CheckEvidence | None


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


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise LifecycleError(f"{label} must be a JSON object")
    return value


def _array(value: object, label: str) -> Sequence[object]:
    if not isinstance(value, list):
        raise LifecycleError(f"{label} must be a JSON array")
    if value and all(isinstance(page, list) for page in value):
        return tuple(item for page in value for item in page)
    return value


def _required_check_names(policy: LifecyclePolicy) -> tuple[str, ...]:
    return tuple(dict.fromkeys((*policy.release_required_checks, policy.pr_check_name)))


def _ruleset_applies_to_default(ruleset: Mapping[str, object]) -> bool:
    conditions = ruleset.get("conditions")
    if not isinstance(conditions, Mapping):
        return False
    ref_name = conditions.get("ref_name")
    return (
        isinstance(ref_name, Mapping)
        and ref_name.get("include") == ["~DEFAULT_BRANCH"]
        and ref_name.get("exclude") == []
    )


def _load_rulesets(client: Gh, repository: str) -> tuple[Mapping[str, object], ...]:
    summaries = _array(client.json(["api", f"repos/{repository}/rulesets"]), "repository rulesets")
    details: list[Mapping[str, object]] = []
    for summary in summaries:
        summary_mapping = _mapping(summary, "ruleset summary")
        ruleset_id = summary_mapping.get("id")
        if not isinstance(ruleset_id, int):
            raise LifecycleError("ruleset summary must contain an integer id")
        details.append(
            _mapping(
                client.json(["api", f"repos/{repository}/rulesets/{ruleset_id}"]),
                "ruleset detail",
            )
        )
    return tuple(details)


def _load_evidence(
    client: Gh,
    repository: str,
    pull_request_number: int,
) -> CheckEvidence:
    pull_request = _mapping(
        client.json(
            [
                "pr",
                "view",
                str(pull_request_number),
                "--repo",
                repository,
                "--json",
                "number,url,state,baseRefName,headRefOid",
            ]
        ),
        "evidence pull request",
    )
    head_sha = pull_request.get("headRefOid")
    if not isinstance(head_sha, str) or len(head_sha) != 40:
        raise LifecycleError("evidence PR must contain a full head SHA")
    raw_pages = client.json(
        [
            "api",
            "--paginate",
            "--slurp",
            f"repos/{repository}/commits/{head_sha}/check-runs?per_page=100",
        ]
    )
    pages = _array(raw_pages, "check-run pages")
    integrations: dict[str, set[int]] = {}
    for raw_page in pages:
        page = _mapping(raw_page, "check-run page")
        runs = page.get("check_runs")
        if not isinstance(runs, list):
            raise LifecycleError("check-run page must contain a check_runs array")
        for raw_run in runs:
            run = _mapping(raw_run, "check run")
            if run.get("status") != "completed" or run.get("conclusion") != "success":
                continue
            name = run.get("name")
            app = run.get("app")
            integration_id = app.get("id") if isinstance(app, Mapping) else None
            if isinstance(name, str) and isinstance(integration_id, int):
                integrations.setdefault(name, set()).add(integration_id)
    return CheckEvidence(
        pull_request_number=pull_request_number,
        pull_request_url=str(pull_request.get("url") or ""),
        state=str(pull_request.get("state") or ""),
        base_branch=str(pull_request.get("baseRefName") or ""),
        head_sha=head_sha,
        successful_integrations={name: frozenset(values) for name, values in integrations.items()},
    )


def discover_repository(
    client: Gh,
    repository: str,
    *,
    evidence_pr: int | None = None,
) -> RepositorySnapshot:
    repository = validate_repository_name(repository)
    metadata = _mapping(
        client.json(
            [
                "repo",
                "view",
                repository,
                "--json",
                "nameWithOwner,defaultBranchRef,viewerPermission,deleteBranchOnMerge",
            ]
        ),
        "repository metadata",
    )
    if metadata.get("nameWithOwner") != repository:
        raise LifecycleError("gh repository response does not match the requested repository")
    default_branch_ref = metadata.get("defaultBranchRef")
    default_branch = (
        default_branch_ref.get("name") if isinstance(default_branch_ref, Mapping) else None
    )
    if not isinstance(default_branch, str) or not default_branch:
        raise LifecycleError("repository must have a default branch")

    actions = _mapping(
        client.json(["api", f"repos/{repository}/actions/permissions/workflow"]),
        "Actions permissions",
    )
    pvr = _mapping(
        client.json(["api", f"repos/{repository}/private-vulnerability-reporting"]),
        "private vulnerability reporting",
    )
    raw_labels = _array(
        client.json(
            [
                "api",
                "--paginate",
                "--slurp",
                f"repos/{repository}/labels?per_page=100",
            ]
        ),
        "repository labels",
    )
    labels = frozenset(
        str(label["name"])
        for label in raw_labels
        if isinstance(label, Mapping) and isinstance(label.get("name"), str)
    )
    rulesets = _load_rulesets(client, repository)
    raw_effective = _array(
        client.json(["api", f"repos/{repository}/rules/branches/{default_branch}"]),
        "effective branch rules",
    )
    effective_rules = tuple(_mapping(rule, "effective branch rule") for rule in raw_effective)
    branch = _mapping(
        client.json(["api", f"repos/{repository}/branches/{default_branch}"]),
        "default branch",
    )
    evidence = _load_evidence(client, repository, evidence_pr) if evidence_pr is not None else None
    return RepositorySnapshot(
        repository=repository,
        default_branch=default_branch,
        viewer_permission=str(metadata.get("viewerPermission") or ""),
        delete_branch_on_merge=metadata.get("deleteBranchOnMerge") is True,
        actions_default_permission=str(actions.get("default_workflow_permissions") or ""),
        actions_can_approve=actions.get("can_approve_pull_request_reviews") is True,
        private_vulnerability_reporting=pvr.get("enabled") is True,
        labels=labels,
        rulesets=rulesets,
        effective_rules=effective_rules,
        branch_protected=branch.get("protected") is True,
        evidence=evidence,
    )


def _effective_rule(snapshot: RepositorySnapshot, rule_type: str) -> Mapping[str, object] | None:
    matches = [rule for rule in snapshot.effective_rules if rule.get("type") == rule_type]
    return matches[0] if len(matches) == 1 else None


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

    status_rule = _effective_rule(snapshot, "required_status_checks")
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
        missing_checks = sorted(set(_required_check_names(policy)) - contexts)
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
        if _effective_rule(snapshot, rule_type) is None:
            findings.append(DoctorFinding("remote", code, detail))

    pull_request_rule = _effective_rule(snapshot, "pull_request")
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
        and _ruleset_applies_to_default(ruleset)
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
        for name in _required_check_names(policy):
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


def _clean_rule(rule: Mapping[str, object]) -> dict[str, object]:
    cleaned: dict[str, object] = {"type": str(rule.get("type") or "")}
    parameters = rule.get("parameters")
    if isinstance(parameters, Mapping):
        cleaned["parameters"] = dict(parameters)
    return cleaned


def _canonical_ruleset(value: Mapping[str, object]) -> Mapping[str, object]:
    canonical_rules: list[dict[str, object]] = []
    raw_rules = value.get("rules")
    if isinstance(raw_rules, list):
        for raw_rule in raw_rules:
            if not isinstance(raw_rule, Mapping):
                continue
            rule = _clean_rule(raw_rule)
            parameters = rule.get("parameters")
            if rule.get("type") == "required_status_checks" and isinstance(parameters, dict):
                checks = parameters.get("required_status_checks")
                if isinstance(checks, list):
                    parameters["required_status_checks"] = sorted(
                        checks,
                        key=lambda check: (
                            str(check.get("context")) if isinstance(check, Mapping) else ""
                        ),
                    )
            canonical_rules.append(rule)
    canonical_rules.sort(key=lambda rule: str(rule.get("type")))
    return {
        "name": value.get("name"),
        "target": value.get("target"),
        "enforcement": value.get("enforcement"),
        "bypass_actors": value.get("bypass_actors") or [],
        "conditions": value.get("conditions"),
        "rules": canonical_rules,
    }


def _build_ruleset_payload(
    snapshot: RepositorySnapshot,
    policy: LifecyclePolicy,
    existing: Mapping[str, object] | None,
) -> tuple[Mapping[str, object] | None, tuple[str, ...]]:
    blockers: list[str] = []
    evidence = snapshot.evidence
    if evidence is None:
        return None, ("bootstrap requires an evidence PR",)
    required_checks: list[dict[str, object]] = []
    for name in _required_check_names(policy):
        integrations = evidence.successful_integrations.get(name, frozenset())
        if len(integrations) != 1:
            blockers.append(f"check {name!r} must have exactly one successful GitHub App identity")
            continue
        required_checks.append({"context": name, "integration_id": next(iter(integrations))})
    if blockers:
        return None, tuple(blockers)

    existing_rules: dict[str, Mapping[str, object]] = {}
    unknown_rules: list[dict[str, object]] = []
    if existing is not None:
        if existing.get("bypass_actors") not in ([], None):
            blockers.append("existing managed ruleset contains bypass actors")
        if not _ruleset_applies_to_default(existing):
            blockers.append("existing managed ruleset does not target only the default branch")
        raw_rules = existing.get("rules")
        if not isinstance(raw_rules, list):
            blockers.append("existing managed ruleset has an invalid rules array")
        else:
            for raw_rule in raw_rules:
                rule = _mapping(raw_rule, "existing ruleset rule")
                rule_type = str(rule.get("type") or "")
                if rule_type in MANAGED_RULE_TYPES:
                    if rule_type in existing_rules:
                        blockers.append(f"existing ruleset repeats rule type {rule_type}")
                    existing_rules[rule_type] = rule
                else:
                    unknown_rules.append(_clean_rule(rule))
    if blockers:
        return None, tuple(blockers)

    existing_status = existing_rules.get("required_status_checks")
    status_parameters = (
        dict(existing_status.get("parameters"))
        if existing_status is not None and isinstance(existing_status.get("parameters"), Mapping)
        else {}
    )
    raw_existing_checks = status_parameters.get("required_status_checks", [])
    combined_checks: dict[str, dict[str, object]] = {}
    if isinstance(raw_existing_checks, list):
        for raw_check in raw_existing_checks:
            if not isinstance(raw_check, Mapping) or not isinstance(raw_check.get("context"), str):
                blockers.append("existing required check entry is invalid")
                continue
            context = str(raw_check["context"])
            combined_checks[context] = dict(raw_check)
    else:
        blockers.append("existing required checks must be an array")
    for check in required_checks:
        context = str(check["context"])
        existing_check = combined_checks.get(context)
        if existing_check is not None and existing_check.get("integration_id") != check.get(
            "integration_id"
        ):
            blockers.append(f"existing check {context!r} uses another GitHub App identity")
        combined_checks[context] = check
    if blockers:
        return None, tuple(blockers)
    status_parameters.update(
        {
            "required_status_checks": [combined_checks[name] for name in sorted(combined_checks)],
            "strict_required_status_checks_policy": True,
            "do_not_enforce_on_create": status_parameters.get("do_not_enforce_on_create", True),
        }
    )

    existing_pr = existing_rules.get("pull_request")
    pr_parameters = (
        dict(existing_pr.get("parameters"))
        if existing_pr is not None and isinstance(existing_pr.get("parameters"), Mapping)
        else {}
    )
    allowed_methods = pr_parameters.get("allowed_merge_methods")
    if isinstance(allowed_methods, list) and "squash" not in allowed_methods:
        return None, ("existing pull-request rule does not permit squash merge",)
    pr_parameters.update(
        {
            "allowed_merge_methods": ["squash"],
            "dismiss_stale_reviews_on_push": pr_parameters.get(
                "dismiss_stale_reviews_on_push", False
            ),
            "require_code_owner_review": pr_parameters.get("require_code_owner_review", False),
            "require_last_push_approval": pr_parameters.get("require_last_push_approval", False),
            "required_approving_review_count": pr_parameters.get(
                "required_approving_review_count", 0
            ),
            "required_review_thread_resolution": True,
        }
    )

    rules = [
        {
            "type": "required_status_checks",
            "parameters": status_parameters,
        },
        {"type": "deletion"},
        {"type": "non_fast_forward"},
        {"type": "pull_request", "parameters": pr_parameters},
        *unknown_rules,
    ]
    return (
        {
            "name": RULESET_NAME,
            "target": "branch",
            "enforcement": "active",
            "bypass_actors": [],
            "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
            "rules": rules,
        },
        (),
    )


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
            if not _ruleset_applies_to_default(ruleset):
                continue
            raw_rules = ruleset.get("rules")
            if isinstance(raw_rules, list) and any(
                isinstance(rule, Mapping) and rule.get("type") in MANAGED_RULE_TYPES
                for rule in raw_rules
            ):
                blockers.append(
                    f"another active ruleset manages the default branch: {ruleset.get('name')}"
                )

        payload, payload_blockers = _build_ruleset_payload(snapshot, policy, existing)
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
                if _canonical_ruleset(existing) != _canonical_ruleset(payload):
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
            [
                "api",
                "--method",
                "PUT",
                f"repos/{repository}/private-vulnerability-reporting",
            ]
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
