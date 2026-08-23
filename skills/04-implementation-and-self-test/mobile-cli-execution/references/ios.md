# iOS CLI 执行

## 工具与发现

- `xcodebuild` 负责列出工程信息、构建、测试和生成 `.xcresult`；`xcrun simctl` 管理 Simulator；真机使用当前 Xcode 提供的 `xcrun devicectl`。
- `xcresulttool` 读取结果包，`xctrace` 采集 Instruments trace。具体子命令以当前选定 Xcode 的 `man`/`help` 和仓库脚本为准。
- 执行前记录 `xcodebuild -version`、`xcode-select -p`，并用以下只读模式确认项目与目标：

```text
xcodebuild -list -json -workspace <workspace>
xcodebuild -showdestinations -workspace <workspace> -scheme <scheme>
xcrun simctl list devices available -j
```

项目使用 `.xcodeproj` 时将 `-workspace` 替换为 `-project`；优先采用仓库固定的 workspace、scheme、test plan 和 configuration。

## 构建与测试

- 使用 Simulator UDID 而不是易冲突的设备名称；为本次运行设置独立的 `-derivedDataPath` 和尚不存在的 `-resultBundlePath`。
- 先运行受影响的窄测试，再按平台开发或验证 SKILL 要求扩大范围。基础形状为：

```text
xcodebuild build -workspace <workspace> -scheme <scheme> -configuration <configuration> -destination 'platform=iOS Simulator,id=<udid>' -derivedDataPath <artifact-dir>/DerivedData
xcodebuild test -workspace <workspace> -scheme <scheme> -testPlan <test-plan> -destination 'platform=iOS Simulator,id=<udid>' -derivedDataPath <artifact-dir>/DerivedData -resultBundlePath <artifact-dir>/<run>.xcresult
```

- 没有 test plan 时省略 `-testPlan`；只测单项时使用项目验证过的 `-only-testing:<identifier>`。不得通过跳过失败测试或改变 scheme shared 状态制造通过。
- 保留 `.xcresult` 并用当前 Xcode 的 `xcresulttool help` 选择兼容的摘要/导出命令；文本日志不能替代结果包中的测试和附件身份。

## Simulator 与真机

- 启动现有 Simulator 时使用明确 UDID，并等待启动完成：

```text
xcrun simctl boot <udid>
xcrun simctl bootstatus <udid> -b
```

- 安装和启动前从构建设置/产物确认 `.app` 路径与 bundle ID；不得从产品名猜测。截图、视频和日志均写入任务产物目录并记录采集时刻。
- 不执行 `simctl erase`、删除 runtime/device 或修改共享 Simulator 状态，除非任务明确要求且目标已核实。只关闭由本任务启动且未被其他工作占用的 Simulator。
- 真机操作前确认 UDID、连接/信任状态、测试授权和签名前置条件。`devicectl` 接口随 Xcode 演进，先读取 `xcrun devicectl help`，不复用未经当前版本验证的旧命令。

## 日志、UI 与性能证据

- 功能/UI 验证优先使用项目 XCTest/Swift Testing/XCUITest；CLI 负责运行和保存附件，不以“进程成功启动”代替用户路径断言。
- 使用 `simctl io` 采集截图/视频时记录目标 UDID、方向和系统外观；视觉结论还需关联基线和容差。
- 性能任务使用 `xctrace` 或项目性能测试，明确 template、持续时间、设备、构建配置和基线。普通功能任务不无条件采集高成本 trace。
- 捕获日志时限制进程、subsystem/category 和时间窗口；对账号、通知载荷、URL 参数及 Keychain 相关内容脱敏。

## iOS 特有停止条件

- scheme 未共享、目标 runtime 缺失、目标 destination 不唯一或签名要求无法满足时，归类为环境/配置阻塞，不擅自修改工程或安装组件。
- Simulator 不能证明的能力必须转交真机验证；无授权真机时明确未覆盖，不外推通过。

## 官方参考

- [Xcode command-line tool reference](https://developer.apple.com/documentation/xcode/xcode-command-line-tool-reference)
- [Running tests and interpreting results](https://developer.apple.com/documentation/xcode/running-tests-and-interpreting-results)
