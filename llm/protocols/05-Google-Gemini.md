# 05 — Google Gemini（GenAI）

## 一句话定义

Google Gemini 的主流应用接口是 Generative AI / Gemini API 的 **`generateContent` / `streamGenerateContent`**：对话以 `contents` 表达，内容以 `parts` 组成，响应落在 `candidates` 里。

它与 OpenAI / Anthropic 是 **第三种独立 schema**，不是「小改字段名」的变体。

## 设计目标

| 目标 | 体现 |
|------|------|
| 原生多模态 | text / inline blob / file URI 等统一进 parts |
| 明确的系统指令字段 | `system_instruction` |
| Google Cloud / AI Studio 一体 | 同一家族 API 覆盖 Studio 与 Vertex 部署形态 |

## 请求形状（核心字段）

概念示意（字段名以当前官方 SDK/REST 为准）：

```json
{
  "system_instruction": {
    "parts": [{ "text": "You are a precise assistant." }]
  },
  "contents": [
    {
      "role": "user",
      "parts": [
        { "text": "Describe this image." },
        { "inline_data": { "mime_type": "image/jpeg", "data": "…" } }
      ]
    }
  ],
  "tools": [],
  "generationConfig": {
    "temperature": 0.2,
    "maxOutputTokens": 1024,
    "responseMimeType": "application/json"
  }
}
```

### 角色与结构差异

| 主题 | Gemini | OpenAI Chat Completions | Anthropic Messages |
|------|--------|-------------------------|-------------------|
| 对话容器 | `contents` | `messages` | `messages` |
| 内容单元 | `parts` | `content` string/parts | content blocks |
| 系统提示 | `system_instruction` | system 角色消息 | 顶层 `system` |
| 模型角色名 | 常见 `user` / `model` | `assistant` | `assistant` |
| 输出长度 | `maxOutputTokens` | `max_tokens` / `max_completion_tokens` | `max_tokens` |

把 OpenAI 客户端的 `assistant` 角色原样送给 Gemini，或把 `max_tokens` 原字段塞进 Gemini，是移植时的高频错误。

## 响应形状

```json
{
  "candidates": [
    {
      "content": {
        "role": "model",
        "parts": [
          { "text": "…" },
          { "functionCall": { "name": "lookup", "args": { "q": "…" } } }
        ]
      },
      "finishReason": "STOP"
    }
  ],
  "usageMetadata": {
    "promptTokenCount": 100,
    "candidatesTokenCount": 40,
    "totalTokenCount": 140
  }
}
```

要点：

- 主路径是 `candidates[0].content.parts`，不是 `choices[0].message`
- `finishReason` 枚举命名风格不同于 OpenAI（如 `STOP`、`MAX_TOKENS`）
- 安全过滤可能导致 candidate 为空或 finishReason 指向安全相关原因——要单独处理

## 工具调用（Function Calling）

Gemini 的 function calling 同样是「声明工具 → 模型返回 functionCall → 本地执行 → 以 functionResponse part 回灌」，但：

- 工具声明 schema 的嵌套位置与 OpenAI `tools[].function` 不同
- 回灌角色/part 类型是 Gemini 自己的 `functionResponse` 语义
- 并行调用、强制调用（tool config）的参数名也不同

经 Chat Completions 兼容层调用 Gemini 时，工具字段常被翻译；原生能力（某些 grounding、Google 搜索集成等）可能只在 GenAI 原生面完整。

## 流式

`streamGenerateContent` 推送增量 candidate/parts。与 OpenAI 的差异：

- 帧结构跟 `candidates` 对齐，不是 `choices[].delta`
- 文本增量在 part 上累积
- 结束原因、安全评级可能出现在流的中后段

## Vertex AI 与 AI Studio

同一套「Gemini 内容模型」会出现在：

| 入口 | 特点 |
|------|------|
| Google AI Studio / Gemini API Key | 个人/小团队快速接入 |
| Vertex AI | 企业 IAM、VPC、区域、计费与治理 |

协议语义相近，但鉴权、endpoint、模型名资源路径不同。写多环境配置时把「schema」和「部署入口」分开。

## 何时优先选它

- 主模型是 Gemini，需要原生多模态 / Google 生态集成
- 已在 GCP 上做 IAM 与数据治理
- 需要 Gemini 特有的 grounding / 某些 Google 工具链

## 何时走兼容层

- 应用已绑死 OpenAI SDK，只是换模型供应商试 Gemini
- 能接受工具/多模态/安全事件的语义损耗

## 实现检查清单

- [ ] 角色用 `model` 而不是盲写 `assistant`
- [ ] 长度参数用 `maxOutputTokens`
- [ ] 解析走 `candidates[].content.parts`
- [ ] 处理空 candidate / 安全过滤
- [ ] 区分 AI Studio 与 Vertex 的鉴权与模型资源名
