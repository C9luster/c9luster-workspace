# LangChain 生态学习笔记

按子项目归档 LangChain 相关开源框架笔记。当前从 **LangGraph** 开始。

## 目录结构

```text
langchain/
├── README.md
└── langgraph/          # 有状态 Agent / 工作流编排框架
    ├── README.md
    ├── 01-概述与定位.md
    ├── 02-仓库结构与包依赖.md
    ├── 03-核心架构.md
    ├── 04-状态通道与控制流.md
    ├── 05-持久化与关键能力.md
    ├── 06-Prebuilt-CLI与SDK.md
    └── 07-选型对照与阅读路径.md
```

## 分类说明

| 目录 | 内容 |
|------|------|
| [langgraph/](./langgraph/) | LangGraph monorepo 定位、架构、Checkpoint、HITL、CLI/SDK |

## 约定

- 文件名：序号 + 中文主题；正文中文
- 风格对齐同级 `../claude-code/`：索引 README + 分篇深挖
- 对照本地源码：`workspace/github/langgraph`
- 后续可在本目录下增补 `langchain-core/`、`deep-agents/` 等子笔记
