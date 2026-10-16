---
template_name: operations-record
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

# Operations and support record

[简体中文](operations-record.md)

Choose acceptance, health, maintenance or support sections for the work unit; reuse the primary system/record rather than duplicate task states. Each independent object has a stable ID, including combined documents; justify inapplicable items with facts. Use the [incident record](incident-record.en.md) for incidents and approved restricted systems for security/privacy details.

## Traceability

- Record ID:
- Record type: operational acceptance | health check | routine maintenance | support request
- Record status: per selected work unit; check results, health, support processing and closure reasons are separate
- Owner: object/current response/communication roles, backup and actual coverage
- Decision authority: identity/data access, diagnosis/change/notification authorization source, action scope and validity
- Risk level: actual risk/priority and basis; link incident severity separately
- Related records: phase 06 release, original signals/cases, primary incident/defect, maintenance/change, phase 08 review/actions
- Source/artifact version: current versions/configuration/dependencies/artifacts and supported client compatibility
- Environment and scope: object, platform/channel, environment/users and critical paths
- Evidence: raw checks/requests/delivery/acceptance/actions/recovery and current digests; no sensitive originals
- Created at with timezone:
- Updated at with timezone:

## Shared facts, responsibilities and clocks

- Original discovery/receipt/impact times, symptoms/request/attempts, facts/hypotheses/unknowns and minimum next verification:
- Source linkage/merge/split basis, original report impact/times and communication responsibility:
- Current owner/action/next update/review, acknowledgment/triage/update/applicable recovery targets and policy:
- Prior rules for waiting/paused clocks, original waiting and total duration; handoff does not reset impact time:
- Shift/handoff context, completed work/side effects/unfinished steps/permissions, sender/actual recipient/time with timezone, original coordination and escalation until acceptance:

## Operational acceptance (when applicable)

- Object/actual version distribution/dependencies/limits, primary/backup/coverage, actual monitoring/feedback/runbook/access and response or escalation capability checks:
- Older client support/compatibility deadlines, supplier coordination, recovery methods/limits, open risks/owners/deadlines/criteria:
- Conclusion: accepted | awaiting completion | emergency takeover; scope/responsibility effective time and gaps/follow-ups without backdating phase 06 success:

## Health and maintenance (when applicable)

| Path/capability | Source/object/denominator and success/failure/exclusions | Window/samples/baseline/target/owner/frequency/action | Current raw result/version/time and evidence validity | Gap/action/owner/deadline/criteria |
| --- | --- | --- | --- | --- |

- Health: normal | degraded | abnormal | indeterminate; collection freshness/scope/version/delivery/actual acknowledgment, conflicting evidence and gaps:
- Alert trigger/recovery/runbook/response target/escalation; aggregation/suppression/silence basis/scope/expiry/alternative coverage:
- Applicable actual drills or valid same-scope evidence: signal generation→local or authorized delivery→human acknowledgment, readable backup→restored data/paths and measured time/loss against targets:
- Capacity/quotas/cost/dependency expiry and alternatives, permissions/certificate/credential rotation, current runbooks, flags/dual-write/old-interface exit:
- Frequency basis and revalidation after major changes; drill environment/authorization/impact limit/stop/recovery; actual changes linked to change control and revalidation:

## Support resolution (when applicable)

- Impact/urgency/commitment/workaround and priority; severe single-user data/security risks escalated to incident or restricted response:
- Risk-based identity/scope verification; minimal sanitized information and log/data purpose/permission/retention:
- Verified environment/reproduction or non-reproduction scope, version applicability, actual action/authorization/result/side effects and original failures:
- Processing: in progress | awaiting user | awaiting internal/supplier | transferred | escalated | resolved | concluded:
- User information needed/reason/alternatives/review; internal/supplier acceptance/follow-up/update and internal coordination:
- Temporary workaround limits/deadline/permanent arrangement; new code/configuration/production actions linked to phase 06:
- Resolution verification: user confirmation | objective evidence | unconfirmed; facts/evidence/time:
- Closure reason: verified resolution | no reply | transfer/escalation | duplicate | withdrawal | outside support scope; reminder/waiting policy/communication/actual acceptance/reopen path, not all counted as resolved:
- Repeat patterns/frequency/impact/versions/workarounds, feedback recipient/priority basis/next decision point; sanitized knowledge with applicability/preconditions/verified steps/risks/failure path:

## Result and phase 08 acceptance

- Applicable seven baseline criteria and results/evidence; unfinished/unverified items with owner/action/review:
- Required audience/authorization/actual delivery and next update; no unsupported repair date:
- Follow-up risks/owners/deadlines/completion and effect criteria, actual recipient/time; phase 08 facts/impact definitions/limits/information at the time/failures/controls/actions:
- Only this work unit concludes; continuous operations and responsibility for ongoing severe impact/unrecovered incidents/restricted response continue:

## Documentation delivery check

- Single [documentation delivery check](../documentation/delivery-check.en.md): file impact/applicable Chinese/English, current digests/actual commands, independent review and recheck:
- Result: passed | blocked. Required documentation/translations/evidence/independence cannot be waived; structure does not authenticate identity, capability, recovery or acceptance. Do not claim unconnected automation is enforced.
