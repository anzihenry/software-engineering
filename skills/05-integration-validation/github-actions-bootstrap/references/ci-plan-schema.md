# CI 计划与生成器

`scripts/render_workflow.py` 从 JSON 计划确定性生成 `.github/workflows/ci.yml`。生成器只负责稳定 CI 主门禁；artifact/deployment workflow 必须按 [CI/CD 模式](cd-modes.md) 的真实目标另行设计和验证。

## 示例计划

```json
{
  "schema_version": 1,
  "workflow_name": "CI",
  "default_branch": "main",
  "runner": "ubuntu-latest",
  "timeout_minutes": 15,
  "merge_group": false,
  "steps": [
    {
      "name": "Check out repository",
      "uses": "actions/checkout@0123456789abcdef0123456789abcdef01234567"
    },
    {
      "name": "Run project checks",
      "run": "./scripts/check"
    }
  ]
}
```

每个 step 必须且只能提供 `uses` 或 `run`。远端 action 的 `uses` 必须固定到完整 40 位十六进制提交 SHA；仓库内以 `./` 开头的 local action 可直接使用。`with` 仅用于 action step，`env` 可用于两类 step，值必须是字符串。

先把计划写到任务专用临时目录，然后运行：

```sh
python3 skills/05-integration-validation/github-actions-bootstrap/scripts/render_workflow.py \
  --plan /tmp/project-ci-plan.json \
  --output .github/workflows/ci.yml
```

已有输出默认拒绝覆盖。只有读取并比较现有 workflow、确认该文件由本次计划管理后才传 `--force`。生成后仍要执行 YAML 解析、项目本地门禁，并审查 `git diff`；生成器不判断命令是否足以覆盖项目风险。
