---
owner: process-owner
scope: "Lifecycle phase 8: measurement and retrospective"
status: active
review_by: "2027-02-26"
---

# 阶段 8：度量与复盘

## 目标

验证交付是否产生预期价值，从成功和失败中提取可执行改进，并将改进回流到产品、技术和流程。

## 输入

- 发布记录、成功指标基线与当前数据、SLO、质量数据、用户反馈、支持工单和事故记录。
- 计划假设、验收标准、目标与已知风险。

## 流程

1. **收集可信证据**：确定观察窗口和数据口径，对比发布前后产品、交付、可靠性和质量指标；记录数据缺口和混杂因素。
2. **评估结果**：判断目标和验收标准的达成情况，区分相关性与因果性；分析不同用户群、环境或发布批次的差异。
3. **组织复盘**：对重要发布、未达预期结果和事故举行无责备复盘，构建时间线，识别促成因素和系统性改进机会，而非归咎个人。
4. **确定行动**：将结论转化为有明确预期效果、负责人、优先级和截止日期的行动项；按需要创建需求、缺陷、技术债、SKILL 或 workflow 改进。
5. **跟踪闭环**：定期审查行动完成情况与实际效果；无效的行动应调整或关闭，并记录学习。
6. **更新基线**：将已验证的经验更新到设计准则、测试策略、运行手册或自动化中，并标注所有者与复审日期。

## 决策门禁

复盘关闭前，结论必须由可追溯证据支撑，行动项必须有所有者和期限，重大风险必须有明确处置路径。没有数据时应记录不确定性，而非把推测写成事实。

## 输出

- 效果评估、复盘记录、关键指标趋势与可追溯数据来源。
- 已排序的改进行动及其负责人、期限、成功判据。
- 对需求池、架构/测试/运行准则、SKILL 或 workflow 的更新建议。
- 使用[效果复盘与行动模板](../../templates/delivery/outcome-retrospective-actions.md)关联结果、系统学习和行动闭环。

## 异常与回流

- 数据不足或质量不可信：补充埋点、观测或研究，延后结论。
- 目标未达成：回到需求与机会重新判断问题、假设和优先级；必要时停止投入。
- 行动项长期未完成：升级给相应所有者，重新排序或明确接受风险。

## 交接给下一轮

将已验证的洞察和行动项回流到“需求与机会”，形成下一轮可排序的改进输入；将稳定、重复的做法固化为 SKILL 或自动化 workflow。

## 固化为 SKILL

| 行为 | SKILL | 适用边界 | 产出 |
| --- | --- | --- | --- |
| 以可信口径评估交付带来的结果 | [`outcome-measurement`](../../skills/08-measurement-and-retrospective/outcome-measurement/SKILL.md) | 需要判断目标、验收或护栏指标是否达成时 | 效果评估、数据限制和后续假设 |
| 复盘重要交付或未达预期结果 | [`delivery-retrospective`](../../skills/08-measurement-and-retrospective/delivery-retrospective/SKILL.md) | 非事故的项目、发布或协作学习时 | 无责备复盘结论与改进候选 |
| 对运行事件进行无责备复盘 | [`incident-review`](../../skills/08-measurement-and-retrospective/incident-review/SKILL.md) | 事件恢复后需要理解促成因素时 | 事实时间线、系统性改进与风险治理输入 |
| 将改进项转化为可验证的闭环 | [`improvement-action-tracking`](../../skills/08-measurement-and-retrospective/improvement-action-tracking/SKILL.md) | 已有复盘、评估或运行发现时 | 有所有者和效果判据的行动组合 |
| 依据验证结果演进准则、workflow 和 SKILL | [`playbook-evolution`](../../skills/08-measurement-and-retrospective/playbook-evolution/SKILL.md) | 稳定做法需要沉淀或现有规范需要修正时 | 版本化更新、试行与复审计划 |

复盘与流程更新必须以证据为基础，不将指标或复盘内容作为个人绩效的简化代理。
