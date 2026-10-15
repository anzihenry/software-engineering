# Draft Release 自动化契约

- 只从 `workflow_dispatch` 接受版本、完整 source SHA、风险、变更记录和摘要；默认 dry-run。
- Python 校验 `vMAJOR.MINOR.PATCH`、source SHA 的 main 可达性、配置的 required checks 及重复 tag/Release；GitHub JSON 由工作流通过 `gh` 采集。
- 实际创建要求关闭 dry-run 且确认字符串精确匹配版本；只有创建 job 使用 `contents: write`。
- 自动化只创建 Draft Release 和候选附件，不发布正式 Release、不部署、不回滚，也不替代人类 Go/No-Go。
- 同版本候选串行且不取消运行；已存在 tag 或 Release 时失败，不覆盖或重用版本。

## 阶段06接收与能力边界

本自动化只完成上述输入校验及Draft创建，不自动核验每次功能合入后端到端、组合风险、独立评审来源、发布授权/有效窗口、实际分发制品验证或观察接收。编排者按[发布流程](../../../../docs/workflows/06-release-and-change-management.md)补核这些要求；缺口阻塞对应节点，不能用main可达和required checks绿代替候选verified或生产Go。

候选ID/修订将source、版本、附件摘要/构建与配置迁移映射到发布主记录；必要转换保留输入输出摘要。版本精确确认只授权本次Draft动作，不自动覆盖公开Release、包/商店分发、部署、迁移或恢复。现有生成器/分发范围未因契约更新而扩大。
