"""Compatibility facade for cross-project GitHub repository governance."""

from .github import Gh, GhClient
from .repository_bootstrap import (
    LABEL_PRESENTATION,
    BootstrapAction,
    BootstrapPlan,
    apply_bootstrap,
    build_bootstrap_plan,
    render_bootstrap_plan,
)
from .repository_inspection import inspect_remote_repository, render_findings
from .repository_ruleset import MANAGED_RULE_TYPES, RULESET_NAME
from .repository_state import CheckEvidence, RepositorySnapshot, discover_repository

__all__ = [
    "BootstrapAction",
    "BootstrapPlan",
    "CheckEvidence",
    "Gh",
    "GhClient",
    "LABEL_PRESENTATION",
    "MANAGED_RULE_TYPES",
    "RepositorySnapshot",
    "RULESET_NAME",
    "apply_bootstrap",
    "build_bootstrap_plan",
    "discover_repository",
    "inspect_remote_repository",
    "render_bootstrap_plan",
    "render_findings",
]
