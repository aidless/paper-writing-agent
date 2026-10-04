# Changelog

## v1.3.0 — 2026-10-04

### Fixed
- **FM-31（实测）：table-vs-prose 门第四类误报——假想值**。dogfood 2（AGI-KIT）发现 Limitations 段把待检验的近邻值对 `(0.8499999 vs 0.8500001)` 与表格 `0.85` 配对报成漂移。新增 `HYPOTHETICAL_RE`：段落含 future / follow-up(s) / planned / will / would / prospective / limitation 时，段内近邻配对降级为 `hypothetical`（与前三类同样照常列出，不隐藏）。
- **`references/failure-modes_EN.md` 脱敏补漏**：EN 版库落后 CN 版一轮脱敏——`35.4-37.2%`、`CV=0.218`、`0.398/1.081=0.368`、`W=412, p=0.0021, r=0.531`、`[0.0275,0.0341]`、`0.806→0.807` 等 17 组真实论文统计值以原值留在公开文件里。已全部替换为与 CN 版一致的示例值并加脱敏声明。
- **双语库分叉治理**：EN 版补入库协议 + INDEX + FM-30/31（此前停在 FM-29）。`fm_index.py` 升级为双语门，同时维护两份 INDEX 并在 `--check` 断言条目数一致（反证：删 EN 的 FM-30 → exit 1 + `entry-count drift CN=31 EN=30`）。

### Added
- 夹具 `hypothetical-false-positive`（期望 0 mismatch / 2 downgrades）；回归 25 → 27 项全 PASS。
- dogfood 2 报告 `dogfood/2026-10-04-agi-kit-scan.md`。
- CI 新增两道门：`run_ci.py` 的 **C12**（`fm_index.py --check`，双语索引 + 计数一致）与 **C13**（`gen_scripts_index.py --check`）——做成门而非改 workflow，云端 CI 已在跑 run_ci.py，无需额外 workflow scope。

### Notes
- 规则实现注记（两条都是被真实稿抓到的）：`follow-?up\b` 匹配不到 "follow-ups"（`s` 紧跟使词边界失败，AGI-KIT 原文正是 "Two follow-ups remain"）；FM-30 的 40 字符 structural 窗口会吞掉真漂移。
- 换域即挖出一类新误报（mm-epc → dimension/format/structural，AGI-KIT → hypothetical）。每次把门用在陌生稿件域都应重跑一遍真实稿。

## v1.2.0 — 2026-10-04

### Fixed
- **FM-30 落地：table-vs-prose 门量纲/格式/结构感知**。dogfood 审计 mm-epc 时该门报 5 条、人工量纲复核后 5 条全是误报——一个总是报警的门会训练使用者忽略输出。三类误报现在被判定前置分类：dimension（`×1.00` 倍数列 vs `1.0%` 百分比）、format（`{+}0.068` 对齐正号 vs 无符号同值）、structural（`Section 3.1` / `### 3.1` 章节号）。
- **降级不等于隐藏**：所有降级配对进独立的 `Format/dimension downgrades (FM-30)` 报告段并附理由，分类过程可审计。

### 反证（AGENTS.md #7）
- 第一版 structural 规则用 40 字符窗口，把真漂移（`Table 1 ... achieves 0.7486`）一起吞了——`table-prose-dirty` 夹具当场抓到，改为行内紧邻锚定。
- 新增夹具 `dimension-false-positive`（期望 0 mismatch / 3 downgrades）；回归 25 → 26 项全 PASS。
- mm-epc 原现场重扫：5 条误报全部正确降级并标注理由，其中 `1.00` vs `1.0` 被准确识别为 ratio/percent 量纲错配。

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
