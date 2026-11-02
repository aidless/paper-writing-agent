# paper-writing-agent 预注册（PREREG）

> 本文档是研究规格（registered-report 风格），不是结果报告。它声明本仓库**计划检验的假设、评测方案、成功标准与明确边界**，全部基于 `README.md`、`SKILL.md`、`references/research-cycle.md`、`references/failure-modes.md`、`scripts/scanner_regression.py` 中已落盘的真实内容。本文档不虚构任何未执行的实验。

## 1. 研究问题

一个「证据优先」的论文写作 agent（编排提示词 + 确定性校验门 + 方法论文档）能否做到：

- **RQ1**：每个校验门都能**检出**其对应的论文缺陷（门必须能失败）？
- **RQ2**：报告中的统计量能否由 stdlib 独立重算，不信任上游数字？
- **RQ3**：稿件与其声明的证据是否一致，能否被机械校验（非人工判断）？

## 2. 预注册假设

| ID | 假设 | 检验方式 | 成功标准 |
|---|---|---|---|
| H1 | 每个校验门配 dirty fixture 反证，注入违规必红 | `scripts/scanner_regression.py` 27 个夹具目录、5 个家族 | 27/27 用例（25 PASS + 2 SKIP 环境降级），注入违规时 exit≠0 |
| H2 | 统计量自洽性由 stdlib 独立重算，不信任上游数字 | `scripts/scan_stats_consistency.py` + `scripts/independent_recompute.py` | 数字不一致被检出，报告值与重算值必须一致 |
| H3 | 稿件与其声明的证据一致可被机械校验 | Phase 3 六扫（数字一致/统计自洽/引文有效/合规/残留/哈希）+ `scan_hallucination.py` | 六类缺陷均被对应门检出 |
| H4 | 门在外部验证器缺失时降级而非静默通过 | `gate_citations.py` 的 `CITATION_VERIFIER_PATH` 处理 | 外部验证器缺失 → `Manual_needed` 并如实标注，不静默通过 |

## 3. 评测方案

- **回归基线**：`scripts/scanner_regression.py` 27/27 用例（25 PASS + 2 SKIP 环境降级，SKIP 为 `compile-gate/compile-error`、`compile-gate/multiply-label`，因本机无 TeX 编译层而降级为 `compile_skipped`，非静默通过）。
- **门禁清单**：Phase 3 六扫（数字一致性、统计自洽、引文有效性、图声明、编译门、幻觉扫描），见 `SCRIPTS.md` 51 个脚本全索引。
- **提交合规门**：G1–G11 门（`run_acceptance_gates.py`）+ 匿名化 + 哈希对账出包（Phase 5）。
- **对抗审稿**：`rebuttal_sim.py` 多角色模拟（独立重算/重编译核实），是模拟工具，不构成形式化证明。

## 4. 已声明边界（证明什么 / 不证明什么）

**证明什么（已实测）**：
- 六类确定性校验门能检出对应论文缺陷——每个门有 dirty fixture 反证，注入违规必红（`assets/scanner_fixtures/` 27 个夹具目录、5 个家族）。
- 统计量自洽性由 stdlib 独立重算校验，不信任上游数字。

**不证明什么（fail-closed 边界）**：
- 不保证投稿被接收、不评估研究本身的科学价值——只做「稿件与其声明的证据是否一致」的机械校验；一致性通过 ≠ 结论为真。
- 校验门是确定性规则，不是概率模型：无法检出设计缺陷、逻辑谬误、或「作者有意在声明与证据之间制造细微不一致」的对抗情形。
- `citation_verifier` 门在外部验证器缺失时降级为 `Manual_needed` 并如实标注，不静默通过。
- 不取代 D1–D3 的实验设计/执行/分析（外部 sibling skills），只消费其产物（protocol.md、结果 JSON）。

## 5. 成功标准（预先声明）

H1 与 H2 的**联合**成功 = 门能失败（注入违规必红）+ 统计量可独立重算。H3 成功 = 六类缺陷均被对应门检出。本文档声明的成功**不**包括「提升论文被接收概率」——那是审稿人/期刊的决策，不在本仓库声明范围。

## 6. 预注册时间戳与状态

- 本文档为**回顾性预注册**：反映仓库既有已落盘内容（`README.md`、`SKILL.md`、`scripts/scanner_regression.py`、`references/*.md`），不做前瞻性承诺。
- 目的：把「假设 + 评测方案 + 成功标准 + 边界」写清楚，供评审判断本仓库到底证明/不证明什么。
