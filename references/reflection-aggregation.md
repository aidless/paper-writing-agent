# Reflection Aggregation(跨轮反思聚合,B3)

> 来源: Generative Agents(arXiv:2304.03442)定期把记忆聚合成高维见解
> ("关于 X 我学到了什么");对接 Reflexion(gate_reflection)与你的 FM 库。
> 适用: 长论文项目每 3 轮生成一次"本项目失败模式画像",防止同模式反复踩。

## 协议(每 3 轮执行一次)

1. **收集**: 汇总最近 3 轮的 GATES 日志 + gate_reflection 卡死记录 + 审稿
   Critical/Major + ROUND 的失败与纠正尝试;
2. **聚类**: 按失败模式归类(对照 FM-15..29 库;新模式记 `FM-<new>` 候选);
3. **画像输出** `FAILURE_PATTERN_<n>.md`:
   - 每模式: 触发情境 / 出现次数 / 是否已入 FM 库 / 根因假设 / 修复是否落地;
   - 高影响模式(≥2 次或含 Critical): 升格为下一轮审稿焦点;
4. **注入**: 画像摘要进下一轮 ROUND 开头(与 gate_reflection 反思块并列),
   并对照 `references/failure-modes.md` 补漏检的失败模式;
5. **沉淀**: 新确认的模式 → 建议 FM 库新增条目(用户批准后入库);
   已修复的模式 → 标 resolved,防回归(接 scanner_regression 加夹具)。

## 与既有机制的关系

| 机制 | 角色 |
|---|---|
| gate_reflection | 单门禁连续失败 → 本轮反思(短循环) |
| 本协议 | 跨轮聚合 → 模式画像(长循环,每 3 轮) |
| FM 库 | 画像的对照表与归宿 |
| scanner_regression | 新失败模式的回归锁(夹具) |
| SELF_ASSESSMENT | 画像作为终评前"项目级自省"输入 |

## 执行要求

- 每满 3 轮强制产出画像(不进上下文,落盘文件);
- 画像只基于 GATES/审稿/ROUND 的可复现记录,不凭印象(证据门禁);
- 画像中"未复现的失败"标注为假设,不硬化为结论(反捕获纪律)。
