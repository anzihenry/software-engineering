---
template_name: verification-matrix
template_version: 1
lifecycle_stages: [3, 4, 5]
traceability_fields:
  - record_id
  - record_type
  - status
  - owner
  - decision_authority
  - risk_level
  - related_records
  - source_version
  - environment_scope
  - evidence
  - created_at
  - updated_at
---

# Verification matrix

[中文](verification-matrix.md)

Reuse one record/stable ID across Phase 03 planning, Phase 04 execution and Phase 05 independent aggregation. Planning is not an executed pass; solution/development approval is not verification or release approval. Follow [Phase 03](../../docs/workflows/03-solution-and-planning.md), [Phase 04](../../docs/workflows/04-implementation-and-self-test.md), [Phase 05](../../docs/workflows/05-integration-validation.md) and [quality gates](../../docs/quality-gates.md) (Chinese). Retain every traceability field, justify inapplicability with facts, and invent no data or authority. Template metadata is not actual verification state.

## Traceability

- Record ID:
- Record type: verification matrix
- Record status: planning | executing | passed | conditionally passed | failed | blocked
- Owner:
- Decision authority: actual person/role, authority source and decision point/scope
- Risk level: low | medium | high
- Related records: current requirements, solution, plan, change, PR and applicable exception IDs/versioned links
- Source/artifact version: current repository/head SHA/build/artifact digest; explain inapplicability
- Environment and scope: platforms, support matrix, tenants/users and reviewed scope
- Evidence: actual raw reports/commands/logs/screenshots/metrics/manual records bound to object/version/time
- Created at with timezone:
- Updated at with timezone:

## Verification baseline and required points

- Requirement/solution/plan revisions and target source/artifact, environment, dependency/test-data versions:
- Production differences, support matrix, actual baseline/threshold sources and limitations:
- Automation/manual boundaries, actual project commands/configuration and evidence locations:
- Critical feasibility/professional evidence required before development in Phase 03; verification possible only during later implementation/integration/release, with reasons:
- Complete mandatory set and domain triggers for this point; missing tools/environment/permission/evidence do not mean inapplicability; production observation does not replace mandatory prerequisite validation:

## Requirement and risk mapping

| Requirement/risk ID and source | Scenario and expected outcome | Verification layer/method/actual command | Environment/data/version | Judgment/threshold and basis | Owner/automation and required point | Required evidence and failure stop scope |
| --- | --- | --- | --- | --- | --- | --- |

Cover applicable normal, boundary, failure, authorization, compatibility, migration, cancellation/recovery risks. Qualitative criteria are valid when decidable; missing critical criteria return to Phase 02. State mock/small-scale/unrepresentative-environment limits; mock success does not establish real integration or production-scale capability. Research coding follows Phase 03 independent-worktree rules; preserve evidence before cleanup and link actual closure facts.

## Actual execution and independent verification

| Requirement/risk ID and execution point | Actual object/version/environment/data | Actual command/method and timestamp with timezone | Current-version raw evidence/digest and limitations | Actual individual result and reason/basis | Executor, independent verification and failure/retest actions |
| --- | --- | --- | --- | --- | --- |

Retain quality-gate states: passed, failed, not-run, blocked, stale, and not-applicable supported by both rules and facts. Phase 03 planning without execution evidence remains not-run. Existing research measurements describe only their tested objects/limits; do not copy them as later test passes. Phase 04 records real execution, Phase 05 has a nonauthor verify the complete set and current evidence. Identify stale scope and retest after environment/version/acceptance changes; old reports cannot cover new candidates.

## Conclusions by point and follow-up work

- Current decision point, version/scope, actual check set, overall conclusion/responsible person/authority source/time:
- Normal, boundary, failure, authorization, compatibility, migration and recovery coverage, including uncovered scope:
- Actual completion of prerequisites now; owners/required points/evidence/failure stop actions for later mandatory work:
- Environment limits, original failures, applicable exception rules/authority/expiry/remediation and reassessment:
- Related requirement/solution/plan changes, invalidated evidence, work that may continue/must wait and next actions:

“Conditionally passed” expresses remaining limitations in the applicable domain only. Under quality gates it grants no merge/release approval and waives no required documentation, translation, evidence, independence, mandatory CI or high-risk/production authorization. Planning completion, solution approval, development approval and executed verification concern separate objects, not one combined pass.

## Documentation delivery check

- Authoritative check: complete or link the [documentation delivery check](../documentation/delivery-check.en.md); retain this matrix's traceability fields without duplicating conclusions:
- File-level impact, Chinese/English updates and reasons for unchanged/inapplicable items:
- Actual mechanical checks and current commit/artifact or complete digest snapshot:
- Nonauthor reviewer identity/actual reading/evidence, corrections/review and timestamp:
- Conclusion: passed | blocked; revalidate related changes. Required documentation, translations, evidence and independence cannot be waived. Never invent results for unimplemented/unexecuted checks:
