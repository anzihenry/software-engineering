# 阶段 5：集成验证

## 目标

通过独立评审和自动化验证，证明变更能够安全地与目标系统、依赖和发布环境协同工作。

## 输入

- PR、代码变更、自测证据、验收标准、设计和风险等级。
- CI 配置、测试环境、契约、基线性能与安全要求。
- GitHub 仓库规则、Actions 可用能力、团队规模和执行成本约束。

## 流程

1. **创建 Draft PR**：从已完成自测的主题分支创建 PR，关联需求与设计，记录范围、风险、测试、迁移、发布和恢复信息；验证未完成前保持 Draft。
2. **执行 CI 自动门禁**：GitHub Actions 在每个 PR 上执行构建、格式化、静态/类型分析、单元测试及适用的依赖与密钥检查；用固定名称的汇总检查作为 required check，失败应定位并修复，而非忽略。
3. **开展独立代码评审**：微型团队由未参与实现的维护者评审；独立开发者使用全新上下文的 Agent 评审形成独立证据，但不将其冒充人工批准。评审覆盖正确性、边界、兼容、安全、测试和运行影响。
4. **执行领域专项验证**：按风险进入移动端、Web 前端或后端专项验证；通过路径、标签或手动触发控制昂贵检查，但合入所需证据必须关联当前提交。
5. **执行跨系统验证**：当风险跨越客户端、服务、数据库或外部依赖时，执行必要的契约、端到端、性能、并发、恢复或安全测试，并说明测试环境与生产差异。
6. **处理反馈与回归**：作者在原分支逐项回应评审意见；每次实质修改重新执行受影响检查，并复审受影响代码，不沿用旧提交结果。
7. **判断合入就绪**：确认 PR 已退出 Draft、最新提交的必需检查全绿、阻塞意见解决、专项/系统证据齐全、无冲突且目标分支仍适用。
8. **通过项目机制合并**：由受保护分支规则执行合入，默认使用 squash merge 并删除主题分支；仅在并发合入频繁且 GitHub 套餐支持时使用 merge queue。合并不等于批准发布。

## 独立开发者与微型团队的 GitHub 基线

| 方面 | 独立开发者 | 微型团队 |
| --- | --- | --- |
| PR 审批 | Required approvals 设为 0，避免无法自批；保留全新上下文 Agent 评审和人类 Go/No-Go | 有第二位维护者时，中高风险要求 1 人批准；可要求最新推送由他人确认 |
| 分支保护 | `main` 必须经 PR、required checks 和对话解决，禁止强推/删除 | 同左，可增加 CODEOWNERS 或按目录请求评审 |
| CI 层级 | 每次提交跑快速层；按风险触发专项/系统/设备层 | 同左，可按责任领域并行验证 |
| 合并方式 | 人工确认或 auto-merge，默认 squash | 默认 squash；并发 PR 明显增加后再考虑 merge queue |
| 高风险变更 | 明确记录人类 Go/No-Go；不能由 Agent 自动批准风险例外 | 由非作者维护者或外部专家确认专项风险 |

Actions 应始终启动主 CI workflow，再在 job 内按变更路径决定是否执行领域任务；不要让整个 required workflow 因路径过滤不触发。对同一 PR 的旧运行启用并发取消，所有合入证据以最新 head SHA 为准。Actions 默认使用只读最小权限，不让不可信 PR 通过高权限事件取得密钥。

## 决策门禁

进入“发布与变更管理”前，必需 CI 全绿，阻塞性评审意见已解决，高风险验收与非功能要求均有验证证据。豁免必须由有权限的负责人记录原因、范围、到期时间和补救计划。

## 输出

- 已批准并可合入的变更、CI 与测试报告、评审决策和已记录的豁免。
- 经过更新的发布候选物及其可追溯版本。
- 在[变更交接模板](../../templates/delivery/change-handoff.md)记录最新 head SHA 的合入结论，并以[验证矩阵](../../templates/delivery/verification-matrix.md)关联门禁和专项证据。

## 异常与回流

- 验证失败：回到开发与自测修复；若根因是方案错误，回到方案与计划。
- 环境不可信：修复或替换测试环境，不将其结果当作发布依据。
- 发现新的高风险：升级变更等级，并补充设计、安全或运维评审。

## 交接给下一阶段

交接已合入的版本标识、验证证据、豁免记录及发布候选的风险说明。

## 固化为 SKILL

| 行为 | SKILL | 适用边界 | 产出 |
| --- | --- | --- | --- |
| 为新 GitHub 仓库建立稳定 CI 与适配真实能力的 CD 基线 | [`github-actions-bootstrap`](../../skills/05-integration-validation/github-actions-bootstrap/SKILL.md) | 项目已有可本地执行的质量命令，需要生成安全 Actions workflow 并通过首次 PR 自动取得真实 check-run 时 | CI/CD workflow、首次 PR 运行证据及仓库设置交接 |
| 为新 GitHub 仓库建立安全仓库设置并收口首次 CI PR | [`github-repository-bootstrap`](../../skills/05-integration-validation/github-repository-bootstrap/SKILL.md) | Actions 引导 PR 已自动产生成功稳定 check，或需要审计 Actions 权限、environments、ruleset 和删分支设置时 | 可验证的仓库治理设置、首次 PR 收口与分支清理证据 |
| 编排 GitHub PR 从 Draft 到受保护合入 | [`github-pr-integration`](../../skills/05-integration-validation/github-pr-integration/SKILL.md) | 独立开发者或微型团队需要在 GitHub 上串联 CI、评审、专项/系统验证和合入判断时 | 对应最新提交的 PR 集成状态与下一动作 |
| 在受控 CI 中解释和处置自动门禁结果 | [`ci-quality-gate-evaluation`](../../skills/05-integration-validation/ci-quality-gate-evaluation/SKILL.md) | PR 已触发构建、测试和安全检查时 | 门禁结论、失败处置与限制 |
| 以独立视角审查变更及其测试证据 | [`pull-request-review`](../../skills/05-integration-validation/pull-request-review/SKILL.md) | 变更需人工评审时 | 可追溯的评审发现与审批结论 |
| 规划并汇总跨平台移动验证 | [`mobile-validation`](../../skills/05-integration-validation/mobile-validation/SKILL.md) | 风险跨越 iOS/Android/HarmonyOS，或需验证共享行为、平台一致性与整体设备矩阵时 | 移动端整体结论、各平台证据和支持范围 |
| 执行移动端 CLI 并采集原始验证证据 | [`mobile-cli-execution`](../../skills/04-implementation-and-self-test/mobile-cli-execution/SKILL.md) | iOS/Android/HarmonyOS 验证需要实际运行官方工具链、锁定设备或保存测试/日志/性能产物时 | 与提交、构建和目标设备关联的原始执行记录 |
| 验证 iOS/iPadOS 平台行为 | [`ios-validation`](../../skills/05-integration-validation/ios-validation/SKILL.md) | 风险涉及 Apple 系统/设备、安装升级、权限、后台、VoiceOver 或端侧性能时 | iOS 专项验证证据与适用范围 |
| 验证 Android 平台行为 | [`android-validation`](../../skills/05-integration-validation/android-validation/SKILL.md) | 风险涉及 API/OEM/设备、进程恢复、后台限制、TalkBack 或端侧性能时 | Android 专项验证证据与适用范围 |
| 验证 HarmonyOS 平台行为 | [`harmonyos-validation`](../../skills/05-integration-validation/harmonyos-validation/SKILL.md) | 风险涉及 API/设备形态、Ability 生命周期、安装升级、分布式能力、辅助功能或端侧性能时 | HarmonyOS 专项验证证据与适用范围 |
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

`github-actions-bootstrap` 负责首次 Actions 接入并产生可信 check-run 交接，`github-repository-bootstrap` 消费该证据完成仓库治理或后续审计，`github-pr-integration` 是面向 GitHub 小团队的日常 PR 编排入口；领域专项验证提供各自风险证据，`mobile-cli-execution` 负责执行官方工具并保存原始产物但不做通过判断，`mobile-validation` 汇总 iOS/Android/HarmonyOS，`web-frontend-validation` 汇总前端三类专项，`backend-validation` 汇总后端五类专项，`system-level-validation` 再保持客户端、服务和外部依赖的跨域汇总责任。所有这些 SKILL 只形成验证与合入结论；生产发布控制由阶段 6 负责。
