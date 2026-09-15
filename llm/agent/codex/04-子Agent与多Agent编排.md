# 04 — 子 Agent 与多 Agent 编排

Codex 把多 Agent 当作**一等公民协议**，而不是「再开一个 Bash 跑脚本」。V2 提供独立 collaboration 工具面、可控历史 fork、Agent Roles、以及可持久化的 Agent Graph。

---

## 概念对照

| 概念 | 本质 | 入口 | 结果回路 |
|------|------|------|----------|
| Root agent (`/root`) | 主线程 Agent | 用户 Turn | 直接对用户 |
| Subagent（ThreadSpawn） | 派生的子 Thread | `spawn_agent` | mailbox / FINAL_ANSWER → 父 |
| Agent Role | 角色配置（指令/工具限制） | `agent_type` + config | 影响 spawn 配置 |
| Agent Graph | parent/child 拓扑 | Graph Store | Resume 时恢复 metadata |
| Inter-agent message | 代理间通信 | `send_message` / `followup_task` | analysis channel 格式化消息 |

---

## 两代协议

| | V1 | V2 |
|--|----|----|
| 工具 | `spawn` / `send_input` / `wait` / `resume_agent` / `close_agent` | `spawn_agent` / `followup_task` / `send_message` / `wait_agent` / `interrupt_agent` / `list_agents` |
| 定位 | 早期多代理面 | 当前主推协作模型 |
| 历史 | 相对简单 | `fork_turns` 精细控制 |

以下以 **V2** 为主。

---

## V2 设计要点（亮点）

### 1. 平等智能体 + 明确根身份

Usage hint 写明：`/root` 与子 agent **同等能力、同一工具集**；子 agent 也可再 spawn。主从是协作拓扑，不是「弱化工具的打工仔」。

### 2. 协作工具独立命名空间

```text
必须：to=functions.collaboration.spawn_agent（等）
禁止：从 functions.exec 的 tools.* 间接调用协作工具
```

这从工具面上切断「模型用 shell 伪造多 Agent」的路径，也避免 Code Mode / exec 命名空间泄漏协作原语。

### 3. 共享文件系统语义写进提示

所有 agent 共享同一目录 / CWD / container 文件系统——**一人改文件，全员立即可见**。产品选择是「共享工作区协作」，不是默认 worktree 隔离（隔离可作为环境/工作流另配）。

### 4. `fork_turns` 控制上下文遗传

| 取值 | 含义 |
|------|------|
| `none` / 小整数 | 少带或不带父历史；允许 model / reasoning_effort override |
| `all` 或省略（全历史 fork） | 继承父模型与 reasoning；**不接受** model override |

全历史 fork 保一致性；浅 fork 适合「换模型跑专项」且避免把父会话噪声全带上。

### 5. 消息类型协议

父/子在 analysis channel 看到结构化消息：

```text
Message Type: NEW_TASK | MESSAGE | FINAL_ANSWER
Task name: <recipient>
Sender: <author>
Payload:
<payload text>
```

子 agent 在 final channel 的输出会交付给父 agent——结果回路清晰。

---

## Spawn 流程（概览）

```text
spawn_agent(agent_type, message, fork_mode, ...)
  → build_agent_spawn_config + apply_spawn_agent_role
  → ThreadManager.spawn_agent()（按 fork 策略复制/截断历史）
  → SessionSource::SubAgent(ThreadSpawn { ... })
  → SubagentStart hook + usage hint 注入
  → 子 Session 独立跑 Turn；经 mailbox / FINAL_ANSWER 回流
```

辅助工具：

| 工具 | 作用 |
|------|------|
| `followup_task` | 给已有 agent 新任务并触发 turn |
| `send_message` | 传消息但不触发 turn |
| `wait_agent` | 等待（提示偏好长等待，避免忙轮询） |
| `interrupt_agent` | 中断子 agent |
| `list_agents` | 列举团队成员 |

---

## Agent Roles

- 配置：`config.toml` 的 `[agents.roles]` + `agents/` 目录发现
- `AgentRoleConfig`：nickname、developer_instructions、工具限制等
- `load_agent_roles()` 按 config layer 低→高 merge

角色让「审查者 / 实现者 / 探索者」成为**可配置资产**，而不是每次在 prompt 里口头扮演。

---

## Agent Graph Store

- 持久化 parent/child 边与状态（如 `ThreadSpawnEdgeStatus`）
- V2 resume 时恢复 agent metadata，避免「会话恢复了但团队拓扑丢了」

配合 Rollout / ThreadStore，多 Agent 不只是内存里的并发任务，而是可恢复的协作图。

---

## 何时用多 Agent

| 场景 | 建议 |
|------|------|
| 可并行的调研 / 实现 / 验证 | spawn 多个 role，浅 fork |
| 需要继承当前排查上下文 | `fork_turns=all` |
| 只要主脑拆解、自己少动手 | 强化 root 的 spawn/wait 节奏；配合 Plan |
| 长期多会话团队 | 依赖 Graph + Resume；注意共享 FS 冲突 |

---

## 设计亮点小结

1. **协议化协作**：工具面 + 消息类型 + usage hint 三位一体  
2. **防 exec 偷渡**：协作原语不能藏进 shell  
3. **fork 粒度可选**：上下文遗传与模型覆盖的显式权衡  
4. **Roles + Graph**：配置与拓扑可持久、可恢复  
5. **共享工作区默认诚实**：把「会互相踩文件」写进系统提示，而不是假装隔离

## 关键源文件

| 主题 | 路径 |
|------|------|
| V2 工具 | `codex-rs/core/src/tools/handlers/multi_agents_v2/` |
| Usage hints | `codex-rs/core/src/session/multi_agents.rs` |
| Agent 控制 | `codex-rs/core/src/agent/` |
| Roles | `codex-rs/agent-roles/` |
| Graph | `codex-rs/agent-graph-store/` |
| 测试 | `codex-rs/core/tests/suite/multi_agent_mode.rs` |
