# 02 — 交互形态与 Agentic Loop

## Agentic Loop 是什么

传统聊天：你问一句，它答一句。

Claude Code：**你说一个需求，它可能连续执行十几步操作**才给你最终结果。

机制是 **Agentic Loop**（智能体循环）——一个 `while(true)` 无限循环，每次迭代代表一次「思考 → 行动 → 观察」周期。

```text
┌─────────────────────────────────────────┐
│  预处理管道（压缩/优化上下文）            │
│       ↓                                 │
│  流式 API 调用（收集 assistant + tool_use）│
│       ↓                                 │
│  工具执行（并行或串行）                    │
│       ↓                                 │
│  终止判定 或 追加消息 → 下一轮 continue    │
└─────────────────────────────────────────┘
```

---

## 单轮 vs 多轮

| 概念 | 范围 | 管理者 |
|------|------|--------|
| **单轮** | 一次 query() 完整执行 | queryLoop：组装上下文 → API → 工具 → 循环直到结束 |
| **多轮（Session）** | 跨越数十次用户输入，持续数小时 | QueryEngine：mutableMessages、成本、权限、文件缓存 |

### QueryEngine 管理的会话状态

```text
QueryEngine 内部状态
├── mutableMessages          完整对话历史，跨 turn 累积
├── readFileState            已读文件缓存，避免重复读取
├── totalUsage               累计 token 消耗
├── permissionDenials        权限拒绝记录
├── discoveredSkillNames     当前 turn 已发现的 skill（submitMessage 开头清空）
├── loadedNestedMemoryPaths  已加载嵌套 memory 路径
└── abortController          会话级中断控制
```

### QueryEngineConfig 值得注意的字段（相对旧文档补全）

| 字段 | 作用 |
|------|------|
| `taskBudget?: { total }` | API beta task-budgets；跨 compact 追踪剩余 |
| `snipReplay?` | SDK 路径对 snip boundary 的重放/截断（REPL 为保 UI 滚动通常不截） |
| `handleElicitation?` | MCP -32042 URL elicitation |
| `orphanedPermission?` | resume 时孤儿权限恢复 |
| `includePartialMessages?` | 是否向前端吐 partial |
| `jsonSchema?` | Structured output |
| `maxBudgetUsd?` / `maxTurns?` | 硬预算与轮次上限 |

公开方法侧重：`submitMessage`、`interrupt`、`getAbortSignal`、`getMessages`、`setModel` 等。

### submitMessage 流程（SDK/多轮）

每次用户输入触发 submitMessage：

1. 清除 turn 级追踪状态
2. 解析模型（用户可能中途切换）
3. **动态组装 System Prompt**（每 turn 重新构建）
4. 包装权限检查（追踪每次拒绝）
5. 调用 query() 执行 agentic loop
6. 逐步 yield SDKMessage 给调用方

---

## REPL 主查询链路

REPL 模式下，用户输入到模型响应的完整调用链：

```text
用户输入
  → onSubmit (REPL)
  → handlePromptSubmit
  → executeUserInput
  → onQuery / onQueryImpl
  → query (Agentic Loop 核心)
```

### onQueryImpl 职责

REPL 中与 AI 交互的核心控制器，负责：

1. **环境准备**：刷新 MCP 客户端、诊断追踪、关闭 IDE 差异视图
2. **会话标题**：首次用户消息时异步生成标题
3. **权限工具覆盖**：将 Skill 的 additionalAllowedTools 写入 store
4. **System Prompt 构建**：并行获取系统提示、用户上下文、系统上下文
5. **流式查询执行**：调用 query 生成器，onQueryEvent 实时更新 UI
6. **后处理**：BUDDY companion、API 指标、性能报告、onTurnComplete

#### shouldQuery = false 的情况

不调用模型的情况：无效斜杠命令、手动 /compact 等。若包含 compact boundary 消息，会生成新 conversationId 促使 UI 重新挂载。

---

## 循环四阶段详解

### 阶段 1：上下文预处理管道

在调用 API 之前串行执行（`src/query.ts`）。注释明确：**snip 与 microcompact 不互斥，两者都可跑**；释放的 token 计入后续 autocompact 阈值。

```text
messagesForQuery（原始）
  ↓ applyToolResultBudget     工具结果内容替换/预算（contentReplacementState）
  ↓ snipCompactIfNeeded       HISTORY_SNIP：历史 Snip（可与 microcompact 同轮）
  ↓ microcompact              旧工具结果清除；可走 cached microcompact 分支
  ↓ applyCollapsesIfNeeded    CONTEXT_COLLAPSE（部分实现为 stub，见 03）
  ↓ autocompact               先 trySessionMemoryCompaction，再 API compact
messagesForQuery（处理后）→ 发往 API
```

另有 **predictive autocompact**：在部分路径用 `estimateMaxTurnGrowth` 预估本轮增长，提前压缩。

### 阶段 2：流式 API 调用

- AssistantMessage 收集到 assistantMessages[]
- tool_use 块提取到 toolUseBlocks[]，设置 needsFollowUp = true
- **StreamingToolExecutor**（门控：`buildQueryConfig().gates.streamingToolExecution` / Statsig `tengu_streaming_tool_execution2`）在流式过程中即可启动工具
- 可恢复错误（prompt-too-long、max-output-tokens）被暂扣，先尝试恢复

关键守卫：
- `backfillObservableInput`：为 tool_use 回填可观察字段，只在添加新字段时克隆（保护 prompt cache）
- 流式降级：`streamingFallbackOccured` 时消息 tombstone；`StreamingToolExecutor.discard()` abort sibling，防泄漏

### 阶段 3：工具执行（并行 / 串行）

```text
needsFollowUp = true 时：
  streamingToolExecutor ? getRemainingResults() : runTools(...)
  → toolResults 标准化 → 合并进 messages → 下一轮迭代
```

#### Multi tool_call 如何并行

| 路径 | 机制 |
|------|------|
| **StreamingToolExecutor** | 每个 tool 解析后看 `tool.isConcurrencySafe(input)`；仅当「当前工具安全且正在执行的全部安全」才重叠执行；不安全工具会卡住队列直到可独占运行 |
| **runTools / toolOrchestration** | `partitionToolCalls`：连续 safe 的 call 合成一批 **并发**；unsafe 单独成批 **串行** |
| **Sibling abort** | Bash 等错误可 `siblingAbortController.abort('sibling_error')` 取消兄弟工具；流式 fallback 也会 abort sibling |

心智模型：**并发安全由工具声明（对具体 input）决定**，不是「模型一次发了 N 个就全并行」。

### 阶段 4：终止或继续

---

## 终止条件

| 终止原因 | 机制 |
|----------|------|
| blocking_limit | Token 超硬限制 → PTL 错误 → 返回 |
| image_error | 图片尺寸/缩放错误 |
| model_error | callModel 不可恢复异常 |
| aborted_streaming | 用户 ESC 中断（流式阶段）→ 未完成 tool_use 合成 tool_result |
| prompt_too_long | 413 且 reactive compact 无法恢复 |
| stop_hook_prevented | Stop hook 返回 preventContinuation |
| hook_stopped | Hook 停止路径（`transitions.ts`） |
| completed | AI 未发 tool_use，正常结束 |
| aborted_tools | 工具执行阶段中断 |
| max_turns | 轮次超限 |

## 继续条件（恢复路径）

| 路径 | 说明 |
|------|------|
| next_turn | 正常工具循环：执行工具 → 追加消息 → continue |
| max_output_tokens_escalate | 首次截断：maxOutputTokens 提升到 64K，静默重试 |
| max_output_tokens_recovery | 仍截断：注入恢复消息，最多 3 次 |
| collapse_drain_retry | 413：提交暂存折叠后重试 |
| reactive_compact_retry | collapse 无效：即时压缩后重试 |
| stop_hook_blocking | Stop hook 注入阻塞错误，强制重新思考 |
| token_budget_continuation | TOKEN_BUDGET：注入 nudge 加速收尾后再 continue |

---

## State 状态机对象

每次迭代通过 State 传递（约 11 字段，含 `transition`）：

| 字段 | 含义 |
|------|------|
| messages | 当前对话消息 |
| toolUseContext | 工具上下文（含权限） |
| autoCompactTracking | 压缩跟踪 |
| maxOutputTokensRecoveryCount | 输出截断恢复计数 |
| hasAttemptedReactiveCompact | 是否已尝试即时压缩 |
| maxOutputTokensOverride | 输出 token 上限覆盖 |
| pendingToolUseSummary | 异步工具摘要 Promise |
| stopHookActive | Stop hook 是否激活 |
| turnCount | 轮次计数 |
| transition | 上一次 continue 的原因（`Continue` 联合类型） |

`transition` 让后续迭代检测特定恢复路径，避免无限循环。定义见 `src/query/transitions.ts`（`Terminal` / `Continue`）。

---

## 流式响应机制

### 为什么需要流式

30 秒才生成完整回答 → 一次性显示体验差。流式让用户**实时看到思考过程**、预览工具参数、感知长时间任务仍在进行。

### 核心事件类型

```text
message_start
  ├── content_block_start (text / tool_use / thinking)
  │   ├── content_block_delta (text_delta / input_json_delta / thinking_delta)
  │   └── content_block_stop → yield AssistantMessage
  └── message_delta (stop_reason + usage)
message_stop
```

一次 AI 响应可产生**多条** AssistantMessage——文本与工具调用交替产出。stop_reason 在 message_delta 才确定，回写到最后一条消息。

### 错误与降级

| 场景 | 处理 |
|------|------|
| 网络停滞 | 30s 被动 stall 检测 + 90s 主动空闲超时看门狗 |
| API 限流 | 指数退避重试 |
| 输出超限 max_tokens | 错误消息 + max_output_tokens 恢复路径 |
| 上下文超限 | 触发 compaction 后重试 |
| 流式失败 | 降级到非流式 executeNonStreamingRequest |

### Bash 流式反馈

BashTool 通过 onProgress 每秒轮询输出，UI 实时展示命令输出；长时间命令支持自动后台化。

---

## 长后台任务与主会话上下文

API 协议始终是 **`tool_use` ↔ `tool_result` 成对**：不会出现「只有启动 Action、没有 result」仍继续采样。后台化改变的是 **result 语义**（启动回执 / 阶段性结果），不是取消配对。

### 两类常见后台

| 类型 | 运行机制 | 启动时主会话立刻得到 |
|------|----------|----------------------|
| Async Agent / Fork / Coordinator worker | `AppState.tasks` + sidechain 独立跑 | `async_launched` 类 **tool_result**（含 task id） |
| 长 Bash（`run_in_background` / 超时自动后台） | `LocalShellTask` 保活进程 | 带 task id / 输出路径的 **tool_result** |

### 时序（主线程视角）

```text
① tool_use(启动后台) → tool_result(回执：已启动 / task id /「完成后通知」)
   → 主 query 可结束；用户可继续提交新 turn
   → 后台平行执行（中间轨迹默认不灌主 transcript）

② 完成后：enqueuePendingNotification(mode=task-notification, priority=later)
   → 主线程空闲时出队（不与 prompt 模式混批；later 不抢用户输入）
   → 注入主 transcript（形态接近又一条用户侧输入，带 <task-notification> 结构）
   → 再驱动一轮主 Agent 采样
```

完成事件 **不是** 挂在原 launch 上的第二个 `tool_result`，也不是模型先发一个「领取完成」的 `tool_use`；而是系统再塞一条 **类用户 query 的 task-notification**，唤醒主循环。

### 用户继续 turn 时上下文怎么组

| 通道 | 内容 |
|------|------|
| 主会话 | 主 transcript + 新用户输入 + 常规 System Prompt / 记忆 / 压缩投影 |
| 后台 | sidechain 或进程输出；默认不进入当前主采样 |
| 完成后 | 主历史 + task-notification（summary / result 等）→ 再采样 |

UI 的 BackgroundTaskStatus 供人观察；模型侧认的是 transcript 里的启动回执，以及之后的 notification。

### Agent 是否「知道」长任务还在跑

- **知道**：靠启动那次完整的 `tool_use` + **回执 `tool_result`**（不是靠持续灌中间 Action/Ob）。
- **不自动禁止**再开新的长任务；是否并行 / 重复启动取决于提示与模型策略。产品若要防重复，需显式约束（任务列表注入、限制再 spawn 等）。

多 Agent 细节与通信表见 [04-子Agent与多Agent编排](./04-子Agent与多Agent编排.md)。

---

## 模型降级（Fallback）

主模型不可用（FallbackTriggeredError）时：

1. 已收集 assistantMessages 清空，tool_use 收到合成 tool_result
2. 移除思维签名块（跨模型回放会 400）
3. 切换到 fallbackModel
4. 生成系统消息通知用户
5. 重新发起流式请求

---

## 为什么不是「一次规划，批量执行」

- **每步产生真实信息**：toolResults 是 API 无法预知的
- **动态上下文管理**：每轮重新评估压缩需求
- **错误即时恢复**：stop hook 可注入阻塞错误修正策略
- **用户可控**：abortController 多检查点，ESC 优雅中断
- **成本控制**：Token Budget 终止前检查

---

## 成本追踪

三层链路：

1. **记录层**：message_delta 的 usage 字段
2. **累计层**：addToTotalSessionCost 按模型定价累计 totalCostUSD、modelUsage
3. **持久化**：saveCurrentSessionCosts 跨重启保留

QueryEngineConfig.maxBudgetUsd 提供硬性预算；REPL 中超过 $5 软提醒（非硬性阻断）。

## 模型热切换

/model sonnet 切换模型：

- mutableMessages 与模型选择解耦，历史不丢失
- 下次 submitMessage 用新模型 + 重新组装的 System Prompt
- contextWindowTokens、maxOutputTokens 按新模型规格重算

## 文件快照与回滚

fileHistoryMakeSnapshot 在 AI 修改文件前自动保存。快照绑定 message.id，--rewind-files 可精确恢复到对话任意时间点的文件状态——比 git 更细粒度。
