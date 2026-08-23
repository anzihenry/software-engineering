# Swift 6.2 编码规范

## API 与建模

- 遵循 Swift API Design Guidelines：调用点清晰优先于声明简短，名称描述角色和副作用，文档说明调用者需要知道的语义。
- 默认使用值类型表达独立数据；引用身份、共享可变状态或框架要求明确时才用 class。无继承意图的 class 标记 `final`。
- 收紧访问控制，公共 API 保持最小。用 enum/关联值表达有限状态，用 protocol 表达真实能力，不为 mocking 提前给每个类型创建协议。
- 正常缺失用 Optional；`!`、`try!` 和强制转换只允许编译期/启动期不变量且失败应立即暴露的情况，并写明依据。

## 并发与生命周期

- 使用 Swift 6 严格并发检查。共享可变状态由 actor、全局 actor 或其他清晰同步边界拥有；跨隔离传递的值满足 `Sendable`。
- Swift 6.2 的默认隔离和调用者上下文行为必须由 target 配置明确。不要为消除诊断随意添加 `nonisolated`、`@unchecked Sendable` 或 `Task.detached`。
- 创建的 Task 必须有生命周期、取消和错误所有者；UI 更新处于正确 actor，长时操作检查取消。并行只用于真正独立工作。
- 闭包捕获显式考虑所有权；`weak self` 不是默认模板。需要对象存活就强捕获，需要打破环才弱捕获，并处理对象消失语义。

## 错误、资源与性能

- 可恢复失败使用 `throws`/Result 并保留底层原因；`precondition`/assertion 只用于程序员违反不变量，不处理网络、用户输入或存储失败。
- 使用 `defer` 和 RAII 风格封装成对资源；unsafe pointer、C/C++ 互操作和 `@unchecked` 代码限制在小边界并配测试/说明。
- 优先标准库集合和清晰算法；性能优化基于 Instruments/基准证据。避免无依据的复制规避或手写低层内存代码。

## 验证

- 运行项目 formatter/lint、Swift 编译和测试；新代码不得引入 warning，严格并发诊断不得通过关闭检查解决。
- 使用项目既有的 Swift Testing 或 XCTest。测试 async 取消、actor 隔离、错误和生命周期；UI/系统能力按移动端专项验证。
- 公共 API 更新 DocC/文档和兼容说明；Package.swift/Xcode target 的语言模式与平台版本是版本事实。

## 官方参考

- [Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/)
- [Swift 6.2 released](https://www.swift.org/blog/swift-6.2-released/)
- [The Swift Programming Language](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/)
