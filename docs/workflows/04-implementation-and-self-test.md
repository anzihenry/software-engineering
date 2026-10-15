---
owner: implementation-lead
scope: "Lifecycle phase 4: implementation and self-test"
status: active
review_by: "2027-02-26"
---

# 阶段 4：开发与自测

## 完成定义与边界

在已批准范围内完成可审查的实现，本阶段必需自测实际通过，形成与当前版本绑定的可信证据和完整交接材料，具备进入阶段 05 独立集成验证的条件。作者自测不代替独立验证，也不产生合入或发布批准。

区分继续修复/准备、Draft 协作和正式交接：实现未完成或必需自测未通过时，可以在任务分支继续工作、准备材料、开 Draft PR 讨论及运行诊断 CI；不得据此宣称阶段完成、待评审或正式验证中。既定阶段05/CI/真机检查可留后续，须明确负责人、节点、判据、证据与失败停止动作；本阶段必需项不能事后改挂后续以制造完成。

## 输入与启动

按[阶段 03 交接](03-solution-and-planning.md#输出与阶段-04-交接)读取当前需求/方案/计划、批准范围与非目标、验收/风险、证据/剩余未知、任务前置、验证/后续控制/文档任务及实际开发批准的权限/限制/时间/来源。方案评审通过不自动产生开发授权；已有有效覆盖授权可引用，无须重复仪式。

核对版本有效、当前任务授权/前置、依赖/环境/权限、阻塞已解和实际项目规范/配置/命令。后续资源不必全部提前交付；mock 只能证明契约限定范围，不能证明真实集成。需要编码确认方案可落地时回[阶段 03 技术预研](03-solution-and-planning.md#未知项与技术预研)，按其独立 worktree 生命周期保全证据后清理；普通正式实现按任务分支，不一律强制 worktree。

## 实施顺序与职责

修改代码、文档或配置前使用 [Git 任务分支管理](../../skills/04-implementation-and-self-test/git-branch-management/SKILL.md)，按[分支规范](../git-branch-workflow.md)检查归属/其他 worktree、fetch、创建或复用任务分支，保护无关工作；默认/受保护分支不承载任务修改或新提交，误提交先安全恢复。

确认批准基线和验收/风险映射，选择可审查、可验证、可恢复的完整切片。源码先用[语言编码规范](../../skills/04-implementation-and-self-test/language-coding-standards/SKILL.md)和匹配参考确认实际配置，依下列标准实现、自测，再使用交接准备。按触发组合领域技能，不能每个任务强制所有技能或新增一套文件。实现编排维持整体切片；本地质量验证执行实际检查；数据/配置技能处理有状态及敏感边界；交接准备判断材料和本阶段资格，均不能越权做独立/合入决定。

## 实现完成的七项标准

1. **范围有效**：实现对应当前批准需求、方案和任务；不夹带未批准能力、依赖/工具链升级或无关重构。
2. **行为完整**：正常路径及适用边界、失败、权限、取消、恢复符合验收；关键行为不能用占位、临时返回或 TODO 代替。后续优化 TODO 可有明确边界，不能缺少必需语义。
3. **切片接通**：相关组件/调用方/数据或异步边界组合可用；模块孤立通过、接口骨架或 UI 主操作未连接不证明用户能力完成。
4. **约束落实**：契约、兼容、授权、数据不变量、迁移和配置符合设计；关键变化按回流处理，不能在编码中重新定义验收。
5. **工程可用**：遵循实际项目编码/工具规范，对适用目标构建、运行和检查；资源、并发、取消、超时、日志与敏感信息符合约定。
6. **配套到位**：本节点适用测试、配置/迁移、观测、恢复、文档及译文实际完成；后续事项有明确节点，不能代替本节点缺项。
7. **可审查追溯**：diff、提交、描述一致，关联需求/决定/验证，准确说明限制及未覆盖范围。

完成以批准范围为单位。经批准的客户端加契约约束 mock 可完成客户端范围，不冒充真实服务集成或完整产品；仅模块骨架不能宣称完整能力。迁移脚本和测试环境验证不是生产执行授权。

## 自测充分的七项标准

1. **覆盖依据完整**：由验收、实际变化和风险生成适用检查集合，保留项目已定义必过集合，不只挑易通过项。
2. **检出错误行为**：断言可观察行为与关键不变量，能区分正确与错误；代码被执行、调用次数或绿测数量不能代替行为证据。
3. **场景按风险**：覆盖正常和适用边界/失败/权限/并发/取消/兼容/迁移/恢复；不要求每任务触发所有类别。文案等轻量变更不凑无意义单测，但项目必过检查仍执行。
4. **修复有回归**：可行时先复现再用同一行为判据验证修复；无法复现记录原因、替代证据及限制。只有独立确认需求/契约改变或测试缺陷，才有依据修订旧断言，不能让测试迎合错误实现。
5. **条件如实**：明确实际版本/配置/目标/环境/依赖/数据及支持范围；替身、模拟器、小样本只支持所测条件，不能外推真实依赖/全平台/生产。
6. **必需项实际通过**：本阶段必需检查均实际通过，失败/未执行/阻塞不能改写成通过。既定后续验证单独列出，不提前填绿。
7. **证据仍有效**：当前提交或文件摘要绑定实际命令、范围、时间、退出码和原始结果；修改影响后重验，无法确认对象的报告不能作当前通过依据。

## 失败处置与回流

结果沿用[质量门禁](../quality-gates.md)的 `passed/failed/not-run/blocked/stale/not-applicable`；不适用需规则和事实，缺工具/权限/证据不能记不适用。原规则允许的非强制限制按其例外机制处理，不得豁免必过检查、文档/译文/证据/独立性或高风险人类决定。

| 情况 | 处置与推进边界 |
| --- | --- |
| 实现/测试真实缺陷 | 按依据修复并回归，本阶段必需项未满足不能完成 |
| 关键设计/可行性缺口 | 回03，仅停受影响实现；需编码预研用独立 worktree |
| 业务/验收歧义 | 回02，不能由开发者猜测 |
| 环境/工具/依赖缺失 | 保留可复现阻塞、负责人、解阻和复验；仅在项目规则允许且真实覆盖条件并通过时使用等效环境 |
| 既有基线失败 | 保存基线与当前证据及影响，不自动豁免、也不擅自扩大重构；可 Draft 协作，本阶段必需失败仍阻止完成 |
| 间歇失败/重试变绿 | 保留首次及全部重试和条件，按项目规则调查，不挑绿、不以重试覆盖失败 |
| 已规划后续节点检查 | 保留负责人/节点/判据/证据/失败动作；该节点前不能宣称通过，不反向延期本阶段必需项 |

缺口按实际影响范围隔离，未受影响且已授权工作可继续，不必一项失败冻结所有工作。新增权限、资金、敏感数据等风险回对应所有者和既有专业评审，Agent 不接受风险。

## 当前证据与重验

证据至少包含：仓库/提交或未提交路径与 SHA-256、适用制品身份；验收/风险/检查范围；影响结果的版本、配置、依赖、环境、数据与参数；实际命令或人工步骤、执行者、带时区时间、退出码或人工观察；原始报告及摘要、局限/未覆盖/后续项。无需倾倒整机信息；UI 手工证据同样绑定版本与步骤。

| 后续变化 | 重验判断 |
| --- | --- |
| 行为代码 | 受影响验收、边界/失败/回归及项目必过集合 |
| 测试/断言/数据 | 重跑并确认仍能检出关键错误 |
| 接口/授权/数据/依赖或锁文件 | 受影响消费者、兼容/不变量及适用专项 |
| 构建/工具/环境 | 受影响目标和声明支持范围 |
| 仅文档 | 核对是否改变行为、操作或配置含义，执行文档及项目必过检查 |
| 同内容提交整理 | 证明摘要映射，项目允许时复用有效结果；要求最新 head CI 仍实际执行 |
| 同步/rebase/基线/冲突 | 判断实际集成候选并重验受影响范围，旧基线通过不代表新候选 |

难以界定影响时扩大验证；项目全量重跑要求仍适用。同一快照已通过且无新影响/失败/未决风险时不机械反复扩测。检查中候选变化需指明实际所测内容，无法识别时标 stale 并重跑；保留旧报告而不覆盖历史。

## 决策门禁

正式交阶段05前，上述实现、自测标准与当前证据成立，本节点文档/译文/迁移/配置及交接材料到位。准备独立文档评审不等于作者自批；后续合入前按文档规范实际通过。Draft 协作与诊断 CI 不绕过正式门槛。

## 文档治理

每次变更使用文档维护技能展开文件级影响清单，同步中文与英文、当前知识、导航和引用。按统一交付检查模板记录实际检查和当前版本，交给非作者独立验证，不能用自测或填写模板代替独立评审。

遵循[项目文档规范](../documentation-standard.md)和[接入说明](../documentation-integration.md)。[文档维护](../../skills/04-implementation-and-self-test/documentation-maintenance/SKILL.md)负责准备与更新，[独立文档验证](../../skills/05-integration-validation/documentation-delivery-validation/SKILL.md)负责检查结论，使用[统一交付检查模板](../../templates/documentation/delivery-check.md)。缺少专用检查器时保留逐项实际核对证据，不能声称第三阶段自动门禁已启用。

## 输出与阶段 05 交接

复用[变更交接模板](../../templates/delivery/change-handoff.md)和[验证矩阵](../../templates/delivery/verification-matrix.md)，一个主记录可位于既有 Issue/PR；需求/方案/任务/验证各维护自身事实，通过稳定 ID 和附件关联，不复制一套状态。正式交接七项：

1. 当前批准范围、需求/方案基线、非目标与实际开发授权。
2. 实际 base/head 或未提交路径/摘要、变化行为与设计对应。
3. 验收/风险到实际变更、接口/权限/数据/运行边界映射。
4. 完整本阶段自测集合、命令/环境/结果/原始证据。
5. 限制和既定后续验证的负责人、节点、判据、证据及停止动作。
6. 文档及译文、契约、配置/迁移、观测/恢复的实际完成和后续安排。
7. 实际交接决定、接收方、未决动作及下一份证据；不伪填接收或批准。

05 接收时核对对象、证据有效性与前置，缺口退回受影响范围。接收不等于独立验证通过。

## 变更交接七状态

| 状态 | 事实含义 |
| --- | --- |
| 实现中 | 实现或本阶段必需自测尚未完成，可已有 Draft PR |
| 待评审 | 本阶段完成、正式材料可交接；不代表独立评审或 CI 已通过 |
| 验证中 | 05 已正式接收且正在执行独立/CI/专项验证，诊断 CI 不自动触发 |
| 可合入 | 05 确认当前候选满足全部合入条件，作者自测不能自行标记 |
| 阻塞 | 推进有必需缺口，记录受影响范围、负责人、补救与复验条件 |
| 已合入 | 有实际 PR、源码/合入 SHA、时间与证据，不等于已发布 |
| 已关闭 | 实际交付或停止交接已收口，保留理由、决定、结果和下游；不证明成功 |

状态转换记录原/新状态、原因、候选版本、实际主体/权限、带时区时间及证据。新增变更使受影响就绪结论失效，按事实返回实现或验证；可合入不沿用旧候选结论。关闭、阻塞恢复或重新开启均保留历史，不补造批准。

## 固化为 SKILL

| 行为 | SKILL | 适用边界 | 产出 |
| --- | --- | --- | --- |
| 准备/复用任务分支、安全同步或恢复误提交、合入后清理 | [`git-branch-management`](../../skills/04-implementation-and-self-test/git-branch-management/SKILL.md) | Git 项目修改前或执行分支操作时 | 任务分支、同步/恢复映射与安全清理证据 |
| 采用文档规范、分析影响并同步双语内容 | [`documentation-maintenance`](../../skills/04-implementation-and-self-test/documentation-maintenance/SKILL.md) | 文档采用、迁移或变更交付准备 | 固定知识/入口覆盖与实际命令的采用记录、双语更新、影响清单、当前快照和待独立验证记录 |
| 编排领域不明确或跨领域的实现切片与整体自测 | [`implementation-and-self-test`](../../skills/04-implementation-and-self-test/implementation-and-self-test/SKILL.md) | 已有实际开发批准，需维持整体切片、风险验证和回流时 | 可构建变更、对应测试和整体自测结论 |
| 确认实际配置、应用语言规范并选择风险验证 | [`language-coding-standards`](../../skills/04-implementation-and-self-test/language-coding-standards/SKILL.md) | 源码实现、重构或评审；按实际语言和跨语言边界加载参考 | 实现交接的验证映射/当前报告，或评审的具体风险/证据缺口；不批准合入 |
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
| 补齐文档并准备评审交接材料 | [`change-handoff-preparation`](../../skills/04-implementation-and-self-test/change-handoff-preparation/SKILL.md) | 准备Draft材料或核对正式交阶段05资格时 | 单一交接记录、真实状态与正式移交资格 |

领域 SKILL 负责其特有的实现风险；移动端共享层协调多平台，iOS/Android/HarmonyOS 层处理平台语义，`mobile-cli-execution` 只提供官方工具链执行和原始证据；Web 前端协调层组合 UI/交互与状态/数据；后端协调层组合 API、领域数据与异步集成。数据/配置、本地门禁和交接仍是共享能力。它们不替代阶段 5 的独立评审、受控 CI 和系统级验证。

项目首次采用或入口/知识 pin/命令变化时，文档维护按[采用规范](../harness-adoption.md)诊断，保留实际 Agent 任务轨迹；可访问不等于已加载，远端能力等待真实平台验收。

后端/Web 风险选择、场景与证据交接遵循[领域执行契约](../domain-validation.md)：阶段 3 固定触发/支持/预算，阶段 4 保存真实执行，阶段 5 按完整专项和非作者内容评审汇总；机器一致性不替代批准。
