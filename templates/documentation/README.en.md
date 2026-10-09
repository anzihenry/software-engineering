---
title: "Project documentation templates"
status: current
owner: process-owner
updated: "2026-10-09"
---

# Project documentation templates

[简体中文](README.md)

## Asset boundary and stage

These are first-layer harness templates for the [documentation standard](../../docs/documentation-standard.en.md). Target projects adopt them as needed; software-engineering does not create target-project directories itself. The current installer does not distribute this directory.

The standard and templates now route through harness entry instructions, all eight workflows, and SKILLs; see [integration](../../docs/documentation-integration.en.md). Target-project checks, configuration and CI templates are available through [tooling integration](../../docs/documentation-tooling.en.md). Templates cannot replace actual checks or independent review.

## Templates

| Template | Suggested target file |
| --- | --- |
| [Project documentation configuration template](documentation.en.md) | `documentation.md` + `.en.md` |
| [Project entry template](project-readme.en.md) | `project-readme.md` + `.en.md` |
| [Change summary template](changelog.en.md) | `changelog.md` + `.en.md` |
| [Documentation index template](index.en.md) | `index.md` + `.en.md` |
| [Maintained knowledge template](knowledge.en.md) | `knowledge.md` + `.en.md` |
| [Initiative entry template](initiative.en.md) | `initiative.md` + `.en.md` |
| [Requirements template](requirements.en.md) | `requirements.md` + `.en.md` |
| [Research template](research.en.md) | `research.md` + `.en.md` |
| [Design template](design.en.md) | `design.md` + `.en.md` |
| [Execution plan template](plan.en.md) | `plan.md` + `.en.md` |
| [Technical decision template](decision.en.md) | `decision.md` + `.en.md` |
| [Version release record template](release.en.md) | `release.md` + `.en.md` |
| [Validation record template](validation.en.md) | `validation.md` + `.en.md` |
| [Documentation delivery check template](delivery-check.en.md) | `delivery-check.md` + `.en.md` |

Use project-readme for root README, changelog for root CHANGELOG, index for directory README, initiative for initiative README, numbered names for decisions, and release for version README. Other names follow the topic; these are not mandatory copied asset filenames.

## Adoption steps

1. Record immutable standard provenance, scope, ownership, and execution in target docs/documentation.
2. Create only directories with actual content. Use both languages, actual metadata, valid object states; remove template-use notes and every placeholder.
3. Add navigation and check same-language relative links; adjust translation links when renaming target files.
4. Combine small initiatives without losing required content; explain non-applicable items.
5. Use delivery-check with a non-author independent reviewer. Run check/snapshot/gate and record actual methods and evidence; never invent automated results.

## Existing delivery templates

[Lifecycle delivery templates, Chinese source](../delivery/README.md) retain record IDs, risk, decision authority, environment, related records, and evidence. Documentation templates govern location and content, not replacements for existing record contracts. When combined, retain traceability fields and separate document status from record status, and updated date from timezone-bearing updated_at.

Keep raw reports once with bilingual entries or summaries. Asset metadata describes the template; adopted metadata describes the target document.

## Execution assets

- [Configuration](documentation-check.json)
- [Independent review record](independent-review.json)
- [CI workflow](documentation-gate.yml)
- [Tooling guide](../../docs/documentation-tooling.en.md)
