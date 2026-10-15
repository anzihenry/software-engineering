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

## Phase 05 end-to-end sets and actual merge objects

- Complete core, change-specific and risk-specialized case IDs/maintainers, acceptance/risks, environment/initial data/dependencies, observable criteria and failure contacts; basis for deduplicating overlapping cases:
- Real business entry → applicable internal UI/services/database/messages → final user outcome and data invariants; asynchronous completion conditions/timeouts:
- External test environment/mock contracts, substituted boundaries and uncovered scope; do not mark a key risk passed when the substitute hides that risk:

| Feature/PR and execution node | head/base and actually tested source/build, or actual main merge SHA | Required cases/criteria and itemized coverage | Environment/dependency/data identity | Actual run/command/time/executor/exit code and original result | Evidence/digest, owner and failure/rerun action |
| --- | --- | --- | --- | --- | --- |

Every feature merge requires actual core and change-specific end-to-end execution both before merge and after merging to main. Pre-merge success cannot replace post-merge execution. Consecutive A/B merges each retain exact objects and full cases; a later green B does not automatically cover A. Shared reports identify the actual tested version, included merges and itemized coverage basis without removing any merge's obligation. Preserve original cancellation/timeout/not-triggered/incorrect-skip results and rerun the specified object; do not silently drop execution. Missing tools/environments are not inapplicability. Fix budgets/criteria before observing results; do not delete tests, relax thresholds or quarantine required cases without effective equivalent evidence to manufacture a pass.

## Independent review and integration closure

- Actual nonauthor identity/independence, reviewed object, actual requirements/design/diff/call-path/test/raw-result reads, reviewed/uncovered scope and re-review conditions:
- Six areas: scope/acceptance; implementation/failure/concurrency/resources; contracts/authorization/invariants; test/end-to-end sufficiency; runtime/migration/recovery; documentation/translations/current evidence:

| Feedback, trigger/observable consequence/basis | Category | Actual fix or evidence that the finding is invalid | Nonauthor re-review/version | Follow-up task/owner/decision |
| --- | --- | --- | --- | --- |

Categories are blocking, clarification, nonblocking improvement and optional suggestion; resolve questions affecting merge decisions first. Closing a thread is not proof of resolution. Contributors to a fix cannot independently approve their modified scope; Agent reviews do not impersonate human/specialist approval. Valid unaffected reviews/specialized evidence may be reused under project rules, but cannot replace each pre/post end-to-end run or required latest-head CI. Record invalidation and reruns after changes.

- Pre-merge readiness decision: complete CI/independent/specialized/end-to-end/documentation set, non-Draft/no conflicts/no blockers, governance and actual authority; main validation remains pending, never prefill it as passed:
- Actual merge fact: PR/head/base/main merge SHA/time/evidence; does not establish phase completion or release:
- Post-merge validation: actual result for main, initial failure/all retries, impact, owner, repair/revert authority and revalidation of the resulting version/data recovery:
- Phase 05 completion conclusion: Integration validation complete for the specified scope | Incomplete; retain the existing seven change states, with Merged expressing only a Git fact:
- Baseline restored by revert: incident handling alone is complete, the original feature remains undelivered; link a repair task or actual stopping decision, never backfill success:
- Actual phase 06 handoff: approved/actual scope; PR/source/merge and existing artifact identity; CI/independent/specialized/pre-post end-to-end evidence; issue handling/outstanding work; release compatibility/configuration/migration/dependencies; observability/recovery/documentation/translations/later nodes; actual transfer/receipt/owners/time with timezone:

Required failures or missing execution block the corresponding gate. Post-merge failure retains the Merged fact with phase incomplete and stops the failed version from entering release. Phase 06 still fixes and verifies the actual candidate/environment and obtains production authority; green main does not automatically mark a candidate verified or authorize release. This template authenticates neither identities nor execution and does not prove project CI integration.

## Documentation delivery check

- Authoritative check: complete or link the [documentation delivery check](../documentation/delivery-check.en.md); retain this matrix's traceability fields without duplicating conclusions:
- File-level impact, Chinese/English updates and reasons for unchanged/inapplicable items:
- Actual mechanical checks and current commit/artifact or complete digest snapshot:
- Nonauthor reviewer identity/actual reading/evidence, corrections/review and timestamp:
- Conclusion: passed | blocked; revalidate related changes. Required documentation, translations, evidence and independence cannot be waived. Never invent results for unimplemented/unexecuted checks:
