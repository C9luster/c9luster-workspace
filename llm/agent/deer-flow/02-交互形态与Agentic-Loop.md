# 02 — 交互形态与 Agentic Loop

## 交互单元

| 概念 | 含义 |
|------|------|
| Thread | 会话容器；绑定工作目录、sandbox、uploads、checkpoint |
| Run | 一次由用户触发的图执行；可中断、可恢复 |
| Stream | Gateway 经 SSE / StreamBridge 推送模型与工具事件 |
| Clarify | `ask_clarification` 等人机确认点；在得到回复前阻塞后续工具执行 |

交互流程：

```text
创建或选择 Thread
  → 发送消息启动 Run
  → 订阅流式事件
  → （可选）回答澄清问题
  → 继续执行或结束
```

## Agentic Loop（Lead）

循环语义与 LangChain `create_agent` 一致，边界由 harness middleware 定义：

```text
用户消息写入 ThreadState
        │
        ▼
 before_agent / before_model（ThreadData、Sandbox 等）
        │
        ▼
   调用 Chat Model
        │
        ├─ 无 tool_calls → 终态响应（Terminal / Title 等收尾）
        │
        └─ 有 tool_calls
              │
              ▼
       wrap_tool_call / Guardrail
              │
              ▼
       执行工具（含 sandbox / task 子 Agent）
              │
              ▼
       结果写回 messages → 再次进入 before_model …
```

执行顺序与槽位说明见上游 `backend/docs/middleware-execution-flow.md` 与 `backend/packages/harness/deerflow/agents/middlewares/`。

## 流式与可观测

- Gateway 将 LangGraph 事件桥接到 HTTP SSE
- Tracing（Langfuse / LangSmith）挂载在**图调用根**（见 Lead 工厂源码文件头 INVARIANT）
- TokenUsage、Title、Summarization 等 middleware 在循环内外产生副作用（用量记账、标题生成、上下文压缩）

## 中断与继续

| 机制 | 行为 |
|------|------|
| `ask_clarification` | 向用户提问；Run 等待人工输入 |
| Guardrail DENY | 工具不执行；拒绝说明写回模型可见消息 |
| Subagent 异步 | `task` 可后台执行；主循环依据结果或状态消息继续 |
| DurableContext | 新用户轮次可取消更早 Run 中未应答的委托 |

## 通道与策略

- Webhook 类通道（如 `github`）限制管理员型工具（如 `update_agent`），降低外部评论者触发高危写配置的风险
- `resolve_run_interaction_policy` 按 Run 上下文解析交互策略
- Authorization provider 可在装载阶段过滤可见工具集
