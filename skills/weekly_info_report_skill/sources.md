# 信息源清单（可扩展）

编辑本文件即可增删源。Skill 运行时只抓取 `enabled: yes` 的条目。

抓取失败时的备用链见 [fetch-playbook.md](fetch-playbook.md)。

格式（每源一块）：

```yaml
- id: unique-id
  name: 显示名
  url: https://...          # 主入口（可为人读列表页）
  type: blog | changelog | docs | discourse | hn-search | github | other
  focus: 关注点简述
  fetch: webfetch | websearch-site | algolia-api | hybrid
  fallbacks:                # 可选；主入口失败时按序尝试
    - https://...
  enabled: yes
```

`fetch` 取值：

| 值 | 含义 |
|----|------|
| `webfetch` | 直接 WebFetch `url` |
| `websearch-site` | **不要**死磕列表页；用 `site:<域名>` + 周窗口搜索，再 WebFetch 命中 URL |
| `algolia-api` | 走 Algolia/JSON API |
| `hybrid` | 先 WebFetch；403/timeout 则自动切 websearch-site（见 playbook） |

---

## 默认源

### Cursor

```yaml
- id: cursor-blog
  name: Cursor Blog
  url: https://cursor.com/blog
  type: blog
  focus: IDE Agent、产品发布、工作流
  fetch: webfetch
  enabled: yes

- id: cursor-changelog
  name: Cursor Changelog
  url: https://cursor.com/changelog
  type: changelog
  focus: 版本与功能变更
  fetch: webfetch
  enabled: yes
```

### Anthropic / Claude

```yaml
- id: anthropic-news
  name: Anthropic News
  url: https://www.anthropic.com/news
  type: blog
  focus: Claude、研究、政策与产品
  fetch: webfetch
  fallbacks:
    - https://www.anthropic.com/institute
  enabled: yes

- id: anthropic-engineering
  name: Anthropic Engineering
  url: https://www.anthropic.com/engineering
  type: blog
  focus: 工程实践、Agent/应用构建
  fetch: webfetch
  enabled: yes

- id: claude-docs-release
  name: Claude Docs / Release notes
  url: https://docs.anthropic.com/en/release-notes/api
  type: docs
  focus: API、工具、Agent 相关文档更新
  fetch: webfetch
  fallbacks:
    - https://platform.claude.com/docs/en/release-notes/overview
    - https://docs.anthropic.com
  enabled: yes
```

### OpenAI

> **已知问题**：`openai.com/blog`、`openai.com/news` 列表页 WebFetch 常 **403**。  
> 正确做法：`fetch: hybrid` → WebSearch 发现 `openai.com/index/<slug>` → WebFetch 单篇；并始终拉 Developers changelog。

```yaml
- id: openai-index
  name: OpenAI Index / News（搜索发现 + 单篇）
  url: https://openai.com/index
  type: blog
  focus: 模型、产品、安全与 Agents 官方长文
  fetch: hybrid
  fallbacks:
    - search: site:openai.com/index after:{{week_start}} before:{{week_end_exclusive}}
    - https://openai.com/news/rss.xml
  enabled: yes

- id: openai-developers
  name: OpenAI Developers / API changelog
  url: https://developers.openai.com
  type: docs
  focus: API、Agents API、Codex、模型 changelog
  fetch: webfetch
  fallbacks:
    - https://developers.openai.com/api/docs/changelog
    - https://developers.openai.com/codex/changelog
  enabled: yes

- id: openai-blog
  name: OpenAI Blog（旧入口，易 403）
  url: https://openai.com/blog
  type: blog
  focus: 与 index 重叠；仅作兼容。列表 403 时改走 openai-index 搜索链，勿整源放弃
  fetch: hybrid
  fallbacks:
    - search: site:openai.com/index after:{{week_start}} before:{{week_end_exclusive}}
  enabled: yes
```

### 社区讨论（评论区 / 论坛信号）

> 与官方博客并列启用。官网正文有更新时，应用这些源补「社区怎么说」。

```yaml
- id: hn-frontier
  name: Hacker News (Algolia API)
  url: https://hn.algolia.com/api/v1/search?query=LLM+agent
  type: hn-search
  focus: 官方发文/论文的主讨论楼与 top 评论
  fetch: algolia-api
  fallbacks:
    - https://hn.algolia.com/api/v1/search_by_date?tags=story&numericFilters=created_at_i>{{week_start_unix}},created_at_i<{{week_end_unix}}
  enabled: yes

- id: reddit-localllama
  name: Reddit r/LocalLLaMA
  url: https://www.reddit.com/r/LocalLLaMA/
  type: discourse
  focus: 开源模型、本地 Agent、工具链实测评论
  fetch: websearch-site
  fallbacks:
    - search: site:reddit.com/r/LocalLLaMA after:{{week_start}}
  enabled: yes

- id: reddit-claudeai
  name: Reddit r/ClaudeAI
  url: https://www.reddit.com/r/ClaudeAI/
  type: discourse
  focus: Claude / Claude Code 使用体验与吐槽
  fetch: websearch-site
  fallbacks:
    - search: site:reddit.com/r/ClaudeAI after:{{week_start}}
  enabled: yes

- id: reddit-openai
  name: Reddit r/OpenAI
  url: https://www.reddit.com/r/OpenAI/
  type: discourse
  focus: OpenAI / Codex 相关讨论
  fetch: websearch-site
  fallbacks:
    - search: site:reddit.com/r/OpenAI after:{{week_start}}
    - search: site:reddit.com/r/codex after:{{week_start}}
  enabled: yes

- id: reddit-cursor
  name: Reddit r/cursor
  url: https://www.reddit.com/r/cursor/
  type: discourse
  focus: Cursor IDE Agent 体验与问题
  fetch: websearch-site
  fallbacks:
    - search: site:reddit.com/r/cursor after:{{week_start}}
  enabled: yes

- id: openai-community-codex
  name: OpenAI Developer Community · Codex
  url: https://community.openai.com/c/codex
  type: discourse
  focus: Codex 配额、模型下线、CLI/App bug 与功能请求（Reddit 不稳定时的主备社区源）
  fetch: webfetch
  enabled: yes

- id: cursor-forum
  name: Cursor Forum
  url: https://forum.cursor.com/
  type: discourse
  focus: 官方论坛帖与回复（产品问题、功能请求）
  fetch: hybrid
  fallbacks:
    - search: site:forum.cursor.com after:{{week_start}}
  enabled: yes

- id: github-openai-codex
  name: OpenAI Codex GitHub Discussions/Releases
  url: https://github.com/openai/codex/releases
  type: github
  focus: Release note 与 Discussions
  fetch: webfetch
  fallbacks:
    - https://github.com/openai/codex
  enabled: yes
```

### 可选扩展（默认关闭，按需改为 yes）

```yaml
- id: google-deepmind-blog
  name: Google DeepMind Blog
  url: https://deepmind.google/discover/blog/
  type: blog
  focus: 模型与 Agent 研究
  fetch: webfetch
  enabled: no

- id: meta-ai-blog
  name: Meta AI Blog
  url: https://ai.meta.com/blog/
  type: blog
  focus: 开源模型与研究
  fetch: webfetch
  enabled: no

- id: langchain-blog
  name: LangChain Blog
  url: https://blog.langchain.com/
  type: blog
  focus: LangGraph / Agent 工程
  fetch: webfetch
  enabled: no

- id: huggingface-blog
  name: Hugging Face Blog
  url: https://huggingface.co/blog
  type: blog
  focus: 开源模型与工具
  fetch: webfetch
  enabled: no

- id: latentspace
  name: Latent Space
  url: https://www.latent.space/
  type: blog
  focus: Agent/应用 AI 工程访谈与评论
  fetch: webfetch
  enabled: no

- id: simonwillison
  name: Simon Willison’s Weblog
  url: https://simonwillison.net/
  type: blog
  focus: LLM 应用与工具实践
  fetch: webfetch
  enabled: no

- id: reddit-machinelearning
  name: Reddit r/MachineLearning
  url: https://www.reddit.com/r/MachineLearning/
  type: discourse
  focus: 论文与业界讨论（噪声较大）
  fetch: websearch-site
  fallbacks:
    - search: site:reddit.com/r/MachineLearning after:{{week_start}}
  enabled: no
```

## 占位符

运行时替换：

| 占位符 | 含义 |
|--------|------|
| `{{week_start}}` | 本周周一 `YYYY-MM-DD` |
| `{{week_end_exclusive}}` | 下周一 `YYYY-MM-DD`（用于 `before:`） |
| `{{week_start_unix}}` / `{{week_end_unix}}` | 对应 Unix 秒（HN `numericFilters`） |

## 如何新增源

1. 复制一块 YAML，改 `id`（唯一）、`name`、`url`、`type`、`focus`、`fetch`。
2. 若列表页易 403/timeout，设 `fetch: hybrid` 或 `websearch-site`，并写 `fallbacks`。
3. 设 `enabled: yes`。
4. 若踩到新墙，把现象与备用链补进 [fetch-playbook.md](fetch-playbook.md)。
