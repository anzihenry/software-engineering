from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from .common import (
    LifecycleError,
    LifecyclePolicy,
    load_json_mapping,
    require_string,
)

VERSION_PATTERN = re.compile(r"^v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
REACHABLE_COMPARISON_STATUSES = {"ahead", "identical"}


@dataclass(frozen=True)
class ReleaseRequest:
    version: str
    source_sha: str
    risk_level: str
    change_records: str
    summary: str
    repository: str
    actor: str
    run_url: str
    created_at: str


@dataclass(frozen=True)
class PreparedRelease:
    record: Path
    checklist: Path
    manifest: Path


def validate_release_inputs(
    version: str,
    source_sha: str,
    risk_level: str,
    policy: LifecyclePolicy,
    *,
    dry_run: bool,
    confirmation: str,
) -> None:
    if not VERSION_PATTERN.fullmatch(version):
        raise LifecycleError("release version must match vMAJOR.MINOR.PATCH")
    if not SHA_PATTERN.fullmatch(source_sha):
        raise LifecycleError("release source SHA must be 40 lowercase hexadecimal characters")
    if risk_level not in policy.risk_levels:
        raise LifecycleError(f"release risk level must be one of: {', '.join(policy.risk_levels)}")
    if not dry_run and confirmation != version:
        raise LifecycleError("release confirmation must exactly match the requested version")


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


def _load_check_runs(path: Path) -> Mapping[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise LifecycleError(f"cannot read check-runs response: {error}") from error
    if isinstance(value, Mapping):
        return value
    if isinstance(value, list) and all(isinstance(page, Mapping) for page in value):
        runs: list[object] = []
        for page in value:
            page_runs = page.get("check_runs")
            if not isinstance(page_runs, list):
                raise LifecycleError("check-runs page must contain a check_runs array")
            runs.extend(page_runs)
        return {"check_runs": runs}
    raise LifecycleError("check-runs response must be an object or an array of page objects")


def _validate_comparison(
    comparison: Mapping[str, object], source_sha: str, default_branch: str
) -> None:
    status = comparison.get("status")
    base_commit = comparison.get("base_commit")
    base_sha = base_commit.get("sha") if isinstance(base_commit, Mapping) else None
    if base_sha != source_sha:
        raise LifecycleError("comparison base commit does not match the requested source SHA")
    if status not in REACHABLE_COMPARISON_STATUSES:
        raise LifecycleError(f"source SHA is not reachable from {default_branch}")


def _validate_required_checks(
    check_runs: Mapping[str, object], required_checks: tuple[str, ...]
) -> dict[str, str]:
    raw_runs = check_runs.get("check_runs")
    if not isinstance(raw_runs, list):
        raise LifecycleError("check-runs response must contain a check_runs array")
    successful: set[str] = set()
    observed: dict[str, str] = {}
    for raw_run in raw_runs:
        if not isinstance(raw_run, Mapping):
            continue
        name = raw_run.get("name")
        status = raw_run.get("status")
        conclusion = raw_run.get("conclusion")
        if isinstance(name, str) and name in required_checks:
            observed[name] = str(conclusion or status or "unknown")
            if status == "completed" and conclusion == "success":
                successful.add(name)
    missing = [name for name in required_checks if name not in successful]
    if missing:
        details = ", ".join(f"{name}={observed.get(name, 'missing')}" for name in missing)
        raise LifecycleError(f"required release checks are not successful: {details}")
    return {name: "success" for name in required_checks}


def _validate_no_existing_version(
    version: str, tag_refs: Sequence[object], releases: Sequence[object]
) -> None:
    if tag_refs:
        raise LifecycleError(f"release tag already exists: {version}")
    for raw_release in releases:
        if (
            isinstance(raw_release, Mapping)
            and raw_release.get("tagName", raw_release.get("tag_name")) == version
        ):
            raise LifecycleError(f"GitHub Release already exists: {version}")


def validate_release_github_state(
    request: ReleaseRequest,
    policy: LifecyclePolicy,
    comparison_path: Path,
    check_runs_path: Path,
    tag_refs_path: Path,
    releases_path: Path,
) -> dict[str, str]:
    comparison = load_json_mapping(comparison_path, "commit comparison")
    check_runs = _load_check_runs(check_runs_path)
    tag_refs = _load_json_array(tag_refs_path, "matching tag refs")
    releases = _load_json_array(releases_path, "release list")
    _validate_comparison(comparison, request.source_sha, policy.default_branch)
    successful_checks = _validate_required_checks(check_runs, policy.release_required_checks)
    _validate_no_existing_version(request.version, tag_refs, releases)
    return successful_checks


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare_release(
    request: ReleaseRequest,
    policy: LifecyclePolicy,
    comparison_path: Path,
    check_runs_path: Path,
    tag_refs_path: Path,
    releases_path: Path,
    output_dir: Path,
) -> PreparedRelease:
    checks = validate_release_github_state(
        request,
        policy,
        comparison_path,
        check_runs_path,
        tag_refs_path,
        releases_path,
    )
    if output_dir.exists() and (not output_dir.is_dir() or any(output_dir.iterdir())):
        raise LifecycleError(f"release output path must be an empty directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    record = output_dir / "release-record.md"
    record.write_text(
        "\n".join(
            (
                f"# Draft Release {request.version}",
                "",
                f"- Source SHA: `{request.source_sha}`",
                f"- Risk level: `{request.risk_level}`",
                f"- Repository: `{request.repository}`",
                f"- Prepared by: `{request.actor}`",
                f"- Prepared at: `{request.created_at}`",
                f"- Workflow run: {request.run_url}",
                "",
                "## Summary",
                "",
                request.summary,
                "",
                "## Change records",
                "",
                request.change_records,
                "",
                "## Boundary",
                "",
                "This record prepares a Draft Release only. Publishing, deployment, "
                "and rollback remain explicit human decisions.",
                "",
            )
        ),
        encoding="utf-8",
    )

    checklist = output_dir / "release-candidate-checklist.md"
    checklist.write_text(
        "\n".join(
            (
                f"# Release Candidate Checklist: {request.version}",
                "",
                f"- [x] Full source SHA fixed to `{request.source_sha}`",
                f"- [x] Source SHA is reachable from `{policy.default_branch}`",
                *(
                    f"- [x] Required check `{name}` completed successfully"
                    for name in policy.release_required_checks
                ),
                "- [x] Version, tag, and GitHub Release were absent during preparation",
                "- [ ] Authorized human reviewed the Draft Release",
                "- [ ] Authorized human made the publish Go/No-Go decision",
                "",
            )
        ),
        encoding="utf-8",
    )

    manifest = output_dir / "release-candidate.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "version": request.version,
                "source_sha": request.source_sha,
                "risk_level": request.risk_level,
                "repository": request.repository,
                "required_checks": checks,
                "change_records": request.change_records,
                "prepared_by": request.actor,
                "prepared_at": request.created_at,
                "workflow_run": request.run_url,
                "files": {
                    record.name: _sha256(record),
                    checklist.name: _sha256(checklist),
                },
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return PreparedRelease(record=record, checklist=checklist, manifest=manifest)


def build_release_request(
    *,
    version: object,
    source_sha: object,
    risk_level: object,
    change_records: object,
    summary: object,
    repository: object,
    actor: object,
    run_url: object,
    created_at: object,
) -> ReleaseRequest:
    return ReleaseRequest(
        version=require_string(version, "version"),
        source_sha=require_string(source_sha, "source_sha"),
        risk_level=require_string(risk_level, "risk_level"),
        change_records=require_string(change_records, "change_records"),
        summary=require_string(summary, "summary"),
        repository=require_string(repository, "repository"),
        actor=require_string(actor, "actor"),
        run_url=require_string(run_url, "run_url"),
        created_at=require_string(created_at, "created_at"),
    )
