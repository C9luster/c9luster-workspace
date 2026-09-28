# DeerFlow 知识库

本目录整理 DeerFlow 2.0（Deep Exploration and Efficient Research Flow）的 Agent harness 机制：交互形态、Agentic Loop、上下文工程、多 Agent 编排、工具与安全边界、扩展机制与会话持久化。

> 独立知识库；机制描述以 DeerFlow 公开仓库实现与文档为准。扩展点对应 LangGraph / LangChain `create_agent` 的 middleware 链，以及 `plugins` / `deerflow.extensions` 插件体系。

---

## 文档索引

| 序号 | 文档 | 内容概要 |
|------|------|----------|
| 01 | [概述与架构](./01-概述与架构.md) | 产品定位、部署分层、Harness 包布局、Lead Agent 组装 |
| 02 | [交互形态与 Agentic Loop](./02-交互形态与Agentic-Loop.md) | Thread/Run、SSE、澄清中断、模型与工具循环 |
| 03 | [上下文管理](./03-上下文管理.md) | ThreadState、Summarization、Memory、Skills 注入 |
| 04 | [子 Agent 与多 Agent 编排](./04-子Agent与多Agent编排.md) | `task`、SubagentExecutor、并发与限额 |
| 05 | [工具系统与能力边界](./05-工具系统与能力边界.md) | 内置工具、Sandbox、MCP、技能与 ACP |
| 06 | [安全、权限与 Plan Mode](./06-安全权限与Plan-Mode.md) | Sandbox、Guardrails、clarification、授权过滤 |
| 07 | [扩展机制](./07-扩展机制.md) | Middleware、Plugins / Extensions、Skills、MCP |
| 08 | [会话持久化与恢复](./08-会话持久化与恢复.md) | Checkpointer、StreamBridge、Uploads、Artifacts |
| 09 | [特性与模式索引](./09-特性与模式索引.md) | 能力清单、Lead/Subagent 差异、部署组件 |

---

## 定位摘要

DeerFlow 2.0 以 LangGraph 与 LangChain `create_agent` 为核心，提供可部署的 **super agent harness**：沙箱、技能、MCP、子 Agent、记忆，以及可插拔 middleware / extensions。部署形态通常为 Gateway + Frontend + Nginx（可选 Provisioner）。
