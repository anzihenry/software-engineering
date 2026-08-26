# 阶段 4：开发与自测

## 目标

以小而可审查的变更实现已批准的设计，并在提交评审前提供可信的自测证据。

## 输入

- 已评审的设计、任务拆分、验收标准、测试策略和发布预案。
- 项目编码规范、依赖策略、开发环境和 CI 检查要求。

## 流程

1. **准备变更**：确认基线分支、环境和依赖版本；将任务与对应需求、设计和风险记录关联。
2. **实现最小切片**：优先编写可独立评审、可回退的变更；遵循既有边界、契约和安全处理方式，不在同一变更中夹带无关重构。按主要影响域进入移动端、Web 前端或后端实现与自测；跨域变更保持共同验收标准和契约可追溯。
3. **处理数据与配置**：对迁移、配置和密钥使用受控机制；迁移应评估向前兼容、回填、恢复和执行时长，密钥不得进入代码或日志。
4. **编写并运行测试**：按测试策略覆盖正常、边界、失败和授权场景；运行格式化、静态分析、类型检查、单元测试及适用的本地集成检查。
5. **更新交付信息**：同步接口契约、运维说明、用户文档和变更说明；记录未自动化验证的项目及原因。
6. **发起评审**：PR 描述须包含变更目的、范围、风险、测试证据、发布影响和回滚注意事项。

## 决策门禁

进入“集成验证”前，本地必需检查通过，变更可追溯至验收标准，测试与风险匹配，文档/迁移/配置已准备。无法通过的检查不得通过删测、跳过或降低门禁来掩盖。

## 输出

- 可构建的代码变更、自动化测试、必要的迁移和配置。
- 完整 PR 及自测证据、已知限制和发布注意事项。
- 使用[变更交接模板](../../templates/delivery/change-handoff.md)汇总当前提交，持续更新[验证矩阵](../../templates/delivery/verification-matrix.md)。

## 异常与回流

- 实现暴露设计缺口：暂停扩大变更，回到方案与计划更新设计。
- 验收标准不清：回到澄清与立项，不以开发者猜测替代业务决策。
- 本地环境或依赖阻塞：记录可复现信息并转交对应所有者，避免提交未经验证的假成功。

## 交接给下一阶段

交接 PR、CI 所需上下文、自测记录、契约/迁移说明及风险提示。集成验证以此检查系统级行为和独立评审质量。

## 固化为 SKILL

| 行为 | SKILL | 适用边界 | 产出 |
| --- | --- | --- | --- |
| 编排领域不明确或跨领域的实现切片与整体自测 | [`implementation-and-self-test`](../../skills/04-implementation-and-self-test/implementation-and-self-test/SKILL.md) | 已有评审通过的设计与任务，需维持整体范围和证据关联时 | 可构建变更、对应测试和整体自测结论 |
| 应用语言编码规范和最佳实践 | [`language-coding-standards`](../../skills/04-implementation-and-self-test/language-coding-standards/SKILL.md) | 编写、修改或评审 TypeScript、ArkTS、Python、Swift、Kotlin、Go、SQL、zsh 或 C++ 代码时 | 与项目配置一致的实现、检查证据和已知偏差 |
| 实现共享移动逻辑或协调多平台交付 | [`mobile-implementation-and-self-test`](../../skills/04-implementation-and-self-test/mobile-implementation-and-self-test/SKILL.md) | 涉及跨平台框架、共享业务逻辑或 iOS/Android/HarmonyOS 一致性时 | 跨平台移动变更、平台影响和整体自测证据 |
| 通过官方移动端 CLI 执行构建、测试和证据采集 | [`mobile-cli-execution`](../../skills/04-implementation-and-self-test/mobile-cli-execution/SKILL.md) | Agent 需要实际调用 Apple/Android/HarmonyOS 工具链、管理目标设备或保存原始产物时 | 可重复命令、目标身份、原始结果与安全收口记录 |
| 实现并自测 iOS/iPadOS 平台行为 | [`ios-implementation-and-self-test`](../../skills/04-implementation-and-self-test/ios-implementation-and-self-test/SKILL.md) | 涉及 Apple 生命周期、并发、系统能力、数据保护或 Xcode target 时 | iOS 平台变更、测试和代表性设备自测证据 |
| 实现并自测 Android 平台行为 | [`android-implementation-and-self-test`](../../skills/04-implementation-and-self-test/android-implementation-and-self-test/SKILL.md) | 涉及 Android 生命周期、协程、后台限制、API 差异或 Gradle 变体时 | Android 平台变更、测试和代表性设备自测证据 |
| 实现并自测 HarmonyOS 平台行为 | [`harmonyos-implementation-and-self-test`](../../skills/04-implementation-and-self-test/harmonyos-implementation-and-self-test/SKILL.md) | 涉及 ArkTS/ArkUI、Ability 生命周期、分布式能力、API 差异或 Hvigor 构建时 | HarmonyOS 平台变更、测试和代表性设备自测证据 |
| 协调完整 Web 前端页面切片 | [`web-frontend-implementation-and-self-test`](../../skills/04-implementation-and-self-test/web-frontend-implementation-and-self-test/SKILL.md) | 变更跨越 UI/交互与路由/状态/数据边界，或需汇总前端证据时 | 完整前端变更、跨边界测试和整体自测结论 |
| 实现并自测 Web UI 与交互 | [`web-ui-implementation-and-self-test`](../../skills/04-implementation-and-self-test/web-ui-implementation-and-self-test/SKILL.md) | 涉及页面/组件、设计系统、表单、焦点、响应式或可访问性时 | UI 变更、组件/交互测试和浏览器自测证据 |
| 实现并自测 Web 状态与数据流 | [`web-state-data-implementation-and-self-test`](../../skills/04-implementation-and-self-test/web-state-data-implementation-and-self-test/SKILL.md) | 涉及路由、状态、数据获取、缓存、认证、竞态或恢复时 | 状态/数据变更、测试和失败语义证据 |
| 协调完整后端服务切片 | [`backend-implementation-and-self-test`](../../skills/04-implementation-and-self-test/backend-implementation-and-self-test/SKILL.md) | 变更跨越 API、领域数据和异步集成边界，或需汇总后端证据时 | 完整后端变更、跨边界测试和整体自测结论 |
| 实现并自测后端 API | [`backend-api-implementation-and-self-test`](../../skills/04-implementation-and-self-test/backend-api-implementation-and-self-test/SKILL.md) | 涉及同步入口、协议 schema、校验、认证授权、错误或版本兼容时 | API 变更、契约测试和调用方影响证据 |
| 实现并自测后端领域与数据 | [`backend-domain-data-implementation-and-self-test`](../../skills/04-implementation-and-self-test/backend-domain-data-implementation-and-self-test/SKILL.md) | 涉及领域规则、事务、数据模型、查询、并发写入或迁移准备时 | 领域/数据变更、不变量和事务证据 |
| 实现并自测后端异步与集成 | [`backend-async-integration-implementation-and-self-test`](../../skills/04-implementation-and-self-test/backend-async-integration-implementation-and-self-test/SKILL.md) | 涉及消息、队列、任务、Webhook、外部依赖、重试或最终一致性时 | 异步/集成变更、重复失败语义和遥测证据 |
| 安全地处理迁移、运行配置和密钥 | [`data-and-configuration-change`](../../skills/04-implementation-and-self-test/data-and-configuration-change/SKILL.md) | 变更涉及数据、配置、权限或密钥时 | 受控变更方案及恢复/验证说明 |
| 执行并记录本地质量门禁 | [`local-quality-validation`](../../skills/04-implementation-and-self-test/local-quality-validation/SKILL.md) | 提交评审前需要验证变更时 | 可追溯的本地检查证据与限制 |
| 补齐文档并准备评审交接材料 | [`change-handoff-preparation`](../../skills/04-implementation-and-self-test/change-handoff-preparation/SKILL.md) | 变更已具备提交评审条件时 | 完整 PR 描述、交接信息和已知限制 |

领域 SKILL 负责其特有的实现风险；移动端共享层协调多平台，iOS/Android/HarmonyOS 层处理平台语义，`mobile-cli-execution` 只提供官方工具链执行和原始证据；Web 前端协调层组合 UI/交互与状态/数据；后端协调层组合 API、领域数据与异步集成。数据/配置、本地门禁和交接仍是共享能力。它们不替代阶段 5 的独立评审、受控 CI 和系统级验证。
