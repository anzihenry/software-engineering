# Software Engineering Playbook

用于沉淀团队的软件研发准则、可复用 SKILL 与自动化 workflow。

当前基线：[研发全流程](docs/software-development-lifecycle.md)。

## 三层能力边界

- **研发知识与 SKILL**：定义如何完成研发工作，包括准则、阶段 workflow、SKILL、交付模板和演练。
- **GitHub 生命周期自动化**：把适合机械验证的规则落实为 PR、Release、Issue 和 Actions 编排。
- **跨项目安装与治理工具**：通过确定性打包及 `install`、`doctor`、`bootstrap` 分发和治理 GitHub 自动化。

完整的责任、权限、分发和依赖约束见[项目三层边界](docs/project-boundaries.md)。三层使用同一仓库版本；CI、Dependabot、本地开发入口和综合自检是横切的内部支持面，不作为第四个产品层，也不进入跨项目自动化包。

“准则、流程、技能、自动化”用于描述资产形态，不再作为与上述三层并列的项目分类。仓库首先维护流程基线，再依操作频率和风险优先级沉淀专题 workflow、SKILL 与自动化。

项目内 SKILL 按研发阶段组织，使用入口见 [SKILL 导航](skills/README.md)。

跨阶段交付物可从[生命周期交付物模板](templates/delivery/README.md)开始，使用统一追溯字段关联机会、需求、方案、验证、变更、发布、事件和复盘行动。

通过[端到端研发演练](docs/exercises/README.md)检验低、中、高风险变更能否实际走通八阶段门禁、证据和回流。

[GitHub 生命周期自动化](docs/github-lifecycle-automation.md)将 PR、发布、普通事故和复盘逐步固化为最小权限、可复制的原生编排，并提供跨项目 `install`、只读 `doctor` 和显式 `bootstrap`。

跨项目采用可选择 `governance`、`incident`、`release` 或默认的 `full` 安装 profile，让已有成熟流程的仓库只引入需要的 GitHub 能力；Python、Node、Swift、Go 和自定义 adapter 再把本地检查、Dependabot、稳定 `validate` check 与发布候选保留策略映射到项目自身实现。

开发与验证阶段在生命周期主轴下进一步按移动端、Web 前端和后端划分领域 SKILL；移动端区分跨平台共享层与 iOS/Android/HarmonyOS 平台层，并通过独立 CLI 执行层调用三端官方工具链、管理测试目标和留存原始证据；Web 前端区分 UI/状态开发和功能/视觉/性能验证，后端区分 API/数据/异步开发和契约/一致性/性能/韧性/安全验证。跨领域工作仍由阶段通用 SKILL 编排，避免领域流程与统一质量门禁脱节。

集成验证与发布阶段默认适配独立开发者或微型团队使用 GitHub 的场景：PR、Actions、Environments、Deployments 和 Releases 分别承载合入门禁、确定性执行、环境控制、部署追踪与对外版本记录；平台套餐不支持的审批能力使用明确的人类决策记录替代，不虚构自动化保证。

Coding Agent 的跨项目语言约束见 [编码规范](docs/coding-standards.md)，当前覆盖 TypeScript 7、ArkTS、Python 3.14、Swift 6.2、Kotlin 2.4、Go 1.27、SQL、zsh 和 C++20。

workflow 与 SKILL 的所有者、适用范围、状态和定期复审规则见[内容治理](docs/content-governance.md)；过期内容由仓库自检阻止合入。

## 仓库自检

仓库使用 Python 3.14 执行确定性的结构与格式门禁，覆盖 YAML 解析、GitHub 自动化权限与固定 Action、SKILL frontmatter、workflow/SKILL 内容治理和复审期限、交付物模板及追溯契约、端到端演练覆盖、目录与名称一致性、站内相对链接、导航/workflow 覆盖以及 Markdown 基础格式。

日常开发优先使用[统一的本地开发入口](docs/local-development.md)：

```sh
./bin/playbook setup
./bin/playbook check
```

Dependabot 每周为 Python 开发依赖和固定 SHA 的 GitHub Actions 创建更新 PR；更新仍须通过相同门禁并由人类审查后合入。

```sh
python3 -m pip install --requirement requirements-dev.txt
ruff check scripts tests skills/05-integration-validation/github-actions-bootstrap/scripts
ruff format --check scripts tests skills/05-integration-validation/github-actions-bootstrap/scripts
python3 -m unittest discover --start-directory tests
python3 scripts/check_repository.py
```

Pull Request 和推送到 `main` 时，[Repository checks](.github/workflows/repository-checks.yml) workflow 会执行同一组检查。
