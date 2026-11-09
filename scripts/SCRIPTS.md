# Scripts 索引(可检索化,D3)

> 每个脚本一行定位 + 触发条件 + 用法。agent 写作/审稿/自查时按需检索本表,
> 不凭记忆调用。格式: `名称 — 一句话 | 触发 | 用法`。

## 机器检查(Phase 3,名字引用: number-scan/stats-scan/style-scan/tmlr-scan/ledger-scan/taint-scan/compile-gate;全部 exit 0 = 通过)

- `scan_number_consistency.py` — 数字一致性扫描(过期标记/反转 CI/证据值未用) | 每次修改后/审稿前 | `python scripts/scan_number_consistency.py <dir> --fail-on-stale --out reports/numbers.md`
- `scan_stats_consistency.py` — 统计一致性扫描(p↔t/z/χ²/F 重算核验/效应量越界/n 冲突/符号不一致/p=0.000/多重比较风险) | Phase 3 | `python scripts/scan_stats_consistency.py <dir> --fail-on-error --out reports/stats.md`
- `check_writing_style.py` — 写作风格扫描(强声明/Chinglish/CI 跨零) | Phase 3 | `python scripts/check_writing_style.py <dir> --out reports/style.md`
- `check_tmlr_compliance.py` — TMLR 合规扫描(G1/G3/G4/G6/占位/zip) | Phase 3/5 | `python scripts/check_tmlr_compliance.py <dir> --names "a,b" --out reports/tmlr.md`
- `verify_claim_ledger.py` — claim 账本校验(字段存在/数值匹配) | Phase 1/4 | `python scripts/verify_claim_ledger.py <dir> --out reports/ledger.md`
- `verify_taint.py` — 证据污染传播检查(引用 broken/tainted 证据的声称自动 blocked / 缺失证据) | Phase 1/3 | `python scripts/verify_taint.py <dir> --fail-on-error --out reports/taint.md`
- `compile_gate.py` — LaTeX 编译门(pdflatex -draftmode+bibtex 临时目录编译 + 日志扫描: 编译错误/undefined ref/cite/重复 label/overfull; 静态 cite↔bib、ref↔label 键核对为无 TeX 兜底层, 降级记 "## Compile skipped: 1"; orphan label/未引用 bib 条目为警告, --fail-on-warning 提升) | Phase 3/每次改 .tex/.bib 后 | `python scripts/compile_gate.py <dir> --out reports/compile.md`

## 门禁与反思(Phase 4)

- `run_acceptance_gates.py` — 配置驱动验收门,exit 0=全 PASS;`--report` 落报告、`--record` 记历史;每门可标 `"expected_fail": true, "expected_reason": "..."`(设计性阻断 → 打印 FAIL(expected), 不影响退出码, gate_reflection 忽略) | 每轮结束 | `python scripts/run_acceptance_gates.py gates_config.json --report reports/gates.json --record gates_history.jsonl`
- `gate_reflection.py` — 检测连续 FAIL 门禁并生成反思块(Reflexion;expected_fail 门不计入且重置连击) | 门禁历史≥2 条时 | `python scripts/gate_reflection.py --history gates_history.jsonl --out ROUND_Rn_reflection.md`
- `scanner_regression.py` — 失败类夹具回归(脏夹具必须命中、clean 不得误报;族和例数以 `FAMILIES` 为准,当前 5 族。`skip_when` 环境降级打印 SKIP,摘要里不计入 PASS;`--fail-on-skip` 把 SKIP 当成失败) | 新增失败模式后 | `python scripts/scanner_regression.py`
- `check_judge_calibration.py` — judge 校准门(FNR/FPR 阈值,ARS 标准;未校准禁止计入终评) | Phase 4.5 O2 打分前 | `python scripts/check_judge_calibration.py <calibration.json> --fail-on-uncalibrated --out reports/calibration.md`

## 证据与可复现(Phase 0/1/5)

- `build_evidence_manifest.py` — evidence manifest 构建/校验(SHA-256,`--verify` 字节对账) | 修改交付文件后立即 | `python scripts/build_evidence_manifest.py <dir> --verify evidence_manifest.json`
- `init_paper.py` — 一键建论文项目(骨架+TMLR 模板+账本+门禁) | 新项目 | `python scripts/init_paper.py <dir> --title "..." --round-report`
- `seal_run.py` — 原子封存实验 run(不可覆盖) | 证据转 verified 前 | `python scripts/seal_run.py <run>`
- `verify_tree_diff.py` — 保护树快照/diff(验证器不得改写证据) | 证据只读校验 | `python scripts/verify_tree_diff.py`
- `make_run_record.py` — 生成 run record | 实验完成 | `python scripts/make_run_record.py`
- `test_evidence_protection.py` — 负注入测试(生成器/验证器不得写 canonical evidence) | 改动证据链后 | `python scripts/test_evidence_protection.py`

## 文献与检索(Phase 0/D0)

- `literature_discovery.py` — arXiv 语义发现(query→dedupe→排序→表) | D0 文献综述 | `python scripts/literature_discovery.py --query "..." `
- `check_literature_freshness.py` — 文献新鲜度门(L2-3: LITERATURE_REVIEW.md 缺失/过期 + novelty 声称覆盖数) | 投稿前 Phase 5 | `python scripts/check_literature_freshness.py <dir> --claims-file claims.txt --max-age-days 30 --out reports/literature_freshness.md --fail-on-stale`
- `citation_network.py` — 引文关系筛查(supportive/contradictory/neutral) | 引文核验 | `python scripts/citation_network.py`
- `consensus_check.py` — 证据合成裁决(YES/NO/MIXED + 强度) | 多证据综合 | `python scripts/consensus_check.py`
- `chat_pdf.py` — 轻量 Chat-with-PDF | 读 PDF 证据 | `python scripts/chat_pdf.py <pdf>`

## 审稿与写作(Phase 2/4.5)

- `polish_manuscript.py` — 润色建议(不重写) | 初稿后 | `python scripts/polish_manuscript.py <dir>`
- `gen_review_cards.py` — 生成 deepseek-eyes 图表审阅卡(喂 R8) | 审稿前 | `python scripts/gen_review_cards.py <pdf> --page N --out card.md`
- `scan_figure_claims.py` — 图-文双向校验扫描(未定义 fig label 引用/缺失图片文件/孤儿图/数字式提及计数) | Phase 4.5 R8 前 | `python scripts/scan_figure_claims.py <dir> --fail-on-error --out reports/figures.md`
- `log_writing_session.py` — 写作溯源日志(append-only JSONL: 文件/章节/模型/prompt hash/证据 hash) | Phase 2 每次写作/Phase 4 每次修订 | `python scripts/log_writing_session.py --log writing_session.jsonl --file <tex> --section <名> --model <名> --prompt-hash <h> --evidence-hash <h>`

## 交付(Phase 5)

- `check_submit_ready.py` — 投稿就绪检查 | Phase 5 前 | `python scripts/check_submit_ready.py <dir>`
- `gate_citations.py` — 引用验证门禁(外部 verify_citations.py;路径只认 CITATION_VERIFIER_PATH、已设置的 PWA_RESEARCH_KIT、仓库内 tools/citation-verifier/。缺失 exit 2,不是 Manual_needed。Manual_needed 的结论是 MANUAL_REVIEW,退出码仍为 0。断网为 DEGRADED) | Phase 5 终稿前 | `python scripts/gate_citations.py <dir> --fail-on-suspicious --out reports/citations_gate.md`
- `release.py` — 发布打包 | 交付 | `python scripts/release.py`

## 测试

- `test_pyramid.py` — 技能测试金字塔 | 改动脚本后 | `python scripts/test_pyramid.py`
- `test_evidence_protection.py` — 见证据节(兼作测试)

> 维护规则: 新增脚本必须在本表登记(名称/触发/用法一行),否则视为未发布;
> 删除/改名脚本同步更新本表与 SKILL.md Resources。
> `tests/test_inventory_drift.py` 会断言 `scripts/*.py` 的每个文件名都出现在本表。

## 索引补齐（与 scripts/*.py 对齐）

上面各节没点到的文件。一行一个名字,用途取自各文件 docstring 首行。

- `scan_hallucination.py` — hallucination scanner (MLR-Bench 四类) | Phase 3 | `python scripts/scan_hallucination.py <dir> --fail-on-error`
- `scan_answer_fabrication.py` — 答案拟合扫描器 | 改 scripts/ 后 / CI C11 | `python scripts/scan_answer_fabrication.py <dir>`
- `verify_labels.py` — 标签判定器验证门 | 使用标签匹配器之前 | `python scripts/verify_labels.py <data.jsonl>`
- `fm_index.py` — 生成并核对 failure-modes 的 INDEX | 改 FM 库后 | `python scripts/fm_index.py --check`
- `gen_scripts_index.py` — 从 docstring 重建根目录 SCRIPTS.md | 增删脚本后 | `python scripts/gen_scripts_index.py --check`
- `run_ci.py` — 本地 CI（C1–C13；C5 要 demo 目录，C7 要 scipy） | 改动工具链后 | `python scripts/run_ci.py`
- `run_experiment_plan.py` — 实验计划编排 | 跑实验计划 | `python scripts/run_experiment_plan.py <plan.json> --dry-run`
- `suggest_experiments.py` — 由审稿缺口生成实验建议 | 对抗审稿之后 | `python scripts/suggest_experiments.py --review <review.md>`
- `sweep_coefficients.py` — 系数扫描 | 实验分析 | `python scripts/sweep_coefficients.py --help`
- `switch_project.py` — 多项目切换 | 并行多个论文目录 | `python scripts/switch_project.py list`
- `validate_judge_output.py` — judge 输出 schema 校验 | 任何 judge 调用之后 | `python scripts/validate_judge_output.py --schema score --input <f>`
- `independent_recompute.py` — 从原始数据独立重算 | Phase 3 | `python scripts/independent_recompute.py <paper_dir>`
- `make_camera_ready.py` — camera-ready 转换 | 录用之后（录用决定不由本仓库做出） | `python scripts/make_camera_ready.py <paper_dir>`
- `power_analysis.py` — 功效 / 样本量 | 写 Methods 里的 N 之前 | `python scripts/power_analysis.py --selftest`
- `prepare_submission.py` — 打包投稿材料（上传仍是人工） | Phase 5 | `python scripts/prepare_submission.py <paper_dir>`
- `rebuttal_sim.py` — rebuttal 模拟 | Phase 5 前 | `python scripts/rebuttal_sim.py --help`
- `refine_verify.py` — 多种子复核训练配置 | 实验分析 | `python scripts/refine_verify.py --help`
- `retrieve_experience.py` — 三因子经验检索 | 会话开始 | `python scripts/retrieve_experience.py --task "<goal>"`
- `draft_rebuttal.py` — 从审稿摘要起 rebuttal 骨架 | 收到审稿后 | `python scripts/draft_rebuttal.py --help`
- `check_submission_package.py` — 投稿包检查 | 上传前 | `python scripts/check_submission_package.py <paper_dir> --fail-on-error`
- `stats.py` — exact McNemar / Wilcoxon / Friedman+Nemenyi / CLES | 被其他脚本 import | `python scripts/stats.py --help`
