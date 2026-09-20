# 06 — Prebuilt、CLI 与 SDK

## 官方分层：Runtime vs Harness

```text
Deep Agents                 ← 厚 harness（规划、文件、子 Agent、部分上下文）
langchain.agents.create_agent ← 轻 harness（工具循环 + middleware）
LangGraph                   ← runtime（本目录主体）
```

- 要开箱 Agentic 体感 → 站 harness 层  
- 要强控流程 / 混确定性步骤 → 手写 `StateGraph`  
- harness **跑在** LangGraph 上，不是替代关系  

---

## Prebuilt：高层快捷入口

包：`langgraph-prebuilt`（通常随 `langgraph` 安装）

路径：`libs/prebuilt/langgraph/prebuilt/`

### `create_react_agent`（已弃用方向）

仍可用，但 v1 起官方标记 deprecated，推荐迁到 LangChain：

```python
# 旧（langgraph.prebuilt）
from langgraph.prebuilt import create_react_agent
app = create_react_agent(model, tools)

# 新（推荐）
from langchain.agents import create_agent
app = create_agent(model, tools, system_prompt="...")
```

`create_agent` 同样基于 LangGraph 运行，并增加更灵活的 middleware。

### `ToolNode`

执行 AIMessage 里 `tool_calls` 的节点，可嵌入自定义 `StateGraph`。

### Deep Agents

独立库 `deepagents`：官方口中的 **agent harness**。  
内置规划、虚拟文件系统、子 Agent、HITL 等；底层仍是 LangGraph。  
默认能力可覆盖一部分上下文管理，但仍可替换 / 扩展。

---

## CLI：本地开发与部署

包：`langgraph-cli`

| 命令 | 用途 |
|------|------|
| `langgraph new` | 从模板建项目 |
| `langgraph dev` | 本地 API Server + 热重载 |
| `langgraph build` / `up` | 镜像构建与拉起 |

```bash
uv add "langgraph-cli[inmem]"
langgraph dev --host 127.0.0.1 --port 2024
```

---

## SDK：对接 LangGraph Server

| SDK | 用途 |
|-----|------|
| `langgraph-sdk`（Python） | 建 thread、跑 run、订阅流 |
| `sdk-js` | 前端 / Node 同能力 |

```text
图代码 → CLI → Server → SDK/HTTP → 流式事件 →（可选）LangSmith
```

---

## 最小落地路径

1. `uv add langgraph` + 模型 provider（及按需 `langchain`）  
2. `create_agent` 或最小 `StateGraph`  
3. `InMemorySaver` 验证 thread / resume  
4. 换 Postgres checkpointer；按需加 Store  
5. **显式做上下文策略**（或选用 Deep Agents / middleware）  
6. 需要服务化时上 `langgraph-cli` + SDK  

钩子 / callback / middleware 专章见 [09-钩子与旁路扩展](./09-钩子与旁路扩展.md)。

---

*上一篇：[持久化与关键能力](./05-持久化与关键能力.md) · [下一篇：选型对照与阅读路径](./07-选型对照与阅读路径.md)*
