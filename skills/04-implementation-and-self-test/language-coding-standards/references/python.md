# Python 3.14 编码规范

## 风格与结构

- 遵循 PEP 8 和项目 formatter；格式由工具决定，不在同一变更混入无关格式化。模块和包按领域职责命名，避免泛化的 `utils.py`。
- 导入只放模块级真实依赖；类型专用且昂贵/循环的导入可放在 `TYPE_CHECKING`。禁止修改 `sys.path` 绕过包结构。
- 用小函数、数据类和组合表达行为；继承用于真实的可替换关系。可哈希/值对象优先不可变 `dataclass(frozen=True)` 等表示。

## 类型与数据

- 对公共 API、领域边界和非显然内部函数提供类型标注，并在 CI 运行项目选定的静态类型检查器；Python 运行时不会执行类型标注。
- Python 3.14 新代码使用内置泛型、`X | None` 和 `type Alias = ...`。参数尽量接收 `Sequence`、`Mapping`、`Iterable` 等所需最小协议，返回具体且有所有权含义的类型。
- `Any` 只限隔离的动态边界，并尽快验证/收窄。外部 JSON、环境变量和数据库行不可仅靠 `cast` 变成可信领域对象。
- 禁止可变默认参数；区分 `None` 哨兵、空集合和缺失值。避免把布尔参数堆成隐式状态机。

## 错误、资源与并发

- 捕获最窄异常；禁止裸 `except`、静默 `pass` 和用异常控制普通分支。转换异常时使用 `raise ... from ...` 保留因果链。
- 文件、锁、事务和临时资源使用上下文管理器；路径使用 `pathlib`，文本 I/O 明确 encoding。
- 异步代码不调用阻塞 I/O；任务必须有所有者、取消和异常收集。相关并发任务优先使用 `asyncio.TaskGroup` 等结构化方式，不创建无人等待的后台任务。
- 日志使用结构化参数而不是预拼接敏感字符串；库代码不配置全局日志、事件循环或进程状态。

## 验证

- 运行项目 formatter、linter、类型检查、测试和适用的导入/打包检查；库代码还要在声明的最低 Python 版本验证。
- 测试使用临时目录、固定时钟/随机源和显式依赖，避免依赖执行顺序、真实网络或全局环境。
- 对解析、序列化、异常映射和 async 取消路径编写负向测试；mock 只替代边界，不复制被测实现。

## 官方参考

- [PEP 8](https://peps.python.org/pep-0008/)
- [Python 3.14 typing](https://docs.python.org/3.14/library/typing.html)
- [Python 3.14 asyncio](https://docs.python.org/3.14/library/asyncio.html)
