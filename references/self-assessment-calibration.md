# Self-Assessment Calibration(双模型终评 + judge agreement,O2)

> 来源: jcode 的 judge agreement 复跑思想 + research-kit judge_calibration_kit + floor-model 政策
> 目的: 收敛后的 TMLR 加权终评不是"一个模型说了算",而是两个模型独立打分、
> 报告一致性;不一致 = 终评不稳定,不得直接作为结论引用。
> C1(2026-08): 补 Agent-as-a-Judge(arXiv:2410.10934)强制步骤——judge 上岗前
> 必须用**与被测任务同分布**的 gold set 校准;judge 与被测能力差距本身是偏置源。

## 1. 背景

现状: Phase 4.5 收敛后用 scholar-evaluation 的 TMLR 加权分
(0.30N + 0.35S + 0.25Si + 0.10C)做终评,落盘 SELF_ASSESSMENT.md。
问题: 单模型自评既是作者又是评审(serena 式立场冲突),分数可能有系统性偏好。

## 1.5 judge 上岗前校准(Agent-as-a-Judge,C1,强制第一步)

终评/审稿 judge **启用前**必须先自校准,否则分数不可信:

1. **同分布 gold set**: 准备已人工定级的样例(与被测手稿同类型/同难度,如上一轮
   收敛论文的定级评审),不跨任务借用(judge 与被测能力差距 = 偏置源);
2. **校准协议**: 按 research-kit `judge_calibration_kit.md` 跑 FPR/FNR;
   通过门槛(如 FNR<0.15 且 FPR<0.10,参考 ARS 门)才启用该 judge;
3. **记录**: SELF_ASSESSMENT.md 写明"该 judge 已用 N 条同分布 gold set 校准,
   FPR/FNR = …";未校准的 judge 分数标注"未经校准的模型估计";
4. 校准失败 → 换 judge 模型或补 gold set,不降低门槛硬启。

## 2. 双模型终评协议

1. **独立打分**: 两个模型(建议 pro + flash,floor-model 政策——flash 代表"更弱但
   更常见的评审者")分别对同一手稿按四维打分,互不看到对方分数;
2. **报告 agreement**: 记录两模型各维分数 + 加权总分;一致率 = 同维分数相同的比例
   (或 |Δ总分| 阈值判断);
3. **判定**:
   - 一致率 ≥ 80%(或 |Δ总分| ≤ 阈值)→ 终评稳定,取两模型平均分入
     SELF_ASSESSMENT.md,并注明双模型;
   - 一致率 < 80%(或 |Δ总分| 超阈值)→ 标记 `UNSTABLE`,不直接作为结论;
     分歧维(如 N 差 2 分)列为下一轮审稿焦点,回 Phase 4.5 再核。

## 3. 与 judge_calibration_kit 的接线

- 若存在 gold set(已人工定级的样例评审/分数): 用 research-kit 的
  `judge_calibration_kit.md` 协议校准每个评审模型的 FPR/FNR,校准通过才启用
  该模型的终评分(与 deepteam/ARS 的 judge 验收门同构);
- 无 gold set 时: 至少保留双模型 agreement 报告,并声明"终评是模型估计,
  不是人工标注"(powercontext judge boundary 纪律)。

## 4. 纪律(强化既有)

- **审稿收敛 ≠ 科学结论成立**: 双模型一致只说明"流程问题清零且模型估计稳定",
  不证明 N/Si 有真实证据——无证据维永远不给 4(既有规则 7 不变);
- 终评分数变化必须有新证据支撑,禁止"改分数凑一致"(既有硬规则 7 延伸);
- SELF_ASSESSMENT.md 记录: 两模型各维分数、总分、agreement、判定
  (stable/unstable)、gold set 校准状态(如有)。

## 5. 落地方式

- 有 workflow 工具时: 两个 `agent(prompt, {model})` 独立跑 scholar-evaluation
  四维 rubric,主 agent 合并分数 + 算 agreement;
- 无 workflow 时: 串行跑两次,第二次 prompt 明确"独立打分,勿参考上次结果"。
