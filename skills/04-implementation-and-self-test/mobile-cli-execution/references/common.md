# 通用执行与证据规则

## 执行前发现

- 优先使用仓库提交的 wrapper、脚本和任务；不得用全局工具替代 `./gradlew`/`hvigorw`，也不得绕过项目固定的 Xcode、DevEco、JDK、SDK 或依赖版本。
- 记录提交 SHA、工作树状态、主机架构、工具链版本和实际构建入口。工作树非干净时将其写入证据，不把结果误称为对应某个干净提交。
- 通过只读命令列出 scheme/variant/product、可用 runtime/API 和设备。不要猜测 bundle ID、application ID、bundleName、Ability、scheme、module、product 或目标名称。
- 为任务创建独立产物目录，避免覆盖既有 `.xcresult`、HAP/APP、测试报告、截图、日志或性能数据；并行任务必须隔离设备、端口和产物路径。

## 目标与生命周期

- 涉及 Simulator、Emulator 或真机时锁定明确的 UDID、serial 或 HDC connect-key；存在多个在线目标时禁止依赖默认选择。纯编译和本地单元测试无需虚构设备目标。
- 区分共享开发设备与任务专属设备。只启动、停止或清理本任务创建/占用的资源，不改变其他开发者正在使用的设备状态。
- 模拟器适合可重复的构建、功能和基础 UI 测试；相机、推送、蓝牙、后台限制、能耗、OEM/设备形态或分布式能力差异等结论必须来自适用真机或明确标注为未覆盖。
- 设置与任务风险匹配的超时。超时后先保存日志和状态，再终止本任务进程；不得用无限等待或无限重试掩盖挂起。

## 证据要求

每次执行至少记录：

```markdown
## 移动端 CLI 执行记录
- 平台、提交与工作树状态：
- 主机、工具链与构建入口：
- scheme/variant/product、configuration/buildMode 与测试范围：
- Simulator/Emulator/真机标识及系统/API：
- 实际命令、开始/结束时间与退出状态：
- 测试结果、日志、截图/视频、性能产物路径：
- 失败摘要与首次相关错误：
- 清理结果、环境限制与未覆盖项：
```

- 保留机器可读原始结果，再提供摘要；失败时保存首个相关错误及其上下文，不只保留末尾退出码。
- 证据路径必须可追溯到本次运行，且位于项目允许的 artifact/临时目录。报告不得引用已被覆盖、来自其他提交或无法定位的文件。
- 日志和截图不得暴露 token、签名材料、个人账号、设备隐私数据或完整生产载荷；必要时先脱敏再共享。

## 授权与安全边界

- 只读发现、项目既有构建/测试和在专用模拟器安装 debug 构建通常属于正常执行范围。
- 安装或升级 Xcode/DevEco/SDK/JDK/runtime/image、创建或删除共享设备、擦除/卸载/清空数据、改变系统权限与网络代理，必须确认任务授权和影响范围。
- 真机必须是明确的测试目标；不得操作个人设备或读取无关数据。涉及证书、Provisioning Profile、Keychain、keystore、HarmonyOS 签名配置或 release signing 时停止并转交签名/发布流程。
- 不调用 TestFlight、App Store Connect、Play Console、Firebase Test Lab、AppGallery Connect 或其他云设备/分发服务，除非任务明确授权了目标、账号、费用和数据范围。

## 失败分类

- **代码/测试失败**：命令和环境可信，失败可归因于被测变更；回流对应平台实现。
- **环境失败**：runtime/image 缺失、设备离线、磁盘不足、权限或工具链不一致；修复环境后重试，不能判定产品失败。
- **不确定**：日志或目标身份不足，无法区分代码与环境；补证据前不重复大量运行，也不给出通过结论。

## 官方参考

- [Apple Xcode command-line tool reference](https://developer.apple.com/documentation/xcode/xcode-command-line-tool-reference)
- [Android: Build your app from the command line](https://developer.android.com/build/building-cmdline)
- [Android: Test from the command line](https://developer.android.com/studio/test/command-line)
- [HarmonyOS: Command Line Tools](https://developer.huawei.com/consumer/cn/doc/doccenter-deveco-studio/ide-commandline-get)
- [HarmonyOS Device Connector](https://developer.huawei.com/consumer/en/doc/harmonyos-guides/hdc)
