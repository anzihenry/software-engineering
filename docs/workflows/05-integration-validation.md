---
owner: quality-lead
scope: "Lifecycle phase 5: integration validation"
status: active
review_by: "2027-02-26"
---

# 阶段 5：集成验证

## 完成定义与阶段边界

对明确的集成候选完成独立评审及全部适用验证，取得有当前证据支持的合入决定，经授权通过项目机制合入main；实际合入版本的必需端到端验证通过，并形成可追溯的阶段06交接。

正式接收、可合入、实际合入、本阶段完成分别判断。接收不是通过，可合入不产生合并授权，已合入不等于验证完成或发布。验证完成但尚无合并授权可停可合入，保留有效结果，不无故重跑或伪记已合入。沿用[七状态](04-implementation-and-self-test.md#变更交接七状态)；已合入只记录Git事实，合入后执行结果/阶段完成结论另记，不新建第二套变更状态。阶段06仍固定候选、核对环境及生产权限，main通过不自动产生候选verified或生产Go。

## 正式接收与输入

按[阶段04正式交接](04-implementation-and-self-test.md#输出与阶段-05-交接)核对当前批准范围、需求/方案/验收与风险、实际head/base、自测完整集合及原始证据、本节点前置和文档材料。缺04必需项退回受影响范围，不用本阶段代替未完成自测；已经规划本阶段的真实依赖、真机、专项/系统验证由本阶段承接。Draft可提前讨论/诊断，验证未完成保持Draft，正式接收并实际开展验证才记验证中。

读取项目CI/工具/支持矩阵、契约、环境/依赖/测试数据、性能安全基线、仓库治理、团队权限和执行成本；实际所测源码/构建须可识别。不要求所有无关后续资源提前就绪，不把mock或未运行环境当当前能力。

## 最低完成七项标准

1. **交接合格**：04范围、实现/自测、配套文档及当前证据符合交接门槛，本阶段任务清楚。
2. **集合完整**：从验收、实际变化、依赖和风险确定CI、独立评审、领域专项与端到端完整集合，不只挑出现的绿项。
3. **必需CI实际通过**：对当前候选执行项目要求；失败、取消、超时、未触发、错误跳过不当通过。
4. **独立评审通过**：非作者检查实现/测试/运行影响，阻塞问题解决且修复经过必要复审，文档独立验证实际通过。
5. **专项及合入前端到端通过**：适用专项和完整路径/关键失败风险有实际证据，替代边界及局限准确。
6. **受控合入完成**：当前候选满足规则、有实际授权，经项目机制合入main，记录PR/精确head、base及合入SHA/时间。
7. **合入后端到端通过并交接**：每次功能实际main合入版本的必需端到端回归通过，问题已处置，06材料完整。

前五项及合入规则满足可判断可合入；后两项完成才成功交付本阶段。必需文档/译文/证据/独立性/既有必过CI/高风险人类决定仍按[质量门禁](../quality-gates.md)不可豁免，专项conditional不允许合入或阶段成功收口。

## 执行顺序与职责

在任务分支核对/复用PR和当前对象，确认完整集合及正式接收；安排CI、独立评审、领域专项和端到端，独立项可并行但先满足真实依赖。反馈回原任务分支修复，按影响重验/复审，再由merge-readiness汇总当前候选；没有缺口且有实际授权后交项目机制合并。合入后记录真实main对象，执行必需端到端、处置失败并交06。

分支准备/同步/误提交恢复/清理沿[Git规范](../git-branch-workflow.md)，不得在默认分支写任务修改；合并默认squash，只有项目适用且平台支持才使用merge queue。合入后先保全复验材料、核对远端删除及其他worktree/待保留工作再安全清理，不因清理丢失失败证据。技能编排不自动获得合并/发布/设置变更权限。

## 每次功能合入的端到端底线

每次功能合入前和合入main后都实际执行；合入前结果不能代替合入后执行。端到端从真实业务入口到最终可观察结果和关键数据状态；适用的界面、服务、数据库、消息链路组合验证，后端/CLI不硬造UI。组件/API单测和全mock不能代替。异步等待明确业务完成条件及合理超时，不凭固定sleep认定成功。

| 集合 | 内容与执行 |
| --- | --- |
| 核心集合 | 项目维护的关键用户能力及高影响失败路径，每次功能合入前后均跑，规模可负担且判据完整 |
| 本次变更集合 | 本次验收、缺陷回归、受影响已有行为/权限/失败恢复，合入前后均跑 |
| 风险专项 | 权限、迁移、兼容、并发、恢复、性能等按真实触发及既定节点执行，合入前必需项不延期 |

集合重叠可去重执行并关联多个判据；不减少必需覆盖。03规划、04补实施影响、05独立查漏；每用例有稳定ID、验收/风险、前置数据/环境/依赖版本、可观察判据、维护人、失败入口及节点。增删依据来自需求/契约/影响和等效覆盖，不因失败、运行慢或难搭环境删项。

内部适用边界使用真实链路；外部依赖优先获授权测试环境，替身写明契约/替代范围及未验证结论。替身覆盖关键变更风险时不能据此宣称该风险已通过。缺必需环境记blocked/not-run，不能not-applicable；获允许且实际覆盖同判据的替代验证才可使用。不稳定必需用例被隔离且无有效替代仍阻塞。

可按影响选用例、独立并行隔离账号/数据、复用环境准备/构建并确认版本初态、把细节放低层测试，保留端到端完整路径和关键风险。结束清理自己创建的数据/资源，保全必要证据，不误删共享数据；耗时/排队/失败原因用于改善执行，超时或无限重试不制造通过。

## 独立评审最低要求

非作者人类或全新上下文Agent自行读需求/设计、实际diff、相关调用路径/测试及原始证据，深度按风险，不能只复述作者摘要或凭CI绿批准。六方面：范围/验收、实现路径/失败/并发/资源、契约/授权/不变量、测试及端到端检错充分性、运行/迁移/恢复、文档/译文/当前证据。记录对象版本、已审/未覆盖范围、证据和复审条件。Agent不冒充GitHub人工批准或专业风险决定；评审者直接参与修复后换非作者复核其修改范围。

| 反馈 | 闭环要求 |
| --- | --- |
| 阻塞 | 合入前修复并复审，或有依据证明不成立 |
| 待澄清 | 影响正确性/验收/风险/合入判断的先澄清，不悬而放行 |
| 非阻塞改进 | 明确本次处理或后续任务、理由及责任 |
| 可选建议 | 可不采纳，个人偏好不变强制门槛 |

每项给触发、可观察后果、依据和所需动作；关闭线程不是解决证据。分歧依需求/契约/规则交相应负责人，不通过多数意见覆盖必需失败。汇总者不能替专项所有者改写原结果，同人多角色不省独立性和授权。

## 候选、证据与连续合入

一个主交接记录链接[验证矩阵](../../templates/delivery/verification-matrix.md)的完整集合：适用依据、验收/风险/用例、head/base及实际所测集成源码/构建摘要、环境/数据/依赖、命令/步骤、执行者/起止时区时间/退出码、原始结果/报告、限制/责任/下一动作。来源核对按[证据契约](../evidence-trust.md)，不能只信PR自填passed。

代码、依赖、断言/数据、环境、目标基线、rebase、冲突或合入内容变化后按影响重验/复审，难界定则扩大；检查中对象变化须识别实际所测内容，否则stale。有效且未受影响的04自测/专项/评审可按项目规则引用，不能代替最新head必需CI、独立判断或每次功能合入前后端到端。合入后绑定实际main SHA/对应构建，不以旧版本通过补新版本。

连续A/B各自关联实际合入SHA、用例、结果、责任；B更晚绿不能自动覆盖A。共用执行记录必须明确实际测试版本、包含合入、逐项完整用例/判据与适用依据；仅“包含代码”不证明行为覆盖，也不免除任何一次合入的必需执行。PR诊断旧任务可取消；合入后必需端到端取消/超时记录缺口并补跑指定对象，保持阶段未完成。不得用分支最新链接混淆精确版本。

## 失败分流与合入后处置

单项用passed/failed/not-run/blocked/stale/not-applicable；取消、超时、跳过、未触发保留原始平台结论及原因，按事实归未执行/失败/阻塞，不伪装通过；NA必须规则和事实。保留首次及全部重试、基线与当前报告，不挑绿、不过度未授权重构、不删测降门禁。

| 原因 | 回流与责任 |
| --- | --- |
| 实现缺陷 | 回04修复/回归/必要复审 |
| 测试缺陷 | 按已确认需求/契约/环境依据修正，仍能检出关键错误 |
| 环境/基础设施 | 对应所有者解阻后重跑准确候选，不以部分绿放行 |
| 关键方案/兼容性 | 回03重评方案和受影响计划 |
| 业务/验收歧义 | 回02，不让测试人员临时定义正确行为 |
| 新高风险及安全/隐私/数据风险 | 升级变更等级并补设计、安全、隐私/合规或运维等适用专业评审；疑似已发生事件立即按事件流程 |
| 间歇/既有失败 | 保留全部原结果和归因，按规则调查，必需失败不豁免 |

合入前失败阻止受影响候选；拆分先证明独立实现/验收/风险及批准范围，不靠开关藏关键缺口。合入后失败保留已合入事实、阶段未完成、失败版本暂停进入发布：保全→定位影响→按授权修复或回退→对处置版本执行端到端→核对数据/副作用实际恢复→记录结果。代码回退不等于数据恢复。

局部隔离明确时无关已授权工作可继续；公共认证/数据/基础能力受影响时暂停依赖其能力的合入，影响未知先扩大停止范围再定位。不能继续叠加变更掩盖首次失败。

修复后完整要求通过才交付原功能；回退恢复基线仅故障处置收口，记录原功能未交付、后续修复任务或实际停止决定，不补记原功能成功。紧急处置仍沿既有授权/最低测试/事后补验，不由紧迫性获得生产或旁路权限。

## 决策门禁

可合入前PR必须已退出Draft，由集成负责人核对当前完整集合、独立评审/文档及专业决定、无阻塞意见/冲突、有效仓库治理及合并条件，再交有权主体执行。阶段完成由负责人核对实际合入、对应main端到端通过、问题闭环及06交接；已合入本身不满足完成。任何必需缺口保持原结果并给最小解阻动作，不取多数绿项、不用一般例外豁免硬门禁。

## 首次采用与仓库治理检查

进入 GitHub 集成验证时，先核对[默认仓库治理](../github-repository-defaults.md)：保护默认分支（新项目为 `main`）并启用合并后自动删分支。首次采用或漂移必须路由到 `github-repository-bootstrap`；没有真实稳定 check 时先执行 `github-actions-bootstrap`。配置并重新读取验证前，不报告治理完成或受保护合入就绪。

## 独立开发者与微型团队的 GitHub 基线

| 方面 | 独立开发者 | 微型团队 |
| --- | --- | --- |
| PR 审批 | Required approvals 设为 0，避免无法自批；保留全新上下文 Agent 评审和人类 Go/No-Go | 有第二位维护者时，中高风险要求 1 人批准；可要求最新推送由他人确认 |
| 分支保护 | `main` 必须经 PR、required checks 和对话解决，禁止强推/删除 | 同左，可增加 CODEOWNERS 或按目录请求评审 |
| CI 层级 | 每次提交跑快速层；按风险触发专项/系统/设备层 | 同左，可按责任领域并行验证 |
| 合并方式 | 人工确认或 auto-merge，默认 squash | 默认 squash；并发 PR 明显增加后再考虑 merge queue |
| 高风险变更 | 明确记录人类 Go/No-Go；不能由 Agent 自动批准风险例外 | 由非作者维护者或外部专家确认专项风险 |

Actions 应始终启动主 CI workflow，再在 job 内按变更路径决定是否执行领域任务；不要让整个 required workflow 因路径过滤不触发。可取消被新提交取代的PR诊断运行，但不得静默取消每次功能合入后的必需端到端；取消要保留对象/原因并补跑，不能被更新的main绿测自动覆盖。合入前证据以当前head/base及实际集成内容为准，合入后绑定实际main合入SHA。Actions 默认使用只读最小权限，不让不可信 PR 通过高权限事件取得密钥。

需要把 PR 记录完整性固化为只读门禁时，使用 [GitHub 生命周期自动化](../github-lifecycle-automation.md) 的 `lifecycle-policy`；该检查不替代现有构建、测试、独立评审或高风险人工决定。

## 文档治理

合入前必须由非作者人类或独立 Agent 使用文档交付验证技能，独立读取实现、双语文档和证据。全部本次必需检查与评审通过、快照有效才可合入；必需文档、英文或证据缺失不得豁免，实质变更后重验受影响范围。

遵循[项目文档规范](../documentation-standard.md)和[接入说明](../documentation-integration.md)。[文档维护](../../skills/04-implementation-and-self-test/documentation-maintenance/SKILL.md)负责准备与更新，[独立文档验证](../../skills/05-integration-validation/documentation-delivery-validation/SKILL.md)负责检查结论，使用[统一交付检查模板](../../templates/documentation/delivery-check.md)。缺少专用检查器时保留逐项实际核对证据，不能声称第三阶段自动门禁已启用。

## 可信证据来源

独立验证按[证据契约](../evidence-trust.md)区分来源认证与记录一致性；采用受信维护者模式时，合入就绪使用固定读取器回读候选和真实 CI。

## 输出与阶段 06 交接

复用[变更交接](../../templates/delivery/change-handoff.md)，以稳定ID链接原需求/方案/任务及验证矩阵，不复制状态。实际交接至少七项：

1. 当前批准范围、验收、方案与实际交付内容。
2. PR、源码head/base、真实main合入SHA/时间及已有构建/制品身份摘要。
3. CI、独立评审、适用专项、合入前及合入后端到端原始证据和当前覆盖。
4. 失败、修复、回退、复验及未决事项/责任；恢复基线不说成功交付原功能。
5. 发布兼容、配置/开关、迁移顺序、依赖与实际环境/规模限制。
6. 观测、恢复、文档及译文、运行准备和发布前后仍需做的节点/责任/判据/证据/停止动作。
7. 实际交出决定、版本/范围、接收方、责任/时区时间及下一动作；不伪填接收或发布批准。

06按[正式接收与候选身份](06-release-and-change-management.md#正式接收与候选身份)核对这些事实，再固定实际发布候选及源码/制品映射，验证候选组合、环境和有效发布权限；不从main绿自动得到制品verified或发布Go。本地模板、规则或合成演练不证明目标项目已强制CI，实际采用仍按既有接入与远端验收。

## 固化为 SKILL

| 行为 | SKILL | 适用边界 | 产出 |
| --- | --- | --- | --- |
| 同步任务分支、恢复误提交或合入后安全清理 | [`git-branch-management`](../../skills/04-implementation-and-self-test/git-branch-management/SKILL.md) | PR 分支操作需要实际执行时，不替代合入判断 | 分支操作、最新证据与保留/清理理由 |
| 独立核对本次文档影响、双语内容与证据 | [`documentation-delivery-validation`](../../skills/05-integration-validation/documentation-delivery-validation/SKILL.md) | 合入、专题完成或正式发布前 | 对应当前版本的通过/阻塞结论及修正复核 |
| 为新 GitHub 仓库建立稳定 CI 与适配真实能力的 CD 基线 | [`github-actions-bootstrap`](../../skills/05-integration-validation/github-actions-bootstrap/SKILL.md) | 项目已有可本地执行的质量命令，需要生成安全 Actions workflow 并通过首次 PR 自动取得真实 check-run 时 | CI/CD workflow、首次 PR 运行证据及仓库设置交接 |
| 为新 GitHub 仓库建立安全仓库设置并收口首次 CI PR | [`github-repository-bootstrap`](../../skills/05-integration-validation/github-repository-bootstrap/SKILL.md) | Actions 引导 PR 已自动产生成功稳定 check，或需要审计 Actions 权限、environments、ruleset 和删分支设置时 | 可验证的仓库治理设置、首次 PR 收口与分支清理证据 |
| 编排PR正式验证、受控合入及合入后收口 | [`github-pr-integration`](../../skills/05-integration-validation/github-pr-integration/SKILL.md) | 独立开发者或微型团队需要在 GitHub 上串联 CI、评审、专项/系统验证和合入判断时 | 前后精确对象、PR/合入后结果及06交接 |
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
| 验证并汇总跨领域、跨环境系统行为 | [`system-level-validation`](../../skills/05-integration-validation/system-level-validation/SKILL.md) | 每次功能合入前后端到端及跨边界系统验证时 | 跨域系统验证证据与适用范围 |
| 汇总反馈、豁免与最新状态以判断可合入性 | [`merge-readiness`](../../skills/05-integration-validation/merge-readiness/SKILL.md) | 准备合入目标分支时 | 可合入/阻塞结论及剩余事项 |

`github-actions-bootstrap` 负责首次 Actions 接入并产生可信 check-run 交接，`github-repository-bootstrap` 消费该证据完成仓库治理或后续审计，`github-pr-integration` 是面向 GitHub 小团队的日常 PR 编排入口；领域专项验证提供各自风险证据，`mobile-cli-execution` 负责执行官方工具并保存原始产物但不做通过判断，`mobile-validation` 汇总 iOS/Android/HarmonyOS，`web-frontend-validation` 汇总前端三类专项，`backend-validation` 汇总后端五类专项，`system-level-validation` 再保持客户端、服务和外部依赖的跨域汇总责任。所有这些 SKILL 只形成验证与合入结论；生产发布控制由阶段 6 负责。

项目采用验收按[采用规范](../harness-adoption.md)分别核对本地、非作者 Agent 实际行为与远端证据，缺覆盖/译文/真实 CI/可信记录或平台漂移均保持对应门禁阻塞。

后端/Web 风险选择、场景与证据交接遵循[领域执行契约](../domain-validation.md)：阶段 3 固定触发/支持/预算，阶段 4 保存真实执行，阶段 5 按完整专项和非作者内容评审汇总；机器一致性不替代批准。
