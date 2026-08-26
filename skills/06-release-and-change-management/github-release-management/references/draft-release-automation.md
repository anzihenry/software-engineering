# Draft Release 自动化契约

- 只从 `workflow_dispatch` 接受版本、完整 source SHA、风险、变更记录和摘要；默认 dry-run。
- Python 校验 `vMAJOR.MINOR.PATCH`、source SHA 的 main 可达性、配置的 required checks 及重复 tag/Release；GitHub JSON 由工作流通过 `gh` 采集。
- 实际创建要求关闭 dry-run 且确认字符串精确匹配版本；只有创建 job 使用 `contents: write`。
- 自动化只创建 Draft Release 和候选附件，不发布正式 Release、不部署、不回滚，也不替代人类 Go/No-Go。
- 同版本候选串行且不取消运行；已存在 tag 或 Release 时失败，不覆盖或重用版本。
