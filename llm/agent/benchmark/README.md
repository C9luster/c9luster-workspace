# Agent Benchmark 知识库

聚焦 **Agent 评测数据集如何构建**：以 SWE-bench 与 Terminal-Bench 为主，梳理流水线、关键模块与任务应具备的性质。

> 机制描述以公开论文与官方仓库为准；不绑定私有跑测路径。

---

## 文档索引

| 序号 | 文档 | 内容概要 |
|------|------|----------|
| 01 | [数据集构建与性质](./01-数据集构建与性质.md) | **选题来源**、**覆盖广度**、构建流水线、模块与性质 |

## 一句话对照

| | SWE-bench | Terminal-Bench |
|--|-----------|----------------|
| **选题怎么来** | 自动挖：Merged PR + Issue + 测试改动，再执行录取 | 人写/投稿：rubric 收「可验证终态 + 概念难」题 |
| **Agent 要交付什么** | 能让测试 fail→pass 的 **patch** | 容器内达成 **outcome**（文件/服务/状态） |
| **如何判分** | FAIL_TO_PASS / PASS_TO_PASS | `tests/test.sh` → `reward.txt` |
| **覆盖靠什么** | 加仓/语言衍生、按 repo 分层报分 | category 策展、缺领域征稿、分层报分 |

## 关键链接

- SWE-bench: [论文](https://arxiv.org/abs/2310.06770) · [GitHub](https://github.com/SWE-bench/SWE-bench) · [collect 说明](https://github.com/SWE-bench/SWE-bench/tree/main/swebench/collect)
- Terminal-Bench: [论文](https://arxiv.org/abs/2601.11868) · [tbench.ai](https://www.tbench.ai) · [Harbor Tasks](https://www.harborframework.com/docs/tasks)
- 任务写作指南: [Adversarial / Difficult / Legible](https://arxiv.org/html/2604.28093) · [TB3 proposal rubric](https://github.com/harbor-framework/terminal-bench-3/blob/main/rubrics/task-proposal.md)

---

*整理：2026-09-15*
