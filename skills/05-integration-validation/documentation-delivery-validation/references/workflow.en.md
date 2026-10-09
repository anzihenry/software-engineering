# Independent documentation delivery validation

[简体中文](../SKILL.md)

## Inputs and independence

Read the [standard](../../../../docs/documentation-standard.en.md), target execution configuration, [shared checklist](../../../../templates/documentation/delivery-check.en.md), actual implementation/diff, bilingual documents, raw check evidence, and commit/digest snapshot. Relative links require a full harness checkout. Standalone skills need pinned rules/templates or project equivalents; report missing basis when unavailable.

The reviewer MUST NOT author or modify reviewed content. An author context hands off to another human or independent Agent with raw tasks, files, configuration, checklist, and evidence, rather than only expected conclusions. The Agent reads independently. Record identity, scope, and snapshot first; an AI verdict is not GitHub human approval. Source-code review also follows project coding-review rules.

## Validation

1. Independently establish changes and acceptance goals; compare domain/file-level impact and actively find omitted files, not just those the author listed. Check reasons for no-change and non-applicability.
2. Verify commit/artifact or uncommitted digest evidence. Check metadata, states, names, bilingual pairs, reciprocal and section links, navigation, single sources, and historical scope. Until dedicated tooling exists, record per-item method, scope, and evidence; never pass unexecuted checks.
3. Compare implementation with documentation, Chinese with English semantics, examples/commands, and candidate/publication evidence. Explain non-applicability if no implementation changed. Existence, counts, and author assertions do not establish correctness. Execute reversible verification as appropriate and preserve environment/results.
4. Report findings with locations, impact, fixes; the author fixes them and the reviewer does not modify reviewed content. Independently recheck the affected scope against the new snapshot. Relevant changes invalidate prior results.
5. Merge requires passing documentation checks. Initiative completed also requires completion criteria, maintained knowledge/translations, and follow-up handoff. Publication requires version contents, compatibility/upgrade guidance, and matching artifacts. Reuse only evidence still valid for the scope; earlier success cannot cover changed work.

## Output and gates

Use the shared checklist for reviewer identity/independence, files and evidence read, version, mechanical/content/translation findings, rechecks, verdict, and time.

Verdicts are passed or blocked. Pass only when all required checks and independent content review pass, translations are synchronized, and no required gap exists. Missing rules, configuration, required documents/translations, actual evidence, required CI, independence, or version binding blocks delivery. No conditional documentation pass or waiver. Track unrelated existing issues separately with reasons they do not affect delivery. Give minimum unblock actions to existing merge/release mechanisms; do not merge, publish, or change protection. Existing human high-risk decisions still apply.

## Tool execution

Use the [tooling guide](../../../../docs/documentation-tooling.en.md) for project inventories and check/snapshot/gate. Independent reviewers fill actual inspections, evidence and conclusions; never generate passed automatically. CI requires trusted independent records and verified platform enforcement before claiming it is required.
