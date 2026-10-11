---
title: "Delivery evidence record template"
status: current
owner: process-owner
updated: "2026-10-11"
---

# Delivery evidence record template

[中文](evidence-record.md)

## Traceability and execution

- record_id, record_type, record_status, owner, decision_authority, risk_level:
- related_records, requirement_id and original applicability scope:
- source_version: repository, full head/base/merge SHAs and snapshot digest; candidates also need artifact digest/build run, deployments need deployment ID/configuration/scope; explain inapplicable fields.
- environment_scope, tool/dependency/data baseline, method and actual reading/execution scope:
- created_at, updated_at and actual executed_at with timezone:
- evidence: immutable original report location, digest, access control and identity source:
- Original result: passed | failed | not-run | blocked | stale | not-applicable (rule and factual reason):
- Simulation/real-state boundary, uncovered scope, reuse rationale, invalidation conditions and revalidation owner:

## Independent source and conclusion

- Authors/modifiers, independent reviewer, separate context and actual materials inspected:
- Trusted publisher, controlled-source verifier, identity/permission/candidate/actual CI observations:
- Findings, author corrections, independent recheck and final current-version conclusion:
- Reference independent review and human authorization separately; entry by an author cannot self-approve passed.

Follow the [evidence contract](../../docs/evidence-trust.md) (Chinese), reuse the existing documentation review schema, and avoid duplicating task state.
