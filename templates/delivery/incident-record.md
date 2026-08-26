---
template_name: incident-record
template_version: 1
lifecycle_stages: [7]
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

# 事件记录

安全、隐私或受限证据事件使用 `security-privacy-incident-response` 的专项记录；本模板只保存允许进入普通运行记录的最小事实和受限记录标识。

## 追溯信息

- 记录 ID：
- 记录类型：运行事件 | 安全/隐私专项引用
- 状态：调查中 | 缓解中 | 已恢复 | 已升级 | 已关闭
- 所有者：
- 决策权限：
- 风险等级：严重度/优先级及映射依据
- 关联记录：告警、发布、变更、专项事件、工单或复盘 ID/链接
- 源码/制品版本：受影响版本、deployment、配置或依赖标识
- 环境与适用范围：服务、环境、地区、租户和用户范围
- 证据：指标、日志、追踪、状态页或受限证据记录标识
- 创建时间及时区：
- 更新时间及时区：

## 影响与响应

- 发现来源、开始时间、症状和用户影响：
- 已知事实、未知项和当前假设：
- 事件协调、技术处置、沟通和值守角色：

## 时间线

| 时间及时区 | 观察/操作/决定 | 操作者或决策人 | 授权 | 结果与证据 |
| --- | --- | --- | --- | --- |

## 沟通与关闭

- 当前状态、已执行缓解、下一更新时间和受众：
- 恢复验证、影响结束时间和残余风险：
- 安全/隐私专项、证据和通知状态（如适用，仅引用受限记录）：
- 关闭依据、关闭人和时间：
- 缺陷、运行改进、复盘和行动 ID/链接：
