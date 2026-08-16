# Scripts index (English)

> One line per script: purpose | trigger | usage. The full Chinese index with
> additional detail is `SCRIPTS.md`; this English mirror serves international
> readers and the TMLR review context.

## Machine checks (Phase 3)

- `scan_number_consistency.py` — number-consistency scan (stale markers /
  inverted CIs / evidence values never used / table-vs-prose mismatches) |
  after every revision, before review | `python scripts/scan_number_consistency.py <dir> --fail-on-stale --out reports/numbers.md`
- `scan_stats_consistency.py` — statistical-consistency scan (recomputes p
  from t/z/chi2/F via stdlib CDFs; effect-size ranges; n conflicts; sign
  mismatches; p=0.000; multiple-comparison risk) | Phase 3 |
  `python scripts/scan_stats_consistency.py <dir> --fail-on-error --out reports/stats.md`
- `scan_hallucination.py` — hallucination scan (MLR-Bench 4 types:
  nonexistent citations / hallucinated methodology / math errors / faked
  results) | Phase 3 | `python scripts/scan_hallucination.py <dir> --fail-on-error --out reports/hallucination.md`
- `scan_figure_claims.py` — figure-claim scan (undefined fig refs / missing
  includegraphics / orphan figures) | before R8 figures role |
  `python scripts/scan_figure_claims.py <dir> --fail-on-error --out reports/figures.md`
- `check_writing_style.py` — writing-style scan (strong claims / Chinglish /
  CI crossing zero) | Phase 3 | `python scripts/check_writing_style.py <dir> --out reports/style.md`
- `check_tmlr_compliance.py` — TMLR compliance scan (G1/G3/G4/G6/G7 +
  dataset-license & compute declarations) | Phase 3/5 |
  `python scripts/check_tmlr_compliance.py <dir> --names "a,b" --out reports/tmlr.md`
- `verify_claim_ledger.py` — claim-ledger verifier (file/field/value
  traceability; inconclusive = WARN with named missing evidence) |
  Phase 1/4 | `python scripts/verify_claim_ledger.py <dir> --out reports/ledger.md`
- `verify_taint.py` — evidence-taint verifier (claims referencing
  broken/tainted/missing evidence are blocked) | Phase 1/3 |
  `python scripts/verify_taint.py <dir> --fail-on-error --out reports/taint.md`
- `verify_labels.py` — label-matcher validation gate (exact vs tolerant
  flip-set; >5% unadjudicated → exit 2 BLOCKED) | before matcher-based claims |
  `python scripts/verify_labels.py <data.jsonl> --adjudicate`
- `compile_gate.py` — LaTeX compile gate (pdflatex -draftmode + bibtex in a
  temp copy; log scan for errors/undefined refs/cites/multiply labels/overfull;
  static key check as TeX-free fallback) | Phase 3 / after every .tex/.bib edit |
  `python scripts/compile_gate.py <dir> --out reports/compile.md`
- `check_literature_freshness.py` — literature-freshness gate (max-age;
  `--check-drift` flags novelty claims stale vs review coverage) | Phase 5 |
  `python scripts/check_literature_freshness.py <dir> --claims-file novelty_claims.txt --check-drift --fail-on-stale`
- `gate_citations.py` — citation-verification gate (4-layer arXiv check;
  network outage degrades to documented pass) | Phase 5 |
  `python scripts/gate_citations.py <dir> --fail-on-suspicious --out reports/citations_gate.md`

## Gates & reflection (Phase 4)

- `run_acceptance_gates.py` — config-driven acceptance gates (exit 0 = all
  PASS; `expected_fail` supported) | end of every round |
  `python scripts/run_acceptance_gates.py gates_config.json --report reports/gates.json --record gates_history.jsonl`
- `gate_reflection.py` — detects consecutive gate FAILs and generates a
  reflection block (Reflexion) | when gate history >= N entries |
  `python scripts/gate_reflection.py --history gates_history.jsonl`
- `scanner_regression.py` — failure-class fixture regression (25 fixtures /
  12 families; `--fixture`/`--family` selectable; `skip_when` env degradation) |
  after adding a failure pattern | `python scripts/scanner_regression.py`
- `check_judge_calibration.py` — judge-calibration gate (FNR/FPR vs ARS
  thresholds; uncalibrated scores excluded from final assessment) | Phase 4.5 |
  `python scripts/check_judge_calibration.py <calibration.json> --fail-on-uncalibrated`

## Review & rebuttal (Phase 4.5)

- `rebuttal_sim.py` — rebuttal simulation against 3 reviewer types
  (evidence-doubt / overclaim / mechanism), two-phase; `--live` uses the real
  LLM base | before Phase 5 | `python scripts/rebuttal_sim.py --rebuttal REBUTTAL.md --evidence <dir>`
- `draft_rebuttal.py` — rebuttal draft skeleton from review summaries
  (table or `[severity]` formats) | when real reviews arrive |
  `python scripts/draft_rebuttal.py --review REVIEW_R1_summary.md --out REBUTTAL.md`
- `validate_judge_output.py` — judge-output schema validator + tolerant
  parser (review/rebuttal/score schemas; fence/trailing-comma/single-quote
  drift recovery; invalid = judge failure in denominator) | any judge call |
  `python scripts/validate_judge_output.py --schema review --input out.json`
- `gen_review_cards.py` — deepseek-eyes review cards for PDF table/figure
  pages (feeds the R8 figures reviewer) | before R8 |
  `python scripts/gen_review_cards.py <pdf> --page N --mode paper`

## Statistics & analysis

- `stats.py` — statistical library: exact McNemar, Wilcoxon+CLES,
  Friedman+Nemenyi with CD plot, bootstrap CI (seed=300), Breslow-Day
  heterogeneity, forest plot | import | `from stats import ...`
- `power_analysis.py` — power / sample-size analysis (paired & two-sample t,
  exact McNemar, proportion, correlation; solve n / power / min-detectable
  effect; validated vs Cohen 1988) | before writing any N in Methods |
  `python scripts/power_analysis.py --t-paired --solve n --d 0.5 --alpha 0.05 --power 0.80`
- `independent_recompute.py` — independent recompute from raw per-seed data
  (no analysis.py / ledger read) | Phase 3 |
  `python scripts/independent_recompute.py <paper_dir>`
- `sweep_coefficients.py` — coefficient sweep helper | experiment analysis

## Generation & build

- `init_paper.py` — one-command paper bootstrap (skeleton + anonymous TMLR
  template + ledger + protocol + gates + 34 scripts) | new paper |
  `python scripts/init_paper.py <paper_dir> --title "T" --round-report`
- `prepare_submission.py` — submission package (zip + OpenReview checklist +
  G3 anonym re-scan; upload stays manual) | Phase 5 |
  `python scripts/prepare_submission.py <paper_dir>`
- `check_submission_package.py` — package checks C1-C7 (zip size / pdf /
  anonymity / manifest / gates / ledger / no process docs) | before upload |
  `python scripts/check_submission_package.py <paper_dir> --fail-on-error`
- `make_camera_ready.py` — camera-ready conversion ([accepted] + author
  block; anonymous backup kept) | after acceptance |
  `python scripts/make_camera_ready.py <paper_dir> --authors authors.json`
- `build_evidence_manifest.py` — evidence manifest builder/verifier (SHA-256) |
  every change | `python scripts/build_evidence_manifest.py <dir> --verify evidence_manifest.json`
- `release.py` / `seal_run.py` — release packaging / atomic run sealing

## Execution & orchestration

- `run_experiment_plan.py` — experiment-plan orchestrator (declarative JSON:
  resource pre-check, scheduling, artifact verification, resume, failure
  classification) | running experiments |
  `python scripts/run_experiment_plan.py experiment_plan.json --dry-run`
- `switch_project.py` — multi-project switcher (list/switch/init; context
  digest per project) | multi-project work | `python scripts/switch_project.py <name>`
- `suggest_experiments.py` — experiment-suggestion generator (review
  Critical/Major + ledger inconclusive gaps → P0/P1 completion plans) |
  after adversarial review | `python scripts/suggest_experiments.py --review REVIEW_R1_summary.md`
- `run_ci.py` — local CI (10 checks: compile/help/selftest/regression/
  evidence-protection/power/stats-vs-scipy/judge-validator/plan/suggest) |
  any change | `python scripts/run_ci.py`
- `retrieve_experience.py` — 3-factor lesson retrieval (recency × importance
  × relevance; verified/active only) | session start |
  `python scripts/retrieve_experience.py --task "<goal>"`
- `log_writing_session.py` — writing-provenance logger (append-only JSONL) |
  after each section | `python scripts/log_writing_session.py --log writing_session.jsonl ...`
- `polish_manuscript.py` — polishing suggestions (never rewrites) |
  Phase 2 | `python scripts/polish_manuscript.py <paper_dir>`
- `chat_pdf.py` / `citation_network.py` / `consensus_check.py` /
  `literature_discovery.py` — PDF Q&A / citation-relation screening /
  evidence-synthesis adjudication / arXiv discovery
- `verify_tree_diff.py` / `test_evidence_protection.py` / `test_pyramid.py` —
  evidence-tree protection & integration tests (do not mutate evidence)
