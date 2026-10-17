# 生命周期交付物模板

本目录提供覆盖八阶段研发流程的最小交付物模板。模板可复制到项目采用的 Issue、PR、文档或变更系统中；文件位置不是事实来源，稳定记录 ID 和关联关系才是。

## 统一追溯字段

每份模板的 YAML frontmatter 声明相同的 `traceability_fields` 契约，正文“追溯信息”用于填写实际值：

| 字段 | 记录要求 |
| --- | --- |
| `record_id` | 稳定且唯一；推荐使用 `OPP-`、`REQ-`、`DES-`、`VER-`、`CHG-`、`REL-`、`INC-`、`RET-` 前缀 |
| `record_type` | 与模板负责的交付物类型一致 |
| `status` | 使用模板列出的状态；状态变化保留决策时间和依据 |
| `owner` | 对记录完整性和下一步负责的单一所有者 |
| `decision_authority` | 有权作出当前阶段 Go/No-Go、接受风险或关闭决定的人或角色 |
| `risk_level` | `低`、`中`、`高`或`不适用`；与风险评估保持一致 |
| `related_records` | 关联的上下游记录 ID/链接，至少能从当前记录回到需求并向后追到发布或关闭结果 |
| `source_version` | 适用时记录仓库、commit SHA、制品摘要、部署或发布标识；不能只写可变分支名 |
| `environment_scope` | 适用的产品、服务、环境、租户、地区、平台或用户范围 |
| `evidence` | 支撑结论的测试、运行、数据或决策记录；优先使用对应不可变版本的链接 |
| `created_at` | 带时区的创建时间，推荐 ISO 8601 |
| `updated_at` | 带时区的最后更新时间，状态或关键结论变化时同步更新 |

字段暂不适用时保留字段并写明原因，不删除字段或编造值。记录不得包含密钥、token、完整个人数据、受限事件证据或未经脱敏的生产载荷；敏感材料只保存受控位置，并在普通记录中引用其受限标识。

## 文档交付检查关联

交付记录继续使用本目录追溯契约；文档位置与内容遵循[项目文档规范](../../docs/documentation-standard.md)。变更交接、验证矩阵与发布记录统一引用[文档交付检查](../documentation/delivery-check.md)，避免复制多个结论。检查必须由非作者独立执行，绑定当前版本；文档 status 与交付 record_status 分开。

节点决策与例外引用[质量门禁规范](../../docs/quality-gates.md)；例外记录使用[中英模板](gate-exception.md)，保留失败结果与受控授权来源。

## 模板导航

| 阶段 | 模板 | 主要交付物 |
| --- | --- | --- |
| 1 | [机会记录](opportunity-record.md) / [English](opportunity-record.en.md) | 唯一机会主记录、六项判断、有限验证、状态迁移、排序与澄清交接 |
| 2 | [需求与风险包](requirements-risk-package.md) / [English](requirements-risk-package.en.md) | 七项设计投入条件、可判定验收、风险/依赖/未知、基线变更与实际决定 |
| 3 | [方案决策](solution-decision.md) / [English](solution-decision.en.md) | 有据方案、worktree预研、计划/实际开发批准、基线/变更/交接 |
| 3–5 | [验证矩阵](verification-matrix.md) / [English](verification-matrix.en.md) | 分节点规划/执行、前后端到端集合、精确合入对象、独立复核及阶段收口 |
| 4–5 | [变更交接](change-handoff.md) / [English](change-handoff.en.md) | 完整实现/自测、七状态、05前后验证/收口及06交接 |
| 6 | [发布记录](release-record.md) | [中英配对](release-record.en.md)，候选修订/组合、有效授权、批次/观察、中断恢复及07接收 |
| 7 | [事件记录](incident-record.md)（[English](incident-record.en.md)） | 责任/时钟、分诊、实际恢复与关闭、受限引用及08接收 |
| 8 | [效果复盘与行动](outcome-retrospective-actions.md) / [English](outcome-retrospective-actions.en.md) | 按类型填写评估/复盘/行动/规则；口径与决定、实施与效果、实际接收及回流分开 |

按风险裁剪正文中的非必需章节，但保留统一追溯字段和对应阶段的质量门禁。跨阶段合并记录时，仍为各类交付物分配独立 ID，避免一个状态同时代表需求、变更和发布状态。

阶段07常规工作使用补充[运行与支持记录](operations-record.md)（[English](operations-record.en.md)），按接收/健康/维护/支持适用章节填写，独立工作单元有各自ID；没有事件不创建假事故。两套模板均保留版本1/12字段，事件过程、健康、支持状态及结案原因分开。
