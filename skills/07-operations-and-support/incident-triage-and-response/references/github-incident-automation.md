# GitHub 普通事故自动化契约

- Issue Form 只承载普通、非敏感事故，要求严重度、带时区时间、范围、影响、事实/未知项、所有者、版本关联和证据链接。
- 手动状态机只允许 `investigating → mitigating/recovered/escalated`、`mitigating → recovered/escalated`、`recovered → closed` 和重新打开后的 `closed → investigating`。
- 默认 dry-run；实际写入要求 `incident-N` 精确确认，并追加操作者、时间、决定和 HTTPS 证据，保持单一当前状态标签。
- 已处于目标状态的重试为 no-op。安全/隐私升级只保留受限事件 ID，普通决定和证据文本会被忽略。
