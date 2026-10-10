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

## Default GitHub governance / GitHub 默认治理

- On first harness adoption or governance drift, use `$github-repository-bootstrap` to enable and verify default-branch protection and `delete_branch_on_merge=true`. New projects default to `main`; protect the actual default branch in existing projects. Use `$github-actions-bootstrap` first when trustworthy stable CI checks are missing.
- GitHub 项目首次采用或治理漂移时，默认使用 `$github-repository-bootstrap` 启用并验证默认分支保护和合并后自动删分支；新项目默认 `main`，已有项目保护实际默认分支。缺少可信稳定 CI 时先使用 `$github-actions-bootstrap`。
- Reuse explicit authorization already provided; prepare reviewable differences before obtaining missing remote-write authorization. Keep governance incomplete when permission, platform capability, evidence, or compatible rules are missing. Loading instructions or installing files is not proof of enforcement; daily PRs must verify this baseline before declaring merge readiness. Non-GitHub projects record this as inapplicable.
- 复用已有明确授权；缺少远端写入授权时先准备可审查差异。权限、平台能力、证据或规则兼容性不足时记录治理未完成；加载入口或安装文件不证明远端已生效，日常 PR 合入就绪前须验证基线。非 GitHub 项目标记不适用。
- Make the pinned harness `docs/github-repository-defaults.md` / `.en.md` and both bootstrap skills accessible, or provide checked-in equivalents; report missing prerequisites instead of claiming completion.
- 确保固定版本的 harness 默认治理双语规范和两个初始化技能可访问，或提供项目提交的等价副本；依据缺失时报告缺口，不声称完成。

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
