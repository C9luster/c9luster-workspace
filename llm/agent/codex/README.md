# Codex Agent 框架知识库

本目录是对 OpenAI Codex（终端侧 Coding Agent）的系统性整理，聚焦 **Agent 层面**：交互形态、Agentic Loop、上下文工程、多 Agent 编排、工具与安全边界、扩展机制与会话持久化。

> 独立知识库；概念与机制描述基于 Codex 开源实现（`codex-rs/`）整理。

---

## 文档索引

| 序号 | 文档 | 内容概要 |
|------|------|----------|
| 01 | [概述与架构](./01-概述与架构.md) | 产品定位、分层架构、核心设计原则、与同类工具差异 |
| 02 | [交互形态与 Agentic Loop](./02-交互形态与Agentic-Loop.md) | CLI/TUI/Exec/App-Server、Turn 准入、采样循环、Steer、长任务 yield/poll |
| 03 | [上下文管理](./03-上下文管理.md) | WorldState Diff、双轨历史、Compaction、AGENTS.md、Memories |
| 04 | [子 Agent 与多 Agent 编排](./04-子Agent与多Agent编排.md) | Multi-Agent V2、spawn/fork、Roles、Agent Graph |
| 05 | [工具系统与能力边界](./05-工具系统与能力边界.md) | ToolRouter、apply_patch、Unified Exec、MCP、Code Mode |
| 06 | [安全、权限与 Plan Mode](./06-安全权限与Plan-Mode.md) | Sandbox、ExecPolicy、Approval、Guardian、Plan |
| 07 | [扩展机制](./07-扩展机制.md) | Skills（@ 注入）、Hooks、Plugins、Extension API |
| 08 | [会话持久化与恢复](./08-会话持久化与恢复.md) | Rollout JSONL、ThreadStore、Resume/Fork/Revert |
| 09 | [特性与模式索引](./09-特性与模式索引.md) | Multi-Agent、Code Mode、Remote Exec、Collaboration Mode 等 |

---

## 全局心智模型

```text
Thread 是一条可恢复的对话世界线。
Session 是 Thread 的运行时（同一时刻最多一个 active turn）。
Turn 是一次用户目标驱动的采样+工具循环。
Step 是 Turn 内的一次 model sampling 快照。
WorldState 是结构化「世界事实」，按 diff 注入，而不是整段 system prompt 重贴。
ToolOrchestrator 是「审批 → 选沙箱 → 执行 → 升级重试」的统一闸门。
Collaboration 工具是多 Agent 的一等公民命名空间，禁止经 exec 间接调用。
```

## 五层系统分层

| 层 | 回答的问题 | 典型对象 |
|---|---|---|
| 入口层 | 用户通过什么启动 | CLI Multitool、TUI、`codex exec`、IDE / App |
| 协议层 | UI 与 Core 如何解耦 | App-Server JSON-RPC（thread/turn 生命周期） |
| 编排层 | 谁管理 Thread / Turn / Steer | ThreadManager、Session、turn_input 准入 |
| 运行层 | 谁真正采样与执行工具 | run_turn、ToolCallRuntime、Exec Server |
| 持久化层 | 重启后还能看见什么 | Rollout JSONL、state_db、Agent Graph |

## Codex Agent 设计亮点（速览）

| 亮点 | 一句话 |
|------|--------|
| **Core 可复用** | `codex-core` 禁止直接打 stdout；所有 UI 走事件流，CLI/IDE/Exec 共享同一套 loop |
| **Turn 准入即决策** | Start / Steer / Reject 在 hooks/采样之前确定，避免「先跑再说」竞态 |
| **WorldState Diff** | 权限、工具、AGENTS.md、协作模式等按 section 增量注入 |
| **安全纵深** | PermissionProfile → 平台沙箱 → ExecPolicy → Guardian AI 审查 |
| **多 Agent V2** | 独立 collaboration 命名空间 + 可控 fork 深度 + 共享文件系统语义 |
| **扩展面完整** | Skills / Hooks / Plugins / Extension Contributor 覆盖生命周期全点 |
| **生产级持久化** | Rollout + SQLite 索引，Resume/Fork/Revert 语义完整 |

## 快速选型：什么时候用哪套机制

| 场景 | 推荐机制 |
|------|----------|
| 日常交互编码 | TUI（默认 `codex`） |
| CI / 管道 / 脚本 | `codex exec`（无头 + 事件/最终输出） |
| IDE / 桌面 App 集成 | App-Server 协议（daemon） |
| 主脑拆解、并行子任务 | Multi-Agent V2（`spawn_agent` 等） |
| 先规划后动手 | Collaboration Mode = Plan |
| 自定义工作流拦截 | Hooks + Skills |
| 远程/容器内执行 | Exec Server + Environment |

---

*整理日期：2026-09-08*
