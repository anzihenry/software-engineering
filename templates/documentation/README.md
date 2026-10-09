---
title: "项目文档模板"
status: current
owner: process-owner
updated: "2026-10-09"
---

# 项目文档模板

[English](README.en.md)

## 资产边界与当前阶段

本目录是 harness 的第一层模板资产，配套[项目文档规范](../../docs/documentation-standard.md)。模板供目标项目按需采用，不要求 software-engineering 自身创建目标项目目录；当前安装器不分发本目录。

规范和模板已通过[接入说明](../../docs/documentation-integration.md)连入 harness 入口、八阶段 workflow 与 SKILL。目标项目检查器、配置和 CI 模板见[工具接入](../../docs/documentation-tooling.md)；使用模板不能代替实际检查或独立评审。

## 模板导航

| 模板 | 推荐目标文件 |
| --- | --- |
| [项目文档规范配置模板](documentation.md) | `documentation.md` |
| [项目入口模板](project-readme.md) | `project-readme.md` |
| [变更摘要模板](changelog.md) | `changelog.md` |
| [文档导航模板](index.md) | `index.md` |
| [长期知识文档模板](knowledge.md) | `knowledge.md` |
| [专题入口模板](initiative.md) | `initiative.md` |
| [需求模板](requirements.md) | `requirements.md` |
| [研究模板](research.md) | `research.md` |
| [方案模板](design.md) | `design.md` |
| [执行计划模板](plan.md) | `plan.md` |
| [技术决策模板](decision.md) | `decision.md` |
| [版本发布记录模板](release.md) | `release.md` |
| [验证记录模板](validation.md) | `validation.md` |
| [交付文档检查模板](delivery-check.md) | `delivery-check.md` |

推荐目标：project-readme 用于根 README，changelog 用于根 CHANGELOG，index 用于目录 README，initiative 用于专题 README，decision 按编号命名，release 用于版本 README。其他文件按主题采用；不是要求统一复制模板文件名。

## 使用步骤

1. 在目标项目 docs/documentation 记录固定规范来源、采用范围、责任与执行配置。
2. 仅创建有实际内容的领域或专题目录；所有正式文档复制中英文配对模板，填写真实元信息、选择合法状态、删除模板使用说明和全部占位项。
3. 为实际目录创建导航，检查同语言相对链接；模板互链需要随目标文件重命名一起修改。
4. 小专题可合写，必需内容不可遗漏；不适用项注明原因。
5. 交付前使用 delivery-check，由非作者独立评审。使用 check/snapshot/gate 记录实际检查方法与证据，不能编造自动检查结果。

## 与已有交付模板配合

[生命周期交付物模板](../delivery/README.md) 继续负责稳定记录 ID、风险、决策权限、环境、关联记录和证据。本文档模板负责文档位置与内容，不替换既有模板。合并使用时保留既有追溯字段，区分文档 status 与记录状态、updated 日期与 updated_at 带时区时间。

原始报告只保存一份，两种语言通过入口或摘要引用。模板正文中的元信息描述资产本身；用于项目后的 metadata 表达目标文档。

## 执行资产

- [Configuration](documentation-check.json)
- [Independent review record](independent-review.json)
- [CI workflow](documentation-gate.yml)
- [Tooling guide](../../docs/documentation-tooling.md)
