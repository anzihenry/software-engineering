---
title: "交付证据记录模板"
status: current
owner: process-owner
updated: "2026-10-11"
---

# 交付证据记录模板

[English](evidence-record.en.md)

## 追溯与执行

- record_id、record_type、record_status、owner、decision_authority、risk_level：
- related_records、requirement_id 及原条款适用范围：
- source_version：仓库、完整 head/base/merge SHA、快照摘要；候选还需制品摘要/构建 run，部署还需 deployment ID/配置/范围；不适用说明原因。
- environment_scope、工具/依赖/数据基线、方法和实际读取/执行范围：
- created_at、updated_at、实际 executed_at（带时区）：
- evidence：原始报告不可变地址、摘要、保存权限和身份来源：
- 原始结果：passed | failed | not-run | blocked | stale | not-applicable（依据/事实原因）：
- 模拟/实态边界、未覆盖范围、复用理由、失效条件和补验责任：

## 独立来源与结论

- 作者/修改者、独立评审者、另起上下文及实际读取材料：
- 受信发布者、受控来源核验者、身份/权限/候选/真实 CI 回读：
- 发现、作者修正、独立复核及最终当前版本结论：
- 独立评审与人类授权分别引用；不由填写人自批 passed。

遵循[证据契约](../../docs/evidence-trust.md)，复用原文档评审 schema，不复制另一套任务状态。
