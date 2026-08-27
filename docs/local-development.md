# 本地开发入口

仓库以 Python 3.14、`requirements-dev.txt` 和 `pyproject.toml` 为可执行开发基线。激活目标虚拟环境后，在仓库根目录运行统一入口：

```sh
./bin/playbook setup
./bin/playbook check
```

入口根据自身位置解析仓库根目录；从其他目录调用时可以使用它的绝对路径。

`setup` 安装固定版本的开发依赖；`check` 按 CI 相同顺序执行 Ruff 静态检查、Ruff 格式检查、全部单元测试和仓库自检。入口在任一步失败时立即返回该命令的非零状态，不掩盖后续门禁。

需要缩小反馈范围时可以分别运行：

```sh
./bin/playbook lint
./bin/playbook format-check
./bin/playbook format
./bin/playbook test
./bin/playbook repository
```

`format` 会修改 Python 文件，其余命令只读。默认使用 `python3`；需要指定已创建的解释器时设置项目专用变量，例如：

```sh
PLAYBOOK_PYTHON=/path/to/venv/bin/python ./bin/playbook check
```

## 依赖与 Action 更新

Dependabot 每周一 UTC 03:00 后分别检查根目录的 Python 开发依赖和全部 GitHub Actions。minor/patch 更新按生态合并成小批次，major 更新保持独立 PR；Dependabot 只创建或 rebase PR，不自动合入。

远端 Action 必须继续固定到完整 40 位提交 SHA，并在行尾记录精确版本，例如：

```yaml
uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
```

审查更新 PR 时，应确认 SHA 对应官方仓库的声明 tag，阅读破坏性变化和运行时迁移说明，并要求 `validate` 与 `lifecycle-policy` 对当前 PR head 成功。依赖更新失败时修复或关闭该更新 PR，不降低检查、改用浮动 tag 或绕过 main ruleset。
