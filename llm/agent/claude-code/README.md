# Claude Code Agent 框架知识库

本目录是对 Claude Code 官方文档的系统性整理，聚焦 **Agent 层面**：交互形态、Agentic Loop、上下文工程、多 Agent 编排、工具与安全边界、扩展机制与会话持久化。

> 文档为独立知识库，不依赖外部代码仓库链接；概念与机制描述基于 Claude Code 源码级白皮书整理。

---

## 文档索引

| 序号 | 文档 | 内容概要 |
|------|------|----------|
| 01 | [概述与架构](./01-概述与架构.md) | 产品定位、五层架构、核心设计原则、与同类工具差异 |
| 02 | [交互形态与 Agentic Loop](./02-交互形态与Agentic-Loop.md) | REPL/SDK/ACP、主循环状态机、流式响应、多轮编排 |
| 03 | [上下文管理](./03-上下文管理.md) | System Prompt、Token 预算、三层压缩、项目记忆 |
| 04 | [子 Agent 与多 Agent 编排](./04-子Agent与多Agent编排.md) | Subagent、Fork、Coordinator、Swarm、通信路径 |
| 05 | [工具系统与能力边界](./05-工具系统与能力边界.md) | Tool 抽象、内置工具、MCP、Task 白板 vs Runtime Task |
| 06 | [安全、权限与 Plan Mode](./06-安全权限与Plan-Mode.md) | Allow/Ask/Deny、权限模式、沙箱、计划模式 |
| 07 | [扩展机制](./07-扩展机制.md) | 自定义 Agent、Skills、Hooks、MCP 配置 |
| 08 | [会话持久化与恢复](./08-会话持久化与恢复.md) | JSONL Transcript、Sidechain、Compact 投影、Resume |
| 09 | [特性与模式索引](./09-特性与模式索引.md) | Coordinator、Fork、Remote、Worktree、Daemon 等 |

---

## 全局心智模型

```text
Agent 是派人干活。
TaskCreate 是往白板上贴任务卡。
Runtime Task 是正在跑的人或远端人影。
Coordinator 是星型编排器。
Swarm 是有成员、有邮箱、有任务白板的团队。
```

## 五层系统分层

| 层 | 回答的问题 | 典型对象 |
|---|---|---|
| 入口层 | 用户或模型通过什么启动动作 | 斜杠命令、Agent 工具、TeamCreate、SendMessage |
| 编排层 | 谁拆解、派发、控制、综合 | Coordinator、Team Lead、Agent 路由 |
| 运行层 | 谁真正执行 | LocalAgentTask、InProcessTeammateTask、RemoteAgentTask |
| 通信层 | 结果如何回流 | tool_result、task-notification、mailbox、CCR 事件 |
| 持久化层 | 重启后还能看见什么 | Session JSONL、sidechain、team config、task files |

## 快速选型：什么时候用哪套机制

| 场景 | 推荐机制 |
|------|----------|
| 需要主脑拆解、派发、综合、纠偏 | Coordinator Mode（用户显式开启） |
| 多个独立任务、长期队友持续领任务 | Agent Teams / Swarm |
| 派一个专家做一次性研究或修改 | 普通 subagent |
| 复制当前上下文做并行探索 | fork agent |
| 工作放到远端环境执行 | remote agent |

---

*整理日期：2026-07-14*
