---
title: "项目采用、知识加载与复验"
status: current
owner: implementation-lead
updated: "2026-10-12"
---

# 项目采用、知识加载与复验

## 采用清单与顺序

采用完整固定 harness checkout 或明确等价资产，不扩大现有安装器的第一层分发范围。固定仓库、完整提交与资产路径；按[项目入口](../templates/codex/AGENTS.md)合并到已有 AGENTS，保留项目规则，不能直接覆盖。先按[分支规范](git-branch-workflow.md)检查归属/fetch/建立任务分支，再做任何配置或文档修改。

目标项目在 docs/harness-adoption.json 登记 schema_version=1、harness_revision、scope（github/offline/non-github）、language_references（仅实际涉及语言名称）、entrypoints（全部 Git 可见 AGENTS.md 路径到 SHA-256）、global_context（全局指令实际作用域评估）、unresolved_overrides、protected_branches、owners（角色到实际人）、task_facts（唯一任务事实来源）、independent_review（实际机制/受控记录位置）、commands。各入口摘要改变后重新核对覆盖关系；摘要相同仍需检查语义，不能把目录覆盖、命令或来源冲突仅当路径问题。

commands 精确包含 format/lint/build/test/documentation，值为实际 argv 列表。可替换 `{harness}`、`{project}`、`{python}`、`{ruff}`、`{base}`；只替换这五种字面占位串，其他 argv 花括号原样保留；不运行 shell 展开，子进程仍继承调用者身份与环境，执行前由调用者审查 argv 并提供受控环境。已配置项目具体工具优先，不因为模板而升级或新增生产依赖。工具不适用须有项目事实与独立核对，不能用成功空命令代替检查；当前运行器要求完整可执行命令集，不支持命令豁免。报告保留实际 head、工作树 dirty 状态及 Git 可见文件的摘要/执行位（沿用文档检查器的仓库内规范路径与禁止 symlink 契约）；命令执行期间目标对象/分支或知识 checkout 变化则阻塞并保留可回读的前后绑定；删除文件、Git/权限错误等导致末尾不可回读时仍保留初始绑定、实际报告与错误，不把未提交内容当 head 提交。失败、不可执行和超时保留已执行报告与失败命令的可用输出；尚未运行的命令不记通过。

规范、语言 common/适用 references、分支/文档技能及模板必须实际可访问；GitHub 另需仓库规范和两个 bootstrap 技能。目标双语 docs/documentation 固定规范版本、角色、检查、CI、独立记录和迁移位置；root README/CHANGELOG/docs 索引等按原规范登记。不一次建立空领域目录。已有项目先盘点，保留未触及旧资产的限期迁移；受影响内容立即遵守规范，不能借迁移豁免。

## 三类证据与复验

1. 运行 [采用诊断器](../scripts/harness_adoption.py)，核对固定 checkout、必需技能/规范/适用 references、全部局部 AGENTS、真实命令配置、责任和任务分支。默认只读；`--run` 执行已审查的项目命令，不提升调用者权限或授予生产授权。available/checks-passed 仅说明可访问/命令实测，不代表 Agent 已加载。
2. 在隔离项目由独立 Agent 执行真实研发任务（如源码评审），观察实际读取根/局部入口、按需读取 SKILL 与 matching references、使用项目真实命令和停止边界；保留原始工具/命令记录及结果。不能只接受“我已加载”的自述。独立 Agent 内容评审仍不能是本次作者。
3. GitHub 项目审计 gh 身份、真实 CI/App、受控评审发布权限和保护规则，按[可信来源](evidence-trust.md)接入并回读；正常与违规候选分别记录平台 check 和合入状态。保持原必过检查和人类授权，不以 doctor、本地模拟或安装文件替代平台验收。

```sh
"$HARNESS/.venv/bin/python" "$HARNESS/scripts/harness_adoption.py" \
  --root "$PROJECT" --harness "$PINNED_HARNESS" --base "$BASE" --run
```

本工具可从本次固定工具版本运行，知识资产 checkout 单独记录其不可变版本。首次验证新工具时可用文件摘要绑定工具、固定已有知识提交；提交后保留工具 commit 对应关系。不把开发中的工作树称为已发布版本。

新项目按清单最小接入；成熟项目合并入口、检查既有 CI、逐项记录覆盖/迁移，不取代原流程。非 GitHub/离线项目据实际平台说明 GitHub 操作不适用，仍执行本地规范、文档、独立评审与明确离线基线。缺网络/权限的 GitHub 项目记远端阻塞，不能更改 scope 来伪造采用完成。

更改全局/根/目录入口、固定版本、技能、命令、配置、责任或信任/平台规则后重验相关范围。未知高风险、不可访问资产、未解决覆盖、不可执行命令、缺译文、旧评审、必过失败和治理漂移均阻塞相应交付。采用记录使用[双语模板](../templates/documentation/adoption-record.md)，明确本地、行为观察、远端和未执行范围。

## 实施验证边界

本轮结果由[试点报告](harness-p0-validation.md)保存固定版本、原始报告、真实 PR/check/规则和正反例；不把一个合成项目推广为所有项目已成功。试点 PR 关闭而不合入，受保护合入只验证服务器是否阻塞违规候选，不执行生产部署/发布。此资产仓库继续保持 skills/workflows/templates 组织。
