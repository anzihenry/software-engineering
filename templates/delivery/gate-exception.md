---
template_name: gate-exception
template_version: 1
lifecycle_stages: [4, 5, 6]
traceability_fields:
  - record_id
  - record_type
  - status
  - owner
  - decision_authority
  - risk_level
  - related_records
  - source_version
  - environment_scope
  - evidence
  - created_at
  - updated_at
---

# 门禁例外记录

[English](gate-exception.en.md)

## 追溯信息

- 记录 ID：
- 记录类型：
- 状态：
- 所有者：
- 决策权限：
- 风险等级：
- 关联记录：
- 源码/制品版本：
- 环境与适用范围：
- 证据：
- 创建时间及时区：
- 更新时间及时区：

## 决定与限制

- rule_id、允许例外的原规则依据：
- 节点、实际对象/范围、当前原始检查结果：
- 授权人、身份核验者及可追溯授权来源：
- 原因、剩余风险与允许推进范围：
- 带时区的决定时间和到期时间：
- 补救任务、责任人及截止时间：
- 撤销条件、复核条件和实际补验记录：

按[门禁规范](../../docs/quality-gates.md)判断；必需文档、适用译文、证据、独立性、既有必过 CI 及人类生产/高风险授权不可豁免。作者填写不构成授权；条件结论不改写原失败结果，不自动批准合入/发布。
