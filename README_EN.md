# Paper Writing Agent (English overview)

An **evidence-first scientific paper writing and TMLR-submission agent**:
turn delivered evidence into a manuscript that clears the
*Transactions on Machine Learning Research* (TMLR) bar. Every number must be
independently recomputable from the evidence package; no claim enters the text
without a ledger entry backed by a file+field.

## Quick start

```bash
# 1. Bootstrap a paper project (anonymous TMLR template + claim ledger +
#    protocol with failure-mode lessons baked in + gates config)
python scripts/init_paper.py <paper_dir> --title "Your Title" --round-report

# 2. Inventory evidence and hash it (SHA-256)
python scripts/build_evidence_manifest.py <paper_dir> --out evidence_manifest.json

# 3. Register claims BEFORE drafting
#    edit <paper_dir>/CLAIM_LEDGER.md  (states: draft/verified/inconclusive/blocked)

# 4. Draft (Methods+Results from computed values; Abstract last)

# 5. Machine checks (12 scanners)
python scripts/scan_number_consistency.py <paper_dir> --fail-on-stale
python scripts/scan_stats_consistency.py  <paper_dir> --fail-on-error
python scripts/scan_hallucination.py      <paper_dir> --fail-on-error   # MLR-Bench 4-type hallucination
python scripts/verify_claim_ledger.py     <paper_dir>
python scripts/verify_taint.py            <paper_dir> --fail-on-error
python scripts/compile_gate.py            <paper_dir>
python scripts/check_tmlr_compliance.py   <paper_dir> --names "author1,author2"

# 6. Adversarial review (8 roles) until one round with no new Critical/Major
# 7. Submission package + checks (upload stays manual — protected layer)
python scripts/prepare_submission.py       <paper_dir>
python scripts/check_submission_package.py <paper_dir> --fail-on-error
```

## Architecture

```
Phase 0  Intake          — experience retrieval (3-factor), project switch, literature review
Phase 1  Claim ledger    — every claim → evidence file+field; inconclusive outlet for weak claims
Phase 2  Draft           — power analysis before any N; writing provenance per section
Phase 3  Machine checks  — 12 scanners (numbers/stats/hallucination/figures/taint/compile/
                           style/TMLR/ledger/labels/freshness/citations)
Phase 4  Revision loop   — ROUND_Rn + acceptance gates stay green
Phase 4.5 Adversarial review — 8 roles (methodology/statistics/experiments/novelty/
                           reproducibility/writing/ethics/figures), dual-axis verification,
                           no-code ablation, rebuttal simulation, staged review for long papers
Phase 5  Submission      — TMLR G1-G11 compliance, citation gate, hash reconciliation,
                           submission package + mechanical checks (upload manual)
```

## Key scripts (48 total; ~34 copied into each paper project)

**Scanners / checks** — `scan_number_consistency` (stale markers, inverted CIs,
table-vs-prose), `scan_stats_consistency` (recomputes p vs t/z/chi2/F with
stdlib CDFs, effect-size ranges, n conflicts, MCP risk), `scan_hallucination`
(MLR-Bench four types: nonexistent citations / hallucinated methodology /
mathematical errors / faked results), `scan_figure_claims`, `verify_taint`
(evidence pollution state machine), `compile_gate` (pdflatex + log scan),
`check_tmlr_compliance` (G1/G3/G4/G6/G7 + dataset-license & compute
declarations), `verify_claim_ledger` (file/field/value traceability;
inconclusive = WARN), `verify_labels` (label-matcher validation gate),
`check_literature_freshness` (+novelty-drift detection), `gate_citations`
(4-layer arXiv verification).

**Stats / analysis** — `stats.py` (exact McNemar, Wilcoxon+CLES,
Friedman+Nemenyi with CD plot, bootstrap CI, Breslow-Day heterogeneity,
forest plot), `power_analysis.py` (paired/two-sample t, exact McNemar,
proportion, correlation; solve n / power / min-detectable effect; validated
against Cohen 1988), `independent_recompute.py`.

**Generation / build** — `init_paper.py` (one-command bootstrap),
`prepare_submission.py` (zip + OpenReview checklist + G3 anonym re-scan),
`check_submission_package.py` (C1-C7), `draft_rebuttal.py` (per-comment
skeleton), `make_camera_ready.py` ([accepted] + author block), `release.py`,
`seal_run.py`.

**Execution / orchestration** — `run_experiment_plan.py` (declarative plan →
resource pre-check → scheduling → artifact verification → resume),
`switch_project.py` (multi-project isolation), `suggest_experiments.py`
(review/ledger gaps → experiment-completion plans), `run_ci.py` (10-check
local CI), `scanner_regression.py` (25 fixtures / 12 families),
`validate_judge_output.py` (judge JSON schema + tolerant parsing),
`retrieve_experience.py` (3-factor lesson retrieval).

## Statistical correctness (independently verified)

- Wilcoxon / exact McNemar: bit-identical to `scipy` (incl. zero-drop path)
- Power analysis: matches Cohen 1988 tables (paired n=34 @ d=0.5/p=0.8;
  two-sample power 0.478 @ n=30/d=0.5; r_min 0.431 @ n=40)
- Bootstrap CI: deterministic under `seed=300`
- Everything recomputable from raw per-seed data (`independent_recompute.py`)

## External benchmark: AIRS-Bench evaluation (E139-E144)

The agent was evaluated on **AIRS-Bench** (Meta; 20 ML research tasks, pure
metric scoring vs SOTA, no LLM judge):

- Pipeline: task description + data samples → LLM writes predictor code →
  local execution → official `evaluate.py` scoring
- **12/13 tasks scored, mean normalized score (NS) = 0.3785**
  (official leaderboard reference: gpt-oss-120b Greedy NS≈0.40 — single-shot
  deepseek-v4-flash, no retries/multi-candidate)
- All scores independently recomputable (submission.csv + evaluate.py,
  SHA-256 manifest); failures honestly classified (env-dependency vs agent)
- Tools: external `airs-eval` toolkit (6 scripts; path configurable, not bundled)

## Documentation languages

Core docs are Chinese-first; this README and the CI guide are English.
See `SCRIPTS.md` for the full script index (Chinese) and `references/`
for methodology docs (Chinese).

## License & attribution

The skill bundles the official TMLR style (`templates/tmlr/`, from the
JmlrOrg/tmlr-style-file repo). AIRS-Bench evaluation data is CC BY-NC 4.0
(non-commercial).
