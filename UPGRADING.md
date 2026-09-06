# Upgrading GitHub Lifecycle Automation

升级命令以固定的新旧发布包和目标仓库当前文件做三方比较。它只自动修改仍与可信旧基线一致的文件；不会覆盖本地定制、自动删除上游移除项、切换 adapter、缩小 profile 或执行 GitHub 设置写入。

当前稳定版 `v1.2.0` 首次提供 `upgrade` 命令。该命令从新版本工具运行，以固定的 `v1.0.0` 或 `v1.1.0` 发布包建立旧基线；旧版本本身不需要包含升级代码。

## 升级前

1. 阅读[版本兼容矩阵](docs/version-compatibility.md)和 [CHANGELOG](CHANGELOG.md)。
2. 确认目标仓库工作区干净，并保留可恢复的 Git 提交或分支。
3. 从 GitHub Release 下载官方旧包、新包及各自 `.sha256`，分别核验摘要。
4. 使用安装时相同的 repository、默认分支、profile 和 adapter；升级不会替你推断迁移。
5. 不要从浮动分支、重新打包的目录或未知 ZIP 建立旧基线。

## 从 v1.1.0 升级

先只生成计划：

```sh
python3 -m scripts.github_lifecycle upgrade \
  --from-package /path/to/github-lifecycle-v1.1.0.zip \
  --to-package /path/to/github-lifecycle-v1.2.0.zip \
  --target /absolute/path/to/target-repository \
  --repository OWNER/REPOSITORY \
  --default-branch main \
  --from-ref v1.1.0 \
  --to-ref v1.2.0 \
  --profile governance \
  --output /tmp/lifecycle-upgrade-plan.json
```

`v1.1.0` 没有 installation record。工具会把官方旧包作为候选基线，只有目标中的旧托管文件逐项匹配时才允许应用，并生成新的 `.github/lifecycle-installation.json`。

## 从 v1.0.0 升级

命令相同，但将旧包和来源改为 `v1.0.0`，并保持其 legacy `full` 来源：

```sh
python3 -m scripts.github_lifecycle upgrade \
  --from-package /path/to/github-lifecycle-v1.0.0.zip \
  --to-package /path/to/github-lifecycle-v1.2.0.zip \
  --target /absolute/path/to/target-repository \
  --repository OWNER/REPOSITORY \
  --default-branch main \
  --from-ref v1.0.0 \
  --to-ref v1.2.0 \
  --from-profile full \
  --profile full \
  --output /tmp/lifecycle-upgrade-plan.json
```

不要在同一次升级中把 `v1.0.0` 拆成较小 profile。先按 `full` 建立可信的新版本记录，再把 profile 调整作为独立变更审查；额外文件不会被隐式删除。

## 理解计划

| 分类 | 是否自动写入 | 处理方式 |
| --- | --- | --- |
| `unchanged` | 无需写入 | 内容已是新版本目标，保留 |
| `create` | 可以 | 新版本新增且目标路径不存在 |
| `safe-update` | 可以 | 目标仍与旧摘要完全一致，可替换为新内容 |
| `local-modification` | 阻止 | 比较本地定制与新版本，决定保留、采用上游或人工合并后重新规划 |
| `removed-upstream` | 不删除、不阻止 | 文件保留，但不再写入新的托管记录；另开删除变更处理 |
| `conflict` | 阻止 | 修正来源、路径、符号链接、记录、profile 或摘要问题后重新规划 |

不得通过修改计划 JSON、伪造 installation record 或临时移走冲突文件来绕过分类。

## 应用与验证

计划没有 blocker 后，使用与计划完全相同的参数，并提供绑定仓库和版本的确认字符串：

```sh
python3 -m scripts.github_lifecycle upgrade \
  --from-package /path/to/github-lifecycle-v1.1.0.zip \
  --to-package /path/to/github-lifecycle-v1.2.0.zip \
  --target /absolute/path/to/target-repository \
  --repository OWNER/REPOSITORY \
  --default-branch main \
  --from-ref v1.1.0 \
  --to-ref v1.2.0 \
  --profile governance \
  --no-dry-run \
  --confirmation upgrade:OWNER/REPOSITORY:v1.1.0:v1.2.0
```

应用前工具会重新核对目标摘要；计划后发生变化会停止。写入中失败会回滚本次已经创建或替换的文件，但不会替代 Git 提交、备份或目标项目自己的恢复机制。

随后在目标仓库运行本地检查和只读诊断：

```sh
python3 -m scripts.github_lifecycle run-adapter \
  --config .github/lifecycle-adapter.json

python3 -m scripts.github_lifecycle doctor \
  --repository OWNER/REPOSITORY \
  --profile governance
```

把升级放入独立 PR，等待 `validate` 与 `lifecycle-policy` 对同一 head SHA 成功。只有 `doctor` 健康且人工确认目标项目发布/恢复策略未被替换，才完成升级。

## 恢复与重试

- Dry-run 失败：不产生目标写入，修正 blocker 后重新生成完整计划。
- 应用前状态变化：保持新变化，丢弃旧计划并重新运行；不要强制覆盖。
- 应用中异常：检查工具回滚结果和 `git status`，用目标仓库的 Git 分支恢复，再重新规划。
- 合入后发现问题：优先回退升级 PR 或发布前滚修复；不要覆盖同一正式 tag 或 Release 资产。
- 需要降级：当前没有自动降级命令。根据目标仓库的安装记录和 Git 历史设计独立反向迁移，并重新通过 PR 门禁。
