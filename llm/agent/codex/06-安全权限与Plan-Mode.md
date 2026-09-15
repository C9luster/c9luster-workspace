# 06 — 安全、权限与 Plan Mode

Codex 默认拥有对项目目录动手的能力；安全不是插件，而是 **工具执行路径上的多层闸门**。理解 Agent 设计，很大程度是理解「模型想做」与「系统允许做」如何对齐。

---

## 安全纵深（四层）

```text
PermissionProfile / 审批策略
        ↓
平台沙箱（Seatbelt / bwrap / Windows token）
        ↓
ExecPolicy 规则（Starlark-like .rules）
        ↓
Guardian / AutoReview（可选 AI 审查员）
```

任一层可 fail-closed；冲突时偏向拒绝而非「方便一下」。

---

## 审批策略 AskForApproval

| 值 | 含义 |
|----|------|
| `UnlessTrusted`（untrusted） | 不可信项目：除非 exec policy 显式允许，否则要批 |
| `OnRequest`（默认） | 模型/策略认为需要时再问用户 |
| `Granular{...}` | 细粒度：sandbox_approval / rules / skill_approval 等开关 |
| `Never` | 不再问人；失败直接回模型（适合 CI，风险自负） |

### 审查者 ApprovalsReviewer

| 值 | 含义 |
|----|------|
| `User`（默认） | 人批 |
| `AutoReview`（原 `guardian_subagent`） | 独立审查子代理：采集上下文 + 风险框架后批准/拒绝 |

**亮点**：把「谁来批」从「批什么」拆开——同一审批事件可路由给人或 Guardian，而不改工具 handler。

---

## 平台沙箱

| 平台 | 机制（摘要） |
|------|----------------|
| macOS | `/usr/bin/sandbox-exec`（Seatbelt）；workspace-write 下保护 `.git` / `.codex` 等 |
| Linux | 旧路径 Landlock；split filesystem 走 **bubblewrap**（可捆绑 bwrap）；WSL1 不支持 bwrap 所需 user namespace |
| Windows | Restricted Token / Elevated 后端；split policy 能强制则强制，否则 fail-closed |

`SandboxPolicy` / split filesystem policy：可读/可写 roots、网络等。Core README 强调：**语义不能弱化执行**——无法在所选后端真实强制的策略直接失败，而不是静默降级。

### Orchestrator 中的升级重试

```text
第一次：按当前策略选沙箱执行
  → sandbox denial
  → 升级沙箱策略再试（审批结果缓存，避免重复弹窗）
```

网络访问另有 managed network / deferred approval 路径。

---

## ExecPolicy

- `.rules` 文件（默认规则 + 用户/项目自定义）
- **PrefixRule**：命令前缀 allow / deny / prompt
- **NetworkRule**：网络相关
- 与 `AskForApproval` 联动；危险命令检测（shell-command 分析）

相对「只靠模型自觉」：ExecPolicy 是**确定性**的命令策略层，适合企业基线与「已知危险前缀」。

---

## Guardian 审查

- 独立同步 reviewer session（超时有界，如约 90s 量级设计）
- 覆盖 exec、network、MCP 等高风险审批
- `GuardianRootSnapshot`：有界的 root 对话 + authorization version
- 与 compaction 的 history_version 概念配合，避免「压缩后用过期授权」
- 另有 Guardian V2 / 异步 scorer 扩展路径（`ext/guardian-v2` 等）

**亮点**：安全决策也可 Agent 化，但放在**旁路审查会话**，不与主任务 prompt 糊成一团。

---

## Plan Mode（Collaboration Mode）

`ModeKind`：

| 模式 | 含义 |
|------|------|
| `Plan` | 规划协作：强调计划、限制自动执行类启动 |
| `Default` | 默认执行协作（历史别名含 code / execute 等） |

约束与 Turn 准入联动：

- `Automatic` 启动不能在 Plan 下进行
- Automatic 也不可通过 settings 切入/切出 Plan

`update_plan` 工具用于步骤跟踪；Plan 下对 `request_user_input` 等能力有模式级允许函数。

Plan 模式强调 **协作模式 + 准入策略**（什么种类的 turn 能开），与沙箱权限叠加。

---

## 权限升级与用户输入

| 机制 | 作用 |
|------|------|
| `request_permissions` | 模型显式申请更大权限 |
| `request_user_input` | 同步/异步向用户提问 |
| Skill script approval | Granular 中可单独开关 |
| 网络审批 | 与沙箱网络策略联动 |

---

## 设计亮点小结

1. **纵深而非单点开关**：人、规则、内核沙箱、AI 审查叠代  
2. **Orchestrator 统一闸门**：所有危险工具共享审批/沙箱/重试语义  
3. **不静默降级**：强制不了就失败，避免「以为进了沙箱其实没有」  
4. **Guardian 旁路化**：审查上下文与主任务隔离  
5. **Plan 与 Turn 准入绑定**：模式不只是提示词标签  

## 关键源文件

| 主题 | 路径 |
|------|------|
| Orchestrator | `codex-rs/core/src/tools/orchestrator.rs` |
| AskForApproval | `codex-rs/protocol/src/protocol.rs` |
| ApprovalsReviewer / ModeKind | `codex-rs/protocol/src/config_types.rs` |
| 沙箱 crate | `codex-rs/sandboxing/` |
| Core 沙箱说明 | `codex-rs/core/README.md` |
| ExecPolicy | `codex-rs/execpolicy/` |
| Guardian | `codex-rs/core/src/guardian/` |
| Linux / Windows sandbox | `linux-sandbox/`, `windows-sandbox-rs/` |
