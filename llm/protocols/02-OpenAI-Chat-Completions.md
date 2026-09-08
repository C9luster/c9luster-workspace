# 02 — OpenAI Chat Completions

## 一句话定义

Chat Completions（`POST /v1/chat/completions`）是以 **role 标记的消息数组** 为核心的无状态对话 API。它是目前跨厂商移植性最好的 LLM wire format，也是绝大多数「OpenAI 兼容」网关实际实现的那一套。

## 设计目标

| 目标 | 体现 |
|------|------|
| 简单 | 一轮请求 = 完整上下文 + 生成参数 |
| 无状态 | 服务端不默认记住上一轮；历史由调用方回传 |
| 可移植 | 大量开源框架、本地推理引擎、聚合网关都以它为公共面 |

适合：聊天机器人、摘要、分类、简单 tool-calling agent（由你自己编排工具循环）。

不适合作为唯一选择的场景：强依赖厂商内置工具循环、服务端会话、Claude extended thinking、精细 prompt cache 标记等。

## 请求形状（核心字段）

```json
{
  "model": "gpt-4.1",
  "messages": [
    { "role": "system", "content": "You are a helpful assistant." },
    { "role": "user", "content": "Summarize this repo structure." }
  ],
  "temperature": 0.2,
  "max_tokens": 1024,
  "stream": false,
  "tools": [],
  "tool_choice": "auto",
  "response_format": { "type": "json_object" }
}
```

### `messages` 角色约定

| role | 含义 |
|------|------|
| `system` | 指令（部分兼容实现也接受 `developer`） |
| `user` | 用户输入 |
| `assistant` | 模型历史输出；可含 `tool_calls` |
| `tool` | 工具执行结果；用 `tool_call_id` 关联 |

多模态时，`content` 可以是字符串，也可以是 part 数组（如 `text` + `image_url`）。不同兼容后端对 vision part 的支持度不一致，移植时要单独验证。

### 常用生成与约束参数

| 字段 | 作用 | 移植注意 |
|------|------|----------|
| `temperature` / `top_p` | 采样 | 合法范围因模型而异 |
| `max_tokens` | 输出上限 | 新模型上也可能叫 `max_completion_tokens` |
| `stop` | 停止序列 | 部分推理模型忽略或限制 |
| `response_format` | JSON / json_schema | 兼容层常降级或拒绝 |
| `logprobs` | token 概率 | 很多兼容后端不支持 |
| `n` | 多样本 | 流式 + tools 时很少用 |

## 响应形状

```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "…",
        "tool_calls": [
          {
            "id": "call_abc",
            "type": "function",
            "function": {
              "name": "read_file",
              "arguments": "{\"path\":\"README.md\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ],
  "usage": {
    "prompt_tokens": 120,
    "completion_tokens": 40,
    "total_tokens": 160
  }
}
```

要点：

- 业务内容在 `choices[0].message`，不是顶层 `content`
- 文本与工具调用可以同时出现（取决于模型）
- `finish_reason` 常见：`stop` / `length` / `tool_calls` / `content_filter`

## 工具调用循环（调用方编排）

Chat Completions **不**在服务端替你跑完整个 agent loop。典型客户端循环：

```text
1. 发送 messages + tools
2. 若 message.tool_calls 非空：
   a. 本地执行每个 function
   b. 追加 assistant 消息（含 tool_calls）
   c. 追加若干 role=tool 消息
   d. 再次请求
3. 直到 finish_reason 为 stop（或你设的终止条件）
```

工具定义常见形态：

```json
{
  "type": "function",
  "function": {
    "name": "read_file",
    "description": "Read a UTF-8 text file",
    "parameters": {
      "type": "object",
      "properties": {
        "path": { "type": "string" }
      },
      "required": ["path"]
    }
  }
}
```

注意：`arguments` 在协议里是 **JSON 字符串**，不是对象。流式场景下常常是分片拼接后再 `JSON.parse`。

## 流式（SSE）

`stream: true` 时，响应为 SSE 帧，每帧大体是 `chat.completion.chunk`：

```text
data: {"id":"chatcmpl-...","choices":[{"delta":{"content":"Hel"},"index":0}]}

data: {"id":"chatcmpl-...","choices":[{"delta":{"content":"lo"},"index":0}]}

data: [DONE]
```

| 现象 | 含义 |
|------|------|
| `delta.role` | 通常只在首包出现 |
| `delta.content` | 文本增量 |
| `delta.tool_calls[].function.arguments` | 工具参数字符串增量 |
| `finish_reason` | 出现在接近结束的 chunk |
| `[DONE]` | OpenAI 风格结束哨兵；部分兼容实现省略 |

流式 usage：官方可用 `stream_options.include_usage`；兼容后端行为不一。

## 与其他协议的关键差异

| 主题 | Chat Completions | 对照 |
|------|------------------|------|
| system | 放进 `messages` | Messages 用顶层 `system` |
| 工具结果 | `role: tool` | Messages 用 `tool_result` content block |
| 主响应容器 | `choices[].message` | Responses 用 `output[]` items；Messages 用 `content[]` |
| 服务端记忆 | 默认无 | Responses 可 `previous_response_id` / Conversations |

## 何时优先选它

- 需要跨多家模型/网关切换
- 使用 LangChain、LlamaIndex 等默认适配 Chat Completions 的框架
- 自己掌控完整 tool loop，不需要厂商内置 web/computer 工具
- 本地推理（vLLM、Ollama、SGLang 等）——多数先实现这一面

## 实现检查清单

- [ ] 正确回传完整 `messages`（含 tool 轮次），避免丢 `tool_call_id`
- [ ] 流式拼接 `arguments` 后再解析 JSON
- [ ] 不要假设所有兼容后端支持 `response_format.json_schema` / vision
- [ ] token 字段名可能是 `prompt_tokens` 或被翻译成别的名字——观测层做归一化
