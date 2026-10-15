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

## 端到端接入能力边界

生成器schema1仅基础CI模板，未独立配置每次功能合入前后端到端、逐合入版本保留/补跑或数据隔离。采用[阶段05](../../../../docs/workflows/05-integration-validation.md)时，先发现真实端到端命令与环境，按项目受控workflow接通PR/实际main版本验证，不能直接把基础CI的ref级取消策略当作逐次合入端到端保障；已取消必须补跑指定对象。模板生成/YAML通过不能证明这些平台行为已实现，保留实际正反例和限制。
