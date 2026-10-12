---
title: "Harness P1 分步验证记录"
status: current
owner: quality-lead
updated: "2026-10-12"
---

# Harness P1 分步验证记录

工作包状态只在[实施计划](harness-p1-implementation-plan.md)维护；本文记录本轮实际范围、运行与文档影响，不代表 main 合入或正式发布。

## P1-01 的参考范围与证据

用户确认使用隔离合成后端/Web 项目与 canary；交付渠道仅本地。任务分支 `codex/harness-p1-plan`，本包基线 `a703737acf561f2c0e2a752a71f1723b5611156a`。参考维护者为 anzihenry，执行者 Agent `/root`，独立验证身份与结论以外部实际评审记录为准；不冒充维护者的人类批准。

本包新增[领域执行契约](domain-validation.md)、schema 1 内部读取器、双语目标输出模板和 loopback HTTP/静态 Web 合成项目。真实运行 Python 3.14.8、Node 24.19.0、已有 Playwright 1.62.1 与 Chromium 153.0.8010.12；原生 Chrome 155.0.8059.39/VoiceOver 在 macOS 27.0.1；无需安装生产依赖。Playwright CLI 缺失且 npm 镜像 DNS 不可用，内置浏览器走代理无法连接；改用已安装库的隔离无代理浏览器测试，未控制用户现有标签页。Ruff 0.16.7 使用仓库 py314 配置；未配置独立 Python type checker，不声称执行其检查。

原始材料位于 `/tmp/harness-p1-evidence/01`，首轮及 recheck/final/final-keyboard/radio 保留历史；当前候选报告在 candidate 子目录，current 保留第二轮历史：`http.json`（真实 HTTP、16 次/4 workers 不可变读）、`browser.json`（请求/响应、日志、五种状态、完整键盘路径、实际环境与 accessibility tree）、宽窄屏 PNG、`server.log`、`candidate/policy.json`、`candidate/report.json`、`candidate/admission.json`（九类来源 100 条原文与要求 ID）、仓库检查与独立评审。路径为本机试点证据；远端不可变保留在 P1-04 验证前不声称完成。重跑写新目录，旧报告保留。

合成准入只覆盖 HTTP 版本/序列化/错误、合成身份默认拒绝与对象边界、无状态故障恢复、不可变并发读、当前浏览器五种状态/键盘/宽窄屏、局部性能与跨边界路径。数据专项未触发：没有持久写、数据库、事务、迁移或最终一致性。消息、真实 IdP、第三方依赖、缓存/SSR、跨地域、真实容量与用户指标均不存在，不能从参考得出对应通过。用户已授权临时开启 VoiceOver 和系统 AppleScript 控制并恢复；首轮曾取得 Scenario/Load item/Reference item 的真实语义朗读，当前候选真实操作已执行：Service failure 单选 → Load item → 503 错误朗读 → Normal 单选 → Load item → Reference item 恢复朗读；当前非作者已核准限定路径与旧执行证据的适用范围，保留原 source 身份。accessibility tree 不能替代它，参考不能关闭完整 Web 产品的辅助技术验收。

本参考预算为全部非超时 HTTP 原始观察的最大值/五次导航最大值 2000 ms，用于超时与数值门禁演示，不是 SLO、吞吐或尾延迟容量批准。视觉为首次参考设计，截图须经非作者读取批准后才形成该参考基线；缺批准的实际报告保持 blocked；本轮限定参考基线已由非作者实际读图核准。正常、匿名 401、对象 403、版本 409、控制故障 503/恢复 200 都保留真实输出；单项有预期拒绝不是免除产品缺陷。

负向行为测试覆盖候选/环境漂移、场景遗漏、替身、证据缺失/篡改/路径穿越、未批准或作者自批基线、数值预算失败/NaN/布尔、未知 schema；不把合成报告当真实平台 CI。P1-04 才接通本轮 canary 新候选、真实必过 checks 和可信来源。

## 文件级文档影响与检查

| 类别 | 影响及处理 |
| --- | --- |
| 研究 | 经检查无需更新：不引入产品/用户研究；原始试点观察只在本文及原报告 |
| 产品 | 经检查无需更新：三层权限/安装边界不变；新增内部支持工具没有分发承诺 |
| 设计 | 已更新 domain-validation.md：支持、预算与基线批准/辅助技术边界；无目标产品设计系统变更 |
| 工程 | 已更新 domain-validation.md、读取器与测试：独立 schema、旧报告兼容和失败行为；不改 P0 schema |
| 指南 | 已更新 domain-validation.md：真实运行命令、既有工具发现、证据保留和阻塞方式 |
| 计划 | 已更新实施计划：本地/合成/canary 范围落实，工作包状态唯一维护 |
| 专题 | 不适用：harness 资产保持现有组织；目标项目记录用双语模板，不创建空目标目录 |
| 发布 | 不适用：本包无版本发布、渠道交付或生产验收 |
| 导航与职责 | 已更新阶段 3–5、skills/README、三个协调 SKILL、模板双语导航、要求来源清单 |

本包使用 Git 分支管理、语言编码规范（common/Python）、文档维护和独立文档验证 SKILL。机械检查执行 canonical `.venv/bin/python -m scripts.development check`，额外 Python compileall 与浏览器脚本 Node syntax check；实际结果/当前文件摘要/独立内容与模板翻译评审记录在同目录。未实现周期任务、CI 领域报告消费者或生产发布，不声称已强制。全部必过文档检查与当前快照独立评审通过后才提交本包。

首轮非作者验收阻塞并发现完整准入/漏报屏幕阅读器、非法输入与无断言缺口；已修正为逐条字段与双向场景映射、未执行项显式阻塞。真实补测发现按钮禁用造成焦点丢失，已修复；当前 Loading 五次、键盘正常/503/恢复和焦点保持、五次导航与真实客户端超时均有原始记录。匿名授权/协议拒绝等结果保留；favicon 404 为未定义可选图标资源，不影响合成请求路径，日志不删除。视觉与准入已由当前非作者逐项复核，相应 blocked 已解除。

最终补测增加两个实际主体/资源的正常与双向对象授权、1024 query 上限及重复参数/路径/SQL状输入/NaN版本拒绝。375 px 错误长文本在 18→36 px 的 200%文字渲染下 scrollWidth=375，明确不声称执行桌面缩放按钮；真实 computed style 得出正文对比度 16.451622、焦点 6.878484，原色/公式与独立复算保存。五次导航、交互耗时、layout-shift 与 resource entries 保存原数组；同一服务 PID 的 CPU/RSS 样本不外推容量。辅助技术原始 native 输出保留 voiceover-*.txt 与执行元信息，未经批准没有向其他窗口扩张访问；首次模糊窗口动作被自动审批拒绝，随后确切标题校验、用户手动置前与实际语义导航完成受限目标测试。用户手动解锁后已实际核对恢复：VoiceOver off、AppleScript 控制 0、ChatGPT→VoiceOver 的新增自动化权限 off；未改变既有 System Events 权限。原生测试与恢复分开记录，避免把设置开启当测试通过。

后续独立真实请求发现空参数丢弃和 empty=0 对象响应错误，已用 keep_blank_values 和按已授权资源组装响应修复；增加两项实际 ephemeral loopback 回归。报告 equals 按 JSON 类型区分 bool/number（含嵌套），CLI 输入缺失/坏 JSON/重复键输出结构化 blocked。修正后重新运行全部 HTTP/浏览器与仓库检查；旧 source/原报告保留，HTML 与原生 VoiceOver 相关正常/故障路径未改变时，仅由非作者明确核准可复用范围，不静默重写旧版本。

P1-01 最终复核：当前参考源摘要 `b23cff3d863633d9da1e30942879987a445156a1b58d8b461c26238f1232727e`；独立 Agent `/root/validate_p1_01` 核准九领域 100 条准入（89 适用、11 数据项不适用）、视觉和限定 VoiceOver 路径。全部 39 场景的实际一致性汇总通过，原始独立记录与 domain-gate-final.json 保存在 candidate。210 项测试、Ruff 与完整仓库检查通过。当前服务 PID 88299 的独立 CPU/RSS 样本保存于 independent-process-resource.txt；旧 PID 78986 样本只属于旧 source 历史。最终文件快照与内容/双语/恢复核对以独立评审记录为准；此包结论仅覆盖已声明的合成范围。

## P1-02 的运行观察与复验

本包新增[运行观察规范](harness-observation.md)、schema 1 内部只读 capture/summarize、双语项目报告、阶段8/三个既有SKILL与导航路由。基线 b6aca49（P1-01 提交），不改安装包、P0 schema、目标 CI 或既有周期审计。实际维护者 anzihenry，执行者/root；指标 owner 映射以受控试点配置为准。

原始证据在 `/tmp/harness-p1-evidence/02`。records 保留 P1-01 原文件副本，2026-10-12T09:07:13Z 附近两次真实 reader 调用为 3.353333/3.513042 ms，各39场景通过、89/89适用要求有效；第三次真实读取未核准旧报告为blocked、0/89，原始事件保留。只证明 reader 可复算，不代表重演浏览器或全 CI 时间，也不以两次短窗口证明效果改善。实际缺文件 capture exit1/stdout/stderr 保存 collection-failure.json，归类受控负例采集失败；未将其写成产品事故或丢失总体分母。

机器按完整受控策略摘要分组、完整事件去重、attempt保留、UTC窗口及原文/报告SHA重新核验。10项有行为断言的测试覆盖零/无数据、重复/冲突、原证据篡改、部分样本/作者自批、版本分组、时区/窗口/重跑/缺口、非法类型/路径、十项漂移/到期/旧闭环；要求映射所有必需场景通过才计有效。误阻塞分母仅实际被非作者复核的阻塞样本，已接入非作者实际复算的 correct-block 记录，复核样本误阻塞为0/1；它不是总体误阻塞率。

本地参考复验指纹来源保存在 fingerprint-sources.json：入口/当前知识提交、条款、命令、依赖、环境/支持、责任、合成对象授权与本地质量规范；不冒充新的GitHub权限审计。baseline知识 a703737→当前b6aca49、时间修正后的 requirements 摘要变化及受控本次复审期限触发 required/overdue；期限是本机验收演练的即时检查点，不是人类团队日历承诺。旧报告保留，闭环已由非作者核对当前39场景/89条准入、来源与新指纹后记录，旧review_by未推进；复用P1-01有效范围，不声称重跑原生AT。十类漂移的单位测试注入只证明触发逻辑，未真的更改权限/远端规则。

文件级影响：研究无需更新（没有新产品研究）；产品无需更新（无业务/SLO或三层分发变化）；设计/工程已更新运行观察规范与内部事件schema/计算/兼容边界；指南已更新真实命令和异常；计划已更新P1-02验收中状态；专题/发布不适用（harness资产、无发布）；导航已更新阶段8、三个SKILL、skills/README与双语模板入口、要求来源。目标报告模板需中英独立语义验证；harness规范/操作资产中文适用。全量仓库检查、当前文件摘要、独立复算与最终文档核准通过后才提交本包。

P1-02 独立复算发现截止时间未限制后来的样本评审/缺口记录，已修正为复核不晚于 until、缺口记录在同一 `[from, until)`，增加未来记录不能改写早期观察的反例。旧配置/汇总仍保留；要求清单变化使用新当前指纹并重新请求非作者复核，不把旧闭环记录复制到新指纹。

P1-02 最终汇总接入真实 block-review/closure-review：两个有效样本89/89，旧阻塞样本0/89，已复核误阻塞0/1、未复核0，知识/条款/到期复验对象closed。原始初始配置、旧闭环和初始汇总保留，当前汇总以真实后续until为截止；这些是限定范围复算与闭环，不表示总体改善或生产授权。

## P1-03 的隔离本地交付渠道

本包基线180d8dee4c111ddb7edfe59d13932bc896a07a6e，按用户授权仅执行合成后端/Web真实本地渠道。[渠道参考](local-delivery-channel.md)、内部项目侧工具、双语渠道报告及阶段6/六项既有发布技能/导航已更新；正式候选已合入/Actions构建、云身份/环境/生产Go等门槛不因local-rehearsal而关闭，不扩第二层或安装包。实际owner为本机UID/anzihenry，executor/root。

证据在 `/tmp/harness-p1-evidence/03`。fixed-channel/exercise.json 为独立反馈修正后当前工具摘要冻结的真实执行：旧source b6aca49cb3fc7bd632a2304bea37a7e68098319b、制品960c0511889e6a503487cf1c33d74af8d3a417880e7c8a1a56d948bcc5c11841；当前source180d8dee4c111ddb7edfe59d13932bc896a07a6e、制品9d7e32465c9f2e80e96bfdd70d787dc39ecc124f90e077b215a8d4c468fd20e3。真实构建读取固定Git文件、Python compile、manifest/摘要与工具时间保存；示例业务字节相同，manifest/source与制品身份不同，不声称业务变更效果。新制品在后端/Web两真实目标消费，failed仍同一新制品，restored使用原旧ZIP，无部署重建。

各role四阶段healthy/healthy/实际health503 paused/healthy restored；三次间隔健康+身份、API200/匿名401/HTML与制品header均验证。Web候选与恢复各自真实隔离Chromium跑五状态、Loading/键盘503恢复与焦点、宽窄/文字reflow、原请求/资源/截图，浏览器脚本摘要绑定；未重跑原生AT，因为HTML与其路径沿用P1-01且本包仅渠道/动态loopback地址变化，复用适用范围已由非作者核准，旧原生执行身份保留。全部本次Popen子进程实际returncode/stopped记录保留，不停止其他服务、不声称仍在线。

fixed-negatives/observations.json 保存当前实际制品篡改、target/source漂移、UID不匹配、200ms/50ms真实健康超时、排他锁并发和ready后取消；对应child实际停止。9项行为测试覆盖确定性制品不覆盖、非法manifest/路径、所有权、双领域失败恢复、重复目录保护、取消/超时与并发。首次调用把旧完整SHA抄错，Git正确阻塞，纠正为实际rev-parse结果后执行；incorrect-source-first-attempt保留。real-channel/runtime-bound-channel/final-channel及早期negatives为执行历史，不能覆盖final冻结版本的成功。

文件级影响：研究/产品无需更新（无产品研究、业务/SLO或分发改变）；设计/工程已更新渠道契约/制品兼容/运行工具与目标生命周期；指南更新真实命令与停止恢复；计划更新P1-03验收中状态；专题/正式发布不适用（资产、本地演练）；导航更新阶段6、六技能、skills/README、双语模板入口与要求清单。Python/Ruff沿用项目工具，浏览器JS无新增formatter/type checker，实际Node syntax与浏览器行为验证；不升级依赖。全量检查及当前文件/源码/制品/配置/原始证据的非作者内容与双语核准后再提交。

P1-03 独立发现健康检查失败中途raw及browser超时部分输出丢失，另核对取消可能遗留collector；已修正为逐次共享原响应、owned collector/独立组、有限SIGINT/等待、超时与取消partial输出/报告和实际returncode。真实Chromium两次负例保存browser-lifecycle：Node均130、无forced fallback，本次启动PID72316/72345的后续ps均无进程；服务子进程亦停止。domain-validation默认8765文案同步为仅允许本次动态loopback根URL，旧条款退役替代保留约束。修正后完整229测试及仓库检查通过；源码/工具/浏览器摘要冻结后的fixed-channel重跑两领域交付/503/恢复均通过，当前非作者已核准21文件、全部实际证据与三项缺口关闭，限定本地真实渠道范围通过。

P1-03 最终独立验证通过：制品/Git字节、八阶段身份与健康/API/浏览器、实际取消/超时与自持进程清理、默认/动态URL兼容、旧AT限定复用及双语模板一致。当前整包文件快照和最后检查以独立评审记录为准，结论只关闭本轮已授权的隔离本地渠道，不代表正式发布、main合入或其他平台能力。
