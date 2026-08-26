---
template_name: change-handoff
template_version: 1
lifecycle_stages: [4, 5]
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

# 变更交接

## 追溯信息

- 记录 ID：
- 记录类型：变更交接
- 状态：实现中 | 待评审 | 验证中 | 可合入 | 阻塞 | 已合入 | 已关闭
- 所有者：
- 决策权限：
- 风险等级：低 | 中 | 高
- 关联记录：需求、方案、验证矩阵、PR 或豁免 ID/链接
- 源码/制品版本：仓库、base、head SHA、构建或制品摘要
- 环境与适用范围：
- 证据：本地检查、CI、评审和专项验证
- 创建时间及时区：
- 更新时间及时区：

## 变更说明

- 目的、范围与非目标：
- 主要实现、公共契约和用户可见变化：
- 数据、迁移、配置、权限、依赖和文档变化：
- 已知限制和兼容影响：

## 验证与评审

| 检查/评审 | 当前 head SHA 与环境 | 结果 | 证据 | 未执行项及影响 |
| --- | --- | --- | --- | --- |

- 验收标准与风险覆盖：
- 阻塞意见及解决状态：
- 豁免、授权、到期和补救计划：

## 发布交接

- 发布、特性开关、迁移和观察影响：
- 回滚/前滚注意事项：
- 运行手册、支持和通知变化：
- 合入结论、决策人和时间：
