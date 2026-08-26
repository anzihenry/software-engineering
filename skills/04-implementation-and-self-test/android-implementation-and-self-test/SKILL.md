---
name: android-implementation-and-self-test
metadata:
  owner: implementation-lead
  scope: "Lifecycle phase 4: implementation and self-test"
  status: active
  review_by: "2027-02-26"
description: "实现并自测 Android 原生或平台专属变更；适用于涉及组件生命周期、协程、权限、后台执行、本地数据或 Gradle 变体的开发任务。"
---

# Android 实现与自测

在既有 Android 架构和支持范围内实现可审查的平台变更，并形成 Android 专属自测证据。跨 iOS/Android/HarmonyOS 的共享逻辑和一致性由 `mobile-implementation-and-self-test` 协调；本 SKILL 不负责 Play Console、签名审批或商店发布。

## 输入

- 验收标准、交互设计、最低/目标 API、设备形态、技术设计和风险等级。
- Kotlin/Java、Compose/View、模块与 Gradle 约定，数据存储、权限、后台任务和遥测要求。

## 工作方式

1. 确认受影响的 module、build type/flavor、API 范围和设备形态；保持 Compose/View 或共享/原生边界与项目架构一致。
2. 明确 UI、导航和状态所有权；处理 Activity/Fragment/Compose 生命周期、配置变化、进程死亡与状态恢复，不将短生命周期对象泄漏到长生命周期作用域。
3. 将 coroutine/Flow 绑定到正确作用域并处理取消、异常和重复收集；避免阻塞主线程、无界任务和不受控并发更新。
4. 对运行时权限、Intent/App Link、通知、WorkManager/后台限制、Room/DataStore、Keystore 和系统 API 处理 API 级差异；Manifest、资源和已有安装数据保持兼容。
5. 添加单元、组件或 UI 测试，并在适用的 Emulator 和真机上检查主流程、失败恢复、字体缩放、TalkBack、不同窗口尺寸、键盘及主题；实际调用 Gradle Wrapper、`adb`、Emulator 或 SDK 工具时组合 `mobile-cli-execution`，记录命令、目标、变体、API、原始产物和环境限制。

## 输出格式

```markdown
## Android 实现与自测记录
- module、API、设备与构建变体：
- UI、导航、状态和生命周期处理：
- 协程、取消和资源管理：
- 权限、后台行为、数据与 Manifest 变化：
- 自动化测试及 Emulator/真机结果：
- 可访问性与视觉适配：
- 未覆盖项、剩余风险与 Android 验证需求：
```

## 停止条件

- 当相关变体可构建，平台关键行为有测试，且代表性 Emulator 或真机自测通过时，交给本地质量验证和交接准备。
- 当结论需要 API/OEM/设备矩阵、升级安装、真实推送/后台限制或性能基线时，交给 `android-validation`。
- 当需改变支持 API、Manifest 能力、数据模型或跨平台契约时，回流方案与计划，不在实现中静默扩大范围。
