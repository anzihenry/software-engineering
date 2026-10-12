---
title: "后端与 Web 专项执行契约"
status: current
owner: quality-lead
updated: "2026-10-12"
---

# 后端与 Web 专项执行契约

## 准入与责任

本契约细化既有后端五类、Web 三类和系统验证，复用[验证矩阵](../templates/delivery/verification-matrix.md)、[质量门禁](quality-gates.md)和[证据来源](evidence-trust.md)。新增内部一致性读取器不进入第二层自动化或第三层安装包，不自动批准合入或生产。

执行前由目标 maintainer 维护独立于候选的策略，列出全部相关来源文件、要求 ID/完整条款、触发条件、实际事实、专项、场景、支持矩阵、执行者、决策者、阈值、失败回流与完成条件。逐项判定全部已触发强制要求，不得只挑示例锚点。盘点必须覆盖契约、数据、并发性能、恢复、授权、浏览器、视觉可访问性、Web 性能及跨边界系统九类；未触发项说明事实理由，由非作者核对。缺工具、缺环境或缺批准不能写不适用。

策略固定完整 source SHA 或文件摘要快照、环境身份/工具/依赖/数据、浏览器版本/视口/辅助技术、所有适用场景与预算。阈值必须在观察结果前确定；失败不能靠放宽预算或更新视觉基线消除。项目支持策略不是脚本自动推断的默认值。真实认证、数据库、消息系统、外部服务和生产容量只有实际执行到对应边界才可声称验证。

## 版本化结果与消费者

领域机器报告独立采用 `schema_version: 1`，不修改文档 check/snapshot/gate、P0 门禁或已有 Markdown 输出。旧 Markdown 报告继续人工按本契约审查；不能自动导入为通过。未知 schema 阻塞，迁移须保留原报告并重新运行，不填补虚构观察值。

[读取器](../scripts/domain_validation.py)通过 `python -m scripts.domain_validation --root EVIDENCE_ROOT --policy POLICY.json --report REPORT.json` 调用。策略由受控来源提供，报告不能选择策略文件或削减场景；维护者核对要求 ID 与固定[要求清单](harness-requirements.json)，CI/Agent 从固定 harness 运行。读取器只核对一致性，不证明策略/记录身份、真实执行或批准真实性。

| 字段 | 策略 | 报告 |
| --- | --- | --- |
| schema_version | 固定 1 | 固定 1 |
| source_version、environment、support | 当前完整候选身份、实际环境与支持配置 | 必须完全相同；变化使证据失效 |
| authors | 本次作者/修改者身份 | 不由候选覆盖 |
| domains | 九类的 applicable 布尔值与 reason | 不替代准入盘点 |
| admission | 每条唯一 id、source/完整原文、trigger、applicable、reason、owner、failure_action、cases；适用条款必须映射场景，不适用条款不得声称执行 | 不由报告覆盖；独立核对固定清单完整性 |
| cases | 按唯一场景 ID：domain、requirements、恰好一个 equals 或 maximum、可选 review_required；与 admission 双向一致 | 同一完整场景集合 |
| 单项 | 预期观察或非负有限数值上限；来源条款和独立审查需求 | state、execution、observed、evidence；必要时 review |
| evidence | 原始材料的保留位置由项目登记 | 根目录内相对 path 与 sha256；禁止穿越和符号链接 |
| review | 需要批准设计/基线或人工判断时设置 review_required | reviewer、state、source_version；非作者实际读取的原报告同时进入 evidence |

报告保留原始 HTTP 请求/响应、浏览器日志、场景状态/截图、工具版本、实际带时区执行时间和执行命令。`passed` 必须有当前原始证据和满足预期的观察；只有替身、not-run/blocked/stale、缺材料、未批准视觉基线或作者自批均阻塞。读取器拒绝非法对象/schema（包括布尔值冒充版本）、没有断言或未准入的场景，并将异常输入转换成 blocked；数值预算拒绝 NaN、布尔、负值或越界；预期 401/403/409/503 是负向场景成功的观察，不是把实际产品缺陷改写成功。

单项失败回流对应实现；契约、支持、预算或基线缺口回流方案/负责人，环境失败先修环境。汇总完整用户旅程时引用专项原报告，不复制另一份事实；整体结论由既有节点策略决定，领域通过不能越过必过 CI、独立文档门禁或人类高风险决定。有条件结论不能推进合入、候选或生产。

## 可重复的隔离参考

[合成服务](../tests/fixtures/domain-reference/server.py)仅绑定 loopback，标准库 HTTP 与静态 Web，共享真实传输。两个主体分别拥有 alpha/beta 两个实际不可变资源，验证各自读取 200 与双向越权 403。`X-Reference-Actor` 是公开合成身份，不是密码/token 或生产认证；不可部署成公开服务。[采集器](../scripts/domain_reference.py)保存匿名 401、对象拒绝 403、版本拒绝 409、控制故障 503 和恢复 200，以及 4 workers/16 次不可变读取和客户端超时。故障是服务内显式注入：正常请求控制延迟 100 ms，慢请求 200 ms、客户端超时 50 ms；不冒充外部依赖断连。客户端取消后的 BrokenPipe 日志属于该受控超时，可独立核对；内存不可变读不证明事务、迁移或持久恢复。

```text
python tests/fixtures/domain-reference/server.py --port 8765
python -m scripts.domain_reference --port 8765 --output /tmp/reference-http.json
node tests/fixtures/domain-reference/browser.cjs /tmp/reference-browser
```

浏览器采集需要项目已安装的 Playwright；可通过 NODE_PATH 指定既有包、REFERENCE_CHROMIUM 指定匹配的既有浏览器。没有运行时则记录 blocked，不由示例安装或升级依赖。浏览器脚本默认 loopback 8765，可由 REFERENCE_URL 指定本次隔离进程的实际 http/127.0.0.1 根 URL，拒绝其他主机、协议、凭据、查询和片段；保存引擎版本、视口、网络/控制台、正常/故障/恢复/过期/空状态、仅键盘正常/故障/恢复及焦点保持、accessibility tree、宽窄屏/焦点截图和五次导航原始测量。场景用原生语义单选组，结果使用 status live region；禁用按钮后恢复原焦点。真实屏幕阅读器验证仍由适用支持策略要求的人工路径执行，accessibility tree 不能替代它。

参考仅验证其明确的合成支持配置，不代表完整 Web 产品已验收。项目若采用生产认证、数据库、其他浏览器、屏幕阅读器、地域故障或真实用户性能预算，须补相应场景并阻塞未执行项。参考的 schema/证据负例同时覆盖必需浏览器/键盘场景缺失、未批准基线、预算失败、环境/原报告缺失、旧候选和只提供替身；项目报告用[双语模板](../templates/documentation/domain-validation.md)记事实与限制。

真实辅助技术试点可记录系统提供的 VoiceOver 原始游标/朗读与操作轨迹，但不得把脚本注入朗读文本当界面语义证据；必须绑定当前页面与候选、在授权目标上操作并恢复临时设置。未执行的关键辅助技术场景必须进入报告 blocked/not-run，而不是只写旁注后给整体 passed。

复合条款准入须分拆子项判断，不能以领域通用理由覆盖输入大小/格式/路径、两倍文字/窄屏错误长文、对比度或已触发性能指标。参考限制 query 为 1024 字符、拒绝重复参数；两倍文字渲染明确为 18→36 px，不冒充桌面缩放按钮。正文最低对比度 4.5:1、焦点与背景最低 3:1 的局部检查依据 [W3C 文字对比度说明](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)和[非文字对比度说明](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)，不构成完整 WCAG 合规结论。
