# 版本兼容矩阵

本页描述发布包之间可验证的兼容关系，不构成支持时限或服务等级承诺。采用时优先选择最新稳定版本；旧版本保留为可复现基线和升级来源，不会自动获得新能力。

## 发布版本

| 版本 | 状态 | Manifest | Profile | Adapter | Installation record | `upgrade` |
| --- | --- | --- | --- | --- | --- | --- |
| `v1.0.0` | 可复现旧基线 | schema 1 | 仅 `full` | 仅保留项目现有实现 | 无 | 无 |
| `v1.1.0` | 可复现旧基线 | schema 3 | `governance`、`incident`、`release`、`full` | Python、Node、Swift、Go、external/custom | 无 | 无 |
| `v1.2.0` | 当前稳定版 | schema 3 | 同 `v1.1.0` | 同 `v1.1.0` | 有 | 有；已验证从 `v1.0.0`、`v1.1.0` 升级 |
| `main` | 下一版本开发线，不视为稳定发布 | 以仓库内容为准 | 以仓库内容为准 | 以仓库内容为准 | 以仓库内容为准 | 以仓库内容为准 |

schema 1 和 2 可以被当前读取器作为 legacy bundle 读取，但只支持 `full`。schema 3 定义两个互斥组件和四种安装 profile。manifest schema 描述包结构，不等同于 Git tag 或 lifecycle policy schema。

## 升级关系

| 来源 | 目标 | 支持方式 |
| --- | --- | --- |
| `v1.0.0` | `v1.2.0` | 显式提供官方旧包和新包；无安装记录时要求所有旧托管文件与旧包逐项一致 |
| `v1.1.0` | `v1.2.0` | 同上；保留原 profile 和 adapter，生成新 installation record |
| 含 installation record 的版本 | 更新版本 | 根据安装时摘要三方比较，只自动执行 `create`、`safe-update`、`unchanged` |
| 任意版本 | 更旧版本 | 不支持自动降级；使用独立恢复方案或经审查的反向迁移 |

`local-modification` 与 `conflict` 会阻止写入；`removed-upstream` 会保留在目标仓库中但退出新托管记录。切换 adapter、缩小 profile 或删除旧文件不是升级命令的隐式行为。

## 语言适配基线

| Adapter | 已验证运行环境 | 依赖生态 | 稳定 check |
| --- | --- | --- | --- |
| Python | Python 3.14 / `ubuntu-latest` | pip + GitHub Actions | `validate` |
| Node | Node 24 / `ubuntu-latest` | npm + GitHub Actions | `validate` |
| Swift | Swift Package / `macos-15` | Swift + GitHub Actions | `validate` |
| Go | `go.mod` 工具链 / `ubuntu-latest` | gomod + GitHub Actions | `validate` |
| external/custom | 由目标仓库声明并验证 | 由目标仓库维护 | 必须稳定为 `validate` |

内置 adapter 是可工作的基线，不代表所有项目布局。monorepo、非根目录包、自定义构建系统或不同 runner 应使用 external/custom，不应为了匹配本矩阵替换项目事实。

## GitHub 能力边界

- `install` 只处理本地文件；`doctor` 只读；`bootstrap` 默认 dry-run 并要求精确确认字符串。
- `governance` 和 `full` 的 ruleset 配置需要一个 Open 证据 PR，其中 `validate` 与 `lifecycle-policy` 已对当前 head SHA 成功。
- Rulesets、Private Vulnerability Reporting 和 Actions 设置的可用性仍受目标仓库可见性、GitHub 套餐和调用者权限约束。
- 正式 Release、部署、回滚、高风险批准和敏感事故存储不在自动化兼容承诺内。

具体迁移命令和冲突恢复见 [`UPGRADING.md`](../UPGRADING.md)。真实平台证据见 [GitHub canary 验收](github-canary-validation.md)。
