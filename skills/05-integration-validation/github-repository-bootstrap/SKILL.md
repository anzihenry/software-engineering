---
name: github-repository-bootstrap
description: "为新建或尚未治理的 GitHub 仓库建立可重复的 PR 基线：验证稳定 CI check，配置默认分支 strict required-check ruleset，并开启合并后自动删除远端分支；适用于首次接入 GitHub 开发流程或审计现有设置时。"
---

# GitHub 仓库初始化

把已经存在且成功运行的 GitHub Actions 门禁固化为仓库级治理设置，使独立开发者或微型团队后续通过 PR 和稳定 required check 合入。此 SKILL 负责仓库设置的发现、差异规划、授权写入和验证；不替代项目 CI 设计，不把 workflow 名误当作 check 名，也不自行批准风险例外或合并 PR。

## 输入

- 目标 GitHub 仓库；默认从当前仓库的 `origin` 解析，也可由用户明确指定。
- 需要设为 required 的稳定检查；若未指定，从默认分支最近一次成功的目标 workflow check-run 中解析。
- 团队模式、期望的旁路策略，以及仓库或组织已经存在的 ruleset/branch protection 约束。

## 前置条件

- GitHub CLI 已对目标 host 登录，当前身份对仓库具有管理 ruleset 和仓库设置的权限。
- 目标 CI 已在默认分支至少成功运行一次，且提供不会随矩阵、路径或事件变化的稳定 job/check 名。
- required check 的内容已经覆盖项目规定的格式化、静态分析、构建和测试门禁；本 SKILL 只固化检查结果，不设计或伪造检查能力。

需要调用 GitHub REST API 时，读取 [GitHub ruleset 基线](references/github-ruleset-baseline.md)。

## 工作方式

1. **解析目标和权限**：确认仓库全名、默认分支、可见性、套餐能力、当前身份与管理权限；不得因当前目录存在 Git remote 就假设用户授权修改远端设置。
2. **读取现状**：获取仓库的 `delete_branch_on_merge`、仓库级 rulesets、默认分支有效规则、传统 branch protection 及最近 Actions/check-runs。记录组织级继承规则，但不尝试用仓库设置覆盖它们。
3. **锁定真实检查身份**：从成功 check-run 读取 `name` 和提供者 App ID。GitHub Actions required check 使用 job 名；不要使用 workflow 显示名，也不要仅凭预期字符串创建尚未实际运行的门禁。
4. **形成最小差异**：默认目标为 `delete_branch_on_merge=true`，并在默认分支启用 active、strict 的 required-status-check ruleset。required check 绑定最近实际提供结果的 GitHub App；默认不配置旁路主体。审批人数、对话解决、强推/删除保护、merge queue 和合并方式属于独立决策，不随本基线静默启用。
5. **处理已有规则**：若存在本 SKILL 管理的同名 ruleset，计算并展示更新差异；不存在时计划创建。若其他 ruleset 或 branch protection 已覆盖同一检查且语义兼容，保留现状并避免重复；存在冲突、未知旁路或组织策略时停止写入并说明冲突。
6. **请求远端写入授权**：在创建/更新 ruleset 或修改仓库设置前，展示目标仓库、规则名称、check/App、strict 与旁路状态，分别确认本次变更授权。读取和计划阶段的授权不能替代写入授权。
7. **幂等应用**：只修改已展示的字段，不删除未知规则、不扩大 token scope，也不把凭据或完整 API 响应写入仓库。部分写入失败时停止后续动作，报告已生效状态和安全恢复方式。
8. **验证有效规则**：重新读取 ruleset、默认分支有效规则和仓库设置；确认 required check 的 context、App、strict 状态、旁路能力及 `delete_branch_on_merge=true`，并确认默认分支已被 GitHub 标记为 protected。
9. **处理历史分支**：自动删除只影响设置生效后的合并。若刚合并的旧 PR 分支仍存在，仅在确认 PR 已合并且用户明确要求清理后删除；不要批量删除无法证明已合并的远端分支。

## 默认基线

| 设置 | 默认值 | 原因 |
| --- | --- | --- |
| 目标引用 | GitHub 默认分支 | 避免把 `main`/`master` 名称写死到跨项目流程 |
| required checks | 用户指定或成功 check-run 中确认的稳定 job 名 | 防止 required check 永久等待不存在的 context |
| strict | 开启 | PR 必须基于最新默认分支重新验证 |
| check 提供者 | 最近实际提供该 check 的 GitHub App | 防止其他身份伪造同名状态 |
| bypass actors | 空 | 默认不让管理员或自动化静默绕过门禁 |
| 合并后删分支 | 开启 | 减少已合并远端分支堆积 |

## 输出格式

```markdown
## GitHub 仓库初始化结果
- 仓库、默认分支与团队模式：
- 已确认的 required check、App 与证据提交：
- 既有 ruleset/branch protection 与冲突：
- 已创建或更新的 ruleset、ID 与链接：
- strict、旁路和 protected 状态：
- 合并后自动删分支状态：
- 未修改的相邻设置：
- 已执行验证、限制与后续动作：
```

## 停止条件

- 无有效 GitHub 身份、管理权限或套餐不支持目标规则时停止，不请求扩大权限范围来规避限制。
- 没有成功的稳定 check-run，或无法确认 check 名/App 身份时，先完成 CI 接入和一次可信运行，不创建可能锁死默认分支的 required check。
- 已有规则冲突、组织策略不明或目标差异未获授权时保持只读并给出最小解阻动作。
- 写入后只有在有效规则和仓库设置均重新读取并与目标一致时才报告完成；不能以 API 请求返回成功代替最终验证。
