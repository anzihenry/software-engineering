from __future__ import annotations

import json
import shutil
import subprocess
from collections.abc import Mapping, Sequence
from typing import Protocol

from .common import LifecycleError


class Gh(Protocol):
    def json(self, arguments: Sequence[str]) -> object: ...

    def execute(self, arguments: Sequence[str], input_text: str | None = None) -> str: ...


class GhClient:
    def __init__(self, *, timeout_seconds: int = 30) -> None:
        if shutil.which("gh") is None:
            raise LifecycleError("GitHub CLI (gh) is required")
        self.timeout_seconds = timeout_seconds

    def execute(self, arguments: Sequence[str], input_text: str | None = None) -> str:
        try:
            result = subprocess.run(
                ["gh", *arguments],
                input=input_text,
                text=True,
                capture_output=True,
                check=False,
                timeout=self.timeout_seconds,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise LifecycleError(f"cannot execute gh: {error}") from error
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or "unknown gh error"
            raise LifecycleError(f"gh command failed: {detail}")
        return result.stdout

    def json(self, arguments: Sequence[str]) -> object:
        output = self.execute(arguments)
        try:
            return json.loads(output)
        except json.JSONDecodeError as error:
            raise LifecycleError(f"gh returned invalid JSON: {error}") from error


def json_mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise LifecycleError(f"{label} must be a JSON object")
    return value


def json_array(value: object, label: str) -> Sequence[object]:
    if not isinstance(value, list):
        raise LifecycleError(f"{label} must be a JSON array")
    if value and all(isinstance(page, list) for page in value):
        return tuple(item for page in value for item in page)
    return value
