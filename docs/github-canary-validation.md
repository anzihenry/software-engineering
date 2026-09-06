# GitHub Canary 验收

真实 canary 用于验证离线矩阵无法证明的 GitHub 平台行为：新 workflow 在 PR 中触发、稳定 check 名、不同 runner、`gh` 状态发现、profile 范围内的 `bootstrap` 写入，以及写入后的 `doctor` 复核。它是第三层的内部验收设施，不是新的产品层，也不进入自动化包。

## 固定范围

受控仓库为 [`anzihenry/software-engineering-canary`](https://github.com/anzihenry/software-engineering-canary)。仓库只包含合成代码和自动化资产，不得写入凭据、个人信息、生产日志、真实事故内容或其他业务数据；仓库与 PR 不由自动化创建或删除。

每轮从干净的 canary `main` 建立四条互不合入的分支，覆盖每个内置 adapter 和 profile 一次：

| Adapter | Profile | 额外目标 | 证据 |
| --- | --- | --- | --- |
| Python | `full` | 从 `v1.1.0` 安装提交升级到任务 16 固定 SHA | [PR #1](https://github.com/anzihenry/software-engineering-canary/pull/1) |
| Node | `governance` | Node 24、npm lockfile 与治理门禁 | [PR #2](https://github.com/anzihenry/software-engineering-canary/pull/2) |
| Swift | `release` | `macos-15` 上真实编译 Swift Package | [PR #3](https://github.com/anzihenry/software-engineering-canary/pull/3) |
| Go | `incident` | Go 1.27 与事故治理边界 | [PR #4](https://github.com/anzihenry/software-engineering-canary/pull/4) |

机器可读结果见 [`automation/github-canary-evidence.json`](../automation/github-canary-evidence.json)。仓库自检固定检查四种组合、不可变源码 SHA、升级样本、两项成功 check 的证据 URL，以及最终治理结果；它不联网重新解释已经固定的历史记录。

## 单条链路

1. 使用固定 tag、完整 commit SHA 和显式 profile/adapter 生成安装 dry-run。
2. 在 canary 分支加入该语言的最小合成项目，显式应用安装并运行本地检查。
3. 推送分支并通过 `gh pr create` 创建低风险 PR。
4. 用 `gh pr checks` 等待 `validate` 与 `lifecycle-policy` 成功。
5. 在该分支运行只读 `doctor`，记录预期缺失项。
6. 生成 `bootstrap` dry-run；没有 blocker 后使用精确确认字符串应用。
7. 再次运行 `doctor`，要求相应 profile 健康。
8. 关闭而不合入 PR，保留分支提交、PR、Actions job 和评论作为证据。

首次 canary 按 `release → incident → governance → full` 应用仓库状态：release 验证默认只读权限；incident 创建生命周期标签并启用 Private Vulnerability Reporting；governance 依据真实证据 PR 建立 main ruleset 并启用合入后删除分支；full 最终确认三者并集没有剩余动作。

## 2026-09-07 验收结果

- 四条 PR 的 `validate` 和 `lifecycle-policy` 共八项 check 全部成功。
- Python/full 分支保留独立的 `v1.1.0` 安装提交与任务 16 升级提交，升级计划为 3 个新增、5 个安全更新、24 个不变、0 个冲突。
- Swift 和 Go 合成项目在推送前分别真实通过 `swift test` 与 `go test ./...`；GitHub runner 再次通过。
- incident 写入 13 个生命周期标签并启用 Private Vulnerability Reporting，写后 `doctor` 健康。
- governance 建立 active、无 bypass 的 `main required checks` ruleset，要求 `validate` 和 `lifecycle-policy`，并启用合入后删除分支；写后 `doctor` 健康。
- 最终 full `bootstrap` 无待执行动作，full `doctor` 健康。

## 重跑与失败边界

- 离线 16 组合仍是每次 CI 的快速门禁；真实 canary 在发布前、GitHub 权限模型变化或 adapter runner 发生实质变化时重跑。
- canary 不自动创建、重置或删除仓库，不自动合入 PR，也不自动放宽 ruleset。需要新一轮干净基线时由维护者明确决定保留策略。
- 任一 check、`doctor` 或 bootstrap 验证失败即停止后续写入；保留失败记录并在源仓库修复，不用重跑掩盖失败。
- 若证据来源、仓库或固定源码版本变化，必须更新证据 JSON、本文和仓库自检测试；历史 PR 不改写。
