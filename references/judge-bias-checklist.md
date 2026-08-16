# Judge 反偏置检查表(LLM-as-Judge survey E054 落地,I2)

> 来源: A Survey on LLM-as-a-Judge(2411.15594)偏置分类法 + your stack 的既有缓解。
> 用途: 对抗审稿 / 终评 / rebuttal 模拟的 judge prompt 启用前与评审中对照本表。

## 四类主要偏置与缓解

| 偏置 | 表现 | 本栈缓解 | 检查 |
|---|---|---|---|
| 位置偏置 | 偏向 A/B 中先出现的 | 盲对双判 + 位置交换(judge_dual.py) | 一致性率 ≥80%? |
| 自偏好 | 偏向与自己(同族模型)输出一致的 | judge 与被测异源;双模型终评(O2) | judge 模型 ≠ 被测模型家族? |
| 冗长/格式偏置 | 长输出/特定格式得分高 | 输出截断上限 + JSON-only schema | 长度归一? |
| 权威/顺序偏置 | 受角色/排序影响 | 角色独立 prompt,无跨角色通信 | 角色间无通信? |

## 启用前检查(每条可勾选)

- [ ] 位置偏置: 双判位置交换已启用,一致性率报告
- [ ] 自偏好: judge 与被测模型异源(或声明同源并计入 agreement)
- [ ] 冗长: 输入截断(如 40k 字符上限)+ 输出仅 JSON
- [ ] 校准: judge 已用同分布 gold set 校准(FPR<0.10/FNR<0.15,self-assessment-calibration.md §1.5)
- [ ] 判定优先级: 可程序化判定的(数字/文件/引用)先走断言,judge 只兜底

## 评审中监控

- 每轮记录 judge 一致性率 → rounds_consistency.jsonl(I4);下降 = 自偏放大信号;
- 同一缺陷被 ≥2 角色独立指出 = 高置信(既有经验 2);单角色独见 = 复核。

## 纪律

- judge 是仪器,报告其性能(FPR/FNR/一致性),不把 judge 输出当人工标注(powercontext 边界声明);
- 发现偏置 → 先修 judge prompt/换 judge,不靠"多跑几次"掩盖。
