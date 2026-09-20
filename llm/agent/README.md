# AI Agent 学习笔记

AI Agent 开发与实践。

## 目录结构

```text
agent/
├── README.md
├── benchmark/       # Agent 评测与数据集构建
├── claude-code/     # Claude Code Agent 框架知识库
├── codex/           # Codex Agent 框架知识库
├── langchain/       # LangChain 生态（含 LangGraph）
└── skill/           # Skill 相关（待补充）
```

同级协议知识库见 [../protocols/](../protocols/)（模型 Wire API 与 MCP/A2A 等）。  
用 Agent 写代码的实践技巧见 [../tips/](../tips/)。

## 脚手架文档约定

撰写或增补某个 Agent 脚手架知识库时：

1. **必须有 Hook / 等价扩展点说明**（生命周期拦截、middleware、callback、图内策略节点等，按该脚手架真实机制写）。  
2. **各脚手架独立成文**：不写「相对 XX 脚手架」对照表或互比段落。  
3. **不写入公司内部运行时/业务仓库说明**（只基于该脚手架公开实现与文档）。

| 脚手架 | Hook 相关文档 |
|--------|----------------|
| [claude-code](./claude-code/) | [07-扩展机制 · Hooks](./claude-code/07-扩展机制.md) |
| [codex](./codex/) | [07-扩展机制 · Hooks](./codex/07-扩展机制.md) |
| [langgraph](./langchain/langgraph/) | [09-钩子与旁路扩展](./langchain/langgraph/09-钩子与旁路扩展.md) |

## 知识库索引

| 目录 | 内容概要 |
|------|----------|
| [benchmark/](./benchmark/) | SWE / Terminal-Bench 数据集构建、验证模块与任务性质 |
| [claude-code/](./claude-code/) | 交互形态、Agentic Loop、多层上下文、多 Agent、工具与权限、**Hooks**、会话持久化 |
| [codex/](./codex/) | Core/App-Server、Turn 准入、WorldState、Multi-Agent V2、沙箱与 Guardian、**Hooks** |
| [langchain/langgraph/](./langchain/langgraph/) | 有状态编排、Checkpoint/Store、harness 分层、**钩子与 middleware**、心智模型 |
| [skill/](./skill/) | Skill 机制相关笔记 |
| [../protocols/](../protocols/) | Chat Completions / Responses / Messages / Gemini、兼容层、MCP/A2A |
| [../tips/](../tips/) | Coding Prompt、Agent 高效开发、前沿社区 |

## 学习主题（总览）

- Agent 框架与架构设计
- 工具调用（Tool Calling）
- 多 Agent 协作
- ReAct 模式
- 记忆与上下文管理
- 错误处理与重试机制
- Agent 评估与测试
- 实际应用场景

## 相关框架

- LangChain / LangGraph（见 [langchain/](./langchain/)）
- Claude Code（见 [claude-code/](./claude-code/)）
- Codex（见 [codex/](./codex/)）
- AutoGPT / BabyAGI / CrewAI 等（待整理）

## 学习 TODO

| 序号 | 主题 | 状态 |
|------|------|------|
| 1 | Codex | 已完成（见 [codex/](./codex/)） |
| 2 | Deer-Flow | 待学习 |
| 3 | ExploreAgent | 待学习 |
| 4 | Pi | 待学习 |
| 5 | grok-build | 待学习 |
| 6 | kimi-code | 待学习 |
| 7 | benchmark | 已开始（见 [benchmark/](./benchmark/)） |

AI 办公 / Vibe Coding 见独立目录 [../../ai-applications/](../../ai-applications/)。

## 相关资源

- 持续更新中…
