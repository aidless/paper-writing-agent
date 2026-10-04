# paper-writing-agent — 统一入口
.PHONY: help regression ci clean help

help:
	@echo "make regression  # 25 项门禁回归（反证 fixture 锁）"
	@echo "make ci          # 全量 CI 门（run_ci.py，含 TeX 编译层需本机 TeX）"
	@echo "make clean       # 清理运行残留"

regression:
	python scripts/scanner_regression.py

ci:
	python scripts/run_ci.py

clean:
	rm -rf scripts/llm_calls.jsonl scripts/results/ .tmp*/ .verify*/ *.tmpdir/ 2>/dev/null || true
