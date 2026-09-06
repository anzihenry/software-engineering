from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .common import LifecycleError, load_json_mapping, require_string
from .package import validate_profile

INSTALLATION_RECORD_PATH = ".github/lifecycle-installation.json"
INSTALLATION_RECORD_KEYS = {
    "schema_version",
    "repository",
    "default_branch",
    "profile",
    "adapter",
    "source_ref",
    "manifest_schema_version",
    "files",
}
SOURCE_REF_PATTERN = re.compile(
    r"(?:v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)|"
    r"[0-9a-f]{40}|sha256:[0-9a-f]{64})"
)
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class InstallationRecord:
    repository: str
    default_branch: str
    profile: str
    adapter: str
    source_ref: str
    manifest_schema_version: int
    files: Mapping[str, str]


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def content_source_ref(files: Sequence[tuple[str, bytes]]) -> str:
    paths = [path for path, _ in files]
    if len(paths) != len(set(paths)):
        raise LifecycleError("installation source contains duplicate file paths")
    digest = hashlib.sha256()
    for relative, content in sorted(files):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(content).digest())
    return f"sha256:{digest.hexdigest()}"


def validate_source_ref(value: str) -> str:
    if SOURCE_REF_PATTERN.fullmatch(value) is None:
        raise LifecycleError(
            "source_ref must be vMAJOR.MINOR.PATCH, a full lowercase commit SHA, "
            "or sha256:<64 lowercase hex>"
        )
    return value


def _safe_record_path(value: object) -> str:
    path = require_string(value, "installation record file path")
    pure_path = PurePosixPath(path)
    if (
        pure_path.is_absolute()
        or ".." in pure_path.parts
        or str(pure_path) != path
        or path == INSTALLATION_RECORD_PATH
    ):
        raise LifecycleError(f"installation record contains unsafe file path: {path}")
    return path


def build_installation_record(
    *,
    repository: str,
    default_branch: str,
    profile: str,
    adapter: str,
    source_ref: str | None,
    manifest_schema_version: int,
    files: Sequence[tuple[str, bytes]],
) -> InstallationRecord:
    if manifest_schema_version not in {1, 2, 3}:
        raise LifecycleError("installation record manifest_schema_version must be 1, 2, or 3")
    resolved_ref = validate_source_ref(source_ref) if source_ref else content_source_ref(files)
    hashes = {path: sha256_bytes(content) for path, content in files}
    if len(hashes) != len(files):
        raise LifecycleError("installation record files must not contain duplicate paths")
    return InstallationRecord(
        repository=require_string(repository, "repository"),
        default_branch=require_string(default_branch, "default_branch"),
        profile=validate_profile(profile),
        adapter=require_string(adapter, "adapter"),
        source_ref=resolved_ref,
        manifest_schema_version=manifest_schema_version,
        files=dict(sorted(hashes.items())),
    )


def render_installation_record(record: InstallationRecord) -> bytes:
    return (
        json.dumps(
            {
                "schema_version": 1,
                "repository": record.repository,
                "default_branch": record.default_branch,
                "profile": record.profile,
                "adapter": record.adapter,
                "source_ref": record.source_ref,
                "manifest_schema_version": record.manifest_schema_version,
                "files": dict(record.files),
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode()


def parse_installation_record(raw: Mapping[str, object]) -> InstallationRecord:
    if set(raw) != INSTALLATION_RECORD_KEYS:
        raise LifecycleError(
            "installation record must contain only: " + ", ".join(sorted(INSTALLATION_RECORD_KEYS))
        )
    if raw["schema_version"] != 1:
        raise LifecycleError("installation record schema_version must be 1")
    manifest_schema = raw["manifest_schema_version"]
    if not isinstance(manifest_schema, int) or manifest_schema not in {1, 2, 3}:
        raise LifecycleError("installation record manifest_schema_version must be 1, 2, or 3")
    raw_files = raw["files"]
    if not isinstance(raw_files, Mapping) or not raw_files:
        raise LifecycleError("installation record files must be a non-empty object")
    files: dict[str, str] = {}
    for raw_path, raw_digest in raw_files.items():
        path = _safe_record_path(raw_path)
        if not isinstance(raw_digest, str) or SHA256_PATTERN.fullmatch(raw_digest) is None:
            raise LifecycleError(f"installation record contains invalid SHA-256 for {path}")
        files[path] = raw_digest
    if len(files) != len(raw_files):
        raise LifecycleError("installation record files must not contain duplicate paths")
    return InstallationRecord(
        repository=require_string(raw["repository"], "installation record repository"),
        default_branch=require_string(raw["default_branch"], "installation record default_branch"),
        profile=validate_profile(require_string(raw["profile"], "installation record profile")),
        adapter=require_string(raw["adapter"], "installation record adapter"),
        source_ref=validate_source_ref(
            require_string(raw["source_ref"], "installation record source_ref")
        ),
        manifest_schema_version=manifest_schema,
        files=dict(sorted(files.items())),
    )


def load_installation_record(path: Path) -> InstallationRecord:
    return parse_installation_record(load_json_mapping(path, "installation record"))
