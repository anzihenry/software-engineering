---
template_name: release-record
template_version: 1
lifecycle_stages: [6]
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

# Release record

[简体中文](release-record.md)

## Traceability

- Record ID:
- Record type: release
- Record status: candidate preparation | awaiting approval | releasing | observing | paused | recovering | concluded (process state; outcome is separate)
- Owner:
- Decision authority: authorized human/preapproved policy and identity/authority source; an author's declaration is not authorization proof
- Risk level: low | medium | high
- Related records: requirements/design/change, PR, verification, authorization, incident and Release IDs/links
- Source/artifact version: candidate ID/revision, full source SHA, version, artifact digests, build run and deployment
- Environment and scope: environment, region, tenant, platform, channel, audience and approved target
- Evidence: raw build, readiness, authorization, batch/health, failure/retry, recovery and notification records
- Created at with timezone:
- Updated at with timezone:

## Phase 05 acceptance and candidate inventory

- Scope/acceptance criteria, all included changes and exclusion/isolation evidence; PR and actual main merge SHA:
- Passed CI, independent review, specialist and pre/post-merge E2E evidence; issue disposition/open items; actual handoff and recipient/time:
- Candidate ID/revision, version/baseline and source SHA; combination risks and mandatory candidate verification:

| Platform/deliverable | Immutable ID/digest/location | Build run/toolchain/locked dependencies/parameters | Signature/SBOM/provenance and applicability | Required transformation inputs/outputs and distributed artifact verification |
| --- | --- | --- | --- | --- |

- Configuration version, flags, migrations/dependencies, supported version combinations/deadlines, execution and cleanup order/conditions, recovery target:
- Verification mapping for source/artifact/target environment, rehearsal, production differences/unverified risks:
- Candidate/condition changes, new revisions, affected evidence/authorization and revalidation:

## Readiness and execution authorization

- Current check results/raw evidence; readiness: passed | conditional | blocked; gaps, owners and verification method:
- Authorization: single release | staged decision | human-preapproved continuous policy; decision: approved | awaiting conditions | rejected/revoked:
- Approver/authority source, decision/evidence, time with timezone, candidate ID/revision/SHA/artifacts:
- Environment/channel/actions/scope, batches/maximum coverage, effective/expiry/release window with timezone:
- Preconditions, designated verification mechanism, whether reconfirmation is required; completed verification and readiness reassessment:
- Stop thresholds, permitted recovery, on-call/observability, exclusion covering deployment and observation, grounds for isolated parallel work:
- Policy change types/risk ceiling/mandatory checks; drift, expiry, revocation, new failures and renewed decisions:

Readiness does not authorize execution; unmet conditions block execution. Explicit preauthorization permits scoped execution after designated verification and a new passed readiness result. Later batches within valid authorization need no repeated approval; scope violations pause progression.

## Batch plan and actual timeline

- Each batch's initial state/target, artifacts/configuration/migrations, order, verification/observation/minimum samples, timeout/stop/recovery and owner:

| Start/end with timezone | Batch/target scope/initial state | Artifacts/configuration and run/deployment | Action/operator/authorization | Actual versions/coverage and path/data evidence | Health and next decision |
| --- | --- | --- | --- | --- | --- |

- Timeout/disconnection/cancellation: completed/running/unexecuted targets, version distribution, side-effect reconciliation, compensation or safe retry basis, linked continuation record:
- Partial success: mixed versions/scope/impact, compatibility basis, deadline/disposition; paused expansion and review time:
- Locations of all initial failures, retries and raw results:

## Health observation and decision

| Technical/business/data/impact signal | Data source/baseline/control | Threshold/window/minimum valid samples | Actual value/scope/time/samples/raw evidence | Quality/confounders and individual result |
| --- | --- | --- | --- | --- |

- Actual observation start/end, elapsed time and sample sufficiency, monitoring validity; preplanned low-traffic evidence and limitations:
- Health: passed | continue observing | abnormal | indeterminate; continue/hold/pause/recover/incident decision and basis:
- Hard-stop containment before attribution; authorization, owner, next action and review time:

## Recovery and emergency change

- Trigger, impact, recovery target/authorization, reversibility/compatibility/data risk and selected path:
- Actual steps/runs/times, versions/configuration/flags, data/external side effects, critical paths and stability-window verification:
- Recovered | partially recovered | forward fix in progress | blocked | incident escalation; remaining impact/owner; new forward candidate/verification/approval:
- Original release termination/pause/resumption decision and revalidation; cancellation residuals, existing actions/side effects and cleanup:
- Applicable emergency incident/severity/target/reason, human authorization, minimum diff, minimum checks/independent review:
- Unexecuted routine checks, risk/decision maker/follow-up owner/deadline/criteria; mitigated/recovered versus still open:
- Mainline synchronization, full verification, documentation, bypass record, accepted follow-ups, retrospective actions and closure evidence:

## Conclusion and phase 07 acceptance

- Approved target and actual versions/artifacts/configuration/distribution; each channel's review/listing/availability/installation and combined target result:
- Evidence for all eight success criteria: handoff, candidate, authorization, execution, target verification, observation, issues and closure/acceptance:
- Outcome: delivered successfully | cancelled | failed and recovered | failed and transferred to incident response; decision maker/time/basis; original change delivered/partial/undelivered:
- Paused/recovering remains open: owner/next action/review time; incident owner's acceptance and continuing response record:
- Actual phase 07 recipient/time with timezone (also for one person in both roles); versions/mixed distribution, configuration/migrations/compatibility, monitoring/on-call/escalation, recovery methods/limits, follow-up observation/support:
- Open issues/temporary measures/flags/dual writes/old interfaces: risk, owner, deadline, completion criteria and exit conditions; mandatory gaps cannot be waived by handoff:
- Bilingual release notes/upgrade guides/runbooks, actual notifications within authorization and evidence; unfinished items:

## Documentation delivery check

- Single check record: link the [documentation delivery check](../documentation/delivery-check.en.md), preserve traceability fields and avoid duplicate conclusions.
- File-level impact, Chinese/English updates and reasons for no update:
- Actual checks and current commit/artifact or digest snapshot:
- Independent non-author reviewer, files/evidence read and correction recheck:
- Result: passed | blocked; revalidate after relevant changes. Required documentation, translations, evidence and independence cannot be waived. Structural checks do not prove authorization, health or actual publication; retain actual verification methods when automated gates are not connected.
