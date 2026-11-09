# paper-writing-agent

[![CI](https://github.com/aidless/paper-writing-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/aidless/paper-writing-agent/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/CI_matrix-3.11%20%7C%203.12%20%7C%203.13-blue)
![License](https://img.shields.io/badge/license-Apache--2.0-green)
![Regression cases](https://img.shields.io/badge/regression_cases-27-blue)

<!-- problem-start -->
确定性门禁，用来核对稿件里的数字、引文和 TMLR 投稿卫生是否对得上证据包。
本仓库不写论文，也不接收论文；起草的是人，录用的是会议或期刊。
离线自检是 `make regression`（不需要 LLM，也不需要 TeX）。TeX 编译门在 CI 的 `tex-gates` 作业里跑；本地 SKIP 不是通过。
<!-- problem-end -->

**STATUS: WORK-IN-PROGRESS — not A yet.**

还缺的部分（所以现在不是 A）：

- no writing-quality evaluation：仓库里没有写作质量评估（没有盲审、没有模型当裁判的草稿评分、没有可核对的录用记录）。以前英文简介里的 AIRS-Bench 分数没有随仓库提供 manifest、日志或提交物，已从简介里撤下，不当作结果。
- 内容扫描器对空稿 exit 0。见 [FAILURE_MODES.md](FAILURE_MODES.md)。
- 引用门的 `Manual_needed` 退出码仍是 0（报告写 `MANUAL_REVIEW`，不是通过）。
- `scripts/` 有 51 个 Python 文件。带 dirty fixture 的回归是 5 族、27 例。其余是初始化、统计、检索和 CI 辅助，不是“每个都有反证夹具的门”。
- `make ci` 里的 C7 需要 scipy，C5 需要一份 demo 论文目录。那条路径和离线 `make regression` 不是同一件事。

`regression_cases` 徽章是静态计数，由 drift 测试锁住，不表示 CI 此刻是绿的。没有 PyPI 包。上面的 CI 徽章指向 GitHub Actions，那才是实时结果。本审计在 Python 3.12.3 上跑过离线回归，没有在这里重跑 3.11 和 3.13。CI 矩阵声明了这三个版本。

<!-- inventory: scripts=51 regression_cases=27 fixture_cases=27 families=5 reference_docs=27 script_lines=10103 drift_tests=14 pytest_collected=0 -->

## 两条检查路径

| 命令 | 需要什么 | 证明什么 |
|---|---|---|
| `make regression` | Python 3 标准库。不装 TeX，不调 LLM，不装 `requirements.txt` | 27 个夹具里，静态门必须打中 dirty、放过 clean。没有 pdflatex 时，`compile-error` 和 `multiply-label` 记 SKIP |
| `make regression-tex` | pdflatex 和 bibtex | 只跑 compile-gate，并且 `--fail-on-skip` |
| `make drift` | 标准库 unittest | README 计数、两份手写脚本索引、空稿退出码、引用门降级 |
| `make ci` | `pip install -r requirements.txt`（含 scipy）；C5 还要 demo 目录 | `scripts/run_ci.py` 的 C1–C13。这不是离线回归 |

GitHub Actions 拆成三块：`offline-regression`（不装 TeX、不装科学计算依赖）、`tex-gates`（只装 TeX，`--fail-on-skip`）、`verify`（完整依赖 + TeX + `run_ci.py`）。

## 计数（与树一致，由 drift 测试锁定）

- `scripts/*.py`：51。根目录 [SCRIPTS.md](SCRIPTS.md) 由 `scripts/gen_scripts_index.py` 生成，必须与这 51 个文件逐名一致。`scripts/SCRIPTS.md` 和 `scripts/SCRIPTS_EN.md` 是人手索引，也必须点名每一个文件。
- `assets/scanner_fixtures/`：5 个族的直接子目录共 27 个，全部登记在 `scanner_regression.FAMILIES`。`figure-claims/clean/clean/` 是 clean 夹具内部的一份嵌套副本，不是第 28 例。
- `references/*.md`：27 个文件，含中英对照，不是 27 篇互相独立的方法。
- 旧简介里的门数、fixture 数，以及把回归写成一个固定的通过分数，都和当前树对不上。以本页 inventory 注释和 `make regression` 的输出为准。

## 引用门的路径

`gate_citations.py` 按这个顺序找 `verify_citations.py`：

1. 环境变量 `CITATION_VERIFIER_PATH`
2. 环境变量 `PWA_RESEARCH_KIT`（只有你设置了才用；不会默认去用户主目录）
3. 仓库内 `tools/citation-verifier/verify_citations.py`

三处都没有时退出码是 2，并写明这不是 PASS，也不是 `Manual_needed`。仓库里目前没有这个工具。

## 文档地图

- [SKILL.md](SKILL.md) — 给写作 agent 的编排提示。提示词可以要求模型起草；仓库里的脚本本身不起草。
- [SCRIPTS.md](SCRIPTS.md) — 51 个脚本的生成索引
- [FAILURE_MODES.md](FAILURE_MODES.md) — 空稿通过、Manual_needed、本地跳过 TeX 门
- [README_EN.md](README_EN.md) — 英文概览
- [references/](references/) — 方法论笔记（含 `failure-modes.md`，那是改稿教训库，和本页的 FAILURE_MODES 不是同一份清单）
- [templates/tmlr/](templates/tmlr/) — TMLR 官方 LaTeX 模板

## 编排一览（SKILL.md 的 Phase 结构）

`SKILL.md` 告诉使用它的模型按这些阶段组织工作。能在本仓库里离线跑完的是其中的确定性检查，不是整篇论文的生成或录用。

```
Phase 0   Intake                证据包验收：manifest 哈希对账、数据-声明可溯源
Phase 1   Claim ledger          每个数字/主张先入 ledger（file+field 级溯源）
Phase 2   Draft                 模板起稿由使用技能的模型完成，不由这些脚本完成
Phase 3   Machine checks        数字 / 统计 / 引文 / 合规 / 编译（编译依赖 TeX）
Phase 4   Revision loop         修订轮：修复后重扫
Phase 4.5 Adversarial review    对抗审稿协议（模型角色，不是本仓库的自动录用）
Phase 5   Submission compliance 匿名化与打包检查；上传仍然是人工操作
```

## License

Apache-2.0（`templates/tmlr/` 沿用 JmlrOrg 官方模板的 Apache-2.0 许可）
