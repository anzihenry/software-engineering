# 阶段 5：集成验证

## 目标

通过独立评审和自动化验证，证明变更能够安全地与目标系统、依赖和发布环境协同工作。

## 输入

- PR、代码变更、自测证据、验收标准、设计和风险等级。
- CI 配置、测试环境、契约、基线性能与安全要求。

## 流程

1. **执行自动门禁**：构建、格式化、静态/类型分析、单元测试、依赖与密钥扫描必须在受控环境执行；失败应定位并修复，而非忽略。
2. **开展代码评审**：评审者检查正确性、边界和错误处理、兼容性、可维护性、数据/权限安全、测试充分性及对运行/发布的影响。
3. **验证系统行为**：按风险进入移动端、Web 前端或后端专项验证，并执行必要的跨领域集成、契约、端到端、性能、并发、恢复或安全测试；验证测试环境与生产差异是否会影响结论。
4. **处理反馈与回归**：作者逐项回应评审意见；每次实质修改重新执行受影响检查，必要时请求重新评审。
5. **确认合入**：确认全部必需检查通过、审批达到项目规则、冲突已解决且目标分支仍适用。

## 决策门禁

进入“发布与变更管理”前，必需 CI 全绿，阻塞性评审意见已解决，高风险验收与非功能要求均有验证证据。豁免必须由有权限的负责人记录原因、范围、到期时间和补救计划。

## 输出

- 已批准并可合入的变更、CI 与测试报告、评审决策和已记录的豁免。
- 经过更新的发布候选物及其可追溯版本。

## 异常与回流

- 验证失败：回到开发与自测修复；若根因是方案错误，回到方案与计划。
- 环境不可信：修复或替换测试环境，不将其结果当作发布依据。
- 发现新的高风险：升级变更等级，并补充设计、安全或运维评审。

## 交接给下一阶段

交接已合入的版本标识、验证证据、豁免记录及发布候选的风险说明。

## 固化为 SKILL

| 行为 | SKILL | 适用边界 | 产出 |
| --- | --- | --- | --- |
| 在受控 CI 中解释和处置自动门禁结果 | [`ci-quality-gate-evaluation`](../../skills/05-integration-validation/ci-quality-gate-evaluation/SKILL.md) | PR 已触发构建、测试和安全检查时 | 门禁结论、失败处置与限制 |
| 以独立视角审查变更及其测试证据 | [`pull-request-review`](../../skills/05-integration-validation/pull-request-review/SKILL.md) | 变更需人工评审时 | 可追溯的评审发现与审批结论 |
| 规划并汇总跨平台移动验证 | [`mobile-validation`](../../skills/05-integration-validation/mobile-validation/SKILL.md) | 风险跨越 iOS/Android，或需验证共享行为、两端一致性与整体设备矩阵时 | 移动端整体结论、两端证据和支持范围 |
| 验证 iOS/iPadOS 平台行为 | [`ios-validation`](../../skills/05-integration-validation/ios-validation/SKILL.md) | 风险涉及 Apple 系统/设备、安装升级、权限、后台、VoiceOver 或端侧性能时 | iOS 专项验证证据与适用范围 |
| 验证 Android 平台行为 | [`android-validation`](../../skills/05-integration-validation/android-validation/SKILL.md) | 风险涉及 API/OEM/设备、进程恢复、后台限制、TalkBack 或端侧性能时 | Android 专项验证证据与适用范围 |
| 规划并汇总 Web 前端验证 | [`web-frontend-validation`](../../skills/05-integration-validation/web-frontend-validation/SKILL.md) | 需要综合功能兼容、视觉可访问性和性能证据时 | Web 前端整体结论、缺陷映射与浏览器范围 |
| 验证 Web 功能和浏览器兼容性 | [`web-functional-compatibility-validation`](../../skills/05-integration-validation/web-functional-compatibility-validation/SKILL.md) | 风险涉及端到端路径、真实数据、导航、认证、存储或浏览器运行时差异时 | 功能/兼容专项证据与支持范围 |
| 验证 Web 视觉和可访问性 | [`web-visual-accessibility-validation`](../../skills/05-integration-validation/web-visual-accessibility-validation/SKILL.md) | 风险涉及视觉回归、响应式、键盘、屏幕阅读器、缩放或内容适配时 | 视觉/可访问性专项证据与已审查差异 |
| 验证 Web 加载和运行时性能 | [`web-performance-validation`](../../skills/05-integration-validation/web-performance-validation/SKILL.md) | 风险涉及关键页面、交互、资源、缓存、第三方或性能预算时 | 性能指标、回归归因和适用限制 |
| 规划并汇总后端验证 | [`backend-validation`](../../skills/05-integration-validation/backend-validation/SKILL.md) | 需要综合契约、数据、性能、韧性或安全证据时 | 后端整体结论、专项映射与生产适用限制 |
| 验证后端契约和真实集成 | [`backend-contract-integration-validation`](../../skills/05-integration-validation/backend-contract-integration-validation/SKILL.md) | 风险涉及 API/事件版本、调用方、序列化、协议或外部依赖兼容时 | 契约/集成专项证据与版本范围 |
| 验证后端数据一致性 | [`backend-data-consistency-validation`](../../skills/05-integration-validation/backend-data-consistency-validation/SKILL.md) | 风险涉及事务、并发写入、迁移、回填、回滚或最终一致性时 | 数据完整性、兼容和恢复证据 |
| 验证后端性能和并发 | [`backend-performance-concurrency-validation`](../../skills/05-integration-validation/backend-performance-concurrency-validation/SKILL.md) | 风险涉及吞吐、延迟、资源、争用、容量、背压或性能预算时 | 负载指标、并发正确性和容量限制 |
| 验证后端韧性和恢复 | [`backend-resilience-recovery-validation`](../../skills/05-integration-validation/backend-resilience-recovery-validation/SKILL.md) | 风险涉及超时、依赖故障、重启、降级、重放或恢复目标时 | 故障注入、降级恢复和可观测性证据 |
| 验证后端安全和授权 | [`backend-security-authorization-validation`](../../skills/05-integration-validation/backend-security-authorization-validation/SKILL.md) | 风险涉及认证授权、资源/租户隔离、敏感数据、输入或滥用控制时 | 安全负向证据、缺口和专项评审需求 |
| 验证并汇总跨领域、跨环境系统行为 | [`system-level-validation`](../../skills/05-integration-validation/system-level-validation/SKILL.md) | 风险跨越客户端、服务和外部依赖，或需完整用户旅程证据时 | 跨域系统验证证据与适用范围 |
| 汇总反馈、豁免与最新状态以判断可合入性 | [`merge-readiness`](../../skills/05-integration-validation/merge-readiness/SKILL.md) | 准备合入目标分支时 | 可合入/阻塞结论及剩余事项 |

领域专项验证提供各自风险证据；`mobile-validation` 汇总 iOS/Android，`web-frontend-validation` 汇总前端三类专项，`backend-validation` 汇总后端五类专项，`system-level-validation` 再保持客户端、服务和外部依赖的跨域汇总责任。所有这些 SKILL 只形成验证与合入结论；生产发布控制由阶段 6 负责。
