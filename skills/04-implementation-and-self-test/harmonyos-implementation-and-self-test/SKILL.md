---
name: harmonyos-implementation-and-self-test
description: "实现并自测 HarmonyOS 原生或平台专属变更；适用于涉及 ArkTS/ArkUI、Ability 生命周期、权限、分布式能力、本地数据或 Hvigor 构建的开发任务。"
---

# HarmonyOS 实现与自测

在既有 HarmonyOS 架构、SDK/API 和设备支持范围内实现可审查的平台变更，并形成 HarmonyOS 专属自测证据。跨移动平台共享逻辑和一致性由 `mobile-implementation-and-self-test` 协调；本 SKILL 不负责签名审批、AppGallery Connect 或应用市场发布。

## 输入

- 验收标准、交互设计、compatible/target API、目标设备形态、技术设计和风险等级。
- ArkTS/ArkUI、Stage 模型、module/product/buildMode、依赖管理、数据存储、权限、系统能力和遥测约定。

## 工作方式

1. 确认受影响的 module、product、target、buildMode、API 范围和设备形态；区分 HAP/HSP/HAR、共享代码与 HarmonyOS 专属行为，遵循项目实际 SDK 和 DevEco/Hvigor 配置。
2. 明确 ArkUI 页面、导航和状态所有权；处理 UIAbility/ExtensionAbility 生命周期、前后台、窗口变化、进程终止与状态恢复，不依赖仅在理想启动路径成立的内存状态。
3. 遵循 ArkTS 静态类型与并发约束；将 Promise、TaskPool、Worker 和 Sendable 用于其适合边界，处理取消、异常、线程间数据传递和 UI 主线程更新，避免无界任务及共享可变状态。
4. 对权限、Want、通知、后台任务、分布式/跨设备能力、Preferences/ArkData、文件和安全存储同步 module 配置及隐私声明；已有安装的数据、bundle/module 和 capability 变化必须兼容。
5. 添加 Local Test、Instrument Test 或 UI 测试，并在适用的 Emulator 和真机上检查主流程、失败恢复、不同窗口/折叠形态、字体缩放、深色模式、键盘、本地化和辅助功能；实际调用 `hvigorw`、`codelinter`、`ohpm`、`hdc` 或 HiLog 时组合 `mobile-cli-execution`，记录命令、目标、product/buildMode、API、原始产物和环境限制。

## 输出格式

```markdown
## HarmonyOS 实现与自测记录
- module、product、API、设备与 buildMode：
- ArkUI、导航、状态和 Ability 生命周期处理：
- 异步、TaskPool/Worker、Sendable 与资源管理：
- 权限、系统/分布式能力、数据与配置变化：
- 自动化测试及 Emulator/真机结果：
- 多设备适配、辅助功能与视觉检查：
- 未覆盖项、剩余风险与 HarmonyOS 验证需求：
```

## 停止条件

- 当相关产物可构建，平台关键行为有测试，且代表性 Emulator 或真机自测通过时，交给本地质量验证和交接准备。
- 当结论需要 API/设备形态矩阵、升级安装、真实分布式/通知/后台行为或性能基线时，交给 `harmonyos-validation`。
- 当需改变 compatible/target API、签名、module/bundle、系统能力、数据模型或跨平台契约时，回流方案与计划，不在实现中静默扩大范围。
