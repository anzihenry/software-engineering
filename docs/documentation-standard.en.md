---
title: "Project documentation standard"
status: current
owner: process-owner
updated: "2026-10-10"
---

# Project documentation standard

[简体中文](documentation-standard.md)

## Scope and asset boundary

This is the software-development harness's documentation standard for target projects, covering research, product, design, engineering, planning, usage, operations, and releases. Its version is `0.1.0`. MUST denotes a requirement after adoption; recommendations can be tailored.

`software-engineering` remains an asset repository for standards, workflows, SKILLs, and templates. The directory layout below belongs to projects developed using the harness; it does not require reorganizing the asset repository. The standard and templates are first-layer knowledge assets and are excluded from the existing GitHub automation installation bundle.

The standard and templates now route through harness entry instructions, all eight workflows, and documentation maintenance/independent-validation SKILLs as default requirements for harness-based development. Target-project tooling and CI templates are available; configure and verify actual enforcement through [tooling integration](documentation-tooling.en.md). See [documentation integration](documentation-integration.en.md).

## Language boundary for harness assets

Formal target-project documents still require Chinese and English, and templates that generate those documents retain corresponding language variants. Harness standards, workflows, SKILLs and operational references need only Chinese; English copies, reciprocal language links and translation review are not required. Asset governance, file-level impact, actual checks, independent review and current-version evidence still apply. A path under `docs/` does not make an asset a target-project document. Assess references before handling historical English assets; no whole-repository migration is required.

## Organization principles

- Maintain current knowledge by domain, work in initiatives, and historical context and evidence in records.
- A formal definition, task status, or original material MUST have one maintenance location; other documents link to it.
- Create directories as needed. Combine small initiatives and split complex ones. Reducing files never removes bilingual, acceptance, or independent-review requirements.
- Historical records need not describe current behavior, but MUST identify status, time, and applicable version to avoid being mistaken for current guidance.

## Target-project layout

```text
README.md / README.en.md
CHANGELOG.md / CHANGELOG.en.md
docs/
├── README.md / README.en.md
├── documentation.md / documentation.en.md
├── research/
├── product/
├── design/
├── engineering/
│   └── decisions/
├── guides/
├── planning/
├── initiatives/
│   ├── feature/
│   ├── improvement/
│   ├── refactor/
│   ├── research/
│   └── process/
└── releases/
```

| Location | Responsibility and boundary |
| --- | --- |
| Root README | Purpose, capabilities, shortest usable example, prerequisites, documentation entry, license; link to guides for detailed procedures |
| Root CHANGELOG | Version summaries; link to releases for compatibility, acceptance, and actual publication status |
| docs/README | Documentation map, reader-oriented paths, domain entries |
| docs/documentation | Adopted standard version, ownership, check commands, review mechanism, migration configuration |
| research | Reusable product-wide findings with sources, study dates, scope, and limitations |
| product | Effective direction, capabilities, business rules, target users, success metrics; proposed changes belong to initiatives |
| design | Current journeys, information architecture, interaction and visual rules, design system; technical design belongs to engineering |
| engineering | Current architecture, boundaries, data models, contracts, security and performance constraints, long-term technical decisions |
| guides | Repeatable usage, development, testing, deployment, operations, recovery, and release procedures |
| planning | Cross-initiative roadmaps, priorities, milestones, resources, dependencies, risks, collaboration rules |
| initiatives | Requirements, research, design, execution, acceptance, and retrospective for a particular objective |
| releases | Delivery, compatibility, evidence, artifacts, and actual status for a version or stable release event |

Research for an initiative stays with it; standalone studies can be research initiatives. Keep original material once and extract reusable findings into research with source links. If tasks live in an issue system, plans reference them and maintain objectives and milestones, rather than duplicating task status.

## Initiative categories and files

Choose exactly one category by primary objective: `feature` adds capabilities; `improvement` improves existing capabilities; `refactor` changes internal structure; `research` investigates questions; `process` improves working processes.

An initiative is recommended for an objective with clear completion criteria and multiple types of information needing ongoing maintenance, such as `initiatives/feature/adapter-upgrade/`. It may span versions and stages. Small fixes can be tracked in an issue/PR with corresponding current-document updates.

Each initiative MUST have Chinese and English READMEs covering objective, scope, status, owner, completion criteria, and navigation. Add requirements, research, design, plan, or validation files as needed. Split complex designs into experience-design and technical-design when useful. Every maintained split document MUST be bilingual. Completion and delivery checks can live in validation or the combined README.

## States and lifecycle

| Object | States |
| --- | --- |
| Maintained documents and indexes | draft; current; superseded (replaced or no longer applicable) |
| Initiative entry | proposed; active; paused; completed; cancelled |
| Release entry | planned; verified (specific candidate accepted); released; cancelled; withdrawn |

Requirements, designs, and reports within an initiative use maintained-document states. Their `current` status is scoped to the stated initiative and version, not a substitute for project-wide current knowledge. The initiative entry separately expresses work status.

Paused initiatives MUST state why and when work can resume. Cancelled initiatives MUST state why and how existing outputs are handled. Before completed, acceptance, affected current documents and translations, evidence links, and explicit follow-up tasks or initiatives MUST be complete. Completed does not imply publication.

Archive through status and indexes while keeping paths stable. Superseded documents MUST state why and link replacements, or explain why none exists. Correct historical factual errors explicitly; subsequent behavior changes belong in new records and current documentation.

Verified MUST bind candidate digest and source commit; a changed candidate needs revalidation. Released MUST identify publication time, artifact identity, address, and publication evidence. Cancelled and withdrawn require reasons; withdrawn also requires user guidance.

## Naming, metadata, and languages

Directories and files MUST use lowercase English kebab-case, except reserved names `README.md`, `CHANGELOG.md`, and their language variants such as `README.en.md` and `CHANGELOG.en.md`. Entries use the fixed name `README.md`. Use stable topics rather than status, owners, or phases in paths. Release directories use versions or stable event names; recurring records may include YYYY-MM-DD. Technical decisions use non-reusable four-digit numbers, for example `engineering/decisions/0001-preparation-boundary.md`.

Maintained documents MUST begin with YAML metadata:

```yaml
title: Document title
status: current
owner: technical-lead
updated: "2026-10-10"
```

Owner is a person or stable role mapped to a responsible maintainer in project configuration. Updated means the last substantive content update or validity review; formatting alone need not change it. Additional fields may identify versions, sources, scope, and replacement relationships. Never fabricate dates, ownership, or evidence.

Chinese is primary with unsuffixed names; English uses `.en.md`; other languages are optional. Maintained documents, initiative entries and split files, and release records MUST be bilingual and link to each other. Owner and status match for the same object. Updated records each translation's actual update or review date and may differ.

Mark stale English translations with the affected scope and corresponding Chinese version; they cannot pass the relevant delivery check. Original interviews, logs, and generated reports may retain their original language and format, with bilingual entries or summaries explaining purpose, provenance, and scope.

## Templates and existing traceability

Templates prescribe necessary content, not rigid headings or file counts. Explain why required items do not apply. Template-asset metadata describes the template; replace metadata and every placeholder when creating a project document, select valid object states, and recheck links. Drafts and templates are not acceptance evidence.

| Type | Required content |
| --- | --- |
| Maintained knowledge | Current facts or rules, scope, references |
| Initiative entry | Objective, scope, status, owner, completion criteria, navigation |
| Requirements | User problem, outcomes, scope and non-goals, acceptance criteria |
| Research | Questions, methods and sample, findings, limitations, sources |
| Design | Context and constraints, solution, decisions, risks, verification |
| Plan | Tasks, dependencies, owners, progress, risks, completion criteria |
| Validation | Acceptance, evidence, outstanding issues, documentation checks, independent review |
| Release | Version and status, contents, compatibility, artifacts, acceptance and publication evidence |
| Technical decision | Context, alternatives, decision and reasons, consequences, supersession |

Existing workflow/SKILL active/deprecated states and scope/review_by remain governed by content governance; SKILLs retain their supported frontmatter. They are not target-project document states and MUST NOT be replaced wholesale. Overdue ordinary documents are flagged for review without automatic status changes. Existing workflow/SKILL expiry gates remain intact.

Existing delivery records retain record_id, related_records, source_version, evidence, and timezone-bearing created_at/updated_at. Document updated is a content-review date; record updated_at is an event/status timestamp. Keep document and record states separate, for example record_status in a traceability section. One status cannot simultaneously represent an initiative, requirement, and release.

## Navigation, references, and evidence

Every created domain directory MUST have bilingual READMEs; add subdirectory entries where separate navigation is useful. Initiative indexes group by category and status, release indexes by version and publication status. Metadata owns titles and states; authors maintain reading paths and purpose. Generated indexes are not a second source of truth.

Repository references MUST be relative and prefer the same language, with section links when useful. Label untranslated original sources in English references. Maintain detailed definitions, task states, originals, and shared evidence once. Update navigation and affected references when locations or states change.

Long-term technical decisions belong in engineering/decisions and are referenced by initiative designs. Update current architecture and contracts after implementation. A changed decision gets a new numbered record; mark the old one superseded and link the replacement.

Keep explanatory images and design attachments in nearby assets directories, reports and measurements in evidence. Initiative evidence stays with initiatives, version-level evidence with releases, and may be shared by reference. Identify generation method, time, commit or artifact digest, and environment. Store large or sensitive material externally with controlled locations and identifiers; do not copy secrets or unredacted personal data.

## Strict delivery checks

Merge, initiative completed, and release released are mandatory gates. The delivery owner uses the shared checklist in a PR for ordinary changes, validation or a combined entry for initiatives, and linked check results for releases, without duplicating conclusions.

Explicitly assess product, research, design, engineering, guides, planning, initiatives, releases, and navigation. Mark each updated, reviewed-no-change, or not-applicable; the latter two require reasons. Tools check metadata, states, names, links, bilingual pairs, and index consistency. A human or independent AI Agent checks completeness of impact, actual behavior, translation meaning, evidence, and applicable examples. English-file existence does not establish translation correctness.

The reviewer MUST NOT be the author or modifier of the reviewed content. An independent Agent MUST use a separate review context and independently read implementation, documents, and evidence, not rely on the author's summary. Record identity, commit or uncommitted-file digest snapshot, files inspected, findings, rechecks, and verdict. The author fixes issues and the reviewer rechecks. Subsequent relevant changes invalidate affected conclusions and require revalidation.

Delivery requires every mandatory check and independent review to pass, synchronized translations, and no required documentation gaps. Required updates, translations, or evidence cannot be waived. Unrelated pre-existing issues can be tracked separately with reasons they do not affect delivery. Existing human high-risk Go/No-Go requirements remain; documentation review is not specialist authorization.

Periodic owner reviews supplement delivery gates and update updated after actual review; do not mass-advance dates. Automation cannot prove factual correctness or replace independent review. Later implementation MUST wire mechanical checks and review-record consistency into required gates. Until a dedicated checker exists, perform every item using evidenced manual or temporary-tool checks plus independent review, state the actual method, and never mark unimplemented or unexecuted automation as passed. Existing project-required CI checks still need actual passing runs.

## Adoption and migration

Target-project docs/documentation MUST identify a fixed standard version or commit, role mapping, task system, actual check commands and CI gates, independent-review location, review intervals, and external material storage. The harness maintains common rules; projects configure execution rather than keeping an untraceable copy.

Existing projects inventory documents, assign domains, statuses and owners, correct current errors first, then migrate directories, metadata, languages, and navigation incrementally. Assign migration owners, completion criteria, and evidence. New changes comply immediately; affected legacy documents are brought into compliance with their delivery. Migration does not excuse missing gates, and completion requires independent acceptance. Adoption does not automatically move or overwrite project assets.

## Assets and existing references

- [Bilingual documentation templates](../templates/documentation/README.en.md)
- [Existing content governance, Chinese source](content-governance.md)
- [Existing lifecycle traceability templates, Chinese source](../templates/delivery/README.md)
- [Harness three-layer boundary, Chinese source](project-boundaries.md)
