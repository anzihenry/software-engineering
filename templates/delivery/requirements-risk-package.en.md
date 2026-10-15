---
template_name: requirements-risk-package
template_version: 1
lifecycle_stages: [2]
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

# Requirements and risk package

[中文](requirements-risk-package.md)

Maintain one authoritative requirement record; a small task may share an existing issue and attachments reference its status/owner. A shared opportunity/requirement issue retains distinct IDs, states and decisions. The [Phase 02 workflow](../../docs/workflows/02-refinement-and-initiation.md) (Chinese) defines the full rules, states and authority. Completion approves solution-design effort only; technical feasibility, development and date commitments require an authorized decision after Phase 03. Retain all traceability fields, explain inapplicability and never invent facts or approval. Template frontmatter is not the actual requirement state.

## Traceability

- Record ID:
- Record type: requirements and risk package
- Record status: refining | awaiting alignment | ready for solution design | blocked | cancelled
- Owner:
- Decision authority: actual person/role and authority source
- Risk level: low | medium | high; distinguish recommendation from actual confirmation
- Related records: upstream opportunity ID/link, research, policies, incidents and downstream records
- Source/artifact version: immutable version where applicable; otherwise explain why; separate from the requirement baseline below
- Environment and scope:
- Evidence: raw material/confirmation location, version, time, scope and limitations; controlled identifiers only for sensitive material
- Created at with timezone:
- Updated at with timezone:

## Problem, scope and original constraints

- Actual upstream approval for refinement and its source, problem, affected actors and desired outcome:
- Complete behavioral slice, scope and non-goals:
- Roles/states, preconditions, input, trigger, main flow and applicable exceptions:
- Explicit user solution/constraints and sources; unverified implementation hypotheses listed separately:
- Existing business rules, facts, assumptions, conflicting interpretations and decision maker:

## Behavioral acceptance and applicable nonfunctional requirements

Small tasks may use entries instead of tables; numbers and Given–When–Then are optional. Outcomes must be observable, conditions clear and judgment supported; cover applicable boundaries/failures/permissions/cancellation/recovery and trace sources. “Works normally”, “smooth” or “friendly” and internal steps alone are insufficient.

| Requirement/acceptance ID | Role/conditions/trigger and expected outcome | Judgment basis and verification method | Applicable boundaries/failures, etc. | Original problem/constraint and source | Priority |
| --- | --- | --- | --- | --- | --- |

| NFR ID/category | Trigger/source or factual reason for inapplicability | Confirmed threshold or qualitative criterion | Verification method/owner | Critical open decision and decision point |
| --- | --- | --- | --- | --- |

An unspecified requirement does not imply no requirement. Clarify critical acceptance criteria in this phase; do not invent metrics or defer everything. Reference valid existing standards when available.

## Risk, controls and professional reviews

- Affected actors, worst consequence, risk triggers/reasons, recommendation/actual confirmation and remaining unknowns:
- Preserve every existing high-risk trigger in the workflow, including data migration; small code changes or planned audit/rollback do not justify downgrading:

| Control/review and applicability | Proposed/validated, source and object version | Owner/authorized reviewer | Required point: before design or later | Actual result/evidence/limitations | Stop action if incomplete or failed |
| --- | --- | --- | --- | --- | --- |

Professional evaluations required before design must actually be complete; a review queue is not a pass. Hand later verification to its required point. Assess risk grade and permission to enter design separately. An Agent cannot approve exceptions; follow the [existing quality gates](../../docs/quality-gates.md) (Chinese).

## Dependencies and unknowns

| Dependency ID/provider/consumer | Owner, concrete content/conditions/required point | Identified/awaiting confirmation/confirmed | Actual acceptance evidence/time | Failure impact/unblocking action | Authorized exploration scope/judgment/exit criteria |
| --- | --- | --- | --- | --- | --- |

No reply, a contact or a future roadmap establishes neither confirmation nor current availability. Clarify dependencies affecting scope/acceptance/key-risk judgments first; carry others under controlled exploration rules without requiring all implementation dependencies to be delivered early.

| Unknown ID/question and category | Impact and destination | Owner/decision maker | Validation goal/judgment or allowed adjustment boundary | Completion/confirmation point, exit and failure action | Current evidence and actual conclusion |
| --- | --- | --- | --- | --- | --- |

Use the workflow categories: blocking requirement judgment, technical solution to validate, nonblocking detail, and unknown high-risk impact. Unclear business rules/acceptance stay in Phase 02. Do not prefill technical success; unknown high-risk impact requires professional evaluation first.

## Seven readiness criteria and actual decision

Record evidence/gaps for each: clear scope; decidable acceptance; applicable NFRs identified; clear risk/required reviews with prerequisite evaluations actually complete; supported critical dependencies; assigned destinations for unknowns; and actual authorized approval for design. One overall tick is insufficient; an Agent recommendation is not approval.

- Agent recommendation, reasons and outstanding confirmations:
- Actual stakeholder confirmations/disagreements and sources:
- Actual decision, reasons, approved scope/limits, decision maker and authority source:
- Confirmation timestamp with timezone, baseline version and decision evidence:
- Unmet criteria, minimal unblocking actions, owners and reassessment conditions:

## Baseline, state history and changes

- Referenceable requirement version/revision or file digest, location and upstream opportunity:
- Baseline locations for scope/non-goals, behavioral/NFR acceptance, risk/controls, dependencies/unknowns and approval:

Maintain one state following [state and change rules](../../docs/workflows/02-refinement-and-initiation.md#需求状态与基线变更) (Chinese). Distinguish routine confirmation waits from known critical conflicts. Readiness and cancellation require an actual authorized decision; reopening requires reassessment.

| Previous state | New state | Reason/evidence | Actual actor/authority source; recommendations separate | Timestamp with timezone |
| --- | --- | --- | --- | --- |

| Previous/new baseline and change reason | Affected criteria/risks/dependencies/downstream and invalidated evidence | Return phase/confirmation actor and evidence | Work that can continue/must wait and reasons |
| --- | --- | --- | --- |

Wording-only edits update the original record. Business/scope/acceptance changes return to Phase 02; users/value/priority to Phase 01; pure technical changes go to Phase 03, with feedback to Phase 02 if acceptance/cost constraints/risk are affected. Old approval does not cover new scope; do not automatically stop unrelated work.

- Original legacy ID/state/source/time, missing history and current evidence/reassessment, if applicable:
- Unblocking/reassessment conditions; cancellation reasons/results/downstream treatment and reopening criteria, if applicable:

## Phase 03 handoff and return

- Current baseline, upstream opportunity, behavioral/NFR acceptance and specified solution constraints/hypotheses:
- Risk/required controls, owners, required points and actual evidence:
- Factual dependencies/unknowns, validation/exit criteria and failure actions:
- Actual design-effort approval scope, reasons, actor/authority, timestamp and source:
- Receiving owner and item-by-item response location; missing business meaning returns to Phase 02 and invalid value to Phase 01:
- Initial documentation impact, responsibilities and target-project bilingual requirements:
