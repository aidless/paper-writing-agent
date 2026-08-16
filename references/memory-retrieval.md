# Memory Retrieval(三因子记忆检索,B2,Generative Agents)

> 来源: Generative Agents(arXiv:2304.03442)记忆流检索评分 = 新近度 × 重要性 × 相关性。
> 适用: 会话开始时从 lessons/FINDINGS 检索可用经验,以及跨轮复用论文项目知识。

## 三因子检索公式

```
score = w_recency · recency + w_importance · importance + w_relevance · relevance
```

| 因子 | 定义 | 论文 agent 的取值来源 |
|---|---|---|
| 新近度(recency) | 距现在的衰减(半衰期) | 条目日期(现有 lessons 已含) |
| 重要性(importance) | 该经验曾对应的严重程度 | gate 连续 FAIL 次数 / 审稿 severity(Critical/Major)/ FM 编号命中 |
| 相关性(relevance) | 与当前任务的相似度 | 任务相似度(现有 retrieve_lessons 用 embedding/关键词) |

## 与既有检索的关系

- 现状(continuous-memory LESSON): `retrieve_lessons.py` 用
  **任务相似度 × 置信度 × 新近度**;
- 本协议补**重要性因子**: 同一相似度下,曾引发 gate 连续失败或审稿 Critical 的
  教训应排前面——否则高频小教训会淹没低频高影响教训;
- 落地方式: 在 lessons/FINDINGS 条目加 `importance` 字段(0-1,= min(1, 0.2·连续失败
  次数 + 0.4·Critical 次数 + 0.4·FM 命中)),检索排序时乘入。

## 跨轮反思聚合的输入(B3 衔接)

- 检索不只看单条,还要**聚合**: 同主题条目聚类 → 生成"该主题的平均重要性",
  供跨轮反思(每 3 轮失败模式画像)使用。

## 执行要求

- 会话开始检索时: 除相似度外报告 importance 排名(谁最该进上下文);
- 新 lessons/FINDINGS 条目写入时: 填 importance 字段(可后补,证据门禁不变)。

## 落地实现(2026-08-15)

脚本: `scripts/retrieve_experience.py`(本协议的代码实现, 纯标准库)。

- 用法: `python scripts/retrieve_experience.py --task "<任务>" --ledger <lessons.md> [--findings f.jsonl] [--top 5] [--task-type auto|knowledge|general|reasoning|hallucination_sensitive] [--out digest_experience.md] [--include-draft]`; `--selftest` 自测。
- **importance 字段已入 lessons.md 第 11 列**(2026-08-15 起; schema 头注释含规范)。取值规范:
  `importance = min(1, 0.2·连续失败次数 + 0.4·审稿Critical次数 + 0.4·FM命中数)`; 新条目可后补,
  缺省由 conf/status 推导(high=0.8/med=0.6/low=0.4, verified+0.1, 封顶 0.95)。
- **默认只检索 verified/active**(证据门禁, 与 continuous-memory 一致); `--include-draft` 仅审计用。
- **α 任务类型加权**(E073/memory-trust-scheduling): 权重表按 (relevance/importance/recency)
  knowledge(0.75/0.15/0.10)、general(0.60/0.25/0.15)、reasoning(0.45/0.30/0.25)、
  hallucination_sensitive(0.50/0.30/0.20)——知识任务重相关性, 推理/防幻觉压相关性抬重要性/新近度。
- FINDINGS: 结构化 JSONL 可选支持(`--findings`, 字段 id/sit/act/importance/date);
  FINDINGS.md 自由格式需手工转为 JSONL 后方可检索。
- 验收: `--selftest` PASS + 真实账本排序测试(importance 高者置顶)。
- 与 retrieve_lessons.py 分工: 前者是 continuous-memory 的 LESSON 检索(相似度×置信度×新近度,
  已 A/B hold); 本脚本是论文 agent 的经验检索(三因子 + importance), 共享 lessons.md。
