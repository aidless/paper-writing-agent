# paper-writing-agent

[![CI](https://github.com/aidless/paper-writing-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/aidless/paper-writing-agent/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)
![License](https://img.shields.io/badge/license-Apache--2.0-green)
![Tests](https://img.shields.io/badge/scanner_regression-27%2F27%20PASS-brightgreen)

**证据优先的论文写作 Agent Skill**（TMLR 投稿向）：编排提示词（`SKILL.md`）+ 49 个可运行的确定性校验门（`scripts/`，约 9.8K 行）+ 27 篇方法论文档（`references/`）+ TMLR 官方 LaTeX 模板（`templates/tmlr/`）。

核心设计：**每个校验门都配 dirty fixture 反证**（`assets/scanner_fixtures/` 27 个，`scanner_regression.py` 27/27 PASS——门必须能失败，才配得上"门"这个字），统计量由 stdlib 独立重算（不信任上游数字）。

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
- [SCRIPTS.md](SCRIPTS.md) — 49 个脚本全索引（docstring 自动生成）
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
