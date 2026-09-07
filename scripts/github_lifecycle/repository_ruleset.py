from __future__ import annotations

from collections.abc import Mapping

from .common import LifecyclePolicy
from .github import json_mapping
from .repository_state import RepositorySnapshot

RULESET_NAME = "main required checks"
MANAGED_RULE_TYPES = {
    "deletion",
    "non_fast_forward",
    "pull_request",
    "required_status_checks",
}


def required_check_names(policy: LifecyclePolicy) -> tuple[str, ...]:
    return tuple(dict.fromkeys((*policy.release_required_checks, policy.pr_check_name)))


def ruleset_applies_to_default(ruleset: Mapping[str, object]) -> bool:
    conditions = ruleset.get("conditions")
    if not isinstance(conditions, Mapping):
        return False
    ref_name = conditions.get("ref_name")
    return (
        isinstance(ref_name, Mapping)
        and ref_name.get("include") == ["~DEFAULT_BRANCH"]
        and ref_name.get("exclude") == []
    )


def effective_rule(snapshot: RepositorySnapshot, rule_type: str) -> Mapping[str, object] | None:
    matches = [rule for rule in snapshot.effective_rules if rule.get("type") == rule_type]
    return matches[0] if len(matches) == 1 else None


def _clean_rule(rule: Mapping[str, object]) -> dict[str, object]:
    cleaned: dict[str, object] = {"type": str(rule.get("type") or "")}
    parameters = rule.get("parameters")
    if isinstance(parameters, Mapping):
        cleaned["parameters"] = dict(parameters)
    return cleaned


def canonical_ruleset(value: Mapping[str, object]) -> Mapping[str, object]:
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


def build_ruleset_payload(
    snapshot: RepositorySnapshot,
    policy: LifecyclePolicy,
    existing: Mapping[str, object] | None,
) -> tuple[Mapping[str, object] | None, tuple[str, ...]]:
    blockers: list[str] = []
    evidence = snapshot.evidence
    if evidence is None:
        return None, ("bootstrap requires an evidence PR",)
    required_checks: list[dict[str, object]] = []
    for name in required_check_names(policy):
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
        if not ruleset_applies_to_default(existing):
            blockers.append("existing managed ruleset does not target only the default branch")
        raw_rules = existing.get("rules")
        if not isinstance(raw_rules, list):
            blockers.append("existing managed ruleset has an invalid rules array")
        else:
            for raw_rule in raw_rules:
                rule = json_mapping(raw_rule, "existing ruleset rule")
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
        {"type": "required_status_checks", "parameters": status_parameters},
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
