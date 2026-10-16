---
template_name: outcome-retrospective-actions
template_version: 1
lifecycle_stages: [8]
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

# Outcomes, Retrospectives, and Actions

[中文](outcome-retrospective-actions.md)

Complete sections applicable to the record type; explain exclusions. Do not invent incidents or actions for an assessment. Retain stable IDs and maintain status only in each primary record. Record status is separate from document metadata, action progress/effectiveness, and rule status. Retain the original scope and basis of historical Verified/Closed records; do not retrospectively mark them effective.

## Traceability

- Record ID:
- Record type: Outcome assessment | Delivery retrospective | Incident retrospective | Periodic trend assessment | Improvement action portfolio | Action effectiveness verification | Playbook evolution
- Record status: Preparing | Analyzing | Awaiting decision | Tracking | Verified | Closed
- Owner: One coordinator; record actual acceptance separately
- Decision authority: Actual person/role and verifiable authority source; completing a field grants no authority
- Risk level: Low | Medium | High | Not applicable
- Related records: Opportunity, requirement, design, change, release, incident, retrospective, or action IDs/links
- Source/artifact version: Fixed commit/digest/batch/actual version distribution, not only a mutable branch
- Environment and scope: Cohorts, channels, regions, environments, teams, and exclusions
- Evidence: Raw data/queries/extraction time and digests, feedback, timelines, checks, and decisions; only minimal sanitized summaries/controlled references for sensitive material
- Created at with timezone:
- Updated at with timezone:

## Trigger, Acceptance, and Plan

- Trigger, question to answer, and related objectives/guardrails:
- Start and delivery deadline; planned observation window/timezone, sample conditions, and their source:
- Recipient, actual confirmation of scope/responsibility/deadline and time; coordination/escalation until acceptance:
- Preparation before data matures; if evidence is insufficient at the deadline: method/owner/deadline/cost cap, interim state/operations owner, and decision owner if still insufficient:
- Current incident response stage/owner; interim review must not delay response, later additions, and history:

## Definitions, Data Quality, and Revisions

| Metric/related objective | Definition/formula/numerator/denominator/exclusions | Data source/query/extraction identity and time | Object/cohort/version/window | Baseline/threshold/sample requirement/owner |
| --- | --- | --- | --- | --- |

- Checks/evidence for missing, duplicate, delayed, sampled/instrumentation/identity changes, version coverage, and denominator completeness:
- Original objective/definition/window; reason, data correction versus target change, decision maker/authority/time/scope:
- Original values and recalculation evidence; scope that cannot be recalculated or directly compared:
- Treatment of outage-period gaps, bias impact, and sensitive-data access limits:

## Results

| Delivery acceptance/outcome objective/operational guardrail | Baseline and current trend | Relevant cohorts/controls and differences | Met/partly met/not met/insufficient | Evidence sufficiency and limits | Observation/association/causal claim and basis |
| --- | --- | --- | --- | --- | --- |

- Confounders, post-hoc exploratory findings, scope of qualitative material, and unverified hypotheses:
- Actual phase07/specialist handling and acceptance of current guardrail risks; do not wait for assessment completion:

## Decisions and Execution

| Scope | Maintain/expand/adjust/gather evidence/pause-stop/revisit opportunity | Basis and alternative explanations | Recommendation/approval/actual execution | Decision maker/authority source/time | Caps/guardrails/stop and reassessment conditions |
| --- | --- | --- | --- | --- | --- |

- User/operations/data/compatibility/communication obligations when stopping and their actual recipients:
- Decision revision history, new evidence, and confirmation by affected recipients:

## Blameless Retrospective

- Planned versus actual objectives/results, deviations, and evidence:

| Time and timezone | Facts and evidence | Signals/unknowns/conflicts visible then | Available options, authority/resources/time limits | Judgment and actual actions/failures/retries/side effects | New evidence/changes |
| --- | --- | --- | --- | --- | --- |

- Contributing mechanisms and evidence across technology/process/organization/dependencies/tools/information flow:
- Effective, failed, and missing guards; repeatable conditions versus fortunate circumstances in successes:
- Facts/judgment at the time/later explanations, disagreements and evidence on each side, remaining unknowns:
- Disposition: new action/existing action coverage check/further investigation/retain practice/authorized no-action or risk acceptance; actual acceptance and reassessment:
- Required communication/restricted evidence and specialist handling; basis for review completion, separate from phase07 or specialist closure:

## Improvement Actions

| Action ID/primary record/source finding | Target outcome/risk/hypothesis and scope | Single owner/actual acceptance/time | Priority/deadline/dependencies/investment authority | Implementation completion criteria and evidence | Effectiveness criteria/window/samples/guardrails/verifier | Action progress/blockers |
| --- | --- | --- | --- | --- | --- | --- |

Action progress: Awaiting acceptance → Accepted → Implementing → Awaiting effectiveness verification → Verifying → Closed. Follow facts; an unimplemented action can close after an authorized stop without inventing implementation/verification. Record blocker owner, next step, update time, and original deadline/revision history. Exploration completes against questions and evidence; infeasibility does not remove the original risk.

| Action ID | Actual implementation result | Effectiveness: effective/partly effective/ineffective/insufficient/justified not applicable | Evidence/method/actual window and samples | Side effects/false positives/cost | Adjust-replace/gather evidence/stop and interim risk owner |
| --- | --- | --- | --- | --- | --- |

- Overdue decision, authority, reason, and new arrangement; extension does not accept risk:
- Remaining-risk scope/authority source/expiry/compensating measures/reassessment; no waiver of hard gates:
- Closure reason, actual basis, decision maker/time, residual handoff, necessary documents/communication; closed counts do not measure effectiveness:
- Reopening or linked ID after recurrence/new evidence/environment changes, retaining the original closure basis:

## Playbook Evolution and Feedback

- Problem/applicable evidence, audience/exclusions, existing-rule coverage, and smallest suitable vehicle:
- Local repair or scoped trial; authority, scope, version, owner, cost, and rollout/withdrawal criteria:
- Rule status: Proposed | Trial approved | Trialing | Awaiting decision | Adopted at scale | Withdrawn or replaced; transition evidence/authority/time:
- Record publication, entry-point access/execution conditions/actual adoption behavior, effectiveness/side effects/cost separately:
- Affected workflows/skills/templates/navigation/references/applicable translations/checks and current independent validation:
- Review date and actual revalidation, change triggers, replacement links, and affected recipients:
- Feedback to 01/02/03/04 and subsequent phases/07: source, receiving ID, recipient, and acceptance time; original coordinator continues until accepted:

## Assessment Acceptance and Follow-through

- Check the [seven phase08 minimum conditions](../../docs/workflows/08-measurement-and-retrospective.md#七项共同验收底线) and applicable work-unit requirements (Chinese source):
- Current conclusion, impact of insufficient evidence, and disposition of open actions/major risks:
- Actual decision maker/authority/time, next review date/milestone or justified exclusion, and reassessment conditions; review completion does not prove action effectiveness, stopping does not mark the target met:
- [Documentation delivery check](../documentation/delivery-check.en.md): file impacts, applicable English, non-author verification of the current version, findings/corrections, and evidence:
