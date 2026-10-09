# Changelog

本文件记录面向采用者的能力变化。日期使用正式 Release 的 UTC 发布日期；仓库内部维护依赖仅在影响使用方式或兼容性时列出。

## [Unreleased]

### Added

- 文档治理第三阶段：增加目标项目 check/snapshot/gate、配置/独立评审 JSON 与可复用 CI 模板；行为测试覆盖交付失败场景，不修改安装器或替目标项目启用远端规则。
- 增加面向目标项目的双语文档规范、按需使用的文档/交付检查模板及接入说明；保留资产仓库边界和既有治理/追溯契约。
- 增加文档维护与独立交付验证 SKILL，将文档影响、英文同步、当前版本证据和非作者评审接入 harness 入口、八阶段 workflow、交付模板及合入/发布就绪要求；目标项目检查器和 CI 模板已提供，安装包保持不变。

### Changed

- 将第三层 GitHub 仓库治理实现拆分为调用、状态读取、ruleset 规划、诊断和显式写入模块；保留原导入门面、CLI、确认字符串、dry-run 默认值和权限边界。

## [v1.2.0] - 2026-09-06

仓库发布说明：[GitHub Lifecycle Automation v1.2.0](docs/releases/v1.2.0.md)。

### Added

- 安装时写入版本化 installation record，并提供基于固定新旧包的三方 `upgrade` 计划与安全应用。
- 使用真实 GitHub canary 验证 Python/full、Node/governance、Swift/release 和 Go/incident，以及 `v1.1.0` 到当前源码的升级链路。
- 增加 10 分钟快速开始、版本兼容矩阵、升级/恢复指南和可复用 Release notes。

### Changed

- README 首屏改为按采用目标、profile、adapter、验证和安全边界导航。

## [v1.1.0] - 2026-09-01

仓库发布说明：[GitHub Lifecycle Automation v1.1.0](docs/releases/v1.1.0.md)。

### Added

- 明确研发知识、GitHub 生命周期自动化、跨项目安装治理三层边界。
- 增加 `governance`、`incident`、`release`、`full` 四种安装 profile。
- 增加 Python、Node、Swift、Go 内置 adapter 和保留既有实现的 external/custom 路径。
- 增加 4 × 4 离线跨项目验收矩阵。
- 增加 Dependabot 与本地开发入口。

### Changed

- Dependabot PR 使用受限的低风险结构验证，但仍保留 `validate`、Action 完整 SHA 和危险 workflow 检查。
- 自动化 manifest 升级到 schema 3；schema 1 和 2 继续作为只支持 `full` 的 legacy bundle 读取。

## [v1.0.0] - 2026-08-27

仓库发布说明：[GitHub Lifecycle Automation v1.0.0](docs/releases/v1.0.0.md)。

### Added

- 首个稳定的 GitHub 生命周期自动化包。
- PR 生命周期 policy、风险条件证据和稳定 `lifecycle-policy` check。
- Draft Release 候选准备、普通事故状态流转、安全/隐私受限入口、复盘、改进行动和只读审计。
- 确定性 `package`、默认 dry-run 的 `install`、只读 `doctor` 和证据 PR 约束的 `bootstrap`。

[Unreleased]: https://github.com/anzihenry/software-engineering/compare/v1.2.0...HEAD
[v1.2.0]: https://github.com/anzihenry/software-engineering/compare/v1.1.0...v1.2.0
[v1.1.0]: https://github.com/anzihenry/software-engineering/compare/v1.0.0...v1.1.0
[v1.0.0]: https://github.com/anzihenry/software-engineering/releases/tag/v1.0.0
