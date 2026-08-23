# C++20 编码规范

## 语言与接口

- 编译为标准 C++20，非标准扩展由项目显式批准。开启高等级 warning 并将新 warning 视为失败；格式遵循项目 clang-format/等价配置。
- 接口表达所有权、可空性、生命周期和单位：值表示复制/移动所有权，引用表示必需且非空借用，指针表示可空或与 C API 互操作；裸指针不拥有资源。
- 优先值语义、RAII 和 Rule of Zero。独占所有权用 `std::unique_ptr`，共享所有权只在真实共享生命周期时用 `std::shared_ptr`；禁止手写 `new`/`delete` 管理普通资源。
- 用 `enum class`、强类型、concept 和受约束模板表达意图。模板/元编程只有在改善调用端并提供清晰诊断时使用，不为消除少量重复制造难读实例化。

## 安全与正确性

- 所有对象必须初始化；避免窄化、未定义行为、悬垂 view、越界和无依据转换。优先范围 for、标准算法、`std::span` 和 `std::string_view`，同时证明被引用存储活得足够久。
- 禁止 C 风格 cast；按语义使用最窄 C++ cast，`reinterpret_cast`/unsafe 边界集中、注释并测试。宏仅用于条件编译或无法用 constexpr/template 表达的编译器接口。
- `const` 表达不修改；不要返回对临时对象或内部可失效存储的引用/view。容器迭代器和引用失效规则必须在修改路径中考虑。
- 错误策略遵循项目：异常、`expected`/状态值或错误码必须在模块边界一致。析构函数不抛异常，异常安全至少保证不泄漏和不破坏不变量。

## 并发与性能

- 共享可变状态最小化；锁使用 RAII（`lock_guard`/`scoped_lock`），明确锁顺序，不在持锁时调用未知回调或阻塞 I/O。
- 线程优先 `std::jthread` 和 `stop_token` 等有结束语义的结构；每个异步任务必须可 join/取消并传播失败。atomic 必须说明内存顺序，不默认写 lock-free 技巧。
- 优化以 profile/benchmark 为依据；先选正确复杂度和数据布局，再考虑分配、拷贝和缓存。不要用“零开销”口号绕过测量或安全抽象。

## 验证

- 运行 clang-format、clang-tidy/项目静态分析、全部目标编译和测试；高风险内存/并发变更运行适用的 ASan、UBSan、TSan。
- 测试边界、异常/失败、移动后状态、生命周期和并发；性能测试固定编译模式、硬件条件和数据集。
- 公共头文件自包含、最小 include，并验证不同编译器/平台矩阵；ABI 稳定项目不得无意改变布局、符号或异常边界。

## 官方参考

- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)
- [Standard C++ Foundation](https://isocpp.org/)
- [WG21 C++ standards papers](https://www.open-std.org/jtc1/sc22/wg21/)
