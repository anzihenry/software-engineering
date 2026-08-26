---
exercise_name: medium-risk-feature
exercise_version: 1
risk_level: medium
scenario_type: feature
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

# 中风险演练：保存默认筛选功能

## 演练目标

验证普通功能跨越 Web 状态、后端 API 和低敏偏好持久化时，团队能否保持契约兼容、失败语义、端到端证据和可控发布。

## 初始条件

- 用户希望保存一个项目列表默认筛选条件，下次登录自动恢复；偏好包括状态和排序，不包含敏感数据。
- 现有旧客户端不知道该字段，列表 API 有缓存，数据库尚无偏好列；功能可由服务端开关关闭。
- 建议记录链：`OPP-FILTER-001` → `REQ-FILTER-001` → `DES-FILTER-001`/`VER-FILTER-001` → `CHG-FILTER-001` → `REL-FILTER-001` → `INC-FILTER-001` → `RET-FILTER-001`。

## 阶段 1：需求与机会

- 使用[机会记录](../../templates/delivery/opportunity-record.md)记录重复设置筛选的用户比例、任务耗时和反馈证据。
- 门禁：成功指标、目标用户、隐私边界和不保存自由文本的非目标明确。

## 阶段 2：澄清与立项

- 使用[需求与风险包](../../templates/delivery/requirements-risk-package.md)定义首次使用、保存、清除、跨设备、无效值、未登录、后端失败和旧客户端行为。
- 风险评为中：涉及普通功能、内部 API、缓存和持久化，但不改变授权或敏感数据范围。
- 注入：产品要求“保存全部搜索词”。期望决定是识别数据/隐私范围扩大并单独评估，而不是沿用中风险结论。

## 阶段 3：方案与计划

- 使用[方案决策](../../templates/delivery/solution-decision.md)比较客户端本地保存与服务端保存，定义 schema、默认值、版本兼容、幂等更新、缓存失效和删除语义。
- 在[验证矩阵](../../templates/delivery/verification-matrix.md)覆盖单元、契约、数据库、缓存、端到端、性能和恢复场景。
- 注入：旧客户端会忽略新增响应字段但更新请求不会发送该字段。参与者需证明向后兼容和默认值语义。
- 门禁：迁移向前兼容、开关和回退/前滚路径明确，任务拆为可审查切片。

## 阶段 4：开发与自测

- 按前端、API、领域数据边界实现；迁移先兼容旧代码，缓存键/失效与服务端事实来源一致。
- 在[变更交接](../../templates/delivery/change-handoff.md)记录当前 SHA、迁移、配置、测试和发布影响，持续更新验证矩阵。
- 门禁：正常、空值、非法值、依赖失败、竞态和缓存陈旧场景有行为断言；日志不记录完整偏好载荷。

## 阶段 5：集成验证

- 对最新 SHA 执行 CI、独立评审、API 契约、迁移/回滚、缓存和完整用户旅程验证。
- 注入：基础 CI 通过，但端到端测试发现用户清除默认筛选后旧缓存仍恢复筛选。期望结论是阻塞合入，修复后重跑当前 SHA，而非将其标为偶发。
- 使用[验证矩阵](../../templates/delivery/verification-matrix.md)和[变更交接](../../templates/delivery/change-handoff.md)记录修复、复审和最终合入结论。

## 阶段 6：发布与变更管理

- 使用[发布记录](../../templates/delivery/release-record.md)固定同一制品，先部署兼容迁移，再以内部用户/小流量开关批次推进。
- 健康阈值包含 API 错误、偏好读取/写入失败、列表延迟、缓存异常和清除成功率；达到阈值关闭开关或按预案恢复。

## 阶段 7：运行与支持

- 观察技术指标、功能使用、清除失败和支持反馈。用户可关闭功能且旧客户端继续正常工作。
- 若出现大范围错误筛选或列表不可用，使用[事件记录](../../templates/delivery/incident-record.md)关联发布批次、缓解和恢复证据。

## 阶段 8：度量与复盘

- 使用[效果复盘与行动](../../templates/delivery/outcome-retrospective-actions.md)比较重复设置次数、任务耗时、采用率和护栏指标，区分相关性与因果性。
- 将缓存测试缺口或迁移经验转为有所有者、期限和效果判据的行动。

## 演练通过条件

- 中风险结论与实际数据、接口和缓存边界一致；范围扩大能触发重新评估。
- 缓存端到端失败确实阻塞合入，修复证据对应最终 SHA。
- 发布批次、开关和兼容迁移可恢复，结果记录能追溯到原始成功指标。
