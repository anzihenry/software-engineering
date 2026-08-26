# Workflow 与 SKILL 内容治理

本仓库把 workflow 和 SKILL 视为需要持续维护的可执行流程资产。每份内容必须在 YAML frontmatter 中声明所有者、适用范围、状态和下次复审日期；仓库自检会阻止缺失、无效或过期的内容进入主分支。

## 元数据契约

workflow 直接声明治理字段；SKILL 为保持标准 frontmatter 兼容性，将相同字段放在受支持的 `metadata` 映射中：

```yaml
# workflow
owner: quality-lead
scope: "Lifecycle phase 5: integration validation"
status: active
review_by: "2027-02-26"

# SKILL
name: system-level-validation
description: ...
metadata:
  owner: quality-lead
  scope: "Lifecycle phase 5: integration validation"
  status: active
  review_by: "2027-02-26"
```

| 字段 | 规则 | 含义 |
| --- | --- | --- |
| `owner` | 非空、小写 kebab-case 角色标识 | 对准确性、复审和退役决定负责；不是每次执行该流程的人 |
| `scope` | 非空字符串 | 内容适用的生命周期阶段或工作边界；具体触发条件仍由正文和 SKILL `description` 说明 |
| `status` | `draft`、`active` 或 `deprecated` | 草拟中、当前可用或等待迁移/删除 |
| `review_by` | 引号包裹的 `YYYY-MM-DD` | 最迟完成下一次复审的日期；当天仍有效，次日起视为过期 |

`owner` 使用稳定角色而非个人姓名。当前阶段责任分别为 `product-owner`、`delivery-lead`、`technical-lead`、`implementation-lead`、`quality-lead`、`release-manager`、`operations-lead` 和 `process-owner`；团队可在本地责任映射中把角色关联到具体人员。

## 状态与使用规则

- `draft`：允许协作完善，但不得在导航或 workflow 中描述为默认可用能力。
- `active`：可按正文适用范围执行，所有链接、示例和工具约束必须与当前仓库实践一致。
- `deprecated`：只为迁移保留；正文必须明确替代路径或删除条件，不得继续扩大使用范围。

所有状态都必须按期复审。标记为 `deprecated` 不能代替清理，也不能绕过过期门禁。

## 复审流程

1. 所有者核对触发条件、停止边界、角色权限、链接、工具版本和实际交付证据。
2. 根据证据选择继续启用、修改范围、标记弃用或删除；涉及责任变化时同步更新 workflow 和 [`skills/README.md`](../skills/README.md) 的路由。
3. 只在完成实质复审后更新 `review_by`。建议复审周期不超过六个月；安全、隐私、发布和平台工具链内容可采用更短周期。
4. 在 PR 中记录复审依据和变更决定。不得仅批量顺延日期来制造未过期状态。

运行 `python3 scripts/check_repository.py` 会按执行日检查全部 workflow 和 SKILL。需要复现特定日期的结果时使用 `--as-of YYYY-MM-DD`；缺失字段、无效状态/日期以及 `review_by` 早于检查日都会失败。
