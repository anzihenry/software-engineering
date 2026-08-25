# Bootstrap 收口

仅在 `github-repository-bootstrap` 消费 `$github-actions-bootstrap` 交接或准备合并首次 CI PR 时读取。本流程提供一次受限的“先有 check、再保护默认分支”闭环，不授予日常自动合并权限。

## 校验交接

根据 [Actions bootstrap 交接契约](../../github-actions-bootstrap/references/bootstrap-handoff.md) 读取字段，并用 GitHub 实时响应逐项验证：

1. 仓库全名与当前目标一致，默认分支仍一致。
2. PR number/url 指向该仓库，状态为 open，base 是默认分支。
3. PR 当前 `headRefName` 和 `headRefOid` 分别等于交接的 head ref/head SHA。
4. 该 head SHA 上存在交接指定 `context` 的成功 check-run，其 `app.id` 等于 `integration_id`。
5. 交付模式和 environments 与 PR 中实际 workflow diff 一致。

任何一项不一致都使交接失效。不要根据相似分支名、旧 SHA 或旧成功运行自动修补交接。

## 设置与合并顺序

1. 先应用并重新验证 Actions 默认权限、目标 environments、strict required-check ruleset 和 `delete_branch_on_merge=true`。
2. 重新读取 bootstrap PR 的 mergeability、review decision、最新 head SHA 和全部 required checks。strict 规则要求分支落后时，更新该分支并让最新 SHA 重跑，而不是旁路。
3. 展示 PR number/title/url、精确 head SHA、合并方式和当前 required checks，单独请求用户授权合并这一份 PR。
4. 仅合并交接记录中的 PR；不使用管理员 bypass，不批准自己的 review，不启用会影响其他 PR 的 auto-merge。
5. 读取合并提交 SHA，等待该 SHA 在默认分支上的 `validate` 成功。PR head 的成功不能替代这一步。
6. 确认远端 head ref 因仓库设置自动删除。若仍存在，先确认 PR 已合并且 ref 未被复用，再请求单独删除授权。
7. 本地分支只在不是当前分支、没有未推送提交、且上游确实为已删除的同名 bootstrap ref 时删除；否则给出安全的人工清理动作。

## 完成语义

可以分别报告“仓库治理已配置”和“bootstrap 已收口”。只有默认分支合并后 CI 成功、远端删除行为已验证、以及适用的本地分支已安全清理时，才报告两者全部完成。任何失败都保留准确的 PR、SHA、设置和分支状态，不回滚已验证的安全设置，也不扩大权限解阻。
