---
name: backend-api-implementation-and-self-test
metadata:
  owner: implementation-lead
  scope: "Lifecycle phase 4: implementation and self-test"
  status: active
  review_by: "2027-02-26"
description: "实现并自测后端同步入口与 API 契约；适用于 HTTP/RPC 端点、输入校验、认证授权、错误语义、分页或版本兼容变更。"
---

# 后端 API 实现与自测

在既有服务边界内实现兼容、可观测的同步入口，并用测试证明契约和授权语义。领域持久化协同使用 `backend-domain-data-implementation-and-self-test`；本 SKILL 不替代消费者集成验证或安全专项审批。

## 输入

- 验收标准、API/协议契约、调用方与兼容窗口、授权模型和风险等级。
- 项目路由、序列化、错误处理、遥测、限流和版本策略。

## 工作方式

1. 明确请求/响应 schema、必填与默认值、状态/错误码、分页排序和兼容规则；区分公开契约与内部实现。
2. 在入口完成结构与边界校验，认证后按资源/动作执行授权；不依赖前端隐藏字段或调用方自律保证安全。
3. 保持错误语义稳定且不泄露内部堆栈、密钥或敏感对象；写入口明确重复请求、超时后重试和幂等行为。
4. 添加 handler/组件测试，覆盖正常、边界、畸形输入、无认证、无权限、资源不存在、冲突及依赖失败，并检查响应 schema。
5. 补齐不含敏感数据的结构化日志、指标和追踪关联，记录调用方影响及需真实协议/版本验证的内容。

## 输出格式

```markdown
## 后端 API 实现自测记录
- 入口、协议和调用方：
- schema、版本与兼容性：
- 校验、认证授权和错误语义：
- 幂等、超时和重复请求处理：
- 自动化测试与遥测：
- 未覆盖项及契约/安全验证需求：
```

## 停止条件

- 当契约、授权和错误路径有测试且入口可构建运行时，交给后端协调层和本地质量验证。
- 真实调用方、协议栈或版本兼容结论交给 `backend-contract-integration-validation`；高风险授权交给 `backend-security-authorization-validation`。
- 契约或授权模型需改变时回流方案设计，不以实现细节静默破坏兼容性。
