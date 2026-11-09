# paper-writing-agent
# regression: offline, stdlib, no LLM, no TeX. SKIP is not PASS.
# regression-tex: compile-gate family; fails if TeX is missing.
# drift: unittest inventory lock. pytest is not required.
# ci: run_ci.py. C7 needs scipy; C5 needs a demo paper directory.
.PHONY: help regression regression-tex drift ci clean fm-index scripts-index

help:
	@echo "make regression      # offline fixtures (no LLM, no TeX). SKIP != PASS"
	@echo "make regression-tex  # compile-gate only; --fail-on-skip"
	@echo "make drift           # unittest tests/test_inventory_drift.py"
	@echo "make ci              # scripts/run_ci.py (not the offline path)"
	@echo "make clean           # drop runner residue"

regression:
	python3 scripts/scanner_regression.py

regression-tex:
	python3 scripts/scanner_regression.py --family compile-gate --fail-on-skip

drift:
	python3 -m unittest tests.test_inventory_drift -v

ci:
	python3 scripts/run_ci.py

clean:
	rm -rf scripts/llm_calls.jsonl scripts/results/ .tmp*/ .verify*/ *.tmpdir/ reports/ 2>/dev/null || true

fm-index:  ## regenerate the FM index (references/failure-modes.md INDEX section)
	python3 scripts/fm_index.py --write && python3 scripts/fm_index.py --check

scripts-index:  ## regenerate SCRIPTS.md from script docstrings
	python3 scripts/gen_scripts_index.py
