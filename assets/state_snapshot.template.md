# STATE_SNAPSHOT.md — 科研状态快照（E104，InnovatorBench InternalSummarizeAction 模式）

> 用途：写作各阶段（Phase 1 登记 → Phase 2 起草 → Phase 4 修改）强制维护的
> "科研工作台"状态机。claim ledger 管"声明↔证据"的静态对账；本快照管
> "研究进程"的动态状态——当前要超越的基线、假设生命周期、实验史、反思。
> 终稿交付前，claim ledger 与快照必须一致（快照里的 PROVEN 假设才能以
> 强断言出现；TESTING/TODO 只能 hedge 或 inconclusive，见 E095）。

## 状态字段（每轮修改后更新）

| 字段 | 内容 | 示例 |
|---|---|---|
| `state_of_the_art` | 本工作要超越的基线（论文+数值），可追溯到文献综述 | "2504.02902：迭代校准 ECE 0.38（raw）" |
| `hypotheses` | 假设清单 + 生命周期标记 `[TESTING]/[PROVEN]/[TODO]` | "H1：演化后统一校准最低 raw ECE [PROVEN]" |
| `key_knowledge` | 关键领域知识/约束（含反例） | "温度缩放对退化分布分桶无效（E083）" |
| `reflection` | 对已做实验的反思（什么没控制好） | "三臂实验单 seed，非统计裁决" |
| `experiment_history` | 已跑实验（配置→结果→证据文件） | "armA: 演化后校准 ECE 0.0703 → three_arm_result.json" |
| `recent_actions` | 最近的动作（写了什么/改了什么） | "补 B1 幻觉扫描 + 回归 24/24" |
| `open_questions` | 未决问题（对应 claim ledger 的 inconclusive） | "机制解释缺消融 → 降级 inconclusive" |

## 假设生命周期规则

- `[TODO]`：已登记未实验 → 正文不得提及（或只能作为 future work）；
- `[TESTING]`：实验进行中/已有初步结果未复核 → 正文 hedge；
- `[PROVEN]`：证据文件 + 独立重算通过 → 可强断言，且 claim ledger 对应条目必须 verified；
- 任何假设状态变更必须在 `experiment_history` 记录触发证据（文件路径）。

## 时机

- Phase 1（claim ledger 登记）时初始化快照；
- 每次 Phase 2 起草/Phase 4 修改轮后更新（与 ledger 同批）；
- Phase 3 机器检查把 `open_questions` 与 claim ledger 的 inconclusive 条目对账；
- Phase 5 交付前：快照 `hypotheses[PROVEN]` ↔ ledger `verified` ↔ 正文强断言三处一致。
