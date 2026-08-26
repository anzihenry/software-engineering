---
exercise_name: low-risk-copy-change
exercise_version: 1
risk_level: low
scenario_type: copy-change
lifecycle_stages: [1, 2, 3, 4, 5, 6, 7, 8]
required_templates:
  - opportunity-record.md
  - requirements-risk-package.md
  - solution-decision.md
  - verification-matrix.md
  - change-handoff.md
  - release-record.md
  - incident-record.md
  - outcome-retrospective-actions.md
---

# 低风险演练：空状态文案调整

## 演练目标

验证团队能否对纯文案变化精简流程，同时保留可验收性、当前版本证据、发布观察和结果回流，不把“小改动”理解为无须验证。

## 初始条件

- Web 项目列表空状态当前显示“暂无项目”，用户研究表明新用户不知道下一步，但本次不新增按钮、链接、埋点或业务逻辑。
- 仅调整现有简体中文资源为“还没有项目，创建后会显示在这里”；其他语言、API、权限、数据和布局组件不在范围内。
- 建议记录链：`OPP-COPY-001` → `REQ-COPY-001` → `DES-COPY-001`/`VER-COPY-001` → `CHG-COPY-001` → `REL-COPY-001` → `INC-COPY-001`（仅发生异常时启用）→ `RET-COPY-001`。

## 阶段 1：需求与机会

- 使用[机会记录](../../templates/delivery/opportunity-record.md)记录研究证据、受影响用户、新用户空状态理解率或支持咨询基线。
- 门禁：业务负责人确认问题值得解决，成功指标不是“文案已修改”，而是可观察的理解或支持结果。
- 注入：利益关系人顺便要求给文字增加跳转链接。期望决定是拆分新范围并重新评估，而不是继续标记为低风险文案。

## 阶段 2：澄清与立项

- 使用[需求与风险包](../../templates/delivery/requirements-risk-package.md)定义准确文案、显示条件、允许换行、缩放/屏幕阅读器要求和非目标。
- 门禁：确认没有交互、路由、埋点、数据或多语言回退变化；否则重新分级。

## 阶段 3：方案与计划

- 使用[方案决策](../../templates/delivery/solution-decision.md)简要记录复用现有资源键、不修改组件结构以及用版本回退恢复。
- 在[验证矩阵](../../templates/delivery/verification-matrix.md)映射资源检查、代表性视口截图、200% 缩放、屏幕阅读器文本和现有自动测试。
- 门禁：无需召开重型设计评审，但变更路径、验证方法和恢复方式明确。

## 阶段 4：开发与自测

- 只修改目标资源，更新[变更交接](../../templates/delivery/change-handoff.md)中的当前 head SHA、本地命令、截图和未执行项。
- 注入：窄屏截图出现三行换行但没有遮挡。参与者需依据事先验收标准判断，而不是临时把任何视觉差异当失败或直接忽略。
- 门禁：项目规定的格式、静态检查和相关测试通过，diff 没有夹带组件重构。

## 阶段 5：集成验证

- PR 的固定 required check 对最新 SHA 成功；独立评审确认文案、范围、可访问性和截图证据。
- 更新[验证矩阵](../../templates/delivery/verification-matrix.md)和[变更交接](../../templates/delivery/change-handoff.md)，旧提交截图不得替代当前提交。
- 门禁：无阻塞意见、无未说明范围扩大，结论为可合入。

## 阶段 6：发布与变更管理

- 使用[发布记录](../../templates/delivery/release-record.md)关联 source SHA、同一构建/部署、目标环境、短观察窗口和回退提交。
- 低风险连续发布可以自动推进，但不得省略版本身份、部署结果和页面健康检查。

## 阶段 7：运行与支持

- 观察页面错误、关键前端健康信号和相关用户反馈。无异常时记录“未触发事件”，不创建虚假事故。
- 若文案遮挡主要操作或导致明显误导，使用[事件记录](../../templates/delivery/incident-record.md)记录影响并按预案回退。

## 阶段 8：度量与复盘

- 使用[效果复盘与行动](../../templates/delivery/outcome-retrospective-actions.md)比较观察窗口内理解指标或支持咨询，记录样本限制。
- 未改善时回到问题假设，不通过继续堆文案修改来伪造成功。

## 演练通过条件

- 全流程保持低风险边界，新增链接/逻辑要求被拆分或重新分级。
- 证据对应最新版本且覆盖代表性视觉和可访问性风险。
- 发布和效果记录可以从 `REL-COPY-001` 回溯到机会与需求；没有异常时不制造 `INC-COPY-001` 的假数据。
