# 04 — 子 Agent 与多 Agent 编排

## 编排模型

DeerFlow 采用 **Lead + Subagent** 结构：

| 角色 | 职责 |
|------|------|
| Lead | 完整 middleware、工具、澄清、记忆；对用户负责验收与汇报 |
| Subagent | 由 `task`（及批处理）拉起；middleware 子集更小，专注委派任务执行 |

结果以消息或状态回流 Lead。编排不是固定 DAG 研究图，而是由 Lead 在 Run 内按需委派。

## 核心类型

| 类型 | 路径 | 职责 |
|------|------|------|
| `SubagentExecutor` | `backend/packages/harness/deerflow/subagents/executor.py` | 单任务异步执行、状态机、取消与清理 |
| `SubagentStatus` / `SubagentResult` | 同上 | 生命周期与产物 |
| `SubagentBatchService` | `backend/packages/harness/deerflow/subagents/batch_service.py` | 并发批跑、轮询、取消 |
| `SubagentRuntime` | `backend/packages/harness/deerflow/subagents/runtime.py` | 运行时批量 stop 等 |
| Capacity | `subagents/capacity.py`、`config/subagents_config.py` | 并发与 `max_total_subagents_per_run` |

`execute_async(task, task_id=...)` 返回 `execution_id`。配套接口：`request_cancel_background_task`、`cleanup_background_task`、`force_cleanup_background_task`。

## 限额与防护

- `SubagentLimitMiddleware`：限制单次 Run 拉起的子 Agent 总量
- `effective_subagent_concurrency`：有效并发
- 后台任务清理拒绝非终态条目，避免清理仍在执行的任务

## Lead 协作约定

摘自 `backend/packages/harness/deerflow/agents/middlewares/AGENTS.md`：

- 委托结论不可信：持久化字段须再校验；畸形值忽略
- 已完成工作作为可复用证据，不视为自动验收通过
- DurableContext 在新用户轮次取消更早 Run 中未应答的委托；保留 resume、同 Run 续跑、无 `run_id` 的条目
- 任意回复可阻止取消；缺少 status 元数据的遗留回复可能仍为 `in_progress`；状态不得从回复正文推断

## 适用边界

| 更适合 Subagent | 更适合留在 Lead |
|-----------------|-----------------|
| 可并行的调研或编码切片 | 需逐步向用户澄清的交互 |
| 长耗时沙箱作业 | 依赖完整记忆与技能激活栈的决策 |
| 需要隔离工具集的子任务 | 对用户的最终验收与汇报 |
