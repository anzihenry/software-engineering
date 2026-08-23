# Go 1.27 编码规范

## 风格与包设计

- 所有 `.go` 文件由 `gofmt`（以及项目采用时的 `goimports`）处理。遵循 Go Code Review Comments；不要用手工对齐或个人格式偏好对抗工具。
- package 名短、小写、表达职责，避免 `util`、`common`、`misc`、`api`、`types`。导出 API 保持最小，导出声明写以名称开头、面向调用者的完整 doc comment。
- 接口由消费者在需要替换行为处定义并保持小；不要为“可测试”给每个实现预建接口。接收具体类型，返回调用方真正需要的抽象。
- 零值应尽量可用；不要无意义地区分 nil slice 与空 slice，除非 JSON/协议契约需要。receiver 类型和值/指针选择在整个类型上保持一致。

## 错误、上下文与资源

- 普通失败返回 `error`，不 panic。错误必须处理、返回或在明确不可恢复的启动不变量处终止；禁止 `_` 丢弃有意义错误。
- 使用 `%w` 包装上下文并通过 `errors.Is/As` 判断；错误字符串小写开头、无结尾标点，不依赖字符串匹配做控制流。
- `context.Context` 通常作为第一个参数传入，不存入 struct，不传 nil；传播取消、deadline 和请求级值，库代码不私自替换调用者 context。
- `defer` 就近释放文件、锁、响应体和事务资源；循环中大量资源不得积到函数结束才释放。

## 并发与泛型

- 每个 goroutine 必须有明确结束条件、错误/结果接收者和取消路径；发送方负责关闭 channel，禁止通过 sleep 同步。
- 共享状态优先消息传递或小范围 mutex；持锁时不调用未知/阻塞代码。包含 mutex 的值不可复制，测试适用时运行 race detector。
- Go 1.27 支持泛型方法，但只在减少真实重复且不损害 API 可读性时使用。不要为模拟其他语言的抽象层而引入复杂约束。
- 使用 `sync.WaitGroup.Go` 等项目版本支持的结构时仍要定义 panic、取消和错误策略；并发 fan-out 必须有界。

## 验证

- 至少运行 `gofmt`、`go vet`/项目 linter、`go test ./...`；并发或共享状态变更运行 `go test -race`，性能敏感路径使用可比较 benchmark/profile。
- `go.mod` 声明 `go 1.27` 时遵循标准库版本检查；`go test` 的 `stdversion` 诊断不得被忽略。依赖变更后按项目要求运行 `go mod tidy` 并审查差异。
- 测试优先表驱动和子测试，但不为形式强行合并不同场景；错误、取消和资源泄漏必须有对应验证。

## 官方参考

- [Go 1.27 release notes](https://go.dev/doc/go1.27)
- [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments)
- [Effective Go](https://go.dev/doc/effective_go)
