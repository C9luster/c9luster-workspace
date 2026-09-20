# LangGraph 知识库

本目录是对 [LangGraph](https://github.com/langchain-ai/langgraph) 的系统性整理，聚焦 **有状态 Agent / 工作流编排**：定位、架构、控制流、Checkpoint/Store、与 harness 分层，以及讨论沉淀的心智模型。

> 独立知识库；概念基于官方文档、开源实现与概念讨论整理（核心包量级约 `langgraph` 1.x）。

---

## 文档索引

| 序号 | 文档 | 内容概要 |
|------|------|----------|
| 01 | [概述与定位](./01-概述与定位.md) | 运行时定位、与 LangChain/`create_agent` 分工、DIY 边界 |
| 02 | [仓库结构与包依赖](./02-仓库结构与包依赖.md) | Monorepo 布局、各 libs 职责、依赖关系图 |
| 03 | [核心架构](./03-核心架构.md) | StateGraph → Pregel → Channels；reducer 输入示例 |
| 04 | [状态、通道与控制流](./04-状态通道与控制流.md) | State/Channel、**node/edge 棋盘隐喻**、Send/Command |
| 05 | [持久化与 Memory](./05-持久化与关键能力.md) | Checkpoint/Store 机制、接口、上下文策略（细） |
| 06 | [Prebuilt、CLI 与 SDK](./06-Prebuilt-CLI与SDK.md) | harness 分层、`create_agent`、CLI/SDK |
| 07 | [选型对照与阅读路径](./07-选型对照与阅读路径.md) | 选型、与 Claude Code 概念对照、阅读路径 |
| 08 | [心智模型与常见误解](./08-心智模型与常见误解.md) | 编排vs调度、ReAct、workflow 感、DIY |
| 09 | [钩子与旁路扩展](./09-钩子与旁路扩展.md) | Callback、middleware、图内策略节点；无跨脚手架对照 |


---

## 全局心智模型

```text
人定棋规（图/边/约束），LLM 在规内 ReAct（逐步调度）。
LangGraph = 跑循环的 runtime + 恢复/HITL 安全带，不是完整业务大脑。
Checkpoint = 短期可恢复状态；Store = 长期 KV（可选向量）；策略自管。
create_agent / Deep Agents = 更上层 harness，仍建在 LangGraph 上。
```

## 三层分层

| 层 | 回答的问题 | 典型对象 |
|---|---|---|
| 构建层 | 图长什么样、状态怎么定义 | `StateGraph`、`add_node`、`add_edge`、reducer |
| 执行层 | 这一步谁跑、怎么合并写 | `Pregel`、Channels、`Send` / `Command` |
| 持久化 / 部署层 | 挂了能否接着跑、如何对外服务 | Checkpointer、Store、CLI、SDK、LangSmith |

## 快速选型

| 场景 | 推荐做法 |
|------|----------|
| 快速工具循环 Agent | `langchain.agents.create_agent` 或 Deep Agents |
| 复杂分支 / 混确定性流程 | 手写 `StateGraph` |
| 人工审批 / 中断恢复 | Checkpointer + `interrupt` |
| 多会话记忆 | Checkpoint（短）+ Store（长）+ **自管策略** |
| 本地开发 / 容器部署 | `langgraph-cli`（`dev` / `up`） |

---

*整理日期：2026-08-11（含讨论沉淀更新）*
