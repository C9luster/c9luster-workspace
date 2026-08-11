# 06 — Prebuilt、CLI 与 SDK

## Prebuilt：高层快捷入口

包：`langgraph-prebuilt`（通常安装 `langgraph` 即带上，无需单独关注包名）

路径：`libs/prebuilt/langgraph/prebuilt/`

### `create_react_agent`

预置「模型 ⇄ 工具」ReAct 风格循环，适合快速验证工具调用 Agent。

```python
from langgraph.prebuilt import create_react_agent

app = create_react_agent(model, tools)
app.invoke({"messages": [{"role": "user", "content": "..."}]})
```

### `ToolNode`

专门执行 AIMessage 里 tool_calls 的节点，可嵌入自定义 `StateGraph`，自己掌控边与状态，同时复用工具执行逻辑。

### 其他

- interrupt 相关辅助
- tool 校验 / Agent Inbox 一类 schema（随版本演进，以 API reference 为准）

**选型**：能用 prebuilt 先跑通，再把需要定制的部分拆成手写 `StateGraph`。

### Deep Agents（生态上层）

官方另推更高层的 Deep Agents（规划、子 Agent、文件系统等），底层仍基于 LangGraph。本知识库不展开，需要时查 LangChain 文档的 Deep Agents overview。

---

## CLI：本地开发与部署

包：`langgraph-cli`

常见命令：

| 命令 | 用途 |
|------|------|
| `langgraph new` | 从模板建项目 |
| `langgraph dev` | 本地 API Server + 热重载 |
| `langgraph build` / `up` | 镜像构建与拉起（Docker 工作流） |

开发模式常装 extras：

```bash
uv add "langgraph-cli[inmem]"
langgraph dev --host 127.0.0.1 --port 2024
```

`libs/cli` 内还有 JS / Python monorepo 示例，说明如何把 agent 应用拆成 apps + shared libs。

---

## SDK：对接 LangGraph Server

| SDK | 用途 |
|-----|------|
| `langgraph-sdk`（Python） | 客户端调 Server：建 thread、跑 run、订阅流 |
| `sdk-js` | 前端 / Node 同能力 |

典型链路：

```text
你的图代码
  → CLI 打成 LangGraph Server
  → SDK / HTTP 创建 thread + run
  → 流式事件回前端
  → （可选）LangSmith 观测
```

与「进程内 `compiled.invoke`」对比：

| | 进程内 | Server + SDK |
|---|---|---|
| 集成复杂度 | 低 | 中 |
| 多客户端 / 多语言 | 弱 | 强 |
| 运维与扩缩 | 自管 | 平台 / 容器化更顺 |
| HITL / 长任务 | 可用 | 更适合做成服务 |

---

## 和 LangSmith 的关系

LangGraph 可单独跑；上生产时常配：

- **LangSmith**：轨迹、评估、调试
- **LangSmith Deployment / Studio**：部署、可视化原型、团队复用

本目录聚焦开源编排运行时；平台侧细节以 LangSmith 文档为准。

---

## 最小落地路径

1. `uv add langgraph` + 模型 provider  
2. `create_react_agent` 或最小 `StateGraph`  
3. 加上 `InMemorySaver` 验证 thread / resume  
4. 换 Postgres checkpointer  
5. 需要服务化时上 `langgraph-cli` + SDK  

---

*上一篇：[持久化与关键能力](./05-持久化与关键能力.md) · [下一篇：选型对照与阅读路径](./07-选型对照与阅读路径.md)*
