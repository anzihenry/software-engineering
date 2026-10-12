---
title: "Domain validation record template"
status: current
owner: quality-lead
updated: "2026-10-12"
---

# Domain validation record template

[中文](domain-validation.md)

## Traceability and admission

- record_id, record_type, record_status, owner, decision_authority, risk_level:
- related_records, requirement_id and full source clause, trigger and actual project facts:
- source_version: full head/base/merge or file-digest snapshot; artifact/deployment identity where applicable:
- created_at, updated_at, executed_at (with timezone):
- Complete domain applicability inventory; scenario, support matrix, tool/actor, threshold and failure action:


- For each part of a compound clause, record its trigger, applicability, factual reason and scenario; a generic domain reason is insufficient:

## Actual execution and evidence

- environment_scope, versions, data, baseline approval, commands and raw evidence locations/digests:
- Every applicable scenario: observation, passed/failed/not-run/blocked/stale/not-applicable and factual reason:
- Real boundaries versus substitutes, unsupported scope, invalidation and revalidation owner:
- Independent reviewer, actual reading, content/translation findings, corrections and current-snapshot conclusion:

Use the [domain contract](../../docs/domain-validation.md) (Chinese source) and [existing verification matrix](../delivery/verification-matrix.md). Do not replace P0 gates, required CI, independent approval or human decisions. Preserve raw reports; schema 1 consumers check consistency only.
