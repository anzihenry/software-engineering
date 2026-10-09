# Project instructions

## Coding standards

- For every source-code change or review, use `$language-coding-standards`.
- `$language-coding-standards` is a repository prerequisite. If it is unavailable, do not claim compliance; request installation or use a checked-in equivalent before coding.
- Read the common rules and only the references for languages touched by the task.
- The repository's pinned language version and committed formatter, linter, compiler, build, and test configuration are authoritative.
- Do not silently upgrade toolchains, add production dependencies, weaken checks, or mix unrelated cleanup into a change.
- Run project-defined formatting, static analysis/type checking, build, and relevant tests; report commands not run and remaining risk.

## Project documentation

- Use `$documentation-maintenance` for software-development changes, from requirements/design through implementation, operations, and release; follow the shared documentation standard and `docs/documentation.md`.
- Make the pinned standard, templates, and both documentation skills accessible through the harness or checked-in equivalents. If prerequisites are missing, report the gap and do not claim compliance.
- Assess file-level documentation impact, keep Chinese and English synchronized, and update affected maintained knowledge, metadata, relative links, and navigation. Existing projects migrate incrementally; affected legacy documents must comply with the current delivery.
- Before merge, initiative completion, or formal publication, obtain `$documentation-delivery-validation` from a non-author human or a separate independent Agent context. Record actual files/evidence inspected and bind the verdict to the current commit or digest snapshot.
- Required documentation checks cannot be waived or conditionally passed. Use actual manual/temporary checks until dedicated tooling exists; existing required CI still must pass. Relevant changes require revalidation.
- Apply target-project directory conventions only to product/project documentation; preserve the structure and governance contracts of a harness asset repository.

## Project-specific commands

- Format: `<project command>`
- Lint/static analysis: `<project command>`
- Type check/build: `<project command>`
- Test: `<project command>`

## Project documentation configuration

- Standard source/version: `<immutable harness source or checked-in equivalent>`
- Project configuration: `docs/documentation.md` and `docs/documentation.en.md`
- Documentation check method/commands: `<actual commands or evidenced per-item manual methods>`
- Independent review record: `<PR/initiative validation location and reviewer mechanism>`
- Required CI checks: `<existing real check names; no invented gate>`

## Project-specific overrides

- `<add only rules that differ from the shared language standards>`
