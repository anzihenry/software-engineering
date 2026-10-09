---
title: "文档机械门禁与 CI 接入"
status: current
owner: process-owner
updated: "2026-10-09"
---

# 文档机械门禁与 CI 接入

[English](documentation-tooling.en.md)

## 运行入口与资产边界

[检查器](../scripts/documentation_check.py)是第一层规范的执行工具，通过固定 harness checkout 调用，目标项目保留自己的目录、代码和开发工具。不会修改目标项目或现有安装器；harness 资产仓库不采用目标项目布局。使用现有 Python 3.14 与 PyYAML 6.0.3，无新增依赖；可用 harness 的 `.venv/bin/python`。本仓库原有 `scripts.development check` 会通过 unittest 运行门禁行为测试。

## 配置与文档登记

将[配置样例](../templates/documentation/documentation-check.json)填为目标项目 `docs/documentation-check.json`，在双语 docs/documentation 中链接并说明责任和执行方式。schema_version 为 1；standard_version 填实际固定提交，owners 将元信息角色映射到实际团队；required_checks 列出项目真实必过检查名称（尚无项目检查可为空，但要在配置说明中解释）。documents 只登记中文路径及 knowledge/initiative/release 类型；英文自动对应 `.en.md`；可选 translations 对象以中文路径为键、语言代码列表为值（例如 `"README.md": ["ja"]`），仅检查声明的其他译本及同语言导航。四个基础入口 README、CHANGELOG、docs/README、docs/documentation 必须登记。目录按内容增加，领域 README 必须登记；更深子目录按需设入口，由最近已登记双语索引链接文档。

所有 Git 可见 Markdown 必须归入 documents、legacy 或 raw。legacy 每个文件登记 owner、reason、due（ISO 日期）、evidence（存在的仓库相对证据文件）；不得重叠或逾期。本次相对 base 触及 legacy 文件必须迁移。raw 使用同样字段但不需要 due，仅限原始材料/生成报告；独立评审核对分类，不能把正式文档登记 raw 以绕过规范。原始证据只维护一份，由双语说明链接。

检查覆盖：必填元信息、类型状态、日期、责任映射、命名、配对与互链、同语言链接、相对文件链接和章节、两种语言导航与完整登记。暂支持常用行内链接、引用式链接定义、ATX 标题和显式 HTML id；不是完整 Markdown 渲染器，Setext 标题、自定义渲染锚点等先改为受支持形式或由独立评审补充核验，不能声称全部渲染语法已覆盖。工具不检查翻译语义、历史状态的正文解释或事实真实性。

## 三步交付

以下命令在目标项目外执行；`HARNESS` 是固定 checkout，`PROJECT` 是目标 Git 根目录，`BASE` 是实际对比基线的完整提交。不要为获得通过改用遗漏真实变更的基线。输出与评审 JSON 放目标项目外，避免自身摘要循环。未被 Git 忽略的新增文件也进入快照。

```sh
"$HARNESS/.venv/bin/python" "$HARNESS/scripts/documentation_check.py" check --root "$PROJECT" --base "$BASE"
"$HARNESS/.venv/bin/python" "$HARNESS/scripts/documentation_check.py" snapshot --root "$PROJECT" --base "$BASE" --author author-id --output /tmp/documentation-snapshot.json
"$HARNESS/.venv/bin/python" "$HARNESS/scripts/documentation_check.py" gate --root "$PROJECT" --snapshot /tmp/documentation-snapshot.json --review /tmp/documentation-review.json --output /tmp/documentation-gate.json
```

1. 作者先运行项目测试，保存真实报告到项目适用 evidence 位置，补齐双语和配置，然后 check/snapshot；所有作者/修改者都通过重复 `--author` 登记实际身份。快照包含整个 Git tracked + nonignored untracked 清单、删除标记、可执行权限、base、作者、配置和变更清单。被忽略的运行产物不在快照中；作为交付依据的文件必须可见，不能用 ignore 隐藏实现变更。Git 子模块、符号链接目前阻塞，需在采用前明确处理。
2. 非作者独立读取实现、变更/删除差异、全部登记文档、证据；按[评审 JSON](../templates/documentation/independent-review.json)和[统一清单](../templates/documentation/delivery-check.md)填写实际结论。inspected_files 包含删除路径时表示读取删除 diff。checks 五项都 passed，并引用 evidence_files 中实际存在且被读取的快照证据；required_checks 名称精确对应配置并全部通过。九领域影响须有处理结论、理由及文件；发现的问题需 resolved 和实际 recheck，不能伪造检查或自动生成批准。无关既有问题在外部记录中跟踪并解释不影响交付。
3. gate 重新检查全部文档、重算完整快照、检查独立身份和上下文、范围、影响、证据、必过检查和问题复核。任何变化都使旧快照失效；包括证据变化，必须重建快照并由评审者重新确认。JSON status=passed 且退出 0 才通过；失败退出 1，输出 blocked 与原因。check 仅表示结构通过，不能代替 gate。

身份、作者清单、独立性和检查结果是评审声明，工具能校验一致性而不能认证身份或证明执行真实性；身份与证据来源必须由实际评审过程、受控 CI 和权限机制保障。review JSON 由评审者输出，不由作者代填通过。快照绑定文件集合，不等同签名或平台人工批准。

身份与角色、带时区 reviewed_at、独立上下文都必须记录。

## CI 接入与信任来源

[可复用 workflow](../templates/documentation/documentation-gate.yml)提供 `documentation-gate` job，在当前事件 checkout 上运行同一 gate，harness_revision 必须完整 SHA。将模板复制到目标 `.github/workflows`，由受保护的调用流程填固定 harness 仓库/版本及当前候选的 snapshot_json、review_json。base 必须在 fetch 的提交历史中。评审候选必须等同 CI 当前 checkout（PR merge tree 也需要对应快照），不能把分支头评审直接视为合并树评审。

调用者必须从可信独立评审者或受控评审服务取得记录，并核验评审者身份、实际作者与基线、候选/运行关联、必过 CI 真正完成情况。不得从可由 PR 作者改写的仓库文件或任意用户输入取得 passed 记录；不使用 pull_request_target 执行不可信代码，也不向检查进程提供写权限或生产密钥。模板负责机械一致性，不创建可信评审服务。未接通可信来源时缺记录就阻塞。

在项目分支保护/ruleset 将实际 workflow job 配置为必过，验证正常候选通过及缺译文/旧评审失败，记录真实 Actions 运行和规则配置证据后才能声称远端已强制。项目测试及人类发布权限保持各自职责。此阶段已完成本地工具与 CI 模板；尚未替任何目标仓库启用远端规则，也不声称 Actions 已运行。

## 采用验证

使用隔离 Git 项目执行真实 CLI、保存测试报告、独立评审、通过 gate，并通过破坏翻译/实现快照验证失败；不在 harness 中创建产品目录。单元测试覆盖缺翻译、坏章节、英文导航漏项、重复配置、符号链接、未登记/受影响旧文档、旧快照、自评、评审漏读、证据缺失、必过检查失败、删除与权限变化。证据仅支持该次固定版本和环境，推广到其他项目仍须记录各自采用结果。
