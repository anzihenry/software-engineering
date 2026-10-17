# GitHub 复盘自动化契约

## 实际支持的来源与期限

来源仅 `incident:N` 或正式非Draft/Prerelease的 `release:vX.Y.Z`。普通事故需唯一状态标签，状态为recovered/closed，或触发者明确确认稳定；工具不验证真实恢复。未稳定阶段复盘用通用记录，不虚填stable。SEV1/2/3按当前policy为7/14/30天，SEV4为none；正式Release为发布日期后30天。触发/期限可配置，通用评估仍按项目约定，不因工具不支持而遗漏。

`retrospective.py`当前实现：显式 `stability_confirmed=true` 时无论当前是否recovered/closed，期限锚点均用请求 `occurred_at`；false时从评论匹配recovered/closed转换时间取最早值，没有时间拒绝。工作流occurred_at取运行时UTC，不等真实恢复时间。应核对锚点与真实适用期限，不能以晚触发/重复确认稳定静默顺延；有偏差在通用记录保留真实应到期、工具日期与处置。

## 幂等与执行边界

隐藏 `lifecycle-source:<source>` 标记在读取的既有Issue中查重，返回首个可用匹配编号/URL；不自动合并内容或认证所有发现已覆盖。工作流相同source串行且不取消运行，查重结果才跳创建；不构成跨入口全局事务保障。dry-run仅验证/渲染，apply需精确 `retrospective-incident-N` 或 `retrospective-release-vX.Y.Z` 确认和既有授权；用户请求本地复盘不自动授权外发或建Issue。

正文保留事实时间线、当时可见信息、促成因素、防护有效性、不确定性及行动链接（可明确pending）。生成/去重不证明分析正确、行动接收或复盘完成。安全/隐私只脱敏摘要与受限ID/受控引用，不复制专项详情。
