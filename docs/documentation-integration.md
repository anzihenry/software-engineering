---
title: "文档治理接入"
status: current
owner: process-owner
updated: "2026-10-10"
---

# 文档治理接入

[English](documentation-integration.en.md)

## 当前能力与边界

文档规范已成为 harness 第一层默认研发要求：入口指令、八阶段 workflow、文档维护/独立验证技能和交付模板均已接入。规范版本为 0.1.0；[规范](documentation-standard.md)负责规则，[模板](../templates/documentation/README.md)负责交付内容。本阶段不改变第二、三层安装器或 GitHub policy，不创建目标项目目录，也不声称目标 CI 已启用文档门禁。

## harness 加载前提

完整 checkout 可使用文内相对路径；通过全局插件或单独技能分发时必须同时保证固定规范、模板与两个技能可访问，或在目标仓库提交等价规则并将路径填入项目配置。仅复制 AGENTS 模板、仅安装两个技能或仅填写检查清单不能构成完整接入。规则不可访问时记录缺口，不能声称合规。

## 目标项目入口

1. 将[项目 AGENTS 模板](../templates/codex/AGENTS.md)的文档条款合并到既有入口，保护原有指令和命令。不会替换项目整个 AGENTS 文件。
2. 用[配置模板](../templates/documentation/documentation.md)建立或补齐 docs/documentation 及英文版，固定规范来源，填写责任、任务系统、检查方式、CI与评审位置。
3. 新项目按需建目录，已有项目列迁移清单；受本次交付影响的旧文档立即补齐，无关历史内容分批迁移。harness 资产库自身仍按 docs/workflows、skills、templates 组织。

## 生命周期路由

| 阶段 | 文档动作 | 完成判断 |
| --- | --- | --- |
| 需求与研究 | 原始材料唯一来源，需求/专题归属，研究范围与局限 | 证据可追溯，影响和责任明确 |
| 方案与计划 | 专题方案、长期决策、接口与体验规则，双语和验证任务 | 正式定义唯一，更新与评审纳入计划 |
| 实施与交接 | documentation-maintenance 同步文档、英文、导航和快照 | 准备完整检查记录，不由作者自批 |
| 合入验证 | documentation-delivery-validation 独立查实现、文档、漏项、证据 | 当前版本文档检查通过，否则阻塞 |
| 专题完成 | 核对验收、长期知识/英文回写、遗留转交 | 文档检查通过才 completed |
| 正式发布 | 核对版本说明、兼容/升级指南、实际候选与检查证据 | 文档检查通过再进入既有人类 Go/No-Go |
| 运行与复盘 | 回写手册和研究结论，保留历史与受限证据 | 修正仍走检查，定期复核补充交付门槛 |

[文档维护技能](../skills/04-implementation-and-self-test/documentation-maintenance/SKILL.md)可跨阶段使用；[独立验证技能](../skills/05-integration-validation/documentation-delivery-validation/SKILL.md)不能由作者上下文执行。现有需求、方案、交接、PR评审、合入就绪、发布就绪和收口技能均有直接调用要求。

## 检查与评审执行

用[统一检查模板](../templates/documentation/delivery-check.md)记录一份实际结论。普通变更在 PR、专题在 validation/README、发布链接该记录。先核对元信息、状态、命名、配对、互链/章节/导航，再独立核对内容、实现、中英语义和适用示例。

使用[机械门禁与 CI 接入](documentation-tooling.md)执行 check/snapshot/gate，记录实际范围、结果和证据，不把文件存在当语义正确。项目已声明必过的 CI 要有真实通过结果；无规范配置、必需更新、英文、证据、独立性或有效快照时阻塞，不能给文档条件通过。

独立评审者只记录问题，作者修改后评审者复核。未提交工作可用路径与 SHA-256 清单绑定；相关修改使对应结论失效。AI 评审不冒充平台人工批准，不替代专业审批或生产 Go/No-Go。紧急运行恢复仍按既有授权执行，但不能把缺失文档验收记为通过或 completed。

## 资产维护与后续验证

harness 规范、workflow、SKILL 和操作参考只维护中文，不要求新增英文副本或翻译评审；本仓库入口仍要求影响检查、路由、独立内容评审和当前版本证据，保留治理状态、review_by 与追溯字段。目标项目正式文档及其输出模板仍需双语。历史英文资产不自动整库迁移，删除前核对引用。

第三阶段已提供机械校验、评审记录一致性门禁、配置与 CI 模板；采用验证通过隔离 Git 项目的实际 CLI 和独立评审执行。当前流程接入本身不证明 Agent 一定加载成功、平台一定强制门禁或所有目标项目已经采用，实际使用需保留加载与交付证据。
