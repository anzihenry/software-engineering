---
title: "Local delivery channel report template"
status: current
owner: release-manager
updated: "2026-10-12"
---

# Local delivery channel report

[中文](local-delivery-channel.md)

Replace placeholders according to the [local-channel contract](../../docs/local-delivery-channel.md) (Chinese) and actual project roles. This template is not execution evidence.

## Traceability, authorization and scope

- record_id / related_records / source_version / created_at / updated_at (with timezone):
- Fixed candidate/recovery commits, head/base/merge, artifact SHA, build times/raw logs/tools/configuration/dependencies/retention responsibility:
- Actual owner/executor/independent reviewer, specific local authorization and stop/recovery plan:
- target_id/role/UID/nonce/PID/actual port, runtime/browser-script digests; factual reasons for non-applicable platform fields:

## Raw evidence by stage

| Stage/actual time | Same artifact and target identity | config/ready/health/API/Web/browser raw records and SHA | Health window and finding | Stop/pause/recovery/cancellation and actual returncode |
| --- | --- | --- | --- | --- |

Retain baseline/candidate/failed/restored records. Distinguish controlled faults from actual incidents; failures and cancellations cannot become success. Missing authorization/identity/digest, tampering, concurrency, timeout or failed health block expansion. Recovery consumes the original previous artifact and rechecks key paths, without rebuilding at deployment. Stop only owned child processes.

## Limitations, documentation and handoff

Record synthetic scope, reasons for non-applicability, observation window, unverified platforms/identity/migrations/product effects and remaining issues. A local rehearsal is not a formal release or production authorization. Update affected guides/current documents and English, and independently verify source, artifact, tool and evidence snapshots. Retain failure history, recovered facts and subsequent revalidation tasks.
