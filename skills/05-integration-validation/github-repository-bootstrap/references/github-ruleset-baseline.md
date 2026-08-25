# GitHub 仓库设置基线

仅在执行 `github-repository-bootstrap` 的 GitHub 远端发现、规划、写入或验证时读取本参考。API 字段和套餐能力可能变化；执行前以 GitHub 当前 REST 文档和目标仓库实际响应为准。

## 发现

使用 `gh` 的当前认证 host 和仓库上下文，至少读取：

- 仓库元数据：默认分支、`delete_branch_on_merge`、可见性和可用合并方式。
- `GET /repos/{owner}/{repo}/actions/permissions/workflow`：Actions 默认 token 权限与 workflow 是否可批准 PR。
- `GET /repos/{owner}/{repo}/environments` 及目标 environment 详情：已有环境、保护、分支/tag policy 和关联部署。
- `GET /repos/{owner}/{repo}/rulesets`：仓库级 ruleset 列表。
- `GET /repos/{owner}/{repo}/rules/branches/{branch}`：默认分支的有效规则。
- `GET /repos/{owner}/{repo}/branches/{branch}/protection`：仍可能同时生效的传统 branch protection；`404 Branch not protected` 只表示没有传统规则，不代表没有 ruleset。
- `GET /repos/{owner}/{repo}/commits/{sha}/check-runs`：成功 check-run 的 `name`、`app.id`、head SHA 和详情链接。

GitHub Actions 的 required-check context 是 job/check-run 名。Reusable workflow 使用组合后的 job 名；workflow 显示名、事件名和矩阵不是 required check 的身份。

## Actions 默认权限

设置仓库内未显式声明权限的 `GITHUB_TOKEN` 默认值：

```text
PUT /repos/{owner}/{repo}/actions/permissions/workflow
{
  "default_workflow_permissions": "read",
  "can_approve_pull_request_reviews": false
}
```

这不会覆盖 workflow/job 中显式声明的 `permissions`。写入前检查现有 workflow 是否依赖隐式写权限；应优先把所需权限明确放到最小 job，而不是维持仓库级宽权限。组织策略可能强制更严格的值，仓库不能放宽组织限制。

## Environments

用 `PUT /repos/{owner}/{repo}/environments/{environment_name}` 幂等创建或更新交接中明确列出的 environment。保护规则、required reviewers、等待时间和 deployment branch policy 受仓库可见性与套餐能力影响；先读取能力与现状，再只提交用户确认的字段。

- `ci` 模式默认不创建 environment。
- `artifact` 只有在 workflow 实际使用 environment 控制制品发布时才创建。
- `deployment` 按交接列出的 staging/production 名称配置；production 默认需要明确的人类保护决策，但不能在套餐不支持时声称已实现审批。
- 不通过 environment API 写入 secret 值，不删除未知保护规则，不把 environment 名称当作已经部署的证据。

## 仓库设置

开启合并后自动删除远端 head branch：

```text
PATCH /repos/{owner}/{repo}
{"delete_branch_on_merge": true}
```

该设置不追溯删除此前已合并的分支。历史分支必须先关联 PR 并确认其状态为 `MERGED`，再按用户明确授权逐个清理。

## Required-check ruleset

创建仓库级 ruleset 使用 `POST /repos/{owner}/{repo}/rulesets`；更新本 SKILL 已管理的 ruleset 使用其 ID 调用 `PUT /repos/{owner}/{repo}/rulesets/{ruleset_id}`。不要用创建新规则代替对同一职责规则的幂等更新。

最小 payload 结构：

```json
{
  "name": "main required checks",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": {
    "ref_name": {
      "include": ["~DEFAULT_BRANCH"],
      "exclude": []
    }
  },
  "rules": [
    {
      "type": "required_status_checks",
      "parameters": {
        "required_status_checks": [
          {
            "context": "<successful check-run name>",
            "integration_id": 12345
          }
        ],
        "strict_required_status_checks_policy": true,
        "do_not_enforce_on_create": true
      }
    }
  ]
}
```

`integration_id` 必须来自目标仓库实际 check-run 的 `app.id`，示例数字 `12345` 只展示字段类型，不得复制为配置值。若 App 尚未在该仓库提供过对应检查，先运行可信 workflow；不要退化为允许任意身份提供同名状态，除非用户明确接受该风险。

## 验证

写入后重新读取并确认：

1. ruleset `enforcement=active`，引用条件命中 `~DEFAULT_BRANCH`。
2. Actions 默认 token 返回 `read`，`can_approve_pull_request_reviews=false`；显式 workflow 权限仍符合设计。
3. 目标 environments 存在，保护和 deployment branch policy 与计划一致；不存在未声明的虚假部署结论。
4. required check 的 context、`integration_id` 和 strict 状态与计划一致。
5. `bypass_actors` 与用户选择一致，并报告当前身份是否可旁路。
6. 默认分支有效规则包含相同 required check，且分支元数据显示 `protected=true`。
7. 仓库元数据返回 `delete_branch_on_merge=true`。

需要证明端到端行为时，在功能分支创建最小 PR，让目标 check 对 PR head 实际运行；不要通过失败推送或管理员旁路测试生产仓库规则。

## 安全边界

- 不输出 `gh auth token`，不在命令行、日志、临时仓库文件或 PR 中保存 token。
- ruleset、branch protection 和组织规则会叠加；不得因仓库级请求成功就声称其他规则已被替换。
- 不使用空检查列表启用 strict，不创建尚未出现过的 required context，也不删除来源不明的 ruleset。
- 不把 Actions 默认 token 设为 `write`，不允许 workflow 创建或批准 PR review，除非独立用例明确要求、审计现有 workflow 并获得授权。
- 不覆盖 environment secrets，不为尚未存在的部署 workflow 创建看似受保护但从未被使用的 environment。
- 完全免逐仓库配置需要组织级 ruleset；只有目标仓库属于合适的组织且套餐支持时才提出该方案，并将其作为独立、明确授权的组织治理变更。
