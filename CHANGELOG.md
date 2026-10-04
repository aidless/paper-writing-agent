# Changelog

## v1.0.0 — 2026-10-04

首个开源发布。

- **编排**：SKILL.md（Phase 0-5：Intake → Claim ledger → Draft → Machine checks → Revision/Adversarial review → TMLR Submission compliance）
- **校验门**：scripts/ 49 个确定性 Python 门（约 9.8K 行），统计量 stdlib 独立重算
- **反证锁**：assets/scanner_fixtures/ 29 个 dirty fixture，scanner_regression 25/25 PASS
- **方法论**：references/ 27 篇（含 failure-modes.md 29 条失败模式库，统计值已脱敏）
- **模板**：templates/tmlr/（JmlrOrg 官方样式，Apache-2.0）

### 本版本包含的工程修正

- 引用验证路径改由 `CITATION_VERIFIER_PATH` 环境变量解析（不再依赖本机绝对路径，缺省仓内相对路径，缺失时门降级为 Manual_needed）
- 运行残留（llm_calls.jsonl / scripts/results/）移出仓库并纳入 .gitignore
- 依赖下限 pin（requirements.txt），CI py3.11/3.12 持续验证最新版
- 补 Apache-2.0 LICENSE、SCRIPTS.md 脚本索引（docstring 自动生成）、Makefile 统一入口
