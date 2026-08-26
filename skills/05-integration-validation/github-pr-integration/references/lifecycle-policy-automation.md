# PR 生命周期策略自动化

当目标仓库采用本手册的 GitHub 生命周期自动化时，先读取 [`docs/github-lifecycle-automation.md`](../../../../docs/github-lifecycle-automation.md)，再核对项目自己的 required checks、风险模型和团队审批能力。

`lifecycle-policy` 只验证 PR 记录的结构与风险条件。Draft 中的缺口是警告；Ready PR 中的缺口会阻塞。它不读取受限证据、不验证外部链接内容，也不把结构通过解释为独立评审、测试或生产批准。

将新 check 加入 ruleset 前必须已有真实 PR check-run。若误阻塞，先移除新增 check 并保留原质量门禁，修复和验证后再恢复。
