---
title: "Harness 运行指标与持续复验"
status: current
owner: process-owner
updated: "2026-10-12"
---

# Harness 运行指标与持续复验

## 适用与责任

本文承接[领域契约](domain-validation.md)、[采用](harness-adoption.md)、[内容治理](content-governance.md)与[证据来源](evidence-trust.md)。指标用于发现执行缺口和安排复验；不能批准合入、替代目标产品 SLO、承诺效果改善或用于个人绩效排名。项目责任映射必须落实到实际维护者；本轮隔离试点由 anzihenry 维护、Agent 执行、非作者独立核验。

第一层规范与双语[项目报告模板](../templates/documentation/harness-observation.md)提供口径；`scripts/harness_metrics.py` 是本仓库内部只读支持工具，不进入现有安装包，不配置新周期任务或远端写入。现有周一只读 Issue 审计仍按原契约运行，其关闭数量不能替代效果验证。本工具只接收 schema 1 领域策略/报告，不改变 P0 或目标 CI 契约；旧 Markdown/CI/采用记录按同一字典人工提取和独立复算，不能伪称机器已接通。

## 最小指标字典

| 指标 | 分子/分母或统计对象 | 单位、来源、窗口与 owner | 缺失/解释边界 |
| --- | --- | --- | --- |
| 适用要求有效证据覆盖 | 当前完整准入中，其全部映射场景通过的适用要求数 / 全部适用要求数；不是通过场景数 | 比例；受控策略、实际报告、原证据与非作者准入核准；按候选/策略摘要和采集时点；quality-lead | 任一必需场景失败、未执行或缺评审，该要求不计有效；全局输入错误分子归零；分母零为 null，不写100% |
| 已复核阻塞样本误阻塞占比 | 独立判为 false-block 的事件数 / 被独立复核的 blocked 或 failed 事件数 | 比例；带事件 ID/理由/时间的非作者原始记录；同一窗口；quality-lead | 无复核为 null，未复核数单列；样本比例不是总体误阻塞率，AI 记录不是人类批准 |
| 阻塞分类 | 当前单项未通过名称、全局错误，以及已复核样本的原始原因计数 | 次；原始 reader 输出/评审原因；同一窗口；implementation-lead | 不从字符串猜根因，不将未知或采集失败记成功；未归因项继续诊断 |
| 检查耗时与重跑 | 实际 domain reader 调用的毫秒值全数组；同策略 cohort 不同事件数减一为窗口内重跑数 | ms/次；capture 的单调时钟、带时区起止与 attempt；operations-lead | 不是全 CI、产品请求或发布耗时；窗口前首跑未知，跨窗口不推断重跑总数；取消/采集失败没有伪造时长 |
| 复验逾期与关闭 | 必需且未有效关闭、due_at早于评估时点的对象 / 实际复验对象；逐项闭环状态 | 对象数；受控指纹、期限及当前非作者闭环记录；process-owner | 无对象不能证明无风险；关闭必须有当前范围证据、有效性判据，不自动改日期或减少原门禁 |

机器结果 `observed` 表示形成观察，`no-data` 表示窗口内无成功采集事件，`blocked` 表示输入或证据不可复算；没有质量授权含义。JSON fraction 的 null 必须在项目报告显示“无数据/分母未知或零”及原因。报告须保留全部原值、样本量、观察窗口、分组依据、缺口和敏感字段处理；不同口径、版本或环境不合并比较，不以短窗口两次读数证明趋势或因果改善。

## 事件、去重与采集

内部 capture 真实调用领域读取器并计时，记录 schema、完整 source_version、policy_sha256、attempt、带时区 started_at/finished_at、原始策略/报告路径与 SHA、单项结果和事件摘要。输入在读取前后变化则阻塞。原始执行文件仍由领域契约核验；散列一致性不证明真实运行、策略控制权或身份，独立评审与受信发布规则继续适用。

汇总配置 schema 1 必填 owner/from/until，窗口为 UTC 归一的 `[from, until)`，以采集结束时间归属。无时区、未知 schema、倒置窗口、不同事件复用同 cohort attempt、冲突重复、结果不可复算、原文件缺失/篡改/越界均阻塞。完全相同的事件 ID/内容只计一次；不同 attempt 保留为重跑。策略摘要包含来源、环境、支持与要求，形成独立 cohort；旧文件原路径/版本/摘要保留，不能把旧采集改成新报告。

配置可提供 block_reviews（path/sha256）及 collection_gaps。前者记录 event_id/reviewer/classification（false-block或correct-block）/reason/reviewed_at，非作者、样本身份及时间必须一致，复核不得早于采集或晚于统计截止；不自动生成通过。后者显式记录 id/state（cancelled、collection-failed、unknown）/reason/owner/source_version/recorded_at；缺口记录时间必须在同一观察窗口，它们不进入已执行检查分母，报告必须说明未采集范围，不能凭排除缺口承诺总体成功。

```text
.venv/bin/python -m scripts.harness_metrics capture --root EVIDENCE --policy EVIDENCE/policy.json --report EVIDENCE/report.json --attempt 1
.venv/bin/python -m scripts.harness_metrics summarize --root EVIDENCE --config EVIDENCE/metrics-config.json --events EVIDENCE/event-1.json EVIDENCE/event-2.json
```

调用者将 stdout 保存到新的受控位置，禁止覆盖已发布原始记录。读取失败输出结构化 blocked/exit1；成功采集一个实际 failed/blocked 检查仍是有效观察，不代表该检查通过。summarize 不写输入、任务状态或权限；人工消费者按同一字典核对当前实际来源后使用，不能从工具存在推导 CI 或调度已启用。

## 复验触发与闭环

每个对象记录唯一 id、实际 owner、authors、baseline/current 两份完整指纹、current_since、due_at、review_by、remedy、effect。十项指纹为 entry、knowledge、requirements、commands、dependencies、environment、support、roles、permissions、rules；值来自真实入口/知识 pin/条款/命令与工具/依赖/环境支持/责任/权限规则的受控版本或摘要，不能用随意占位值证明采用。改变任一项触发对应受影响范围复验，review_by 到期追加 review-due；缺当前盘点不能声称 current。

复验配置由负责人指定期限与解阻动作，不由工具编造承诺。到期或漂移仍保留旧报告，回到采用/领域/平台对应入口验证；原始失败与修正后新运行都保留。评估时点是报告窗口 until，项目必须选择真实已发生的结束时间；未来预测窗口只能标预测，不能作为当前闭环验收。

closure 引用外部原始记录 path/sha256，包含 state=passed、非作者 reviewer、当前 fingerprint、verified_at 和非空 evidence（path/sha256）。核对当前版本、变更后验证、到期后的实际复核、时间不超过评估时点及证据完整才显示 closed；旧指纹/作者自批/旧时间不能关闭。散列或闭环字段不能认证内容有效性，负责人和独立验证者还须实际核对 remedy/effect 达成，未达成时保持 required。此工具不推进 review_by、不改文档 updated、不关闭 Issue、不执行调度。

## 兼容与实际验收

本 schema 为内部首版，未知版本阻塞，不静默转换旧记录。没有机器消费者的 CI/采用/内容复审以实际报告和双语项目记录人工复算；不能为了统一形式改变安装 manifest 或放宽 P0 必过检查。两个真实采集时点用于验证可复算性，权限/环境/知识/入口/条款/命令依赖/支持责任/规则与到期的负例用于验证触发，修正后由非作者核准闭环；注入数据只证明检测逻辑，不宣称实际权限或定时任务改变。
