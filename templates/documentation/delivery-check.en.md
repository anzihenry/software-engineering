---
title: "Documentation delivery check template"
status: current
owner: process-owner
updated: "2026-10-09"
---

# Documentation delivery check template

[简体中文](delivery-check.md)

## Delivery object and traceability

- Record ID/type: `<stable ID, documentation delivery check>`.
- Record status: `<pending/failed/passed; separate from document frontmatter status>`.
- Object, scope, gate: `<change/initiative/version; merge/completion/publication>`.
- Owner and decision authority: `<responsible and authorized roles>`.
- Risk: `<low/medium/high/not applicable with reason>`.
- Related records: `<requirements, design, VER/CHG/REL, PR>`.
- source_version: `<repository, full base/head SHAs, artifact digest; uncommitted snapshots list paths and SHA-256>`.
- environment_scope: `<platform, environment, users>`.
- evidence: `<single locations for reports and review>`.
- created_at / updated_at: `<actual timezone-bearing timestamps>`.

## Documentation impact

Assess every domain and expand to actual files. Reviewed-no-change and not-applicable require reasons.

| Domain | Chinese and English files | Disposition | Reason and evidence |
| --- | --- | --- | --- |
| research | `<paths>` | `<updated/reviewed-no-change/not-applicable>` | `<basis>` |
| product | `<paths>` | `<disposition>` | `<basis>` |
| design | `<paths>` | `<disposition>` | `<basis>` |
| engineering | `<paths>` | `<disposition>` | `<basis>` |
| guides | `<paths>` | `<disposition>` | `<basis>` |
| planning | `<paths>` | `<disposition>` | `<basis>` |
| initiatives | `<paths>` | `<disposition>` | `<basis>` |
| releases / CHANGELOG | `<paths>` | `<disposition>` | `<basis>` |
| Entries, configuration, navigation | `<paths>` | `<disposition>` | `<basis>` |

## Mechanical checks

| Mandatory item | Actual command/tool and scope | Result | Evidence and snapshot |
| --- | --- | --- | --- |
| Metadata and valid states | `<actual check>` | `<passed/failed/not run>` | `<report>` |
| Names, links including sections, navigation | `<actual check>` | `<result>` | `<report>` |
| Bilingual pairs and matching owner/status | `<actual check>` | `<result>` | `<report>` |
| Project required CI | `<actual check>` | `<result>` | `<report>` |

Explicitly identify missing implementations or unexecuted checks, never mark them passed. Actual execution and reports provide evidence; checkboxes do not prove execution.

## Independent content and translation review

- Reviewer identity, role, independence: `<human or independent Agent, not author/modifier; separate Agent context identifier>`.
- Reviewed commit/digest snapshot: `<matches delivery object>`.
- Implementation, documents, evidence actually read: `<file/report list; explain if no implementation change>`.
- Completeness of impact: `<verdict and basis>`.
- Current facts, procedures, applicable examples: `<implementation comparison, executed checks, or non-applicability>`.
- Chinese/English semantic consistency: `<item-by-item review, not just pair existence>`.
- Evidence provenance and versions: `<result>`.

## Findings and rechecks

| Finding | Owner | Fixed version | Independent recheck and evidence | Result |
| --- | --- | --- | --- | --- |
| `<finding>` | `<author>` | `<SHA/digest>` | `<reviewer recheck>` | `<resolved/unresolved>` |

Track unrelated existing problems separately with reasons they do not affect delivery. Required documentation, translation, and evidence gaps cannot be waived.

## Final verdict

- Verdict: `<passed/failed>`.
- Confirming reviewer and date: `<identity, actual date>`.
- Outstanding work and next actions: `<none or details>`.
- Passing requires complete impact, passed mandatory checks and independent review, synchronized English, and no required documentation gaps.
- Invalidation: relevant modifications require rechecking affected parts; do not reuse stale snapshot conclusions.

Embed in PRs or initiative validation/README; releases link to the record. Both languages reference shared command output and evidence instead of copying reports.

## Template use constraints

Metadata here describes a harness template. Set actual title/owner/updated and the appropriate object status in project documents, replace placeholders, and verify every link. See the [template entry](README.en.md).

## Tool execution contract

Register configuration, actual checks and independent-review JSON using the [tooling guide](../../docs/documentation-tooling.en.md). Passing check is not delivery approval; run gate for delivery.
