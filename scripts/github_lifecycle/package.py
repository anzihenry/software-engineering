from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path, PurePosixPath

from .common import LifecycleError, load_json_mapping


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


def load_manifest(path: Path) -> tuple[str, ...]:
    raw = load_json_mapping(path, "automation manifest")
    schema_version = raw.get("schema_version")
    if schema_version == 1:
        if set(raw) != {"schema_version", "files"}:
            raise LifecycleError(
                "automation manifest schema 1 must contain only schema_version and files"
            )
        return _normalize_files(raw["files"], context="files")
    if schema_version != 2:
        raise LifecycleError("automation manifest schema_version must be 1 or 2")
    if set(raw) != {"schema_version", "components"}:
        raise LifecycleError(
            "automation manifest schema 2 must contain only schema_version and components"
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


def package_bundle(root: Path, manifest: Path, output: Path) -> str:
    root = root.resolve()
    if output.exists() or output.with_suffix(output.suffix + ".sha256").exists():
        raise LifecycleError(f"package output already exists: {output}")
    files = load_manifest(manifest)
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


def render_package_result(output: Path, digest: str) -> str:
    return json.dumps(
        {"archive": str(output), "sha256": digest}, ensure_ascii=False, sort_keys=True
    )
