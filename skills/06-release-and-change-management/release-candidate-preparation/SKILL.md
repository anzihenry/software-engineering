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

确保被部署和分发的是同一份已验证内容，而不是各环境临时重建的近似版本。此 SKILL 准备候选和证据，不发布标签、Release、包、商店版本或生产部署。

## 输入

- 已合入提交和集成验证证据、风险等级、版本策略与交付渠道。
- 构建/签名流程、依赖锁、目标平台、迁移和发布恢复预案。

## 工作方式

1. 固定 source SHA、基线版本和候选版本；确认版本号、标签和渠道符合项目策略，发布内容不包含未验证提交。
2. 在受控 GitHub Actions 运行中从锁定依赖构建一次，记录 workflow/run、工具链和配置；生成制品、镜像或安装包的不可变标识与摘要。
3. 对适用制品执行签名、校验、SBOM、来源证明或恶意内容扫描；密钥只在最小权限的目标 job/environment 中可用，不进入日志和普通构建 job。
4. 建立发布清单：提交、版本、制品摘要、配置/数据库迁移、兼容范围、特性开关、已知问题、恢复目标和验证证据。
5. 在 staging、内部测试或 prerelease 渠道验证这份候选本身；任何修复都产生新的提交、候选和摘要，不原地替换已验证制品。
6. 准备 Release notes 和必要的 Draft GitHub Release；公开发布前确认二进制、说明和校验信息齐全。

## 输出格式

```markdown
## 发布候选清单
- 候选版本、source SHA、基线版本：
- 构建 workflow/run 与工具链：
| 制品/镜像 | 平台/架构 | 摘要/不可变标识 | 签名/来源证明 | 存储位置 |
| --- | --- | --- | --- | --- |

- 迁移、配置、开关和兼容范围：
- 候选验证及证据：
- Release notes / Draft Release 状态：
- 已知问题、恢复目标与剩余风险：
- 结论：候选就绪 | 需重建 | 阻塞
```

## 停止条件

- 候选身份、制品摘要、验证证据和恢复关联完整时，交给 `release-readiness`。
- 制品无法追溯、构建不可重复、签名/迁移不明或候选与验证提交不一致时阻塞。
- 不为赶发布窗口修改既有制品、移动标签或覆盖公开版本。
