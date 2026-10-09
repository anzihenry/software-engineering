---
title: "Documentation governance integration"
status: current
owner: process-owner
updated: "2026-10-09"
---

# Documentation governance integration

[简体中文](documentation-integration.md)

## Capability and boundary

Documentation is now a default first-layer harness requirement, routed through entry instructions, all eight workflows, maintenance/independent-validation skills, and delivery templates. Standard version 0.1.0: the [standard](documentation-standard.en.md) owns rules and [templates](../templates/documentation/README.en.md) own deliverable content. This stage does not change layer-two/three installers or GitHub policy, create target directories, or claim target CI enforcement.

## Harness availability

Relative links work in a full checkout. Plugin or standalone-skill distribution must also expose pinned rules, templates, and both skills, or use checked-in equivalents with real paths in project configuration. Copying only AGENTS, installing only the skills, or filling a checklist is not complete adoption. Report missing prerequisites rather than claiming compliance.

## Target entry

1. Merge documentation clauses from the [project AGENTS template](../templates/codex/AGENTS.md) into existing instructions, preserving rules and commands. Do not replace the whole file.
2. Use the [configuration template](../templates/documentation/documentation.en.md) to create/update docs/documentation and English, pinning sources and configuring roles, task system, checks, CI, review records.
3. New projects create directories as needed. Existing ones inventory migration; affected legacy documents comply with current deliveries, unrelated history migrates incrementally. The asset repository keeps docs/workflows, skills, templates.

## Lifecycle routing

| Stage | Documentation work | Completion basis |
| --- | --- | --- |
| Demand/research | Single original sources, requirement/initiative scope, study limitations | Traceable evidence, impact and ownership |
| Solution/planning | Initiative designs, long-term decisions, contracts/experience rules, bilingual validation tasks | Single definitions, planned updates and review |
| Implementation/handoff | documentation-maintenance updates knowledge, English, navigation, snapshot | Complete checklist preparation without self-approval |
| Merge validation | documentation-delivery-validation reads implementation, documents, omissions, evidence independently | Current-version documentation passes or merge blocks |
| Initiative completion | Acceptance, maintained knowledge/English, follow-up handoff | Passed check before completed |
| Publication | Version contents, compatibility/upgrade guidance, actual candidate/check evidence | Passed check before existing human Go/No-Go |
| Operations/retrospective | Update guides/findings; preserve history and restricted evidence | Corrections still checked, periodic review supplements gates |

[Maintenance](../skills/04-implementation-and-self-test/documentation-maintenance/SKILL.md) applies across phases; [independent validation](../skills/05-integration-validation/documentation-delivery-validation/SKILL.md) cannot run in the author context. Existing requirement, solution, handoff, PR review, merge-readiness, release-readiness/closure skills also route directly.

## Checks and reviews

Use one [checklist record](../templates/documentation/delivery-check.en.md): in PRs, initiative validation/README, linked from releases. Check metadata, states, naming, pairs, reciprocal/section links, navigation, then independently compare content, implementation, translations, and examples.

Use [tooling and CI integration](documentation-tooling.en.md) to execute check/snapshot/gate with actual scope, results and evidence; file existence is not semantic validation. Existing required CI needs real passing runs. Missing configuration, updates, English, evidence, independence, or valid snapshots blocks delivery; no conditional documentation pass.

Reviewers report findings, authors fix, reviewers recheck. Uncommitted work can bind paths and SHA-256; relevant changes invalidate results. AI review is not platform human approval, specialist authorization, or production Go/No-Go. Emergency recovery retains existing authorization but missing documentation acceptance cannot be labelled passed or completed.

## Asset maintenance and next validation

This repository's entry requires impact checks, affected bilingual standards/templates, routing, and independent review for harness assets while retaining existing governance states, review_by, and traceability. Target-project conventions do not wholesale rename or translate existing Chinese workflows/SKILLs. New maintenance/validation skills have English references; standards/templates stay bilingual.

Stage 3 now provides mechanical checks, review-record consistency gates, configuration and CI templates; adoption validation uses actual CLI execution and independent review in an isolated Git project. Routing alone does not prove successful Agent loading, platform enforcement, or universal adoption. Actual uses must retain loading and delivery evidence.
