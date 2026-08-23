# Kotlin 2.4 编码规范

## 风格与建模

- 遵循 Kotlin 官方 Coding Conventions 和项目 formatter；源码路径匹配 package，文件名表达内容，避免 `Util`/`Helper` 等无边界名称。
- 默认 `val`，缩小可变状态和可见性。使用 data/value class 表达数据，用 sealed class/interface 表达封闭状态；不要把多个 nullable/Boolean 字段组合成非法状态。
- 利用 null safety；禁止用 `!!` 掩盖不确定性。Java/platform type 在适配边界立即验证并转换为明确 nullable/non-null Kotlin 类型。
- 扩展函数放在拥有该语义的模块并保持可发现；不要用大规模扩展集合制造隐藏依赖。作用域函数嵌套时优先可读性，避免 `this`/`it` 指代不清。

## API、错误与集合

- 公共 API 显式返回类型和可见性；库 API 考虑二进制/源兼容。默认参数和重载不得产生 Java 调用歧义。
- 异常用于失败，不用 nullable 混淆“没有结果”和“发生错误”。捕获最窄异常，转换时保留 cause；不吞掉 `CancellationException`。
- 集合转换链保持清晰并考虑分配成本；复杂或性能敏感逻辑可用普通循环。暴露只读接口不代表底层真正不可变，跨边界时明确所有权。

## 协程与 Flow

- 遵循结构化并发；协程必须在有生命周期的 `CoroutineScope` 中启动，禁止 `GlobalScope` 和无所有者的 fire-and-forget。
- suspend 函数应 main-safe/调用方安全；阻塞工作进入明确 dispatcher。dispatcher、时钟和外部依赖在需测试处注入，不硬编码全局调度。
- 传播取消与超时；只在需要隔离兄弟失败时使用 supervisor。`launch`/`async` 的异常必须被拥有者观察。
- Flow 明确冷/热、重放、缓冲、背压和收集生命周期；不要因重复 collect 触发未预期副作用。

## 验证

- 运行项目 formatter、静态分析、Kotlin 编译和测试；所有目标平台/源集按变更范围验证。
- 协程测试使用测试调度器和虚拟时间，断言取消、异常、顺序及重复收集；不要用真实 sleep 制造时序。
- Kotlin 2.4 实验特性仅在项目显式 opt-in 时使用；公共 API 不泄露未批准实验类型。

## 官方参考

- [Kotlin coding conventions](https://kotlinlang.org/docs/coding-conventions.html)
- [Kotlin coroutines guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [Kotlin 2.4 documentation](https://kotlinlang.org/docs/home.html)
