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
3. 显式确认并应用安装，检查安装记录中的 profile、adapter 和不可变来源；再以 `auto` adapter 重跑，确认结果幂等且没有覆盖或冲突。
4. 使用同一资产内容模拟 `v1.1.0 → v1.2.0`，确认 `upgrade` 只更新安装记录、保持文件内容幂等，并在 16 个组合中延续原 adapter/profile。
5. 通过参数数组模拟 `run-adapter`，确认采用 adapter 声明的命令且不经过 shell 拼接。
6. 运行本地 `doctor`，确认安装健康；随后分别制造必需路径缺失和托管 workflow 漂移，确认诊断能够发现。
7. 对未配置的 GitHub 仓库快照生成 `bootstrap` 计划，确认写操作严格受 profile 边界约束。

此外，每个 profile 单独生成两次确定性 ZIP，要求内容摘要与 SHA-256 完全一致。全部验收由 `python3 -m unittest discover --start-directory tests` 和 `./bin/playbook check` 自动执行。

## 不在离线矩阵内的边界

矩阵不会调用真实语言工具链、访问网络或修改 GitHub。目标项目仍须在安装 PR 上运行自己的真实 `validate`，并在该 Open PR 同时产生成功的 `lifecycle-policy` 后，才能对需要 ruleset 的 profile 执行真实 `bootstrap`。

正式版本发布前，由[真实 GitHub canary](github-canary-validation.md)在受控合成仓库中完成四个代表组合、一次真实的新旧包升级、PR 两项稳定 check、dry-run `doctor/bootstrap`、显式应用和写后诊断。该 smoke 是外部状态验证，不由普通仓库 CI 自动创建、重置或清理测试仓库。

## P1 后端/Web 代表闭环

P1 在原 16 组合之外增加合成新后端、已有入口/CI/双语指南的成熟 Web，以及 GitHub canary 两者系统路径。每个项目均执行固定知识的真实读取、项目五类检查、逐条领域准入、HTTP/浏览器与本地制品交付/失败恢复；非作者另起任务重跑。它不扩展安装包、语言 adapter 或生产渠道支持，实际结果见[分步记录](harness-p1-validation.md)。

`scripts/p1_acceptance.py` 是内部隔离夹具准备器，不批准采用、不创建远端 PR、不发布独立状态。只接受干净固定知识 checkout 与完整旧/新提交，目标必须是尚不存在的新目录；成熟夹具保留原入口段、CI、双语指南和未知文件。已有真实项目应按采用规范合并入口，不将此合成准备器直接运行到项目目录。

```sh
python3 -m scripts.p1_acceptance --root /tmp/new-p1-trial \
  --harness /tmp/pinned-harness \
  --old-ref c8b47b6f53813a91308e171905a62750ba08d1fd \
  --new-ref eb674f606ba36b6b8e5b7da3c00c40b915c49f17
```

使用仓库固定 Python 3.14 环境，先将独立完整 checkout 固定到 new-ref；重跑另选目录。输出 setup.json 绑定项目 base/head/application_base、安装、旧新升级/同版重跑/冲突拒绝/回退和上游删除保留。上游删除用内容摘要绑定的受控合成包，不冒称已发布版本实际删除。准备成功之后仍须运行 `harness_adoption.py --run`、当前领域/渠道工具和非作者任务；仅有文件或 source 摘要不构成行为验收。

缺专项、旧 source/环境、原证据篡改或采集未完成须在领域读取节点阻塞；缺译文须在文档与真实 CI 节点阻塞；制品/目标漂移与健康失败须在渠道节点停止；规则/权限漂移须在受信读取节点复验。保留负例与修正后的当前报告，不覆盖旧报告、不改变候选 scope 掩盖平台缺口。实际远端规则不为负例而放宽，规则漂移可用明确标注的受控 API 数据验证，不能称实际设置变更。

每项目指标按独立 policy 摘要与 UTC 窗口复算，至少两次实际读取；短窗口 reader 耗时不等于 CI/业务性能，无独立阻塞样本时误阻塞比例为 null。原生辅助技术仅在非作者确认路径/语义/环境适用范围未变后限定复用，保留原执行 source/time；不能改为当前执行或扩为完整产品验收。
