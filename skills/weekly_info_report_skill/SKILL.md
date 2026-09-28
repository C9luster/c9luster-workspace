---
name: weekly-info-report-skill
description: >-
  Collects and synthesizes a weekly frontier-tech briefing focused on LLM Agents
  and related computer science topics from official blogs (Cursor, Claude/Anthropic,
  OpenAI, etc.) plus discussions/comments. Use when the user asks for a weekly info
  report, 每周信息搜集, 每周前沿简报, 周报, blog weekly digest, or weekly_info_report_skill.
---

# Weekly Info Report Skill

按 **自然周** 从可配置信息源搜集 **LLM Agent / 模型 / 编程 Agent / 计算机前沿** 相关动态，整理成结构化周报。信息源可扩展，见 [sources.md](sources.md)。抓取失败备用链见 [fetch-playbook.md](fetch-playbook.md)。

## When to run

- 用户提到：周报、每周搜集、每周前沿简报、`weekly_info_report_skill`、Cursor/Claude/OpenAI 周汇总
- 需要「这一周有什么值得跟的 Agent/LLM 动态」

## Workflow

Copy and track:

```text
Weekly Info Report
- [ ] 1. 确定报告周次与范围
- [ ] 2. 加载信息源清单（sources.md + 用户追加）
- [ ] 3. 拉取各源本周条目（优先官方博客/changelog）
- [ ] 4. 补充讨论区/社区评论信号（必做补强）
- [ ] 5. 过滤、去重、分级
- [ ] 6. 按模板写出周报并落盘
- [ ] 7. 列出未覆盖源与失败项
```

### 1. 周次与范围

- 默认报告周：用户指定周；否则 **包含「今天」的自然周**（本地时区，**周一至周日**）。
- 周标识：ISO 周 `YYYY-Www`（如 `2026-W38`），并写明起止日期 `YYYY-MM-DD ~ YYYY-MM-DD`。
- 默认回看窗口：该自然周全日；用户可改为「过去 7 天滚动」或自定义。
- 主题优先级（高→低）：
  1. LLM Agent / Coding Agent / harness / tools / MCP / eval
  2. 模型发布、API、上下文/推理相关产品更新
  3. 开发者工具与 IDE Agent（Cursor 等）
  4. 其它 CS 前沿（系统、安全、MLSys）——仅在与 Agent/LLM 工作流相关或用户要求时展开

### 2. 加载信息源

1. 读取 [sources.md](sources.md) 中 **enabled** 源。
2. 合并用户本轮追加的 URL / 源名。
3. 若用户说「加上 XXX」，更新建议写回 `sources.md`（仅在用户明确要求修改配置时改文件）。

### 3. 拉取官方内容

对每个 enabled 源：

1. 读该源的 `fetch` 字段（见 [sources.md](sources.md)），按类型拉数，**不要**对所有源只 WebFetch 一次列表页。
2. 收集 **本周窗口内** 的标题、链接、摘要、发布/更新日期。
3. Changelog / Docs 更新页与 Blog 同等对待。
4. 主入口失败 → 走该源 `fallbacks` 与 [fetch-playbook.md](fetch-playbook.md)；备用成功则覆盖表记 `ok`（备注失败原因），**不要**整源放弃。
5. 备用链全失败才记 `fail`，不中断整份报告。

**已知易失败源（必须按 playbook）：**

| 源 | 常见失败 | 正确做法 |
|----|----------|----------|
| `openai-blog` / `openai-index` | 列表页 **403** | `site:openai.com/index after:周起始 before:下周一` → WebFetch 单篇 `/index/<slug>`；并拉 `developers.openai.com` changelog |
| Reddit `reddit-*` | 列表/JSON **timeout** | `site:reddit.com/r/<sub> <关键词> after:周起始`；OpenAI 话题优先补 `community.openai.com/c/codex` |

### 4. 讨论区 / 评论信号（必做补强）

官方博客页内评论区常为空或不可抓；**不能只采官方正文**。对每条 P0/P1 候选至少尝试一种社区信号：

| 策略 | 做法 |
|------|------|
| 官方页评论 | 有则摘 1–3 条高赞/维护者回复，并给锚点链接 |
| HN | Algolia **API**（`hn.algolia.com/api/v1/...`），勿只开 UI；摘 top 评论论点 + thread 链接 |
| Reddit | **优先 WebSearch** `site:reddit.com/r/...`（直接 WebFetch 列表易超时）；注明 subreddit |
| OpenAI 论坛 | [community.openai.com/c/codex](https://community.openai.com/c/codex)（Reddit 失败时的主备） |
| GitHub | Releases / Discussions / Issues 高互动楼层（产品开源时优先） |
| 论坛 / Discord 纪要 | Cursor Forum、公开 Discord 摘要帖；分类页不够则 `site:forum.cursor.com` 搜索（无法登录则记 `未覆盖`） |

启用的社区源见 [sources.md](sources.md)「社区讨论」一节。  
评论只保留 **可核实论点**；无讨论时在条目下写「无可靠社区信号」，禁止编造。

### 5. 过滤与分级

每条候选标级：

| 级 | 含义 |
|----|------|
| P0 | 直接影响 Agent 产品/脚手架选型或必须跟进的发布 |
| P1 | 重要但可稍后读的更新/论文/实践 |
| P2 | 值得知道的周边动态 |

去重规则：同一发布多源报道 → 合并为一条，**主链用官方**，讨论作附录。  
周报额外要求：同主题多条可收成「主题簇」，避免流水账。

### 6. 写报告

严格按 [report-template.md](report-template.md) 输出。

落盘路径（默认）：

```text
skills/weekly_info_report_skill/reports/YYYY-Www.md
```

若用户指定路径，以用户为准。同周重复运行 → 覆盖并在文首注明 `updated_at`。

写作要求：

- 中文简体；专有名词保留英文。
- 每条必须有 **链接**；无链接不进「要点」。
- 区分 **事实**（官方所述）与 **解读**（你的归纳）；解读单独小节或用「编者注」。
- 不编造日期、不编造评论；不确定标 `未核实`。
- 文首给出本周 3–5 条主线（叙事，而非日期流水）。

### 7. 收尾

向用户交付：

1. 报告文件路径
2. 三句话 executive summary
3. 失败源 / 建议下次启用的源

## Tools

- Prefer: `WebSearch`、`WebFetch`；需要登录墙后内容时再用浏览类工具。
- OpenAI / Reddit 失败时 **必须** 读并执行 [fetch-playbook.md](fetch-playbook.md)。
- 不要为「凑篇幅」扩写无关新闻。

## Extending sources

在 [sources.md](sources.md) 追加一块即可（id / 名称 / url / type / fetch / fallbacks / enabled）。  
类型建议：`blog` | `changelog` | `docs` | `discourse` | `hn-search` | `github` | `other`。  
新源若易墙，同步更新 [fetch-playbook.md](fetch-playbook.md)。

## Anti-patterns

- 只转述标题、无链接、无日期
- 把营销文案当技术结论
- 用 LLM 幻觉补「评论区热议」
- 按天堆砌、无周维度主线归纳
- 把其它脚手架对照表硬塞进报告（除非当周源文本身在对比）
- **列表页 403/timeout 后直接标 fail、不走 fallbacks / playbook**
- **对 Reddit 反复 WebFetch `/new/` 却不用 `site:reddit.com` 搜索**
