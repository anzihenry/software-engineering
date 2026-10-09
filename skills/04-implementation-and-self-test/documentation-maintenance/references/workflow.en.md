# Documentation maintenance

[简体中文](../SKILL.md)

## Basis and inputs

Read the [standard](../../../../docs/documentation-standard.en.md) and target-project docs/documentation. Load the [template index](../../../../templates/documentation/README.en.md), changes, research/requirements/design, existing documentation, and task system as needed. Repository-relative links require the full harness checkout. Standalone skill distribution must also provide accessible pinned standards/templates or checked-in equivalents. If unavailable, report missing adoption/compliance evidence rather than guessing or claiming compliance.

## Work

1. Distinguish target projects from harness assets. Apply the target layout only to projects; keep the asset repository's skills/workflows/templates and existing governance metadata.
2. New projects configure provenance, roles, and real check commands. Existing projects inventory domains, states, owners, and migration tasks while preserving content. Choose initiative categories by objective; small work can stay in issues/PRs. Do not automatically migrate everything or create empty directories.
3. Assess research through publication: product, design, engineering, guides, planning, initiatives, releases, navigation. Expand to files and mark updated, reviewed-no-change, or not-applicable; the latter two need reasons. Maintain task status and definitions once.
4. Synchronize affected Chinese and English, metadata and object states, navigation, relative references, and decision supersession. Work history stays in initiatives; effective facts update maintained knowledge. Historical material identifies time and version scope.
5. Use the [delivery checklist](../../../../templates/documentation/delivery-check.en.md) to record the commit or path/digest snapshot, actual mechanical checks, example verification, outstanding work, and findings. Until dedicated tooling exists, evidence every structural and bilingual-pair item manually or with temporary tools. Existing required CI cannot be substituted.
6. Hand off to a non-author human or independent Agent with a separate context using documentation-delivery-validation. Modifiers cannot approve their own content. Fix findings and request affected-scope rechecks.

## Output and boundaries

Produce adoption configuration or migration inventory, synchronized documents, file-level impact, snapshot and evidence, and a checklist awaiting independent review. Use PRs for ordinary changes, validation/README for initiatives, linked results for releases; avoid duplicate verdicts.

Complete required documentation, translation, and evidence or record blockers; never label missing work complete, merge-ready, or publish-ready. Track unrelated existing issues separately with impact reasons. Hand off only after independent validation passes for the current version. This skill does not approve merge, production publication, or specialist risk exceptions.

## Tool execution

Use the [tooling guide](../../../../docs/documentation-tooling.en.md) for project inventories and check/snapshot/gate. Independent reviewers fill actual inspections, evidence and conclusions; never generate passed automatically. CI requires trusted independent records and verified platform enforcement before claiming it is required.
