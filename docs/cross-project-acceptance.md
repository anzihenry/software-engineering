# 跨项目验收矩阵

跨项目治理工具以 4 种内置语言 adapter 与 4 种安装 profile 的笛卡尔积作为离线验收基线，共 16 个组合。矩阵验证安装与治理契约，不声称替代目标项目自己的编译、测试、人工评审或真实 GitHub 证据 PR。

| Adapter \ Profile | `governance` | `incident` | `release` | `full` |
| --- | --- | --- | --- | --- |
| Python | 验收 | 验收 | 验收 | 验收 |
| Node | 验收 | 验收 | 验收 | 验收 |
| Swift | 验收 | 验收 | 验收 | 验收 |
| Go | 验收 | 验收 | 验收 | 验收 |

权威用例清单位于 [`tests/fixtures/github-lifecycle-acceptance-matrix.json`](../tests/fixtures/github-lifecycle-acceptance-matrix.json)。仓库自检要求 adapter、profile 与 16 个组合完整且无重复；新增或删除 adapter/profile 时必须同步更新矩阵和测试。

## 每个组合的自动验收

每个组合在独立临时仓库中执行以下验证：

1. 建立该语言最小必需路径，运行 `install` 计划并确认所有目标文件都是新增项。
2. 解析全部生成的 YAML，检查 profile 工作流边界、稳定 `validate` job、runner、Dependabot 生态和完整 SHA Action。
3. 显式确认并应用安装，再以 `auto` adapter 重跑，确认结果幂等且没有覆盖或冲突。
4. 通过参数数组模拟 `run-adapter`，确认采用 adapter 声明的命令且不经过 shell 拼接。
5. 运行本地 `doctor`，确认安装健康；随后分别制造必需路径缺失和托管 workflow 漂移，确认诊断能够发现。
6. 对未配置的 GitHub 仓库快照生成 `bootstrap` 计划，确认写操作严格受 profile 边界约束。

此外，每个 profile 单独生成两次确定性 ZIP，要求内容摘要与 SHA-256 完全一致。全部验收由 `python3 -m unittest discover --start-directory tests` 和 `./bin/playbook check` 自动执行。

## 不在离线矩阵内的边界

矩阵不会调用真实语言工具链、访问网络或修改 GitHub。目标项目仍须在安装 PR 上运行自己的真实 `validate`，并在该 Open PR 同时产生成功的 `lifecycle-policy` 后，才能对需要 ruleset 的 profile 执行真实 `bootstrap`。

正式版本发布前，应至少选择一个受控测试仓库完成 GitHub smoke：安装所选组合、推送 PR、核验两项稳定 check、dry-run `doctor/bootstrap`、显式应用并再次运行只读 `doctor`。该 smoke 是外部状态验证，不由普通仓库 CI 自动创建或清理测试仓库。
