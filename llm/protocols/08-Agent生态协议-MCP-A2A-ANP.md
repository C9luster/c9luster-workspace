# 08 — Agent 生态协议：MCP / A2A / ANP

## 一句话定义

这类协议解决的是 **Agent 如何连工具、如何与其他 Agent 协作/发现**，一般 **不替代** Chat Completions / Messages 等模型 Wire API。模型仍然通过模型协议被调用；MCP/A2A 挂在 Agent 运行时周围。

## 先分清两层

```text
┌─────────────────────────────────────────────┐
│  A2A / ANP —— Agent ↔ Agent                 │
│  MCP —— Agent ↔ Tools / Data                │
└─────────────────────────────────────────────┘
                    │
                    ▼
        Chat Completions / Messages / …
                    │
                    ▼
                 模型推理
```

把 MCP 当成「另一种 LLM HTTP API」是常见误解。

---

## MCP（Model Context Protocol）

| 项 | 内容 |
|----|------|
| 起源 | Anthropic 提出，后进入更广泛的生态与治理 |
| 问题 | 每个工具/数据源都要写一套定制集成 |
| 形态 | 主机（Host/Client）通过 JSON-RPC 连 MCP Server |
| 能力面 | tools、resources、prompts 等（随版本演进） |
| 传输 | stdio、HTTP/SSE 等常见 |

直觉：MCP 像「Agent 界的 USB」——模型侧用统一方式发现并调用外部能力。

**不是：** 模型厂商的 chat endpoint 替代品。

---

## A2A（Agent-to-Agent）

| 项 | 内容 |
|----|------|
| 起源 | Google 发起，并推动成为开放标准（Linux Foundation 生态） |
| 问题 | 不同框架/厂商的 Agent 如何发现彼此、委托长任务、回传结果 |
| 形态 | Agent Card 描述能力；任务（Task）导向的协作消息 |
| 与 MCP | 互补：MCP 装备单个 Agent 的工具；A2A 让 Agent 之间协作 |

典型故事：研究 Agent 通过 A2A 把「写代码」委托给编码 Agent；编码 Agent 内部仍用 MCP 读仓库、跑测试，并用 Messages/Chat Completions 调模型。

---

## ANP（Agent Network Protocol）

| 项 | 内容 |
|----|------|
| 定位 | 更偏去中心化的 Agent 发现与互联 |
| 关键词 | DID、开放发现、跨组织 |
| 与 A2A | A2A 偏企业协作与任务委派；ANP 偏开放网络身份与发现 |

适合讨论「Agent 互联网」愿景；落地成熟度与 A2A/MCP 不同，选型时看具体实现与生态，而不是只看概念完整性。

---

## ACP：不是第三套 Agent ↔ Agent 协议

缩写撞车，先看全称。

| 全称 | 谁跟谁说话 | 现状（2025-08 之后） |
|------|------------|----------------------|
| **Agent Communication Protocol**（IBM BeeAI） | Agent ↔ Agent | **已并入 A2A**（Linux Foundation / LF AI & Data）。ACP 停更，能力往 A2A 贡献；BeeAI 走 `A2AServer` / `A2AAgent` 迁移 |
| **Agent Client Protocol**（Zed，后与 JetBrains 共维） | 编辑器 / CLI ↔ Coding Agent | **仍在演进**。stdio + JSON-RPC，Claude Code / Gemini CLI / Zed / JetBrains 这条线。见 [../agent/claude-code/](../agent/claude-code/) |
| 偶见 **Agentic Commerce Protocol** 等 | 无关协作栈 | 再确认上下文，不要和上面两个混 |

所以：

- **Agent 之间**：用 **A2A**（发现、委托、长任务）。不要再把 IBM ACP 当成并行标准。
- **人面前的 IDE 控制 coding agent**：用 **Zed ACP**。它和 A2A 不在一层，也不互相替代。
- 文档里不要裸写「ACP」；必须写全称，或标明是 Client Protocol 还是已归档的 Communication Protocol。

---

## 和其他「协议」的边界

| 名称 | 层 |
|------|----|
| OpenAI Chat Completions / Responses | 模型 Wire |
| Anthropic Messages | 模型 Wire |
| MCP | Agent ↔ 工具 |
| A2A | Agent ↔ Agent（含原 IBM ACP 的协作目标） |
| Zed ACP（Agent Client Protocol） | 编辑器 ↔ Coding Agent，**不是** Agent 间协议 |
| HTTP + SSE | 传输 |

## 落地组合建议

```text
单 Agent + 很多内部工具
  → 模型协议任选 + MCP（或等价工具网关）

多团队 / 多厂商 Agent 协作
  → A2A（发现与委托）+ 各 Agent 自己的 MCP + 各自模型协议

开放互联网式发现
  → 评估 ANP；同时仍需身份、鉴权、计费与滥用治理
```

## 实现检查清单

- [ ] 架构图上分开「模型调用」与「工具/Agent 调用」
- [ ] MCP server 鉴权与最小权限（工具 = 能力扩大面）
- [ ] A2A 任务超时、取消、幂等与结果投递语义写清楚
- [ ] 文档里避免用「ACP」单缩写而不加全称
