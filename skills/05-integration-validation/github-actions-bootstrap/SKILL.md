---
name: github-actions-bootstrap
metadata:
  owner: quality-lead
  scope: "Lifecycle phase 5: integration validation"
  status: active
  review_by: "2027-02-26"
description: "为新建或尚未接入自动化的 GitHub 仓库建立可重复的 Actions CI/CD 基线：发现项目真实门禁，生成固定 `validate` check 的安全 CI，按已有交付能力选择 ci/artifact/deployment 模式，并用首次 PR 自动运行产出仓库治理所需的可信交接证据；适用于初始化 Actions，而非解释单次 CI 失败或执行日常发布。"
---

# GitHub Actions 初始化

把项目已经能够在本地确定执行的质量命令接入 GitHub Actions，并通过首次 PR 自动产生真实 check-run。此 SKILL 负责 workflow 设计、实现、验证和交接；不修改 required-check ruleset 等仓库治理设置，也不虚构项目尚未具备的部署能力。

## 输入

- 目标仓库、默认分支及 GitHub Actions 可用性。
- 项目提交的工具链版本、依赖安装方式、格式化、静态分析、构建和测试命令。
- 期望的交付模式：仅 CI、构建制品或真实部署；未指定时从现有项目能力选择最低真实模式。
- 已有 workflow、环境、secrets/variables 名称及发布/恢复约束。

设计交付层级时读取 [CI/CD 模式与边界](references/cd-modes.md)。需要生成 CI 主 workflow 时读取 [CI 计划与生成器](references/ci-plan-schema.md)。准备后续仓库设置交接时读取 [Bootstrap 交接契约](references/bootstrap-handoff.md)。

## 工作方式

1. **发现项目标准**：读取 `AGENTS.md`、依赖锁文件、构建脚本、formatter/linter/type checker/test 配置和现有 CI；实际执行项目规定的本地门禁。不能从语言生态惯例猜测命令，也不静默升级工具链或新增生产依赖。
2. **选择真实交付模式**：默认从 `ci` 开始；只有存在确定性构建物时选择 `artifact`，只有目标平台、短期身份、环境保护、健康验证和恢复动作均明确时选择 `deployment`。把缺失信息列为后续升级条件。
3. **定义稳定检查契约**：CI workflow 在 `pull_request` 和默认分支 `push` 上触发，固定汇总 job ID 与显示名为 `validate`。不要用顶层路径过滤跳过整个 required workflow；矩阵或专项 job 的结果必须汇总到稳定 `validate`。
4. **设计最小权限执行**：顶层默认 `contents: read`，配置 PR concurrency、取消旧运行和 job timeout。禁止用 `pull_request_target` 执行 PR 代码；所有远端 actions 固定完整提交 SHA，并从官方仓库或可信发布记录核对版本。
5. **生成和审查 workflow**：把已确认的命令与固定 action SHA 写入临时 JSON 计划，用 `scripts/render_workflow.py` 生成 CI。若已有 workflow，先比较职责、触发器和 check 名，优先最小更新；不得未经确认覆盖未知自动化。artifact/deployment workflow 根据真实平台单独设计。
6. **本地验证**：解析全部 workflow YAML，运行 formatter/linter/build/tests 及仓库自检，审查权限、事件、表达式、缓存键、secret 边界、超时和失败传播。报告本地无法证明的 runner 或平台行为。
7. **创建首次 PR**：在 `codex/` 主题分支提交最小变更并创建 PR；依赖 `pull_request` 事件自动运行 CI，不要求用户先手动运行。workflow 尚未进入默认分支时不把 `workflow_dispatch` 当作首次验证入口。
8. **验证真实运行**：等待当前 PR head SHA 上名为 `validate` 的 check-run 成功；读取其 `name`、`app.id`、head SHA 和 run URL。失败则修复原分支并等待最新 SHA，不沿用旧运行。
9. **输出受限交接**：按交接契约记录仓库、默认分支、PR/head、成功 check/App、交付模式和 environments。交给 `$github-repository-bootstrap` 配置远端治理；本 SKILL 不自行创建 ruleset 或合并 PR。

## CI 契约

| 项目 | 必须满足 |
| --- | --- |
| 触发器 | `pull_request` 与默认分支 `push`；需要 merge queue 时增加 `merge_group` |
| required context | 固定 job/check 名 `validate`，对所有 PR 始终产生结论 |
| 权限 | 顶层显式最小权限；部署身份仅授予部署 job |
| 供应链 | 远端 action 固定完整提交 SHA，依赖安装尊重锁文件 |
| 并发 | 同一 PR/ref 取消旧运行，结论只对应最新 head SHA |
| 失败语义 | 不用 `continue-on-error`、空命令或占位部署掩盖门禁失败 |
| 交付声明 | `ci`、`artifact`、`deployment` 三选一，只报告已真实验证的能力 |

## 输出格式

```markdown
## GitHub Actions 初始化结果
- 仓库、默认分支与项目标准：
- CI workflow、触发器与固定 check：
- 权限、action pins、concurrency 与 timeout：
- 本地验证及限制：
- Bootstrap PR、head SHA 与运行链接：
- 成功 check context 与 App ID：
- 交付模式、environments 与未满足的升级条件：
- 交给 $github-repository-bootstrap 的 handoff：
```

## 停止条件

- 无法确认项目真实门禁或本地基础检查失败时，不创建声称可用的 CI。
- 现有 workflow 职责冲突、所需 secrets/环境未知或远端 action 来源无法核实时，保持最小 CI 或停止相应交付层写入。
- PR 最新 head SHA 上没有成功的 `validate` check-run 时，不输出可供 required check 使用的完成交接。
- 只有 CI workflow、本地验证、首次 PR 运行和交接证据均对应同一提交时才报告 Actions 引导完成。
