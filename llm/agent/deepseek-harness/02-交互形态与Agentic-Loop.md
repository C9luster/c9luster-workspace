# 02 — 交互形态与 Agentic Loop

## 单位

| 概念 | 含义 |
|------|------|
| 步骤 | 一次模型请求，加上该请求产生的工具调用 |
| 轮次 | 零个或多个步骤。领取第一条输入之前打开，不再欠工作时关闭 |
| 会话 | 仅追加事件日志。模型可见历史从日志派生 |
| Inbox | 待处理输入。没有活跃 Agent 时，持久投影仍可读取 |

输入经同一 inbox 到达。注入的上下文等待一条唤醒消息。声明式 Agent 在 `dsh-agent-loop` 配置中列出；宿主也可以 `ctx.agents.create()` 或 `ctx.agents.resume()`。

## 轮次流程

```text
turn/start
  领取下一步输入和一条排队消息
  组装提示词段与工具 schema
  agent/pre-step          拒绝，或进入（可改写消息）
    首次进入被拒绝或改写为空 → 关闭不含步骤的轮次
    step/start
    agent/request         准备调用；取消在此之前不提交系统提示与用户消息
    追加被接纳的用户消息；按需记录 request/header 与 request/context
    从日志派生并冻结模型历史
    流式响应
    tool/call → tools/pre-execute → tools/execute → tools/post-execute → tool/result
    step/end
    工具要求另一次请求，或已有下一步输入 → 再领取
  agent/turn-stopping
turn/end
```

`turn/*`、`step/*`、`system/message`、`user/message`、`assistant/message`、`assistant/attempt` 和 `tool/*` 写入会话日志。`agent/pre-step`、`agent/request`、`llm/stream` 和 `tools/*` 是 waterfall：监听器必须调用 `next()` 才能继续委托。`agent/turn-stopping` 是串行事件，没有 `next()`。

重试不重复组装，也不重复 `agent/pre-step`。系统提示词只经 `system/message` 历史生效。空渲染清除仍生效的系统节点；具备前缀缓存能力的路由可在缓存前缀之后追加非空更新；新请求序列把非空提示词归并到首个系统节点。

并行安全的工具调用最多同时在途 `maxParallelToolCalls` 个（默认 10）。独占调用单独运行，并形成顺序屏障。`agent.cancel()` 中止当前活动；未设置 `keepInbox` 时清除待处理工作。已经流式交付给用户的文本在取消时保留。

## 事件域

| 域 | 用途 |
|----|------|
| 会话事件 | 追加到日志并经 `session/event` 广播。事实必须在重新加载后仍存在时使用 |
| `agent/*` | 观察或拦截进行中的工作：inbox、步骤、请求、续跑 |
| 能力事件 | 不导入循环即可向 `fs/*`、`tools/*`、`telemetry/*` 等 seam 附加策略 |

AgentLoop 在启动已排队工作前等待串行 `agent/created`。初始化失败会回滚创建。

## 恢复入口

| 字段 | 行为 |
|------|------|
| `sessionId` | 首次使用创建该身份；再次挂载时恢复已实体化的历史 |
| `resumeSessionId` | 加载指定的持久会话。与 `sessionId` 互斥 |
