---
title: "本地交付渠道报告模板"
status: current
owner: release-manager
updated: "2026-10-12"
---

# 本地交付渠道报告

[English](local-delivery-channel.en.md)

按[本地渠道契约](../../docs/local-delivery-channel.md)替换占位，使用实际项目角色；模板不是执行证据。

## 追溯、授权与范围

- record_id / related_records / source_version / created_at / updated_at（带时区）：
- 固定候选/恢复提交、head/base/merge、制品SHA、构建起止/原日志/工具/配置/依赖/保留责任：
- 实际owner/executor/独立reviewer、具体本地授权与停止/恢复预案：
- target_id/role/UID/nonce/PID/实际端口、runtime/browser脚本摘要；不适用平台字段的事实：

## 逐阶段原始证据

| 阶段/实际时间 | 同一制品与目标身份 | config/ready/health/API/Web/browser原报告及SHA | 健康窗口与判定 | 停止/暂停/恢复/取消和实际returncode |
| --- | --- | --- | --- | --- |

保留baseline/candidate/failed/restored原记录；受控fault与真实异常区分，失败和取消不能改成成功。缺授权/身份/摘要、篡改、并发、超时或健康失败阻塞扩大；恢复使用原旧制品并重验关键路径，不在部署步骤重建。仅停止自己的子进程。

## 限制、文档与交接

记录合成范围、NA原因、观察窗口、未验证平台/身份/迁移/产品效果与剩余问题；不把本地演练当正式发布或生产授权。更新受影响指南/长期文档与英文，独立核准实际源码、产物、工具及证据快照。保留失败历史、恢复后的事实及后续复验任务。
