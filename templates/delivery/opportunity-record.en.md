---
template_name: opportunity-record
template_version: 1
lifecycle_stages: [1]
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

# Opportunity record

[中文](opportunity-record.md)

Maintain one authoritative opportunity record in the existing issue, task or document system. The [Phase 01 workflow](../../docs/workflows/01-demand-and-opportunity.md) (Chinese) defines states and readiness for refinement. A small, clear issue may use one combined record without a separate report. Phase 01 approves refinement effort only, not development or delivery dates. Retain every traceability field; explain inapplicability and never invent data or approval. Template frontmatter is not the actual record state.

## Traceability

- Record ID:
- Record type: opportunity
- Record status: needs information | validating | candidate pool | entering refinement | deferred | closed
- Owner:
- Decision authority:
- Risk level: low | medium | high-risk candidate | not applicable
- Related records:
- Source/artifact version: explain inapplicability; otherwise use an immutable version
- Environment and scope:
- Evidence: source/raw report location, time, scope and limitations; controlled identifiers only for sensitive material
- Created at with timezone:
- Updated at with timezone:

## Original signal and problem

- Original request, submitter, each source and its time:
- Affected actors, situation, current behavior, frequency and scope:
- Actual/expected behavior and available reproduction steps for a defect, if applicable:
- Existing alternatives and known impact:
- Explicit user solution/constraints and unverified implementation hypotheses, labeled separately:
- Known facts, assumptions and unknowns, listed separately:
- Deduplication search scope, repeated sources/related distinct issues and incomplete searches:

## Desired outcome, scope and risk

- Observable improvement and assessment method, which may be qualitative; observation window/guardrails if applicable:
- Numerical measures, baseline/target if known; otherwise acquisition method, owner and limitations:
- Initial scope, non-goals and known time/cost/policy/technical constraints:
- Initial risk triggers, required roles and next action; controlled response record for urgent events:
- Critical unknowns and whether they change the investment decision; unknowns handed to Phase 02, their owners and next actions:

## Bounded validation, when needed

If validation is not triggered, state the factual reason while retaining source evidence and risk assessment. A plan is not completed validation. Record “validating” only after authorized work actually starts; external research and data access require actual permissions.

- Hypothesis and minimal validation method/sources:
- Actual owner, approving authority/source and timestamp with timezone:
- Confirmed time or cost limit and completion/stop criteria:
- Actual execution facts: not started/in progress/finished, results/limitations and raw report:
- Stop and renewed decision on reaching the limit, inconclusive results, new risk or additional investment:

## Relative priority and decision

- Decision window, value/impact, urgency and evidence/uncertainty:
- Next refinement/validation effort, dependencies/capacity and existing commitments; rough implementation cost is only a constraint:
- Shared comparison record link, relative order/reasons, displaced/waiting work and impact; explain if nothing is displaced:
- Verified mandatory constraints and responsible authority, if applicable; evidence/conditions that could change the order:
- Agent recommendation and items awaiting an authorized decision:
- Actual decision, reasons, authorized decision maker, approval source and timestamp with timezone:

## State history, reassessment and migration

Maintain state/owner only in this authoritative record; attachments must not duplicate task state. Follow [state rules](../../docs/workflows/01-demand-and-opportunity.md#机会状态与转换) and [legacy migration](../../docs/workflows/01-demand-and-opportunity.md#旧记录迁移) (Chinese). An old label does not establish compliance with the new baseline.

| Previous state | New state | Reason/evidence | Decision maker and authority source | Timestamp and timezone |
| --- | --- | --- | --- | --- |

- Current owner, missing information/reassessment time, or candidate reassessment triggers, deferred resumption criteria, closure/reopening criteria:
- Original state/source/time, mapping rationale and owner confirmation; unavailable material and current gaps, if applicable:

## Phase 02 handoff and return

- Actual satisfaction of all six readiness criteria; do not record approved refinement when they are unmet:
- Refinement owner, approval decision link and downstream requirement ID/location:
- Locations of problem/evidence, desired outcome, initial scope/non-goals and constraints/risks in the authoritative record:
- Unresolved questions, owners, next actions and the nature of specified solutions/hypotheses:
- Reassessment decision after value or scope changes, affected downstream work and existing commitments:
