---
name: documentation-maintenance
metadata:
  owner: implementation-lead
  scope: "Lifecycle phase 4: documentation adoption and maintenance across development"
  status: active
  review_by: "2027-02-26"
description: "在目标项目研发中分析文档影响、按规范组织研究/需求/方案与同步中英内容，或迁移既有文档；适用于文档准备与维护，不作独立验收结论。"
---

# 项目文档维护

[English](references/workflow.en.md)

## 依据与输入

读取[通用规范](../../../docs/documentation-standard.md)和目标项目 `docs/documentation.md`；按需要读取[模板入口](../../../templates/documentation/README.md)、实际变更、研究/需求/方案、既有文档与任务系统。仓库相对链接仅适用于完整 harness checkout；独立分发技能必须同时提供可访问的固定规范和模板，或项目提交的等价副本。依据不可访问时标记采用/合规证据缺失，不猜测规则或声称合规。

## 工作方式

1. 区分目标项目与 harness 资产维护。目标项目按规范建立按需目录；资产库保留 skills/workflow/templates 结构及其原有治理字段，不把目录骨架套在资产库。
2. 新项目填写规范来源、责任映射与实际检查配置；已有项目先列归属、状态、owner 和迁移任务，保护已有内容。按主要目标选择专题分类；小工作可留在 Issue/PR。不自动批量迁移或创建空目录。
3. 从研究到发布逐项列出产品、设计、工程、指南、计划、专题、发布和导航的文档影响，展开到文件。每项写已更新、经检查无需更新或不适用，并为后两者记录理由。只在一个位置维护任务状态与定义。
4. 同步受影响的中文和英文，选择合法元信息与对象状态；更新导航、相对引用与决策替代关系。需求/方案过程留在专题，生效事实回写长期文档，历史材料保留时间和版本范围。
5. 根据[交付检查模板](../../../templates/documentation/delivery-check.md)记录当前提交或路径/摘要快照、实际机械检查、示例验证、遗留事项与问题。缺少专用工具时逐项人工或临时工具核对结构和配对，并保留执行证据；项目已有必过 CI 不可替代。
6. 把材料交给未参与修改的人类或另起上下文的独立 Agent 使用 `documentation-delivery-validation`。自己修改过内容就不能自行批准。根据发现修正，再请求受影响范围复核。

## 输出与完成边界

输出采用配置或迁移清单、双语文档更新、文件级影响清单、证据快照和待独立评审的交付检查记录。普通变更放 PR，专题放 validation/README，发布链接该记录；不要复制多份结论。

必需文档、翻译或证据缺失时继续补齐或记录阻塞，不标记已完成/可合入/可发布。无关既有问题可另行跟踪并说明影响。仅在独立验证通过且相关检查仍对应当前版本时，向既有交付机制交接；本技能不批准合入、生产发布或专业风险例外。

## 机械执行入口

按[工具接入](../../../docs/documentation-tooling.md)配置目标项目登记清单并运行 check/snapshot/gate。评审记录由独立评审者填写实际读取、证据和结论；不得自动生成 passed。CI 模板必须接通可信独立记录来源并验证实际平台门禁，不能仅因模板存在声称已强制。
