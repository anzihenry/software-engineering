---
name: mobile-cli-execution
metadata:
  owner: implementation-lead
  scope: "Lifecycle phase 4: implementation and self-test"
  status: active
  review_by: "2027-02-26"
description: "通过 Apple、Android 或 HarmonyOS 官方命令行工具执行移动端环境检查、构建、测试、模拟器/设备操作和证据采集；适用于 Agent 需要实际运行平台工具链时，不替代实现或验证结论。"
---

# 移动端 CLI 执行

将 iOS、Android 和 HarmonyOS 开发与验证任务转化为可重复、目标明确且可审计的命令行执行。平台实现范围和验证结论仍由对应开发/验证 SKILL 负责；本 SKILL 只负责工具调用、目标生命周期和原始证据。

## 使用方式

1. 始终先读 [通用执行与证据规则](references/common.md)。
2. 只读取任务涉及的平台参考；跨平台任务读取所有涉及项：
   - Apple 平台：[iOS CLI](references/ios.md)
   - Android 平台：[Android CLI](references/android.md)
   - HarmonyOS 平台：[HarmonyOS CLI](references/harmonyos.md)
3. 从仓库脚本、构建配置和 CI 获取真实命令、scheme/variant、设备范围及产物路径；本文示例中的占位符不能直接执行。
4. 先执行只读发现，再锁定单一目标和任务专属产物目录；执行后收集退出状态、结构化结果、日志和环境身份。

## 职责边界

- 使用 `ios-implementation-and-self-test`、`android-implementation-and-self-test` 或 `harmonyos-implementation-and-self-test` 决定如何实现与自测。
- 使用 `ios-validation`、`android-validation` 或 `harmonyos-validation` 决定矩阵、风险覆盖和通过结论。
- 本 SKILL 不修改业务代码，不自行扩大设备矩阵，也不执行签名、商店上传、生产发布或未经授权的云设备测试。

## 停止条件

- 工具链、构建入口、目标设备或产物身份不唯一时，先从仓库和只读命令确认；仍无法确认则停止执行并报告缺口。
- 命令成功，或失败已完成分类且继续重试不会增加有效证据，并且所需证据已持久化、敏感信息已脱敏、任务启动的资源已安全收口时完成。
- 需要安装/升级工具链、擦除设备数据、修改签名/密钥、操作未授权真机或产生外部费用时，在动作前请求对应授权。
