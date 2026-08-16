# EXPERIMENT_PLAN.md — 声明驱动实验路线图

> **借鉴 Modex EXPERIMENT_PLAN_TEMPLATE（逆向学习 2026-08-14），适配本技能门控。**
> 用途：D1 阶段（实验设计）产出，驱动 D2（执行）与 D3（分析）。
> 每个 Claim 必须有"最低说服证据"——这直接映射到 CLAIM_LEDGER 的验证方法列。

## Problem & Thesis

- **Problem**：[要解决的问题]
- **Method Thesis**：[方法一句话]

## Claim Map

| Claim | Why It Matters | Minimum Convincing Evidence | Linked Blocks | Ledger ID |
|-------|---------------|------------------------------|---------------|-----------|
| C1: [主声明] | [为什么重要] | [证据标准，如 "配对 Wilcoxon p<0.05 + 效应量 r>0.3"] | B1, B2 | C01 |
| C2: [支撑声明] | [为什么重要] | [证据标准] | B3 | C02 |

> **纪律**：Claim 的"最低证据"必须在 D1 写死（预注册），D3 不降低标准。
> 证据标准映射到 CLAIM_LEDGER 的验证方法列（可执行检查）。

## Experiment Blocks

### Block 1: [主实验名]
- **Claim tested**: C1
- **Dataset / split / task**: [e.g., CIFAR-10 test]
- **Compared systems**: [方法 vs 基线 A vs 基线 B]
- **Metrics**: [Primary + Secondary]
- **Setup details**: [架构/优化器/lr/epochs/seeds]
- **Success criterion**: [e.g., "Holm 校正 p<0.05"]
- **Failure interpretation**: [负结果意味着什么——预注册]
- **Priority**: MUST-RUN

### Block 2: [消融]
- **Claim tested**: C1 (novelty isolation)
- **Compared systems**: [Full vs -A vs -B]
- **Success criterion**: [每组件贡献阈值]
- **Priority**: MUST-RUN

### Block 3: [补充实验]
- **Priority**: NICE-TO-HAVE

## Run Order（决策门）

| Milestone | Goal | Runs | Decision Gate | Cost |
|-----------|------|------|---------------|------|
| M0: Sanity | 管线跑通 | 1 quick | Loss 下降? | ~0.5h |
| M1: Baselines | 复现基线 | Block 3 | 数字对齐? | ~4h |
| M2: Main | 主实验 | Block 1 | 达标准? | ~8h |
| M3: Ablation | 消融 | Block 2 | 组件都有用? | ~6h |

## Compute Budget

- **Total**: ~X GPU-hours
- **Hardware**: [e.g., RTX 3060 6GB 共享]
- **Biggest bottleneck**: [e.g., 基线复现]

## Risks

- **Risk** → **Mitigation**

---

## 与现有机制的关系

- Claim Map 的"最低证据" → CLAIM_LEDGER 验证方法列（已验证/阻塞状态）
- Run Order 的 Decision Gate → gates_config.json 的验收门
- Failure Interpretation → HYPOTHESES.md 的"若不成立则如何"（预注册）
- 本模板 → `F:\deepseek\demo-tmlr-paper\evidence\EXPERIMENT_PLAN.md`（Phase A 实际应用）
