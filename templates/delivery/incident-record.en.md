---
template_name: incident-record
template_version: 1
lifecycle_stages: [7]
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

# Incident record

[简体中文](incident-record.md)

Use for ordinary incidents. Security/privacy entries contain only permitted minimal sanitized facts and a restricted ID; originals, credentials, personal data, investigations and notification/legal analysis stay in approved restricted systems. Use the [operations and support record](operations-record.en.md) for routine acceptance/health/maintenance/support, with separate work-unit IDs and linked rather than duplicated states.

## Traceability

- Record ID:
- Record type: operational incident | security/privacy reference
- Record status: investigating | mitigating | recovered | escalated | closed (incident process; milestones/closure reason are separate)
- Owner: current coordination/technical/communication responsibilities and backup
- Decision authority: actual authorization source, scope and validity for diagnosis/production/data/notifications
- Risk level: severity and support priority separately, mapping basis and provisional confidence
- Related records: original alerts/cases, release/change, primary/split incidents, restricted response, review/actions and acceptance
- Source/artifact version: actual affected/recovery versions, artifact digests, deployment, configuration/migrations/dependencies
- Environment and scope: service, environment, region, tenant, channel, version distribution and affected users
- Evidence: raw metrics/requests/logs/traces and digests, status updates; restricted evidence IDs only
- Created at with timezone:
- Updated at with timezone:

## Acceptance, impact and triage

- Source, discovery/receipt times, impact start/unknown intervals, symptoms, user/business/data impact:
- Known facts, hypotheses, unknowns, non-reproduction scope and next verification:
- Duplicate linkage/merge basis, retained reports/times/impact/communication; splits and reasons:
- Provisional severity, basis/scope/duration/trend/workaround, severe single-user risks; evidence/decision maker/time for level changes:
- Triage destination and actual acceptance; supplier escalation and internal coordination; emergency takeover scope/gaps and incomplete phase 06 facts:

## Responsibilities, clocks and authorization

- Object owner, current responder, incident coordinator, technical/communication roles, backup/coverage (roles may be combined):
- Acknowledgment/initial triage/next update and applicable mitigation/recovery targets, policy source and timeout escalation; preserve original impact time:
- Shift/handoff context, completed work/side effects, unfinished steps/permissions, next action; sender and actual recipient/time with timezone:
- Current action target/expectation, version/environment/scope, valid preauthorization/new approval, risks/stop and failure/recovery path:

## Raw timeline and response

| Time with timezone | Fact/hypothesis/action/decision and original record | Operator/decision maker and authorization | Actual applied/running/unexecuted state and side effects | Result/evidence/next action |
| --- | --- | --- | --- | --- |

- Conflicting-operation coordination and scope; new code/artifacts/migrations linked to phase 06 and applicable emergency process:
- Actual reconciliation after timeout/cancellation/disconnection/partial success, safe retry/compensation/continuation basis and linked execution; retain initial failures:
- Mitigated milestone and remaining impact (no new platform state); actual user-path/service/data/version/configuration verification:
- Required stability window/valid samples/monitoring quality, actual start/end/samples/criteria; insufficiency or indeterminate results:
- Predefined minimum standard for degraded recovery, limited capabilities/deadline/full recovery plan; blocking impact/partial recovery:
- Recurrence intervals, reopening/linkage, original closure basis and new response:

## Communication, closure and phase 08 acceptance

- Known impact/scope, actions/workarounds, next update; audience/authorization/actual delivery or pending evidence; no unsupported recovery date:
- Recovery verification, impact end and residual risks; recovered and ready to close assessed separately:
- Security signal/response/impact separately (restricted IDs and permitted sanitized references only); detailed notification/preservation decisions remain restricted:
- Closure/escalation basis, decision maker/time; current recovery, required communication/records/documentation and accepted follow-ups complete:
- Phase 08 acceptance of facts/revisions, impact definitions/limits, information/hypotheses/authorization/successes/failures at the time, controls and actions; recipient/time:
- Action/review IDs, owners/priority basis/deadlines/completion and effect criteria; unimplemented improvements stay open and unrecovered response responsibility continues:

## Documentation delivery check

- Single [documentation delivery check](../documentation/delivery-check.en.md): file impact, applicable Chinese/English, current digests/actual checks, independent review and correction recheck:
- Result: passed | blocked. Authorized emergency containment can proceed first without claiming missing documentation/translations/evidence passed; mandatory closure gaps cannot be waived by handoff. Filled fields or successful state transitions do not authenticate recovery, authorization or security closure.
