# LangChain 生态学习笔记

按子项目归档 LangChain 相关开源框架笔记。当前从 **LangGraph** 开始。

## 目录结构

```text
langchain/
├── README.md
└── langgraph/          # 有状态 Agent / 工作流编排框架
    ├── README.md
    ├── 01 … 07         # 定位、架构、控制流、Memory、CLI、选型
    └── 08-心智模型与常见误解.md   # 讨论沉淀
```

## 分类说明

| 目录 | 内容 |
|------|------|
| [langgraph/](./langgraph/) | 定位与架构、node/edge、Checkpoint/Store、harness 分层、心智模型 |

## 约定

- 文件名：序号 + 中文主题；正文中文
- 风格对齐同级 `../claude-code/`：索引 README + 分篇深挖
- 机制描述以官方文档与开源实现为准
- 后续可在本目录下增补 `langchain-core/`、`deep-agents/` 等子笔记
