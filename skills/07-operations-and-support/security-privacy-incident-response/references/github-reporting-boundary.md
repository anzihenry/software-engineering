# GitHub 安全与隐私报告边界

- 安全漏洞使用仓库 `SECURITY.md` 指向的 Private Vulnerability Reporting。
- 活跃隐私/安全事故在团队受限系统建立记录；普通 Issue 只可引用安全字符组成的受限事件 ID 和脱敏服务状态。
- 一旦标记安全/隐私风险，普通状态自动化只允许升级为 `escalated`，并忽略普通决定与证据输入，避免把敏感内容写回公开记录。
- 凭据、个人信息、受限日志、取证材料、恶意载荷、法律与通知判断不得进入普通 Issue、PR、Release 或 Actions 摘要。
