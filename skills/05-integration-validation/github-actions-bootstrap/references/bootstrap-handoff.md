# Bootstrap 交接契约

`github-actions-bootstrap` 用这份契约把已经运行的 CI 证据交给 `github-repository-bootstrap`。交接记录用于限制后续远端写入范围，不是凭据文件，也不能替代 GitHub 的实时状态。

## 结构

```json
{
  "schema_version": 1,
  "repository": "owner/repository",
  "default_branch": "main",
  "bootstrap_pull_request": {
    "number": 12,
    "url": "https://github.com/owner/repository/pull/12",
    "head_ref": "codex/github-actions-bootstrap",
    "head_sha": "0123456789abcdef0123456789abcdef01234567"
  },
  "required_check": {
    "context": "validate",
    "integration_id": 15368,
    "conclusion": "success",
    "run_url": "https://github.com/owner/repository/actions/runs/123"
  },
  "delivery": {
    "mode": "ci",
    "environments": []
  }
}
```

## 约束

- `repository`、PR、head ref 与 head SHA 必须与 GitHub 实时读取结果一致。
- `required_check.context` 必须来自该 head SHA 上成功的 check-run `name`，`integration_id` 必须来自同一 check-run 的 `app.id`。
- `delivery.mode` 只能是 `ci`、`artifact` 或 `deployment`。只有 workflow 确实生成可追溯制品时使用 `artifact`；只有目标平台、身份、环境保护、健康验证和恢复动作均已落地时使用 `deployment`。
- `environments` 只列 workflow 实际引用的 GitHub Environment；每项记录名称、用途及是否需要保护规则或 secrets，但不记录 secret 值。
- 交接信息默认放在 PR 描述的 `GitHub bootstrap handoff` 折叠段中，避免为一次性运行状态提交仓库文件。需要机器读取时可使用临时 JSON 文件，任务结束后删除。

## 重新验证

消费方必须重新读取 PR 和 check-run。PR 已关闭未合并、head SHA 改变、检查不是成功状态、App 不一致或仓库不一致时，交接失效；返回 Actions 引导流程刷新证据，不能沿用旧记录。
