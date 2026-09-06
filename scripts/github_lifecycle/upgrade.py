from __future__ import annotations

import json
import os
import stat
import tempfile
import zipfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .adoption import _safe_destination, rendered_files
from .common import LifecycleError
from .installation import (
    INSTALLATION_RECORD_PATH,
    InstallationRecord,
    build_installation_record,
    load_installation_record,
    render_installation_record,
    sha256_bytes,
    validate_source_ref,
)
from .package import detect_installed_profile, load_manifest_schema, validate_profile

MAX_PACKAGE_FILES = 512
MAX_PACKAGE_UNCOMPRESSED_BYTES = 50 * 1024 * 1024
BLOCKING_ACTIONS = frozenset({"conflict", "local-modification"})


@dataclass(frozen=True)
class UpgradeEntry:
    path: str
    action: str
    expected_sha256: str | None
    desired_sha256: str | None


@dataclass(frozen=True)
class UpgradePlan:
    repository: str
    default_branch: str
    from_profile: str
    profile: str
    adapter: str
    from_ref: str
    to_ref: str
    target: Path
    entries: tuple[UpgradeEntry, ...]

    @property
    def blockers(self) -> tuple[str, ...]:
        return tuple(entry.path for entry in self.entries if entry.action in BLOCKING_ACTIONS)

    @property
    def confirmation(self) -> str:
        return f"upgrade:{self.repository}:{self.from_ref}:{self.to_ref}"


def _safe_archive_path(value: str) -> str:
    path = PurePosixPath(value)
    if not value or "\\" in value or path.is_absolute() or ".." in path.parts or str(path) != value:
        raise LifecycleError(f"upgrade package contains unsafe path: {value}")
    return value


@contextmanager
def materialize_package(package: Path) -> Iterator[Path]:
    try:
        package = package.resolve(strict=True)
    except OSError as error:
        raise LifecycleError(f"cannot resolve upgrade package: {error}") from error
    if package.is_dir():
        yield package
        return
    if not package.is_file() or not zipfile.is_zipfile(package):
        raise LifecycleError("upgrade package must be a directory or ZIP archive")

    with tempfile.TemporaryDirectory(prefix="github-lifecycle-upgrade-") as directory:
        root = Path(directory)
        try:
            with zipfile.ZipFile(package) as archive:
                entries = archive.infolist()
                if len(entries) > MAX_PACKAGE_FILES:
                    raise LifecycleError("upgrade package contains too many files")
                if sum(entry.file_size for entry in entries) > MAX_PACKAGE_UNCOMPRESSED_BYTES:
                    raise LifecycleError("upgrade package is too large when uncompressed")
                seen: set[str] = set()
                for entry in entries:
                    relative = _safe_archive_path(entry.filename)
                    if relative in seen:
                        raise LifecycleError(f"upgrade package contains duplicate path: {relative}")
                    seen.add(relative)
                    mode = entry.external_attr >> 16
                    if entry.flag_bits & 0x1:
                        raise LifecycleError("upgrade package must not contain encrypted files")
                    if stat.S_ISLNK(mode):
                        raise LifecycleError(
                            f"upgrade package must not contain symlinks: {relative}"
                        )
                    if entry.is_dir():
                        (root / relative).mkdir(parents=True, exist_ok=True)
                        continue
                    destination = root / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(archive.read(entry))
        except (OSError, zipfile.BadZipFile, RuntimeError) as error:
            raise LifecycleError(f"cannot read upgrade package: {error}") from error
        yield root


def _adapter_name(files: tuple[tuple[str, bytes], ...]) -> str:
    for relative, content in files:
        if relative != ".github/lifecycle-adapter.json":
            continue
        try:
            raw = json.loads(content.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as error:
            raise LifecycleError(f"cannot identify rendered adapter: {error}") from error
        if not isinstance(raw, dict) or not isinstance(raw.get("name"), str):
            raise LifecycleError("rendered adapter configuration has no name")
        return raw["name"]
    return "external"


def _record_for_source(
    root: Path,
    manifest: Path,
    target: Path,
    *,
    repository: str,
    default_branch: str,
    profile: str,
    source_ref: str,
) -> tuple[InstallationRecord, tuple[tuple[str, bytes], ...]]:
    rendered = rendered_files(
        root,
        manifest,
        repository=repository,
        default_branch=default_branch,
        profile=profile,
        adapter="auto",
        target=target,
    )
    manifest_path = manifest if manifest.is_absolute() else root / manifest
    record = build_installation_record(
        repository=repository,
        default_branch=default_branch,
        profile=profile,
        adapter=_adapter_name(rendered),
        source_ref=source_ref,
        manifest_schema_version=load_manifest_schema(manifest_path),
        files=rendered,
    )
    return record, rendered


def _load_existing_record(target: Path) -> InstallationRecord | None:
    path = target / INSTALLATION_RECORD_PATH
    if path.is_symlink():
        raise LifecycleError("installation record must not be a symlink")
    if not path.exists():
        return None
    if not path.is_file():
        raise LifecycleError("installation record must be a regular file")
    return load_installation_record(path)


def _validate_record_identity(
    record: InstallationRecord,
    *,
    repository: str,
    default_branch: str,
    adapter: str,
) -> None:
    mismatches = []
    if record.repository != repository:
        mismatches.append("repository")
    if record.default_branch != default_branch:
        mismatches.append("default_branch")
    if record.adapter != adapter:
        mismatches.append("adapter")
    if mismatches:
        raise LifecycleError(
            "installation record does not match the upgrade request: " + ", ".join(mismatches)
        )


def _classify_entry(
    target: Path,
    relative: str,
    old_sha256: str | None,
    new_sha256: str | None,
) -> UpgradeEntry:
    try:
        destination = _safe_destination(target, relative)
    except LifecycleError:
        return UpgradeEntry(relative, "conflict", old_sha256, new_sha256)
    if new_sha256 is None:
        return UpgradeEntry(relative, "removed-upstream", old_sha256, None)
    if destination.is_symlink() or (destination.exists() and not destination.is_file()):
        return UpgradeEntry(relative, "conflict", old_sha256, new_sha256)
    if not destination.exists():
        action = "create" if old_sha256 is None else "conflict"
        return UpgradeEntry(relative, action, old_sha256, new_sha256)
    current_sha256 = sha256_bytes(destination.read_bytes())
    if current_sha256 == new_sha256:
        return UpgradeEntry(relative, "unchanged", current_sha256, new_sha256)
    if old_sha256 is None:
        return UpgradeEntry(relative, "conflict", current_sha256, new_sha256)
    if current_sha256 != old_sha256:
        return UpgradeEntry(relative, "local-modification", old_sha256, new_sha256)
    return UpgradeEntry(relative, "safe-update", current_sha256, new_sha256)


def plan_upgrade(
    from_root: Path,
    to_root: Path,
    target: Path,
    *,
    repository: str,
    default_branch: str,
    from_ref: str,
    to_ref: str,
    profile: str,
    from_profile: str | None = None,
    manifest: Path = Path("automation/github-lifecycle-manifest.json"),
) -> tuple[UpgradePlan, tuple[tuple[str, bytes], ...]]:
    from_ref = validate_source_ref(from_ref)
    to_ref = validate_source_ref(to_ref)
    profile = validate_profile(profile)
    target = target.resolve(strict=True)
    if not target.is_dir():
        raise LifecycleError("upgrade target must be an existing directory")
    existing = _load_existing_record(target)
    if from_profile is None:
        from_profile = (
            existing.profile
            if existing is not None
            else detect_installed_profile(target, target / manifest)
        )
    from_profile = validate_profile(from_profile)
    old_record, _ = _record_for_source(
        from_root.resolve(strict=True),
        manifest,
        target,
        repository=repository,
        default_branch=default_branch,
        profile=from_profile,
        source_ref=from_ref,
    )
    new_record, new_rendered = _record_for_source(
        to_root.resolve(strict=True),
        manifest,
        target,
        repository=repository,
        default_branch=default_branch,
        profile=profile,
        source_ref=to_ref,
    )
    if old_record.adapter != new_record.adapter:
        raise LifecycleError("upgrade does not change the installed language adapter")

    baseline = old_record
    if existing is not None:
        _validate_record_identity(
            existing,
            repository=repository,
            default_branch=default_branch,
            adapter=old_record.adapter,
        )
        if (existing.profile == profile and dict(existing.files) == dict(new_record.files)) or (
            existing.profile == from_profile and dict(existing.files) == dict(old_record.files)
        ):
            baseline = existing
        else:
            raise LifecycleError(
                "installation record does not match the supplied old or new package"
            )

    entries = [
        _classify_entry(
            target,
            relative,
            baseline.files.get(relative),
            new_record.files.get(relative),
        )
        for relative in sorted(set(baseline.files) | set(new_record.files))
    ]
    record_content = render_installation_record(new_record)
    record_path = target / INSTALLATION_RECORD_PATH
    if record_path.exists():
        current_record_sha = sha256_bytes(record_path.read_bytes())
        desired_record_sha = sha256_bytes(record_content)
        record_action = "unchanged" if current_record_sha == desired_record_sha else "safe-update"
        entries.append(
            UpgradeEntry(
                INSTALLATION_RECORD_PATH,
                record_action,
                current_record_sha,
                desired_record_sha,
            )
        )
    else:
        entries.append(
            UpgradeEntry(
                INSTALLATION_RECORD_PATH,
                "create",
                None,
                sha256_bytes(record_content),
            )
        )
    desired_files = (*new_rendered, (INSTALLATION_RECORD_PATH, record_content))
    return (
        UpgradePlan(
            repository=repository,
            default_branch=default_branch,
            from_profile=from_profile,
            profile=profile,
            adapter=new_record.adapter,
            from_ref=from_ref,
            to_ref=to_ref,
            target=target,
            entries=tuple(entries),
        ),
        desired_files,
    )


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _preflight_upgrade(plan: UpgradePlan, desired: dict[str, bytes]) -> None:
    for entry in plan.entries:
        if entry.action == "removed-upstream":
            continue
        if entry.path not in desired:
            raise LifecycleError(f"upgrade desired content is missing: {entry.path}")
        destination = _safe_destination(plan.target, entry.path)
        if destination.is_symlink() or (destination.exists() and not destination.is_file()):
            raise LifecycleError(f"upgrade destination changed after planning: {entry.path}")
        if entry.action == "create":
            if destination.exists():
                raise LifecycleError(f"upgrade destination changed after planning: {entry.path}")
            continue
        if not destination.is_file() or entry.expected_sha256 is None:
            raise LifecycleError(f"upgrade destination changed after planning: {entry.path}")
        if sha256_bytes(destination.read_bytes()) != entry.expected_sha256:
            raise LifecycleError(f"upgrade destination changed after planning: {entry.path}")


def apply_upgrade(
    plan: UpgradePlan,
    files: tuple[tuple[str, bytes], ...],
    *,
    confirmation: str,
) -> None:
    if confirmation != plan.confirmation:
        raise LifecycleError(f"upgrade confirmation must exactly match {plan.confirmation}")
    if plan.blockers:
        raise LifecycleError("upgrade refuses unresolved files: " + ", ".join(plan.blockers))
    desired = dict(files)
    if len(desired) != len(files):
        raise LifecycleError("upgrade desired files must not contain duplicate paths")
    _preflight_upgrade(plan, desired)

    writable_entries = [
        entry for entry in plan.entries if entry.action in {"create", "safe-update"}
    ]
    originals: dict[str, bytes | None] = {}
    try:
        for entry in writable_entries:
            destination = _safe_destination(plan.target, entry.path)
            originals[entry.path] = destination.read_bytes() if destination.exists() else None
            _atomic_write(destination, desired[entry.path])
    except (LifecycleError, OSError) as error:
        rollback_errors = []
        for relative, original in reversed(tuple(originals.items())):
            try:
                destination = _safe_destination(plan.target, relative)
                if original is None:
                    destination.unlink(missing_ok=True)
                else:
                    _atomic_write(destination, original)
            except (LifecycleError, OSError) as rollback_error:
                rollback_errors.append(f"{relative}: {rollback_error}")
        detail = f"upgrade write failed and was rolled back: {error}"
        if rollback_errors:
            detail += "; rollback failures: " + "; ".join(rollback_errors)
        raise LifecycleError(detail) from error


def render_upgrade_plan(plan: UpgradePlan, *, dry_run: bool) -> str:
    actions = (
        "create",
        "safe-update",
        "unchanged",
        "local-modification",
        "removed-upstream",
        "conflict",
    )
    return json.dumps(
        {
            "schema_version": 1,
            "mode": "dry-run" if dry_run else "apply",
            "repository": plan.repository,
            "default_branch": plan.default_branch,
            "from_profile": plan.from_profile,
            "profile": plan.profile,
            "adapter": plan.adapter,
            "from_ref": plan.from_ref,
            "to_ref": plan.to_ref,
            "confirmation": plan.confirmation,
            "target": str(plan.target),
            "counts": {
                action: sum(entry.action == action for entry in plan.entries) for action in actions
            },
            "entries": [
                {
                    "path": entry.path,
                    "action": entry.action,
                    "expected_sha256": entry.expected_sha256,
                    "desired_sha256": entry.desired_sha256,
                }
                for entry in plan.entries
            ],
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
