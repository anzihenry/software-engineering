---
title: "Documentation tooling and CI integration"
status: current
owner: process-owner
updated: "2026-10-09"
---

# Documentation tooling and CI integration

[中文](documentation-tooling.md)

## Entry point and asset boundary

The [checker](../scripts/documentation_check.py) executes first-layer rules from a fixed harness checkout against a separate project. It does not edit project files, modify the installer, or reorganize this asset repository. Use existing Python 3.14 and PyYAML 6.0.3, for example the harness virtual environment. Existing `scripts.development check` runs behavior tests through unittest.

## Configuration and inventory

Fill the [configuration example](../templates/documentation/documentation-check.json) as project `docs/documentation-check.json`; link it from bilingual docs/documentation and explain ownership and execution. schema_version is 1; standard_version identifies the actual fixed commit, owners maps metadata roles to real maintainers, and required_checks names real mandatory project checks (an empty list needs a documented explanation if none exist). documents lists primary Chinese paths with knowledge/initiative/release types; English counterparts use `.en.md`. Optional translations maps primary paths to language-code lists (for example `"README.md": ["ja"]`); only declared additional translations and their same-language navigation are required. Register README, CHANGELOG, docs/README and docs/documentation. Add directories only as needed and register domain README entries with navigation in both languages. Deeper directories may use the nearest registered bilingual index instead of adding an entry.

Every Git-visible Markdown file must be registered as documents, legacy or raw. Each legacy file has owner, reason, due (ISO date), and evidence (an existing repository-relative evidence file); inventories cannot overlap or be overdue. Legacy files changed against base must migrate immediately. raw has the same fields except due and is only for original materials/generated reports. Independent review must verify this classification; maintained documents cannot evade rules through raw. Preserve original evidence once and link it from bilingual explanations.

Checks cover metadata, type-specific states, dates, owner mappings, naming, pairs/backlinks, same-language links, relative files/headings, bilingual navigation, and complete registration. Supported Markdown includes common inline links, reference definitions, ATX headings and explicit HTML ids. This is not a full renderer: use supported syntax for Setext/custom anchors or perform additional independent checks without claiming full rendering coverage. Translation meaning, state explanations and factual correctness remain independent review responsibilities.

## Three-step delivery

Run outside the target project. HARNESS is a fixed checkout, PROJECT is the Git root, and BASE is the full actual comparison commit. Do not choose a base that hides real changes. Keep outputs and review JSON outside the target to avoid digest cycles. Nonignored untracked files also enter the snapshot.

```sh
"$HARNESS/.venv/bin/python" "$HARNESS/scripts/documentation_check.py" check --root "$PROJECT" --base "$BASE"
"$HARNESS/.venv/bin/python" "$HARNESS/scripts/documentation_check.py" snapshot --root "$PROJECT" --base "$BASE" --author author-id --output /tmp/documentation-snapshot.json
"$HARNESS/.venv/bin/python" "$HARNESS/scripts/documentation_check.py" gate --root "$PROJECT" --snapshot /tmp/documentation-snapshot.json --review /tmp/documentation-review.json --output /tmp/documentation-gate.json
```

1. Authors run actual project tests and save real reports under applicable evidence locations, synchronize documents and configuration, then check/snapshot. Repeat --author for every actual author/modifier. Snapshots include all Git tracked and nonignored untracked paths, deletions, executable modes, base, authors, configuration and changed paths. Ignored runtime outputs are outside the snapshot; delivery evidence must be Git-visible and implementation changes must not be hidden by ignore rules. Git submodules and symlinks currently block adoption until explicitly handled.
2. A nonauthor independently reads implementation, changed/deleted diffs, all registered documents and evidence. Fill the [review JSON](../templates/documentation/independent-review.json) and [shared checklist](../templates/documentation/delivery-check.en.md) with actual conclusions. A deleted inspected_files path means its deletion diff was read. All five checks must pass and reference existing, inspected snapshot files in evidence_files; required_checks must exactly match configuration and pass. All nine impact domains require treatment, rationale and files. Findings require resolved status and actual recheck. Never invent tests or automatically approve. Track unrelated preexisting issues separately with reasons they do not affect delivery.
3. gate rechecks documents and the entire snapshot, independent identity/context, inspection scope, impacts, evidence, mandatory checks and finding rechecks. Every change, including evidence changes, invalidates approval: regenerate the snapshot and obtain reviewer confirmation. Only JSON status=passed with exit 0 passes; failures exit 1 with blocked and a reason. check proves structure only and cannot replace gate.

Identity, author lists, independence and check outcomes are attestations. The tool validates consistency rather than authenticating people or proving execution; the actual review process, controlled CI and permissions must establish provenance. Reviewers produce review JSON; authors cannot fill their own approval. A file snapshot is neither a signature nor platform human approval.

Record identity/role, timezone-aware reviewed_at and the independent context.

## CI and trusted provenance

The [reusable workflow](../templates/documentation/documentation-gate.yml) provides a documentation-gate job running the same gate on the current event checkout; harness_revision must be a full SHA. Copy it into project .github/workflows and use a protected caller supplying the fixed harness repository/revision and current-candidate snapshot_json/review_json. Base must be available in fetched history. Reviewed files must match the actual CI checkout, including a PR merge tree; branch-head approval cannot substitute for merge-tree approval.

The caller must obtain records from a trusted independent reviewer/service and verify identity, actual authors/base, candidate/run binding and genuinely completed mandatory CI. Never trust passed records from PR-author-editable files or arbitrary user input. Do not execute untrusted code through pull_request_target or give the checker write privileges/production secrets. The template validates mechanical consistency and does not create a trusted review service. Missing trusted records must block.

Configure the actual job as required in branch protection/rulesets, verify passing and missing-translation/stale-review failures, and retain real Actions runs and rule-setting evidence before claiming remote enforcement. Existing project tests and human release authority retain their responsibilities. This stage supplies the local tool and CI template; no target remote rules were enabled and no Actions run is claimed.

## Adoption validation

Use an isolated Git project to execute the actual CLI, retain test output, obtain independent review, pass gate, then break translation/implementation bindings to verify failures. Do not create product directories in this harness. Unit tests cover missing translation, broken anchors, missing English navigation, duplicate configuration, symlinks, unregistered/touched legacy files, stale snapshots, self-review, unread files, missing evidence, failed mandatory checks, deletions and permission changes. Evidence only supports the tested revision/environment; other projects need their own adoption records.
