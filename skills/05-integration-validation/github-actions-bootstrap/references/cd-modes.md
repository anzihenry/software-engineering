# CI/CD 模式与边界

根据项目已经存在的交付能力选择最低但真实的模式，不用空壳 deploy job 把 CI 包装成 CD。

## `ci`

适用于尚未确定发布平台或只需要 PR 质量门禁的仓库。workflow 在 PR 和默认分支 push 上运行，固定汇总 job/check 名为 `validate`。输出是可合入证据，不声称生成发布物或完成部署。

## `artifact`

项目已有确定性构建命令和版本标识，但还没有部署目标时使用。除 `validate` 外，可在受信任的 tag、release 或手动事件上构建不可变制品，记录提交 SHA、校验和和保留期。上传动作必须固定完整提交 SHA；不得把 fork PR 的不可信代码放进可发布制品流程。

## `deployment`

只有以下信息都明确时才配置真实部署：

- 目标平台、区域/账户和 staging/production 环境；
- 使用 OIDC 或平台原生短期身份的认证路径；
- 环境 secrets/variables 的名称和最小权限，不含明文值；
- 部署命令、部署对象标识和 GitHub Deployment/Environment 关联；
- 部署后健康验证、失败判定、超时与回滚/前滚动作；
- production 的人工审批、分支/tag 限制或其他等价保护需求。

缺少任一关键输入时停在 `ci` 或 `artifact`，列出升级到 `deployment` 所需信息。不要生成永远成功的占位部署，不要用 `pull_request_target` 执行 PR 代码，也不要向 fork PR 暴露环境凭据。

## 通用安全约束

- workflow 顶层显式声明最小 `permissions`，默认只给 `contents: read`；需要 `id-token: write` 时只给部署 job。
- 第三方与 GitHub 官方 actions 都固定完整 40 位提交 SHA，并在注释中保留审计过的版本标签。
- PR 主 workflow 不使用会导致 required check 缺席的顶层路径过滤；昂贵任务在 job/step 内判定，固定 `validate` 始终产生结论。
- 为 PR 运行配置 concurrency 和 `cancel-in-progress`，所有 job 设置合理超时。
- `workflow_dispatch` 只能作为补充入口，首次引导依靠 PR 的 `pull_request` 事件自动产生真实 check-run。
