# LLM 协议知识库

系统整理 **模型调用 Wire API** 与 **Agent 协作协议**：各自的设计目标、请求/响应形状、流式事件、工具调用差异，以及如何选型与迁移。

> 本目录只记录公开协议与官方语义，不绑定任何私有网关或内部实现。

## 为什么要单独学协议

LLM 没有统一的 wire format。同一句「聊天 + 工具调用」，在不同厂商里字段名、角色约定、流式事件、工具结果回传方式都不同。

不理解协议时，常见后果是：

- 以为「OpenAI 兼容」等于兼容一切，实际只兼容 Chat Completions
- 把 Claude 的 Messages 请求硬塞进 Chat Completions 客户端
- 流式解析写死一种 delta 格式，换厂商就挂
- 把 MCP / A2A 误当成「调模型」的协议

## 两层模型（先记住这个）

```text
应用 / Agent 框架
        │
        ├─ Agent 协作层：MCP（工具）、A2A（Agent 间）、ANP（去中心发现）…
        │
        └─ 模型调用层：Chat Completions / Responses / Messages / Gemini / Bedrock Converse…
              │
              └─ 传输：几乎都是 HTTPS + JSON，流式多用 SSE
```

- **模型调用层**：你的代码如何把 prompt、工具定义发给模型，并解析 token / tool_call。
- **Agent 协作层**：Agent 如何发现工具、委托其他 Agent；底层仍然要再走模型调用层。

## 文档索引

| 序号 | 文档 | 内容概要 |
|------|------|----------|
| 01 | [概述与协议分层](./01-概述与协议分层.md) | 版图、分层、碎片化原因、阅读路径 |
| 02 | [OpenAI Chat Completions](./02-OpenAI-Chat-Completions.md) | 事实标准、`messages`/`choices`、function calling、SSE |
| 03 | [OpenAI Responses](./03-OpenAI-Responses.md) | Agent 向 API、`input`/`output` items、内置工具、状态链 |
| 04 | [Anthropic Messages](./04-Anthropic-Messages.md) | Claude 原生、content blocks、thinking、cache_control |
| 05 | [Google Gemini GenAI](./05-Google-Gemini.md) | `generateContent`、`contents`/`parts`/`candidates` |
| 06 | [云厂商封装](./06-云厂商封装-Bedrock与Azure.md) | Bedrock Converse/Invoke、Azure OpenAI |
| 07 | [兼容层与网关](./07-兼容层与网关.md) | OpenAI-compatible、LiteLLM、翻译边界与陷阱 |
| 08 | [Agent 生态协议](./08-Agent生态协议-MCP-A2A-ANP.md) | MCP（工具）、A2A（Agent 间，IBM ACP 已并入）、ANP；Zed ACP 是编辑器协议 |
| 09 | [选型对照与迁移](./09-选型对照与迁移.md) | 对照表、迁移清单、决策树 |

## 四套主流 Wire API（速查）

| 协议 | 典型端点 | 设计目标 | 生态地位 |
|------|----------|----------|----------|
| Chat Completions | `POST /v1/chat/completions` | 无状态对话生成 | **事实标准**，兼容面最广 |
| Responses | `POST /v1/responses` | Agent 工作流、内置工具、可选服务端状态 | OpenAI 新主推方向 |
| Messages | `POST /v1/messages` | Claude 原生能力（thinking、精细缓存） | Anthropic 专用主路径 |
| Gemini GenAI | `…:generateContent` | Google 原生 contents/parts 模型 | Gemini 主路径 |

## 建议阅读路径

```text
1. 01 概述 → 建立分层心智
2. 02 Chat Completions → 先掌握事实标准
3. 04 Messages 与 03 Responses → 理解「同功能不同形状」
4. 05 + 06 → 补 Google / 云封装
5. 07 → 搞清兼容层能做什么、不能做什么
6. 08 → 分清 MCP/A2A 与调模型不是一层
7. 09 → 选型与迁移
```

## 相关目录

| 目录 | 关系 |
|------|------|
| [../llm/](../llm/) | 训练、对齐、部署（模型怎么造） |
| [../agent/](../agent/) | Agent 框架与 Agentic Loop（模型怎么用） |
