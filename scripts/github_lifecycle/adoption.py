from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .common import LifecycleError, load_policy
from .package import load_manifest, validate_profile

REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
BRANCH_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,254}$")
SECURITY_REPOSITORY_URL_PATTERN = re.compile(
    r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?=/security(?:/|$))"
)
DEFAULT_BRANCH_ENV_PATTERN = re.compile(r"(?m)^(\s*DEFAULT_BRANCH:\s*)[^\s#]+(\s*)$")
ACTION_USE_PATTERN = re.compile(r"(?m)^\s*uses:\s*(?P<value>\S+)\s*(?:#.*)?$")
PINNED_ACTION_PATTERN = re.compile(r"^[^\s@]+@[0-9a-f]{40}$")


@dataclass(frozen=True)
class InstallEntry:
    path: str
    action: str


@dataclass(frozen=True)
class InstallPlan:
    repository: str
    default_branch: str
    profile: str
    target: Path
    entries: tuple[InstallEntry, ...]

    @property
    def conflicts(self) -> tuple[str, ...]:
        return tuple(entry.path for entry in self.entries if entry.action == "conflict")


@dataclass(frozen=True)
class DoctorFinding:
    scope: str
    code: str
    detail: str


def validate_repository_name(value: str) -> str:
    if REPOSITORY_PATTERN.fullmatch(value) is None or any(
        segment in {".", ".."} for segment in value.split("/")
    ):
        raise LifecycleError("repository must use owner/name format")
    return value


def validate_default_branch(value: str) -> str:
    parts = value.split("/")
    if (
        BRANCH_PATTERN.fullmatch(value) is None
        or ".." in value
        or "//" in value
        or value.endswith((".", "/"))
        or any(part in {".", ".."} or part.endswith(".lock") for part in parts)
    ):
        raise LifecycleError("default_branch is not a safe Git branch name")
    return value


def _resolve_file(root: Path, relative: str, label: str) -> Path:
    candidate = root / relative
    if candidate.is_symlink():
        raise LifecycleError(f"{label} must not be a symlink: {relative}")
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as error:
        raise LifecycleError(f"cannot resolve {label} {relative}: {error}") from error
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise LifecycleError(f"{label} is outside its repository root: {relative}")
    return resolved


def _safe_destination(root: Path, relative: str) -> Path:
    destination = root / relative
    current = root
    for part in Path(relative).parts[:-1]:
        current /= part
        if current.is_symlink():
            raise LifecycleError(f"install destination parent is a symlink: {relative}")
        if current.exists() and not current.is_dir():
            raise LifecycleError(f"install destination parent is not a directory: {relative}")
    existing_parent = destination.parent
    while not existing_parent.exists() and existing_parent != root:
        existing_parent = existing_parent.parent
    if not existing_parent.resolve(strict=True).is_relative_to(root):
        raise LifecycleError(f"install destination escapes the target root: {relative}")
    return destination


def _render_file(
    relative: str,
    content: bytes,
    *,
    repository: str,
    default_branch: str,
) -> bytes:
    if relative == ".github/lifecycle-policy.json":
        try:
            raw = json.loads(content.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as error:
            raise LifecycleError(f"cannot render lifecycle policy: {error}") from error
        if not isinstance(raw, dict):
            raise LifecycleError("lifecycle policy must be a JSON object")
        raw["default_branch"] = default_branch
        return (json.dumps(raw, ensure_ascii=False, indent=2) + "\n").encode()

    if relative in {".github/ISSUE_TEMPLATE/config.yml", "SECURITY.md"}:
        try:
            text = content.decode("utf-8")
        except UnicodeError as error:
            raise LifecycleError(f"cannot render {relative}: {error}") from error
        rendered = SECURITY_REPOSITORY_URL_PATTERN.sub(f"https://github.com/{repository}", text)
        return rendered.encode()

    if relative == ".github/workflows/prepare-release.yml":
        try:
            text = content.decode("utf-8")
        except UnicodeError as error:
            raise LifecycleError(f"cannot render {relative}: {error}") from error
        rendered, count = DEFAULT_BRANCH_ENV_PATTERN.subn(rf"\g<1>{default_branch}\g<2>", text)
        if count != 2:
            raise LifecycleError(
                "prepare-release workflow must contain two DEFAULT_BRANCH declarations"
            )
        return rendered.encode()

    return content


def rendered_files(
    source_root: Path,
    manifest_path: Path,
    *,
    repository: str,
    default_branch: str,
    profile: str = "full",
) -> tuple[tuple[str, bytes], ...]:
    repository = validate_repository_name(repository)
    default_branch = validate_default_branch(default_branch)
    profile = validate_profile(profile)
    source_root = source_root.resolve(strict=True)
    manifest = manifest_path if manifest_path.is_absolute() else source_root / manifest_path
    files = load_manifest(manifest, profile=profile)
    rendered: list[tuple[str, bytes]] = []
    for relative in files:
        source = _resolve_file(source_root, relative, "automation source file")
        rendered.append(
            (
                relative,
                _render_file(
                    relative,
                    source.read_bytes(),
                    repository=repository,
                    default_branch=default_branch,
                ),
            )
        )
    return tuple(rendered)


def plan_install(
    source_root: Path,
    manifest_path: Path,
    target: Path,
    *,
    repository: str,
    default_branch: str,
    profile: str = "full",
) -> tuple[InstallPlan, tuple[tuple[str, bytes], ...]]:
    source_root = source_root.resolve(strict=True)
    target = target.resolve(strict=True)
    if not target.is_dir():
        raise LifecycleError("install target must be an existing directory")
    if target == source_root:
        raise LifecycleError("install target must differ from the automation source root")
    files = rendered_files(
        source_root,
        manifest_path,
        repository=repository,
        default_branch=default_branch,
        profile=profile,
    )
    entries: list[InstallEntry] = []
    for relative, content in files:
        try:
            destination = _safe_destination(target, relative)
        except LifecycleError:
            entries.append(InstallEntry(relative, "conflict"))
            continue
        if destination.is_symlink():
            entries.append(InstallEntry(relative, "conflict"))
            continue
        if destination.exists():
            if not destination.is_file():
                entries.append(InstallEntry(relative, "conflict"))
                continue
            action = "unchanged" if destination.read_bytes() == content else "conflict"
        else:
            action = "create"
        entries.append(InstallEntry(relative, action))
    return (
        InstallPlan(
            repository=repository,
            default_branch=default_branch,
            profile=profile,
            target=target,
            entries=tuple(entries),
        ),
        files,
    )


def apply_install(
    plan: InstallPlan,
    files: tuple[tuple[str, bytes], ...],
    *,
    confirmation: str,
) -> None:
    expected = f"install:{plan.repository}"
    if confirmation != expected:
        raise LifecycleError(f"install confirmation must exactly match {expected}")
    if plan.conflicts:
        raise LifecycleError(
            "install refuses to overwrite conflicting files: " + ", ".join(plan.conflicts)
        )
    actions = {entry.path: entry.action for entry in plan.entries}
    for relative, content in files:
        if actions[relative] != "create":
            continue
        destination = _safe_destination(plan.target, relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() or destination.is_symlink():
            raise LifecycleError(f"install destination changed after planning: {relative}")
        destination.write_bytes(content)


def render_install_plan(plan: InstallPlan, *, dry_run: bool) -> str:
    counts = {
        action: sum(entry.action == action for entry in plan.entries)
        for action in ("create", "unchanged", "conflict")
    }
    return json.dumps(
        {
            "schema_version": 2,
            "mode": "dry-run" if dry_run else "apply",
            "repository": plan.repository,
            "default_branch": plan.default_branch,
            "profile": plan.profile,
            "target": str(plan.target),
            "counts": counts,
            "entries": [{"path": entry.path, "action": entry.action} for entry in plan.entries],
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )


def inspect_local_install(
    root: Path,
    manifest_path: Path,
    *,
    repository: str,
    expected_default_branch: str,
    profile: str = "full",
) -> tuple[DoctorFinding, ...]:
    findings: list[DoctorFinding] = []
    root = root.resolve(strict=True)
    repository = validate_repository_name(repository)
    manifest = manifest_path if manifest_path.is_absolute() else root / manifest_path
    try:
        files = load_manifest(manifest, profile=profile)
    except LifecycleError as error:
        return (DoctorFinding("local", "manifest-invalid", str(error)),)

    for relative in files:
        try:
            _resolve_file(root, relative, "installed automation file")
        except LifecycleError as error:
            findings.append(DoctorFinding("local", "file-invalid", str(error)))

    policy_path = root / ".github/lifecycle-policy.json"
    try:
        policy = load_policy(policy_path)
    except LifecycleError as error:
        findings.append(DoctorFinding("local", "policy-invalid", str(error)))
        policy = None
    if policy is not None and policy.default_branch != expected_default_branch:
        findings.append(
            DoctorFinding(
                "local",
                "default-branch-mismatch",
                f"policy default branch {policy.default_branch!r} does not match "
                f"GitHub {expected_default_branch!r}",
            )
        )

    expected_url = f"https://github.com/{repository}"
    for relative in (".github/ISSUE_TEMPLATE/config.yml", "SECURITY.md"):
        path = root / relative
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            security_urls = SECURITY_REPOSITORY_URL_PATTERN.findall(text)
            if security_urls and any(url != expected_url for url in security_urls):
                findings.append(
                    DoctorFinding(
                        "local",
                        "repository-link-mismatch",
                        f"{relative} contains a security link for another repository",
                    )
                )

    workflows_root = root / ".github/workflows"
    for workflow in sorted(workflows_root.glob("*.y*ml")):
        text = workflow.read_text(encoding="utf-8")
        if "pull_request_target" in text:
            findings.append(
                DoctorFinding(
                    "local",
                    "unsafe-trigger",
                    f"{workflow.relative_to(root)} uses pull_request_target",
                )
            )
        for match in ACTION_USE_PATTERN.finditer(text):
            value = match.group("value")
            if not value.startswith("./") and PINNED_ACTION_PATTERN.fullmatch(value) is None:
                findings.append(
                    DoctorFinding(
                        "local",
                        "action-not-pinned",
                        f"{workflow.relative_to(root)} uses unpinned action {value}",
                    )
                )

    prepare_release = workflows_root / "prepare-release.yml"
    if prepare_release.is_file():
        declarations = DEFAULT_BRANCH_ENV_PATTERN.findall(
            prepare_release.read_text(encoding="utf-8")
        )
        expected_lines = [
            line
            for line in prepare_release.read_text(encoding="utf-8").splitlines()
            if "DEFAULT_BRANCH:" in line
        ]
        if len(declarations) != 2 or any(
            line.split("DEFAULT_BRANCH:", 1)[1].strip() != expected_default_branch
            for line in expected_lines
        ):
            findings.append(
                DoctorFinding(
                    "local",
                    "workflow-default-branch-mismatch",
                    "prepare-release workflow default branch does not match GitHub",
                )
            )
    return tuple(findings)
