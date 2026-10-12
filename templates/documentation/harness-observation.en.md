---
title: "Harness observation and revalidation report template"
status: current
owner: process-owner
updated: "2026-10-12"
---

# Harness observation and revalidation report

[中文](harness-observation.md)

Replace all placeholders in the target project, using the [observation definitions](../../docs/harness-observation.md) (Chinese) and actual project roles. This template is not evidence.

## Traceability and scope

- record_id / related_records / source_version / created_at / updated_at (with timezone):
- Actual owner, executor, independent reviewer, policy and support-matrix digests:
- Raw locations and immutable digests, observation window `[from, until)`, actual collection times:
- Candidate head/base/merge, environment, platform and check kind; explain factual non-applicability:

## Metrics and limitations

| Metric | Definition, numerator/denominator, unit | Actual raw source/cohort | Samples/raw values and finding | Missing, cancelled, failed, unknown and limitations |
| --- | --- | --- | --- | --- |

Record requirement coverage only when every required mapped case passes; false blocks among independently reviewed blocked samples and the unreviewed count; raw blocking reasons; all actual check durations and reruns within the window; overdue and closed revalidations. Show no data for zero or unknown denominators. Separate policy/version/environment cohorts, deduplicate identical events and retain reruns. Two short-window observations do not prove improvement. These are not product SLOs, personal performance ratings or quality approval.

## Revalidation closure

| Object/actual owner | Baseline/current ten-field fingerprints, change reasons and current_since | Deadline/review time | Remedy/effect criterion | Actual fresh evidence, non-author review and state |
| --- | --- | --- | --- | --- |

Retain old fingerprints and raw reports. Check entry, knowledge, requirements, commands, dependencies, environment, support, roles, permissions, rules and review expiry individually. Unexecuted work, missing evidence or old versions cannot close an object. Do not change dates automatically, waive gates or claim recurring tasks are enabled.

## Independent verification

Record actual reading/recalculation methods, identity and snapshot, documentation impact, bilingual meaning, findings and rechecks. Current closure requires verification of effectiveness and origin; matching hashes do not authenticate execution. Observation findings and merge/production authorization are separate decisions.
