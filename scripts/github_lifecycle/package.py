from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path, PurePosixPath

from .common import LifecycleError, load_json_mapping

SUPPORTED_PROFILES = ("governance", "incident", "release", "full")
PACKAGE_PROFILES = ("auto", *SUPPORTED_PROFILES)


def _normalize_files(files: object, *, context: str) -> tuple[str, ...]:
    if not isinstance(files, list) or not files:
        raise LifecycleError(f"automation manifest {context} must be a non-empty array")
    normalized: list[str] = []
    for item in files:
        if not isinstance(item, str) or not item:
            raise LifecycleError("automation manifest file entries must be non-empty strings")
        path_value = PurePosixPath(item)
        if path_value.is_absolute() or ".." in path_value.parts or str(path_value) != item:
            raise LifecycleError(f"automation manifest contains unsafe path: {item}")
        normalized.append(item)
    if len(normalized) != len(set(normalized)):
        raise LifecycleError(f"automation manifest {context} must not contain duplicate files")
    return tuple(sorted(normalized))


def validate_profile(profile: str) -> str:
    if profile not in SUPPORTED_PROFILES:
        raise LifecycleError("automation profile must be one of: " + ", ".join(SUPPORTED_PROFILES))
    return profile


def _load_components(raw: dict[str, object], *, schema_version: int) -> tuple[str, ...]:
    expected_keys = {"schema_version", "components"}
    if schema_version == 3:
        expected_keys.add("profiles")
    if set(raw) != expected_keys:
        raise LifecycleError(
            f"automation manifest schema {schema_version} must contain only "
            + ", ".join(sorted(expected_keys))
        )
    components = raw["components"]
    if not isinstance(components, dict) or not components:
        raise LifecycleError("automation manifest components must be a non-empty object")
    combined: list[str] = []
    for name, files in components.items():
        if not isinstance(name, str) or not name:
            raise LifecycleError("automation manifest component names must be non-empty strings")
        combined.extend(_normalize_files(files, context=f"component {name!r}"))
    if len(combined) != len(set(combined)):
        raise LifecycleError("automation manifest files must not appear in multiple components")
    return tuple(sorted(combined))


def load_manifest(path: Path, *, profile: str = "full") -> tuple[str, ...]:
    profile = validate_profile(profile)
    raw = load_json_mapping(path, "automation manifest")
    schema_version = raw.get("schema_version")
    if schema_version == 1:
        if set(raw) != {"schema_version", "files"}:
            raise LifecycleError(
                "automation manifest schema 1 must contain only schema_version and files"
            )
        if profile != "full":
            raise LifecycleError("automation manifest schema 1 only supports the full profile")
        return _normalize_files(raw["files"], context="files")
    if schema_version == 2:
        files = _load_components(raw, schema_version=2)
        if profile != "full":
            raise LifecycleError("automation manifest schema 2 only supports the full profile")
        return files
    if schema_version != 3:
        raise LifecycleError("automation manifest schema_version must be 1, 2, or 3")

    all_files = _load_components(raw, schema_version=3)
    profiles = raw["profiles"]
    if not isinstance(profiles, dict) or set(profiles) != set(SUPPORTED_PROFILES):
        raise LifecycleError(
            "automation manifest profiles must equal: " + ", ".join(SUPPORTED_PROFILES)
        )
    normalized_profiles = {
        name: _normalize_files(files, context=f"profile {name!r}")
        for name, files in profiles.items()
    }
    for name, files in normalized_profiles.items():
        unknown = sorted(set(files) - set(all_files))
        if unknown:
            raise LifecycleError(
                f"automation manifest profile {name!r} contains files outside components: "
                + ", ".join(unknown)
            )
    if normalized_profiles["full"] != all_files:
        raise LifecycleError("automation manifest full profile must contain every component file")
    return normalized_profiles[profile]


def detect_installed_profile(root: Path, manifest: Path) -> str:
    root = root.resolve(strict=True)
    manifest = manifest if manifest.is_absolute() else root / manifest
    all_files = set(load_manifest(manifest, profile="full"))
    present_files = {
        relative
        for relative in all_files
        if (root / relative).is_file() and not (root / relative).is_symlink()
    }
    for profile in ("full", "release", "incident", "governance"):
        try:
            files = load_manifest(manifest, profile=profile)
        except LifecycleError:
            if profile == "full":
                raise
            continue
        if set(files).issubset(present_files):
            unexpected = sorted(present_files - set(files))
            if unexpected:
                raise LifecycleError(
                    "cannot auto-detect a profile from a partial or mixed installation; "
                    "unexpected installed assets: " + ", ".join(unexpected)
                )
            return profile
    raise LifecycleError("cannot detect a complete installed automation profile")


def package_bundle(root: Path, manifest: Path, output: Path, *, profile: str = "full") -> str:
    root = root.resolve()
    manifest = manifest if manifest.is_absolute() else root / manifest
    if output.exists() or output.with_suffix(output.suffix + ".sha256").exists():
        raise LifecycleError(f"package output already exists: {output}")
    files = load_manifest(manifest, profile=profile)
    resolved_files: list[tuple[str, Path]] = []
    for relative in files:
        source = root / relative
        if source.is_symlink():
            raise LifecycleError(f"automation bundle does not allow symlinks: {relative}")
        try:
            resolved = source.resolve(strict=True)
        except OSError as error:
            raise LifecycleError(
                f"cannot resolve automation bundle file {relative}: {error}"
            ) from error
        if not resolved.is_relative_to(root) or not resolved.is_file():
            raise LifecycleError(f"automation bundle file is outside the root: {relative}")
        resolved_files.append((relative, resolved))

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative, source in resolved_files:
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes())

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    checksum = output.with_suffix(output.suffix + ".sha256")
    checksum.write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    return digest


def render_package_result(output: Path, digest: str, *, profile: str = "full") -> str:
    return json.dumps(
        {"archive": str(output), "profile": profile, "sha256": digest},
        ensure_ascii=False,
        sort_keys=True,
    )
