---
title: "隔离本地交付渠道参考"
status: current
owner: release-manager
updated: "2026-10-16"
---

# 隔离本地交付渠道参考

## 范围与前置条件

本参考落实[领域验证](domain-validation.md)、[运行观察与复验](harness-observation.md)及[质量门禁](quality-gates.md)，用于用户明确授权的合成后端/Web本地真实进程演练。它是项目侧渠道参考与内部验证工具，不增加第二层 deployment 写权限，不进入安装包。角色由实际维护者 anzihenry/执行者 Agent 映射；授权包括隔离目标的启动、受控失败、停止自身子进程和恢复，不涉及生产、云账户、远端设置或外发通知。

`local-rehearsal` 使用固定已验证的任务提交；不冒充正式发布，不关闭正式候选要求的已合入来源、GitHub Actions 构建、签名/来源证明、平台环境与生产 Go/No-Go。既有[CI/CD 模式](../skills/05-integration-validation/github-actions-bootstrap/references/cd-modes.md)和六项发布技能保持原门槛；目标平台未具备其条件时不得宣称已接通生产 deployment。将此参考扩到云/生产须先补齐真实平台身份、短期凭据、保护、观察/恢复和具体人类授权。

## 制品与兼容契约

`scripts/local_delivery.py` 的 build 从完整40位 Git commit读取固定 server.py/index.html，执行真实 Python compile，生成确定性ZIP与manifest：schema 1、source_version、文件SHA、Python主次版本、标准库依赖和限定范围。ZIP按内容SHA命名，重复构建相同输入只读核对、不覆盖；新source生成新manifest/摘要，即便示例内容相同。记录真实构建起止/工具，保留制品及原输出；本机保留责任由调用者承担，不宣称已配置自动保留或清理。

消费同一ZIP，先核对受控 expected SHA、完整source与runtime版本、精确三成员/展开大小上限256KiB/各文件摘要，再向新应用目录写入固定文件。未知schema、重复/越界/多余成员、内容篡改、runtime不支持均阻塞。没有远端凭据、签名、SBOM、数据库迁移或密钥；NA基于这个两文件公共标准库参考，不扩张为其他产品免检。旧报告/制品保持原版本，不在部署步骤重建。源码、运行工具、配置或浏览器collector改变时保存新证据并按影响重验。

## 本地目标、身份与生命周期

每个实际目标配置 target_id（唯一local UUID）、role（backend或web）、当前owner_uid；只绑定127.0.0.1，由内核分配端口。一次演练两个独立目标/进程，均消费同一当前制品，底层合成服务同时含API和Web，不能据此声称独立生产架构。进程由当前 Popen 上下文持有，不通过外部PID猜测或杀其他服务；正常、异常、超时、取消均在finally终止/等待自己的子进程，记录实际PID/returncode/stopped_at。

每次启动使用独立nonce和新目录，config/ready记录UID、角色、目标、PID、source/制品、runtime_sha256、实际端口；ready不匹配就停止自身子进程并阻塞。nonce是本机隔离对应标识，不是生产身份认证或秘密。运行工具与浏览器脚本摘要纳入记录；输入或实际身份变化不能继承旧健康结论。云OIDC、账户/区域与Environment在本范围不存在，不冒充凭据不可用测试；本机UID/目标拒绝只证明本地所有权约束。

目标目录的排他锁拒绝并发，未知/已有锁不自动删除；相同演练路径重复执行拒绝覆盖既有阶段。新的演练写新目录。取消后停止扩大、保留stage/config/log/stopped，不自动继续或将取消写成功；参考没有持久业务数据，不承诺进程停止后服务仍在线。

## 健康、失败与恢复

开始前指定同一制品、配置、目标与恢复版本；每阶段记录原始请求状态/完整合成body/摘要/时延/时间。健康窗口至少三次实际请求及间隔，响应身份必须匹配，同时验证正常API200、匿名401、真实HTML200与制品header。Web候选和恢复另运行实际隔离浏览器五种状态、键盘503/恢复与焦点、宽窄图和资源日志；部署命令/单点健康成功不能替代应用路径。

按 baseline旧制品 → candidate当前制品 → failed当前制品受控健康503 → restored原旧制品推进。失败配置是事前声明的本机fault，健康实际503则暂停、停止子进程，不扩大；恢复消费原旧ZIP并再次验证健康/API/Web。两个候选的示例业务字节可能相同，source/manifest/制品身份不同；只证明制品提升与恢复机制，不证明产品变更效果。真实健康超时负例使用200ms受控延迟/50ms客户端截止，停止子进程并保留结果；不伪称生产SLO。

异常阶段stage.json、逐次失败响应与进程日志保留；browser collector由独占Popen/进程组持有，中断通知既有Playwright关闭其自身Chromium组，有限等待/必要时强制停止本次组，保存partial stdout/stderr、可取得的部分浏览器报告和实际returncode。强制fallback不能单凭Node退出证明Chromium清理，必须核对其本次启动轨迹与子树，无证据保持阻塞。实际参考仅POSIX本机/runner，不声称Windows渠道。整体失败/取消只输出blocked/cancelled/exit1，不生成restored成功。恢复不足保持暂停；无授权、目标/候选不匹配、制品漂移、未知runtime、并发与健康失败不得继续。数据、迁移和不可逆恢复不在参考中，实际项目触发时仍需专项与人类决定。

## 执行与交接

```text
.venv/bin/python -m scripts.local_delivery exercise --root NEW_EVIDENCE --current FULL_CURRENT_COMMIT --previous FULL_PREVIOUS_COMMIT --browser-script tests/fixtures/domain-reference/browser.cjs
```

实际浏览器工具路径按[领域参考](domain-validation.md)发现已有安装，通过NODE_PATH/REFERENCE_CHROMIUM使用；不安装新生产依赖。REFERENCE_URL仅接受http/127.0.0.1根路径，无凭据/查询/片段；实际不同端口服务来自本次子进程。`--browser-timeout`在40秒内指定受控采集截止；`--cancel-after-ready`用于独立新目录内的受控取消演练；保留实际ready后的取消与stopped记录，不将其当真实发布事故。

使用[双语渠道报告](../templates/documentation/local-delivery-channel.md)，记录授权/预案、候选与不可变制品、构建/配置/依赖/工具、目标与逐阶段raw、健康/API/浏览器、失败停止/恢复/取消、剩余限制和独立核准。通过仅表示指定本地渠道演练满足声明范围；main合入、正式发布、生产和其他渠道另行判断。P1-04将核对采用/升级/真实GitHub门禁及不可变证据保留，不预先写其成功。

## 执行结果与渠道验收的区别

现有CLI允许不传browser-script；此时restored/退出0只证明已执行的HTTP制品/进程/恢复子范围，不证明完整Web渠道验收。调用者必须逐项核对实际报告的覆盖；Web候选和恢复缺真实浏览器证据仍按上文保持完整渠道验收阻塞，不能用HTML200或CLI退出码替代。仅HTTP机制试用可记录自身范围通过及浏览器not-run，保留完整渠道未通过事实。此说明不增加新CLI门禁、平台分发或生产权限。
