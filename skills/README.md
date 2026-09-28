# Skills

本目录存放 **c9luster-workspace 项目级 Agent Skills**（与 `llm/` 脚手架笔记独立）。

## 目录

| Skill | 说明 |
|-------|------|
| [weekly_info_report_skill](./weekly_info_report_skill/) | 按自然周从 Cursor / Claude / OpenAI 等官方博客与讨论区搜集 LLM Agent 等前沿信息并出周报 |

## 使用

在对话中点名 skill，或描述「跑每周信息报告 / 每周前沿简报 / 周报」。  
各 skill 以目录内 `SKILL.md` 为准；信息源扩展改对应 `sources.md`。

### 推荐提示词（周报）

```text
请按 skills/weekly_info_report_skill 执行本周前沿信息周报。

要求：
1. 先读 SKILL.md、sources.md、report-template.md
2. 只抓 sources.md 里 enabled: yes 的源
3. 周区间：包含今天的自然周（周一至周日，本地时区）；文中写清 YYYY-Www 与起止日期
4. 焦点：LLM Agent / Coding Agent / harness / MCP / 模型与 API 更新
5. 每条 P0/P1 必须尝试补社区信号；没有就写「无可靠社区信号」，禁止编造
6. 按模板写成中文周报（要有本周主线，不要按天流水账），保存到：
   skills/weekly_info_report_skill/reports/YYYY-Www.md
7. 完成后三句话 executive summary，并列出失败/空源
```

## 约定

- 每个 skill 一个子目录，内含 `SKILL.md`
- 详细清单与模板用 progressive disclosure（如 `sources.md`、`report-template.md`）
- 报告等产物默认写在该 skill 的 `reports/` 下（若 skill 需要）
