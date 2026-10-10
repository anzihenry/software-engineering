---
title: "Default GitHub repository governance"
status: current
owner: quality-lead
updated: "2026-10-10"
---

# Default GitHub repository governance

[中文](github-repository-defaults.md)

## Defaults and scope

GitHub projects developed with this harness must enable these two settings by default, without requiring users to request them for every project:

1. Protect the default branch. New projects default to `main`; existing projects protect their actual default branch without automatically renaming it. Effective rules require PRs, real required checks, validation against the latest default branch, and resolved review conversations; prohibit force pushes and deletion; and default to no bypass.
2. Enable repository `delete_branch_on_merge=true` so GitHub automatically deletes eligible remote feature branches after PR merge. This does not clean up historical or local branches, nor guarantee deletion of protected branches or fork branches in other repositories.

This is a default adoption requirement of the first-layer development process, reusing existing second- and third-layer implementations. Loading the harness, copying instructions, or installing files does not change GitHub settings. Report governance complete only after actual application and read-back verification. PR merge, publication, and deployment are not automatic.

## Default routing

- On first adoption or setting drift, use the [repository bootstrap skill](../skills/05-integration-validation/github-repository-bootstrap/SKILL.md) to inspect, plan, and verify. Reuse existing CI with trustworthy stable checks; otherwise use the [Actions bootstrap skill](../skills/05-integration-validation/github-actions-bootstrap/SKILL.md) to obtain successful check/App evidence on the first PR's current head SHA before configuring protection, avoiding nonexistent required checks.
- Full adoption through the cross-project installer defaults to `full`; select `governance` when only governance is needed. Both existing implementations configure these settings. Explicit `incident` or `release` selections retain their limited responsibilities without additional writes. Completing a partial installation does not establish full harness governance compliance; use the repository bootstrap skill separately.
- For each target repository, confirm identity, administration permission, plan capabilities, and existing organization/repository rules. Perform necessary authorized writes without requesting authorization again when already explicit. Loading the harness alone does not authorize arbitrary remote writes; prepare reviewable differences before obtaining missing authorization. Report incomplete governance and the smallest unblock action when permission, capabilities, real checks, or compatible rules are missing. Do not bypass or weaken existing protection.
- Daily PRs check the baseline through [PR integration](../skills/05-integration-validation/github-pr-integration/SKILL.md) and [merge readiness](../skills/05-integration-validation/merge-readiness/SKILL.md). Route drift back to repository bootstrap instead of implicitly changing rules in daily PR workflows.

## Installer operation and verification

The installer already defaults to `full`; this example explicitly selects governance-only `governance`. In the target repository, after the installation PR remains Open and `validate` and `lifecycle-policy` succeed on its current head SHA, run:

```sh
python3 -m scripts.github_lifecycle bootstrap \
  --repository OWNER/REPOSITORY --profile governance --evidence-pr 123
```

Review the dry-run plan and apply within the authorized scope:

```sh
python3 -m scripts.github_lifecycle bootstrap \
  --repository OWNER/REPOSITORY --profile governance --evidence-pr 123 \
  --no-dry-run --confirmation bootstrap:OWNER/REPOSITORY
python3 -m scripts.github_lifecycle doctor \
  --repository OWNER/REPOSITORY --profile governance --evidence-pr 123
```

Replace repository and PR placeholders; install the shared tools and policy in the target repository through [Getting started](getting-started.md) first (Chinese). `doctor` must be healthy. Projects using only first-layer skills verify through repository bootstrap and need not install the full automation package merely to enable these settings.

## Completion evidence

Record the target repository, actual default branch, read time, rule ID/link, effective rules, required check/App and current commit evidence, and read-back `delete_branch_on_merge=true` in the adoption/PR record. Also verify branch metadata `protected=true`. A 404 from traditional branch protection does not mean the branch is unprotected; read effective ruleset rules.

Merging the first bootstrap PR still requires the existing merge authorization. After merge, check deletion of its remote head ref before reporting that PR's actual cleanup success. An enabled setting and a deleted branch are separate evidence. Mark this requirement inapplicable for non-GitHub projects. Keep blocked GitHub adoption incomplete; local installation or dry-run is not proof of remote enforcement.
