# SCRIPTS.md — 脚本全索引（自动生成）

> 由 `scripts/` 下各文件的 docstring 首行自动生成。用法细节以 `python scripts/<name>.py --help` 为准。

| 脚本 | 用途 |
|---|---|
| `build_evidence_manifest.py` | paper-writing-agent: build or verify an evidence manifest with SHA-256. |
| `chat_pdf.py` | chat_pdf.py - lightweight Chat-with-PDF (SciSpace-style, offline). |
| `check_judge_calibration.py` | paper-writing-agent: judge-calibration gate (L1-4). |
| `check_literature_freshness.py` | check_literature_freshness.py — 相关文献增量门（审计项 L2-3）。 |
| `check_submission_package.py` | paper-writing-agent: submission package checker (N4). |
| `check_submit_ready.py` | check_submit_ready.py - 投稿阻断门（评估要求：发布阻断而非页眉）。 |
| `check_tmlr_compliance.py` | paper-writing-agent: TMLR submission compliance scanner. |
| `check_writing_style.py` | paper-writing-agent: writing-style static checker (heuristic). |
| `citation_network.py` | citation_network.py - citation network analysis (Scite-style). |
| `compile_gate.py` | compile_gate.py — LaTeX 编译门(gap-review R2 新增): 编译 + 引用键核对。 |
| `consensus_check.py` | consensus_check.py - evidence synthesis adjudicator (Consensus-style). |
| `draft_rebuttal.py` | paper-writing-agent: rebuttal draft generator (N5). |
| `gate_citations.py` | gate_citations.py — Phase 5 引用验证门禁 (L2-2) |
| `gate_reflection.py` | gate_reflection.py — Reflexion 式反思注入(科研论文 agent Phase 4 改造)。 |
| `gen_review_cards.py` | gen_review_cards.py - generate deepseek-eyes review cards for all PDF pages |
| `independent_recompute.py` | independent_recompute.py - 独立重算入口（评估第 4 步）。 |
| `init_paper.py` | paper-writing-agent: one-command paper directory initializer. |
| `literature_discovery.py` | literature_discovery.py - arXiv semantic discovery (Elicit-style). |
| `log_writing_session.py` | log_writing_session.py — 写作溯源日志(append-only JSONL, L2-6 provenance) |
| `make_camera_ready.py` | paper-writing-agent: camera-ready converter (N6). |
| `make_run_record.py` | make_run_record.py - 不可变运行记录（评估 P0 整改）。 |
| `polish_manuscript.py` | polish_manuscript.py - manuscript polishing suggestions (Paperpal-style). |
| `power_analysis.py` | paper-writing-agent: statistical power / sample-size analysis (G1). |
| `prepare_submission.py` | paper-writing-agent: submission package preparer (N1). |
| `rebuttal_sim.py` | rebuttal_sim.py — rebuttal 模拟门禁(τ-bench 两阶段,E060 落地,I3)。 |
| `refine_verify.py` | refine_verify.py - Phase 2: verify best train-time configs with multiple seeds. |
| `release.py` | release.py - 单一发布入口（审查要求：发布门不可被跳过）。 |
| `retrieve_experience.py` | retrieve_experience.py — 论文 agent 三因子经验检索(recency × importance × relevance) + α  |
| `run_acceptance_gates.py` | paper-writing-agent: reusable acceptance-gate runner. |
| `run_ci.py` | paper-writing-agent: local CI runner (D3). |
| `run_experiment_plan.py` | paper-writing-agent: experiment-plan orchestrator (N2). |
| `scan_answer_fabrication.py` | scan_answer_fabrication.py — 答案拟合扫描器 (L047 工具化, 论文 agent 管线集成). |
| `scan_figure_claims.py` |  |
| `scan_hallucination.py` |  |
| `scan_number_consistency.py` | paper-writing-agent: number-consistency scanner. |
| `scan_stats_consistency.py` | paper-writing-agent: statistical-consistency scanner. |
| `scanner_regression.py` | scanner_regression.py — 失败类反例回归(Voyager 自动课程式落地)。 |
| `seal_run.py` | seal_run.py - 原子封存实验 run（评估不变量 2）。 |
| `stats.py` | 统计协议(实验方案文档 §2-§4):exact McNemar / Wilcoxon / Friedman+Nemenyi / CLES。 |
| `suggest_experiments.py` | paper-writing-agent: experiment-suggestion generator (G4). |
| `sweep_coefficients.py` | sweep_coefficients.py - Phase 1 coefficient sweep (R52 plan). |
| `switch_project.py` | paper-writing-agent: project switcher (N3). |
| `test_evidence_protection.py` | test_evidence_protection.py - 证据保护负向测试（评估不变量 1-4）。 |
| `test_pyramid.py` | test_pyramid.py v2 - 三级测试金字塔（覆盖所有科学分支 + 故障注入）。 |
| `validate_judge_output.py` | paper-writing-agent: judge-output schema validator + tolerant parser (G6). |
| `verify_claim_ledger.py` | paper-writing-agent: claim-ledger verifier. |
| `verify_labels.py` | verify_labels.py — 标签判定器验证门(G006, pilot-derived)。 |
| `verify_taint.py` |  |
| `verify_tree_diff.py` | verify_tree_diff.py - 受保护树差分（评估不变量 1+3）。 |
