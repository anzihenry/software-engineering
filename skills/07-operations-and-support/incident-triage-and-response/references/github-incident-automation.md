# GitHub 普通事故自动化契约

- Issue Form 只承载普通、非敏感事故，要求严重度、带时区时间、范围、影响、事实/未知项、所有者、版本关联和证据链接。
- 手动状态机只允许 `investigating → mitigating/recovered/escalated`、`mitigating → recovered/escalated`、`recovered → closed` 和重新打开后的 `closed → investigating`。
- 默认 dry-run；实际写入要求 `incident-N` 精确确认，并追加操作者、时间、决定和 HTTPS 证据，保持单一当前状态标签。
- 当前标签已是目标且Issue开关一致时可no-op，不要求已有operation marker；开关不一致则协调开关，仅无本次marker时追加协调记录。当前标签未到目标时，已有匹配operation marker避免重复评论，工作流仍按计划更新标签/开关；零或多个状态标签、marker冲突直接拒绝。安全/隐私升级只保留受限事件ID，普通决定和证据文本会被忽略。

## 阶段07语义边界

本自动化只校验输入/合法转换并生成状态操作计划，不认证分级、用户/数据恢复、稳定窗、通知、转交接收或关闭证据；这些按[运行契约](../../../../docs/workflows/07-operations-and-support.md)由负责人核对。现有五状态保持，已缓解、降级恢复、支持结案原因等写主记录对应字段，不擅自增加平台标签/转换。预授权缓解不替代既有GitHub写入的dry-run及人类精确确认。
