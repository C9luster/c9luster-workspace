# 06 — 云厂商封装：Bedrock 与 Azure

## 一句话定义

云厂商协议多半是 **「统一控制面 + 多种模型后端」**：你面对的是云侧 API，背后再路由到 Anthropic / Meta / Google / OpenAI 等模型。字段可能统一，也可能提供「OpenAI 形状」兼容面。

## 为什么需要这一层

直接调各家原生 API 时，企业常缺：

- 统一 IAM、审计、VPC、密钥托管
- 跨模型的护栏（guardrails）与限流
- 区域与数据驻留控制
- 账单归集到同一云账户

于是出现 Bedrock、Azure OpenAI、Vertex 等「平台 API」。

---

## Amazon Bedrock

Bedrock Runtime 上常见几类调用面：

| API | 典型用途 |
|-----|----------|
| **Converse / ConverseStream** | 跨模型的统一消息接口（推荐写可移植业务代码） |
| **InvokeModel / InvokeModelWithResponseStream** | 贴近模型原生 payload，控制更细 |
| **OpenAI 兼容面（Chat Completions / Responses）** | 方便迁移已有 OpenAI SDK 代码（以当前区域/模型支持矩阵为准） |

### Converse 心智模型

```text
messages: [{ role, content: [{ text / image / … }] }]
inferenceConfig: { temperature, maxTokens, stopSequences, … }
toolConfig: { tools, toolChoice }
guardrailConfig: { … }   # 可选
```

特点：

- 一套代码可切换 Claude / Llama 等（模型需支持 messages）
- 模型特有参数可走 additional model fields
- Guardrails 可在平台层做内容策略，而不只靠 prompt

### InvokeModel

当你需要某模型独有字段、或 Converse 尚未覆盖的能力时使用。代价是：**每个模型家族可能要单独适配**，回到碎片化。

### 流式

ConverseStream / ResponseStream 事件是 AWS 事件流形状，不等于 OpenAI SSE chunk。写通用 SSE 解析器时不要假设 Bedrock 原生流能直接复用。

---

## Azure OpenAI

Azure OpenAI 基本沿用 OpenAI 的 **Chat Completions /（视开通情况）Responses** 等形状，但部署模型不同：

| 维度 | 典型差异 |
|------|----------|
| 鉴权 | Azure AD / API Key；资源级 endpoint |
| 模型定位 | 用 **deployment name**，不是任意公开 model slug |
| 网络 | 私有终结点、区域数据驻留 |
| 内容过滤 | Azure 侧 content filter 可能改写/截断响应 |

对应用开发者：协议「看起来像 OpenAI」，运维与合规「是 Azure 资源」。把 base URL、api-version、deployment 配错，是最常见的联调失败原因。

---

## 其他常见平台面（简表）

| 平台 | 协议倾向 |
|------|----------|
| **Google Vertex AI** | Gemini GenAI schema + Google Cloud IAM |
| **OpenAI 直接 API** | Chat Completions / Responses 原厂 |
| **多模型聚合网关** | 通常对外 Chat Completions，对内翻译（见下一篇） |

---

## 选型直觉

```text
要企业 IAM / Guardrails / 多模型一站式
  → Bedrock Converse 或对应云平台统一 API

已有 OpenAI 代码，迁到企业云
  → Azure OpenAI 或 Bedrock 的 OpenAI 兼容面

要某模型 100% 原生能力（thinking 细节、最新工具）
  → 直连厂商原生 API，云封装可能滞后或改写
```

## 实现检查清单

- [ ] 分清「统一消息 API」与「模型原生 Invoke」两条路径
- [ ] 流式解析按云事件格式实现，不硬套 OpenAI chunk
- [ ] Azure 使用 deployment + api-version，而不是假设公开 model 名通用
- [ ] 打开 guardrail / content filter 后，把「被拦截」当成一等错误类型处理
