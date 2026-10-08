# 06 — 安全、权限与 Plan Mode

## 安全层次

DeerFlow 将安全能力拆为多层，彼此不互相替代：

| 层次 | 机制 | 解决的问题 |
|------|------|------------|
| 执行隔离 | Sandbox Provider（本机目录映射 / Docker / 云端） | 进程与文件系统边界 |
| 语义授权 | GuardrailMiddleware + GuardrailProvider | 工具调用前按策略 ALLOW / DENY |
| 人机确认 | `ask_clarification` + ClarificationMiddleware | 需要用户决策的步骤 |
| 工具可见性 | authz provider、通道策略 | 装载阶段隐藏高危或管理员工具 |
| 技能内容 | security scanner | 技能包内容风险扫描 |

文档依据：`backend/docs/GUARDRAILS.md`。

## Sandbox

沙箱是线程级执行环境，不是给每条命令套一次内核策略。`SandboxMiddleware` 在 `before_agent` 获取、`after_agent` 释放，并与线程目录、上传文件绑在同一 Thread 上。子任务持有租约，最后一个持有者才释放。

配置项 `sandbox.use` 是 Provider 类路径。启动时解析该类，它必须实现 `SandboxProvider`：`acquire` 返回沙箱 ID，`get` 返回可执行命令、读写文件的 `Sandbox`，结束时 `release`。靠上传同步技能目录的实现覆盖 `sync_agent_skills`；目录已经绑进环境的实现不用做这一步。

| 实现 | 隔离方式 |
|------|----------|
| `LocalSandboxProvider` | 把 `/mnt/user-data/...` 映射到该线程的宿主目录。宿主 bash 打开时，这不是安全边界 |
| AIO | Docker。远程供给走 Provisioner |
| E2B、OpenSandbox、BoxLite、Tenki | 云端或远端虚拟机。技能目录由 Provider 上传或挂载 |

自建云端沙箱写成同一个子类，把类路径配到 `sandbox.use`。工具进入沙箱前还要过 `sandbox:execute` 授权。沙箱里面仍可跑命令和访问网络；命令语义上的禁止由 Guardrail 另做。

## Guardrails

Guardrail 在 **每个 tool call 执行前** 评估：

```text
模型发出 tool_calls
  → GuardrailMiddleware（wrap_tool_call）
  → GuardrailProvider.evaluate / aevaluate
  → ALLOW：继续执行
  → DENY：不执行；向 Agent 返回拒绝说明
```

- Provider 可插拔，在 YAML 中配置
- 相对「每次动作都 clarify」：适合自治多步任务的确定性策略
- 相对「仅靠 sandbox」：可表达「禁止某些参数/命令语义」等策略

在默认 Lead middleware 链中，Guardrail 位于 DanglingToolCall 之后、ToolErrorHandling 之前（见 `backend/docs/middleware-execution-flow.md`）。

## Clarification 与 Plan Mode

| 机制 | 说明 |
|------|------|
| `ask_clarification` | 工具面人机提问；ClarificationMiddleware 置于 wrap_tool_call 链靠后位置 |
| TodoMiddleware | 由 `plan_mode` 相关参数启用；在 before_model / after_model / wrap_model_call 维护待办与提醒 |
| 交互策略 | `resolve_run_interaction_policy` 按 Run 上下文限制可交互行为 |

Plan Mode 在 DeerFlow 中主要体现为 **Todo / 计划提醒中间件 + 澄清工具**，而非独立权限模式枚举。

## 授权与通道限制

- `deerflow/authz/`：Principal、AuthzRequest / AuthzDecision、`apply_tool_authorization`
- Webhook 通道（如 `github`）禁止管理员型工具（如 `update_agent`），避免外部评论者改写 Agent 配置
- 授权在工具装载阶段生效，缩小模型可选工具面

## 循环与限额防护

| Middleware | 作用 |
|------------|------|
| LoopDetectionMiddleware | 检测循环并注入 / 清理 warning |
| SubagentLimitMiddleware | 截断超额 `task` 调用 |
| ToolErrorHandlingMiddleware | 将工具异常转为可消费的 ToolMessage |
| Safety / ModelLength finish_reason | 将安全或长度结束转为可恢复路径 |
