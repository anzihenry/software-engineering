---
name: language-coding-standards
metadata:
  owner: implementation-lead
  scope: "Lifecycle phase 4: implementation and self-test"
  status: active
  review_by: "2027-02-26"
description: "为 TypeScript 7、ArkTS、Python 3.14、Swift 6.2、Kotlin 2.4、Go 1.27、SQL、zsh 和 C++20 的实现、重构与代码评审应用编码规范和最佳实践。"
---

# 编程语言编码规范

在编写、修改或评审源代码时应用一致的工程底线和对应语言约定。规范以项目已提交的 formatter、linter、编译器和版本配置为可执行事实；不得为迎合本文而静默升级工具链、重写无关代码或覆盖更具体的项目约定。

## 使用方式

1. 始终先读 [通用规则](references/common.md)。
2. 只读取本次实际修改语言对应的参考；混合语言变更读取所有涉及项：
   - `.ts`、`.tsx`、`.mts`、`.cts`：[TypeScript 7](references/typescript.md)
   - `.ets`：[ArkTS](references/arkts.md)
   - `.py`、`.pyi`：[Python 3.14](references/python.md)
   - `.swift`：[Swift 6.2](references/swift.md)
   - `.kt`、`.kts`：[Kotlin 2.4](references/kotlin.md)
   - `.go`：[Go 1.27](references/go.md)
   - `.sql`、迁移及嵌入 SQL：[SQL](references/sql.md)
   - `.zsh` 或 shebang 指向 zsh：[zsh](references/zsh.md)
   - `.cpp`、`.cc`、`.cxx`、`.hpp`、`.hh`、`.hxx` 及 C++ 模式的 `.h`：[C++20](references/cpp.md)
3. 读取最近的 `AGENTS.md`、构建文件和项目工具配置，确认实际版本、方言、格式化、静态分析和测试命令。
4. 若项目版本低于本规范基线，只使用项目支持的语法并报告差异；除非任务明确要求升级，不修改版本约束。
5. 实现后运行项目定义的 formatter、linter/type checker、构建和相关测试，记录未执行项及原因。

## 冲突优先级

从高到低遵循：用户明确要求与验收标准、作用域更近的 `AGENTS.md`、仓库已提交配置/生成代码约定、本文语言规范。格式争议交给自动格式化工具；不得手工制造与 formatter 往返冲突。

## 输出要求

交付说明至少包含：涉及语言和版本、应用的项目配置、已运行检查、未执行检查、与本规范的已知偏差。代码评审应指出具体风险和可执行修复，不以个人偏好替代项目规则。

## 停止条件

- 代码与项目版本兼容，必需自动检查通过，且行为、错误、资源和并发边界有相应证据时完成。
- 版本、SQL 方言、错误模型或工具配置不明确且会改变实现时，先从仓库事实确认；仍无法确认则停止相关决定并请求方向。
- 需要新增依赖、改变公共 API、数据库 schema、工具链版本或安全边界时，遵循对应设计/变更流程，不把它当成“编码规范修复”。
