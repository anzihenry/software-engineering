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

跨阶段交付物可从[生命周期交付物模板](templates/delivery/README.md)开始，使用统一追溯字段关联机会、需求、方案、验证、变更、发布、事件和复盘行动。

通过[端到端研发演练](docs/exercises/README.md)检验低、中、高风险变更能否实际走通八阶段门禁、证据和回流。

开发与验证阶段在生命周期主轴下进一步按移动端、Web 前端和后端划分领域 SKILL；移动端区分跨平台共享层与 iOS/Android/HarmonyOS 平台层，并通过独立 CLI 执行层调用三端官方工具链、管理测试目标和留存原始证据；Web 前端区分 UI/状态开发和功能/视觉/性能验证，后端区分 API/数据/异步开发和契约/一致性/性能/韧性/安全验证。跨领域工作仍由阶段通用 SKILL 编排，避免领域流程与统一质量门禁脱节。

集成验证与发布阶段默认适配独立开发者或微型团队使用 GitHub 的场景：PR、Actions、Environments、Deployments 和 Releases 分别承载合入门禁、确定性执行、环境控制、部署追踪与对外版本记录；平台套餐不支持的审批能力使用明确的人类决策记录替代，不虚构自动化保证。

Coding Agent 的跨项目语言约束见 [编码规范](docs/coding-standards.md)，当前覆盖 TypeScript 7、ArkTS、Python 3.14、Swift 6.2、Kotlin 2.4、Go 1.27、SQL、zsh 和 C++20。

## 仓库自检

仓库使用 Python 3.14 执行确定性的结构与格式门禁，覆盖 YAML 解析、SKILL frontmatter、交付物模板及追溯契约、端到端演练覆盖、目录与名称一致性、站内相对链接、导航/workflow 覆盖以及 Markdown 基础格式。

```sh
python3 -m pip install --requirement requirements-dev.txt
ruff check scripts tests skills/05-integration-validation/github-actions-bootstrap/scripts
ruff format --check scripts tests skills/05-integration-validation/github-actions-bootstrap/scripts
python3 -m unittest discover --start-directory tests
python3 scripts/check_repository.py
```

Pull Request 和推送到 `main` 时，[Repository checks](.github/workflows/repository-checks.yml) workflow 会执行同一组检查。
