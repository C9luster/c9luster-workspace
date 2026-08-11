# LangGraph 知识库

本目录是对 [LangGraph](https://github.com/langchain-ai/langgraph) 的系统性整理，聚焦 **有状态 Agent / 工作流编排**：定位、Monorepo 结构、StateGraph / Pregel 架构、Checkpoint、HITL、部署工具链。

> 本地对照仓库：`workspace/github/langgraph`（`main`，核心包约 `langgraph==1.2.10`）。  
> 文档为独立知识库；概念描述基于官方 README / 源码结构整理，不依赖运行时链接。

---

## 文档索引

| 序号 | 文档 | 内容概要 |
|------|------|----------|
| 01 | [概述与定位](./01-概述与定位.md) | 一句话定义、设计目标、与 LangChain Agent 的分工 |
| 02 | [仓库结构与包依赖](./02-仓库结构与包依赖.md) | Monorepo 布局、各 libs 职责、依赖关系图 |
| 03 | [核心架构](./03-核心架构.md) | StateGraph → Pregel → Channels 三层；读源码路径 |
| 04 | [状态、通道与控制流](./04-状态通道与控制流.md) | State / reducer、Channel 类型、Send / Command |
| 05 | [持久化与关键能力](./05-持久化与关键能力.md) | Checkpoint、Store、HITL、流式、重试与缓存 |
| 06 | [Prebuilt、CLI 与 SDK](./06-Prebuilt-CLI与SDK.md) | create_react_agent、langgraph-cli、Server API |
| 07 | [选型对照与阅读路径](./07-选型对照与阅读路径.md) | 何时用 LangGraph、与 Claude Code 等对照、推荐阅读顺序 |

---

## 全局心智模型

```text
StateGraph 是画蓝图（节点 + 边 + 状态 schema）。
compile() 之后才是可执行图。
Pregel 按 superstep 调度节点，读写 Channels。
Checkpointer 把每一步状态快照下来，支持续跑与 HITL。
prebuilt / Deep Agents 是更高层的「开箱 Agent」；LangGraph 本身是底层编排运行时。
```

## 三层分层

| 层 | 回答的问题 | 典型对象 |
|---|---|---|
| 构建层 | 图长什么样、状态怎么定义 | `StateGraph`、`add_node`、`add_edge`、`Annotated[..., reducer]` |
| 执行层 | 这一步谁跑、怎么合并写 | `Pregel`、Channels、`Send` / `Command` |
| 持久化 / 部署层 | 挂了能否接着跑、如何对外服务 | Checkpointer、Store、CLI、SDK、LangSmith |

## 快速选型

| 场景 | 推荐做法 |
|------|----------|
| 快速搭 ReAct / 工具调用 Agent | `langgraph.prebuilt.create_react_agent` 或 Deep Agents |
| 复杂分支、子图、严格控制延迟 | 手写 `StateGraph` |
| 人工审批 / 中断恢复 | Checkpointer + `interrupt` |
| 多会话记忆 | Checkpoint（短）+ Store（长） |
| 本地开发 / 容器部署 | `langgraph-cli`（`dev` / `up`） |

---

*整理日期：2026-08-11*  
*对照源码：`workspace/github/langgraph`*
