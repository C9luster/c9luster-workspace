# 06 — 安全、权限与 Plan Mode

Claude Code 拥有完整 Shell 访问权，安全机制不是可选装饰，而是 Agent 架构的内建边界。

---

## 三种权限行为

每次工具调用，系统做出三种裁决之一：

| 行为 | 含义 | 典型场景 |
|------|------|----------|
| **Allow** | 自动放行 | Read 项目内文件 |
| **Ask** | 弹出确认 | Bash 未知命令 |
| **Deny** | 直接拒绝 | 被禁止的命令 |

---

## 规则来源与优先级

规则从 8 个来源汇聚，**后者覆盖前者**：

```text
1. userSettings        ~/.claude/settings.json
2. projectSettings     .claude/settings.json
3. localSettings       .claude/settings.local.json
4. flagSettings        --settings 参数
5. policySettings      企业策略（用户不可覆盖）
6. cliArg              --allow / --deny
7. command             Skill 的 allowedTools 白名单
8. session             用户当前对话「Always allow」
```

每个来源维护：alwaysAllowRules、alwaysAskRules、alwaysDenyRules。

规则结构：`{ toolName, ruleContent? }`，如 Bash + "git *"、Edit + "src/**"。

---

## 三维度匹配引擎

### 1. 工具名匹配

精确匹配工具或 MCP server 级别：
- `Bash` → BashTool
- `mcp__server1` → 该 server 所有工具
- `mcp__server1__*` → 通配符

### 2. 命令模式匹配（Bash）

通过 tree-sitter bash AST 解析第一个子命令，与 ruleContent glob 匹配。

### 3. 路径匹配（文件工具）

Read/Edit/Write 的 getPath 与 ruleContent glob 匹配。

---

## 权限检查完整流程

```text
1a. Blanket deny（工具名完全匹配 deny → 直接 deny，getTools 阶段已过滤）
1b. Blanket allow（工具名完全匹配 allow → allow）
2.  工具自身 checkPermissions（Bash: readOnly → sandbox → AST → 模式）
3.  Hook：PreToolUse 可 override
4.  Ask 规则检查
5.  默认行为（按 permissionMode）
```

---

## 权限模式

| 模式 | 行为 | 备注 |
|------|------|------|
| default | 多数敏感操作 ask | 外部可见 |
| acceptEdits | 安全路径读/编辑 allow，危险仍 ask | 外部可见 |
| plan | **只读**：写操作 deny，仅 `isReadOnly()` 工具 | 保存 `prePlanMode` |
| bypassPermissions | 全部 allow | 显式危险 |
| dontAsk | 尽量不弹问（偏自动拒绝/按规则） | 外部可见 |
| auto | 分类器辅助自动裁决 | 偏内部 / `TRANSCRIPT_CLASSIFIER` |
| bubble | fork 子 agent：权限请求上浮父终端 | 类型存在；fork definition 使用；非外部主模式集 |

外部校验集合见 `PERMISSION_MODES`（含 dontAsk，不含 auto/bubble 作为对外主枚举的情况以 `isExternalPermissionMode` 为准）。

| auto | 自动模式 + classifier |

Plan Mode 通过 prepareContextForPlanMode 切换；退出 ExitPlanMode 恢复。

---

## Plan Mode：先看后做

### 问题

「重构这个模块」→ AI 立刻改代码，方向错了已改一半。

### 闭环四步

1. **EnterPlanMode**：AI 或用户触发，需用户审批
2. **探索阶段**：mode=plan，仅 Read/Grep/Glob/Agent 等只读工具
3. **ExitPlanModeV2**：提交计划文件，第二个审批节点
4. **恢复执行**：用户批准后恢复进入前模式，按计划执行

### Prompt-based 权限

ExitPlanMode 可声明 allowedPrompts：

```json
[{ "tool": "Bash", "prompt": "run tests" }]
```

用户批准后，「run tests」类 Bash 自动放行，无需逐个确认。

### 计划文件持久化

- 计划写入磁盘，用户**可编辑**后再批准
- planWasEdited 标记影响 tool_result 回显
- Swarm 下 teammate 发 plan_approval_request 到 lead mailbox

---

## 沙箱（Sandbox）

沙箱限制 Bash 的文件系统和网络访问范围，与权限模式协同：

- 只读命令可能自动 allow
- 沙箱外操作升级 ask
- 与 worktree isolation 配合实现文件改动隔离

（具体策略随 feature flag 和平台变化，核心思想：**默认最小权限，逐步放宽**。）

---

## Auto Mode

自动模式通过 transcript classifier 判断是否可跳过部分确认，提高流畅度。classifier 可在 REPL 每 turn 检查并可能禁用 fastMode（断路器）。

---

## Denial Tracking 死循环防护

permissionDenials 记录拒绝历史，防止 AI 反复请求同一被拒操作。QueryEngine 追踪 hasHandledOrphanedPermission 处理孤立权限请求。

---

## 子 Agent 权限特殊性

| 场景 | 行为 |
|------|------|
| 普通 subagent | 按 agent definition permissionMode 重新 assembleToolPool |
| fork | 继承父 exact tools + bubble 上浮 |
| coordinator worker | ASYNC_AGENT_ALLOWED_TOOLS，不能嵌套编排 |
| teammate | mode 参数仅影响 plan_mode_required spawn |
| in-process teammate | 不能 spawn teammate 或后台 agent |

---

## 安全设计原则总结

1. **权限即边界**：每次 tool call 双重校验
2. **Plan 先于 Act**：复杂任务强制只读探索
3. **规则可叠加**：8 层来源，session 级「Always allow」最灵活
4. **Hook 可拦截**：PreToolUse 企业/custom 审计
5. **沙箱 + 权限**：Shell 能力分层约束
6. **子 Agent 隔离**：独立工具池，fork 例外继承

---

## 企业合规要点

- policySettings 用户不可覆盖
- managed MCP 配置
- MIIT 等区域合规响应（特定构建）
- 遥测与远程配置审计（可选）
