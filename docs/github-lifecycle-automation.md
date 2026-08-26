# GitHub 生命周期自动化

本仓库将 PR、发布、普通事故和复盘编排逐步固化为可复制的 GitHub 原生自动化。GitHub 承载普通记录和控制状态；安全、隐私及取证敏感内容只保留受限系统标识，不进入普通 PR、Issue、Actions 日志或 Release。

## 权限模型

- PR 校验和定时审计只读运行。
- 创建 Draft Release、事故状态流转和创建复盘必须由维护者显式触发 `workflow_dispatch`。
- 每个 job 只声明完成当前动作所需的权限；PR 代码不使用 `pull_request_target` 或写 token。
- 自动化只能检查记录结构、GitHub 状态和可追溯标识，不替代独立评审、专家判断或人类生产 Go/No-Go。

## 公共配置与版本

`.github/lifecycle-policy.json` 是版本为 1 的机器契约，定义默认分支、稳定检查名、发布所需检查、风险/严重度、复盘期限和标签。破坏性字段变化必须增加 `schema_version` 并提供迁移说明。

当前 PR 模板要求变更 ID、目的、范围和非目标、风险、验证、发布影响、恢复及关联记录。中高风险增加独立评审和系统证据；高风险增加设计、专项评审、数据恢复及人类 Go/No-Go 责任。

Draft PR 可以保留未完成项，`lifecycle-policy` 会给出警告但不阻塞；PR 进入 Ready 后，相同缺口会使检查失败。通过只表示结构完整，不证明链接内容或测试结论真实。

## 发布候选与 Draft Release

`Prepare Draft Release` 只能通过 `workflow_dispatch` 运行，输入语义版本、完整 source SHA、风险等级、变更记录和摘要。Python 校验器要求版本符合 `vMAJOR.MINOR.PATCH`、SHA 可从 `main` 到达、配置中的 required checks 已成功，且同版本 tag 和 Release 尚不存在。

工作流默认 `dry_run: true`，只生成并上传保留 30 天的发布记录、候选清单、候选清单 JSON、自动化包及 SHA-256 校验和。实际创建要求将 `dry_run` 设为 false，并让确认字符串与版本完全相同；只有该 job 获得 `contents: write`，且只调用 `gh release create --draft`。相同版本使用 concurrency 串行且不会取消进行中的运行，也不会覆盖已存在候选。

Draft Release 不是生产 Go/No-Go。授权人核对 source SHA、附件、变更范围和恢复条件后，优先使用 `gh release edit` 明确发布；正式发布、部署、标签公开和回滚不属于当前自动化。

## 可复制自动化包

`automation/github-lifecycle-manifest.json` 列出公共配置、工作流、表单和脚本。使用固定 tag 或 commit SHA 检出本仓库后运行：

```sh
python3 -m scripts.github_lifecycle package \
  --manifest automation/github-lifecycle-manifest.json \
  --output /tmp/github-lifecycle.zip
```

命令生成确定性 ZIP 和同名 `.sha256` 文件；拒绝重复路径、目录逃逸、符号链接和覆盖已有输出。目标仓库必须在复制后审查配置、权限、required checks 和安全报告入口，不把本仓库的角色或环境假设直接当作自身事实。

## 仓库启用顺序

1. 在 PR 中加入配置、模板、脚本和 `lifecycle-policy` 工作流，先观察真实 check-run。
2. check 名稳定且误报已处理后，才把它加入默认分支 ruleset；保留项目原有构建/测试检查。
3. 若新检查误阻塞，先从 ruleset 移除该检查，不删除既有质量门禁；修复后通过新 PR 再恢复。
4. 发布工作流合入后先对 `main` 上通过检查的完整 SHA 执行 dry-run；真实 Draft Release 仍需单独显式确认。

GitHub 仓库查询和设置统一优先使用 `gh` 或 `gh api`，并在变更前读取现状、变更后重新核验。
