from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path, PurePosixPath

from .common import LifecycleError, load_json_mapping


def load_manifest(path: Path) -> tuple[str, ...]:
    raw = load_json_mapping(path, "automation manifest")
    if set(raw) != {"schema_version", "files"}:
        raise LifecycleError("automation manifest must contain only schema_version and files")
    if raw["schema_version"] != 1:
        raise LifecycleError("automation manifest schema_version must be 1")
    files = raw["files"]
    if not isinstance(files, list) or not files:
        raise LifecycleError("automation manifest files must be a non-empty array")
    normalized: list[str] = []
    for item in files:
        if not isinstance(item, str) or not item:
            raise LifecycleError("automation manifest file entries must be non-empty strings")
        path_value = PurePosixPath(item)
        if path_value.is_absolute() or ".." in path_value.parts or str(path_value) != item:
            raise LifecycleError(f"automation manifest contains unsafe path: {item}")
        normalized.append(item)
    if len(normalized) != len(set(normalized)):
        raise LifecycleError("automation manifest must not contain duplicate files")
    return tuple(sorted(normalized))


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
