# Software Engineering Playbook

用于沉淀团队的软件研发准则、可复用 SKILL 与自动化 workflow。

当前基线：[研发全流程](docs/software-development-lifecycle.md)。

## 分层结构

- **准则（Principles）**：长期稳定的决策约束与质量底线。
- **流程（Workflows）**：从需求到运营的阶段、交付物和质量门禁。
- **技能（Skills）**：在特定工作场景下为人或 Codex 提供的可执行指南。
- **自动化（Automation）**：将重复、可验证的流程步骤固化为 CI/CD 或脚本。

该仓库首先维护流程基线，再依操作频率和风险优先级沉淀专题 workflow 与 SKILL。

项目内 SKILL 按研发阶段组织，使用入口见 [SKILL 导航](skills/README.md)。

开发与验证阶段在生命周期主轴下进一步按移动端、Web 前端和后端划分领域 SKILL；移动端区分跨平台共享层与 iOS/Android 平台层，Web 前端区分 UI/状态开发和功能/视觉/性能验证，后端区分 API/数据/异步开发和契约/一致性/性能/韧性/安全验证。跨领域工作仍由阶段通用 SKILL 编排，避免领域流程与统一质量门禁脱节。
