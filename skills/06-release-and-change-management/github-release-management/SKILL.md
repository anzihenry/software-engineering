---
name: github-release-management
metadata:
  owner: release-manager
  scope: "Lifecycle phase 6: release and change management"
  status: active
  review_by: "2027-02-26"
description: "在独立开发者或微型团队中，用 GitHub Actions、Environments、Deployments 和 Releases 编排发布候选、生产推进、健康判定、恢复与收口；适用于已合入版本准备交付目标环境或用户时。"
---

# GitHub 发布与变更管理

编排[阶段06发布契约](../../../docs/workflows/06-release-and-change-management.md)，不代替人类生产决定或自动取得标签、Release、Environment、部署与恢复权限。使用[发布主记录](../../../templates/delivery/release-record.md)链接原始证据，各技能不维护第二套状态。

## 依据与路由

- 先核对05正式交接、实际合入SHA和合入后端到端通过、风险/范围/问题/发布约束；不把main绿当候选verified。
- `release-candidate-preparation` 固定候选修订、完整变更组合、每平台制品/配置/迁移和验证映射。GitHub采用[Draft自动化契约](references/draft-release-automation.md)，先dry-run，再按已有精确授权创建Draft；Draft不等于正式交付。
- `release-readiness` 核对候选、环境、预演、观测/样本、恢复/值守、当前授权。支持有权人类单次、分段或预批准低风险策略；独立开发者仍保留实际人类决定。范围内后续批次不重复请示，前置未完成不执行。
- `progressive-release-execution` 一批执行，`release-health-assessment` 判断继续/观察/异常/无法判定；冲突部署/配置/开关/迁移互斥涵盖观察期，单个job的concurrency不足以证明全程互斥。
- 异常立即停止扩大，按预授权交 `release-recovery-execution`；严重或超预案转07事故/安全隐私专项。当前严重事件且标准时序不满足恢复目标才走 `emergency-change-management`。
- `release-closure` 核对八项成功条件或其他结案要求，记录真实渠道/覆盖和07接收；恢复旧基线不补记原功能成功。

## GitHub执行边界

用 `gh` 核对Actions、Environments、Deployments、Release/标签和真实保护能力；Git数据用git。用Actions执行确定性步骤、同仓库reusable workflow复用逻辑，以staging/production Environment隔离变量和密钥。默认最小权限，云身份优先OIDC，密钥仅对应environment/job。生产部署串行且不自动取消正在执行任务；观察期另有跨运行协调证据。套餐无required reviewers时使用实际人工触发/决策记录，不虚报平台强制。workflow_dispatch本身不证明授权内容完整，按候选/范围/窗口核对。

多渠道分别核对候选/授权/结果，依赖协同的单侧完成只记部分；服务按流量/实例、客户端按测试/商店、包按预发布/正式渠道推进，客户端固定签名物并预置远程开关、兼容后端和前滚路径；包/CLI先附齐Draft/Prerelease制品再授权公开。具体恢复限制按workflow。新候选或越界变化暂停受影响推进，刷新证据和批准；不得覆盖公开版本或移动已发布标签。

## 输出与停止

输出候选ID/修订及证据、就绪与独立授权、环境/渠道/批次/健康、配置迁移/恢复、过程状态及最终结果、下一动作/责任/复查时间。来源或授权不足停在对应门禁；外发通知和平台写入均按实际授权，不以编排技能名义执行。只有批准目标、验证观察、文档及运行接收齐备才成功收口。
