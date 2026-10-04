# Changelog

## v1.1.0 — 2026-10-04

### Added
- **AAAI venue mapping**（references/venue-mapping.md §3b）：G 级映射 + 维度差异表 + 适配流程——mm-epc（AAAI 2027）投稿线的直接输入；SKILL.md Phase 5 分流同步更新（AAAI 匿名=内容检查非选项检查、生成式 AI 披露必查、双截止节奏）。
- **FM 增长机制**：failure-modes.md 新增入库协议（编号不复用/四字段格式/来源必须为实际修改轮次/脱敏规则）+ `scripts/fm_index.py`（INDEX 自动生成 + `--check` CI 校验）+ `make fm-index`；FM 库 29 → 30 条（FM-30）。
- **SCRIPTS.md 生成器固化**：`scripts/gen_scripts_index.py`（剥文件名前缀、`--check` 模式）+ `make scripts-index`——v1.0.0 的内联生成正式工具化。
- **首次 dogfood**（dogfood/2026-10-04-mm-epc-scan.md）：scan/gate_citations 对布局无关的真实投稿仓开箱即用；产出 FM-30（扫描器误报模式：章节号/格式差异判 mismatch）与 mm-epc 侧 4 项卫生发现（三副本两态/精度不一/正负号呈现/空残留）。

### Unchanged
- 49 门扫描逻辑零改动（本版全部是文档/索引/映射层——护住 25/25 回归与 CI 绿）。

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
