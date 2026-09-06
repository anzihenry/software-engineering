# 10 分钟快速开始

本页帮助一个已有 GitHub 仓库采用生命周期自动化。它不会安装第一层研发知识，也不会自动发布、部署、回滚、批准变更或写入敏感事故内容。第一次采用优先使用当前稳定版本 `v1.1.0`；需要 `upgrade` 命令时等待包含该能力的正式版本，或仅在审查后使用完整 commit SHA。

## 1. 准备

需要 Python 3.14、Git、一个干净的目标仓库，以及已认证的 `gh`。`install` 只修改本地目标目录，不需要 GitHub token；`doctor` 读取 GitHub 状态，`bootstrap` 在显式确认后写入仓库设置。

下载并核验固定发布包：

```sh
mkdir -p /tmp/github-lifecycle-v1.1.0
cd /tmp/github-lifecycle-v1.1.0
gh release download v1.1.0 \
  --repo anzihenry/software-engineering \
  --pattern 'github-lifecycle.zip*'
shasum -a 256 --check github-lifecycle.zip.sha256
unzip github-lifecycle.zip -d package
```

不要用浮动 `main`、未知来源 ZIP 或未匹配的校验和代替固定发布包。

## 2. 选择 profile

| Profile | 适合情况 | 不会引入 |
| --- | --- | --- |
| `governance` | 需要结构化 PR、policy 和 main ruleset | 事故、复盘、发布 workflow |
| `incident` | 需要 SECURITY、普通事故、复盘和审计 | PR ruleset、发布 workflow |
| `release` | 只需要通用 Draft Release 候选 | PR ruleset、事故标签或 PVR |
| `full` | 新仓库或希望采用完整能力 | 无；它是三个较小 profile 的并集 |

已有成熟 CI 的仓库建议从 `governance` 或单项 profile 开始，不必为了采用本项目替换现有流程。

## 3. 选择 adapter

| Adapter | 本地检查入口 | 适用前提 |
| --- | --- | --- |
| `python` | requirements-dev + unittest | 根目录存在 `requirements-dev.txt` 与 `tests/` |
| `node` | `npm ci` + `npm run validate` | 根目录存在 `package.json` 与 lockfile |
| `swift` | `swift test` | 根目录是 Swift Package |
| `go` | `go test ./...` | 根目录存在 `go.mod` |
| `external` | 保留目标仓库自己的实现 | 已有 CI 能稳定产生 `validate` check |
| `custom` | 使用显式 adapter JSON | 内置约定与真实工具链不匹配 |

不要自动猜测语言。成熟项目优先选择 `external`，确认现有 CI 的 job/check 名稳定为 `validate`。

## 4. 预览并安装

以下示例选择 `governance` 和 `external`。先在发布包目录生成计划：

```sh
cd /tmp/github-lifecycle-v1.1.0/package
python3 -m scripts.github_lifecycle install \
  --target /absolute/path/to/target-repository \
  --repository OWNER/REPOSITORY \
  --default-branch main \
  --profile governance \
  --adapter external \
  --output /tmp/lifecycle-install-plan.json
```

检查计划没有 `conflict`，再使用同一来源和精确确认字符串应用：

```sh
python3 -m scripts.github_lifecycle install \
  --target /absolute/path/to/target-repository \
  --repository OWNER/REPOSITORY \
  --default-branch main \
  --profile governance \
  --adapter external \
  --no-dry-run \
  --confirmation install:OWNER/REPOSITORY
```

安装器只创建缺失文件或跳过相同文件；不同内容、符号链接和路径异常会停止，不会覆盖。

## 5. 用 PR 取得真实证据

在目标仓库审查并提交安装结果，通过 `gh pr create` 创建 PR。PR 进入 Ready 后，必须同时看到：

- 目标项目自己的稳定 `validate` check 成功。
- 新增的 `lifecycle-policy` check 成功。

不要在这两项真实 check 出现前把它们加入 ruleset。内置 adapter 会生成 `validate.yml`；使用 `external` 时由目标仓库继续提供该 check。

## 6. 诊断并引导 GitHub 设置

从目标仓库运行只读诊断，并传入仍处于 Open 状态的证据 PR：

```sh
cd /absolute/path/to/target-repository
python3 -m scripts.github_lifecycle doctor \
  --repository OWNER/REPOSITORY \
  --profile governance \
  --evidence-pr 123

python3 -m scripts.github_lifecycle bootstrap \
  --repository OWNER/REPOSITORY \
  --profile governance \
  --evidence-pr 123
```

第二条命令默认仍是 dry-run。复核计划后，才增加 `--no-dry-run --confirmation bootstrap:OWNER/REPOSITORY` 显式应用，再次运行 `doctor` 并要求健康。

## 完成条件

- 安装 PR 只包含选定 profile 和 adapter 的预期文件。
- `validate` 与 `lifecycle-policy` 对当前 head SHA 成功。
- `bootstrap` 真实执行前已审查 dry-run。
- 写后 `doctor` 健康，原有必需检查和发布策略没有被替换。
- 安装版本、包校验和、profile、adapter、PR 和检查链接已记录。

升级现有安装见 [`UPGRADING.md`](../UPGRADING.md)，版本能力见[兼容矩阵](version-compatibility.md)，完整命令和权限边界见 [GitHub 生命周期自动化](github-lifecycle-automation.md)。
