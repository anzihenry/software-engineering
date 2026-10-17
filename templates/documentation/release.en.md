---
title: "Version release record template"
status: current
owner: process-owner
updated: "2026-10-16"
---

# Version release record template

[简体中文](release.md)

## Version and status

`<Version/event; planned/verified/released/cancelled/withdrawn in target frontmatter>`.

## Contents

`<Features, changes, fixes, initiative links>`.

## Compatibility and user guidance

`<Breaking changes, upgrade/recovery guides, limitations; user action if withdrawn>`.

## Candidate and evidence

- Source commit: `<full SHA>`.
- Artifact identity: `<name and digest>`.
- Acceptance: `<environment, method, result, report>`.
- Documentation delivery check: `<passed record for current version>`.

## Release scope and conclusion

- Primary release record: `<REL ID/revision and single record link; candidate/authorization/batch/health/recovery/phase 07 evidence stays in that record>`.
- Approved target and actual scope: `<environments/platforms/channels/regions; review/listing/availability/installation facts and combined target>`.
- Post-release verification and observation: `<actual critical-path/data results, time/minimum samples and health conclusion>`.
- Process and outcome: `<delivered successfully/cancelled/failed and recovered/failed and transferred to incident response; paused/recovering remains open; original change delivery facts>`.
- Recovery and compatibility: `<actual recovery version/data/remaining impact; compatibility window, cleanup conditions and owners>`.
- Operational acceptance and follow-ups: `<recipient/time with timezone, support/monitoring/recovery limits, follow-up owners/deadlines/criteria and authorized notification evidence>`.

Document states such as planned/verified/released describe candidate acceptance and actual distribution separately from release authorization and the eight success criteria. Candidate changes require updated revisions/evidence. Record actual distribution even when closure is incomplete; restoring an old version does not deliver the original feature.

## Actual publication or termination

`<Actual time, address, evidence; explicitly unpublished if not done; cancellation/withdrawal reasons>`.

## Traceability

`<REL record and authorized decision; document status does not replace release Go/No-Go>`.

## Template use constraints

Metadata here describes a harness template. Set actual title/owner/updated and the appropriate object status in project documents, replace placeholders, and verify every link. See the [template entry](README.en.md).
