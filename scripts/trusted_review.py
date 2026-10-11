"""Read maintainer attestations and corroborate current GitHub candidate/CI facts."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import subprocess
from collections.abc import Callable
from pathlib import Path

if __package__:
    from .documentation_check import config, gate, git, outside, read_json, require
else:
    from documentation_check import config, gate, git, outside, read_json, require

type Api = Callable[[str], object]
SHA = r"[a-f0-9]{40}"
HARNESS_ROOT = Path(__file__).resolve().parents[1]


def gh_api(endpoint: str) -> object:
    process = subprocess.run(
        ["gh", "api", endpoint, "--paginate", "--slurp"],
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    require(process.returncode == 0, "gh API unavailable; authenticate or restore access")
    pages = json.loads(process.stdout)
    require(isinstance(pages, list) and bool(pages), "empty GitHub response")
    if isinstance(pages[0], list):
        return [item for page in pages for item in page]
    if "check-runs?" in endpoint:
        return {"check_runs": [item for page in pages for item in page["check_runs"]]}
    require(len(pages) == 1, "unexpected paginated object")
    return pages[0]


def verify(root: Path, policy: dict, number: int, api: Api = gh_api) -> dict:
    """A policy and maintainer attestations are trusted boundaries, not PR inputs."""
    repository = policy["repository"]
    require(
        isinstance(repository, str) and re.fullmatch(r"[\w.-]+/[\w.-]+", repository),
        "invalid repository",
    )
    publishers = policy["publishers"]
    required_ci = policy["required_checks"]
    require(
        isinstance(publishers, list)
        and publishers
        and all(isinstance(x, str) and x.strip() for x in publishers),
        "publisher list required",
    )
    require(
        isinstance(required_ci, dict)
        and required_ci
        and all(
            isinstance(k, str) and k.strip() and type(v) is int and v > 0
            for k, v in required_ci.items()
        ),
        "required CI names/App identities required",
    )
    require(
        policy.get("context") == "harness-independent-review", "trusted status context required"
    )
    require(number > 0, "PR number required")
    require(
        isinstance(policy.get("harness_revision"), str)
        and re.fullmatch(SHA, policy["harness_revision"]),
        "fixed harness revision required",
    )
    prefix = "repos/" + repository
    collaborators = api(f"{prefix}/collaborators?per_page=100")
    require(
        isinstance(collaborators, list) and bool(collaborators), "write-authority audit unavailable"
    )
    require(
        all(
            actor["login"] in publishers
            for actor in collaborators
            if actor["permissions"].get("push") or actor["permissions"].get("admin")
        ),
        "untrusted status writers; dedicated trusted App/service required",
    )
    active_publishers = {
        actor["login"]
        for actor in collaborators
        if actor["permissions"].get("push") or actor["permissions"].get("admin")
    }
    permissions = api(f"{prefix}/actions/permissions/workflow")
    require(
        permissions["default_workflow_permissions"] == "read"
        and permissions["can_approve_pull_request_reviews"] is False,
        "workflow permission boundary drifted",
    )
    pr = api(f"{prefix}/pulls/{number}")
    require(isinstance(pr, dict) and pr["state"] == "open", "current open PR required")
    require(
        type(pr.get("commits")) is int and 0 < pr["commits"] <= 250,
        "complete contributor audit requires at most 250 PR commits",
    )
    head, base, merge = pr["head"]["sha"], pr["base"]["sha"], pr["merge_commit_sha"]
    require(
        all(isinstance(s, str) and re.fullmatch(SHA, s) for s in (head, base, merge)),
        "candidate SHA unavailable",
    )
    require(git(root, "rev-parse", "HEAD").strip() == head, "checkout must equal current PR head")
    require(not git(root, "status", "--porcelain").strip(), "dirty candidate checkout")
    statuses = api(f"{prefix}/commits/{head}/statuses?per_page=100")
    require(isinstance(statuses, list), "status list required")
    selected = next((s for s in statuses if s.get("context") == policy["context"]), None)
    require(
        selected is not None and selected.get("state") == "success",
        "trusted review missing or not successful",
    )
    publisher = selected["creator"]["login"]
    require(
        publisher in publishers and publisher in active_publishers,
        "status publisher not trusted or revoked",
    )
    match = re.fullmatch(
        re.escape(f"https://github.com/{repository}/blob/") + f"({SHA})/review-evidence.json",
        selected.get("target_url", ""),
    )
    require(match is not None, "review must reference an immutable controlled record")
    source_sha = match.group(1)
    require(
        source_sha not in {head, base, merge} and not (root / "review-evidence.json").exists(),
        "review approval cannot be a candidate file",
    )
    comparison = api(f"{prefix}/compare/{source_sha}...{head}")
    require(
        comparison["status"] in {"behind", "diverged"},
        "review record must be outside candidate history",
    )
    content = api(f"{prefix}/contents/review-evidence.json?ref={match.group(1)}")
    require(
        isinstance(content, dict) and content.get("encoding") == "base64",
        "immutable review unavailable",
    )
    payload = json.loads(base64.b64decode(content["content"], validate=False))
    binding = payload["binding"]
    require(payload.get("schema_version") == 1, "attestation schema mismatch")
    require(
        binding
        == {
            "repository": repository,
            "pull_request": number,
            "head_sha": head,
            "base_sha": base,
            "merge_sha": merge,
        },
        "head/base/merge candidate mismatch",
    )
    require(payload["publisher"] == publisher, "publisher attestation mismatch")
    snapshot, review = payload["snapshot"], payload["review"]
    adopted = config(root, snapshot["config"])
    require(
        set(adopted["required_checks"]) == set(required_ci)
        and adopted["standard_version"] == policy["harness_revision"],
        "candidate changed trusted adoption/CI policy",
    )
    require(snapshot["base"] == base, "snapshot base mismatch")
    require(pr["user"]["login"] in snapshot["authors"], "PR author omitted")
    commits = api(f"{prefix}/pulls/{number}/commits?per_page=100")
    require(
        isinstance(commits, list) and len(commits) == pr["commits"],
        "PR commits incomplete; contributor audit blocked",
    )
    for commit in commits:
        for role in ("author", "committer"):
            actor = commit.get(role)
            identity = actor.get("login") if actor else "git:" + commit["commit"][role]["email"]
            require(identity in snapshot["authors"], "actual contributor omitted from authors")
    reports = payload["reports"]
    require(isinstance(reports, list) and reports, "raw independent report required")
    for report in reports:
        require(
            isinstance(report["text"], str) and bool(report["text"].strip()), "empty raw report"
        )
        require(
            hashlib.sha256(report["text"].encode()).hexdigest() == report["sha256"],
            "raw report digest mismatch",
        )
    requirement_ids = payload["requirements"]
    require(
        isinstance(requirement_ids, list)
        and requirement_ids
        and all(
            isinstance(k, str) and re.fullmatch(r"REQ-[a-f0-9]{16}", k) for k in requirement_ids
        ),
        "requirement evidence references required",
    )
    catalog = read_json(HARNESS_ROOT / "docs/harness-requirements.json")
    require(
        set(requirement_ids) <= {row["id"] for row in catalog["requirements"]},
        "unknown requirement evidence reference",
    )
    result = gate(root, snapshot["config"], snapshot, review)
    runs = api(f"{prefix}/commits/{head}/check-runs?per_page=100")
    require(isinstance(runs, dict), "check run response required")
    checks = runs["check_runs"]
    observations = {}
    for name, app in required_ci.items():
        matching = [run for run in checks if run.get("name") == name]
        require(bool(matching), f"{name}: actual CI missing")
        current = max(matching, key=lambda run: run["id"])
        require(
            current["head_sha"] == head and current["app"]["id"] == app,
            f"{name}: CI candidate/App mismatch",
        )
        require(
            current["status"] == "completed" and current["conclusion"] == "success",
            f"{name}: actual CI incomplete or failed",
        )
        observations[name] = {"id": current["id"], "url": current["html_url"], "app_id": app}
    # Close races: evidence and checks must still belong to the current server candidate.
    final = api(f"{prefix}/pulls/{number}")
    require(
        final["state"] == "open" and not final.get("merged", False), "PR closed during verification"
    )
    require(
        (final["head"]["sha"], final["base"]["sha"], final["merge_commit_sha"])
        == (head, base, merge),
        "candidate changed during verification",
    )
    return {
        **result,
        "binding": binding,
        "publisher": publisher,
        "source_url": selected["target_url"],
        "observed_ci": observations,
        "authorization": "no merge or production authorization",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        policy = read_json(outside(root, args.policy))
        require(
            git(HARNESS_ROOT, "rev-parse", "HEAD").strip() == policy["harness_revision"]
            and not git(HARNESS_ROOT, "status", "--porcelain").strip(),
            "trusted harness checkout not fixed or clean",
        )
        result = verify(root, policy, args.pr)
        output = outside(root, args.output)
    except (OSError, KeyError, TypeError, ValueError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"status": "blocked", "error": str(error)}, ensure_ascii=False))
        return 1
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
