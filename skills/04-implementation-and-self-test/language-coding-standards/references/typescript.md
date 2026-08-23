# TypeScript 7 编码规范

## 配置与边界

- 使用项目本地 TypeScript 7.x；锁定依赖和 CI 版本。`tsconfig` 开启 `strict`，新项目同时启用 `noUncheckedIndexedAccess`、`exactOptionalPropertyTypes` 和 `noImplicitOverride`，既有项目分阶段收紧而非一次扩大 ignore。
- TypeScript 版本不等于 JavaScript 运行时能力。`target`、`lib`、模块格式和浏览器/Node 基线由项目声明，不能因编译通过就假设运行时支持。
- TypeScript 7.0 没有旧式编译器 API。依赖 typescript-eslint、Angular、Vue/Svelte/Astro 等嵌入式工具时遵循项目兼容方案，不擅自移除并行的 TypeScript 6 工具链。

## 类型与 API

- 禁止无依据的 `any`、双重断言和非空断言。外部数据从 `unknown` 开始，经 schema/类型守卫收窄；断言只用于已由边界验证但编译器无法表达的事实，并就近说明不变量。
- 用判别联合、穷尽检查和不可达分支表达状态机；不要用多个可矛盾的布尔值编码状态。
- 区分“缺失”和“值为 `undefined`”。公共对象、补丁类型和序列化边界不得随意混用可选属性与 `T | undefined`。
- 使用 `satisfies` 校验形状而保留推断；优先 `as const`/只读视图表达常量数据，但不把深层可变对象误当成真正不可变。
- 公共导出最小化；类型与值使用明确的 type-only import/export。不要建立无语义的 `utils` 聚合层或导致循环依赖的 barrel。

## 控制流、异步与错误

- Promise 必须 `await`、返回或显式处理；禁止浮动 Promise。并发执行仅在任务独立且失败语义明确时使用 `Promise.all` 等组合。
- 可取消操作接受并传播 `AbortSignal`；组件/请求生命周期结束后不得继续提交陈旧结果。
- `catch` 中把错误视为 `unknown`，先收窄再映射。抛出 `Error` 或明确错误类型，不抛字符串；边界处保留 `cause`，不泄露敏感上下文。
- 避免隐式类型强制、松散相等和依赖对象键顺序的业务逻辑。金额、时间和标识符使用明确单位/领域类型。

## 验证

- 使用项目 formatter 和 ESLint 配置；类型检查运行 TypeScript 7 的 `tsc --noEmit` 或项目等价命令。
- 固定 CI 的并行参数；只有测量证明收益后才调整 TypeScript 7 的 `--checkers`/`--builders`，资源受限环境不得盲目提高并行度。
- 测试公共行为、类型边界和失败路径；类型级测试不能替代运行时验证外部数据。

## 官方参考

- [TypeScript 7.0 release](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/)
- [TSConfig `strict`](https://www.typescriptlang.org/tsconfig/strict.html)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
