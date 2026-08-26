---
owner: release-manager
scope: "Lifecycle phase 6: release and change management"
status: active
review_by: "2027-02-26"
---

# 阶段 6：发布与变更管理

## 目标

将通过验证的版本以受控、可观测、可恢复的方式交付到生产环境或目标用户。

## 输入

- 经批准的版本/构建产物、测试证据、变更风险等级和发布候选说明。
- 部署配置、环境状态、监控与告警、发布窗口、迁移和回滚预案。
- GitHub source SHA、Actions 运行、Environments/Deployments、Release/标签及制品存储能力。

## 流程

1. **登记变更并选择模式**：关联 PR、source SHA、风险、交付渠道和目标环境；选择标准发布、已预先批准的低风险连续发布或紧急变更。截止日期压力本身不构成紧急模式。
2. **准备发布候选**：固定版本和候选 source SHA，在受控 Actions 中只构建一次；记录每个制品/镜像/安装包的不可变标识和摘要，准备迁移、兼容范围、Release notes 与恢复目标。
3. **执行发布就绪检查**：核对候选证据、环境/依赖、GitHub workflow 与凭据边界、观测、告警、特性开关、迁移、恢复、发布批次和值守安排，形成 Go/No-Go 建议。
4. **预演非生产路径**：将同一候选提升至 staging、内部测试或 prerelease 渠道，验证部署、迁移、配置、关键用户路径、健康检查和恢复操作；不能预演的风险必须显式保留。
5. **作出生产 Go/No-Go**：由有权限的人类确认发布范围和当前证据。GitHub Environment 支持审批时使用保护规则；独立开发者或套餐不支持时保留明确的 `workflow_dispatch`/决策记录，不让 Agent 代替人类批准生产动作。
6. **执行一个渐进批次**：优先使用特性开关、金丝雀、灰度、分阶段商店发布或分批部署；生产环境一次只允许一个部署，提升同一制品且不夹带新改动。
7. **观察并判定健康**：依据预先定义的业务、错误率、延迟、资源、数据完整性、用户反馈和 SLO 指标判定继续、扩大、暂停、回滚、前滚或转入事故响应。
8. **暂停并执行恢复**：达到停止条件时立即停止扩大范围；按授权优先关闭开关、恢复旧配置/制品、处理迁移或部署已验证前滚修复，并验证用户与数据实际恢复。
9. **完成目标渠道分发**：健康窗口通过后继续下一批次直至目标范围；服务、应用商店和包/Release 分发分别遵循其可恢复性和版本不可覆盖约束。
10. **发布收口与交接**：记录实际 source SHA、制品摘要、GitHub deployment、标签/Release、上线范围和最终状态；更新变更说明、运行手册、支持信息和复盘行动。

## 发布模式

| 模式 | 适用条件 | 可压缩内容 | 不可省略 |
| --- | --- | --- | --- |
| 标准发布 | 默认模式；普通中高风险变更 | 无 | 候选、就绪、生产决策、渐进/观察、恢复、收口 |
| 低风险连续发布 | 变更类型和自动恢复已预先批准，影响受控且观测成熟 | 可自动完成 staging 和预设生产批次 | 同一制品、硬停止阈值、部署串行、可恢复和完整记录 |
| 紧急变更 | 正在缓解严重生产影响或紧迫安全风险，标准时序无法满足恢复目标 | 缩短等待、评审和验证范围 | 事件/授权、最小 diff、目标测试、恢复、观测、主线同步和事后补验 |

## GitHub 小团队基线

| 控制点 | 建议实现 |
| --- | --- |
| 候选身份 | source SHA + 版本 + Actions run + 制品摘要组成发布清单；环境间只提升同一制品 |
| 工作流边界 | 候选构建、环境部署、健康/收口职责分离；重复逻辑使用同仓库 reusable workflow |
| 环境 | 至少区分 `staging` 与 `production`；使用 GitHub Environment 记录 deployment、限制分支并隔离变量/密钥 |
| 生产决策 | 独立开发者保留手动 Go/No-Go；微型团队可由另一维护者审批。套餐不支持 required reviewers 时不得虚构平台审批 |
| 部署互斥 | `production` concurrency 同时只运行一个部署；不自动取消正在执行的生产任务，以免遗留半完成状态 |
| 身份与密钥 | Actions 默认最小权限，云平台优先 OIDC 短期凭据；签名和发布密钥仅暴露给对应 environment/job |
| 发布记录 | GitHub Deployment 记录环境推进，Draft/Prerelease/Release 与标签记录外部分发；公开版本和制品不可原地覆盖 |
| 旁路 | 管理员旁路只用于已授权紧急恢复，必须记录原因、范围、结果和后续补验 |

GitHub 某些 Environment 审批、等待或密钥能力受仓库可见性和套餐影响；流程应根据实际可用能力降级为明确的人工触发和审计记录，而不是删除生产决策门禁。

## 交付渠道差异

| 渠道 | 渐进单位 | 主要恢复手段 | 特别约束 |
| --- | --- | --- | --- |
| Web/后端服务 | 实例、区域、租户、流量或特性开关 | 关开关、旧制品回滚、前滚修复 | 数据迁移需保持兼容窗口，不能假设代码回滚会自动恢复数据 |
| 移动/桌面应用 | 内测、测试用户、商店分阶段比例 | 停止扩大发布、远程开关、服务端兼容、前滚版本 | 已安装客户端通常无法即时撤回，签名制品和版本号不可随意替换 |
| 库、CLI、镜像和下载制品 | prerelease、渠道、包仓库标签 | 撤下渠道、弃用、发布修复版本 | 已公开同版本不得覆盖不同内容，下游缓存和兼容范围需记录 |

## 决策门禁

发布包含四个门禁：候选门禁确保 source SHA、制品和证据一致；生产门禁确保环境、授权、观测和恢复就绪；批次门禁确保健康数据支持继续；收口门禁确保目标范围、实际版本、运行交接和对外状态一致。任何继续推进都必须基于观测结果，而非仅基于部署命令成功。

## 输出

- 发布候选清单、已发布版本、GitHub Actions/Deployment/Release 记录、制品摘要、变更记录、观察结果和对外/对内通知。
- 发布结论：`成功`、`已回滚`、`前滚修复中` 或 `暂停`。
- 使用[发布记录模板](../../templates/delivery/release-record.md)关联候选身份、Go/No-Go、批次、健康与恢复证据。

## 异常与回流

- 指标超过阈值：立即按预案暂停、回滚或前滚，必要时转入事故响应。
- 迁移失败：停止后续推进，按恢复计划处理数据一致性并升级风险。
- 发布窗口失效：保持当前稳定版本，重新计划；不要为了赶窗口跳过门禁。
- GitHub Environment 或套餐能力不可用：保留手动触发、最小权限和决策记录，不把技术限制解释为免审批。
- 紧急变更：进入受控快速通道，缓解后必须同步主线、补验并形成复盘输入。

## 交接给下一阶段

交接生产版本、上线范围、监控链接、观察期限、已知问题和支持指引给运行与支持团队。

## 固化为 SKILL

| 行为 | SKILL | 适用边界 | 产出 |
| --- | --- | --- | --- |
| 编排 GitHub 小团队从候选到发布收口 | [`github-release-management`](../../skills/06-release-and-change-management/github-release-management/SKILL.md) | 独立开发者或微型团队需要用 GitHub 串联候选、环境、部署、健康、恢复和 Release 时 | 当前发布状态、门禁、授权和下一动作 |
| 固定版本并准备可提升的发布候选 | [`release-candidate-preparation`](../../skills/06-release-and-change-management/release-candidate-preparation/SKILL.md) | 已验证提交需要构建、签名、生成摘要或 Draft Release 时 | 发布候选清单与候选就绪结论 |
| 核对版本、环境、审批、观测和恢复条件 | [`release-readiness`](../../skills/06-release-and-change-management/release-readiness/SKILL.md) | 发布候选进入目标环境前 | Go/No-Go 结论及未满足条件 |
| 按授权预案分批推进并记录每一步 | [`progressive-release-execution`](../../skills/06-release-and-change-management/progressive-release-execution/SKILL.md) | 需要执行灰度、金丝雀、开关或分批发布时 | 发布步骤记录与当前范围 |
| 基于预设指标判断继续、暂停或恢复 | [`release-health-assessment`](../../skills/06-release-and-change-management/release-health-assessment/SKILL.md) | 每个发布批次及观察窗口内 | 健康判定与处置建议 |
| 按授权预案执行回滚或前滚恢复 | [`release-recovery-execution`](../../skills/06-release-and-change-management/release-recovery-execution/SKILL.md) | 发布达到暂停/恢复条件，需要控制用户影响时 | 恢复步骤、验证证据与当前影响 |
| 管理正在缓解严重影响的紧急变更 | [`emergency-change-management`](../../skills/06-release-and-change-management/emergency-change-management/SKILL.md) | 标准发布时序无法满足生产事件或紧迫安全风险的恢复目标时 | 紧急授权、最低证据、部署恢复和补验记录 |
| 收口稳定发布并交接运行信息 | [`release-closure`](../../skills/06-release-and-change-management/release-closure/SKILL.md) | 观察窗口稳定、准备完成发布时 | 发布结论、变更记录和支持交接 |

`github-release-management` 是阶段编排入口；候选准备、就绪判断、渐进执行、健康判断、恢复执行、紧急通道和收口分别保留独立职责。实际部署、商店/包发布、回滚、前滚、Environment 审批和管理员旁路均须由具备权限的人员或自动化在明确授权下执行。
