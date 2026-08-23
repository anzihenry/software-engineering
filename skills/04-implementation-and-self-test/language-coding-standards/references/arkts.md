# ArkTS 编码规范

## 版本与工具边界

- 以项目 DevEco Studio/Command Line Tools、HarmonyOS SDK/API、`build-profile.json5`、`module.json5`、`oh-package.json5` 和锁文件为事实，不自行声明一个脱离 SDK 的“ArkTS 版本”。
- `.ets` 使用 ArkTS 规则，不因为语法接近 TypeScript 就直接套用 TS 编译器、ESLint 配置或运行时假设。TS/JS 互操作必须经过项目边界和目标 API 验证。
- 使用仓库配置的 Code Linter、Hvigor 和 ohpm；不手改生成目录或构建产物，依赖变化应由 ohpm 按项目配置更新 lockfile，不伪造解析结果。

## 类型与模块

- 公共 API、导出函数、组件参数、状态和跨线程数据使用明确类型；避免 `any`、动态属性形状、运行时补字段及依赖隐式转换的设计。
- 用 union、enum、class/interface 和受控构造表达领域状态；可空值在边界显式收窄，不用非空断言掩盖生命周期或初始化问题。
- 模块依赖保持单向和可测试；HAR/HSP、跨 module API、Native/Node-API 互操作及序列化格式属于公共边界，变更时评估兼容和打包影响。
- 外部输入、Want 参数、持久化数据和 Kit/API 返回值在进入领域逻辑前校验；不要把类型断言当成运行时验证。

## ArkUI 与生命周期

- 组件只拥有其职责范围内的状态；父子组件和页面/Ability 之间保持单一数据来源，状态装饰器及观察机制遵循项目采用的 ArkUI 版本和范式。
- 避免在构建/渲染路径执行阻塞 I/O、重计算或隐式副作用；昂贵工作移到明确的异步或并发边界，并防止重复订阅和重入更新。
- 将 UIAbility、ExtensionAbility、页面和组件生命周期中的订阅、定时器、监听器、资源句柄和任务成对释放；恢复流程不依赖已被系统回收的内存状态。
- 多设备和响应式 UI 使用能力/窗口信息驱动布局，不用设备型号字符串或固定像素分支模拟适配。

## 异步与并发

- Promise/`async`/`await` 用于异步流程并显式传播错误；不得遗留无观察的 Promise、无限重试或无法取消/超时的长任务。
- 独立 CPU 密集任务优先评估 TaskPool；需要长期独立线程和专有生命周期时才使用 Worker。选择依据是任务生命周期、通信成本和项目 API 支持，而不是个人偏好。
- 跨线程数据遵守 Sendable/可传输对象和序列化约束；避免共享可变普通对象，明确所有权转移、复制成本和线程结束条件。
- UI 状态回写必须回到平台允许的上下文；不要通过绕开静态检查或不安全断言消除并发诊断。

## 错误、安全与性能

- 对权限、文件、网络、数据库、系统 Kit 和跨设备调用区分用户拒绝、暂时失败、不支持与编程错误；不得吞掉异常或把外部失败改成假成功。
- bundleName、Ability、权限、证书、token 和 endpoint 不散落硬编码；敏感数据使用平台安全存储，HiLog 不记录凭据、个人数据或完整业务载荷。
- 依赖和 Kit API 在调用前确认 compatible/target API 与 SystemCapability；降级路径应可观察且保持语义，不以捕获所有异常代替能力检查。
- 性能优化以 Profiler、启动/帧/内存指标或可重复基准为依据；避免在 ArkUI 更新、序列化或线程通信中制造大对象复制和无界集合。

## 验证

- 运行项目 Code Linter 规则集，至少保留项目启用的 TypeScript、ArkTS 风格、安全、性能和跨设备检查；不得扩大 ignore 制造通过。
- 使用最靠近风险的 Local Test、Instrument Test 和 UI 测试，覆盖 Ability/组件生命周期、状态恢复、权限拒绝、API 能力差异、异步失败与跨线程数据。
- 通过项目 `hvigorw` 构建受影响 module/product；需要 Emulator/真机、HDC、HiLog 或性能证据时使用移动端 CLI 和 HarmonyOS 平台 SKILL。

## 官方参考

- [ArkTS overview](https://developer.huawei.com/consumer/en/arkts/)
- [HarmonyOS quick start and ArkTS guides](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/quick-start)
- [Code Linter checks](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V13/ide-code-linter-V13)
- [Code Linter recommended rules](https://developer.huawei.com/consumer/cn/doc/doccenter-deveco-studio/ide-coderlinter-recommended-rules)
