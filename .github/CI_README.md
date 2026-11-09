# CI layout

`.github/workflows/ci.yml` runs on every push to `main` and on every pull request.
The workflow file declares Python 3.11, 3.12, and 3.13 for the full `verify` job.
The offline and TeX jobs pin 3.12. A badge that lists those versions describes the
matrix. It is not a claim that this checkout was executed on all three.

## Jobs

| Job | Installs | What it runs |
|---|---|---|
| `offline-regression` | Python only. No TeX, no `requirements.txt`, no LLM | `scripts/scanner_regression.py` and `python -m unittest tests.test_inventory_drift`. Compile fixtures that need pdflatex print SKIP. SKIP is not a PASS. |
| `tex-gates` | TeX (`pdflatex` + `bibtex`) only | `scanner_regression.py --family compile-gate --fail-on-skip` |
| `verify` | `requirements.txt` (includes scipy) and TeX, on 3.11 / 3.12 / 3.13 | `run_ci.py` subset plus a full regression with `--fail-on-skip` |
| `secret-scan` | gitleaks | full-history secret scan |

`verify` is the heavy path. It is not the fresh-clone offline regression.

## What `run_ci.py` checks

| Check | What it verifies |
|---|---|
| C1 | all scripts compile (`py_compile`) |
| C2 | every CLI script's `--help` works |
| C3 | all declared `--selftest`s pass |
| C4 | scanner regression; the summary line separates PASS, SKIP, and FAIL |
| C5 | evidence protection; needs a demo paper directory, so the workflow does not run it unless that directory exists |
| C6 | power analysis matches the Cohen 1988 check inside `power_analysis.py --selftest` |
| C7 | stats library cross-check vs scipy (needs scipy) |
| C8 | judge-output validator |
| C9 | experiment-plan dry-run |
| C10 | experiment-suggestion mapping |
| C11 | answer-fabrication scan of `scripts/` |
| C12 | failure-mode index sync (`fm_index.py --check`) |
| C13 | root `SCRIPTS.md` matches `scripts/*.py` |

## Local equivalents

```bash
make regression       # offline, no TeX, no LLM
make regression-tex   # needs pdflatex; fails if those fixtures SKIP
make drift            # unittest inventory lock; pytest is not required
make ci               # run_ci.py; install requirements.txt first for C7
```

Network-dependent citation checks are not in CI. A missing `verify_citations.py`
exits 2. That is not a pass. See `FAILURE_MODES.md`.
