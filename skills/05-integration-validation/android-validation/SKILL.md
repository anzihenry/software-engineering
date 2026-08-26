---
name: android-validation
metadata:
  owner: quality-lead
  scope: "Lifecycle phase 5: integration validation"
  status: active
  review_by: "2027-02-26"
description: "验证 Android 变更在目标 API、设备形态、厂商环境和后台限制下的行为；适用于合入前 Android 兼容、生命周期、可访问性与性能验证。"
---

# Android 验证

验证 Android 自测无法充分覆盖的 API、设备、安装升级、系统集成和非功能风险，并界定结论适用范围。跨 iOS/Android/HarmonyOS 的一致性和整体矩阵由 `mobile-validation` 汇总；本 SKILL 不执行 Play Console 或商店发布。

## 输入

- 验收标准、风险等级、Android 自测记录、待验证构建和支持的 API/设备矩阵。
- 测试账号与数据、后端/推送等依赖环境、历史版本、性能基线和观测手段。

## 工作方式

1. 根据支持策略、用户分布和变更触点选择最低/主流/最新 API、设备形态、关键 OEM 及 Emulator/真机组合，并说明未覆盖范围。
2. 验证全新安装、覆盖升级、冷/热启动、配置变化、进程死亡、低内存及任务切换后的恢复；检查本地数据库、偏好和会话兼容性。
3. 覆盖权限的未请求/允许/拒绝/不再询问及适用的一次性授权状态，以及 App Link/Intent、通知、WorkManager、Doze 与后台限制；厂商相关行为应有真机证据或明确限制。
4. 检查不同尺寸、密度、方向、多窗口、字体缩放、主题、键盘和本地化；使用 TalkBack 验证关键路径的语义、顺序、焦点和动态反馈。
5. 按风险测量启动、响应、卡顿、内存、耗电、崩溃与 ANR，并检查 release 变体的混淆/压缩、Manifest 和资源行为没有改变关键功能；实际通过 Gradle/ADB/Emulator 执行矩阵或采集报告、日志、截图和性能数据时组合 `mobile-cli-execution`，保留目标和变体身份。

## 输出格式

```markdown
## Android 验证报告
| 要求/风险 | API、设备/OEM 与变体 | 场景 | 证据/指标 | 结果 |
| --- | --- | --- | --- | --- |

- 安装升级、生命周期与数据兼容结论：
- 权限、Link/Intent、通知与后台限制结论：
- UI、TalkBack 与本地化结论：
- 启动、响应、内存、耗电与稳定性结论：
- 未覆盖矩阵、环境限制及影响：
- 总结：通过 | 有条件通过 | 阻塞 | 环境不可信
```

## 停止条件

- 当 Android 高风险组合和系统集成已有可信证据，且未覆盖范围已明确处置时，将结果交给 `mobile-validation` 或 `merge-readiness`。
- 功能或平台实现失败回流 `android-implementation-and-self-test`；支持范围、能力或数据方案缺口回流方案与计划。
- 关键真机/OEM、升级路径、后台限制或性能要求无法验证时，不给出无条件通过结论。
