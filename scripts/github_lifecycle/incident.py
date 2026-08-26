from __future__ import annotations

import html
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from .common import LifecycleError, LifecyclePolicy, load_json_mapping, require_string

ISSUE_NUMBER_PATTERN = re.compile(r"^[1-9]\d*$")
RESTRICTED_EVENT_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,127}$")
SECTION_PATTERN = re.compile(r"^###\s+(?P<name>[^\n]+?)\s*$", re.MULTILINE)
ALLOWED_TRANSITIONS = {
    "investigating": {"mitigating", "recovered", "escalated"},
    "mitigating": {"recovered", "escalated"},
    "recovered": {"closed"},
    "closed": {"investigating"},
}


@dataclass(frozen=True)
class IncidentTransitionRequest:
    issue_number: int
    target_status: str
    decision: str
    evidence_links: tuple[str, ...]
    actor: str
    occurred_at: str
    security_or_privacy_risk: bool
    restricted_event_id: str
    apply: bool
    confirmation: str


@dataclass(frozen=True)
class IncidentTransition:
    issue_number: int
    current_status: str
    target_status: str
    current_label: str
    target_label: str
    severity_label: str
    issue_action: str
    comment: str
    noop: bool
    security_escalation: bool


def _parse_issue_number(value: object) -> int:
    text = require_string(value, "issue_number")
    if not ISSUE_NUMBER_PATTERN.fullmatch(text):
        raise LifecycleError("issue_number must be a positive integer")
    return int(text)


def _parse_timestamp(value: object) -> str:
    text = require_string(value, "occurred_at")
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as error:
        raise LifecycleError("occurred_at must be an ISO-8601 timestamp with timezone") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise LifecycleError("occurred_at must include a timezone")
    return text


def _parse_evidence_links(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, str):
        raise LifecycleError("evidence_links must be text")
    links = tuple(line.strip() for line in value.splitlines() if line.strip())
    for link in links:
        parsed = urlparse(link)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username is not None:
            raise LifecycleError("every evidence link must be an HTTPS URL without credentials")
    return links


def build_transition_request(
    *,
    issue_number: object,
    target_status: object,
    decision: object,
    evidence_links: object,
    actor: object,
    occurred_at: object,
    security_or_privacy_risk: bool,
    restricted_event_id: object,
    apply: bool,
    confirmation: object,
    policy: LifecyclePolicy,
) -> IncidentTransitionRequest:
    number = _parse_issue_number(issue_number)
    target = require_string(target_status, "target_status")
    status_values = {
        label.removeprefix("status:") for label in policy.labels if label.startswith("status:")
    }
    if target not in status_values:
        raise LifecycleError(f"target_status must be one of: {', '.join(sorted(status_values))}")
    timestamp = _parse_timestamp(occurred_at)
    actor_text = require_string(actor, "actor")
    decision_text = decision.strip() if isinstance(decision, str) else ""
    restricted_id = restricted_event_id.strip() if isinstance(restricted_event_id, str) else ""
    links = () if security_or_privacy_risk else _parse_evidence_links(evidence_links)

    if security_or_privacy_risk:
        if target != "escalated":
            raise LifecycleError("security/privacy escalation must target escalated")
        if not RESTRICTED_EVENT_ID_PATTERN.fullmatch(restricted_id):
            raise LifecycleError("security/privacy escalation requires a safe restricted event ID")
        decision_text = ""
    else:
        if not decision_text:
            raise LifecycleError("ordinary incident transition requires a decision")
        if not links:
            raise LifecycleError("ordinary incident transition requires at least one evidence link")
    confirmation_text = confirmation if isinstance(confirmation, str) else ""
    if apply and confirmation_text != f"incident-{number}":
        raise LifecycleError(
            f"incident confirmation must exactly match incident-{number} for an applied transition"
        )
    return IncidentTransitionRequest(
        issue_number=number,
        target_status=target,
        decision=decision_text,
        evidence_links=links,
        actor=actor_text,
        occurred_at=timestamp,
        security_or_privacy_risk=security_or_privacy_risk,
        restricted_event_id=restricted_id,
        apply=apply,
        confirmation=confirmation_text,
    )


def _label_names(issue: Mapping[str, object]) -> set[str]:
    raw_labels = issue.get("labels")
    if not isinstance(raw_labels, list):
        raise LifecycleError("incident Issue must contain a labels array")
    names: set[str] = set()
    for raw_label in raw_labels:
        if isinstance(raw_label, Mapping) and isinstance(raw_label.get("name"), str):
            names.add(str(raw_label["name"]))
        elif isinstance(raw_label, str):
            names.add(raw_label)
    return names


def _parse_form_sections(body: str) -> dict[str, str]:
    matches = list(SECTION_PATTERN.finditer(body))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections[match.group("name").strip()] = body[start:end].strip()
    return sections


def _severity_from_issue(issue: Mapping[str, object], policy: LifecyclePolicy) -> str:
    labels = _label_names(issue)
    severity_labels = sorted(label for label in labels if label.startswith("severity:"))
    if len(severity_labels) > 1:
        raise LifecycleError("incident Issue must not contain multiple severity labels")
    body = issue.get("body")
    if not isinstance(body, str):
        raise LifecycleError("incident Issue body must be text")
    severity_value = _parse_form_sections(body).get("Severity", "").strip().lower()
    if severity_value not in policy.incident_severities:
        raise LifecycleError("incident Issue body must declare Severity as SEV1 through SEV4")
    expected = f"severity:{severity_value}"
    if severity_labels and severity_labels[0] != expected:
        raise LifecycleError("incident severity label conflicts with the Issue form value")
    return expected


def _escape_markdown(value: str) -> str:
    return html.escape(" ".join(value.split()), quote=False)


def transition_incident(
    issue_path: Path,
    request: IncidentTransitionRequest,
    policy: LifecyclePolicy,
) -> IncidentTransition:
    issue = load_json_mapping(issue_path, "incident Issue")
    issue_number = issue.get("number")
    if issue_number != request.issue_number:
        raise LifecycleError("incident Issue number does not match the requested issue_number")
    labels = _label_names(issue)
    if "type:incident" not in labels:
        raise LifecycleError("target Issue must have the type:incident label")
    status_labels = sorted(label for label in labels if label.startswith("status:"))
    if len(status_labels) != 1:
        raise LifecycleError("incident Issue must contain exactly one current status label")
    current_label = status_labels[0]
    current = current_label.removeprefix("status:")
    target = request.target_status
    state = issue.get("state")
    if state not in {"OPEN", "CLOSED"}:
        raise LifecycleError("incident Issue state must be OPEN or CLOSED")
    if (current == "closed") != (state == "CLOSED"):
        raise LifecycleError("incident Issue state conflicts with its current status label")
    severity_label = _severity_from_issue(issue, policy)

    if current == target:
        return IncidentTransition(
            issue_number=request.issue_number,
            current_status=current,
            target_status=target,
            current_label=current_label,
            target_label=current_label,
            severity_label=severity_label,
            issue_action="none",
            comment="",
            noop=True,
            security_escalation=request.security_or_privacy_risk,
        )
    if target not in ALLOWED_TRANSITIONS.get(current, set()):
        raise LifecycleError(f"illegal incident transition: {current} -> {target}")
    if request.security_or_privacy_risk and current not in {"investigating", "mitigating"}:
        raise LifecycleError("security/privacy escalation is not valid from the current state")

    if request.security_or_privacy_risk:
        decision = "Transferred to the restricted security/privacy response process."
        evidence = (
            f"- Restricted event ID: `{request.restricted_event_id}`\n"
            "- Entry point: `SECURITY.md` (do not add restricted details here)"
        )
    else:
        decision = _escape_markdown(request.decision)
        evidence = "\n".join(f"- {link}" for link in request.evidence_links)
    marker = f"<!-- lifecycle-transition:{request.issue_number}:{current}:{target} -->"
    comment = "\n".join(
        (
            "### Incident state transition",
            "",
            f"- Previous status: `{current}`",
            f"- Current status: `{target}`",
            f"- Operator: `{_escape_markdown(request.actor)}`",
            f"- Time: `{request.occurred_at}`",
            f"- Decision: {decision}",
            "- Evidence:",
            evidence,
            "",
            marker,
            "",
        )
    )
    action = "close" if target == "closed" else "reopen" if current == "closed" else "none"
    return IncidentTransition(
        issue_number=request.issue_number,
        current_status=current,
        target_status=target,
        current_label=current_label,
        target_label=f"status:{target}",
        severity_label=severity_label,
        issue_action=action,
        comment=comment,
        noop=False,
        security_escalation=request.security_or_privacy_risk,
    )


def write_transition_outputs(
    result: IncidentTransition, output_dir: Path, github_output: Path | None
) -> tuple[Path, Path]:
    if output_dir.exists() and (not output_dir.is_dir() or any(output_dir.iterdir())):
        raise LifecycleError(f"incident output path must be an empty directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    comment_path = output_dir / "transition-comment.md"
    comment_path.write_text(result.comment, encoding="utf-8")
    plan_path = output_dir / "transition-plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "issue_number": result.issue_number,
                "current_status": result.current_status,
                "target_status": result.target_status,
                "current_label": result.current_label,
                "target_label": result.target_label,
                "severity_label": result.severity_label,
                "issue_action": result.issue_action,
                "noop": result.noop,
                "security_escalation": result.security_escalation,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    if github_output is not None:
        with github_output.open("a", encoding="utf-8") as output:
            output.write(f"current_label={result.current_label}\n")
            output.write(f"target_label={result.target_label}\n")
            output.write(f"severity_label={result.severity_label}\n")
            output.write(f"issue_action={result.issue_action}\n")
            output.write(f"noop={'true' if result.noop else 'false'}\n")
            output.write(f"comment_path={comment_path}\n")
    return plan_path, comment_path
