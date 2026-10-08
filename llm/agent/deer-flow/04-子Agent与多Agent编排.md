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

## 委派策略

直接执行是默认。`task` 在并行延迟、专家技能或上下文隔离的收益明显大于启动成本和副作用时才使用。并行范围需要独立产出，以及互不重叠的可变状态。

Custom Agent 的 `allowed_subagents` 在 Run 开始时写入运行元数据。`None` 表示全部可用，空列表表示拒绝，列表表示允许集。提示词发现和 `task` 执行都按这份快照过滤，工具内部不再重新读取可变的 Agent 配置。

## 批处理结果

`read_batch_item` 只读取当前线程、当前所有者的条目，按提交顺序投影报告、状态和验收字段。它不持久化快照，不调度工作，也不暴露执行规格。完整结果导出才带有界的检索证据；紧凑投影省略这部分。取消、失败和过期的尝试不能发布证据。

## 共享沙箱

每个获准的子任务带稳定的沙箱租约。一个子任务结束不会释放仍有兄弟持有的 Lead 线程沙箱；最后一个持有者才执行待定的 Provider 释放。

## 提前结束与验收

三条独立上限可以提前结束子任务。原因记在附加字段 `stop_reason`，不新增状态枚举：`token_capped`、`turn_capped`、`loop_capped`。有可用最终回答时状态仍是完成；回合上限下没有任何可用结果时记为失败。

Lead 提供的验收条件由代码检查。可判定的叶子是工作区内的文件存在、非空和已写入，以及能对上一次成功命令执行的测试通过。其余条件记为未验证，不当作通过。

## 子任务上下文

子 Agent 与 Lead 共用 `summarization.enabled`。压缩摘要写入 `summary_text`，再投影进下一次模型请求。子任务路径跳过记忆刷写，避免用父线程标识把子任务内部轮次写进父线程的长期记忆。每个内置子任务在首次模型调用前注入只含当前日期的隐藏系统消息，不继承 Lead 的记忆与跨日更新。

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
