---
title: "领域专项验证记录模板"
status: current
owner: quality-lead
updated: "2026-10-12"
---

# 领域专项验证记录模板

[English](domain-validation.en.md)

## 追溯与准入

- record_id、record_type、record_status、owner、decision_authority、risk_level：
- related_records、requirement_id 与完整来源条款、触发及实际项目事实：
- source_version：完整 head/base/merge 或文件摘要快照；适用的制品/部署身份：
- created_at、updated_at、executed_at（带时区）：
- 完整领域适用性清单；场景、支持矩阵、工具/执行者、阈值与失败动作：


- 复合条款逐子项的触发、适用性、事实理由与场景，不以领域通用理由代替：

## 实际执行与证据

- environment_scope、版本、数据、基线批准、命令与原始材料位置/摘要：
- 全部适用场景：观察、passed/failed/not-run/blocked/stale/not-applicable 及事实理由：
- 真实边界与替身差异、未支持范围、失效条件与复验责任人：
- 独立评审者、实际读取、内容/翻译发现、修正及当前快照结论：

遵循[领域契约](../../docs/domain-validation.md)及[既有验证矩阵](../delivery/verification-matrix.md)，不替代 P0 门禁、必过 CI、独立批准或人类决定。保留原报告；schema 1 消费者仅核对一致性。
