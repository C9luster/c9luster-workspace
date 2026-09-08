# AI Agent 学习笔记

AI Agent 开发与实践。

## 目录结构

```text
agent/
├── README.md
├── claude-code/     # Claude Code Agent 框架知识库
├── langchain/       # LangChain 生态（含 LangGraph）
└── skill/           # Skill 相关（待补充）
```

同级协议知识库见 [../protocols/](../protocols/)（模型 Wire API 与 MCP/A2A 等）。  
用 Agent 写代码的实践技巧见 [../tips/](../tips/)。

## 知识库索引

| 目录 | 内容概要 |
|------|----------|
| [claude-code/](./claude-code/) | 交互形态、Agentic Loop、上下文、多 Agent、工具与权限、会话持久化 |
| [langchain/langgraph/](./langchain/langgraph/) | 有状态编排、棋盘控制流、Checkpoint/Store、harness 分层、心智模型 |
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
- AutoGPT / BabyAGI / CrewAI 等（待整理）

## 学习 TODO

| 序号 | 主题 | 状态 |
|------|------|------|
| 1 | Codex | 待学习 |
| 2 | Deer-Flow | 待学习 |
| 3 | ExploreAgent | 待学习 |
| 4 | Pi | 待学习 |

## 相关资源

- 持续更新中…
