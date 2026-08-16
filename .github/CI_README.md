# Enabling Cloud CI

The `.github/workflows/ci.yml` file in this skill directory is a ready-to-push
GitHub Actions workflow. It runs the full local CI suite (10 checks) on every
push to `main` and on every pull request, across Python 3.11 and 3.12.

## How to enable (3 steps)

1. Push this directory to any GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "paper-writing-agent skill"
   git remote add origin git@github.com:<you>/<repo>.git
   git push -u origin main
   ```
   (The `.github/workflows/ci.yml` must be at the repository root.)

2. GitHub Actions runs automatically on push — no extra setup.

3. Watch the check status on the repo's Actions tab. All 12 steps must pass.

## What CI checks (mirrors `scripts/run_ci.py`)

| Check | What it verifies |
|---|---|
| C1 | all scripts compile (py_compile) |
| C2 | every CLI script's `--help` works |
| C3 | all declared `--selftest`s pass |
| C4 | scanner regression 25/25 (12 families) |
| C6 | power analysis matches Cohen 1988 textbook |
| C7 | stats library bit-identical to scipy (Wilcoxon/McNemar), bootstrap deterministic |
| C8 | judge-output validator (valid / invalid / drifted JSON) |
| C9 | experiment-plan orchestrator dry-run schedule |
| C10 | experiment-suggestion mapping produces P0 plans |

## Local equivalent

Before pushing, run the same suite locally:

```bash
python scripts/run_ci.py          # all checks
python scripts/run_ci.py --only C4,C6,C7   # subset
```

## Notes

- C5 (evidence protection) needs a demo paper dir; the workflow runs it
  via the local `--demo` default when a `demo-tmlr-paper` folder exists
  at the skill root (add one to the repo if you want that check online).
- Network-dependent checks (`gate_citations`, `literature_freshness`) are
  intentionally NOT in CI: they degrade to documented passes offline.
