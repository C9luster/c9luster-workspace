# 04 — 子 Agent 与多 Agent 编排

Claude Code 里有很多看起来都叫「多 Agent」的概念，它们共享部分底层设施，但**不是同一个抽象**。本章厘清 Subagent、Fork、Coordinator、Swarm、Remote Agent 的区别、路由、通信与恢复。

---

## 概念对照表

| 概念 | 本质 | 入口 | 状态位置 | 结果回路 |
|------|------|------|----------|----------|
| 普通 sync subagent | 一次性前台 Agent 调用 | Agent({ subagent_type }) | foreground LocalAgentTask | 当前 turn 的 tool_result |
| 普通 async subagent | 一次性后台 agent | Agent({ async: true }) | AppState.tasks + sidechain | async_launched + task-notification |
| fork agent | 继承父上下文和 exact tools 的后台分支 | 省略 subagent_type 且 fork gate 满足 | LocalAgentTask + .meta.json | task-notification |
| coordinator worker | Coordinator 派出的 worker | Agent({ subagent_type: "worker" }) | LocalAgentTask | task-notification + SendMessage |
| swarm teammate | 长生命周期团队成员 | Agent({ name, team_name? }) | InProcessTeammateTask 或 pane | mailbox by name，idle 后可继续 |
| remote agent | 远端执行体本地镜像 | Agent(..., isolation: "remote") | RemoteAgentTask + sidecar | CCR events / polling |
| work item task | 共享任务白板条目 | TaskCreate/Update/List/Get | ~/.claude/tasks/*.json | teammate/lead 认领更新 |
| runtime task | 正在运行的后台执行体 | 多种入口 | AppState.tasks | UI、spinner、resume、kill |

---

## 四条「子 Agent」执行路径

常被混称为「子 Agent」，实际有四类：

| 类型 | 谁触发 | 经过 Tool 协议 | 结果怎么回来 |
|------|--------|:--------------:|--------------|
| 命名 subagent | 模型 Agent({ subagent_type }) | 是 | tool_result 或 task-notification |
| AgentTool fork | 模型 Agent({}) 且 fork gate 开启 | 是 | async_launched → task-notification |
| Slash command fork | 用户执行 context: fork 的 skill | 否 | 同步输出或后台回注 |
| runForkedAgent() | 运行时内部 API | 否 | 调用方内部消费 |

记忆：`AgentTool fork` 是给模型用的；`runForkedAgent()` 是运行时内部实现；slash command fork 是 skill 执行模式。

---

## AgentTool 路由决策树

同一个 Agent 工具，根据参数和上下文走不同运行时：

```text
AgentTool.call
  ├─ name + team context?     → spawnTeammate（Swarm）
  ├─ isolation=remote?        → registerRemoteAgentTask
  ├─ fork route?              → register async LocalAgentTask as fork
  ├─ shouldRunAsync?          → register async LocalAgentTask
  └─ 默认                     → foreground LocalAgentTask + tool_result
```

| 路由 | 触发条件 | 返回 |
|------|----------|------|
| teammate | 有 name + team_name 或 teamContext | teammate_spawned |
| remote | isolation: "remote" | remote_launched |
| fork | 省略 subagent_type + fork gate | async_launched |
| async local | 显式 async、Coordinator worker、自动后台条件 | async_launched |
| sync local | 默认 | tool_result |

---

## 命名 Subagent 详解

### 核心参数

| 参数 | 作用 |
|------|------|
| description | 3-5 词短描述，UI/通知用，不参与推理 |
| prompt | 完整任务说明（必须自包含） |
| subagent_type | 指定 agent 类型 |
| model | 模型覆盖（coordinator/fork 下忽略或继承） |
| run_in_background | 请求后台运行 |
| name | 注册 name→agentId，供 SendMessage 定向 |
| isolation | worktree 或 remote |
| cwd | 运行目录（KAIROS schema） |

### Agent Definition 字段

定义在 Markdown frontmatter 或 JSON 配置：

| 字段 | 作用 |
|------|------|
| name / description | 标识与选型说明 |
| tools / disallowedTools | 工具白名单/黑名单 |
| prompt | agent system prompt |
| model / effort | 模型与推理深度 |
| permissionMode | 默认 acceptEdits |
| background | 始终后台运行 |
| isolation | worktree / remote |
| maxTurns | 防止无限循环 |
| memory | user/project/local 持久记忆 |
| skills / hooks / mcpServers | 预加载与生命周期扩展 |

### 同步 vs 异步

**同步**（默认）：当前 tool call 阻塞等待，tool_result 直接回当前 turn。

**异步**触发条件：
- run_in_background: true
- agent definition background: true
- coordinator mode（worker 强制异步）
- fork subagent gate 开启（所有 spawn 强制异步）
- assistant mode 等

后台完成通过 `<task-notification>` 注入下一 turn：

```xml
<task-notification>
  <task-id>agent-a1b</task-id>
  <status>completed|failed|killed</status>
  <summary>Agent "Investigate auth bug" completed</summary>
  <result>...</result>
  <usage>...</usage>
</task-notification>
```

### 启动回执 vs 完成回灌（协议）

主会话始终遵守 `tool_use` ↔ `tool_result` 成对：

| 阶段 | 进主上下文的方式 |
|------|------------------|
| 启动 | 一轮 `tool_use(Agent…)` → `tool_result(async_launched / 回执)`；中间后台轨迹默认不灌主 transcript |
| 进行中 | 用户可继续主会话新 turn；上下文 = 主历史 + 新输入（不含后台全量 Ob） |
| 完成 | **不是**原 call 的第二个 tool_result；`enqueuePendingNotification` 将 task-notification 当作 **类用户 query** 入队，主空闲后注入并再采样 |

详情与 Bash 后台对照见 [02-交互形态与Agentic-Loop](./02-交互形态与Agentic-Loop.md)「长后台任务与主会话上下文」。

### 权限三层

1. **启动权限**：filterDeniedAgents、requiredMcpServers、teammate/fork 限制
2. **工具池权限**：按 agent permissionMode 重新 assembleToolPool
3. **执行时权限**：canUseTool → checkPermissions

fork 例外：useExactTools 继承父工具，bubble 模式把权限请求上浮到父终端。

---

## Fork Agent

- 省略 subagent_type + **FORK_SUBAGENT** feature 开启
- 且 **非** Coordinator Mode（`isCoordinatorMode()` 时 fork 直接 false）
- 且 **非** non-interactive / headless（交互 REPL 才开）
- Fork 使用合成 `FORK_AGENT`；可继承父 `renderedSystemPrompt` 以复用 prompt cache
- `permissionMode: bubble`：权限请求上浮父终端
- KAIROS / proactive 活跃时，部分路径会 **强制 async**（`assistantForceAsync` 等）
- 继承父上下文和 exact tools，最大化 prompt cache 复用
- 适合并行探索，不适合长期稳定专业角色
- coordinator / non-interactive 下禁用 fork gate
- fork worker 内不能再次 fork

---

## Coordinator Mode vs Swarm

**两者并存于产品，但不是嵌套关系。**

### 拓扑对比

```text
Coordinator Mode（星型）          Swarm（团队型）
     用户                              用户
      ↓                                ↓
  Coordinator                      Team Lead
   ↙    ↘                         ↙    ↘
worker A  worker B            teammate1  teammate2
  ↓ task-notification            ↕ mailbox
  Coordinator                    Shared TaskList
```

| 维度 | Coordinator | Swarm |
|------|-------------|-------|
| 拓扑 | 星型，Coordinator 居中 | Team Lead + named teammates + mailbox + task list |
| 主 Claude | **只编排**，不 Read/Edit/Bash | 可执行，也可当 lead |
| 执行者 | built-in worker async subagent | in-process 或 pane-based teammate |
| 通信 | task-notification + SendMessage(agentId) | mailbox by name，P2P/broadcast/协议 |
| 任务协作 | 不以 TeamCreate/TaskList 为核心 | TeamFile + shared task list |
| 启用方式 | **用户显式** /coordinator 或环境变量 | 模型按需 TeamCreate；**`isAgentSwarmsEnabled()` 默认 true**，仅 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS_DISABLED` 关闭 |
| Resume | `matchSessionMode()` 可自动翻转 coordinator env | team config + mailbox + task list 文件 |

**Coordinator 不是 Swarm 的 Team Lead。**

### Coordinator 五段状态机

1. **启用**：feature COORDINATOR_MODE + CLAUDE_CODE_COORDINATOR_MODE=1
2. **恢复**：主 session JSONL mode entry，matchSessionMode 对齐环境
3. **Prompt**：Override > Coordinator > Agent > Custom > Default
4. **工具过滤**：主线程仅 Agent/SendMessage/TaskStop 等；worker 用 ASYNC_AGENT_ALLOWED_TOOLS
5. **Worker lifecycle**：强制 async → registerAsyncAgent → task-notification 回主线程

Coordinator 关键约束：**综合而不是转发**。worker prompt 必须自包含（worker 看不到完整对话）。

反模式：`Based on your findings, fix it.`

### Swarm 团队生命周期

```text
NoTeam → TeamCreate → TeamReady
  → Agent(name) → SpawnResolving → InProcess 或 Pane
  → TeammateRunning → Idle → (mailbox/task claim) → Running
  → shutdown_request → approve/reject → cleanup
TeamDelete → shutdown active → cleanup dirs
```

关键不变量：
- roster 扁平（teammate 内禁止 spawn teammate）
- mailbox 按 **name** 寻址（不是 agentId）
- TaskCreate 只写 pending JSON，不启动执行体
- shutdown 是 graceful 协议，不是强杀
- TeamFile 是跨进程事实源

### 存储拓扑（Swarm）

```text
~/.claude/
  teams/<team-name>/
    config.json
    inboxes/<agent-name>.json
  tasks/<team-name>/
    1.json, 2.json, ...
```

---

## 通信路径对照

| 路径 | 发送者 | 接收者 | 用途 |
|------|--------|--------|------|
| tool_result | sync subagent | 当前 assistant turn | 一次性前台结果 |
| task-notification | async local / coordinator worker | 主线程下一 turn | 后台完成/失败/被杀 |
| SendMessage(agentId) | Coordinator/用户 | local agent task | 续跑 worker |
| SendMessage(teammateName) | lead/teammate | teammate mailbox | Swarm 通信 |
| SendMessage("*") | lead/teammate | 全员 broadcast | Swarm 广播 |
| structured protocol | 多方 | 特定 mailbox | permission/plan/shutdown 等 |
| CCR events | remote runtime | RemoteAgentTask | remote 状态 |

plain text SendMessage 必须带 summary。structured message 不能 broadcast。

### Mailbox 协议要点

- 单条 text 64KB，文件 4MB，retained 2MB
- 协议消息（permission、plan、shutdown 等）应保持 unread，由 poller/runner 路由
- mailbox attachment 只消费非结构化消息

---

## Task 不是 Runtime Task

| 名称 | 存储 | 状态 | 消费者 |
|------|------|------|--------|
| work item task | ~/.claude/tasks/\<id\>.json | pending/in_progress/completed | Task tools、teammate 认领 |
| runtime task | AppState.tasks | running/completed/failed/killed | UI、kill/resume |

TaskCreate 创建 JSON；运行体是 LocalAgentTask / InProcessTeammateTask 等。

---

## 持久化与恢复矩阵

| 机制 | resume 后能看到 | resume 后能继续跑 |
|------|-----------------|-------------------|
| coordinator mode | 会话模式 | 是（matchSessionMode） |
| coordinator worker | agent 历史 | 通常可 resumeAgentBackground |
| ordinary/fork subagent | sidechain 历史 | 可恢复 |
| remote agent | remote 镜像 | 取决于 CCR session |
| team config | roster | 不代表 teammate 还活 |
| mailbox | 未读消息 | 可继续投递 |
| shared tasks | task list | 可认领（owner 可能 inactive） |
| in-process teammate | runner 内态 | **不能**跨进程完整恢复 |

调试顺序：文件还在吗 → AppState 投影还在吗 → runtime task 还 running 吗 → 通信通道可用吗 → sidechain/inbox 足够恢复吗？

---

## 选型指南

| 需求 | 推荐 |
|------|------|
| 专业角色、有限上下文、明确工具集 | 命名 subagent |
| 长任务不阻塞主模型 | 异步 subagent |
| 多 worker 共享完整父上下文 + prompt cache | AgentTool fork |
| slash command / skill 隔离执行 | slash command fork |
| 隔离文件改动 | isolation: worktree |
| 主脑拆解派发综合 | Coordinator（用户开启） |
| 长期团队 + 任务板 + mailbox | Swarm |

### 常见误区

- Coordinator = Swarm Team Lead → **不是**
- TaskCreate 创建了运行中的 agent → **只创建 JSON**
- teammate 完成后结果自动给 lead → **需 SendMessage 或 idle notification**
- mailbox 按 agentId 寻址 → **Swarm 按 name**
- in-process teammate 可跨进程 resume → **不行**
