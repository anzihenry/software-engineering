---
template_name: release-record
template_version: 1
lifecycle_stages: [6]
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

# 发布记录

## 追溯信息

- 记录 ID：
- 记录类型：发布
- 状态：候选准备 | 待 Go/No-Go | 发布中 | 观察中 | 成功 | 已回滚 | 前滚修复中 | 暂停
- 所有者：
- 决策权限：
- 风险等级：低 | 中 | 高
- 关联记录：变更、PR、验证、审批、事故或 Release ID/链接
- 源码/制品版本：source SHA、版本、制品摘要、Actions run 和 deployment
- 环境与适用范围：目标环境、地区、租户、平台、渠道或用户批次
- 证据：候选构建、就绪检查、健康指标、恢复和通知记录
- 创建时间及时区：
- 更新时间及时区：

## 候选与就绪

- 候选版本、不可变制品、签名/SBOM/来源证明：
- 配置、迁移、兼容范围、开关和已知问题：
- staging/预演结果及生产差异：
- 观测、阈值、恢复、值守和通知准备：
- Go/No-Go 决定、决策人、时间和条件：

## 发布与健康时间线

| 时间及时区 | 批次/环境/范围 | 版本与 deployment | 操作和授权 | 健康证据 | 决定/下一步 |
| --- | --- | --- | --- | --- | --- |

## 恢复与收口

- 暂停、回滚或前滚触发与实际操作：
- 用户、数据和服务恢复验证：
- 最终上线范围、版本和状态：
- Release notes、运行/支持交接及通知：
- 最终结论、决策人、观察截止和复盘要求：
