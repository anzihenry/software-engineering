---
title: "Harness P0 采用试点验收"
status: current
owner: quality-lead
updated: "2026-10-12"
---

# Harness P0 采用试点验收

## 对象与证据范围

本轮在隔离临时 Git 项目执行采用诊断正反例，再在用户指定的 anzihenry/software-engineering-canary 隔离 checkout 执行真实研发评审、现有安装器和 GitHub 平台验证。采用的知识资产固定为 software-engineering `952e840752741431c027097b5c242b7bc7fa3be5`；新采用工具由本步文件 SHA-256 及最终提交绑定，不把开发工作树称为已发布知识版本。

- 正常 [PR #5](https://github.com/anzihenry/software-engineering-canary/pull/5)：head `276b41057b71de2c980940e49767629f21abffbc`，base `a37d46a346b0d955d99db1c55aa65df1fb281a71`，验收时 GitHub merge 候选 `681c1637dbc1c5b8e6067e9693852452472d9724`。
- 文件快照 `fd264fb5aff664a7098818155a651c9ce36cd60a9416e33e1965dcf9313e8cdf`，真实独立 Agent `/root/canary_independent`，作者 `/root` 与 anzihenry；评审时间 `2026-10-11T14:40:20.090949+00:00`。
- [不可变评审 envelope](https://github.com/anzihenry/software-engineering-canary/blob/352eb51ded31825e11da109cc355d404a7adf056/review-evidence.json)：真实独立读取、命令输出、五项内容检查、九领域影响、修正复核及要求 ID；该提交不在候选历史内。
- [不可变平台原始观察](https://github.com/anzihenry/software-engineering-canary/blob/2f90847fbd53cc228a54bc5ffc6fc3959b1e9d32/pilot-observations.json)：实际失败 CI、规则前后差异/有效规则、可信读取、服务器阻断与 PR 关闭结果；它是报告，不能冒充第二次评审批准。
- [当前 head 本地采用报告](https://github.com/anzihenry/software-engineering-canary/blob/dac2d468101d76709828dcb57e24d88bc582f1cb/current-adoption-observation.json)：最终采用工具摘要、真实 argv、环境路径和输出。早期 local-commands-final.json 在未提交修正期间记录旧 head cd21f63，只保留过程证据；最终对象以独立报告及本报告为准。

原始本地工作报告在 /tmp/harness-p0-evidence/04；长期关键原始报告已提交到候选历史外的固定证据提交。报告生成不改变独立评审 verdict。评审与远端读取在 PR 开放期间完成；关闭后的 PR 按读取器契约不能再作为当前开放候选通过，历史验收结论不自动用于下一条 PR。

## 本地采用与实际行为

临时项目行为测试创建独立 Git 基线/任务分支和固定知识 checkout，实际执行命令并核对阻塞输出。覆盖正常可访问与实测、缺规范、错 pin、漏局部入口、入口摘要改变、默认分支操作、缺命令、伪责任值/common 替代匹配语言、不可执行工具、失败输出、超时 partial/此前报告保留、argv 字面花括号/比较表达式、命令成功但改变源时阻塞、文件删除/同字节外链替换保留报告及前后文件绑定。只读诊断不证明 Agent 加载，也不提升命令权限。

真实 canary 使用 Python 3.14.8、Ruff 0.16.7、PyYAML 6.0.3，无生产依赖；format/lint、py_compile、unittest、固定文档 check 均实际运行。独立 Agent 自行读取目标入口、父运行指令与覆盖范围、固定编码 SKILL/common/Python、文档规范/技能/模板、全部变更和中英文件，执行项目命令、README 示例和两侧非法参数/大整数探针；其工具读取清单、原始输出与 scope 判断保存在 envelope 报告，不只依赖“已加载”自述。

既有安装器 governance/custom dry-run 为 28 创建、1 未变、0 冲突，随后应用；保留原 workflow，不扩张第一层分发。受影响 README 立即双语；未触及 CANARY 原始英文政策登记限期迁移（maintainer，2026-11-01）。两份固定上游安装器原始输入保持原始字节并经独立 hash 对照，以 raw 登记；双语项目文档说明其中文/英文原文、来源、用途与范围。AGENTS 为实际运行路由输入，正式项目知识仍走双语 documents 清单，不能把新的正式指南批量标成 raw。

独立评审先发现双语配置缺实际命令/复验/来源说明及 README 缺最短示例，作者修正后另起上下文评审者实际复核。首次 CI 因浅 checkout 缺候选祖先链而失败，原日志保留；项目 custom adapter 经审查补全历史 fetch，重新跑当前 head，未删除检查或放宽结果。

## 真实平台与信任来源

[validate](https://github.com/anzihenry/software-engineering-canary/actions/runs/38147875425/job/114494927778) 与 [lifecycle-policy](https://github.com/anzihenry/software-engineering-canary/actions/runs/38147875437/job/114494927979) 均为当前正常 head 的 completed/success，实际 GitHub Actions App ID 15368。validate 真实覆盖固定开发依赖安装、格式、静态检查、构建、测试和固定文档规则；lifecycle-policy 校验当前 PR 记录。

发布者 anzihenry 当时为唯一可见 collaborator 写入者（admin/push），Actions 默认 read 且不能自批 review；显式两项 workflow 最小权限也被读取。受控策略在候选 checkout 外，固定来源/发布者/CI App；真实 trusted_review.py 核验 publisher、不可变 envelope、完整作者、文件摘要、head/base/merge、当前 CI，并在结束时再次回读候选，通过结果保留。

用户明确授权仅追加 harness-independent-review 必过状态。现有 bootstrap 应用器消费经审查的最小计划：更新 [ruleset 22393223](https://github.com/anzihenry/software-engineering-canary/rules/22393223)，保留 validate/lifecycle-policy App 15368、strict、无旁路、PR/删除/非快进规则及其他设置；未改 Actions 默认权限、删分支设置或 environments。回读 ruleset 和 main 实际有效规则确认三项必过，前后剔除唯一追加项后逐字段一致。既有 doctor 前后均 healthy、findings 空。

## 正反例结果

| 场景与实际对象 | 方法/证据 | 结果 |
| --- | --- | --- |
| 正常采用与非作者真实任务 | 临时行为测试、当前 head 本地报告、Agent 独立轨迹与 gate | 本地与观察范围通过；可访问和加载行为分别判断 |
| 缺技能/规范、错误 pin、局部入口覆盖、不可执行命令 | 临时 Git 项目实际诊断/命令负例 | blocked，保留真实错误/失败范围，不写成功 |
| 旧独立评审/入口摘要 | 隔离 clone 修改 AGENTS，运行真实原 gate/采用诊断 | snapshot stale、entrypoint changed，均 blocked；正常候选未被改动 |
| 缺必需译文 | [PR #6](https://github.com/anzihenry/software-engineering-canary/pull/6) head `33e1d7f30f1613ee30b137e4d68c40a7f1cf0abf`；[真实失败 CI](https://github.com/anzihenry/software-engineering-canary/actions/runs/38147926362/job/114495078759) | 缺 README.en 导致 validate failure，服务器 blocked |
| 必过测试失败 | PR #6 head `2996d3df89830ca7bb2f96a0891928f07b9fafc0`；[真实失败 CI](https://github.com/anzihenry/software-engineering-canary/actions/runs/38148058778/job/114495479299) | 恢复译文后注入合成加法错误，真实 unittest AssertionError，服务器 blocked |
| 缺可用独立状态 | 正常 head，实际将受信状态暂置 pending；有效规则已含第三必过项 | 服务器 blocked；读取器 trusted review missing or not successful；恢复真实 success 后 clean |
| 治理漂移 | 既有治理测试向检查器注入 strict/App/规则/权限漂移，真实平台前后 doctor 与规则回读 | 漂移模拟被拒绝；未在远端故意放宽保护，此项不冒充真实远端改坏试验 |
| 收口 | 两 PR closed/merged=false，main 回读仍为完整 base SHA | 正反例 PR 关闭未合入，分支与证据保留，无生产动作 |

旧 SHA、自评、漏读、伪 CI/App、候选变化与非受信写入者等来源负例由 P0-03 API 边界测试覆盖；这些为明确的模拟，不冒充本轮真实平台写入。初次失败、缺译文与测试失败保留对应旧 head 的日志，不使用最新状态覆盖历史结果。

## 结论、限制与影响

本地采用、实际非作者任务观察、受信维护者读取及三项远端必过门禁在上述固定对象范围验收。平台只验证服务器 blocked/clean 状态，没有尝试受保护合并，更没有生产发布/部署；CI 基于真实 PR merge checkout，但独立 gate 不自动证明完整合并树语义。维护者见证来源不等于密码学证明 Agent 身份，独立 Agent 也不是 GitHub 人工批准。

当前 API 无法列出全量安装 App/token 权限路径（实际 404/403），不声明全部授权渠道安全；此结论限定 API 可见受信 owner 小仓库模式。多人写入、组织/第三方 App 或更复杂权限项目在部署采用前仍须审计实际权限，必要时转为受控 App/服务。新项目、成熟项目、离线/非 GitHub 项目分别按采用规范决定适用范围；缺权限/网络不能改成不适用。一条合成 canary 不证明其他项目已经采用。

九领域影响：工程新增采用运行器与行为测试；指南/计划/导航更新采用、技能职责和路由；研究/产品/设计无目标产品变化；目标正式专题/版本发布未发生，相关领域不适用并保留理由。未新增 SKILL，未重排资产库、未升级工具链或生产依赖。Harness 中文资产无需英文副本；新增采用输出模板与目标正式文档已中英独立核对。最终仓库检查与非作者独立验收绑定本步摘要快照，相关变化使原结论失效。

后续入口、知识 pin、命令/依赖/工具、责任或平台权限/规则改变后复验；canary 未来 PR 必须真实发布新 head 的受信评审状态，不能沿用本轮不可变记录或把关闭 PR 当新候选。全规范覆盖能力与每个目标采用状态仍由矩阵/项目证据分别维护，不因本轮 P0 实施而将所有条款改写为已自动强制。
