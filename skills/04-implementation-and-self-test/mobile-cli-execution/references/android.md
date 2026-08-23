# Android CLI 执行

## 工具与发现

- 构建和测试始终优先使用仓库的 `./gradlew`；`adb` 管理 Emulator/真机，`emulator` 启动既有 AVD，`sdkmanager`/`avdmanager` 只用于经授权的环境配置。
- 执行前记录 Gradle Wrapper、JDK、Android SDK/Build Tools 和 adb 版本，并使用只读命令确认任务和目标：

```text
./gradlew tasks
adb devices -l
emulator -list-avds
```

- 从 Gradle/Manifest 合并结果和项目配置确认 module、variant、application ID、test runner 与启动入口；不要根据目录名或包名猜测。

## 构建与测试

- 使用最窄的 module/variant 任务开始，再按开发或验证 SKILL 扩大。常见形状如下，实际任务名以 `./gradlew tasks` 和项目约定为准：

```text
./gradlew :<module>:assemble<Variant>
./gradlew :<module>:lint<Variant>
./gradlew :<module>:test<Variant>UnitTest
./gradlew :<module>:connected<Variant>AndroidTest
```

- 项目已配置 Gradle Managed Devices 时优先使用其命名任务，以获得可重复的创建、部署、测试和清理；不要为了单次任务擅自新增设备配置或开启高资源分片。
- 保留 Gradle HTML/XML、instrumentation、Lint 和适用的 coverage 结果；退出码为零不代表目标测试确实被发现，需核对执行数量、skipped 和产物时间。

## Emulator 与真机

- 多设备在线时所有 `adb` 命令使用 `-s <serial>`；启动既有 AVD 后等待目标出现在 `adb devices -l` 且完成启动，再安装或测试。
- 安装 debug APK 前确认产物路径、variant 和 application ID。使用覆盖安装或清数据会改变被测状态，必须与“全新安装/升级/保留数据”场景一致并记录。
- 不执行 `emulator -wipe-data`、`adb uninstall`、`pm clear`、删除 AVD/system image 或改变共享快照，除非任务明确要求且目标已核实。
- 真机必须显式选择 serial 并已授权为测试设备；不浏览、拉取或修改与被测应用无关的文件、账号和系统数据。

## 日志、UI 与性能证据

- 通过项目 Espresso/Compose UI/UI Automator/instrumentation 测试验证用户路径；`adb shell am start` 只证明入口可启动，不等于功能通过。
- `adb logcat` 应按目标 serial、应用进程/tag 和时间窗口过滤；运行前后的缓冲区处理必须记录，避免把历史日志归因于本次测试。
- 截图、录屏、bugreport 和性能数据写入任务产物目录，并记录 API、设备/OEM、方向、窗口、字体和主题等影响解释的状态。
- 性能任务优先使用项目 Macrobenchmark/Baseline Profile 或已批准的 profiler 流程；普通功能任务不随意改变动画、后台限制、thermal 或开发者选项。

## Android 特有停止条件

- SDK/image 缺失、adb target 为 `offline`/`unauthorized`、variant/task 不存在或 Gradle/JDK 不兼容时，归类为环境/配置阻塞，不静默安装组件或切换全局工具链。
- Emulator 不能证明的 OEM、Play 服务、推送、后台限制、耗电或硬件能力必须转交适用真机/设备农场；缺少授权时明确未覆盖。

## 官方参考

- [Build your app from the command line](https://developer.android.com/build/building-cmdline)
- [Test from the command line](https://developer.android.com/studio/test/command-line)
- [Android Debug Bridge](https://developer.android.com/tools/adb)
- [Scale tests with build-managed devices](https://developer.android.com/studio/test/managed-devices)
