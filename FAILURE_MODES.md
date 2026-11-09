# FAILURE_MODES

Measured limits of the scanners in this repository. Observed on Python 3.12.3 with no `pdflatex`, no `verify_citations.py`, and no LLM call.

This file is not an entry in `references/failure-modes.md`. That library only accepts a lesson that came from an actual manuscript revision. The items below are properties of the tools, checked by `tests/test_inventory_drift.py`.

## Scanners that exit 0 on an empty draft

An empty directory, and a directory whose only file is a blank `article` `main.tex`, were scanned from a path that does not contain an excluded directory name (`tmp`, `assets`, and the other names in each script's exclude list).

These commands exited 0 in both layouts, including with `--fail-on-stale` or `--fail-on-error` where that flag exists:

- `scan_number_consistency.py`
- `scan_stats_consistency.py`
- `scan_hallucination.py`
- `scan_figure_claims.py`
- `scan_answer_fabrication.py`
- `check_writing_style.py`

Exit 0 here means the scanner found nothing to report. An empty manuscript satisfies that condition. It does not mean the manuscript is ready to submit.

`check_tmlr_compliance.py` exits 0 when the directory has no `.tex` file (`G1` is INFO, `failures: 0`). The same command exits 1 once any `.tex` file exists without an active anonymous `\usepackage{tmlr}`.

Do not treat a probe whose path contains a directory named `tmp` as evidence for `check_tmlr_compliance.py`. Its exclude list matches that path component, so a draft under `/tmp` is reported as "no .tex files found" even when `main.tex` is there.

`verify_claim_ledger.py` and `verify_taint.py` exit 1 when `CLAIM_LEDGER.md` is missing. `check_literature_freshness.py --fail-on-stale` exits 1 when `LITERATURE_REVIEW.md` is missing.

## Manual_needed does not fail the citation gate

`gate_citations.py` copies `manual_needed` and `suspicious` into the `Manual_needed` section. `--fail-on-suspicious` changes the exit code only for `Not_found` and `Mismatch`.

When `Manual_needed` is greater than 0 and those two counts are 0, the report verdict is `MANUAL_REVIEW` and the exit code stays 0. The exit code is easy to miss in a script that only checks status. `MANUAL_REVIEW` is not a completed citation check.

A missing `verify_citations.py` is different: the process exits 2 and writes that this is not a PASS and not `Manual_needed`. See the path rules below.

If the network probe fails, or the verifier times out, the verdict is `DEGRADED` and the exit code is 0. That records a skipped re-check. It does not mean the citations were verified in this session.

A directory with no `.bib`, run without `--fail-on-suspicious`, exits 0 with verdict `MISSING_BIB` in report mode. With `--fail-on-suspicious` and no `--allow-missing-bib`, that case exits 1.

## TeX-only gates skipped locally

`compile_gate.py` without `pdflatex` and `bibtex` (or with `--no-tex`) runs the static key check only. The report contains `## Compile skipped: 1` and the verdict `STATIC_ONLY`. It does not say PASS. The exit code is still 0 when the static layer finds no errors, so a blank `main.tex` is `STATIC_ONLY` rather than a compile success.

Two regression fixtures declare `skip_when: compile_skipped`:

- `compile-gate/compile-error`
- `compile-gate/multiply-label`

`scanner_regression.py` prints those as `[SKIP]` and the summary is `N PASS, M SKIP, 0 FAIL (27 cases)`. SKIP is not added to PASS. Offline `make regression` exits 0 when the only non-passes are those skips. `make regression-tex` and the `tex-gates` CI job pass `--fail-on-skip`, so a missing TeX install cannot look like a green compile-gate run.

`compile-gate/undefined-citation` and `compile-gate/undefined-ref` are static checks. They run without TeX.

## Absolute paths

`gate_citations.resolve_default_verifier()` does not read the home directory. Order:

1. `CITATION_VERIFIER_PATH` if set
2. `PWA_RESEARCH_KIT` if that variable is set
3. `tools/citation-verifier/verify_citations.py` relative to the repository root

If the chosen path is not a file, the gate exits 2. There is no silent fallback to `~/research-kit`.
