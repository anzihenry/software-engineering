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
- Assess file-level documentation impact, keep target-project documents in Chinese and English synchronized; maintain harness standards and skills in Chinese, and update affected maintained knowledge, metadata, relative links, and navigation. Existing projects migrate incrementally; affected legacy documents must comply with the current delivery.
- Before merge, initiative completion, or formal publication, obtain `$documentation-delivery-validation` from a non-author human or a separate independent Agent context. Record actual files/evidence inspected and bind the verdict to the current commit or digest snapshot.
- Required documentation checks cannot be waived or conditionally passed. Use actual manual/temporary checks until dedicated tooling exists; existing required CI still must pass. Relevant changes require revalidation.
- Apply target-project directory conventions only to product/project documentation; preserve the structure and governance contracts of a harness asset repository.

## Git 分支开发与管理

- 修改代码、文档或配置前默认调用 `$git-branch-management`，依据固定版本的 harness `docs/git-branch-workflow.md` 或项目等价规范检查分支、工作区及任务归属，fetch 后创建/复用功能分支。默认/受保护分支不承载任务修改或新提交；“提交、推送”默认针对任务分支。
- 功能分支使用 `<当前 coding agent 标识>/<简短任务名>`（如 `codex/...`、`deepseek-harness/...`），一个分支对应一个可独立评审任务，已有对应分支复用，更换 Agent 不因此重命名；用户/项目具体规范优先。
- 同步、误提交恢复和合入后清理由该技能按实际需要处理，保护无关、未提交和未推送工作，兼顾 Squash 和其他 worktree；不由加载技能推导推送、删除或合并授权。
- 保证技能及中文规范可访问；缺失时报告缺口，不声称合规。非 Git 项目标记不适用。

## GitHub 默认治理

- GitHub 项目首次采用或治理漂移时默认使用 `$github-repository-bootstrap` 启用并验证默认分支保护和合并后自动删分支；新项目默认 `main`，已有项目保护实际默认分支。缺少可信稳定 CI 时先使用 `$github-actions-bootstrap`。
- 复用已有明确授权；缺少远端写入授权时先准备可审查差异。权限、平台能力、证据或规则兼容性不足时记录治理未完成；加载入口或安装文件不证明远端已生效。日常 PR 合入就绪前须验证基线，非 GitHub 项目标记不适用。
- 保证固定版本的 harness `docs/github-repository-defaults.md` 和两个初始化技能可访问，或提供项目提交的等价副本；依据缺失时报告缺口。

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
