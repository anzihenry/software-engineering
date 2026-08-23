# Coding Agent 编码规范

## 目标

让 Coding Agent 在 TypeScript 7、ArkTS、Python 3.14、Swift 6.2、Kotlin 2.4、Go 1.27、SQL、zsh 和 C++20 项目中按一致底线工作，同时尊重项目实际版本、SDK/API、方言和自动化配置。

## 结构

- [`language-coding-standards`](../skills/04-implementation-and-self-test/language-coding-standards/SKILL.md) 负责识别语言并按需加载通用和语言专项规则。
- 仓库根 [`AGENTS.md`](../AGENTS.md) 是本 playbook 的强制入口。
- [`templates/codex/AGENTS.md`](../templates/codex/AGENTS.md) 用于接入其他代码仓库；复制后补齐项目命令和局部覆盖。

## 接入层级

Codex 在工作前读取 `AGENTS.md`，并按全局、仓库根到当前目录的顺序合并；更靠近当前目录的规则优先。详细规范不应全部塞入 `AGENTS.md`，否则会占用指令预算并让无关语言进入每次任务上下文。

推荐采用：

1. 先通过团队的 SKILL/plugin 分发机制让 `language-coding-standards` 对目标 Coding Agent 可发现；若不安装，则把同等规范与项目一起提交并在 `AGENTS.md` 指向其真实路径。
2. 在全局 Codex home 的 `AGENTS.md` 中声明所有代码任务必须使用 `$language-coding-standards`。
3. 每个仓库根目录使用本仓库模板，填写 formatter、lint/type check、build 和 test 命令。
4. 仅在子目录确有不同工具链或安全边界时增加更近的 `AGENTS.md`/`AGENTS.override.md`。
5. 将可机械检查的风格规则固化到项目配置和 CI；`AGENTS.md` 保留路由、不可自动判断的约束及授权边界。

## 版本策略

- 列出的版本是新项目和升级目标，不授权 Agent 自动升级既有项目。
- 现有项目以版本文件、构建清单和 CI 镜像为准；不兼容时使用现有版本支持的写法并报告差异。
- ArkTS 语言能力跟随项目 DevEco/HarmonyOS SDK 与 API，不从 TypeScript 版本推导兼容性，也不授权 Agent 自动升级 SDK。
- SQL 必须由项目补充数据库方言和主版本。没有方言上下文时，只能给出标准 SQL 层面的实现，不假设 PostgreSQL/MySQL/SQLite 特性等价。
- TypeScript 7 不提供旧版编译器 API；依赖嵌入式 TypeScript API 的工具可能仍需 TypeScript 6 兼容路径，必须按项目工具链验证。

## 验证接入

- 可用 `codex --ask-for-approval never "Summarize the current instructions."` 检查全局与仓库规则是否加载。
- 可用 `codex --cd <subdir> --ask-for-approval never "Show which instruction files are active."` 检查子目录覆盖。
- 代码变更仍需通过项目 formatter、静态分析/type check、构建和测试；Agent 声明“遵守规范”不构成验证证据。

## 官方依据

- [OpenAI：Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- 各语言专项规范末尾列出对应官方语言和工具文档。
