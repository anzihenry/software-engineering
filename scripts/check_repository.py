#!/usr/bin/env python3
"""Validate the playbook's skills, templates, exercises, links, YAML, and Markdown."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import unquote

import yaml

PHASES = {
    1: "01-demand-and-opportunity",
    2: "02-refinement-and-initiation",
    3: "03-solution-and-planning",
    4: "04-implementation-and-self-test",
    5: "05-integration-validation",
    6: "06-release-and-change-management",
    7: "07-operations-and-support",
    8: "08-measurement-and-retrospective",
}
TRACEABILITY_FIELDS = (
    "record_id",
    "record_type",
    "status",
    "owner",
    "decision_authority",
    "risk_level",
    "related_records",
    "source_version",
    "environment_scope",
    "evidence",
    "created_at",
    "updated_at",
)
TRACEABILITY_LABELS = {
    "record_id": "记录 ID",
    "record_type": "记录类型",
    "status": "状态",
    "owner": "所有者",
    "decision_authority": "决策权限",
    "risk_level": "风险等级",
    "related_records": "关联记录",
    "source_version": "源码/制品版本",
    "environment_scope": "环境与适用范围",
    "evidence": "证据",
    "created_at": "创建时间及时区",
    "updated_at": "更新时间及时区",
}
DELIVERY_TEMPLATES = {
    "opportunity-record.md": (1,),
    "requirements-risk-package.md": (2,),
    "solution-decision.md": (3,),
    "verification-matrix.md": (3, 4, 5),
    "change-handoff.md": (4, 5),
    "release-record.md": (6,),
    "incident-record.md": (7,),
    "outcome-retrospective-actions.md": (8,),
}
WORKFLOW_DELIVERY_TEMPLATES = {
    1: ("opportunity-record.md",),
    2: ("requirements-risk-package.md",),
    3: ("solution-decision.md", "verification-matrix.md"),
    4: ("change-handoff.md", "verification-matrix.md"),
    5: ("change-handoff.md", "verification-matrix.md"),
    6: ("release-record.md",),
    7: ("incident-record.md",),
    8: ("outcome-retrospective-actions.md",),
}
END_TO_END_EXERCISES = {
    "low-risk-copy-change.md": ("low", "copy-change"),
    "medium-risk-feature.md": ("medium", "feature"),
    "high-risk-data-permission-change.md": ("high", "data-permission-change"),
}
CONTENT_STATUSES = frozenset({"draft", "active", "deprecated"})
FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+\S")
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PINNED_ACTION_PATTERN = re.compile(r"^[^@\s]+@[0-9a-fA-F]{40}$")
PINNED_ACTION_LINE_PATTERN = re.compile(
    r"^\s*(?:-\s+)?uses:\s+[^@\s]+@[0-9a-fA-F]{40}\s+#\s+"
    r"v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\s*$"
)
AUTOMATION_COMPONENTS = frozenset({"github-lifecycle", "cross-project-governance"})
AUTOMATION_PROFILES = frozenset({"governance", "incident", "release", "full"})
KNOWLEDGE_ASSET_PREFIXES = (
    "skills/",
    "templates/delivery/",
    "docs/workflows/",
    "docs/exercises/",
)
INTERNAL_SUPPORT_ASSETS = frozenset(
    {
        ".github/dependabot.yml",
        ".github/workflows/repository-checks.yml",
        "bin/playbook",
        "requirements-dev.txt",
        "scripts/check_repository.py",
        "scripts/development.py",
    }
)
GOVERNANCE_COMMAND_PATTERN = re.compile(
    r"python(?:3)?\s+-m\s+scripts\.github_lifecycle\s+(?:install|doctor|bootstrap)(?:\s|\\|$)"
)


@dataclass(frozen=True, order=True)
class Issue:
    path: Path
    message: str
    line: int | None = None

    def render(self, root: Path) -> str:
        try:
            display_path = self.path.relative_to(root)
        except ValueError:
            display_path = self.path
        location = f"{display_path}:{self.line}" if self.line is not None else str(display_path)
        return f"{location}: {self.message}"


def repository_files(root: Path, pattern: str) -> list[Path]:
    return sorted(path for path in root.rglob(pattern) if ".git" not in path.parts)


def load_yaml(path: Path, issues: list[Issue]) -> object | None:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        issues.append(Issue(path, f"invalid YAML: {error}"))
        return None


def check_yaml(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    for path in repository_files(root, "*.yaml") + repository_files(root, "*.yml"):
        load_yaml(path, issues)
    return issues


def check_github_automation(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    root = root.resolve()
    github_root = root / ".github"
    workflows_root = github_root / "workflows"
    for path in sorted(workflows_root.glob("*.yml")) + sorted(workflows_root.glob("*.yaml")):
        workflow = load_yaml(path, issues)
        if not isinstance(workflow, dict):
            continue
        triggers = workflow.get("on")
        if triggers is None and True in workflow:
            issues.append(Issue(path, 'workflow trigger key "on" must be quoted'))
            triggers = workflow.get(True)
        if isinstance(triggers, dict) and "pull_request_target" in triggers:
            issues.append(Issue(path, "pull_request_target is not allowed"))
        if not isinstance(workflow.get("permissions"), dict):
            issues.append(Issue(path, "workflow must declare an explicit permissions mapping"))

        jobs = workflow.get("jobs")
        if not isinstance(jobs, dict):
            issues.append(Issue(path, "workflow must contain a jobs mapping"))
            continue
        for job_name, job in jobs.items():
            if not isinstance(job, dict):
                issues.append(Issue(path, f"workflow job {job_name!r} must be a mapping"))
                continue
            if not isinstance(job.get("permissions"), dict):
                issues.append(
                    Issue(path, f"workflow job {job_name!r} must declare explicit permissions")
                )
            action_values: list[object] = []
            if "uses" in job:
                action_values.append(job["uses"])
            steps = job.get("steps", [])
            if isinstance(steps, list):
                action_values.extend(
                    step["uses"] for step in steps if isinstance(step, dict) and "uses" in step
                )
            for uses in action_values:
                if not isinstance(uses, str) or (
                    not uses.startswith("./") and not PINNED_ACTION_PATTERN.fullmatch(uses)
                ):
                    issues.append(
                        Issue(
                            path,
                            f"workflow action must be local or pinned to a full SHA: {uses!r}",
                        )
                    )
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if (
                "uses:" in line
                and "@" in line
                and not line.split("uses:", maxsplit=1)[1].lstrip().startswith("./")
                and PINNED_ACTION_LINE_PATTERN.fullmatch(line) is None
            ):
                issues.append(
                    Issue(
                        path,
                        "pinned workflow action must include an exact vMAJOR.MINOR.PATCH comment",
                        line_number,
                    )
                )

    dependabot_path = github_root / "dependabot.yml"
    if not dependabot_path.is_file():
        issues.append(Issue(dependabot_path, "missing Dependabot configuration"))
    else:
        dependabot = load_yaml(dependabot_path, issues)
        if not isinstance(dependabot, dict) or dependabot.get("version") != 2:
            issues.append(Issue(dependabot_path, "Dependabot version must equal 2"))
        updates = dependabot.get("updates") if isinstance(dependabot, dict) else None
        if not isinstance(updates, list):
            issues.append(Issue(dependabot_path, "Dependabot updates must be an array"))
        else:
            ecosystems = {
                update.get("package-ecosystem"): update
                for update in updates
                if isinstance(update, dict) and isinstance(update.get("package-ecosystem"), str)
            }
            expected_ecosystems = {"pip", "github-actions"}
            if len(updates) != 2 or set(ecosystems) != expected_ecosystems:
                issues.append(
                    Issue(
                        dependabot_path,
                        "Dependabot must configure pip and github-actions exactly once",
                    )
                )
            for ecosystem in expected_ecosystems & set(ecosystems):
                update = ecosystems[ecosystem]
                schedule = update.get("schedule")
                if update.get("directory") != "/":
                    issues.append(
                        Issue(
                            dependabot_path,
                            f"Dependabot {ecosystem} directory must equal '/'",
                        )
                    )
                if not isinstance(schedule, dict) or schedule.get("interval") != "weekly":
                    issues.append(
                        Issue(
                            dependabot_path,
                            f"Dependabot {ecosystem} schedule must be weekly",
                        )
                    )
                if update.get("rebase-strategy") != "auto":
                    issues.append(
                        Issue(
                            dependabot_path,
                            f"Dependabot {ecosystem} rebase strategy must be auto",
                        )
                    )

    repository_workflow = workflows_root / "repository-checks.yml"
    if repository_workflow.is_file():
        workflow = load_yaml(repository_workflow, issues)
        jobs = workflow.get("jobs") if isinstance(workflow, dict) else None
        validate = jobs.get("validate") if isinstance(jobs, dict) else None
        steps = validate.get("steps") if isinstance(validate, dict) else None
        run_commands = (
            {step.get("run") for step in steps if isinstance(step, dict)}
            if isinstance(steps, list)
            else set()
        )
        if "python -m scripts.development check" not in run_commands:
            issues.append(
                Issue(
                    repository_workflow,
                    "validate job must use the canonical development check command",
                )
            )

    development_entry = root / "bin" / "playbook"
    development_module = root / "scripts" / "development.py"
    if not development_entry.is_file():
        issues.append(Issue(development_entry, "missing local development entry"))
    elif development_entry.stat().st_mode & 0o111 == 0:
        issues.append(Issue(development_entry, "local development entry must be executable"))
    if not development_module.is_file():
        issues.append(Issue(development_module, "missing development command module"))

    boundaries = root / "docs" / "project-boundaries.md"
    readme = root / "README.md"
    skill_navigation = root / "skills" / "README.md"
    lifecycle_documentation = root / "docs" / "software-development-lifecycle.md"
    automation_documentation = root / "docs" / "github-lifecycle-automation.md"
    for navigation in (
        readme,
        skill_navigation,
        lifecycle_documentation,
        automation_documentation,
    ):
        if not boundaries.is_file():
            issues.append(Issue(boundaries, "missing project boundary documentation"))
            break
        if navigation.is_file():
            links = {
                resolved
                for _, target in markdown_links(navigation)
                if (resolved := resolve_local_link(navigation, target)) is not None
            }
            if boundaries not in links:
                issues.append(Issue(navigation, "missing project boundary documentation link"))

    policy = github_root / "lifecycle-policy.json"
    manifest = root / "automation" / "github-lifecycle-manifest.json"
    adapter_catalog = root / "automation" / "github-lifecycle-adapters.json"
    pull_request_template = github_root / "PULL_REQUEST_TEMPLATE.md"
    documentation = automation_documentation
    security_policy = root / "SECURITY.md"
    incident_form = github_root / "ISSUE_TEMPLATE" / "incident.yml"
    improvement_form = github_root / "ISSUE_TEMPLATE" / "improvement-action.yml"
    retrospective_workflow = workflows_root / "open-retrospective.yml"
    audit_workflow = workflows_root / "audit-lifecycle-records.yml"
    for path in (
        policy,
        manifest,
        adapter_catalog,
        pull_request_template,
        documentation,
        security_policy,
        incident_form,
        improvement_form,
        retrospective_workflow,
        audit_workflow,
    ):
        if not path.is_file():
            issues.append(Issue(path, "missing GitHub lifecycle automation file"))

    if adapter_catalog.is_file():
        try:
            raw_catalog = json.loads(adapter_catalog.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            issues.append(Issue(adapter_catalog, f"invalid language adapter catalog JSON: {error}"))
        else:
            adapters = raw_catalog.get("adapters") if isinstance(raw_catalog, dict) else None
            if (
                not isinstance(raw_catalog, dict)
                or raw_catalog.get("schema_version") != 1
                or not isinstance(adapters, dict)
                or set(adapters) != {"python", "node", "swift", "go"}
            ):
                issues.append(
                    Issue(
                        adapter_catalog,
                        "language adapter catalog must use schema 1 and define "
                        "python, node, swift, and go",
                    )
                )

    if incident_form.is_file():
        form = load_yaml(incident_form, issues)
        body = form.get("body") if isinstance(form, dict) else None
        if not isinstance(body, list):
            issues.append(Issue(incident_form, "incident Issue Form must contain a body array"))
        else:
            fields = {
                item.get("id"): item
                for item in body
                if isinstance(item, dict) and isinstance(item.get("id"), str)
            }
            required_fields = {
                "severity",
                "started_at",
                "environment_scope",
                "user_impact",
                "known_facts",
                "unknowns",
                "owner",
                "version_release",
                "evidence_links",
                "safety_acknowledgement",
            }
            missing_fields = sorted(required_fields - set(fields))
            if missing_fields:
                issues.append(
                    Issue(
                        incident_form,
                        f"incident Issue Form is missing fields: {', '.join(missing_fields)}",
                    )
                )
            for field_name in required_fields & set(fields):
                validations = fields[field_name].get("validations")
                if not isinstance(validations, dict) or validations.get("required") is not True:
                    issues.append(
                        Issue(
                            incident_form,
                            f"incident Issue Form field {field_name!r} must be required",
                        )
                    )

    if improvement_form.is_file():
        form = load_yaml(improvement_form, issues)
        body = form.get("body") if isinstance(form, dict) else None
        fields = (
            {
                item.get("id"): item
                for item in body
                if isinstance(item, dict) and isinstance(item.get("id"), str)
            }
            if isinstance(body, list)
            else {}
        )
        required_fields = {
            "retrospective_backlink",
            "owner",
            "due_date",
            "definition_of_done",
            "effectiveness_criterion",
            "observation_window",
        }
        missing_fields = sorted(required_fields - set(fields))
        if missing_fields:
            issues.append(
                Issue(
                    improvement_form,
                    f"improvement Issue Form is missing fields: {', '.join(missing_fields)}",
                )
            )
        for field_name in required_fields & set(fields):
            validations = fields[field_name].get("validations")
            if not isinstance(validations, dict) or validations.get("required") is not True:
                issues.append(
                    Issue(
                        improvement_form,
                        f"improvement Issue Form field {field_name!r} must be required",
                    )
                )

    if audit_workflow.is_file():
        workflow = load_yaml(audit_workflow, issues)
        triggers = workflow.get("on") if isinstance(workflow, dict) else None
        schedules = triggers.get("schedule") if isinstance(triggers, dict) else None
        if schedules != [{"cron": "0 2 * * 1"}]:
            issues.append(Issue(audit_workflow, "lifecycle audit must run Mondays at 02:00 UTC"))

    prepare_release_workflow = workflows_root / "prepare-release.yml"
    if prepare_release_workflow.is_file():
        content = prepare_release_workflow.read_text(encoding="utf-8")
        if content.count("--profile auto") != 2:
            issues.append(
                Issue(
                    prepare_release_workflow,
                    "prepare-release must auto-detect the installed automation profile",
                )
            )

    lifecycle_policy_workflow = workflows_root / "lifecycle-policy.yml"
    if lifecycle_policy_workflow.is_file():
        content = lifecycle_policy_workflow.read_text(encoding="utf-8")
        if (
            "pulls/$PR_NUMBER/files?per_page=100" not in content
            or "--paginate --slurp" not in content
        ):
            issues.append(
                Issue(
                    lifecycle_policy_workflow,
                    "lifecycle-policy must fetch the complete pull request file list",
                )
            )
        if '--files "$RUNNER_TEMP/pull-request-files.json"' not in content:
            issues.append(
                Issue(
                    lifecycle_policy_workflow,
                    "lifecycle-policy must pass pull request files to the validator",
                )
            )

    manifest_components: dict[str, list[str]] = {}
    manifest_profiles: dict[str, list[str]] = {}
    manifest_files: list[str] = []
    if manifest.is_file():
        try:
            raw_manifest = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            issues.append(Issue(manifest, f"invalid automation manifest JSON: {error}"))
        else:
            if not isinstance(raw_manifest, dict) or raw_manifest.get("schema_version") != 3:
                issues.append(Issue(manifest, "repository automation manifest must use schema 3"))
            raw_components = (
                raw_manifest.get("components") if isinstance(raw_manifest, dict) else None
            )
            if not isinstance(raw_components, dict):
                issues.append(Issue(manifest, "automation manifest components must be an object"))
            else:
                component_names = set(raw_components)
                if component_names != AUTOMATION_COMPONENTS:
                    issues.append(
                        Issue(
                            manifest,
                            "automation manifest components must equal: "
                            + ", ".join(sorted(AUTOMATION_COMPONENTS)),
                        )
                    )
                for name, raw_files in raw_components.items():
                    if (
                        not isinstance(name, str)
                        or not isinstance(raw_files, list)
                        or not all(isinstance(item, str) for item in raw_files)
                    ):
                        issues.append(
                            Issue(manifest, f"automation manifest component {name!r} is invalid")
                        )
                        continue
                    manifest_components[name] = raw_files
                    if not raw_files:
                        issues.append(
                            Issue(manifest, f"automation manifest component {name!r} is empty")
                        )
                    if raw_files != sorted(raw_files):
                        issues.append(
                            Issue(
                                manifest,
                                f"automation manifest component {name!r} files must be sorted",
                            )
                        )
                    if len(raw_files) != len(set(raw_files)):
                        issues.append(
                            Issue(
                                manifest,
                                f"automation manifest component {name!r} files must be unique",
                            )
                        )
                    manifest_files.extend(raw_files)

                if len(manifest_files) != len(set(manifest_files)):
                    issues.append(
                        Issue(manifest, "automation manifest files must not cross components")
                    )
                for item in manifest_files:
                    item_path = Path(item)
                    if item_path.is_absolute() or ".." in item_path.parts:
                        issues.append(Issue(manifest, f"unsafe automation manifest path: {item}"))
                    elif not (root / item_path).is_file():
                        issues.append(
                            Issue(manifest, f"automation manifest file does not exist: {item}")
                        )
                    if item in INTERNAL_SUPPORT_ASSETS or item.startswith("tests/"):
                        issues.append(
                            Issue(manifest, f"internal support asset must not be packaged: {item}")
                        )
                    if any(item.startswith(prefix) for prefix in KNOWLEDGE_ASSET_PREFIXES):
                        issues.append(
                            Issue(manifest, f"knowledge asset must not be packaged: {item}")
                        )
            raw_profiles = raw_manifest.get("profiles") if isinstance(raw_manifest, dict) else None
            if not isinstance(raw_profiles, dict):
                issues.append(Issue(manifest, "automation manifest profiles must be an object"))
            else:
                if set(raw_profiles) != AUTOMATION_PROFILES:
                    issues.append(
                        Issue(
                            manifest,
                            "automation manifest profiles must equal: "
                            + ", ".join(sorted(AUTOMATION_PROFILES)),
                        )
                    )
                for name, raw_files in raw_profiles.items():
                    if not isinstance(raw_files, list) or not all(
                        isinstance(item, str) for item in raw_files
                    ):
                        issues.append(
                            Issue(manifest, f"automation manifest profile {name!r} is invalid")
                        )
                        continue
                    manifest_profiles[name] = raw_files
                    if not raw_files:
                        issues.append(
                            Issue(manifest, f"automation manifest profile {name!r} is empty")
                        )
                    if raw_files != sorted(raw_files):
                        issues.append(
                            Issue(
                                manifest,
                                f"automation manifest profile {name!r} files must be sorted",
                            )
                        )
                    if len(raw_files) != len(set(raw_files)):
                        issues.append(
                            Issue(
                                manifest,
                                f"automation manifest profile {name!r} files must be unique",
                            )
                        )
                    outside_components = sorted(set(raw_files) - set(manifest_files))
                    if outside_components:
                        issues.append(
                            Issue(
                                manifest,
                                f"automation manifest profile {name!r} has files outside "
                                "components: " + ", ".join(outside_components),
                            )
                        )

    lifecycle_files = {
        policy,
        pull_request_template,
        documentation,
        security_policy,
        root / "scripts" / "__init__.py",
        root / "scripts" / "github_lifecycle" / "__init__.py",
        root / "scripts" / "github_lifecycle" / "common.py",
        root / "scripts" / "github_lifecycle" / "incident.py",
        root / "scripts" / "github_lifecycle" / "pr.py",
        root / "scripts" / "github_lifecycle" / "release.py",
        root / "scripts" / "github_lifecycle" / "retrospective.py",
    }
    lifecycle_files.update((github_root / "ISSUE_TEMPLATE").glob("*.yml"))
    lifecycle_files.update((github_root / "ISSUE_TEMPLATE").glob("*.yaml"))
    lifecycle_files.update(
        path for path in workflows_root.glob("*.yml") if path.name != "repository-checks.yml"
    )
    lifecycle_files.update(
        path for path in workflows_root.glob("*.yaml") if path.name != "repository-checks.yaml"
    )
    governance_files = {
        adapter_catalog,
        manifest,
        root / "scripts" / "github_lifecycle" / "__main__.py",
        root / "scripts" / "github_lifecycle" / "adapters.py",
        root / "scripts" / "github_lifecycle" / "adoption.py",
        root / "scripts" / "github_lifecycle" / "package.py",
        root / "scripts" / "github_lifecycle" / "repository.py",
    }
    for workflow in lifecycle_files:
        if workflow.suffix not in {".yml", ".yaml"} or not workflow.is_file():
            continue
        if GOVERNANCE_COMMAND_PATTERN.search(workflow.read_text(encoding="utf-8")):
            issues.append(
                Issue(workflow, "lifecycle workflow must not invoke cross-project governance")
            )
    expected_components = {
        "github-lifecycle": {
            str(path.relative_to(root)) for path in lifecycle_files if path.is_file()
        },
        "cross-project-governance": {
            str(path.relative_to(root)) for path in governance_files if path.is_file()
        },
    }
    for name, expected_files in expected_components.items():
        actual_files = set(manifest_components.get(name, []))
        missing = sorted(expected_files - actual_files)
        extra = sorted(actual_files - expected_files)
        if missing:
            issues.append(
                Issue(
                    manifest,
                    f"automation manifest component {name!r} is missing files: "
                    + ", ".join(missing),
                )
            )
        if extra:
            issues.append(
                Issue(
                    manifest,
                    f"automation manifest component {name!r} has unexpected files: "
                    + ", ".join(extra),
                )
            )
    shared_profile_files = {
        item
        for files in expected_components.values()
        for item in files
        if item.startswith("automation/")
        or item == "docs/github-lifecycle-automation.md"
        or item.startswith("scripts/")
    }
    expected_profiles = {
        "governance": shared_profile_files
        | {
            ".github/PULL_REQUEST_TEMPLATE.md",
            ".github/lifecycle-policy.json",
            ".github/workflows/lifecycle-policy.yml",
        },
        "incident": shared_profile_files
        | {
            ".github/ISSUE_TEMPLATE/config.yml",
            ".github/ISSUE_TEMPLATE/improvement-action.yml",
            ".github/ISSUE_TEMPLATE/incident.yml",
            ".github/lifecycle-policy.json",
            ".github/workflows/audit-lifecycle-records.yml",
            ".github/workflows/open-retrospective.yml",
            ".github/workflows/transition-incident.yml",
            "SECURITY.md",
        },
        "release": shared_profile_files
        | {
            ".github/lifecycle-policy.json",
            ".github/workflows/prepare-release.yml",
        },
        "full": set().union(*expected_components.values()),
    }
    for name, expected_files in expected_profiles.items():
        actual_files = set(manifest_profiles.get(name, []))
        if actual_files != expected_files:
            missing = sorted(expected_files - actual_files)
            extra = sorted(actual_files - expected_files)
            details = []
            if missing:
                details.append("missing " + ", ".join(missing))
            if extra:
                details.append("unexpected " + ", ".join(extra))
            issues.append(
                Issue(
                    manifest,
                    f"automation manifest profile {name!r} does not match its boundary: "
                    + "; ".join(details),
                )
            )
    return issues


def skill_files(root: Path) -> list[Path]:
    return sorted((root / "skills").glob("[0-9][0-9]-*/*/SKILL.md"))


def governed_content_files(root: Path) -> list[Path]:
    workflows = sorted((root / "docs" / "workflows").glob("*.md"))
    return skill_files(root) + workflows


def check_content_governance(root: Path, as_of: date | None = None) -> list[Issue]:
    issues: list[Issue] = []
    check_date = as_of or date.today()
    for path in governed_content_files(root):
        match = FRONTMATTER_PATTERN.match(path.read_text(encoding="utf-8"))
        if match is None:
            issues.append(Issue(path, "governed content must start with YAML frontmatter"))
            continue
        try:
            metadata = yaml.safe_load(match.group(1))
        except yaml.YAMLError as error:
            issues.append(Issue(path, f"invalid governance frontmatter: {error}"))
            continue
        if not isinstance(metadata, dict):
            issues.append(Issue(path, "governance frontmatter must be a mapping"))
            continue

        governance = metadata.get("metadata") if path.name == "SKILL.md" else metadata
        if not isinstance(governance, dict):
            issues.append(Issue(path, "SKILL metadata must contain a governance mapping"))
            continue

        owner = governance.get("owner")
        if not isinstance(owner, str) or not SLUG_PATTERN.fullmatch(owner):
            issues.append(Issue(path, "owner must be a non-empty lowercase kebab-case role"))

        scope = governance.get("scope")
        if not isinstance(scope, str) or not scope.strip():
            issues.append(Issue(path, "scope must be a non-empty string"))

        status = governance.get("status")
        if not isinstance(status, str) or status not in CONTENT_STATUSES:
            allowed = ", ".join(sorted(CONTENT_STATUSES))
            issues.append(Issue(path, f"status must be one of: {allowed}"))

        review_by = governance.get("review_by")
        if not isinstance(review_by, str):
            issues.append(Issue(path, "review_by must be a quoted YYYY-MM-DD string"))
            continue
        if not ISO_DATE_PATTERN.fullmatch(review_by):
            issues.append(Issue(path, "review_by must use YYYY-MM-DD format"))
            continue
        try:
            review_date = date.fromisoformat(review_by)
        except ValueError:
            issues.append(Issue(path, "review_by must be a valid YYYY-MM-DD date"))
            continue
        if review_date < check_date:
            issues.append(
                Issue(
                    path,
                    f"content review is overdue: {review_by} < {check_date.isoformat()}",
                )
            )
    return issues


def check_skill_structure(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    skills_root = root / "skills"
    if not skills_root.is_dir():
        return [Issue(skills_root, "missing skills directory")]
    expected_phases = {skills_root / name for name in PHASES.values()}
    actual_phases = {path for path in skills_root.iterdir() if path.is_dir()}

    for path in sorted(expected_phases - actual_phases):
        issues.append(Issue(path, "missing phase directory"))
    for path in sorted(actual_phases - expected_phases):
        issues.append(Issue(path, "unexpected phase directory"))

    known_names: dict[str, Path] = {}
    for path in skill_files(root):
        skill_dir = path.parent
        phase_dir = skill_dir.parent
        if not SLUG_PATTERN.fullmatch(skill_dir.name):
            issues.append(Issue(skill_dir, "skill directory must use lowercase kebab-case"))

        match = FRONTMATTER_PATTERN.match(path.read_text(encoding="utf-8"))
        if match is None:
            issues.append(Issue(path, "SKILL.md must start with YAML frontmatter"))
            continue
        try:
            metadata = yaml.safe_load(match.group(1))
        except yaml.YAMLError as error:
            issues.append(Issue(path, f"invalid frontmatter YAML: {error}"))
            continue
        if not isinstance(metadata, dict):
            issues.append(Issue(path, "frontmatter must be a mapping"))
            continue

        name = metadata.get("name")
        description = metadata.get("description")
        if name != skill_dir.name:
            issues.append(
                Issue(path, f"frontmatter name must equal directory name {skill_dir.name!r}")
            )
        if not isinstance(description, str) or not description.strip():
            issues.append(Issue(path, "frontmatter description must be a non-empty string"))
        if isinstance(name, str):
            if name in known_names:
                issues.append(Issue(path, f"duplicate skill name also used by {known_names[name]}"))
            known_names[name] = path

        agent_path = skill_dir / "agents" / "openai.yaml"
        if not agent_path.is_file():
            issues.append(Issue(agent_path, "missing skill agent metadata"))
            continue
        agent = load_yaml(agent_path, issues)
        interface = agent.get("interface") if isinstance(agent, dict) else None
        if not isinstance(interface, dict):
            issues.append(Issue(agent_path, "agent metadata must contain an interface mapping"))
            continue
        for key in ("display_name", "short_description"):
            if not isinstance(interface.get(key), str) or not interface[key].strip():
                issues.append(Issue(agent_path, f"interface.{key} must be a non-empty string"))
        default_prompt = interface.get("default_prompt")
        if default_prompt is not None and (
            not isinstance(default_prompt, str) or not default_prompt.strip()
        ):
            issues.append(Issue(agent_path, "interface.default_prompt must be a non-empty string"))

        allowed_children = {
            path,
            skill_dir / "agents",
            skill_dir / "assets",
            skill_dir / "references",
            skill_dir / "scripts",
        }
        for child in skill_dir.iterdir():
            if child not in allowed_children:
                issues.append(Issue(child, "unexpected entry in skill directory"))
        if phase_dir not in expected_phases:
            issues.append(Issue(path, "skill is not inside a recognized phase directory"))

    discovered = set(repository_files(skills_root, "SKILL.md"))
    expected = set(skill_files(root))
    for path in sorted(discovered - expected):
        issues.append(Issue(path, "SKILL.md must be located at skills/<phase>/<skill>/SKILL.md"))
    return issues


def markdown_links(path: Path) -> Iterable[tuple[int, str]]:
    in_fence = False
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for target in LINK_PATTERN.findall(line):
            yield line_number, target.strip().strip("<>")


def resolve_local_link(source: Path, target: str) -> Path | None:
    if not target or target.startswith(("#", "http://", "https://", "mailto:")):
        return None
    path_part = unquote(target.split("#", maxsplit=1)[0])
    if not path_part:
        return None
    return (source.parent / path_part).resolve()


def check_links(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    for path in repository_files(root, "*.md"):
        for line_number, target in markdown_links(path):
            resolved = resolve_local_link(path, target)
            if resolved is not None and not resolved.exists():
                issues.append(Issue(path, f"broken local link: {target}", line_number))
    return issues


def linked_skill_files(path: Path) -> set[Path]:
    linked: set[Path] = set()
    for _, target in markdown_links(path):
        resolved = resolve_local_link(path, target)
        if resolved is not None and resolved.name == "SKILL.md":
            linked.add(resolved)
    return linked


def check_delivery_templates(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    root = root.resolve()
    templates_root = root / "templates" / "delivery"
    if not templates_root.is_dir():
        return [Issue(templates_root, "missing delivery templates directory")]

    navigation = templates_root / "README.md"
    if not navigation.is_file():
        issues.append(Issue(navigation, "missing delivery template navigation"))

    expected_paths = {templates_root / name for name in DELIVERY_TEMPLATES}
    actual_paths = set(templates_root.glob("*.md")) - {navigation}
    for path in sorted(expected_paths - actual_paths):
        issues.append(Issue(path, "missing required delivery template"))
    for path in sorted(actual_paths - expected_paths):
        issues.append(Issue(path, "unexpected delivery template"))

    if navigation.is_file():
        navigation_links = {
            resolved
            for _, target in markdown_links(navigation)
            if (resolved := resolve_local_link(navigation, target)) is not None
        }
        for path in sorted(expected_paths - navigation_links):
            issues.append(
                Issue(navigation, f"delivery template is missing from navigation: {path.name}")
            )

    for name, lifecycle_stages in DELIVERY_TEMPLATES.items():
        path = templates_root / name
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        match = FRONTMATTER_PATTERN.match(content)
        if match is None:
            issues.append(Issue(path, "delivery template must start with YAML frontmatter"))
            continue
        try:
            metadata = yaml.safe_load(match.group(1))
        except yaml.YAMLError as error:
            issues.append(Issue(path, f"invalid delivery template frontmatter: {error}"))
            continue
        if not isinstance(metadata, dict):
            issues.append(Issue(path, "delivery template frontmatter must be a mapping"))
            continue
        if metadata.get("template_name") != path.stem:
            issues.append(Issue(path, f"template_name must equal {path.stem!r}"))
        if metadata.get("template_version") != 1:
            issues.append(Issue(path, "template_version must equal 1"))
        if metadata.get("lifecycle_stages") != list(lifecycle_stages):
            issues.append(Issue(path, f"lifecycle_stages must equal {list(lifecycle_stages)!r}"))
        if metadata.get("traceability_fields") != list(TRACEABILITY_FIELDS):
            issues.append(
                Issue(path, "traceability_fields must equal the shared traceability contract")
            )
        if "## 追溯信息\n" not in content:
            issues.append(Issue(path, "delivery template must contain a traceability section"))
        for field in TRACEABILITY_FIELDS:
            label = TRACEABILITY_LABELS[field]
            if f"- {label}：" not in content:
                issues.append(Issue(path, f"missing visible traceability field: {field}"))

    for phase, template_names in WORKFLOW_DELIVERY_TEMPLATES.items():
        workflow = root / "docs" / "workflows" / f"{PHASES[phase]}.md"
        if not workflow.is_file():
            continue
        linked_paths = {
            resolved
            for _, target in markdown_links(workflow)
            if (resolved := resolve_local_link(workflow, target)) is not None
        }
        for template_name in template_names:
            template_path = templates_root / template_name
            if template_path not in linked_paths:
                issues.append(
                    Issue(
                        workflow,
                        f"workflow is missing delivery template: {template_path.relative_to(root)}",
                    )
                )
    return issues


def check_end_to_end_exercises(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    root = root.resolve()
    exercises_root = root / "docs" / "exercises"
    if not exercises_root.is_dir():
        return [Issue(exercises_root, "missing end-to-end exercises directory")]

    navigation = exercises_root / "README.md"
    if not navigation.is_file():
        issues.append(Issue(navigation, "missing end-to-end exercise navigation"))

    expected_paths = {exercises_root / name for name in END_TO_END_EXERCISES}
    actual_paths = set(exercises_root.glob("*.md")) - {navigation}
    for path in sorted(expected_paths - actual_paths):
        issues.append(Issue(path, "missing required end-to-end exercise"))
    for path in sorted(actual_paths - expected_paths):
        issues.append(Issue(path, "unexpected end-to-end exercise"))

    if navigation.is_file():
        navigation_links = {
            resolved
            for _, target in markdown_links(navigation)
            if (resolved := resolve_local_link(navigation, target)) is not None
        }
        for path in sorted(expected_paths - navigation_links):
            issues.append(
                Issue(navigation, f"end-to-end exercise is missing from navigation: {path.name}")
            )

    lifecycle = root / "docs" / "software-development-lifecycle.md"
    if lifecycle.is_file() and navigation.is_file():
        lifecycle_links = {
            resolved
            for _, target in markdown_links(lifecycle)
            if (resolved := resolve_local_link(lifecycle, target)) is not None
        }
        if navigation not in lifecycle_links:
            issues.append(Issue(lifecycle, "lifecycle is missing end-to-end exercise navigation"))

    required_templates = list(DELIVERY_TEMPLATES)
    required_template_paths = {
        root / "templates" / "delivery" / name for name in required_templates
    }
    required_stages = list(PHASES)
    for name, (risk_level, scenario_type) in END_TO_END_EXERCISES.items():
        path = exercises_root / name
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        match = FRONTMATTER_PATTERN.match(content)
        if match is None:
            issues.append(Issue(path, "end-to-end exercise must start with YAML frontmatter"))
            continue
        try:
            metadata = yaml.safe_load(match.group(1))
        except yaml.YAMLError as error:
            issues.append(Issue(path, f"invalid end-to-end exercise frontmatter: {error}"))
            continue
        if not isinstance(metadata, dict):
            issues.append(Issue(path, "end-to-end exercise frontmatter must be a mapping"))
            continue
        if metadata.get("exercise_name") != path.stem:
            issues.append(Issue(path, f"exercise_name must equal {path.stem!r}"))
        if metadata.get("exercise_version") != 1:
            issues.append(Issue(path, "exercise_version must equal 1"))
        if metadata.get("risk_level") != risk_level:
            issues.append(Issue(path, f"risk_level must equal {risk_level!r}"))
        if metadata.get("scenario_type") != scenario_type:
            issues.append(Issue(path, f"scenario_type must equal {scenario_type!r}"))
        if metadata.get("lifecycle_stages") != required_stages:
            issues.append(Issue(path, f"lifecycle_stages must equal {required_stages!r}"))
        if metadata.get("required_templates") != required_templates:
            issues.append(
                Issue(path, "required_templates must equal the delivery template contract")
            )

        for stage in PHASES:
            if f"## 阶段 {stage}：" not in content:
                issues.append(Issue(path, f"missing lifecycle stage section: {stage}"))
        if "## 演练通过条件\n" not in content:
            issues.append(Issue(path, "end-to-end exercise must define pass conditions"))

        linked_paths = {
            resolved
            for _, target in markdown_links(path)
            if (resolved := resolve_local_link(path, target)) is not None
        }
        for template_path in sorted(required_template_paths - linked_paths):
            issues.append(
                Issue(path, f"exercise is missing delivery template: {template_path.name}")
            )
    return issues


def check_navigation(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    all_skills = set(skill_files(root))
    navigation = root / "skills" / "README.md"
    if navigation.is_file():
        navigation_links = linked_skill_files(navigation)
    else:
        issues.append(Issue(navigation, "missing skill navigation"))
        navigation_links = set()
    missing_from_navigation = all_skills - navigation_links
    for path in sorted(missing_from_navigation):
        issues.append(
            Issue(navigation, f"skill is missing from navigation: {path.relative_to(root)}")
        )

    for phase_name in PHASES.values():
        workflow = root / "docs" / "workflows" / f"{phase_name}.md"
        phase_skills = {path for path in all_skills if path.parent.parent.name == phase_name}
        if workflow.is_file():
            workflow_links = linked_skill_files(workflow)
        else:
            issues.append(Issue(workflow, "missing phase workflow"))
            workflow_links = set()
        missing_from_workflow = phase_skills - workflow_links
        for path in sorted(missing_from_workflow):
            issues.append(
                Issue(workflow, f"skill is missing from workflow: {path.relative_to(root)}")
            )
    return issues


def check_markdown_format(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    for path in repository_files(root, "*.md"):
        content = path.read_text(encoding="utf-8")
        if content and not content.endswith("\n"):
            issues.append(Issue(path, "file must end with a newline"))

        in_fence = False
        fence_marker: str | None = None
        h1_count = 0
        previous_level = 0
        for line_number, line in enumerate(content.splitlines(), start=1):
            stripped = line.lstrip()
            marker = stripped[:3]
            if marker in {"```", "~~~"}:
                if not in_fence:
                    in_fence = True
                    fence_marker = marker
                elif marker == fence_marker:
                    in_fence = False
                    fence_marker = None
                continue
            if line.endswith((" ", "\t")):
                issues.append(Issue(path, "trailing whitespace", line_number))
            if not in_fence and "\t" in line:
                issues.append(Issue(path, "tabs are not allowed outside code fences", line_number))
            if in_fence:
                continue
            heading = HEADING_PATTERN.match(line)
            if heading is None:
                continue
            level = len(heading.group(1))
            if level == 1:
                h1_count += 1
            if previous_level and level > previous_level + 1:
                issues.append(Issue(path, "heading levels must not be skipped", line_number))
            previous_level = level
        if in_fence:
            issues.append(Issue(path, "unclosed fenced code block"))
        if h1_count != 1:
            issues.append(Issue(path, f"expected exactly one level-1 heading, found {h1_count}"))
    return issues


def run_checks(root: Path, as_of: date | None = None) -> list[Issue]:
    checks = (
        check_yaml,
        check_github_automation,
        check_skill_structure,
        check_links,
        check_delivery_templates,
        check_end_to_end_exercises,
        check_navigation,
        check_markdown_format,
    )
    issues = [issue for check in checks for issue in check(root)]
    issues.extend(check_content_governance(root, as_of=as_of))
    return sorted(issues)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--as-of",
        type=date.fromisoformat,
        default=date.today(),
        help="check content review dates as of YYYY-MM-DD (default: today)",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    issues = run_checks(root, as_of=args.as_of)
    if issues:
        print(f"Repository checks failed with {len(issues)} issue(s):", file=sys.stderr)
        for issue in issues:
            print(f"- {issue.render(root)}", file=sys.stderr)
        return 1
    print(
        "Repository checks passed: YAML, GitHub automation, skills, content governance, "
        "delivery templates, exercises, links, navigation, and Markdown."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
