from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

from .common import LifecycleError, LifecyclePolicy, load_json_mapping, require_string
from .release import VERSION_PATTERN

SOURCE_PATTERN = re.compile(r"^(?P<kind>incident|release):(?P<identifier>.+)$")
ISSUE_NUMBER_PATTERN = re.compile(r"^[1-9]\d*$")
SECTION_PATTERN = re.compile(r"^###\s+(?P<name>[^\n]+?)\s*$", re.MULTILINE)
TRANSITION_TIME_PATTERN = re.compile(
    r"- Current status: `(?:recovered|closed)`.*?- Time: `(?P<time>[^`]+)`",
    re.DOTALL,
)
RETROSPECTIVE_METADATA_PATTERN = re.compile(
    r"<!--\s*lifecycle-retrospective\s*\n(?P<body>.*?)\n\s*-->", re.DOTALL
)


@dataclass(frozen=True)
class RetrospectiveRequest:
    source_kind: str
    source_id: str
    source_key: str
    stability_confirmed: bool
    timeline: str
    visible_information: str
    contributing_factors: str
    guard_effectiveness: str
    uncertainties: str
    action_links: str
    actor: str
    occurred_at: str
    apply: bool
    confirmation: str


@dataclass(frozen=True)
class RenderedRetrospective:
    title: str
    body: str
    due_date: date | None
    source_key: str
    duplicate_number: int | None
    duplicate_url: str | None

    @property
    def duplicate(self) -> bool:
        return self.duplicate_number is not None


@dataclass(frozen=True)
class AuditFinding:
    kind: str
    record: str
    due_date: date | None
    url: str
    detail: str


def _parse_datetime(value: object, field: str) -> datetime:
    text = require_string(value, field)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as error:
        raise LifecycleError(f"{field} must be an ISO-8601 timestamp with timezone") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise LifecycleError(f"{field} must include a timezone")
    return parsed


def _required_text(value: object, field: str) -> str:
    return require_string(value, field).strip()


def build_retrospective_request(
    *,
    source: object,
    stability_confirmed: bool,
    timeline: object,
    visible_information: object,
    contributing_factors: object,
    guard_effectiveness: object,
    uncertainties: object,
    action_links: object,
    actor: object,
    occurred_at: object,
    apply: bool,
    confirmation: object,
) -> RetrospectiveRequest:
    source_text = require_string(source, "source")
    match = SOURCE_PATTERN.fullmatch(source_text)
    if match is None:
        raise LifecycleError(
            "retrospective source must be incident:N or release:vMAJOR.MINOR.PATCH"
        )
    kind = match.group("kind")
    identifier = match.group("identifier")
    if kind == "incident" and not ISSUE_NUMBER_PATTERN.fullmatch(identifier):
        raise LifecycleError("incident retrospective source must use a positive Issue number")
    if kind == "release" and not VERSION_PATTERN.fullmatch(identifier):
        raise LifecycleError("release retrospective source must use vMAJOR.MINOR.PATCH")
    timestamp = require_string(occurred_at, "occurred_at")
    _parse_datetime(timestamp, "occurred_at")
    confirmation_text = confirmation if isinstance(confirmation, str) else ""
    expected_confirmation = f"retrospective-{kind}-{identifier}"
    if apply and confirmation_text != expected_confirmation:
        raise LifecycleError(
            f"retrospective confirmation must exactly match {expected_confirmation}"
        )
    return RetrospectiveRequest(
        source_kind=kind,
        source_id=identifier,
        source_key=source_text,
        stability_confirmed=stability_confirmed,
        timeline=_required_text(timeline, "timeline"),
        visible_information=_required_text(visible_information, "visible_information"),
        contributing_factors=_required_text(contributing_factors, "contributing_factors"),
        guard_effectiveness=_required_text(guard_effectiveness, "guard_effectiveness"),
        uncertainties=_required_text(uncertainties, "uncertainties"),
        action_links=_required_text(action_links, "action_links"),
        actor=require_string(actor, "actor"),
        occurred_at=timestamp,
        apply=apply,
        confirmation=confirmation_text,
    )


def calculate_due_date(anchor: datetime, source_type: str, policy: LifecyclePolicy) -> date | None:
    days = policy.retrospective_deadlines_days[source_type]
    return None if days is None else (anchor + timedelta(days=days)).date()


def _load_json_array(path: Path, label: str) -> Sequence[object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise LifecycleError(f"cannot read {label}: {error}") from error
    if not isinstance(value, list):
        raise LifecycleError(f"{label} must be a JSON array")
    if value and all(isinstance(page, list) for page in value):
        return tuple(item for page in value for item in page)
    return value


def _label_names(issue: Mapping[str, object]) -> set[str]:
    labels = issue.get("labels")
    if not isinstance(labels, list):
        raise LifecycleError("Issue labels must be an array")
    names: set[str] = set()
    for label in labels:
        if isinstance(label, Mapping) and isinstance(label.get("name"), str):
            names.add(str(label["name"]))
        elif isinstance(label, str):
            names.add(label)
    return names


def _mapping_value(record: Mapping[str, object], *names: str) -> object:
    for name in names:
        if name in record:
            return record[name]
    return None


def _issue_state(issue: Mapping[str, object]) -> str:
    state = _mapping_value(issue, "state")
    return state.upper() if isinstance(state, str) else ""


def _issue_url(issue: Mapping[str, object]) -> str:
    value = _mapping_value(issue, "html_url", "url")
    return value if isinstance(value, str) else ""


def _parse_sections(body: str) -> dict[str, str]:
    matches = list(SECTION_PATTERN.finditer(body))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections[match.group("name").strip()] = body[start:end].strip()
    return sections


def _incident_severity(issue: Mapping[str, object], policy: LifecyclePolicy) -> str:
    labels = _label_names(issue)
    severities = sorted(
        label.removeprefix("severity:") for label in labels if label.startswith("severity:")
    )
    if len(severities) > 1:
        raise LifecycleError("incident source has multiple severity labels")
    if severities:
        severity = severities[0]
    else:
        body = issue.get("body")
        if not isinstance(body, str):
            raise LifecycleError("incident source body must be text")
        severity = _parse_sections(body).get("Severity", "").strip().lower()
    if severity not in policy.incident_severities:
        raise LifecycleError("incident source must declare SEV1 through SEV4")
    return severity


def _incident_anchor(issue: Mapping[str, object], request: RetrospectiveRequest) -> datetime:
    if request.stability_confirmed:
        return _parse_datetime(request.occurred_at, "occurred_at")
    comments = issue.get("comments")
    times: list[datetime] = []
    if isinstance(comments, list):
        for comment in comments:
            body = comment.get("body") if isinstance(comment, Mapping) else None
            if not isinstance(body, str):
                continue
            for match in TRANSITION_TIME_PATTERN.finditer(body):
                times.append(_parse_datetime(match.group("time"), "incident transition time"))
    if times:
        return min(times)
    raise LifecycleError(
        "incident has no recovery transition timestamp; explicitly confirm stability "
        "to set an anchor"
    )


def _find_duplicate(existing: Sequence[object], source_key: str) -> tuple[int | None, str | None]:
    marker = f"<!-- lifecycle-source:{source_key} -->"
    for raw_issue in existing:
        if not isinstance(raw_issue, Mapping):
            continue
        body = raw_issue.get("body")
        if isinstance(body, str) and marker in body:
            number = raw_issue.get("number")
            url = _mapping_value(raw_issue, "html_url", "url")
            if isinstance(number, int) and isinstance(url, str):
                return number, url
    return None, None


def _source_details(
    request: RetrospectiveRequest,
    source: Mapping[str, object],
    policy: LifecyclePolicy,
) -> tuple[str, str, date | None]:
    if request.source_kind == "incident":
        if source.get("number") != int(request.source_id):
            raise LifecycleError("incident source number does not match the request")
        labels = _label_names(source)
        if "type:incident" not in labels:
            raise LifecycleError("incident retrospective source must have type:incident")
        statuses = sorted(
            label.removeprefix("status:") for label in labels if label.startswith("status:")
        )
        if len(statuses) != 1:
            raise LifecycleError("incident source must have exactly one current status")
        if statuses[0] not in {"recovered", "closed"} and not request.stability_confirmed:
            raise LifecycleError("incident must be recovered/closed or explicitly confirmed stable")
        severity = _incident_severity(source, policy)
        anchor = _incident_anchor(source, request)
        return (
            f"Incident #{request.source_id}",
            require_string(source.get("url"), "incident url"),
            calculate_due_date(anchor, severity, policy),
        )

    tag_name = source.get("tagName")
    if tag_name != request.source_id:
        raise LifecycleError("release source tag does not match the request")
    if source.get("isDraft") is not False or source.get("isPrerelease") is not False:
        raise LifecycleError("release retrospective requires a published non-prerelease Release")
    published_at = _parse_datetime(source.get("publishedAt"), "release publishedAt")
    return (
        f"Release {request.source_id}",
        require_string(source.get("url"), "release url"),
        calculate_due_date(published_at, "release", policy),
    )


def render_retrospective(
    request: RetrospectiveRequest,
    source_path: Path,
    existing_path: Path,
    policy: LifecyclePolicy,
) -> RenderedRetrospective:
    source = load_json_mapping(source_path, "retrospective source")
    existing = _load_json_array(existing_path, "existing retrospectives")
    source_title, source_url, due_date = _source_details(request, source, policy)
    duplicate_number, duplicate_url = _find_duplicate(existing, request.source_key)
    due_text = due_date.isoformat() if due_date is not None else "none"
    body = "\n".join(
        (
            f"<!-- lifecycle-source:{request.source_key} -->",
            "<!-- lifecycle-retrospective",
            "schema-version: 1",
            f"source: {request.source_key}",
            f"due-date: {due_text}",
            "-->",
            "",
            "# Lifecycle Retrospective",
            "",
            f"- Source: [{source_title}]({source_url})",
            f"- Due date: `{due_text}`",
            f"- Created by: `{request.actor}`",
            f"- Created at: `{request.occurred_at}`",
            "",
            "## Factual timeline",
            "",
            request.timeline,
            "",
            "## Information visible at the time",
            "",
            request.visible_information,
            "",
            "## Contributing factors",
            "",
            request.contributing_factors,
            "",
            "## Guard effectiveness",
            "",
            request.guard_effectiveness,
            "",
            "## Uncertainties",
            "",
            request.uncertainties,
            "",
            "## Improvement action links",
            "",
            request.action_links,
            "",
        )
    )
    return RenderedRetrospective(
        title=f"[Retrospective] {source_title}",
        body=body,
        due_date=due_date,
        source_key=request.source_key,
        duplicate_number=duplicate_number,
        duplicate_url=duplicate_url,
    )


def write_retrospective_outputs(
    result: RenderedRetrospective,
    output_dir: Path,
    github_output: Path | None,
) -> tuple[Path, Path]:
    if output_dir.exists() and (not output_dir.is_dir() or any(output_dir.iterdir())):
        raise LifecycleError(f"retrospective output path must be an empty directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    body_path = output_dir / "retrospective.md"
    body_path.write_text(result.body, encoding="utf-8")
    plan_path = output_dir / "retrospective-plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "title": result.title,
                "source": result.source_key,
                "due_date": result.due_date.isoformat() if result.due_date else None,
                "duplicate": result.duplicate,
                "duplicate_number": result.duplicate_number,
                "duplicate_url": result.duplicate_url,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    if github_output is not None:
        with github_output.open("a", encoding="utf-8") as output:
            output.write(f"duplicate={'true' if result.duplicate else 'false'}\n")
            output.write(f"duplicate_url={result.duplicate_url or ''}\n")
            output.write(f"title={result.title}\n")
            output.write(f"body_path={body_path}\n")
    return plan_path, body_path


def _metadata(body: str) -> dict[str, str]:
    match = RETROSPECTIVE_METADATA_PATTERN.search(body)
    if match is None:
        return {}
    values: dict[str, str] = {}
    for line in match.group("body").splitlines():
        key, separator, value = line.partition(":")
        if separator:
            values[key.strip()] = value.strip()
    return values


def _parse_date(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise LifecycleError(f"{field} must be an ISO date") from error


def _comment_issue_number(comment: Mapping[str, object]) -> int | None:
    issue_url = _mapping_value(comment, "issue_url", "issueUrl")
    if not isinstance(issue_url, str):
        return None
    _, separator, suffix = issue_url.rstrip("/").rpartition("/")
    return int(suffix) if separator and ISSUE_NUMBER_PATTERN.fullmatch(suffix) else None


def _comments_by_issue(comments_path: Path | None) -> dict[int, list[Mapping[str, object]]]:
    if comments_path is None:
        return {}
    comments = _load_json_array(comments_path, "lifecycle Issue comments")
    by_issue: dict[int, list[Mapping[str, object]]] = {}
    for raw_comment in comments:
        if not isinstance(raw_comment, Mapping):
            continue
        issue_number = _comment_issue_number(raw_comment)
        if issue_number is not None:
            by_issue.setdefault(issue_number, []).append(raw_comment)
    return by_issue


def _incident_recovery_anchor(
    issue: Mapping[str, object], external_comments: Sequence[Mapping[str, object]]
) -> datetime:
    raw_comments = issue.get("comments")
    comments: list[object] = list(external_comments)
    if isinstance(raw_comments, list):
        comments.extend(raw_comments)
    times: list[datetime] = []
    for comment in comments:
        body = comment.get("body") if isinstance(comment, Mapping) else None
        if not isinstance(body, str):
            continue
        for match in TRANSITION_TIME_PATTERN.finditer(body):
            times.append(_parse_datetime(match.group("time"), "incident recovery time"))
    if not times:
        raise LifecycleError("recovered/closed incident has no recovery transition timestamp")
    return min(times)


def _invalid_finding(record: str, url: str, detail: str) -> AuditFinding:
    return AuditFinding("record-invalid", record, None, url, detail)


def _validate_source_key(source_key: str) -> None:
    match = SOURCE_PATTERN.fullmatch(source_key)
    if match is None:
        raise LifecycleError("retrospective metadata source is missing or invalid")
    identifier = match.group("identifier")
    if match.group("kind") == "incident" and ISSUE_NUMBER_PATTERN.fullmatch(identifier) is None:
        raise LifecycleError("retrospective incident source must use a positive Issue number")
    if match.group("kind") == "release" and VERSION_PATTERN.fullmatch(identifier) is None:
        raise LifecycleError("retrospective release source must use vMAJOR.MINOR.PATCH")


def audit_records(
    issues_path: Path,
    releases_path: Path,
    policy: LifecyclePolicy,
    as_of: date,
    comments_path: Path | None = None,
) -> tuple[AuditFinding, ...]:
    issues = _load_json_array(issues_path, "lifecycle Issues")
    releases = _load_json_array(releases_path, "release list")
    comments_by_issue = _comments_by_issue(comments_path)
    retrospective_records: dict[str, list[tuple[str, str]]] = {}
    findings: list[AuditFinding] = []

    for raw_issue in issues:
        if not isinstance(raw_issue, Mapping) or "pull_request" in raw_issue:
            continue
        number = raw_issue.get("number")
        record = f"Issue #{number}"
        url = _issue_url(raw_issue)
        try:
            labels = _label_names(raw_issue)
            body = raw_issue.get("body")
            body_text = body if isinstance(body, str) else ""
            state = _issue_state(raw_issue)
            if "type:retrospective" in labels:
                metadata = _metadata(body_text)
                if metadata.get("schema-version") != "1":
                    raise LifecycleError("retrospective metadata schema-version must be 1")
                source_key = metadata.get("source", "")
                _validate_source_key(source_key)
                due_value = metadata.get("due-date")
                if not due_value:
                    raise LifecycleError("retrospective metadata due-date is missing")
                due = (
                    None
                    if due_value == "none"
                    else _parse_date(due_value, f"retrospective #{number} due-date")
                )
                retrospective_records.setdefault(source_key, []).append((record, url))
                if state == "OPEN" and due is not None and due < as_of:
                    findings.append(
                        AuditFinding(
                            "retrospective-overdue",
                            record,
                            due,
                            url,
                            "retrospective remains open after its deadline",
                        )
                    )
            if "type:improvement-action" in labels:
                due_value = _parse_sections(body_text).get("Due date", "")
                due = _parse_date(due_value, f"improvement action #{number} Due date")
                if state == "OPEN" and due < as_of:
                    findings.append(
                        AuditFinding(
                            "improvement-action-overdue",
                            record,
                            due,
                            url,
                            "improvement action remains open after its deadline",
                        )
                    )
        except LifecycleError as error:
            findings.append(_invalid_finding(record, url, str(error)))

    for source_key, records in retrospective_records.items():
        if len(records) > 1:
            record_names = ", ".join(record for record, _ in records)
            findings.append(
                AuditFinding(
                    "retrospective-duplicate",
                    record_names,
                    None,
                    records[0][1],
                    f"multiple retrospectives reference {source_key}",
                )
            )

    retrospective_sources = set(retrospective_records)

    for raw_issue in issues:
        if not isinstance(raw_issue, Mapping) or "pull_request" in raw_issue:
            continue
        number = raw_issue.get("number")
        record = f"Incident #{number}"
        url = _issue_url(raw_issue)
        try:
            labels = _label_names(raw_issue)
            statuses = {
                label.removeprefix("status:") for label in labels if label.startswith("status:")
            }
            if "type:incident" not in labels:
                continue
            if len(statuses) != 1:
                raise LifecycleError("incident must contain exactly one current status label")
            if not statuses.intersection({"recovered", "closed"}):
                continue
            if not isinstance(number, int):
                raise LifecycleError("incident number must be an integer")
            source_key = f"incident:{number}"
            severity = _incident_severity(raw_issue, policy)
            anchor = _incident_recovery_anchor(raw_issue, comments_by_issue.get(number, ()))
            if source_key in retrospective_sources:
                continue
            days = policy.retrospective_deadlines_days[severity]
            if days is None:
                continue
            due = (anchor + timedelta(days=days)).date()
            if due < as_of:
                findings.append(
                    AuditFinding(
                        "retrospective-missing",
                        record,
                        due,
                        url,
                        "eligible incident has no linked retrospective",
                    )
                )
        except LifecycleError as error:
            findings.append(_invalid_finding(record, url, str(error)))

    for raw_release in releases:
        if not isinstance(raw_release, Mapping):
            continue
        tag = raw_release.get("tagName", raw_release.get("tag_name"))
        record = f"Release {tag}"
        url_value = raw_release.get("html_url", raw_release.get("url"))
        url = url_value if isinstance(url_value, str) else ""
        try:
            is_draft = raw_release.get("isDraft", raw_release.get("draft"))
            is_prerelease = raw_release.get("isPrerelease", raw_release.get("prerelease"))
            if is_draft is not False or is_prerelease is not False:
                continue
            if not isinstance(tag, str) or VERSION_PATTERN.fullmatch(tag) is None:
                raise LifecycleError("published Release tag must match vMAJOR.MINOR.PATCH")
            source_key = f"release:{tag}"
            if source_key in retrospective_sources:
                continue
            published_at = raw_release.get("publishedAt", raw_release.get("published_at"))
            anchor = _parse_datetime(published_at, f"release {tag} publishedAt")
            due = calculate_due_date(anchor, "release", policy)
            if due is not None and due < as_of:
                findings.append(
                    AuditFinding(
                        "retrospective-missing",
                        record,
                        due,
                        url,
                        "published Release has no linked retrospective",
                    )
                )
        except LifecycleError as error:
            findings.append(_invalid_finding(record, url, str(error)))
    return tuple(
        sorted(
            findings,
            key=lambda finding: (
                finding.due_date or date.max,
                finding.kind,
                finding.record,
            ),
        )
    )


def write_audit_outputs(findings: tuple[AuditFinding, ...], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            [
                {
                    "kind": finding.kind,
                    "record": finding.record,
                    "due_date": finding.due_date.isoformat() if finding.due_date else None,
                    "url": finding.url,
                    "detail": finding.detail,
                }
                for finding in findings
            ],
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
