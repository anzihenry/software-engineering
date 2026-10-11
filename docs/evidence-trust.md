---
title: "交付证据与独立评审可信来源"
status: current
owner: quality-lead
updated: "2026-10-11"
---

# 交付证据与独立评审可信来源

## 最小公共证据契约

沿用[追溯字段](../templates/delivery/README.md)和[文档快照/评审 schema 1](documentation-tooling.md)，不把 CI、独立评审或生产授权合成一个批准。每项证据用[双语记录模板](../templates/documentation/evidence-record.md)记录 requirement_id、实际对象、source_version、基线、环境/工具版本、实际方法及范围、带时区的执行时间、原始报告地址及摘要、来源身份、结果和局限。未执行、模拟、结构一致性、真实行为验证分别说明；模板不能预填通过。

source_version 必须给出完整 head SHA；PR 验证同时记录当前 base 和 GitHub merge 候选 SHA。只评 head 不能声称独立审过合并树；本文接入对 merge SHA 做身份/失效核对，合并树语义或运行验证仍需相应报告。候选发布补制品 SHA-256、构建 run、签名身份和环境范围；部署再记录 deployment ID、实际配置/迁移版本与范围。非发布试点明确未生成制品/部署，不伪填生产证据。

实现、配置、依赖、规范固定版本、文档/译文、证据文件、执行权限、环境、目标基线或部署身份相关变化后，旧结论失效，重验受影响范围。复用证据须列未受影响对象、原始报告和依赖关系，由独立验证者核对理由；实际未复核不得沿用 passed。当前文档 gate 重算整个文件快照，不提供选择性豁免。

## 受信维护者接入模式

本轮选择受信维护者发布独立 Agent 记录，而非新建评审服务或 App。维护者先独立取得另起上下文的评审结果，核对非作者身份、实际读取范围、原始报告、问题修正与当前快照。维护者承担来源核验责任；工具不从 JSON 自动证明 Agent 身份或内容真伪，不把此记录当 GitHub 人工批准。发布者可负责作者交接，但内容评审者必须非作者；发布身份和评审身份分开。

1. 从目标 PR 外、固定 harness checkout 运行检查。受控策略保存在目标 checkout 外，维护者核实 repository、harness_revision、publishers、required_checks（真实名称与 App ID）及固定 status context `harness-independent-review`。PR 内容不得选择可信发布者、减少必过集合或替换 harness 版本。
2. 独立评审者产生现有 schema 的 snapshot/review 和原始报告；以 binding 固定 repository、pull_request、head_sha、base_sha、merge_sha。requirements 引用本次实际核对的稳定 ID，不能用格式合法的虚构 ID代替要求对应关系。reports 保留实际原文及 SHA-256，不从作者摘要生成批准。
3. 经来源核验后，维护者把 envelope 提交到独立证据分支的 `review-evidence.json`，保留不可变完整提交；不把评审批准文件放候选 PR。使用 gh 在当前 head 发布 status，target_url 必须是同仓库 `/blob/<完整SHA>/review-evidence.json`。state 保留真实 success/failure/pending；任何必需证据缺口均不得发布 success。
4. [可信读取器](../scripts/trusted_review.py)只用 gh 获取最新同名 status、实际 creator 及其当前写权限、候选历史之外的不可变 envelope、完整作者/提交者（PR 最多 250 提交，API 列表与总数不一致即阻塞）、head/base/merge、当前 checkout、现有文档 gate 和真实 CI。要求 CI 实际 completed/success、完整 head 与指定 App 相符；skipped、pending、伪填成功或新失败 run 均拒绝。验证结束再次回读 open 状态与候选，避免候选变化后沿用早期通过。
5. 维护者在实际成功 status 和 CI 出现后审查 ruleset 差异，保留已有门禁，只增加受控 status；回读规则和正常/违规候选的服务器合入状态。在此之前只报告本地一致性/可信读取能力，不报告平台强制。

envelope 是接入封装，不改变原 snapshot/review 的 schema。顶层 schema_version=1、publisher、binding、snapshot、review、reports（text/sha256）、requirements（REQ ID 列表）；文件名与 URL 固定以避免浮动分支和任意地址。发布使用当前 authenticated gh 身份，原始 JSON 和来源核验记录在受控证据位置保存。

## 权限与能力边界

该模式仅用于全部仓库 status 写入者均为受信发布者的小团队仓库。读取器每次回读 collaborators 的写/管理员角色及 Actions 默认只读/不可自批设置；出现非受信写入者或无法审计时阻塞，转用独立受控 App/服务。GitHub 通用 status context 不提供独立 Agent 身份认证，也不能仅凭 context 名防止有写权限的人伪造。已安装 App、显式 workflow 权限、组织权限和 token 分发仍需维护者审查；此读取器不证明全部平台权限路径已安全。

可信维护者/凭据本身被攻破不在机械一致性保证内；维护者不能将自己的内容结论包装为独立 Agent 评审。对非受信写入者、复杂组织或需要自动接收外部批准的项目，不宣称本模式已满足安全门禁，必须先接通具有受控身份的服务。受信策略与读取器也须在 PR 作者控制范围外执行；把它们复制到候选后由候选随意改写，不建立信任。

```sh
"$HARNESS/.venv/bin/python" "$HARNESS/scripts/trusted_review.py" \
  --root "$PROJECT" --policy /controlled/trust-policy.json --pr 123 \
  --output /controlled/trusted-result.json
```

缺 gh/认证/权限/真实 CI/记录时保持 blocked，不回退浏览器或作者提供的 passed 文件。该命令只读，不发布 status、不改变保护、不合并或发布。local evidence 与受控 GitHub 实态各自出结论；试点实施与真实身份/权限验收由 P0-04 承担。

## 本步交付与验收

工程实现受控读取器和合成 API 负例；指南/计划/导航、文档维护/独立验证/合入路径链接本契约；新增中英证据记录模板。研究/产品/设计无目标行为变化，专题/正式发布未发生。单元测试明确为合成边界验证，不冒充 GitHub 已执行；自评、漏读、旧摘要、浮动作者批准、原始报告缺失、伪造/未完成 CI、合并候选变化及权限漂移拒绝，修正后可重新验证。四检查和独立内容验收绑定当前摘要。
