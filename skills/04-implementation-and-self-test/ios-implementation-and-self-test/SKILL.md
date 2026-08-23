---
name: ios-implementation-and-self-test
description: "实现并自测 iOS/iPadOS 原生或平台专属变更；适用于涉及 Apple 生命周期、并发、权限、系统能力、本地数据或 Xcode 构建的开发任务。"
---

# iOS 实现与自测

在既有 Apple 平台架构和支持范围内实现可审查的 iOS/iPadOS 变更，并形成平台专属自测证据。跨平台共享逻辑和两端一致性由 `mobile-implementation-and-self-test` 协调；本 SKILL 不负责签名审批、TestFlight 或 App Store 发布。

## 输入

- 验收标准、交互设计、最低系统版本、目标设备形态、技术设计和风险等级。
- Swift/Objective-C、SwiftUI/UIKit、依赖管理、构建配置、数据存储、权限与遥测约定。

## 工作方式

1. 确认受影响的 target、extension、scheme/configuration、系统版本和设备形态；保持 SwiftUI/UIKit 或共享/原生边界与项目架构一致。
2. 让视图、导航和状态所有权保持单一；处理 scene/app 生命周期、前后台、中断、状态恢复和系统终止后的重建，不依赖只在理想启动路径成立的内存状态。
3. 遵守 Swift 并发隔离、主线程 UI 更新和任务取消边界；避免非结构化任务、循环引用及在视图生命周期外继续持有资源。
4. 对权限、Universal Link/URL Scheme、通知、后台任务、Keychain/Data Protection、文件与系统框架同步所需 entitlement、Info.plist 和隐私声明；已有安装的数据演进须向前兼容。
5. 添加单元、状态/视图或 UI 测试，并在适用的 Simulator 和真机上检查主流程、失败恢复、Dynamic Type、VoiceOver、安全区、键盘及深色模式；记录构建配置和环境限制。

## 输出格式

```markdown
## iOS 实现与自测记录
- target、系统版本、设备与构建配置：
- UI、导航、状态和生命周期处理：
- 并发、取消和资源管理：
- 权限、系统能力、数据与隐私声明：
- 自动化测试及 Simulator/真机结果：
- 可访问性与视觉适配：
- 未覆盖项、剩余风险与 iOS 验证需求：
```

## 停止条件

- 当相关 target 可构建，平台关键行为有测试，且代表性 Simulator 或真机自测通过时，交给本地质量验证和交接准备。
- 当结论需要系统/设备矩阵、升级安装、真实通知/后台行为或性能基线时，交给 `ios-validation`。
- 当需改变支持版本、entitlement、数据模型或跨平台契约时，回流方案与计划，不在实现中静默扩大范围。
