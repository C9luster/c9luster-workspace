# 前沿从哪跟

## 一句话

Agent 迭代太快，**没有一个类似 Stack Overflow 的总论坛**。高信号讨论在 Discord、X、播客和会议；中文源适合扫新闻和补底座，不宜当唯一信源。

## 怎么跟（低负担闭环）

1. 每周听 1 期 [Latent Space](https://www.latent.space/)，只跟自己正在做的主题（session、tool、eval、coding agent）。
2. 只常驻 1 个 Discord（Latent Space 或 Anthropic），静音刷，卡住再问。
3. 看到新范式（skills、MCP、native session、eval harness）立刻用 coding agent 复现一版最小实验。
4. 写一页「什么有效、什么失败」——比收藏 20 个社区有用。

## 英文：信号最高

| 去哪 | 形态 | 适合跟什么 |
|------|------|------------|
| [Latent Space](https://www.latent.space/) | 播客 + [Discord](https://www.latent.space/p/community) + 每周 Paper Club | Agent / RAG / eval / harness，应用 AI 工程的主场 |
| [AI Engineer](https://www.ai.engineer/) | World’s Fair / Summit | 落地工程，不是纯论文会 |
| Anthropic Discord | 实时讨论 | Claude Code、agent 产品向实战 |
| Cursor Forum / Discord | 实时 / 帖子 | 编辑器工作流、Agent 模式、rules |
| X | 信息流 | `@swyx`、`@karpathy`、`@simonw`、Anthropic / Cursor 工程师。这个领域比传统论坛快 |
| GitHub Discussions | 协议 / 仓库 | MCP、各 harness / runner。协议层变化看这里最准 |

加入方式以各站当前入口为准；Latent Space Discord 邀请链接偶尔会失效，从官网 community 页再取一次。

## 论文和深度源

- arXiv `cs.AI` / `cs.CL`，配合 Hugging Face Papers
- [Interconnects](https://www.interconnects.ai/)：训练 / post-training
- [Simon Willison 的博客](https://simonwillison.net/)：工具调用、MCP、工程笔记

## 中文：能跟，别当唯一信源

| 去哪 | 适合 |
|------|------|
| [Datawhale Hello-Agents](https://github.com/datawhalechina/hello-agents) | 系统入门，补底座 |
| V2EX | 偶尔有生产级脚手架 / 踩坑帖 |
| 即刻 | 比知乎快，适合追工具链变化 |
| 知乎 / 机器之心 / 量子位 | 扫新闻可以，深度讨论少 |

公司内用知识库（ku / 如流）建自己的 paper club 和 postmortem，往往比追外部群更贴近正在做的 gateway、session、filesync 这类 harness 问题。

## 不建议的跟法

- 同时加十几个 Discord，全部当主时间线
- 只看中文二手解读、不读原仓库 / 原论文
- 收藏工具清单但不复现：这个领域「听过」和「跑通过」差一个数量级

## 和本仓库其他目录的关系

- 框架原理：[../agent/](../agent/)（Claude Code、LangGraph）
- 协议层：[../protocols/](../protocols/)（Wire API、MCP/A2A）
- 怎么用这些知识写代码：本文 + [coding-prompt](./coding-prompt.md) + [coding-agent-workflow](./coding-agent-workflow.md)
