---
template_name: change-handoff
template_version: 1
lifecycle_stages: [4, 5]
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

# Change handoff

[中文](change-handoff.md)

Use one authoritative record linked to existing requirements, solution, tasks and the [verification matrix](verification-matrix.en.md); keep facts at their original source without duplicate statuses. Follow [phase 04](../../docs/workflows/04-implementation-and-self-test.md) and [phase 05](../../docs/workflows/05-integration-validation.md). A template is neither execution evidence nor approval. Draft discussion or diagnostic CI does not establish phase 04 completion or formal validation in progress.

## Traceability

- Record ID:
- Record type: Change handoff
- Record status: Implementing | Awaiting review | Validating | Ready to merge | Blocked | Merged | Closed
- Owner:
- Decision authority:
- Risk level: Low | Medium | High
- Related records: Requirements, solution, verification matrix, PR or exception IDs/links
- Source/artifact version: Repository, base/head SHA, build or artifact digest; uncommitted paths and hashes where applicable
- Environment and scope:
- Evidence: Local checks, CI, reviews and specialized validation
- Created at with timezone:
- Updated at with timezone:

## Approved scope and actual change

- Current requirements/acceptance, solution/plan revisions, approved scope/non-goals, actual development authority and its source:
- Task branch, remote/upstream, actual base/head; path/SHA-256 snapshot for uncommitted contents and applicable artifact identity:
- Implemented observable behavior, key decisions and complete slice; interface/authorization/data/asynchronous/runtime boundaries and compatibility:
- Consistency of actual diff/commits with description; handling of unapproved changes:

## Acceptance and self-test mapping

| Acceptance/risk ID | Actual change and scenario/criterion | Required phase checks and actual command/manual steps | Version/configuration/environment/dependencies/data | Time with timezone/executor/exit code or observation | Individual result and reason/basis | Raw evidence/digest and limitations |
| --- | --- | --- | --- | --- | --- | --- |

- Complete project-required set and additional checks selected by risk; applicable normal/boundary/failure/authorization/concurrency/cancellation/compatibility/recovery scope:
- Before-fix reproduction and after-fix regression against the same behavior criterion; inability to reproduce and alternative evidence; independently confirmed requirement/contract basis for test changes:
- Initial failure, all retries, pre-existing baseline issues, impact/owner/remedy/recheck; no cherry-picking green runs or weakening required checks:
- Current evidence validity and invalidation/rechecks after changes; actual tested object if contents change during execution:

Use passed/failed/not-run/blocked/stale/not-applicable. Not applicable requires both a rule and factual basis; missing tools/environments do not qualify. Mocks/simulators/small samples support only their tested scope. Scale copy-change checks to risk while preserving project requirements. Unpassed required phase checks prevent formal handoff and cannot be retroactively deferred to phase 05.

## Limitations and later validation

| Uncovered item/reason and limitation | Previously planned completion node | Owner and actual acceptance | Criteria/required evidence | Failure stop scope/action |
| --- | --- | --- | --- | --- |

- Valid nonmandatory exceptions: rule, actual authority source, expiry, remedy and review conditions; preserve original results. Required CI, documentation/translations/evidence/independence and human high-risk decisions cannot be waived:
- Authorized work that may continue and affected work waiting or returning to phase 02/03:

## Supporting work and release impact

- Actual completion/evidence of contracts, configuration/flags, migration, observability, recovery, runbooks, support/notifications required at this node; link previously planned later items above:
- Migration compatibility/read-write order/invariants/partial failure/recovery execution and environment/scale limitations:
- Configuration defaults/missing/invalid values/flags and recovery; reference controlled secret identifiers only, never secrets:
- Release order, flags, observation, rollback/roll-forward and specialized/human decisions:

All migrations retain high-risk requirements. Scripts or successful test-environment checks do not authorize production operations.

## Formal handoff and status history

- Check phase 04's seven implementation and seven self-test criteria, supporting work and complete materials; if unmet, remain in implementation/preparation/Draft collaboration:
- Actual handoff decision, version/scope, decision maker/authority, time/evidence, recipient, open actions/next evidence:
- Actual phase 05 receipt/prerequisite checks, returned scope, independent review/CI/specialized execution and current-head merge decision:
- Actual PR/merge SHA/time/evidence; closure or stopping reason, existing results and transferred outstanding work:

| Previous → new status | Reason/candidate version and scope | Actual actor/authority source | Time with timezone | Decision evidence/remedy and recheck |
| --- | --- | --- | --- | --- |

Implementing means implementation or required phase self-tests are incomplete; Awaiting review means phase 04 is complete with formal materials ready; Validating means phase 05 has formally received the change and is actually validating; Ready to merge requires phase 05 confirmation of all conditions for the current candidate; Blocked means a necessary advancement gap; Merged means actual merge; Closed means actual completion or stopping closure, not proof of success. Author self-tests can establish at most Awaiting review. Receipt is not a pass; merge is not release. Changes require reassessing affected status/evidence; do not reuse approval for an old candidate or invent decisions.

## Documentation delivery check

- Unique check record: complete or link the [documentation delivery check](../documentation/delivery-check.en.md); preserve this template's traceability fields without maintaining a duplicate conclusion.
- File-level impact, Chinese/English updates and reasons for unchanged items:
- Actual checks, current commit/artifact or digest snapshot:
- Independent nonauthor reviewer identity, files/evidence read, issue corrections and recheck:
- Conclusion: Passed | Blocked; recheck affected changes. Required documentation, translations, evidence or independent review cannot be waived. If dedicated tooling is not integrated, record actual item-by-item methods and do not invent automated results.
