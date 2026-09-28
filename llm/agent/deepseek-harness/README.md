# DeepSeek Harness 知识库

本目录整理 DeepSeek Harness（`dsh`）的 Agent 机制：交互形态、Agentic Loop、上下文工程、多 Agent 编排、工具与安全边界、扩展机制与会话持久化。

> 独立知识库；机制描述以 DeepSeek Harness 公开仓库实现与文档为准。运行时由 Cordis 插件树组装。扩展点是类型化事件与可替换服务；`hooks` 组另提供 Claude Code / Codex command hook 桥接。

---

## 文档索引

| 序号 | 文档 | 内容概要 |
|------|------|----------|
| 01 | [概述与架构](./01-概述与架构.md) | Profile、组合包、Cordis、能力 seam |
| 02 | [交互形态与 Agentic Loop](./02-交互形态与Agentic-Loop.md) | 轮次与步骤、事件域、输入领取 |
| 03 | [上下文管理](./03-上下文管理.md) | 会话日志、系统提示词、压缩、Skills |
| 04 | [子 Agent 与多 Agent 编排](./04-子Agent与多Agent编排.md) | 进程内/进程外委派、可继续子级、Agent Teams |
| 05 | [工具系统与能力边界](./05-工具系统与能力边界.md) | 工具流水线、文件系统、shell、MCP、Jobs |
| 06 | [安全、权限与 Plan Mode](./06-安全权限与Plan-Mode.md) | 沙箱模式、审批、权限预设、计划模式 |
| 07 | [扩展机制](./07-扩展机制.md) | 事件、插件、Hooks 桥接、Skills |
| 08 | [会话持久化与恢复](./08-会话持久化与恢复.md) | JSONL generation、检查点策略、投影 |
| 09 | [特性与模式索引](./09-特性与模式索引.md) | 能力清单与默认组合 |

---

## 定位摘要

DeepSeek Harness 是可组合的 Agent 运行时。产品能力以 `@deepseek-ai/dsh-*` 包按组交付，由 profile 与组合包在启动时叠成一棵插件树。默认循环是「调用模型、执行工具、再进入下一步」；持久事实写入仅追加会话日志，模型可见历史从该日志派生。
