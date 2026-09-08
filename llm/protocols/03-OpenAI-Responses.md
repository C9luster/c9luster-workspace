# 03 — OpenAI Responses

## 一句话定义

Responses API（`POST /v1/responses`）是 OpenAI 面向 **Agent 工作流** 的新一代接口：输入输出以 typed **items** 组织，可在单次请求内驱动内置工具，并支持用响应 ID 链接多轮上下文。

OpenAI 文档将其定位为长期推荐方向；Chat Completions 仍广泛支持，但新能力会优先落在 Responses。

## 设计目标

| 目标 | 体现 |
|------|------|
| Agent-first | 内置 web search、file search、code interpreter、computer use、远程 MCP 等 |
| 结构化输出项 | 文本、推理、工具调用作为并列 `output` items，而不是全塞进一条 message |
| 降低多轮样板代码 | `previous_response_id` 或 Conversations，减少每次回传全量历史 |
| 更好的缓存利用 | 连续回合复用服务端已存上下文时，可减少重复上传 |

## 请求形状（核心字段）

```json
{
  "model": "gpt-5",
  "input": "Explain how TCP handshake works.",
  "instructions": "Answer like a senior network engineer.",
  "tools": [
    { "type": "web_search_preview" }
  ],
  "store": true
}
```

`input` 可以是：

- 纯字符串（简单问答）
- item 数组（多模态、工具结果回灌、更复杂上下文）

与 Chat Completions 对比：

| Chat Completions | Responses |
|------------------|-----------|
| `messages: [{role, content}]` | `input`（string 或 items） |
| `system` 角色消息 | 常用顶层 `instructions` |
| 客户端编排全部工具 | 可声明内置工具，由服务端参与执行循环 |
| 每次回传全历史 | 可用 `previous_response_id` 链接 |

## 响应形状：`output` items

Responses 不再用单一 `choices[0].message.content` 作为唯一载体，而是返回 **typed output 列表**。概念上类似：

```json
{
  "id": "resp_...",
  "status": "completed",
  "output": [
    { "type": "reasoning", "summary": [{ "type": "summary_text", "text": "…" }] },
    { "type": "message", "role": "assistant", "content": [{ "type": "output_text", "text": "…" }] },
    { "type": "function_call", "name": "…", "arguments": "…", "call_id": "…" }
  ],
  "usage": { "input_tokens": 100, "output_tokens": 50 }
}
```

SDK 常提供便捷属性（如 `output_text`）把文本 item 拼起来；手写解析时必须按 `type` 分支。

### 常见 item 类型（心智模型）

| 类型（示意） | 含义 |
|--------------|------|
| `message` / `output_text` | 对用户可见的文本 |
| `reasoning` | 推理/摘要轨迹（是否返回完整思维链取决于产品策略） |
| `function_call` | 要你本地执行的函数 |
| 内置工具相关 item | web/file/computer 等的调用与结果 |

具体 type 名称以官方当前文档为准；写适配器时用穷尽匹配 + unknown fallback。

## 状态管理的两种姿势

### 1. `previous_response_id`

```text
turn1: responses.create(input=...) → resp_1
turn2: responses.create(input=..., previous_response_id=resp_1) → resp_2
```

调用方仍要自己保存最新 response id，但不必每次重传整段历史。

### 2. Conversations（更重的服务端会话）

把多轮积累交给服务端 conversation 对象，适合持久会话产品。代价是：会话生命周期、删除/合规、多租户隔离都要按云侧模型设计。

`store: true/false` 影响响应是否被服务端保留，从而能否被后续 ID 引用——生产环境要明确数据留存策略。

## 工具：内置 vs 自定义 function

| 类别 | 谁执行 | 典型用途 |
|------|--------|----------|
| 内置工具 | 服务端（或托管环境） | 搜索、跑代码、操作计算机、连远程 MCP |
| 自定义 function | 你的后端 | 访问私有 DB、内部 API、业务动作 |

内置工具是 Responses 相对 Chat Completions 的最大产品差异：许多「agent 样板代码」被收进平台。

自定义 function 的回灌方式也是 item 化的（用 call id 关联结果），不要按 Chat Completions 的 `role: tool` 消息假设去硬套。

## 流式

Responses 流式同样走 SSE，但事件是 **按 item 生命周期** 拆分的（创建 item → 增量 → 完成），而不是只有一种 `delta.content`。

实现要点：

- 用事件类型驱动状态机，而不是假设每帧都有文本
- 文本增量、工具参数增量、完成/失败事件分开处理
- 最终以 `status` / 完成事件为准，而不是只靠 `[DONE]`

## 何时优先选它

- 产品核心是多步 agent，且希望使用 OpenAI 内置工具
- 需要 `previous_response_id` 降低重复上下文成本
- 新项目以 OpenAI 为主要供应商，愿意跟官方长期方向走

## 何时不要急着上

- 必须同时裸连多家模型且拒绝翻译层——Responses 原生生态仍窄于 Chat Completions
- 只做单轮补全，items 模型收益有限、复杂度更高
- 团队已有成熟 Chat Completions tool loop，迁移成本高于收益

## 与 Chat Completions 迁移直觉

| 旧概念 | 新概念 |
|--------|--------|
| `messages` | `input` (+ `instructions`) |
| `message.content` | `output` 里的 message/text items |
| `tool_calls` | `function_call` items |
| 手动拼历史 | `previous_response_id` / Conversations |
| 外挂搜索工具 | `tools: [{type: "web_search_…"}]` 一类内置声明 |

官方提供迁移指南；落地时优先改「会话状态」与「工具结果回灌」两条路径，而不是只改 URL。

## 实现检查清单

- [ ] 解析按 `output[].type` 分支，不假设只有一段文本
- [ ] 分清内置工具（服务端）与 function（本地）的执行责任
- [ ] 明确 `store` / 会话留存与隐私合规
- [ ] 不要把 Responses 客户端指到「仅 Chat Completions 兼容」的 base URL 还期望行为一致
