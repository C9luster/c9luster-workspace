# 04 — Anthropic Messages

## 一句话定义

Anthropic Messages API（`POST /v1/messages`）是 Claude 的原生对话接口：对话轮次在 `messages` 里，**system 独立顶层字段**，模型输出是 **typed content blocks**（文本、工具、thinking、引用等）。

## 设计目标

| 目标 | 体现 |
|------|------|
| 对齐 Claude 产品能力 | extended thinking、精细 prompt caching、citations、server tools |
| 结构化内容 | `content` 永远可视为 block 数组，而不是「偶尔是字符串偶尔是数组」的模糊约定 |
| 清晰的指令边界 | system 不混在 user/assistant 交替历史里 |

## 请求形状（核心字段）

```json
{
  "model": "claude-sonnet-4-5",
  "max_tokens": 1024,
  "system": "You are a careful code reviewer.",
  "messages": [
    {
      "role": "user",
      "content": [
        { "type": "text", "text": "Review this diff." },
        {
          "type": "image",
          "source": {
            "type": "base64",
            "media_type": "image/png",
            "data": "…"
          }
        }
      ]
    }
  ],
  "tools": [],
  "temperature": 0.2,
  "stream": false
}
```

### 与 Chat Completions 最容易踩的差异

| 主题 | Messages | Chat Completions |
|------|----------|------------------|
| system | 顶层 `system`（也可是 block 数组） | `messages` 里 `role=system` |
| 多模态 | `image` + `source` | 常见 `image_url` |
| 工具定义 | `{name, description, input_schema}` | `{type:"function", function:{…}}` |
| 工具结果回传 | user 消息里的 `tool_result` block | `role: tool` 消息 |
| 必填输出上限 | **`max_tokens` 通常必填** | 常可省略（有默认） |

### 消息交替约定

Anthropic 对 user/assistant **严格交替**更敏感。从多来源拼历史时，要合并连续同角色消息，或插入占位，避免直接 400。

## 响应形状：content blocks

```json
{
  "id": "msg_...",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "thinking",
      "thinking": "…",
      "signature": "…"
    },
    {
      "type": "text",
      "text": "Here is the review…",
      "citations": []
    },
    {
      "type": "tool_use",
      "id": "toolu_...",
      "name": "read_file",
      "input": { "path": "main.go" }
    }
  ],
  "stop_reason": "tool_use",
  "usage": {
    "input_tokens": 900,
    "output_tokens": 200,
    "cache_read_input_tokens": 0,
    "cache_creation_input_tokens": 0
  }
}
```

要点：

- 不要假设 `content[0]` 一定是最终文本；可能先有 `thinking`，再有 `text` / `tool_use`
- `tool_use.input` 在非流式响应里通常已是 **对象**，不是 JSON 字符串（与 OpenAI `arguments` 字符串不同）
- `stop_reason` 更细：`end_turn` / `max_tokens` / `stop_sequence` / `tool_use` / `pause_turn` / `refusal` 等

## Extended thinking

开启后，模型可返回 `thinking`（或相关）block，再给出最终答案。用途：

- 复杂推理可视化 / 审计
- 某些工作流把 thinking 与最终答案分开展示

注意：

- 计费与是否返回「完整思维链 vs 摘要」随模型与产品策略变化，以官方文档为准
- 多轮时如何回传 thinking（是否原样带回）要遵循官方约束，乱删可能影响连续性

## Prompt caching（`cache_control`）

Messages 允许在 system 或 content block 上打缓存标记，对「大文档 / 稳定前缀 + 短问题」极有效。

典型收益：

- 降低重复前缀的 input 成本
- 降低首 token 延迟（缓存命中时）

实现要点：

- 缓存粒度是 block 级，不是「整个 messages 模糊缓存」
- TTL、最小 token 门槛、哪些 block 可标记，以当前文档为准
- usage 里关注 `cache_read_input_tokens` / `cache_creation_input_tokens`

## 工具调用循环

```text
1. messages.create(tools=...)
2. 若 content 含 tool_use：
   a. 本地执行
   b. 追加 assistant 消息（含原 tool_use blocks）
   c. 追加 user 消息，content 为若干 tool_result blocks（tool_use_id 关联）
   d. 再次请求
3. 直到 stop_reason == end_turn（或业务终止）
```

`tool_result` 示意：

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_...",
      "content": "file contents here"
    }
  ]
}
```

Server tools（如官方 web search）由 Anthropic 侧执行，响应里会出现对应的 server tool 轨迹 block；与本地 function 的责任边界不同。

## 流式事件

Anthropic SSE **带显式 event 类型**，不是单一 delta 形状：

| 事件（示意） | 含义 |
|--------------|------|
| `message_start` | 消息元数据开始 |
| `content_block_start` | 新 block（text/tool_use/thinking…） |
| `content_block_delta` | 文本增量或 JSON 增量 |
| `content_block_stop` | block 结束 |
| `message_delta` | 如 `stop_reason`、usage 更新 |
| `message_stop` | 结束 |

写解析器时按 block index 组装，比「所有增量都是 content 字符串」更符合协议。

## 何时优先选它

- 主模型是 Claude，需要 thinking / 精细缓存 / citations
- 使用 Anthropic 官方 SDK、Claude Code 一类原生客户端
- 文档型、长前缀重复查询的工作负载（缓存收益大）

## 何时需要翻译层

- 同一套业务代码要同时打 GPT / Gemini / Claude
- 框架只实现了 Chat Completions 客户端

此时常见做法：业务仍用一种内部 IR，或经网关把 Messages ↔ Chat Completions 互译；但 **thinking / cache_control / citations** 往往无法无损映射。

## 实现检查清单

- [ ] `max_tokens` 必填意识；别照搬 Chat Completions 客户端默认
- [ ] system 不要塞进 messages 还以为「兼容就行」
- [ ] 工具结果用 `tool_result`，不要发 `role: tool`
- [ ] 流式按 event 类型状态机解析
- [ ] 需要无损 Claude 能力时，坚持原生 Messages，而不是经 Chat Completions 兼容层硬转
