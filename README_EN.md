# Paper Writing Agent

[![CI](https://github.com/aidless/paper-writing-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/aidless/paper-writing-agent/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/CI_matrix-3.11%20%7C%203.12%20%7C%203.13-blue)
![License](https://img.shields.io/badge/license-Apache--2.0-green)
![Regression cases](https://img.shields.io/badge/regression_cases-27-blue)

<!-- problem-start -->
Deterministic gates that check a manuscript's numbers, citations, and TMLR submission hygiene against an evidence package.
This repository does not write a paper and does not accept one; a person drafts, and a venue decides.
Offline check: `make regression` (no LLM, no TeX). TeX compile gates run in the `tex-gates` CI job; a local SKIP is not a pass.
<!-- problem-end -->

**STATUS: WORK-IN-PROGRESS — not A yet.**

Gaps that keep this short of an A:

- no writing-quality evaluation in this tree: no blinded review, no model-judge study of drafts, and no venue acceptance record. An earlier overview quoted an AIRS-Bench mean score. This repository does not contain the manifest, log, or submission for that number, so the score is not stated here.
- Content scanners exit 0 on an empty draft. See [FAILURE_MODES.md](FAILURE_MODES.md).
- Citation `Manual_needed` still exits 0. The report says `MANUAL_REVIEW`, which is not a pass.
- `scripts/` has 51 Python files. Dirty-fixture regression covers 5 families and 27 cases. The other files are init, stats, retrieval, and CI helpers. They are not each a gate with a counterexample fixture.
- `make ci` needs scipy for C7 and a demo paper directory for C5. That path is separate from offline `make regression`.

The `regression_cases` shield is a static count locked by the drift tests. It is not a live pass signal. There is no PyPI package. The CI badge points at GitHub Actions, which is the live signal. This audit ran the offline regression on Python 3.12.3 and did not re-run 3.11 or 3.13. The workflow matrix declares all three.

<!-- inventory: scripts=51 regression_cases=27 fixture_cases=27 families=5 reference_docs=27 script_lines=10103 drift_tests=14 pytest_collected=0 -->

## Two check paths

| Command | Needs | What it shows |
|---|---|---|
| `make regression` | Python 3 standard library. No TeX, no LLM, no `requirements.txt` | Dirty fixtures must fire and clean fixtures must stay quiet. Without pdflatex, `compile-error` and `multiply-label` are SKIP |
| `make regression-tex` | pdflatex and bibtex | compile-gate family only, with `--fail-on-skip` |
| `make drift` | stdlib unittest | README counts, both hand-written script indexes, empty-draft exit codes, citation-gate degrade |
| `make ci` | `pip install -r requirements.txt` (includes scipy); C5 also needs a demo paper directory | `scripts/run_ci.py` checks C1–C13. Not the offline regression |

GitHub Actions splits the same way: `offline-regression` (no TeX, no scientific stack), `tex-gates` (TeX only, `--fail-on-skip`), and `verify` (full requirements, TeX, and `run_ci.py`).

## Counts locked to the tree

- 51 files in `scripts/*.py`. The generated [SCRIPTS.md](SCRIPTS.md) must name each of them. `scripts/SCRIPTS.md` and `scripts/SCRIPTS_EN.md` must name each of them too.
- 27 fixture directories directly under the five families in `assets/scanner_fixtures/`, each registered in `scanner_regression.FAMILIES`. `figure-claims/clean/clean/` is a nested copy inside the clean fixture, not case 28.
- 27 markdown files in `references/`, including English twins. That is not 27 independent methods.
- Older wording that counted 49 gates and 29 dirty fixtures, and that printed the regression as a frozen pass fraction, does not match the tree. The inventory comment and the `make regression` summary are the counts to trust.

`make drift` is `python3 -m unittest tests.test_inventory_drift`. pytest is not a dependency (`pytest_collected=0`).

## Citation verifier path

`gate_citations.py` resolves `verify_citations.py` in this order:

1. `CITATION_VERIFIER_PATH`
2. `PWA_RESEARCH_KIT` only when that variable is set (no default under the home directory)
3. `tools/citation-verifier/verify_citations.py` inside this repo

If none of those files exist, the process exits 2 and says this is not a PASS and not `Manual_needed`. The tool is not vendored here.

## Docs

- [SKILL.md](SKILL.md) — orchestration prompt for a writing agent. The prompt may ask a model to draft. The scripts do not draft.
- [FAILURE_MODES.md](FAILURE_MODES.md) — empty-draft passes, `Manual_needed`, TeX gates skipped locally
- [README.md](README.md) — Chinese overview
- [references/failure-modes.md](references/failure-modes.md) — manuscript-revision lessons. That library is not this file.

## License

Apache-2.0. `templates/tmlr/` keeps the JmlrOrg template's Apache-2.0 license.
