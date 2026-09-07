from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .adoption import validate_repository_name
from .common import LifecycleError
from .github import Gh, json_array, json_mapping


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


def _load_rulesets(client: Gh, repository: str) -> tuple[Mapping[str, object], ...]:
    summaries = json_array(
        client.json(["api", f"repos/{repository}/rulesets"]), "repository rulesets"
    )
    details: list[Mapping[str, object]] = []
    for summary in summaries:
        summary_mapping = json_mapping(summary, "ruleset summary")
        ruleset_id = summary_mapping.get("id")
        if not isinstance(ruleset_id, int):
            raise LifecycleError("ruleset summary must contain an integer id")
        details.append(
            json_mapping(
                client.json(["api", f"repos/{repository}/rulesets/{ruleset_id}"]),
                "ruleset detail",
            )
        )
    return tuple(details)


def _load_evidence(client: Gh, repository: str, pull_request_number: int) -> CheckEvidence:
    pull_request = json_mapping(
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
    pages = json_array(
        client.json(
            [
                "api",
                "--paginate",
                "--slurp",
                f"repos/{repository}/commits/{head_sha}/check-runs?per_page=100",
            ]
        ),
        "check-run pages",
    )
    integrations: dict[str, set[int]] = {}
    for raw_page in pages:
        page = json_mapping(raw_page, "check-run page")
        runs = page.get("check_runs")
        if not isinstance(runs, list):
            raise LifecycleError("check-run page must contain a check_runs array")
        for raw_run in runs:
            run = json_mapping(raw_run, "check run")
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
    metadata = json_mapping(
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

    actions = json_mapping(
        client.json(["api", f"repos/{repository}/actions/permissions/workflow"]),
        "Actions permissions",
    )
    pvr = json_mapping(
        client.json(["api", f"repos/{repository}/private-vulnerability-reporting"]),
        "private vulnerability reporting",
    )
    raw_labels = json_array(
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
    raw_effective = json_array(
        client.json(["api", f"repos/{repository}/rules/branches/{default_branch}"]),
        "effective branch rules",
    )
    effective_rules = tuple(json_mapping(rule, "effective branch rule") for rule in raw_effective)
    branch = json_mapping(
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
