---
name: release-candidate-preparation
metadata:
  owner: release-manager
  scope: "Lifecycle phase 6: release and change management"
  status: active
  review_by: "2027-02-26"
description: "把已验证提交固化为可追溯、可重复提升的发布候选及发布清单；适用于创建版本、标签、签名制品、镜像或 GitHub Draft Release 之前。"
---

# 发布候选准备

按[候选身份契约](../../../docs/workflows/06-release-and-change-management.md#正式接收与候选身份)固定发布对象，输出到[发布主记录](../../../templates/delivery/release-record.md)。准备候选不自行发布标签、Release、包、商店版本或部署生产。

## 输入与判断

核对05正式交接：批准范围/验收、PR及实际main合入SHA、CI/独立/专项/前后端到端、问题和配置/兼容/迁移/恢复约束。缺口退回受影响范围，保留有效证据，接收不等于验收通过。

- 按项目版本/标签/渠道策略固定唯一候选ID/修订、版本/基线/源码SHA和完整包含变更，不能包含未验证提交。包含A/B但计划只交A，核对B实际生效、隔离及证据；范围不明按完整影响评估。
- 组合多个变更时覆盖组合新增风险和候选必需验证，可复用仍有效的源码证据，不凭逐PR通过替代组合验证。
- 在受控Actions从锁定依赖构建一次，记录workflow/run、工具链、构建参数和来源；每个平台/架构/交付对象有不可变标识、摘要、存储位置和适用签名、SBOM/来源证明/扫描。密钥限最小权限job/environment，不进入日志和普通构建job。
- 固定配置版本、开关、迁移、依赖、兼容窗口、恢复目标、已知问题及Release notes。注明证据分别覆盖源码、最终制品或后续目标环境节点。
- staging/内部/prerelease提升同一制品并验证部署、迁移、路径和恢复。多平台分别绑定；必要签名/打包/商店转换记录输入输出映射并验证实际分发物。
- 源码、依赖、构建参数或制品变化生成新修订；配置/开关/迁移/范围变化更新记录并重评受影响验证和授权，不覆盖旧制品和失败历史。

## 输出与停止

输出候选清单：身份/组合、构建/工具/依赖、平台制品与摘要/证明、执行条件/兼容/恢复、实际验证和待后续节点、文档/Draft状态、候选就绪或阻塞及下一动作。身份明确且候选必需验证通过才交 `release-readiness`；无法追溯、构建不可重复、候选与证据不符、签名/迁移或组合风险不明则阻塞。不为赶窗口覆盖公开版本、移动标签或把Draft当发布成功。

## 隔离本地渠道参考

已明确授权的合成本地渠道按[本地交付契约](../../../docs/local-delivery-channel.md)记录制品、实际进程与应用路径、失败停止/恢复/取消，使用[双语渠道报告](../../../templates/documentation/local-delivery-channel.md)。其local-rehearsal结论不关闭本技能正式候选/平台/生产门槛，不改变第二层分发或写权限；其他渠道仍须补真实身份/保护/授权与独立证据。
