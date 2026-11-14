# paper-writing-agent

[![CI](https://github.com/aidless/paper-writing-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/aidless/paper-writing-agent/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)
![License](https://img.shields.io/badge/license-Apache--2.0-green)
![Tests](https://img.shields.io/badge/scanner_regression-27%2F27%20PASS-brightgreen)

**证据优先的论文写作 Agent Skill**（TMLR 投稿向）：编排提示词（`SKILL.md`）+ 51 个可运行的确定性校验门（`scripts/`，约 10K 行）+ 27 篇方法论文档（`references/`）+ TMLR 官方 LaTeX 模板（`templates/tmlr/`）。

核心设计：**每个校验门都配 dirty fixture 反证**（`assets/scanner_fixtures/` 27 个夹具目录、5 个家族，`scanner_regression.py` 27/27 用例（25 PASS + 2 SKIP 环境降级）——门必须能失败，才配得上"门"这个字），统计量由 stdlib 独立重算（不信任上游数字）。
## 快速开始

```bash
pip install -r requirements.txt
python3 scripts/scanner_regression.py   # 自检：27 项门禁回归（2.2s，真实输出见下）
# make regression 等价（Makefile 硬编码 `python`；无该别名时直接用上一行）
make ci           # 全量 CI 门（需本机 TeX；云端 CI 已内置）
```

实跑输出（2026-11-10，CPython 3.12，无 TeX 环境）：

```text
[PASS] hallucination/clean: OK
[PASS] stats-consistency/p-stat-mismatch: OK
...
[PASS] compile-gate/compile-error: SKIP (compile_skipped 环境降级)
[PASS] compile-gate/multiply-label: SKIP (compile_skipped 环境降级)

scanner regression: 27/27 PASS
```

引用验证门通过环境变量 `CITATION_VERIFIER_PATH` 指向外部 `verify_citations.py`（未设置时依次尝试本机历史路径 → 仓内 `tools/citation-verifier/verify_citations.py`；均不存在则该门降级为 `Manual_needed` 并如实标注，不静默通过）。

## 文档地图

- [SKILL.md](SKILL.md) — Agent 编排入口（各 Phase 触发哪些门）
- [SCRIPTS.md](SCRIPTS.md) — 51 个脚本全索引（docstring 自动生成）
- [README_EN.md](README_EN.md) — English overview + CI guide
- [references/](references/) — 方法论 27 篇（含 `failure-modes.md` 真实改稿教训库）
- [references/research-cycle.md](references/research-cycle.md) — 完整科研循环 D0–D5 与本包边界
- [templates/tmlr/](templates/tmlr/) — TMLR 官方模板

## 编排一览（SKILL.md 的 Phase 结构）

```
Phase 0   Intake                证据包验收：manifest 哈希对账、数据-声明可溯源
Phase 1   Claim ledger          每个数字/主张先入 ledger（file+field 级溯源）
Phase 2   Draft                 TMLR 模板起稿，引用先行（bib 先于正文）
Phase 3   Machine checks        六扫：数字一致性/统计自洽/引文有效性/合规/残留/哈希
Phase 4   Revision loop         R 轮修订：修复→重扫→门全过才算收敛
Phase 4.5 Adversarial review    多角色对抗审稿（独立重算/重编译核实）
Phase 5   Submission compliance 匿名化 + G1-G11 门 + 哈希对账出包
```

## 与完整科研循环的关系（边界声明）

本包是研究循环 `research-cycle.md`（D0–D5）中的 **D4 写作核心 + D4.5 对抗审稿 + D5 投稿合规**：

| 阶段 | 归属 |
|---|---|
| D0 文献综述 / D0.5 假设生成 | 部分内置（`literature_discovery.py`）；novelty 排序依赖外部 `scholar-evaluation` skill |
| D1 实验设计 / D2 实验执行 / D3 分析 | 外部 sibling skills（ablation-design / statistical-analysis / reproducibility），本包只消费其产物（protocol.md、结果 JSON） |
| **D4 写作 / D4.5 对抗审稿 / D5 投稿** | **本包全覆盖** |

## 复算（可复现）

所有报告中的数字均可从仓库内实际文件/命令重算，不依赖记忆：

| 声明 | 重算命令 | 实测值 |
|---|---|---|
| 校验门数量（脚本） | `ls scripts/*.py \| wc -l` | 51 |
| 脚本总行数 | `cat scripts/*.py \| wc -l` | 10030 |
| 方法论文档 | `ls references/*.md \| wc -l` | 27 |
| 夹具目录（leaf） | `find assets/scanner_fixtures -mindepth 2 -maxdepth 2 -type d \| wc -l` | 27 |
| 回归用例 | `python3 scripts/scanner_regression.py` | 27/27（25 PASS + 2 SKIP 环境降级） |
| 脚本索引 | `grep -cE '^\| `' SCRIPTS.md` | 51 |

> SKIP 用例（`compile-gate/compile-error`、`compile-gate/multiply-label`）因本机无 TeX 编译层而降级为 `compile_skipped`（夹具内 manifest 显式声明 `skip_when: compile_skipped`），**不是静默通过**——回归日志逐条记录降级原因，云端 CI 安装 TeX 后同夹具转 PASS。

## 边界声明（证明什么 / 不证明什么）

**证明什么**：
- 六类确定性校验门（数字一致性、统计自洽、引文有效性、图声明、编译门、幻觉扫描）能**检出**对应的论文缺陷——每个门都有 dirty fixture 反证，注入违规必红（`assets/scanner_fixtures/`），这是「门必须能失败」的实证。
- 统计量自洽性由 stdlib 独立重算校验，**不信任上游数字**（`scan_stats_consistency.py`）。

**不证明什么**（fail-closed 边界）：
- 本包**不保证**投稿被接收、不评估研究本身的科学价值——它只做「稿件与其声明的证据是否一致」的机械校验；一致性通过 ≠ 结论为真。
- 校验门是**确定性规则**，不是概率模型：无法检出设计缺陷、逻辑谬误、或「作者有意在声明与证据之间制造细微不一致」的对抗情形（对抗审稿 `rebuttal_sim.py` 是模拟工具，不构成形式化证明）。
- `citation_verifier` 门在外部验证器缺失时**降级为 `Manual_needed` 并如实标注**，不静默通过——这本身是边界而不是功能。
- 本包**不取代** D1–D3 的实验设计/执行/分析（外部 sibling skills），只消费其产物（protocol.md、结果 JSON）。

## License

Apache-2.0（`templates/tmlr/` 沿用 JmlrOrg 官方模板的 Apache-2.0 许可）

## Limits

- `make regression` 依赖 `python` 命令名（Makefile 硬编码）；在只有 `python3` 的系统上
  直接跑 `python3 scripts/scanner_regression.py`（等价）。
- `compile-gate` 两项夹具需要本机 TeX（pdflatex）；无 TeX 时按 `SKIP (环境降级)` 计入
  PASS 并如实标注，云端 CI（py3.11–3.13）已装 TeX 全量跑。
- 引用验证门在 `CITATION_VERIFIER_PATH` 未指向有效脚本时降级为 `Manual_needed` 并如实
  标注——降级可见，不静默通过。
- 本包只覆盖写作/审稿/投稿（D4–D5）；实验设计与统计分析是外部 sibling skills 的职责。

## 结构导览

| 路径 | 内容 |
|------|------|
| `SKILL.md` | Agent 编排入口（Phase 0–5 各触发哪些门） |
| `scripts/` | 49 个确定性校验门（约 10K 行，`SCRIPTS.md` 有全索引） |
| `assets/scanner_fixtures/` | 27 个夹具目录，每门配 dirty 反证 |
| `references/` | 27 篇方法论文档（含 `failure-modes.md` 教训库） |
| `templates/tmlr/` | TMLR 官方 LaTeX 模板 |
| `scripts/scanner_regression.py` | 回归锁：`27/27 PASS`（2.2s） |

## 验收题库与复算

`eval/cases.jsonl` 是 20 条可执行验收题，覆盖 12 个模块/口径（`stats/mcnemar`、
`stats/rank`、`stats/strata`、`power/design`、`ledger/path`、`scanner/pvalue`、
`numbers/scan`、`compile-gate/static`、`fixtures/inventory`、`manifest/integrity`、
`docs/evidence-states`、`docs/phase-map`）。其中 18 条是 `expr`/`raises`，**真调本仓
`scripts/` 的 API 或真解析仓内数据文件**（夹具 JSON、`scanner_regression.py` 的
FAMILIES 字面量、27 个夹具目录）；期望值不是抄文档，而是调用模块现算：

```bash
python3 eval/run_cases.py            # 20/20 cases passed
python3 eval/run_cases.py --save     # 顺带把结果写进 eval/run-report.json
python3 eval/run_cases.py --selftest # 篡改一条期望值，必须变红（19/20）
```

三种 `mode`：`expr`（`verify` 是 Python 代码，执行后读 `result` 与 `expected` 比，
数值容差 1e-9）、`raises`（断言抛出的异常类名，如 BOM manifest → `JSONDecodeError`、
把单张 2×2 表传给 `breslow_day` → `TypeError`）、`doc`（`路径::正则`，断言文档里
写明了某条口径，如证据状态机的「工程失效结果 ≠ 科学负结果」）。

**数字如何复算**：`eval/run-report.json` 里每条 case 都带 `id` / `axis` / `detail`，
把 `detail` 与 `cases.jsonl` 的 `verify` 代码一起看，就能从源码复现该数字；
`--save` 重跑一次即可重建整份报告，不需要手工抄数。

**失败归因**：`run_cases.py` 不只报通过率，失败时按 `axis` 汇总（例如
`stats/mcnemar: 1 条 —— MC-01`），直接指出是哪个模块的哪个口径坏了。
