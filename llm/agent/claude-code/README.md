# Claude Code Agent 框架知识库

本目录是对 Claude Code Agent 框架的系统性整理，聚焦 **Agent 层面**：交互形态、Agentic Loop、上下文工程、多 Agent 编排、工具与安全边界、扩展机制与会话持久化。

> 独立知识库；机制描述以公开/可查阅的 Claude Code 实现与文档为准。上游项目文档（如 architecture overview）可作交叉参考，若与实现冲突以实现为准。

---

## 文档索引

| 序号 | 文档 | 内容概要 |
|------|------|----------|
| 01 | [概述与架构](./01-概述与架构.md) | 产品定位、五层主链路 + 平行子系统、设计原则 |
| 02 | [交互形态与 Agentic Loop](./02-交互形态与Agentic-Loop.md) | REPL/SDK/ACP、预处理管道、并行工具、长后台与 task-notification |
| 03 | [上下文管理](./03-上下文管理.md) | System Prompt、多层预算管道、CLAUDE.md / memdir 长期记忆 |
| 04 | [子 Agent 与多 Agent 编排](./04-子Agent与多Agent编排.md) | Subagent、Fork、Coordinator、Swarm、通信路径 |
| 05 | [工具系统与能力边界](./05-工具系统与能力边界.md) | Tool 抽象、builtin-tools、Deferred Search、MCP |
| 06 | [安全、权限与 Plan Mode](./06-安全权限与Plan-Mode.md) | 8 来源规则、权限模式、沙箱、Plan |
| 07 | [扩展机制](./07-扩展机制.md) | 自定义 Agent、Skills（/ 与 SkillTool 注入）、Hooks、Workflow、MCP |
| 08 | [会话持久化与恢复](./08-会话持久化与恢复.md) | JSONL、Sidechain、snip/compact 投影、Resume |
| 09 | [特性与模式索引](./09-特性与模式索引.md) | Coordinator、Fork、Daemon、Deferred Tools 等 |

---

## 全局心智模型

```text
Agent 是派人干活。
TaskCreate 是往白板上贴任务卡（work item）。
Runtime Task 是正在跑的人或远端人影（AppState.tasks）。
Coordinator 是星型编排器（与 Fork 互斥）。
Swarm 是有成员、有邮箱、有任务白板的团队（默认开启）。
QueryEngine.submitMessage 是多轮会话入口；query()/queryLoop 是单轮 agentic 核。
```

## 五层主链路 + 平行子系统

| 层 | 回答的问题 | 典型对象 |
|---|---|---|
| 入口层 | 用户或模型通过什么启动 | 斜杠命令、Agent 工具、TeamCreate、SendMessage |
| 编排层 | 谁拆解、派发、控制、综合 | QueryEngine、Coordinator、Team Lead |
| 运行层 | 谁真正执行 | LocalAgentTask、InProcessTeammateTask、RemoteAgentTask |
| 通信层 | 结果如何回流 | tool_result、task-notification、mailbox、CCR / ACP |
| 持久化层 | 重启后还能看见什么 | Session JSONL、sidechain、team config、task files |

**平行子系统**（不在五层主图内，但已进源码）：`src/daemon/`、`src/workflow/`、`src/services/acp/` + `packages/remote-control-server/`、`src/proactive/` / KAIROS 工具族。

## 快速选型

| 场景 | 推荐机制 |
|------|----------|
| 需要主脑拆解、派发、综合、纠偏 | Coordinator Mode（用户显式开启） |
| 多个独立任务、长期队友持续领任务 | Agent Teams / Swarm（默认可用） |
| 派一个专家做一次性研究或修改 | 普通 subagent |
| 复制当前上下文做并行探索 | fork agent（feature 门控；与 Coordinator 互斥） |
| 工作放到远端环境执行 | remote agent / Remote Control |
| 工具 schema 过多 | SearchExtraTools + Execute（deferred） |
| 最小工具面调试 | `CLAUDE_CODE_SIMPLE=1` |

---

## 相对旧版文档的主要修订（2026-09）

| 主题 | 旧述风险 | 现依据源码 |
|------|----------|------------|
| 压缩 | 「三层」过粗 | 预算管道：toolResultBudget → snip → microcompact → collapse → autocompact（SM→API） |
| Context Collapse | 当作稳定生产 | 部分开源还原实现中多为 **stub**；勿默认当作可靠生产能力 |
| Swarm | 易被写成实验默认关 | **默认开**；`…_TEAMS_DISABLED` 才关 |
| QueryEngine | 易写成 `.query()` | 公开入口 **`submitMessage()`** |
| 工具包路径 | 暗示仅 `src/tools` | 实现主在 **`packages/builtin-tools/`** |
| Autocompact buffer | 固定 13K | **`getAutocompactBufferTokens(model)`** 按窗口 13K/30K/50K |
| 权限模式 | 缺 dontAsk/auto | 外部模式含 `dontAsk`；`auto`/`bubble` 偏内部 |

---

*整理修订：2026-09-08（对照 Claude Code 实现约 2.8.x）*
