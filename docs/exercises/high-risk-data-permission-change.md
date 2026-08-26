---
exercise_name: high-risk-data-permission-change
exercise_version: 1
risk_level: high
scenario_type: data-permission-change
lifecycle_stages: [1, 2, 3, 4, 5, 6, 7, 8]
required_templates:
  - opportunity-record.md
  - requirements-risk-package.md
  - solution-decision.md
  - verification-matrix.md
  - change-handoff.md
  - release-record.md
  - incident-record.md
  - outcome-retrospective-actions.md
---

# 高风险演练：角色权限与数据迁移

## 演练目标

验证账户权限模型和存量数据迁移同时变化时，团队是否会坚持独立设计/安全评审、负向授权证据、渐进发布、数据恢复和明确的人类 Go/No-Go。

## 初始条件

- 协作产品要把单一“成员”模型拆为查看者、编辑者和管理员；管理员可邀请成员和修改角色，只有资源所属工作区的成员可访问。
- 现有成员拟默认迁移为编辑者，现有工作区创建者成为管理员；约 200 万成员关系需要在线回填，旧服务版本仍会在发布窗口运行。
- 建议记录链：`OPP-RBAC-001` → `REQ-RBAC-001` → `DES-RBAC-001`/`VER-RBAC-001` → `CHG-RBAC-001` → `REL-RBAC-001` → `INC-RBAC-001`/`SEC-RBAC-001` → `RET-RBAC-001`。

## 阶段 1：需求与机会

- 使用[机会记录](../../templates/delivery/opportunity-record.md)记录客户隔离需求、当前权限限制、受影响租户和成功/护栏指标。
- 门禁：价值负责人明确；不能把“客户要求本周上线”当成跳过风险评估的理由。

## 阶段 2：澄清与立项

- 使用[需求与风险包](../../templates/delivery/requirements-risk-package.md)定义角色/动作/资源/租户矩阵、邀请与撤销、最后管理员、并发修改、审计、数据保留和支持场景。
- 风险必须为高：触发账户权限、跨租户隔离、存量迁移和核心数据完整性控制，并进入安全、隐私/合规、架构和运维评审队列。
- 注入：销售承诺了固定日期。期望决定是保留门禁或缩小首批范围，不降低风险等级。

## 阶段 3：方案与计划

- 使用[方案决策](../../templates/delivery/solution-decision.md)定义服务端唯一授权边界、deny-by-default、角色版本、审计事件、双读/双写兼容窗口、回填不变量和清理条件。
- 在[验证矩阵](../../templates/delivery/verification-matrix.md)建立主体、角色、动作、资源、租户矩阵，覆盖匿名、低权限、跨租户、已撤销身份、并发角色变更、回填重跑和部分失败。
- 恢复计划不能假定代码回滚会自动恢复角色数据；明确暂停、前滚修正、备份/重算和不兼容清理的停止条件。
- 门禁：威胁模型、迁移设计、验证策略、渐进发布、恢复预演和专家评审均有明确结论与责任人。

## 阶段 4：开发与自测

- 在拥有责任的服务端边界执行授权，不依赖 UI 隐藏；迁移可重入、可观测、分批且不覆盖较新的并发角色修改。
- 使用[变更交接](../../templates/delivery/change-handoff.md)记录当前 SHA、schema/回填版本、审计、配置、测试和残余风险。
- 门禁：正向功能、跨租户负向、竞态、事务、回填恢复、旧新版本并存和敏感日志边界均有测试。

## 阶段 5：集成验证

- 对最新 SHA 执行 CI、独立代码评审、契约、数据一致性、性能/并发、韧性恢复和安全授权专项验证。
- 硬停止注入：预生产验证发现编辑者能通过直接 API 修改其他工作区资源。唯一合格结论是阻塞，修复服务端授权并重新执行受影响矩阵和独立复审；UI 隐藏、风险豁免或“首批用户可信”均不合格。
- 更新[验证矩阵](../../templates/delivery/verification-matrix.md)和[变更交接](../../templates/delivery/change-handoff.md)，安全负责人和发布负责人基于最终 SHA 作出结论。

## 阶段 6：发布与变更管理

- 使用[发布记录](../../templates/delivery/release-record.md)固定 source SHA、制品摘要、迁移版本、审批、批次和恢复目标；只提升同一候选。
- 先部署向后兼容 schema/代码并影子评估授权差异，再按内部工作区、小租户、大租户逐批启用；每批检查拒绝/允许差异、跨租户信号、角色不变量、回填进度和延迟。
- 硬停止注入：第二批回填中断，2% 成员记录只有新角色而旧版本无法解释。期望是停止扩批，保护数据，按预演方案恢复兼容状态或前滚修正并验证不变量；不得盲目重跑或只回滚应用。

## 阶段 7：运行与支持

- 持续监控跨租户拒绝/允许异常、权限变更审计、最后管理员、回填收敛、支持请求和关键 SLO。
- 普通迁移故障使用[事件记录](../../templates/delivery/incident-record.md)；疑似越权或敏感数据访问立即进入 `security-privacy-incident-response` 并只在普通记录引用受限证据标识。
- 关闭前验证用户访问、数据不变量、威胁状态、沟通以及所需安全/隐私通知决定。

## 阶段 8：度量与复盘

- 使用[效果复盘与行动](../../templates/delivery/outcome-retrospective-actions.md)评估隔离目标、权限支持量、变更失败率、恢复时间和安全护栏。
- 对越权测试和迁移部分失败建立事实时间线，形成可验证的架构、测试、运行和流程行动；不以“操作失误”结束分析。

## 演练通过条件

- 高风险等级、专家评审和人类 Go/No-Go 从需求持续到每个生产批次。
- 跨租户越权注入必然阻塞，修复后证据对应最终 SHA 且覆盖服务端负向授权。
- 部分迁移失败能停止扩批并恢复已验证的数据不变量，不假设代码回滚等于数据恢复。
- 安全事件、普通事件和复盘记录共享标识但保持证据权限边界，整个链路可回溯。
