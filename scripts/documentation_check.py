"""Validate adopted project documents and bind independent review to a Git snapshot.

Run from a fixed harness checkout with --root pointing at the adopting repository.
Review and snapshot outputs live outside that repository to avoid digest cycles.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import UTC, date, datetime
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

DOMAINS = (
    "research",
    "product",
    "design",
    "engineering",
    "guides",
    "planning",
    "initiatives",
    "releases",
    "navigation",
)
REVIEW_CHECKS = ("impact", "implementation", "bilingual", "evidence", "examples")
STATES = {
    "knowledge": {"draft", "current", "superseded"},
    "initiative": {"proposed", "active", "paused", "completed", "cancelled"},
    "release": {"planned", "verified", "released", "cancelled", "withdrawn"},
}
LINK = re.compile(r"!?\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)")
REFERENCE = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)", re.MULTILINE)
NAME = re.compile(r"(?:README|CHANGELOG|[a-z0-9]+(?:-[a-z0-9]+)*)(?:\.[a-z]{2}(?:-[a-z]{2})?)?\.md")


class InvalidDocumentation(ValueError):
    """A configuration, document, or review violates the delivery contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InvalidDocumentation(message)


def mapping(value: object, label: str) -> dict:
    require(isinstance(value, dict), f"{label}: expected object")
    return value


def strings(value: object, label: str, *, empty: bool = False) -> list[str]:
    require(isinstance(value, list), f"{label}: expected list")
    require(all(isinstance(item, str) and item.strip() for item in value), f"{label}: empty item")
    require(empty or bool(value), f"{label}: empty list")
    require(len(value) == len(set(value)), f"{label}: duplicate item")
    return value


def read_json(path: Path) -> dict:
    def unique(pairs: list[tuple[str, object]]) -> dict:
        result = {}
        for key, value in pairs:
            require(key not in result, f"{path}: duplicate key {key}")
            result[key] = value
        return result

    return mapping(
        json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique), str(path)
    )


def local(root: Path, name: str) -> Path:
    require(isinstance(name, str) and bool(name), "empty path")
    path = Path(name)
    require(not path.is_absolute() and ".." not in path.parts, f"unsafe path: {name}")
    require(path.as_posix() == name and name != ".", f"noncanonical path: {name}")
    target = root / path
    require(target.resolve().is_relative_to(root), f"path escapes root: {name}")
    require(
        not any((root / Path(*path.parts[:n])).is_symlink() for n in range(1, len(path.parts) + 1)),
        f"symlink is not supported: {name}",
    )
    return target


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)
    return result.stdout.decode("utf-8")


def inventory(root: Path) -> list[str]:
    require(
        Path(git(root, "rev-parse", "--show-toplevel").strip()).resolve() == root,
        "--root must be the Git repository root",
    )
    return sorted(
        set(
            filter(
                None,
                git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard").split(
                    "\0"
                ),
            )
        )
    )


def changed(root: Path, base: str) -> list[str]:
    return sorted(
        set(
            filter(
                None,
                git(
                    root, "diff", "--no-ext-diff", "--no-textconv", "--name-only", "-z", base
                ).split("\0"),
            )
        )
        | set(
            filter(None, git(root, "ls-files", "-z", "--others", "--exclude-standard").split("\0"))
        )
    )


def config(root: Path, name: str) -> dict:
    data = read_json(local(root, name))
    require(data.get("schema_version") == 1, "unsupported configuration schema")
    require(
        isinstance(data.get("standard_version"), str)
        and re.fullmatch(r"(?:[0-9a-f]{40}|[0-9]+\.[0-9]+\.[0-9]+)", data["standard_version"])
        is not None,
        "fixed standard_version required",
    )
    owners = mapping(data.get("owners"), "owners")
    require(
        bool(owners) and all(isinstance(value, str) and value.strip() for value in owners.values()),
        "owners must map roles to actual maintainers",
    )
    strings(data.get("required_checks"), "required_checks", empty=True)
    docs = mapping(data.get("documents"), "documents")
    require(
        {"README.md", "CHANGELOG.md", "docs/README.md", "docs/documentation.md"} <= set(docs),
        "project, changelog, documentation map and configuration entries required",
    )
    for path, kind in docs.items():
        local(root, path)
        require(path.endswith(".md") and not language(path), f"inventory primary only: {path}")
        require(kind in STATES, f"invalid document kind: {path}")
    translations = mapping(data.get("translations", {}), "translations")
    for path, languages in translations.items():
        require(path in docs, f"translation primary is not registered: {path}")
        for lang in strings(languages, path, empty=True):
            require(
                re.fullmatch(r"[a-z]{2}(?:-[a-z]{2})?", lang) is not None
                and lang not in {"en", "zh"},
                f"invalid optional language: {lang}",
            )
    for field in ("legacy", "raw"):
        entries = mapping(data.get(field, {}), field)
        for path, entry in entries.items():
            local(root, path)
            entry = mapping(entry, path)
            for key in ("owner", "reason", "evidence"):
                require(
                    isinstance(entry.get(key), str) and bool(entry[key].strip()),
                    f"{path}: {key} required",
                )
            require(local(root, entry["evidence"]).is_file(), f"{path}: missing inventory evidence")
            if field == "legacy":
                require(isinstance(entry.get("due"), str), f"{path}: migration due required")
                require(
                    re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", entry["due"]) is not None,
                    f"{path}: due must be YYYY-MM-DD",
                )
                require(
                    date.fromisoformat(entry["due"]) >= date.today(), f"{path}: migration overdue"
                )
    legacy = set(data.get("legacy", {}))
    raw = set(data.get("raw", {}))
    maintained = {variant for path in docs for variant in variants(data, path)}
    require(not maintained & (legacy | raw) and not legacy & raw, "inventories overlap")
    return data


def english(path: str) -> str:
    return path[:-3] + ".en.md"


def variants(data: dict, path: str) -> list[str]:
    return [
        path,
        english(path),
        *(path[:-3] + f".{lang}.md" for lang in data.get("translations", {}).get(path, [])),
    ]


def language(path: str) -> str:
    match = re.search(r"\.([a-z]{2}(?:-[a-z]{2})?)\.md$", path)
    return match[1] if match else ""


def body(text: str) -> str:
    lines = text.splitlines()
    result = []
    fence = None
    for line in lines:
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
        elif fence is None:
            result.append(line)
    return "\n".join(result)


def anchors(text: str) -> set[str]:
    html_text = re.sub(r"(`+).*?\1", "", body(text), flags=re.DOTALL)
    result = set(re.findall(r'(?:id|name)=["\']([^"\']+)["\']', html_text))
    counts: dict[str, int] = {}
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", body(text), re.MULTILINE):
        heading = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", heading)
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        result.add(f"{slug}-{count}" if count else slug)
    return result


def links(text: str) -> list[str]:
    clean = re.sub(r"(`+).*?\1", "", body(text), flags=re.DOTALL)
    return [*LINK.findall(clean), *REFERENCE.findall(clean)]


def frontmatter(path: Path, kind: str) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.DOTALL)
    require(match is not None, f"{path}: YAML frontmatter required")
    # Reject duplicate keys rather than accepting silently overwritten metadata.
    node = yaml.compose(match[1])
    require(isinstance(node, yaml.MappingNode), f"{path}: frontmatter must be a mapping")
    keys = [key.value for key, _ in node.value]
    require(len(keys) == len(set(keys)), f"{path}: duplicate metadata")
    metadata = mapping(yaml.safe_load(match[1]), str(path))
    for key in ("title", "owner", "updated"):
        require(
            isinstance(metadata.get(key), str) and bool(metadata[key].strip()),
            f"{path}: {key} must be a nonempty string",
        )
    require(metadata.get("status") in STATES[kind], f"{path}: illegal {kind} status")
    require(
        re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", metadata["updated"]) is not None,
        f"{path}: updated must be YYYY-MM-DD",
    )
    require(date.fromisoformat(metadata["updated"]) <= date.today(), f"{path}: future updated date")
    return metadata, text[match.end() :]


def check(root: Path, name: str, base: str | None = None) -> dict:
    data = config(root, name)
    files = inventory(root)
    docs = data["documents"]
    maintained = {variant for path in docs for variant in variants(data, path)}
    registered = maintained | set(data.get("legacy", {})) | set(data.get("raw", {}))
    markdown = {path for path in files if path.endswith(".md") and local(root, path).exists()}
    require(not markdown - registered, f"unregistered Markdown: {sorted(markdown - registered)}")
    if base:
        require(re.fullmatch(r"[a-f0-9]{40}", base) is not None, "base must be full commit SHA")
        require(
            git(root, "rev-parse", "--verify", f"{base}^{{commit}}").strip() == base,
            "base is not a commit",
        )
        git(root, "merge-base", "--is-ancestor", base, "HEAD")
        touched = set(changed(root, base))
        require(not touched & set(data.get("legacy", {})), "changed legacy documents must migrate")
    read = {}
    for primary, kind in docs.items():
        family = variants(data, primary)
        for path in family:
            require(path in files, f"document ignored or missing from Git inventory: {path}")
            target = local(root, path)
            require(NAME.fullmatch(target.name) is not None, f"invalid document name: {path}")
            require(
                all(
                    re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", part)
                    for part in Path(path).parts[:-1]
                ),
                f"invalid directory name: {path}",
            )
            read[path] = frontmatter(target, kind)
            require(read[path][0]["owner"] in data["owners"], f"unmapped owner: {path}")
        for peer in family[1:]:
            for key in ("owner", "status"):
                require(
                    read[primary][0][key] == read[peer][0][key], f"pair {key} differs: {primary}"
                )
            for path, other in ((primary, peer), (peer, primary)):
                require(
                    any(
                        (Path(path).parent / unquote(urlsplit(link).path)).as_posix() == other
                        for link in links(read[path][1])
                    ),
                    f"pair backlink missing: {path}",
                )
    families = {
        variant: set(variants(data, primary))
        for primary in docs
        for variant in variants(data, primary)
    }
    for path, (_, text) in read.items():
        for link in links(text):
            parsed = urlsplit(link.strip("<>"))
            if parsed.scheme or parsed.netloc:
                continue
            require(not parsed.path.startswith("/"), f"absolute link: {path}: {link}")
            target = (
                (root / Path(path).parent / unquote(parsed.path)) if parsed.path else (root / path)
            ).resolve()
            require(target.is_relative_to(root), f"link escapes repository: {path}: {link}")
            require(target.exists(), f"broken link: {path}: {link}")
            if parsed.fragment and target.suffix == ".md":
                require(
                    unquote(parsed.fragment) in anchors(target.read_text(encoding="utf-8")),
                    f"broken heading link: {path}: {link}",
                )
            if target.is_file() and target.suffix == ".md":
                relative = target.relative_to(root).as_posix()
                if relative in maintained and relative not in families[path]:
                    require(
                        language(path) == language(relative),
                        f"cross-language maintained link: {path}: {link}",
                    )
    # Domain entries are required; deeper directories may use their nearest index.
    for primary, kind in docs.items():
        parts = Path(primary).parts
        if len(parts) > 2 and parts[0] == "docs" and parts[1] in DOMAINS[:-1]:
            entry = f"docs/{parts[1]}/README.md"
            require(entry in docs, f"missing domain entry: {entry}")
        if kind in {"initiative", "release"}:
            require(Path(primary).name == "README.md", f"{kind} must be a README entry: {primary}")
        parent = Path(primary).parent
        candidates = [parent, *parent.parents]
        index_parent = next(
            (part for part in candidates if (part / "README.md").as_posix() in docs), None
        )
        require(index_parent is not None, f"missing navigation entry for {primary}")
        for path in variants(data, primary):
            suffix = f".{language(path)}" if language(path) else ""
            index = (index_parent / f"README{suffix}.md").as_posix()
            require(index in read, f"missing translated index: {index}")
            if path != index:
                require(
                    any(
                        (root / index_parent / unquote(urlsplit(link).path)).resolve()
                        == (root / path).resolve()
                        for link in links(read[index][1])
                    ),
                    f"entry does not link document: {path}",
                )
    return {"status": "passed", "documents": sorted(maintained), "schema_version": 1}


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def snapshot(root: Path, name: str, base: str, authors: list[str]) -> dict:
    require(re.fullmatch(r"[a-f0-9]{40}", base) is not None, "base must be full commit SHA")
    require(
        git(root, "rev-parse", "--verify", f"{base}^{{commit}}").strip() == base,
        "base is not a commit",
    )
    require(
        bool(authors) and all(author.strip() for author in authors), "author identities required"
    )
    check(root, name, base)
    files = {}
    for path in inventory(root):
        target = local(root, path)
        require(not target.exists() or target.is_file(), f"unsupported Git entry: {path}")
        files[path] = (
            {
                "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                "executable": bool(target.stat().st_mode & 0o111),
            }
            if target.exists()
            else None
        )
    value = {
        "schema_version": 1,
        "base": base,
        "config": name,
        "authors": sorted(set(authors)),
        "files": files,
        "changed_files": changed(root, base),
    }
    return {**value, "digest": digest(value)}


def gate(root: Path, name: str, saved: dict, review: dict) -> dict:
    saved = mapping(saved, "snapshot")
    authors = strings(saved.get("authors"), "snapshot authors")
    current = snapshot(root, name, saved.get("base", ""), authors)
    require(saved == current, "snapshot stale or invalid; rerun independent review")
    require(
        review.get("schema_version") == 1 and review.get("snapshot_digest") == current["digest"],
        "review schema or snapshot mismatch",
    )
    require(
        isinstance(review.get("reviewer_role"), str) and bool(review["reviewer_role"].strip()),
        "reviewer role required",
    )
    reviewed_at = review.get("reviewed_at")
    require(isinstance(reviewed_at, str), "reviewed_at timestamp required")
    reviewed_time = datetime.fromisoformat(reviewed_at)
    require(
        reviewed_time.utcoffset() is not None and reviewed_time <= datetime.now(UTC),
        "reviewed_at must have a timezone and cannot be in the future",
    )
    reviewer = review.get("reviewer")
    require(
        isinstance(reviewer, str) and bool(reviewer.strip()) and reviewer not in authors,
        "reviewer must be an identified nonauthor",
    )
    require(
        review.get("independent") is True
        and isinstance(review.get("context"), str)
        and bool(review["context"].strip()),
        "independent review context required",
    )
    require(review.get("verdict") == "passed", "independent review did not pass")
    inspected = strings(review.get("inspected_files"), "inspected_files")
    require(
        set(inspected) <= (set(current["files"]) | set(current["changed_files"])),
        "inspection names unknown files",
    )
    required = set(check(root, name, current["base"])["documents"]) | set(current["changed_files"])
    require(required <= set(inspected), f"review unread files: {sorted(required - set(inspected))}")
    checks = mapping(review.get("checks"), "review checks")
    for key in REVIEW_CHECKS:
        item = mapping(checks.get(key), key)
        require(
            item.get("result") == "passed"
            and isinstance(item.get("evidence"), str)
            and item["evidence"] in review.get("evidence_files", []),
            f"{key}: passed conclusion and evidence required",
        )
    impacts = mapping(review.get("impacts"), "impacts")
    require(set(impacts) == set(DOMAINS), "all nine impact domains required")
    for domain, value in impacts.items():
        item = mapping(value, domain)
        require(
            item.get("result") in {"updated", "reviewed-no-change", "not-applicable"},
            f"{domain}: invalid impact result",
        )
        require(
            isinstance(item.get("reason"), str) and bool(item["reason"].strip()),
            f"{domain}: impact rationale required",
        )
        paths = strings(item.get("files"), domain, empty=item["result"] != "updated")
        require(set(paths) <= set(inspected), f"{domain}: impact files not inspected")
    evidence = strings(review.get("evidence_files"), "evidence_files")
    require(
        set(evidence) <= set(inspected) and all(current["files"].get(p) for p in evidence),
        "evidence must exist in snapshot and have been inspected",
    )
    ci = mapping(review.get("required_checks"), "required_checks")
    require(
        set(ci) == set(config(root, name)["required_checks"]),
        "required project checks do not match configuration",
    )
    for key, value in ci.items():
        item = mapping(value, key)
        require(
            item.get("result") == "passed" and item.get("evidence") in evidence,
            f"{key}: required check failed or evidence missing",
        )
    findings = review.get("findings")
    require(isinstance(findings, list), "findings list required")
    for value in findings:
        finding = mapping(value, "finding")
        require(
            finding.get("status") == "resolved"
            and isinstance(finding.get("recheck"), str)
            and bool(finding["recheck"].strip()),
            "unresolved finding or absent independent recheck",
        )
    return {
        "schema_version": 1,
        "status": "passed",
        "snapshot_digest": current["digest"],
        "reviewer": reviewer,
        "semantic_review": "attested, not automatically proven",
    }


def outside(root: Path, path: Path) -> Path:
    require(
        not path.resolve().is_relative_to(root),
        "snapshot/review/report must be outside target root",
    )
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "snapshot", "gate"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--config", default="docs/documentation-check.json")
    parser.add_argument("--base")
    parser.add_argument("--author", action="append", default=[])
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--review", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.output:
            outside(root, args.output)
        if args.command == "check":
            result = check(root, args.config, args.base)
        elif args.command == "snapshot":
            require(args.base is not None, "snapshot requires --base")
            result = snapshot(root, args.config, args.base, args.author)
        else:
            require(
                args.snapshot is not None and args.review is not None,
                "gate requires --snapshot and --review",
            )
            result = gate(
                root,
                args.config,
                read_json(outside(root, args.snapshot)),
                read_json(outside(root, args.review)),
            )
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 0
    except (
        InvalidDocumentation,
        OSError,
        ValueError,
        TypeError,
        yaml.YAMLError,
        subprocess.CalledProcessError,
    ) as error:
        print(json.dumps({"status": "blocked", "error": str(error)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
