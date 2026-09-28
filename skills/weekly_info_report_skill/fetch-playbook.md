# Fetch Playbook（失败源修复手册）

Agent 跑周报时优先用 **WebSearch / WebFetch**。下列源在常见 Agent 环境下会失败；**按表内顺序换入口，不要把整源标成永久 fail**。

## 总原则

1. 列表页失败 ≠ 该源无内容；先换备用 URL / 搜索发现，再 WebFetch **单篇**。
2. 同一发布只保留一条：官方主链 + 社区附录。
3. 所有备用路径仍失败 → 源覆盖表写 `fail` + 具体原因（403 / timeout / empty），继续其它源。

---

## OpenAI 官网（`openai-blog` / `openai-index`）

### 现象

| 入口 | WebFetch 常见结果 |
|------|-------------------|
| `https://openai.com/blog` | **403** Forbidden |
| `https://openai.com/news` | **403** |
| `https://openai.com/index`（列表） | **403** |
| `https://openai.com/news/rss.xml` | **500** 或不稳定 |
| `https://openai.com/index/{slug}`（单篇） | **通常 OK** |
| `https://developers.openai.com` / changelog | **通常 OK** |

根因：Cloudflare 对列表/营销页拦指纹；单篇文章与 Developers 站较宽松。

### 推荐抓取链（按序）

```text
1. WebSearch（发现本周 slug）
   site:openai.com/index after:YYYY-MM-DD before:YYYY-MM-DD
   可选加关键词：Agents OR Codex OR GPT OR Astra OR API

2. 对每条结果 WebFetch 单篇
   https://openai.com/index/<slug>

3. 并行拉 Developers（不依赖 openai.com 列表）
   https://developers.openai.com
   https://developers.openai.com/api/docs/changelog
   https://developers.openai.com/codex/changelog

4. 仍缺条目时
   WebSearch: OpenAI Codex OR "Agents API" OR Astra after:周起始
   → 用官方 URL 回抓；二次报道只作线索
```

### 不要做的事

- 不要只 WebFetch `openai.com/blog` / `news` 一次就记 `fail` 并跳过 OpenAI。
- 不要把 RSS 当唯一入口（WebFetch 上常 500）。
- 本地 Shell 若遇代理 403，可用 Chrome impersonation（如 `curl_cffi`）拉 RSS；**Agent 默认路径仍以 WebSearch + 单篇 WebFetch 为准**。

---

## Reddit（`reddit-*`）

### 现象

| 入口 | WebFetch 常见结果 |
|------|-------------------|
| `https://www.reddit.com/r/.../new/` | **timeout** |
| `.../new.json` / `.rss` / `old.reddit.com` | **timeout** 或不可用 |
| WebSearch `site:reddit.com/r/SUB ...` | **通常 OK**（含标题、片段、评论摘录） |

根因：Reddit 对自动化抓取慢/拦；搜索索引仍可发现帖子。

### 推荐抓取链（按序）

```text
1. 对本周 P0/P1 标题或产品名做 WebSearch
   site:reddit.com/r/OpenAI <关键词> after:YYYY-MM-DD
   site:reddit.com/r/ClaudeAI ...
   site:reddit.com/r/cursor ...
   site:reddit.com/r/LocalLLaMA ...
   可选：site:reddit.com/r/codex ...

2. 需要完整楼层时，再 WebFetch 具体帖 URL
   （单帖有时比列表页更容易成功；仍 timeout 则只用搜索摘要 + 帖链接）

3. OpenAI 产品讨论优先补官方论坛（比 Reddit 稳）
   https://community.openai.com/c/codex
```

### 记覆盖状态

- 搜索命中并摘到可核实论点 → 源状态 `ok`（方式：websearch），注明 subreddit。
- 搜索无结果 → `empty`。
- 搜索与单帖均不可用 → `fail`（timeout），改用 HN / 官方论坛。

---

## Hacker News（对照：应保持稳定）

```text
列表/评论 API（优先）:
https://hn.algolia.com/api/v1/search?query=<url或标题>&tags=story
https://hn.algolia.com/api/v1/items/<id>

按自然周时间窗（Unix 秒）:
numericFilters=created_at_i>START,created_at_i<END
```

WebFetch 上述 JSON 通常可用。UI 页 `hn.algolia.com/?q=` 仅作人读入口。

---

## Cursor Forum

- `https://forum.cursor.com/` 分类页可开，但深度帖可能需登录。
- 失败时：WebSearch `site:forum.cursor.com <关键词> after:周起始`；仍无则 `未覆盖`。

---

## 源覆盖表怎么写

| 情况 | 状态 | 备注示例 |
|------|------|----------|
| 列表 403，但 Search+单篇成功 | `ok` | listing 403；via site:openai.com/index |
| Reddit 列表 timeout，Search 有帖 | `ok` | via WebSearch site:reddit.com/r/... |
| 备用链全失败 | `fail` | 403 listing；search empty |
| 有入口无本周条目 | `empty` | — |

---

## 快速自检（跑周报前 30 秒）

1. WebFetch `https://openai.com/news` → 若 403，立刻走 Search 链，勿重试列表。
2. WebFetch `https://www.reddit.com/r/OpenAI/new/` → 若 timeout，立刻 `site:reddit.com/...` Search。
3. WebFetch `https://developers.openai.com/api/docs/changelog` → 应成功；失败则升级为整源网络问题。
