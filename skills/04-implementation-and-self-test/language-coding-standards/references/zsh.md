# zsh 脚本编码规范

## 执行环境与选项

- zsh 脚本使用明确 shebang（按项目选择固定路径或 `/usr/bin/env zsh`）并由 zsh 执行。zsh 默认不兼容 POSIX sh；要求 `/bin/sh` 可移植时另写 POSIX 脚本，不混用 zsh 特性。
- 可复用函数优先以 `emulate -L zsh` 建立局部、可预测环境；按脚本失败语义显式设置命名选项，如 `ERR_EXIT`、`NO_UNSET`、`PIPE_FAIL`。严格选项不是正确性的替代，条件测试和预期失败仍需显式处理。
- 不依赖用户的 alias、交互选项、当前目录、locale 或未声明环境变量。脚本入口解析参数并验证依赖命令、文件和权限。

## 展开、参数与数据

- 默认引用参数展开和命令替换；数组使用 zsh 正确的数组语义，不能照搬 Bash 的索引、split 或 `${array[@]}` 假设而不验证。
- 文件名处理使用数组或安全 glob qualifier；不要解析 `ls` 输出，不把路径拼成空格分隔字符串。需要空匹配时显式选择行为，避免 `NOMATCH`/静默忽略差异。
- 所有外部命令参数在适用时使用 `--` 终止选项；验证用户提供的路径/模式。避免 `eval`，确需动态命令时使用数组构造命令和 allowlist。
- 局部变量用 `local`/`typeset`，常量和环境导出明确；不复用 `HOME`、`PATH` 等全局变量保存临时值。

## 错误、资源与安全

- 每个函数定义成功输出、stderr 和返回码；不要用未检查的 pipeline、command substitution 或 `|| true` 吞掉失败。
- 临时文件/目录使用 `mktemp`，保存解析后的明确路径，并通过 `TRAPEXIT`/`trap` 清理；清理函数必须能处理部分初始化和重复调用。
- 信号处理、后台任务和并行 job 必须有 wait、失败汇总和终止清理。禁止无界后台启动。
- 不在命令行、xtrace 或日志暴露密钥；启用 tracing 前确认参数安全。下载、删除、权限和远端操作需要精确目标及显式失败处理。

## 验证

- 运行 `zsh -n` 和项目 shell linter；注意 ShellCheck 主要面向 POSIX/Bash，不能证明 zsh 专属语义正确。
- 使用隔离临时目录测试空输入、空格/换行/通配符路径、缺失命令、权限失败、信号和部分完成清理。
- 测试从不同当前目录、最小环境和非交互 shell 启动；不得只证明当前用户配置下可运行。

## 官方参考

- [The Z Shell Manual](https://zsh.sourceforge.io/Doc/Release/index.html)
- [zsh options](https://zsh.sourceforge.io/Doc/Release/Options.html)
- [zsh expansion](https://zsh.sourceforge.io/Doc/Release/Expansion.html)
