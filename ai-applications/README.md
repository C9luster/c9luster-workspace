# AI Applications

AI 应用向学习笔记。本文「AI 办公」指 **WorkBuddy / DuMate 这类全能工作搭子**，不是中台/套件产品；**Vibe Coding 是其子集**（也可抽成 Cursor/秒哒等专精 App）。

总览 → [00-harness对比与集合关系.md](./00-harness对比与集合关系.md)。

## 目录结构

```text
ai-applications/
├── README.md
├── 00-harness对比与集合关系.md
├── 01-vibecoding-harness设计.md
└── 02-ai-office-harness设计.md
```

## 知识库索引

| 文档 | 内容概要 |
|------|----------|
| [00-harness对比与集合关系.md](./00-harness对比与集合关系.md) | 父集口径、VC⊂办公、二者皆 cmd 控机、长程/后台、难单测化 |
| [01-vibecoding-harness设计.md](./01-vibecoding-harness设计.md) | VC 子集：仓库+终端 ACI |
| [02-ai-office-harness设计.md](./02-ai-office-harness设计.md) | 工作搭子父集 harness（含多世界剖面） |

## 一句话对照

| | AI 办公（WorkBuddy/DuMate 向） | Vibe Coding |
|--|--------------------------------|-------------|
| **集合** | 工作搭子 **父集** | **⊂ 父集**；可抽成专精产品 |
| **覆盖** | 通用工作 + 文档/浏览/… +（可含）写代码 | repo + shell + 测/预览 |
| **Harness** | `U ∪ W ∪ V ∪ …` + **长程/后台 job** | `U ∪ V`（前台环为主，长任务为加分） |

## 学习 TODO

| 序号 | 主题 | 状态 |
|------|------|------|
| 1 | Harness 对比与集合关系 | 已整理 |
| 2 | Vibe Coding harness 设计 | 已整理 |
| 3 | AI 办公（工作搭子）harness 设计 | 已整理（待按 WorkBuddy/DuMate 实例加深） |
| 4 | 产品案例对照 | 待补充 |
| 5 | 评测与 oracle（办公难单测化；见 00 §1.0c） | 已点题，案例待补 |

## 相关文档

- [00-harness对比与集合关系.md](./00-harness对比与集合关系.md)
- [01-vibecoding-harness设计.md](./01-vibecoding-harness设计.md)
- [02-ai-office-harness设计.md](./02-ai-office-harness设计.md)
