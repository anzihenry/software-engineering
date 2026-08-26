---
name: github-release-management
metadata:
  owner: release-manager
  scope: "Lifecycle phase 6: release and change management"
  status: active
  review_by: "2027-02-26"
description: "在独立开发者或微型团队中，用 GitHub Actions、Environments、Deployments 和 Releases 编排发布候选、生产推进、健康判定、恢复与收口；适用于已合入版本准备交付目标环境或用户时。"
---

# GitHub 发布与变更管理

为小团队提供一条可追溯、成本可控且保留人类生产决策的发布主线。此 SKILL 编排发布阶段，不自行创建标签、发布 Release、批准 Environment、部署生产或执行恢复。

## 输入

- 已合入提交、风险等级、交付渠道、验收/集成验证证据和发布恢复预案。
- GitHub Actions 工作流、可用 Environments/保护规则、制品存储、部署目标和观测能力。
- 版本策略、迁移、特性开关、发布批次、健康阈值和值守安排。

## 运行模型

1. **选择模式**：普通变更走标准发布；已预先批准、可自动恢复且影响受控的低风险变更可走连续发布；正在缓解生产影响的最小修复转交 `emergency-change-management`。时间压力本身不构成紧急变更。
2. **准备候选**：使用 `release-candidate-preparation` 固定 source SHA、版本、制品摘要、迁移、发布说明和工作流运行。制品只构建一次，后续环境提升同一份已验证制品，不从不同分支或环境重新构建。本仓库采用[Draft Release 自动化契约](references/draft-release-automation.md)：先 dry-run，再由人类以版本精确确认创建 Draft Release。
3. **设计 GitHub 控制面**：用 Actions 执行确定性步骤，用 `staging`/`production` Environment 隔离目标、变量和密钥，用 `production` concurrency 防止并发部署；云认证优先使用短期 OIDC 身份。套餐不支持 required reviewers 时，以明确的人工 `workflow_dispatch`/Go-No-Go 记录替代，不声称存在平台强制审批。
4. **形成发布决策**：使用 `release-readiness` 核对候选、环境、观测、恢复、值守和授权。独立开发者必须亲自确认生产 Go/No-Go；Agent 只能准备证据和建议。
5. **预演并推进**：先在非生产环境验证部署、迁移、健康检查与恢复路径，再由 `progressive-release-execution` 一次推进一个批次。每批次保持制品摘要、配置差异和 GitHub deployment/run 可追溯。
6. **观察与控制**：每批次使用 `release-health-assessment` 对照预设业务和技术阈值决定继续、暂停、恢复或转入事件响应；部署任务成功不等于健康。
7. **执行恢复或收口**：达到暂停条件时停止扩大范围，在明确授权后使用 `release-recovery-execution`；稳定达到目标范围后使用 `release-closure` 更新 GitHub Release、变更记录和运行交接。

## 交付渠道差异

- Web/服务：可按实例、区域、租户或流量渐进；优先特性开关和可快速恢复的旧制品。
- 移动/桌面应用：签名制品必须固定；利用测试渠道和商店分阶段发布。商店版本通常无法即时回滚，应预置远程开关、兼容后端和前滚修复。
- 库、CLI 和可下载制品：先创建 Draft/Prerelease 并附齐制品，再发布标签、GitHub Release 和包；已公开版本不得用同版本覆盖不同内容。

## 输出格式

```markdown
## GitHub 发布状态
- 模式、渠道、版本、source SHA 与制品摘要：
- GitHub workflow / deployment / environment：
- 就绪结论与人类 Go/No-Go：
- 当前环境、批次、范围和健康判定：
- 迁移、配置、开关与恢复状态：
- 发布状态：候选准备中 | 待批准 | 进行中 | 暂停 | 恢复中 | 已完成
- 下一动作、授权要求与责任人：
```

## 停止条件

- 候选、授权、环境、观测或恢复条件不足时停止在对应门禁，不用管理员旁路制造进度。
- 任何生产部署、Environment 批准、标签/Release 发布、商店提交、回滚或前滚都必须有针对该动作的明确授权。
- 发布稳定收口后交给运行与支持；存在用户影响时转入恢复或事件响应。
