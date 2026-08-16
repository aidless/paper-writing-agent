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
- `scanner_regression.py` — 失败类夹具回归(机器检查不漏检/不误报;四族 number-consistency + stats-consistency + figure-claims + compile-gate;`--fixture`/`--family` 可选;夹具 spec 支持 `skip_when` 环境降级) | 新增失败模式后 | `python scripts/scanner_regression.py`
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
- `gate_citations.py` — 引用验证门禁(调 research-kit verify_citations.py 4 层验证;断网/超时文档化降级 Skipped_network;无 bib 可用 --allow-missing-bib 放行) | Phase 5 终稿前 | `python scripts/gate_citations.py <dir> --fail-on-suspicious --out reports/citations_gate.md`
- `release.py` — 发布打包 | 交付 | `python scripts/release.py`

## 测试

- `test_pyramid.py` — 技能测试金字塔 | 改动脚本后 | `python scripts/test_pyramid.py`
- `test_evidence_protection.py` — 见证据节(兼作测试)

> 维护规则: 新增脚本必须在本表登记(名称/触发/用法一行),否则视为未发布;
> 删除/改名脚本同步更新本表与 SKILL.md Resources。
