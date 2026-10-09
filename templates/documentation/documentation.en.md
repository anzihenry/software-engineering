---
title: "Project documentation configuration template"
status: current
owner: process-owner
updated: "2026-10-09"
---

# Project documentation configuration template

[简体中文](documentation.md)

## Use

Copy to target-project docs/documentation.md together with English. Reference common rules and fill execution configuration; preserve existing project content. Replace template metadata and all placeholders. Never claim unconfigured checks are enabled.

## Adoption basis

- Standard version: `<fixed version or full commit>`.
- Standard location: `<accessible immutable source>`.
- Scope and migration: `<scope, inventory, owner, completion criteria>`.

## Ownership

| Domain or role | Responsible person/team | Document scope |
| --- | --- | --- |
| `<role>` | `<owner>` | `<scope>` |

## Execution configuration

- Primary language: Chinese; default translation: English; additional languages: `<as needed>`.
- Task source of truth: `<issue/project system/initiative plan>`.
- Mechanical commands and actual coverage: `<commands, scope>`.
- Required CI checks: `<names and current-commit binding>`.
- Independent review and record location: `<human/independent Agent, record>`.
- Merge, initiative-completion, publication responsibilities: `<owners and actual gates>`.
- Periodic review: `<interval, reminders, review-needed flag>`.
- External material locations and access: `<locations, identity, sensitive-material boundary>`.

## Tailoring and migration

Record differences limited to optional practices. Required documentation, translations, evidence, and independent review cannot be waived. Migration tasks identify owners, timing, completion criteria, and acceptance evidence.

## Template use constraints

Metadata here describes a harness template. Set actual title/owner/updated and the appropriate object status in project documents, replace placeholders, and verify every link. See the [template entry](README.en.md).

## Tool execution contract

Register configuration, actual checks and independent-review JSON using the [tooling guide](../../docs/documentation-tooling.en.md). Passing check is not delivery approval; run gate for delivery.
