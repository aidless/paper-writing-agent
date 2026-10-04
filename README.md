# paper-writing-agent

**证据优先的论文写作 Agent Skill**（TMLR 投稿向）：编排提示词（`SKILL.md`）+ 49 个可运行的确定性校验门（`scripts/`，约 9.8K 行）+ 27 篇方法论文档（`references/`）+ TMLR 官方 LaTeX 模板（`templates/tmlr/`，Apache-2.0）。

核心设计：**每个校验门都配 dirty fixture 反证**（`tests/` 29 个 fixture，`scanner_regression.py` 25/25 PASS），统计量由 stdlib 独立重算（不信任上游数字）。方法论与详细脚本索引见：

- [SKILL.md](SKILL.md) — Agent 编排入口（各 Phase 触发哪些门）
- [SCRIPTS.md](SCRIPTS.md) — 脚本全索引（中文）
- [README_EN.md](README_EN.md) — English overview + CI guide
- [references/](references/) — 方法论 27 篇（含 `failure-modes.md` 真实改稿教训库）
- [templates/tmlr/](templates/tmlr/) — TMLR 官方模板

## 快速开始

```bash
pip install -r requirements.txt
python scripts/scanner_regression.py   # 自检：25 项门禁回归
python scripts/run_ci.py               # 全量 CI 门
```

引用验证门通过环境变量 `CITATION_VERIFIER_PATH` 指向外部 `verify_citations.py`（默认仓内 `tools/citation-verifier/verify_citations.py`，不存在时该门降级为 Manual_needed 并如实标注）。

## License

Apache-2.0
