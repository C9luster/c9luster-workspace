# 02 — 交互形态与 Agentic Loop

## Agentic Loop 是什么

传统聊天：你问一句，它答一句。

Codex：**你提交一个 Turn 输入，它可能连续采样并执行多轮工具**，直到模型不再需要 follow-up，或被中断 / 被 Stop Hook 终止。

机制落在 `Session` 上的 **Turn 循环**（`run_turn`）——每次循环是一次「组装上下文 → 采样 → 执行工具 → 判定是否继续」。

```text
┌──────────────────────────────────────────┐
│  Turn 准入：Start | Steer | Reject        │
│       ↓                                  │
│  回合前：Hooks / 预压缩 / WorldState diff │
│       ↓                                  │
│  loop:                                   │
│    drain pending input（steer/mailbox）  │
│    构建/刷新 StepContext                 │
│    流式采样 + ToolCallRuntime            │
│    需要则 mid-turn compact               │
│    Stop hooks → 结束或注入 continuation  │
└──────────────────────────────────────────┘
```

---

## Thread / Session / Turn / Step

| 概念 | 范围 | 管理者 |
|------|------|--------|
| **Thread** | 可持久化的对话世界线（可 resume/fork） | `ThreadManager` + ThreadStore |
| **Session** | Thread 的运行时状态 | `Session`（≤1 个 active turn） |
| **Turn** | 一次目标驱动的采样+工具循环 | `TurnContext` + `RegularTask` |
| **Step** | Turn 内一次 model sampling | `StepContext`（ToolRouter、MCP binding 快照） |

### Session 关键约束

- 同一时刻最多一个 running task（Regular / Compact / Review / UserShell）
- 用户输入可 **interrupt** 或 **steer**（向活跃 turn 追加 pending input）
- 持有 `InputQueue`（steer + 多 Agent mailbox）、`ContextManager`、`McpRefresh`、`active_turn`

### TurnContext vs StepContext（设计亮点）

| | TurnContext | StepContext |
|--|-------------|-------------|
| 生命周期 | 整个 Turn | 单次 sampling |
| 典型内容 | 模型、权限、环境、协作模式 | ToolRouter、MCP 绑定、resolved settings |
| 价值 | mid-turn 改设置、steer、compact 后仍保持回合语义 | 保证「这一次采样」看到的工具面一致 |

这比「一整坨可变全局状态」更利于：工具列表随 MCP 刷新变化、压缩后 reinject、以及测试可复现。

---

## Turn 输入准入（Admission）

`turn_input.rs` 是 Core 决定输入命运的**唯一入口**：

| 决策 | 含义 |
|------|------|
| **Started** | 新开 Turn → `new_turn_with_sub_id()` + 派发 `RegularTask` |
| **Steered** | 活跃 Turn 追加输入 → 写入 `pending_input`，下轮 sampling 前 drain |
| **Rejected** | 例如 Plan 模式下禁止某些 Automatic 任务 |

启动类型 `TurnStartKind`：

| Kind | 说明 |
|------|------|
| User | 用户显式提交 |
| Automatic | 自动续跑 / 系统触发 |
| Recovery | 恢复路径 |

**亮点**：模块注释写明——准入决策后立刻回复调用方；**不**等待 user-prompt hooks、完整 in-memory context 更新、rollout 落盘或采样。Rejected 的 settings 不会提交。这消除了典型 Agent「UI 已显示开始、内核其实拒绝」的竞态。

Plan 约束示例：`Automatic` 既不能在 Plan 模式启动，也不能通过 settings 切进/切出 Plan。

---

## `run_turn()` 四阶段

### 阶段 0：回合前准备

1. `drain_async_hook_results`（消化上轮异步 Hook）
2. `run_pre_sampling_compact`（将超窗则先压缩）
3. 解析 MCP 启动需求（mentions → required servers/plugins）
4. 捕获首个 `StepContext`（含 ToolRouter）
5. 记录 WorldState diff / reference context
6. 构建 Skills / Plugin 注入
7. SessionStart / TurnStart Hooks
8. Shell snapshot 预热（投机优化）

### 阶段 1：主循环

```text
loop {
  drain pending input（steer / mailbox）→ hooks → 记入历史
  maybe_record_reminder（rollout budget / 时间）
  刷新 StepContext
  run_sampling_request（模型流 + 工具）
  若需 rollover → mid-turn auto compact → continue
  若无需 follow-up → Stop hooks → 结束或注入 continuation
}
```

### 阶段 2：采样请求内部

- 构建 `Prompt`（history + base instructions + world state）
- 启动 `ToolCallRuntime`（并行工具协调）与可选 Code Mode worker
- 流式 `ResponseEvent`：assistant / function call / reasoning / plan delta
- 工具经 `handle_tool_call` → `ToolOrchestrator`
- 支持 stream retry、已执行 tool call 元数据绑定

详见下文「Multi tool_call 并行 / 串行」「事件双通道」「长任务后台」。

### 阶段 3：终止或继续

| 路径 | 说明 |
|------|------|
| completed | 无 follow-up，正常结束 |
| next_step | 工具结果回写，继续采样 |
| mid_turn_compact | token 压力，压缩后继续 |
| stop_hook_block | Stop hook 注入 continuation，强制再想一轮 |
| aborted | CancellationToken / 用户中断 |
| steered | pending input 在边界被吸收，进入新 step |

---

## Multi tool_call：并行与串行

模型一次采样可产出多个 `FunctionCall` / `CustomToolCall`。Codex **不是**「全部串行」或「无脑全并行」，而是：

### 1. 流式即调度（边收边跑）

在 `try_run_sampling_request` 里：

```text
ResponseEvent::OutputItemDone(tool_call)
  → handle_output_item_done → 得到 tool_future
  → in_flight.push_back(tool_future)   # FuturesOrdered
  → 继续读流（不必等该工具跑完）
…
ResponseEvent::Completed
  → drain_in_flight(in_flight)         # 按入队顺序收结果并入库
```

要点：

- 工具在 **流式过程中即可启动**（不必等整次 assistant 响应结束）
- `FuturesOrdered` 保证 **结果按入队顺序** 写回历史（对齐 call 顺序），即使实际完成先后不同
- 采样结束后 `drain_in_flight`：每个结果走 `record_annotated_conversation_items`

### 2. 并行闸门：`RwLock` + `supports_parallel_tool_calls`

`ToolCallRuntime`（`tools/parallel.rs`）对每个 call：

```text
supports_parallel?
  true  → 拿 parallel_execution.read()   # 多个读锁可共存 → 并行
  false → 拿 parallel_execution.write()  # 独占 → 与其它工具互斥（串行）
```

| 约定 | 行为 |
|------|------|
| 默认（Trait 默认 `false`） | 串行：拿 write 锁，与任何其它工具互斥 |
| 显式 `supports_parallel_tool_calls() == true` | 可与其它「也可并行」的工具同时跑 |
| 一个不可并行工具在跑 | 持有 write，其它 call（含可并行者）都要等 |

典型可并行：`exec_command` / `write_stdin`（Unified Exec）、部分 MCP（handler 声明）、`view_image`、若干 resource 只读工具等。  
不可并行（默认）：`apply_patch`、协作类、多数状态变更工具等。

另有细节：

- Hidden 暴露面的工具不算可并行（`ToolExposure::Hidden`）
- MCP 并行能力可按 server / tool 元数据配置，不可跨不安全边界「同名冒充」
- 取消时：若尚未到达 terminal outcome，abort task 并合成 aborted tool response

### 3. 心智模型

```text
并行 = 「调度可重叠」
串行 = 「执行闸门互斥」
入库顺序 = 「FuturesOrdered 入队序」，不是完成时刻序
```

---

## 事件：UI 推送 vs 历史入库（双通道）

Loop 里「事件」有两条去向，不要混为一谈：

| 通道 | API（概念） | 用途 | 是否进 model history |
|------|-------------|------|----------------------|
| **实时 UI / 协议事件** | `send_event` / `send_event_raw` | TUI、App-Server、delta 流 | 否（观测面） |
| **对话历史 + Rollout** | `record_conversation_items` / `record_annotated_*` | 下一轮 Prompt、Resume | 是 |

### 入库路径（ResponseItem）

```text
record_conversation_items / record_annotated_conversation_items
  → prepare（图片等）
  → ContextManager.history.record_annotated_items   # 内存 model window
  → persist_rollout_items → live_thread.append_items # 磁盘 Rollout JSONL
  → send_raw_response_items                          # 再通知客户端「原始条目」
```

常见入库时机：

- 非工具 assistant / reasoning 等 completed item
- 工具结果：`drain_in_flight` 后按序 `record_annotated_conversation_items`
- WorldState diff、user input、hook 注入、compaction checkpoint 等（各自 `PersistContext`）

### 不入库或另类持久化

| 类型 | 行为 |
|------|------|
| `AgentMessageContentDelta` / reasoning delta / tool arg diff | 只 `send_event`，最终以 completed item 入库 |
| `ExecCommandOutputDelta` | 流式 UI；tool result 里再带截断后的快照正文 |
| `TurnDiff` / TokenCount / Warning | 事件面；token 等另有 `TokenUsageRecord` rollout 项 |
| WorldState patch | `RolloutItem::WorldState`，与 model-visible diff items 配合 |

**亮点**：流式 delta 不污染 transcript；入库以 completed / tool output 为准，Resume 看到的是稳定条目而非 delta 重放。

更完整的 Rollout / Fork / Resume 见 [08-会话持久化与恢复](./08-会话持久化与恢复.md)。

---

## 长任务：不是另开「后台 Agent Turn」，而是会话化 Exec

Codex 对「跑很久的命令」的主策略在 **Unified Exec**，而不是把整个 Turn 丢进后台线程后结束（Session 仍是 ≤1 active turn；子 Agent 是另一套 Thread）。

API 协议始终是 **`tool_call` ↔ tool output 成对**。长命令不取消配对，而是让 **首次 result 变为阶段性快照 + `process_id`**，进程在 `UnifiedExecProcessManager` 中保活。

### `yield_time`：先收一截，进程可继续活着

`exec_command`：

1. 启动进程（可进沙箱）
2. `start_streaming_output`：后台 task 读 PTY，发 `ExecCommandOutputDelta`（观测通道；不替代入库 tool output）
3. `collect_output_until_deadline(yield_time_ms)`：在窗口内收集快照作为 **本轮 tool result**
4. 若进程仍存活 → 返回 `process_id`，进程留在池中
5. 后续模型用 `write_stdin`（可空 poll）再带 `yield_time_ms` 继续取输出 / 写 stdin

```text
短命令：yield 内退出 → tool result 含完整输出 + exit code，不保留 session
长命令：yield 到期仍 Alive → tool result 含阶段性输出 + process_id
         → 模型可继续采样 / 再 poll / 干不重叠的事
```

`write_stdin`：空 chars ≈ 后台轮询；非空写入可能触发额外 stdin 审批。空 poll 的 yield 有独立上下界（避免极短忙等或过长阻塞）。

### 时序与上下文组装

```text
① tool_call(exec) → tool result(片段 + process_id / Alive)     ← 一轮成对调用
② （可选，可多轮）tool_call(write_stdin/poll) → tool result(更多输出或结束)
③ 用户中途插话：Steer → pending_input，下轮 sampling 前 drain 后记入历史再采
```

| 阶段 | 主模型上下文 |
|------|----------------|
| 启动 / 每次 yield | 历史 + 该次成对的 tool call/result（含 process_id 与阶段性输出） |
| 进程仍在跑 | 不靠「中间每一行日志」自动成对入库；靠下次 poll 再拿 Ob |
| 用户插话 | 原 Turn 历史 + steered 输入（Session 仍单 active turn） |
| 子 Agent 后台 | `spawn_agent` 另开 Thread；经 mailbox / FINAL_ANSWER 回流（与 exec 保活不同抽象） |

### 与 Agentic Loop 的关系

| 层级 | 长任务语义 |
|------|------------|
| Turn / Session | 仍可在 tool 返回后继续采样；Session 不因长命令独占「永远不结束」 |
| ProcessManager | 跨 tool call、跨 step 保留 PTY/进程 |
| UI | delta 事件实时刷新；`list_processes` / BackgroundTerminalInfo 可观测 |
| 多 Agent | `spawn_agent` 才是「另一条世界线」后台；exec 后台是**同 Thread 内进程保活** |

提示词侧也会引导：子 agent 在跑时，root 应立刻做不重叠工作（见 multi-agent usage hint）——这是编排层「后台」，与 Unified Exec 进程保活互补。

### Agent 是否「知道」长任务还在跑

- **知道**：靠已入库的阶段性 tool result（`process_id` / Alive），不是靠未配对的裸 Action。
- **不自动禁止**再开新的长 exec 或 `spawn_agent`；并行与防重复依赖提示与策略，而非「中间 Ob 未进上下文」本身。

---

## SessionTask 抽象

```text
SessionTask
├── RegularTask     # 标准对话 → run_turn
├── CompactTask     # 手动 / 远程压缩
├── ReviewTask      # 代码审查工作流
└── UserShellCommandTask  # 用户 shell 模式
```

任务在后台 Tokio task 运行，经 `active_turn` 跟踪；`abort` 支持优雅中断。

---

## 交互形态详解

### TUI（默认）

- Ratatui 渲染；斜杠命令（`/model`、`/compact`、`/resume`、`/plan`…）
- 经 App-Server 客户端驱动 thread/turn
- 适合长时间交互、审批弹窗、多 Agent 状态展示

### Exec（无头）

- `codex exec`：内嵌 InProcess App-Server Client
- stdout 可只出最终消息或 JSONL 事件流
- 适合 CI：非交互、可脚本化、与审批策略组合（常配 `Never` 或预信任策略）

### App-Server / Daemon

- JSON-RPC：`thread/start`、`thread/resume`、`turn/start` 等
- Daemon 管理跨调用共享生命周期（PID、socket、lock）
- IDE / 桌面 App 的主集成面

---

## 流式响应与可观测性

- 流式事件映射到协议事件（文本 delta、reasoning、tool call、plan item 等）——**观测通道**
- completed ResponseItem / tool output 走 `record_*` → history + Rollout——**入库通道**
- TTFT 等 turn timing 指标可记录
- 工具输出对模型侧有统一格式化（exit code、duration、截断策略）
- 多 tool_call：流式入队 + `supports_parallel` 闸门 + `FuturesOrdered` 有序入库

长时间 `exec`：见上文「长任务」——`yield_time` + 进程保活 + `write_stdin` 续读，而不是「命令结束才整块塞回」。

---

## 为什么不是「一次规划，批量执行」

- 每步工具结果是模型无法预知的真实环境反馈
- mid-turn compact / steer / mailbox 消息需要循环边界消化
- Stop hook 可阻断「假装完成」并注入纠正提示
- 审批与沙箱升级发生在工具路径上，必须逐步执行
- CancellationToken 在采样与工具阶段均可中断

---

## 设计亮点小结

1. **Admission 与执行解耦**：先决生死，再跑副作用  
2. **Steer**：活跃 Turn 可加料，不必强制 abort+restart  
3. **Turn/Step 分层**：回合配置与采样快照分离  
4. **同一 loop 服务多前端**：TUI / Exec / IDE 行为语义对齐  
5. **任务类型可插拔**：Regular / Compact / Review / UserShell 共用 Session 调度  
6. **Multi tool 有序并行**：流式调度 + RwLock 闸门 + FuturesOrdered 入库序  
7. **事件双通道**：delta 只推 UI；completed/tool output 才进 history/Rollout  
8. **长任务进程保活**：`yield_time` 切片返回，不靠「假后台 Turn」

## 关键源文件

| 主题 | 路径 |
|------|------|
| Turn 主循环 | `codex-rs/core/src/session/turn.rs` |
| Turn 准入 | `codex-rs/core/src/session/turn_input.rs` |
| Turn / Step 上下文 | `session/turn_context.rs`, `session/step_context.rs` |
| 并行闸门 | `codex-rs/core/src/tools/parallel.rs` |
| 历史入库 | `codex-rs/core/src/session/mod.rs`（`record_conversation_items`） |
| 注解入库 | `codex-rs/core/src/session/inject.rs` |
| Unified Exec / yield | `codex-rs/core/src/unified_exec/process_manager.rs` |
| 输出流式 watcher | `codex-rs/core/src/unified_exec/async_watcher.rs` |
| 任务调度 | `codex-rs/core/src/tasks/` |
| 线程管理 | `codex-rs/core/src/thread_manager.rs` |
| Exec 入口 | `codex-rs/exec/src/lib.rs` |
| App-Server | `codex-rs/app-server/src/lib.rs` |
