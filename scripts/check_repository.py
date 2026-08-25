#!/usr/bin/env python3
"""Validate the playbook's skills, navigation, links, YAML, and Markdown."""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass
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
FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+\S")
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


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


def skill_files(root: Path) -> list[Path]:
    return sorted((root / "skills").glob("[0-9][0-9]-*/*/SKILL.md"))


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

        allowed_children = {path, skill_dir / "agents", skill_dir / "references"}
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


def run_checks(root: Path) -> list[Issue]:
    checks = (
        check_yaml,
        check_skill_structure,
        check_links,
        check_navigation,
        check_markdown_format,
    )
    return sorted(issue for check in checks for issue in check(root))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    issues = run_checks(root)
    if issues:
        print(f"Repository checks failed with {len(issues)} issue(s):", file=sys.stderr)
        for issue in issues:
            print(f"- {issue.render(root)}", file=sys.stderr)
        return 1
    print("Repository checks passed: YAML, skills, links, navigation, and Markdown.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
