---
template_name: verification-matrix
template_version: 1
lifecycle_stages: [3, 4, 5]
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

# 验证矩阵

## 追溯信息

- 记录 ID：
- 记录类型：验证矩阵
- 状态：规划中 | 执行中 | 通过 | 有条件通过 | 失败 | 阻塞
- 所有者：
- 决策权限：
- 风险等级：低 | 中 | 高
- 关联记录：需求、方案、变更、PR 或豁免 ID/链接
- 源码/制品版本：仓库、head SHA、构建或制品摘要
- 环境与适用范围：
- 证据：CI、测试报告、日志、截图、指标或人工验收记录
- 创建时间及时区：
- 更新时间及时区：

## 验证基线

- 目标版本、环境、依赖和测试数据：
- 生产差异、支持矩阵和基线指标：
- 自动化/人工边界及证据保留位置：

## 要求与风险映射

| 要求/风险 ID | 场景与预期结果 | 验证层次/方法 | 环境/数据 | 通过阈值 | 负责人 | 当前版本证据 | 结果 |
| --- | --- | --- | --- | --- | --- | --- | --- |

## 结论

- 正常、边界、失败、授权、兼容和恢复覆盖：
- 未覆盖范围、环境限制和影响：
- 失败、豁免、授权、到期和补救计划：
- 当前 head SHA 的总体结论和决策人：
