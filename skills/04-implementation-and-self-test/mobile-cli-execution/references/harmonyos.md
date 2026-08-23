# HarmonyOS CLI 执行

## 工具与发现

- 优先使用项目随附的 `hvigorw` 和已锁定配置执行构建/测试；`codelinter` 检查 ArkTS/TS，`ohpm` 管理依赖，`hdc` 连接 Emulator/真机并安装、调试和采集日志。
- 执行前记录 DevEco Command Line Tools、HarmonyOS SDK/API、Hvigor、Code Linter、ohpm 和 hdc 版本，并通过项目帮助及以下只读命令确认构建入口和设备：

```text
hvigorw --help
codelinter -v
ohpm --version
hdc list targets -v
```

- 从 `build-profile.json5`、`module.json5`、`oh-package.json5`、锁文件和 CI 确认 product、module@target、buildMode、bundleName、Ability、compatible/target SDK 及任务名；不要从目录名猜测。

## 构建、检查与测试

- 先执行受影响 module/product 的窄任务，再按平台开发或验证 SKILL 扩大范围。常见构建形状如下，实际参数和任务以项目 wrapper、`hvigorw --help` 和 CI 为准：

```text
hvigorw --mode module -p product=<product> -p module=<module>@<target> -p buildMode=debug assembleHap
hvigorw --mode project -p product=<product> -p buildMode=debug assembleApp
```

- 使用仓库 `code-linter.json5` 的规则集运行 Code Linter；不得通过扩大 ignore、关闭安全/性能规则或改用较宽松全局配置制造通过。
- Local Test 位于项目 `test` 范围且不依赖设备；Instrument Test 位于 `ohosTest` 范围并需要 Emulator/真机。测试任务和报告路径随 DevEco/Hvigor 版本及项目插件变化，必须从项目配置/CI 确认，不复用未经当前版本验证的旧命令。
- 保留 HAP/APP 身份、Hvigor/Code Linter 输出、测试报告和覆盖率产物；`Finished`、`UP-TO-DATE` 或退出码为零不能代替确认目标测试确实执行。

## Emulator 与真机

- 使用 `hdc list targets -v` 确认 connect-key 和连接状态；存在多个目标时，所有设备命令显式使用 `hdc -t <connect-key> ...`。
- 安装前核对 HAP/APP 路径、product/buildMode、bundleName、签名和设备 API/releaseType。可通过项目允许的只读命令查询设备 API，但不得为解决不兼容而静默降低项目 SDK 或升级设备镜像。
- 覆盖安装、卸载或清空应用数据会改变“全新安装/升级/保留数据”场景，只能按测试设计执行并记录。不得删除 Emulator、擦除共享设备、改变快照或操作与被测应用无关的数据。
- 真机或多设备场景必须明确每个 connect-key、设备形态、系统/API、连接方式和角色；分布式能力不能用单设备启动结果外推。

## 日志、UI 与性能证据

- UI 路径由项目自动化测试或明确的交互步骤验证；启动 Ability 只证明入口可达，不等于功能通过。
- 通过 `hdc -t <connect-key> shell hilog ...` 采集 HiLog 时限制进程/domain/tag 和时间窗口；如改变缓冲区或启停日志落盘，记录原状态并仅收口本任务改变的设置。
- 截图、录屏、HiLog、crash/freeze、测试和性能数据写入任务产物目录，并记录 API、设备形态、窗口/折叠状态、字体、主题及采集时刻。
- 性能任务优先使用项目已批准的 DevEco Profiler、性能测试或系统诊断流程；普通功能任务不随意改变调度、thermal、后台或系统开发者选项。

## HarmonyOS 特有停止条件

- Command Line Tools/SDK 缺失、HDC 目标为 Offline/Unauthorized、API/releaseType 不兼容、Hvigor 任务不存在或签名无法满足时，归类为环境/配置阻塞，不静默安装组件、改 SDK 或生成新签名。
- Emulator 不能证明的真机硬件、分布式协同、推送、后台、能耗或设备形态行为必须转交适用真机/设备矩阵；缺少授权时明确未覆盖。

## 官方参考

- [HarmonyOS Command Line Tools](https://developer.huawei.com/consumer/cn/doc/doccenter-deveco-studio/ide-commandline-get)
- [Hvigor build mode and command examples](https://developer.huawei.com/consumer/en/doc/harmonyos-guides-V14/ide-hvigor-compilation-options-customizing-sample-V14)
- [HarmonyOS Device Connector](https://developer.huawei.com/consumer/en/doc/harmonyos-guides/hdc)
- [HarmonyOS code testing](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V13/ide-code-test-V13)
