---
title: "质量门禁、条件结论与例外边界"
status: current
owner: quality-lead
updated: "2026-10-11"
---

# 质量门禁、条件结论与例外边界

## 权威与结果语义

本文补充[生命周期](software-development-lifecycle.md)的跨阶段决策语义；项目具体规则只能在有依据的适用范围内裁剪，不能借一般例外豁免[文档强制交付](documentation-standard.md#严格交付检查)或既有必过 CI。领域验证矩阵的“有条件通过”只表达专项剩余限制，不是可合入或可发布批准。

单项结果保持 passed（实际通过）、failed（失败）、not-run（未执行）、blocked（无法完成）、stale（需重验）、not-applicable（有事实依据不适用）。总体就绪为 passed、conditional 或 blocked；执行授权另行记录。授权不能把单项失败改成通过，就绪通过也不产生合并、部署或生产授权。not-applicable 必须给出规则依据和事实理由；缺工具、权限、译文或证据不是不适用。

## 节点决策表

| 节点 | 输入与必需证据 | 决策责任 | 可推进的范围 | 失败动作 |
| --- | --- | --- | --- | --- |
| local 本地自测 | 项目实际命令、变更与验收映射、当前报告 | implementation-lead | 准备评审交接 | 修复实现或环境，不删测降门禁 |
| review 进入评审 | 自测通过、当前 diff、文档影响、待独立读取材料 | quality-lead | 开展独立验证，尚未可合入 | 补材料；未完成验证保持 Draft |
| merge 合入 | 当前 head/base、必过 CI、独立评审、治理、无冲突及阻塞意见 | quality-lead | 交给项目合并机制 | 修复/重验；不得授权绕过失败 |
| initiative 专题完成 | 完成标准、双语长期文档、验收与遗留转交 | delivery-lead | 记录 completed | 补验收/文档，不以发布成功替代 |
| candidate 候选验收 | source SHA、制品摘要、构建与当前验证、版本文档 | release-manager | 记录 verified、准备环境推进 | 固定候选并补验，变更后重验 |
| production 生产决策 | 候选通过、环境/观测/恢复/值守、人类 Go/No-Go | 有权限的人类 | 授权指定生产范围 | No-Go；条件 Go 的前置条件完成并重验前不得开始 |
| batch 批次推进 | 同一制品、当前健康窗口、硬阈值和范围授权 | release-manager / operations-lead | 授权范围内下一批次 | 暂停扩大，按授权恢复 |
| closure 发布收口 | 实际部署/制品/版本/范围、运行交接、双语说明、观察结果 | release-manager | 记录实际最终状态 | 保留暂停/恢复状态，不虚报成功 |

各节点的表格是最低输入类别，项目维护者必须从实际风险、领域规则及必过命令生成完整检查集合。不能省略必需检查，再凭剩余集合全绿声称通过。准备评审可以交接待独立评审材料；它不能替代 merge 节点的独立评审通过。

## 例外的准入与失效

必需文档、适用译文、证据、独立性、既有必过 CI 和人类生产/高风险授权不可豁免。例外只处理原规则明确允许接受的非强制限制；在受控项目策略中逐项登记允许例外的规则、适用节点和授权人。作者或 Agent 不能以记录中的“已授权”自批；授权来源由项目受信维护者/服务核验。

每份[例外记录](../templates/delivery/gate-exception.md)保留 rule_id、规则依据、实际对象/范围、原结果、授权人及身份来源、原因、剩余风险、带时区的决定/到期时间、补救任务、撤销和复核条件。到期、撤销、范围/节点/候选变化或授权失效后停止采用，补验或重新取得有权决定；保留原失败结果与历史决定。

正常且有效的非强制例外可形成 conditional，并仅在策略允许的 local/review/batch 节点推进指定范围。merge、initiative、candidate、production、closure 的条件结论只能用于补齐条件，不得推进；满足前置条件后按当前对象重新作出 passed。领域更严格规则优先，不能用通用表放行领域硬停止条件。

紧急恢复沿用[发布流程](workflows/06-release-and-change-management.md)已有授权和最小目标测试，不通过普通例外伪造完成。恢复可先执行，缺失验收仍记未完成，主线同步、文档、补验与复盘未完成前不关闭交付。

## 执行与能力边界

`scripts/quality_gate.py` 对受控策略指定的完整检查集合、原结果及例外作确定性决策；CLI 输入与策略均需由调用者核验来源。它不认证身份、证据真实性、领域语义或完成外部操作，也不改变现有文档 gate。策略不得从 PR 的声明直接信任；可信来源由后续证据接入负责。已有项目必过 CI 仍实际执行。

```sh
.venv/bin/python scripts/quality_gate.py --record /outside/gate.json --policy /controlled/policy.json
```

策略包含 node、checks（name 到 category）、exception_rules（允许例外 name 到 authority 列表）；category 为 required、ci、documentation、translation、evidence、independence、authorization 或 optional。策略还可用 not_applicable 列出经维护者核实可不适用的检查名；既有必过 CI 不得列入。记录包含相同 node、非空 scope、source_version（40 位源码 SHA 或 64 位摘要）、checks（name 到 state/reason/basis，不适用时 basis 与事实 reason 均为非空文本）、exceptions（检查名到上节字段）。脚本输出原 checks、就绪、允许的推进范围和 blockers；返回非零表示不可推进。高风险例外、人类身份核验及生产授权由责任人判断，不由本脚本批准。

## 本步影响与验收

工程增加决策器与行为测试；指南/计划/导航、集成/发布 workflow、CI/合入/发布就绪技能增加本文引用；新增例外记录双语模板。研究/产品/设计无目标行为变化，专题/正式发布未发生。四检查及独立验证绑定本步摘要；正反例覆盖必需 CI/译文失败、无授权、过期/撤销、合法非强制例外、条件 Go 和恢复后补验。
