---
name: github-repository-bootstrap
description: "为新建或尚未治理的 GitHub 仓库建立可重复的安全设置：消费首次 Actions PR 的可信 check 交接，收紧 workflow token，配置 environments、strict required-check ruleset 与合并后删分支，并在明确授权后完成唯一的引导 PR；适用于首次仓库治理或后续审计，不用于日常 PR 合并。"
---

# GitHub 仓库初始化

把 `$github-actions-bootstrap` 在首次 PR 上产生的可信门禁固化为仓库级治理设置，使独立开发者或微型团队后续通过 PR 和稳定 required check 合入。此 SKILL 负责仓库设置的发现、差异规划、授权写入、首次引导收口和验证；不替代项目 CI/CD 设计，不把 workflow 名误当作 check 名，也不把引导期的受限合并权扩大到日常 PR。

## 输入

- 目标 GitHub 仓库；默认从当前仓库的 `origin` 解析，也可由用户明确指定。
- `$github-actions-bootstrap` 输出的交接记录；后续审计也可使用默认分支最近一次成功的稳定 check-run。
- 团队模式、期望的旁路策略，以及仓库或组织已经存在的 ruleset/branch protection 约束。
- 需要治理的 GitHub Environments 及其审批、分支/tag 限制；未在交接或用户输入中出现时不创建。

## 前置条件

- GitHub CLI 已对目标 host 登录，当前身份对仓库具有管理 ruleset 和仓库设置的权限。
- 目标 CI 已在交接所指 bootstrap PR 的当前 head SHA 或默认分支上成功运行，且提供不会随矩阵、路径或事件变化的稳定 job/check 名。
- required check 的内容已经覆盖项目规定的格式化、静态分析、构建和测试门禁；本 SKILL 只固化检查结果，不设计或伪造检查能力。

需要调用 GitHub REST API 时，读取 [GitHub 仓库设置基线](references/github-ruleset-baseline.md)。消费 Actions 引导证据或完成首次 PR 时，读取 [Bootstrap 收口](references/bootstrap-finalization.md)。

## 工作方式

1. **解析目标和权限**：确认仓库全名、默认分支、可见性、套餐能力、当前身份与管理权限；不得因当前目录存在 Git remote 就假设用户授权修改远端设置。
2. **验证交接范围**：若提供 Actions bootstrap handoff，重新读取其中唯一的仓库、PR、head ref/head SHA 和 check-run；要求 PR 仍开放、最新 head 未改变、目标检查成功且 App 一致。任一字段漂移即拒绝交接，返回 `$github-actions-bootstrap` 刷新运行证据。
3. **读取现状**：获取 `delete_branch_on_merge`、Actions 默认 workflow 权限、目标 environments、仓库级 rulesets、默认分支有效规则和传统 branch protection。记录组织级继承规则，但不尝试用仓库设置覆盖它们。
4. **锁定真实检查身份**：从交接 PR 当前 head 或默认分支的成功 check-run 读取 `name` 和提供者 App ID。GitHub Actions required check 使用 job 名；不要使用 workflow 显示名，也不要仅凭预期字符串创建尚未实际运行的门禁。
5. **形成最小差异**：默认收紧 Actions token 为只读且不能创建/批准 PR review，开启 `delete_branch_on_merge`，并在默认分支启用 active、strict 的 required-status-check ruleset。检查绑定实际 App，默认无旁路。只为交付 workflow 已引用且用户确认的 environments 规划保护规则。
6. **处理已有规则**：若存在本 SKILL 管理的同名 ruleset，计算并展示更新差异；不存在时计划创建。若其他 ruleset、branch protection、Actions 权限或 environment 规则已经满足目标，保留现状；存在冲突、未知旁路或组织策略时停止相应写入并说明冲突。
7. **请求远端写入授权**：展示目标仓库、Actions 权限、environment 差异、ruleset/check/App、strict、旁路和删分支设置，确认本次设置变更。读取与计划授权不能替代写入授权；引导 PR 的合并需要之后单独确认。
8. **幂等应用**：只修改已展示字段，不删除未知规则、不覆盖 secrets、不扩大 token scope，也不保存凭据或完整 API 响应。按 Actions 权限、environments、ruleset、仓库设置的顺序应用；部分失败时停止后续动作，报告已生效状态和恢复方式。
9. **验证有效设置**：重新读取 Actions 权限、environments、ruleset、默认分支有效规则和仓库元数据；确认 check context/App、strict、旁路、protected 状态及 `delete_branch_on_merge=true` 均与计划一致。
10. **收口首次引导 PR**：仅当交接有效、最新 check 全绿、PR 可合并且用户明确授权时，合并交接中唯一的 bootstrap PR。等待合并提交在默认分支上的 `validate` 成功，再确认远端 head branch 已被自动删除；本地分支仅在不承载未推送提交且不为当前分支时删除。
11. **保持日常边界**：不合并交接之外的 PR，不复用此次授权处理后续 PR。后续开发、评审与合入使用 `$github-pr-integration`；历史分支仅在逐个证明对应 PR 已合并并获得清理授权后处理。

## 默认基线

| 设置 | 默认值 | 原因 |
| --- | --- | --- |
| 目标引用 | GitHub 默认分支 | 避免把 `main`/`master` 名称写死到跨项目流程 |
| Actions 默认 token | `read`，且不能批准 PR | 降低未显式声明权限的 workflow 风险 |
| required checks | 交接 PR 当前 head 或默认分支成功 check-run 中确认的稳定 job 名 | 首次配置无需人工预跑，且防止等待不存在的 context |
| strict | 开启 | PR 必须基于最新默认分支重新验证 |
| check 提供者 | 最近实际提供该 check 的 GitHub App | 防止其他身份伪造同名状态 |
| bypass actors | 空 | 默认不让管理员或自动化静默绕过门禁 |
| 合并后删分支 | 开启 | 减少已合并远端分支堆积 |
| environments | 仅创建交付 workflow 已引用且明确确认的名称 | 避免空壳环境或错误保护制造虚假 CD 保证 |

## 输出格式

```markdown
## GitHub 仓库初始化结果
- 仓库、默认分支与团队模式：
- Actions bootstrap handoff、PR 与 head SHA：
- Actions 默认 workflow 权限：
- Environments 与保护规则：
- 已确认的 required check、App 与证据提交：
- 既有 ruleset/branch protection 与冲突：
- 已创建或更新的 ruleset、ID 与链接：
- strict、旁路和 protected 状态：
- 合并后自动删分支状态：
- Bootstrap PR 合并、默认分支 CI 与远端/本地分支清理：
- 未修改的相邻设置：
- 已执行验证、限制与后续动作：
```

## 停止条件

- 无有效 GitHub 身份、管理权限或套餐不支持目标规则时停止，不请求扩大权限范围来规避限制。
- 交接 PR/current head 不匹配，或没有成功的稳定 check-run，或无法确认 check/App 时，返回 Actions 引导刷新证据；不要求用户手动在默认分支预跑，也不创建可能锁死分支的 required check。
- 已有规则冲突、组织策略不明或目标差异未获授权时保持只读并给出最小解阻动作。
- 设置写入后只有在有效规则和仓库设置均重新读取并与目标一致时才报告治理完成；不能以 API 请求返回成功代替最终验证。
- 未获得独立合并授权、PR 不可合并或默认分支合并后 CI 未成功时，不报告首次引导收口完成；保留准确的当前状态供用户继续。
