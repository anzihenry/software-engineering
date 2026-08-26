---
name: harmonyos-validation
metadata:
  owner: quality-lead
  scope: "Lifecycle phase 5: integration validation"
  status: active
  review_by: "2027-02-26"
description: "验证 HarmonyOS 变更在目标 API、设备形态和真实系统能力下的行为；适用于合入前安装升级、Ability 生命周期、分布式能力、辅助功能与性能验证。"
---

# HarmonyOS 验证

验证 HarmonyOS 自测无法充分覆盖的 API、设备、安装升级、系统集成和非功能风险，并界定结论适用范围。跨移动平台一致性和整体矩阵由 `mobile-validation` 汇总；本 SKILL 不执行 AppGallery Connect 或应用市场发布。

## 输入

- 验收标准、风险等级、HarmonyOS 自测记录、待验证构建和支持的 API/设备矩阵。
- 测试账号与数据、后端/通知/分布式设备等依赖环境、历史版本、性能基线和观测手段。

## 工作方式

1. 根据支持策略、用户分布和变更触点选择 compatible/主流/target API、手机/平板/折叠屏/PC 等适用形态及 Emulator/真机组合，并说明未覆盖范围。
2. 验证全新安装、覆盖升级、冷/热启动、UIAbility 前后台、窗口与设备形态变化、进程终止和资源压力后的恢复；检查 Preferences/ArkData、文件和会话兼容性。
3. 覆盖权限的未请求/允许/拒绝状态，以及 Want、通知、后台任务、系统分享、适用 ExtensionAbility 和分布式/跨设备能力；真机或多设备能力不得只靠 Emulator 外推。
4. 检查不同尺寸、方向、折叠/展开、多窗口、字体缩放、深色模式、键盘和本地化；使用系统辅助功能验证关键路径的语义、顺序、焦点和动态反馈。
5. 按风险测量启动、响应、帧表现、内存、能耗、崩溃与卡死，并检查 release 构建的 ArkGuard/资源处理、module 配置和系统能力没有改变关键行为；实际通过 HarmonyOS CLI 执行矩阵或采集测试报告、HiLog、截图和性能数据时组合 `mobile-cli-execution`，保留目标、API 和构建身份。

## 输出格式

```markdown
## HarmonyOS 验证报告
| 要求/风险 | API、设备形态与构建 | 场景 | 证据/指标 | 结果 |
| --- | --- | --- | --- | --- |

- 安装升级、Ability 生命周期与数据兼容结论：
- 权限、Want、通知、后台与系统/分布式能力结论：
- UI、多设备适配、辅助功能与本地化结论：
- 启动、响应、内存、能耗与稳定性结论：
- 未覆盖矩阵、环境限制及影响：
- 总结：通过 | 有条件通过 | 阻塞 | 环境不可信
```

## 停止条件

- 当 HarmonyOS 高风险组合和系统集成已有可信证据，且未覆盖范围已明确处置时，将结果交给 `mobile-validation` 或 `merge-readiness`。
- 功能或平台实现失败回流 `harmonyos-implementation-and-self-test`；支持范围、能力、签名或数据方案缺口回流方案与计划。
- 关键真机/多设备能力、升级路径或性能要求无法验证时，不给出无条件通过结论。
