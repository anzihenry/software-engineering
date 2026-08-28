from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .common import LifecycleError, load_json_mapping, require_string, require_unique_strings

SUPPORTED_ADAPTERS = ("auto", "external", "python", "node", "swift", "go", "custom")
MANAGED_ADAPTER_FILES = (
    ".github/dependabot.yml",
    ".github/lifecycle-adapter.json",
    ".github/workflows/validate.yml",
)
ADAPTER_KEYS = {
    "schema_version",
    "name",
    "runner",
    "toolchain",
    "required_files",
    "check_commands",
    "dependabot_ecosystems",
    "release_artifact_retention_days",
}
TOOLCHAIN_KEYS = {"kind", "version", "version_file"}
TOOLCHAIN_KINDS = {"python", "node", "swift", "go"}
DEPENDABOT_ECOSYSTEMS = {"pip", "npm", "swift", "gomod", "github-actions"}
YAML_SCALAR_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$")


@dataclass(frozen=True)
class LanguageAdapter:
    name: str
    runner: str
    toolchain_kind: str
    toolchain_version: str | None
    toolchain_version_file: str | None
    required_files: tuple[str, ...]
    check_commands: tuple[tuple[str, ...], ...]
    dependabot_ecosystems: tuple[str, ...]
    release_artifact_retention_days: int


def _safe_relative_path(value: object, field: str) -> str:
    path = require_string(value, field)
    pure_path = PurePosixPath(path)
    if pure_path.is_absolute() or ".." in pure_path.parts or str(pure_path) != path:
        raise LifecycleError(f"{field} must be a safe repository-relative path")
    return path


def _load_commands(value: object) -> tuple[tuple[str, ...], ...]:
    if not isinstance(value, list) or not value:
        raise LifecycleError("check_commands must be a non-empty array")
    commands: list[tuple[str, ...]] = []
    for index, command in enumerate(value):
        if not isinstance(command, list) or not command:
            raise LifecycleError(f"check_commands[{index}] must be a non-empty array")
        arguments = tuple(
            require_string(argument, f"check_commands[{index}] argument") for argument in command
        )
        if any("\0" in argument or "\n" in argument or "\r" in argument for argument in arguments):
            raise LifecycleError("check command arguments must not contain control characters")
        commands.append(arguments)
    return tuple(commands)


def parse_adapter(raw: Mapping[str, object], *, name: str | None = None) -> LanguageAdapter:
    unknown = set(raw) - ADAPTER_KEYS
    required = ADAPTER_KEYS - {"name"}
    missing = required - set(raw)
    if unknown:
        raise LifecycleError(f"adapter contains unknown keys: {', '.join(sorted(unknown))}")
    if missing:
        raise LifecycleError(f"adapter is missing keys: {', '.join(sorted(missing))}")
    if raw["schema_version"] != 1:
        raise LifecycleError("adapter schema_version must be 1")

    adapter_name = name or require_string(raw.get("name"), "name")
    toolchain = raw["toolchain"]
    if not isinstance(toolchain, Mapping) or not set(toolchain).issubset(TOOLCHAIN_KEYS):
        raise LifecycleError("toolchain must contain only kind, version, and version_file")
    kind = require_string(toolchain.get("kind"), "toolchain.kind")
    if kind not in TOOLCHAIN_KINDS:
        raise LifecycleError("toolchain.kind must be python, node, swift, or go")
    version = toolchain.get("version")
    version_file = toolchain.get("version_file")
    if version is not None:
        version = require_string(version, "toolchain.version")
    if version_file is not None:
        version_file = _safe_relative_path(version_file, "toolchain.version_file")
    if version is not None and version_file is not None:
        raise LifecycleError("toolchain must not define both version and version_file")
    if version is not None and YAML_SCALAR_PATTERN.fullmatch(version) is None:
        raise LifecycleError("toolchain.version contains unsafe characters")
    if kind in {"python", "node", "go"} and version is None and version_file is None:
        raise LifecycleError(f"{kind} toolchain requires version or version_file")
    if kind == "swift" and (version is not None or version_file is not None):
        raise LifecycleError("swift toolchain version is selected by the runner image")

    required_files = tuple(
        _safe_relative_path(item, "required_files item")
        for item in require_unique_strings(raw["required_files"], "required_files")
    )
    ecosystems = require_unique_strings(raw["dependabot_ecosystems"], "dependabot_ecosystems")
    if set(ecosystems) - DEPENDABOT_ECOSYSTEMS:
        raise LifecycleError("adapter contains an unsupported Dependabot ecosystem")
    if "github-actions" not in ecosystems:
        raise LifecycleError("adapter must include the github-actions Dependabot ecosystem")
    retention = raw["release_artifact_retention_days"]
    if not isinstance(retention, int) or isinstance(retention, bool) or not 1 <= retention <= 90:
        raise LifecycleError("release_artifact_retention_days must be between 1 and 90")

    runner = require_string(raw["runner"], "runner")
    if YAML_SCALAR_PATTERN.fullmatch(runner) is None:
        raise LifecycleError("runner contains unsafe characters")

    return LanguageAdapter(
        name=adapter_name,
        runner=runner,
        toolchain_kind=kind,
        toolchain_version=version,
        toolchain_version_file=version_file,
        required_files=required_files,
        check_commands=_load_commands(raw["check_commands"]),
        dependabot_ecosystems=ecosystems,
        release_artifact_retention_days=retention,
    )


def load_adapter_catalog(path: Path) -> Mapping[str, object]:
    raw = load_json_mapping(path, "language adapter catalog")
    if set(raw) != {"schema_version", "adapters"} or raw["schema_version"] != 1:
        raise LifecycleError("language adapter catalog must use schema 1")
    adapters = raw["adapters"]
    if not isinstance(adapters, Mapping) or set(adapters) != {"python", "node", "swift", "go"}:
        raise LifecycleError("language adapter catalog must define python, node, swift, and go")
    return adapters


def load_adapter(path: Path, *, name: str | None = None) -> LanguageAdapter:
    return parse_adapter(load_json_mapping(path, "language adapter"), name=name)


def select_adapter(
    source_root: Path,
    target: Path,
    selection: str,
    custom_config: Path | None = None,
) -> LanguageAdapter | None:
    if selection not in SUPPORTED_ADAPTERS:
        raise LifecycleError("adapter must be one of: " + ", ".join(SUPPORTED_ADAPTERS))
    installed = target / ".github/lifecycle-adapter.json"
    if selection == "auto":
        return load_adapter(installed) if installed.is_file() else None
    if selection == "external":
        if custom_config is not None:
            raise LifecycleError("external adapter does not accept --adapter-config")
        return None
    if custom_config is not None:
        return load_adapter(custom_config)
    if selection == "custom":
        raise LifecycleError("custom adapter requires --adapter-config")
    catalog = load_adapter_catalog(source_root / "automation/github-lifecycle-adapters.json")
    raw_adapter = catalog[selection]
    if not isinstance(raw_adapter, Mapping):
        raise LifecycleError(f"catalog adapter {selection!r} must be an object")
    return parse_adapter({"schema_version": 1, **raw_adapter}, name=selection)


def render_adapter_config(adapter: LanguageAdapter) -> bytes:
    toolchain: dict[str, str] = {"kind": adapter.toolchain_kind}
    if adapter.toolchain_version is not None:
        toolchain["version"] = adapter.toolchain_version
    if adapter.toolchain_version_file is not None:
        toolchain["version_file"] = adapter.toolchain_version_file
    raw = {
        "schema_version": 1,
        "name": adapter.name,
        "runner": adapter.runner,
        "toolchain": toolchain,
        "required_files": list(adapter.required_files),
        "check_commands": [list(command) for command in adapter.check_commands],
        "dependabot_ecosystems": list(adapter.dependabot_ecosystems),
        "release_artifact_retention_days": adapter.release_artifact_retention_days,
    }
    return (json.dumps(raw, ensure_ascii=False, indent=2) + "\n").encode()


def render_dependabot(adapter: LanguageAdapter) -> bytes:
    lines = ["version: 2", "updates:"]
    for ecosystem in adapter.dependabot_ecosystems:
        lines.extend(
            [
                f'  - package-ecosystem: "{ecosystem}"',
                '    directory: "/"',
                "    schedule:",
                '      interval: "weekly"',
                '    rebase-strategy: "auto"',
            ]
        )
    return ("\n".join(lines) + "\n").encode()


def _toolchain_setup(adapter: LanguageAdapter) -> list[str]:
    if adapter.toolchain_kind in {"python", "swift"}:
        return []
    if adapter.toolchain_kind == "node":
        lines = [
            "      - name: Set up Node",
            "        uses: actions/setup-node@820762786026740c76f36085b0efc47a31fe5020 # v7.0.0",
            "        with:",
        ]
        key = "node-version" if adapter.toolchain_version is not None else "node-version-file"
        value = adapter.toolchain_version or adapter.toolchain_version_file
        return [*lines, f'          {key}: "{value}"']
    lines = [
        "      - name: Set up Go",
        "        uses: actions/setup-go@b7ad1dad31e06c5925ef5d2fc7ad053ef454303e # v7.0.0",
        "        with:",
    ]
    key = "go-version" if adapter.toolchain_version is not None else "go-version-file"
    value = adapter.toolchain_version or adapter.toolchain_version_file
    return [*lines, f'          {key}: "{value}"']


def render_validate_workflow(adapter: LanguageAdapter, default_branch: str) -> bytes:
    python_key = "python-version"
    python_value = "3.14"
    if adapter.toolchain_kind == "python":
        if adapter.toolchain_version is not None:
            python_value = adapter.toolchain_version
        else:
            python_key = "python-version-file"
            python_value = adapter.toolchain_version_file or ""
    lines = [
        "name: Validate",
        "",
        '"on":',
        "  pull_request:",
        "  push:",
        "    branches:",
        f"      - {default_branch}",
        "",
        "permissions: {}",
        "",
        "jobs:",
        "  validate:",
        f"    runs-on: {adapter.runner}",
        "    timeout-minutes: 30",
        "    permissions:",
        "      contents: read",
        "    steps:",
        "      - name: Check out repository",
        "        uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1",
        "",
        "      - name: Set up automation Python",
        "        uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0",
        "        with:",
        f'          {python_key}: "{python_value}"',
    ]
    setup = _toolchain_setup(adapter)
    if setup:
        lines.extend(["", *setup])
    lines.extend(
        [
            "",
            "      - name: Run project validation",
            "        run: python -m scripts.github_lifecycle run-adapter "
            "--config .github/lifecycle-adapter.json",
        ]
    )
    return ("\n".join(lines) + "\n").encode()


def render_managed_files(
    adapter: LanguageAdapter, default_branch: str
) -> tuple[tuple[str, bytes], ...]:
    return (
        (".github/dependabot.yml", render_dependabot(adapter)),
        (".github/lifecycle-adapter.json", render_adapter_config(adapter)),
        (".github/workflows/validate.yml", render_validate_workflow(adapter, default_branch)),
    )


def run_adapter(config: Path, root: Path) -> None:
    adapter = load_adapter(config)
    root = root.resolve(strict=True)
    missing = [path for path in adapter.required_files if not (root / path).exists()]
    if missing:
        raise LifecycleError("adapter required paths are missing: " + ", ".join(missing))
    for command in adapter.check_commands:
        completed = subprocess.run(command, cwd=root, check=False)
        if completed.returncode != 0:
            raise LifecycleError(
                f"adapter command failed with exit code {completed.returncode}: {command[0]}"
            )
