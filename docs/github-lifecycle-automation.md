# GitHub 生命周期自动化

本仓库将 PR、发布、普通事故和复盘编排逐步固化为可复制的 GitHub 原生自动化。GitHub 承载普通记录和控制状态；安全、隐私及取证敏感内容只保留受限系统标识，不进入普通 PR、Issue、Actions 日志或 Release。

按[项目三层边界](project-boundaries.md)，本页同时描述第二层“GitHub 生命周期自动化”及第三层“跨项目安装与治理工具”。前者执行仓库内生命周期规则，后者只负责打包、安装、诊断和仓库设置；两层不能替代第一层的研发知识与人工责任。

## 权限模型

- PR 校验和定时审计只读运行。
- 创建 Draft Release、事故状态流转和创建复盘必须由维护者显式触发 `workflow_dispatch`。
- 每个 job 只声明完成当前动作所需的权限；PR 代码不使用 `pull_request_target` 或写 token。
- 自动化只能检查记录结构、GitHub 状态和可追溯标识，不替代独立评审、专家判断或人类生产 Go/No-Go。

## 公共配置与版本

`.github/lifecycle-policy.json` 是版本为 1 的机器契约，定义默认分支、稳定检查名、发布所需检查、风险/严重度、复盘期限和标签。破坏性字段变化必须增加 `schema_version` 并提供迁移说明。

当前 PR 模板要求变更 ID、目的、范围和非目标、风险、验证、发布影响、恢复及关联记录。中高风险增加独立评审和系统证据；高风险增加设计、专项评审、数据恢复及人类 Go/No-Go 责任。

Draft PR 可以保留未完成项，`lifecycle-policy` 会给出警告但不阻塞；PR 进入 Ready 后，相同缺口会使检查失败。通过只表示结构完整，不证明链接内容或测试结论真实。

Dependabot PR 使用受限的自动低风险记录，不要求机器人生成面向人工变更的完整 PR 模板，也不获得无条件豁免。校验器要求作者同时满足固定登录名 `dependabot[bot]` 和 GitHub `Bot` 类型，分支以 `dependabot/` 开头、来自同一仓库并指向 policy 默认分支；工作流通过只读 `gh api --paginate --slurp` 提供完整文件清单，并与事件中的 `changed_files` 数量核对。

自动通道只允许 Python、Node、Swift 和 Go 的依赖 manifest/lock 文件。对 `.github/workflows/*.{yml,yaml}`，每个增删行必须是同一 Action 的完整 40 位 SHA 与精确 `vMAJOR.MINOR.PATCH` 注释替换，缺失或截断 patch、浮动 tag、文件重命名、trigger、权限、脚本及其他工作流逻辑变化全部失败。普通 `validate` 仍独立执行仓库测试、全量工作流危险触发器和 Action 固定检查；两项 required checks 必须同时成功。

## 发布候选与 Draft Release

`Prepare Draft Release` 只能通过 `workflow_dispatch` 运行，输入语义版本、完整 source SHA、风险等级、变更记录和摘要。Python 校验器要求版本符合 `vMAJOR.MINOR.PATCH`、SHA 可从 `main` 到达、配置中的 required checks 已成功，且同版本 tag 和 Release 尚不存在。

工作流默认 `dry_run: true`，只生成并上传保留 30 天的发布记录、候选清单、候选清单 JSON、自动化包及 SHA-256 校验和。实际创建要求将 `dry_run` 设为 false，并让确认字符串与版本完全相同；只有该 job 获得 `contents: write`，且只调用 `gh release create --draft`。相同版本使用 concurrency 串行且不会取消进行中的运行，也不会覆盖已存在候选。

Draft Release 不是生产 Go/No-Go。授权人核对 source SHA、附件、变更范围和恢复条件后，优先使用 `gh release edit` 明确发布；正式发布、部署、标签公开和回滚不属于当前自动化。

## 普通事故与安全入口

普通事故使用 Issue Form 登记 SEV1—SEV4、开始时间及时区、环境/范围、用户影响、已知事实、未知项、单一所有者、版本/发布关联和非敏感证据链接。提交者必须确认未包含凭据、个人信息、受限日志、取证内容或恶意载荷；已知安全/隐私风险应直接进入 [`SECURITY.md`](../SECURITY.md) 的受限入口。

`Transition Ordinary Incident` 只允许 `investigating → mitigating/recovered/escalated`、`mitigating → recovered/escalated`、`recovered → closed` 和关闭后的 `closed → investigating`。工作流默认 dry-run；实际变更要求确认 `incident-N`，每次追加操作者、时间、决定和 HTTPS 证据，并保持一个当前状态标签。每个 workflow run 使用稳定的 operation ID，按“转换记录、状态标签、Issue 开关状态”的顺序写入；失败后重跑同一 run 会读取转换标识并只补齐缺失步骤。三项均已一致时才视为 no-op；标签与 Issue 开关状态不一致时会生成公开的非敏感协调记录并修复状态。

若处理中发现安全或隐私风险，目标必须是 `escalated`。Python 会忽略普通决定和证据文本，只在公开记录保留安全字符组成的受限事件 ID，并引导到 `SECURITY.md`；后续安全、隐私、法律和取证内容不得回写普通 Issue。安全漏洞通过 GitHub Private Vulnerability Reporting 接收，隐私事件使用团队受限系统。

## 复盘、改进行动与只读审计

`Open Lifecycle Retrospective` 支持 `incident:N` 和 `release:vMAJOR.MINOR.PATCH`。事故须为 recovered/closed，或触发者明确确认已经稳定；Release 必须已正式发布且不能是 Draft/Prerelease。SEV1、SEV2、SEV3 分别按恢复锚点计算 7、14、30 天期限，SEV4 默认无强制期限，发布复盘为 30 天。

复盘使用 `<!-- lifecycle-source:... -->` 隐藏标识去重，发现已有记录时返回原 Issue 而不重复创建。正文固定包含事实时间线、当时可见信息、促成因素、防护有效性、不确定性和行动链接。独立改进行动 Issue Form 强制复盘反链、单一所有者、期限、完成定义、效果判据和观察窗口。

`Audit Lifecycle Records` 每周一 02:00 UTC 以及手动触发时只读运行。它通过分页 API 读取全部 Issue、全仓库 Issue 评论和 Release，以首次 `recovered`/`closed` 转换记录的时间计算事故复盘期限，不使用可能被后续编辑推迟的 Issue `updatedAt`。除缺失/未完成且逾期的复盘和行动外，审计还报告无效记录与重复来源；单条记录损坏不会中断其余扫描。审计只写 Actions summary 和 job 结论，不评论、不改标签、不关闭 Issue。

## 跨项目安装、诊断与引导

`automation/github-lifecycle-manifest.json` 使用 schema 3，将文件分为 `github-lifecycle` 和 `cross-project-governance` 两个互斥组件，并定义四个安装 profile。schema 1 和 2 的 legacy bundle 仍可读取，但只支持 `full`。第一层研发知识和本仓库内部支持面不进入 manifest。应先用固定 tag 或完整 commit SHA 检出本仓库，避免在未复核的浮动分支上安装。

| Profile | 本地能力 | `bootstrap` 远端治理 |
| --- | --- | --- |
| `governance` | PR 模板、policy、`lifecycle-policy` 门禁及共享工具 | Actions 默认只读、main ruleset、合并后删除分支；要求真实证据 PR |
| `incident` | SECURITY、事故表单、状态流转、复盘、行动和审计及共享工具 | Actions 默认只读、生命周期标签、Private Vulnerability Reporting；不要求证据 PR |
| `release` | policy、通用 Draft Release 及共享工具 | Actions 默认只读；不创建 ruleset、标签或 PVR，不要求证据 PR |
| `full` | 三个 profile 的并集；默认值，保持旧版安装行为 | 完整治理；ruleset 部分要求真实证据 PR |

profile 是可叠加采用的声明，不执行删除。由较小 profile 切换到 `full` 会补齐缺失文件；由 `full` 改用较小 profile 时，既有额外文件和 GitHub 设置会被保留，不再作为该 profile 的必需项或远端治理目标。`doctor` 仍会对仓库中实际存在的所有 workflow 执行危险触发器和 Action 固定 SHA 安全检查。`install`、`doctor` 和 `bootstrap` 必须使用同一个 profile。

### 跨语言适配层

安装 profile 决定“采用哪些生命周期能力”，语言 adapter 决定“目标项目怎样实现这些能力”。`python`、`node`、`swift`、`go` 四个内置 adapter 统一生成以下托管资产，但不要求四类项目复制同一种构建实现：

- `.github/lifecycle-adapter.json`：版本化声明 runner、工具链来源、必需路径、参数数组形式的本地检查命令、Dependabot 生态和发布候选制品保留期。
- `.github/workflows/validate.yml`：对外始终产生稳定的 `validate` job/check；Python 和 Node/Go 使用各自的 setup Action，Swift 使用 macOS runner。所有 Action 固定到完整提交 SHA，job 只授予 `contents: read`。
- `.github/dependabot.yml`：按语言使用 `pip`、`npm`、`swift` 或 `gomod`，并始终覆盖 `github-actions`。

适配器明确选择，不自动猜测语言。首次安装默认 `--adapter auto`：目标已有 `.github/lifecycle-adapter.json` 时继续使用该配置，否则等同 `external`，保留项目自己的检查与 Dependabot。选择内置 adapter 会把这些文件纳入安装冲突保护；已有同名但内容不同的文件不会被覆盖。成熟项目可继续使用 `external`，只需确保自己的 CI 产生稳定的 `validate` check。

内置约定分别是 Python 的 `requirements-dev.txt` + unittest、Node 的 `npm ci` + `npm run validate`、Swift Package Manager 的 `swift test`、Go module 的 `go test ./...`。这些是显式基线而非语言真理；命令、runner、必需路径或工具链版本不匹配时，应复制同一 schema 编写自定义配置，并通过 `--adapter custom --adapter-config /path/to/adapter.json` 安装。Dependabot 不是根目录单包结构时使用 `external` 保留项目现有配置。配置命令以参数数组执行，不经过 shell 拼接。

本地和 CI 使用同一个入口：

```sh
python3 -m scripts.github_lifecycle run-adapter \
  --config .github/lifecycle-adapter.json
```

`doctor` 会检查 adapter schema、必需路径以及三个托管文件是否缺失或漂移。由 Dependabot 提交的完整 Action SHA 与精确版本注释更新不会被视为结构漂移，触发器、runner、权限、步骤和命令的其他变化仍会报告。`release_artifact_retention_days` 只控制 Draft Release 候选上传制品的保留期，范围为 1—90 天，并受仓库、组织或企业的上限约束；它不改变正式 Release、tag、部署或回滚策略。

四种内置 adapter 与四种 profile 的 16 个组合由[跨项目验收矩阵](cross-project-acceptance.md)执行离线验收。矩阵覆盖安装、幂等、生成 YAML、adapter 命令入口、本地诊断、确定性打包和远端治理计划；目标仓库的真实工具链与 GitHub check 仍须在安装 PR 中验证。

三个命令的责任边界如下：

- `install` 只操作目标仓库的本地文件。默认 dry-run；只创建缺失文件，相同文件跳过，任何内容不同、目录占位或符号链接均记为冲突且不覆盖。
- `doctor` 只读检查本地安装及 GitHub 设置，包括目标仓库链接、默认分支、Action 固定 SHA、危险触发器、Actions 默认权限、标签、Private Vulnerability Reporting、默认分支有效规则和可选证据 PR。
- `bootstrap` 只配置 GitHub 仓库设置。它要求一个仍处于 Open 状态、目标为默认分支且已成功产生稳定检查的证据 PR；默认仅输出计划，真实写入还要求 `--no-dry-run` 和精确确认字符串。

在自动化源码检出目录先预览并安装本地文件：

```sh
python3 -m scripts.github_lifecycle install \
  --target /path/to/target-repository \
  --repository OWNER/REPOSITORY \
  --default-branch main \
  --profile governance \
  --adapter node

python3 -m scripts.github_lifecycle install \
  --target /path/to/target-repository \
  --repository OWNER/REPOSITORY \
  --default-branch main \
  --profile governance \
  --adapter node \
  --no-dry-run \
  --confirmation install:OWNER/REPOSITORY
```

安装完成后，在目标仓库中审查 adapter 命令、工具链、Dependabot 和发布保留期，再提交这些文件，推送功能分支并创建 PR。等 `validate` 和 `lifecycle-policy` 真实 check-run 成功后，使用该 Open PR 的编号诊断和预览远端设置：

```sh
python3 -m scripts.github_lifecycle doctor \
  --repository OWNER/REPOSITORY \
  --profile governance \
  --evidence-pr PR_NUMBER

python3 -m scripts.github_lifecycle bootstrap \
  --repository OWNER/REPOSITORY \
  --profile governance \
  --evidence-pr PR_NUMBER
```

确认计划没有 blocker 后再显式应用，并立即重新执行只读诊断：

```sh
python3 -m scripts.github_lifecycle bootstrap \
  --repository OWNER/REPOSITORY \
  --profile governance \
  --evidence-pr PR_NUMBER \
  --no-dry-run \
  --confirmation bootstrap:OWNER/REPOSITORY

python3 -m scripts.github_lifecycle doctor \
  --repository OWNER/REPOSITORY \
  --profile governance \
  --evidence-pr PR_NUMBER
```

所有 GitHub 读取和写入都通过参数化的 `gh`/`gh api` 执行。`doctor` 发现漂移时返回非零；`bootstrap` 遇到权限不足、检查 App 身份不唯一、bypass、目标条件不明、重复管理规则或其他 ruleset 重叠时拒绝写入。它只补缺失标签，不覆盖同名标签；更新托管 ruleset 时保留额外检查、未知规则和更严格的评审条件。

## 确定性自动化包

如需归档、离线审查或自行复制，可在同一个固定版本检出中运行：

```sh
python3 -m scripts.github_lifecycle package \
  --manifest automation/github-lifecycle-manifest.json \
  --profile full \
  --output /tmp/github-lifecycle.zip
```

命令生成所选 profile 的确定性 ZIP 和同名 `.sha256` 文件；拒绝未知 profile、重复路径、目录逃逸、符号链接和覆盖已有输出。`prepare-release` 使用 `--profile auto`，按 `full`、`release`、`incident`、`governance` 的顺序选择当前仓库中最大的完整安装，因此不会为切换 profile 改写工作流。若现有文件构成不完整或混合 profile，自动检测会失败而不会静默降级；应先用明确 profile 运行 `doctor`。目标仓库必须在复制后审查配置、权限、required checks 和安全报告入口，不把本仓库的角色或环境假设直接当作自身事实。

## 仓库启用顺序

1. 在 PR 中加入配置、模板、脚本和 `lifecycle-policy` 工作流，先观察真实 check-run。
2. check 名稳定且误报已处理后，才把它加入默认分支 ruleset；保留项目原有构建/测试检查。
3. 若新检查误阻塞，先从 ruleset 移除该检查，不删除既有质量门禁；修复后通过新 PR 再恢复。
4. 发布工作流合入后先对 `main` 上通过检查的完整 SHA 执行 dry-run；真实 Draft Release 仍需单独显式确认。
5. 事故表单和工作流合入后，用 `gh label create --force` 建立配置中的标签，并用 `gh api` 启用、再读取确认 Private Vulnerability Reporting；事故状态工作流先 dry-run 再执行写入。
6. 复盘和审计工作流合入后，先用标记 `automation:smoke` 的合成普通事故执行 dry-run，再完成恢复、复盘、行动和审计链路；关闭记录但保留为非敏感证据。

GitHub 仓库查询和设置统一优先使用 `gh` 或 `gh api`，并在变更前读取现状、变更后重新核验。
