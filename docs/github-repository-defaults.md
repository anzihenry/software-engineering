---
title: "GitHub 仓库默认治理"
status: current
owner: quality-lead
updated: "2026-10-10"
---

# GitHub 仓库默认治理

[English](github-repository-defaults.en.md)

## 默认要求与适用范围

使用本 harness 研发的 GitHub 项目，默认必须启用以下两项设置，无须用户逐次额外提出：

1. 保护默认分支。新项目默认使用 `main`；已有项目保护实际默认分支，不自动重命名。有效规则要求 PR、真实 required checks、最新默认分支验证和评审对话解决，禁止强推和删除，默认无旁路。
2. 开启仓库 `delete_branch_on_merge=true`，让 GitHub 在 PR 合并后自动删除可删除的远端功能分支。该设置不清理历史分支或本地分支，也不保证删除受保护分支或其他仓库中的 fork 分支。

这是第一层研发流程的默认采用条件，复用已有第二、三层实现。仅加载 harness、复制入口或安装文件不会改变 GitHub 设置；只有实际应用并重新读取验证后，才能报告仓库治理已完成。不自动合并 PR、发布或部署。

## 默认执行路由

- 首次采用或发现设置漂移时，使用 [仓库初始化技能](../skills/05-integration-validation/github-repository-bootstrap/SKILL.md)读取现状、规划差异并验证。已有 CI 提供可信稳定检查时复用；否则先用 [Actions 初始化技能](../skills/05-integration-validation/github-actions-bootstrap/SKILL.md)通过首次 PR 取得当前 head SHA 的成功 check/App 证据，再配置保护，避免引用不存在的检查。
- 使用跨项目安装器的完整采用默认选择 `full`，仅需要治理时选择 `governance`；二者已有实现会配置上述两项。明确选择 `incident` 或 `release` 仍保持其单项职责，不额外扩展写入范围；单项安装完成不能据此声称已满足完整 harness 治理基线，须另走仓库初始化技能。
- 每个目标仓库确认身份、管理权限、套餐能力与已有组织/仓库规则。执行必要且已获授权的写入；已有明确授权时不重复请求。仅加载 harness 不构成任意远端写入授权；缺少授权时先提供可审查差异再取得授权。缺少权限、能力、真实检查或规则冲突时报告治理未完成及最小解阻动作，不绕过或削弱既有保护。
- 日常 PR 通过 [PR 集成](../skills/05-integration-validation/github-pr-integration/SKILL.md)和[合入就绪确认](../skills/05-integration-validation/merge-readiness/SKILL.md)核对基线；漂移交回仓库初始化技能，不由日常 PR 流程隐式修改规则。

## 安装器操作与验证

安装器已默认使用 `full`；下面显式使用仅治理的 `governance`。在目标仓库中，安装 PR 仍 Open 且 `validate`、`lifecycle-policy` 对其当前 head SHA 成功后运行：

```sh
python3 -m scripts.github_lifecycle bootstrap \
  --repository OWNER/REPOSITORY --profile governance --evidence-pr 123
```

复核 dry-run 计划，并在已授权的范围内应用：

```sh
python3 -m scripts.github_lifecycle bootstrap \
  --repository OWNER/REPOSITORY --profile governance --evidence-pr 123 \
  --no-dry-run --confirmation bootstrap:OWNER/REPOSITORY
python3 -m scripts.github_lifecycle doctor \
  --repository OWNER/REPOSITORY --profile governance --evidence-pr 123
```

替换仓库和 PR 占位值；目标仓库必须先按[快速开始](getting-started.md)安装共享工具及 policy。`doctor` 必须健康。仅使用第一层技能的项目按仓库初始化技能验证，无须为了设置这两项而强制安装完整自动化包。

## 完成证据

在采用/PR 记录中保存目标仓库、实际默认分支、读取时间、规则 ID/链接、有效规则、required check/App 与当前提交证据，以及重新读取的 `delete_branch_on_merge=true`。同时核对分支元数据 `protected=true`。传统 branch protection API 返回 404 不代表未保护，必须读取有效 ruleset 规则。

首次引导 PR 的合并仍遵守已有合并授权；合并后检查远端 head ref 是否已删除，才能报告该 PR 的实际清理成功。设置已启用和某个分支已删除是不同证据。非 GitHub 项目标记本项不适用；GitHub 项目存在阻塞时保留未完成状态，不能把本地安装或 dry-run 当成远端已生效。
