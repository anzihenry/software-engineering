---
template_name: solution-decision
template_version: 1
lifecycle_stages: [3]
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

# Solution decision

[中文](solution-decision.md)

Reuse one authoritative solution record/existing issue with versioned attachments; do not create six skill documents or duplicate task state. The [Phase 03 workflow](../../docs/workflows/03-solution-and-planning.md) (Chinese) defines completion, research, six solution states and changes. Record solution approval, implementation readiness and actual development authorization separately. Completion requires an evidence-supported solution, executable plan and actual development approval for explicit scope; it does not automatically commit dates or production release. Small tasks may use entries. Retain all traceability fields, explain inapplicability and invent no facts, evidence or approval. Template metadata is not the actual record state.

## Traceability

- Record ID:
- Record type: solution decision
- Record status: exploring | awaiting review | approved | conditionally approved | rejected | superseded
- Owner:
- Decision authority: actual person/role, authority source and decision scope
- Risk level: low | medium | high; distinguish recommendation from actual confirmation
- Related records: current requirements, risks, contracts, verification, tasks and prior decisions with IDs/versioned links
- Source/artifact version: baseline repository and commit/digest; explain inapplicability; this does not replace the approved solution baseline
- Environment and scope:
- Evidence: controlled locations, versions, timestamps, objects and limitations of raw results/reviews/confirmations
- Created at with timezone:
- Updated at with timezone:

## Current baseline, scope and original constraints

- Requirement baseline, actual upstream design-effort approval, scope and non-goals:
- Referenceable revisions, commits or file digests/locations for solution, contracts, verification and plan:
- Acceptance/NFRs, explicitly specified solution/technology constraints, sources and unacceptable risks:
- Existing architecture/interactions/data/interfaces/operations, actual platform/tool configuration and cost boundaries:
- Known facts, unverified hypotheses and missing business meaning, separately; return business gaps to Phase 02:

## Choices and key design

Compare alternatives only for substantive tradeoffs; small tasks can be brief. Do not silently replace user-specified constraints.

| Option | Requirement/constraint IDs and how they are met | Benefits, costs and risks | Reversibility/evolution/evidence limits | Selection or rejection reason |
| --- | --- | --- | --- | --- |

- Selected design and key decisions, boundaries/flows/failure semantics:
- Applicable interactions/states, authorization, security/privacy and observability:
- Interfaces/events/fields/errors/idempotency, consumers/providers and actual confirmation source/time:
- Version compatibility/deprecation/switching sequence, data invariants/read-write/backfill/concurrency/partial failure:
- Environment progression, controls/thresholds/observation windows and pause/rollback/forward-repair/data-recovery paths:
- Feasibility/professional evidence required now; verification possible only after implementation or in preproduction, with required points:

## Technical research and unknowns

| Question/hypothesis and impact | Category/destination | Owner/judge/actual authorization source | Judgment or allowed adjustment boundary | Time/cost limit and data/environment/operation boundaries | Actual conclusion/evidence/limits and next action |
| --- | --- | --- | --- | --- | --- |

Coding to establish feasibility is Phase 03 technical research and uses an independent worktree. Prototypes are not merged automatically; small-scale success does not prove production capability. Unknown high-risk impact needs professional evaluation first; missing business criteria return to Phase 02. Stop expanding research at its limit or on new risk and obtain a renewed decision.

- Git repository/main checkout, exact research worktree path/dedicated branch, fixed source baseline and ownership/permission checks:
- Raw commands, actual versions/environment/data scale, output/exit status/time, supported/unsatisfied/inconclusive result and limits:
- Necessary reproducible code/configuration/data descriptions, run instructions/raw results/conclusion outside the worktree, with verified locations/digests:
- Uncommitted/untracked/ignored files, other tasks/users, material still needed for revalidation and preservation treatment:
- Actual closure decision after success/failure/inconclusive work, cleanup or retention reason; original HEAD/target path/branch, archive/removal result and time:
- Explicit scope, preparation/checks and normal review for any selected prototype reuse, where applicable:

## Executable plan and implementation readiness

Reference the authoritative task table in the existing task system; do not duplicate state. Include all applicable costs and distinguish estimates, executable plans and actual commitments.

| Task/slice and output | Related requirements, completion criteria and verification | Dependencies/order/required point | Size/range, basis and assumptions | Actual owner acceptance/evidence and capacity |
| --- | --- | --- | --- | --- |

- Applicable implementation, tests, documentation/translations, migration, observability, independent review, release preparation/operations handoff, research preservation/cleanup:
- Critical path/parallel scope, factual dependency confirmation and delivery; contacts/roadmaps are not current capability:
- Actual capacity, existing commitments and specialist support confirmations/sources; do not accept work for others:
- Effort versus elapsed/waiting time, requested date and any separately confirmed date commitment with its basis:
- Estimate uncertainty/re-estimation triggers, work that may continue/must wait and interface/data/permission/release-dependency isolation for partial approval:
- Actual implementation-readiness judgment, responsible person, evidence/gaps and timestamp:

## Technical review and actual decisions

- Evidence/gaps for each of seven design criteria: requirements response, key design, tradeoffs, feasibility, contracts/recovery, verification arrangements and required reviews complete:
- Technical review scope/version, independent identity, actual reading/evidence, time and conclusion: reviewed scope passed/revision and re-review/specialist review/return:

| Finding/required review | Blocker/prerequisite confirmation/later mandatory item/suggestion and basis | Owner/required point | Actual result/evidence or pending work | Failure stop/review scope |
| --- | --- | --- | --- | --- |

- Actual solution decision/reasons, approver/authority source, baseline/scope/limits, timestamp with timezone and evidence; Agent recommendations separate:
- Actual development approval: current requirement/solution/plan versions, supporting review/readiness, approved scope/non-goals, actor/authority, reasons/limits, timestamp/source; verify and reference valid existing authorization covering this scope:
- Unmet conditions/open decisions; conditional approval does not start affected work; shared code cannot conceal unapproved capability:

## State history, changes and legacy records

Maintain state/owner once in the main record; readiness and development authorization remain separate. Follow [solution state rules](../../docs/workflows/03-solution-and-planning.md#方案状态与基线变更) (Chinese). Retain history; missing evidence for legacy approval requires current reassessment, never invented past decisions.

| Previous state/baseline | New state/baseline | Reason/impact and invalidated evidence | Actual actor/authority/evidence and timestamp with timezone | Work that may continue/must wait and re-review conditions |
| --- | --- | --- | --- | --- |

- Wording-only edits update the record; implementation details within scope stay in Phase 04; key technology/contracts/migration/recovery return to 03; business/acceptance/cost constraints/risk to 02; users/value/priority to 01; capacity/dependencies/time trigger plan/commitment reassessment:
- Legacy ID/state/version/time/source, unavailable material and current evidence; rejected-result treatment and supersession links/historical scope:

## Phase 04 handoff

- Receiving owner and seven versioned locations: requirements/approved scope, solution decisions, evidence/unknowns, plan, verification/quality commands, later controls/documentation/translations and actual development approval:
- Startup check: valid versions, authorization/prerequisites for the current task, blockers resolved and accessible standards/configuration/commands; gaps/owners/unblocking actions:
- Required points for later resources, mock boundaries and real integration requirements; pause affected work only, old authority does not cover new scope:
- Initial documentation impact, target-project bilingual/independent documentation checks and current-knowledge update locations:
