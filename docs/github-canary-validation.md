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

历史机器结果保存在 [`v1.2.0原始证据`](../automation/github-canary-evidence-v1.2.0.json)；当前机器记录使用 [`automation/github-canary-evidence.json`](../automation/github-canary-evidence.json)。仓库自检固定检查四种组合、不可变源码 SHA、升级样本、两项成功 check 的证据 URL，以及最终治理结果；它不联网重新解释已经固定的历史记录。

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

## P1 后端/Web 当前候选试点

P1 使用新的隔离 PR，复用已有保护，不重新执行历史四组合设置写入。正常候选 [PR #7](https://github.com/anzihenry/software-engineering-canary/pull/7) 固定知识 eb674f606ba36b6b8e5b7da3c00c40b915c49f17；缺必需译文负例 [PR #8](https://github.com/anzihenry/software-engineering-canary/pull/8) 必须在真实 validate 阻塞，不能用 Draft 状态本身证明违规拒绝。

独立评审与 snapshot 由未参与修改者实际读取/执行后产生；维护者只发布经内容审查和公开出站授权的精确 envelope，其他原始材料按本地保留策略保存。不可变记录位于 [fa7f2a0 的 review-evidence.json](https://github.com/anzihenry/software-engineering-canary/blob/fa7f2a0ab852ce36000fbd63a6c63abb2da43b16/review-evidence.json)。候选文件不能携带自身批准，必需检查不能豁免；固定 clean 读取器核对原报告、当前开放 PR、head/base/merge、发布者、实际 CI/App 与权限。

本轮 ruleset 22393223 的 validate/lifecycle-policy 仍绑定 App 15368，harness-independent-review 仍为已授权现存必过状态，strict 和无旁路保持；不增加设置写入。单 owner 的 API 可见审计不覆盖组织/第三方 App/token 的全部写入路径。读取通过后仍不获得合入或生产授权，试点关闭而不合入，实际时间和结果见[分步记录](harness-p1-validation.md)。

## v1.3.0发布前复验（2026-10-17）

本轮固定自动化源码 `283f9ee85763dc9e8f47f4717b172e6862be9949`，从既有干净main分别建立4条不合入测试分支：[Python/full #9](https://github.com/anzihenry/software-engineering-canary/pull/9)、[Node/governance #10](https://github.com/anzihenry/software-engineering-canary/pull/10)、[Swift/release #11](https://github.com/anzihenry/software-engineering-canary/pull/11)、[Go/incident #12](https://github.com/anzihenry/software-engineering-canary/pull/12)。当前8项实际Actions检查通过，全部已关闭而未合入；测试分支/提交和首次失败保留。

Python从官方v1.2.0包实际安装并提交，再升级至固定新源码；4项目本地原生测试均通过，远端按实际runner再验。Swift沿用既有tools-version6.0合成fixture，不等Swift6.4最低规范已在adapter强制；不借验证自动升级工具链。原4条PR因测试正文change-id含小写被policy拒绝，保留原body/失败run，仅修大写后重验，不改代码或弱化门禁。

每组doctor健康，bootstrap dry-run的actions/blockers均空；随后实际执行零动作幂等apply并再次doctor健康，未改规则/标签/权限。ruleset22393223保留strict、无旁路及原P1的harness-independent-review第三项，当前自检精确核3项；该保护存在不等本轮PR取得第三项状态，更不授权合入。原v1.2.0证据原字节归档，当前JSON承接本轮结果，机器结构检查不联网认证真实性。

最终发布文档/自检/证据提交与此源码不同时，独立核对manifest/full全部33项逐字节一致及ZIP摘要相同；该canary仅复用相同自动化制品的有效范围，最终完整候选仍另跑检查/PR/main及Actions，源代码变化不得沿用。当前原始日志、平台响应、升级/诊断/零动作证明随本版发布验证附件保全。
