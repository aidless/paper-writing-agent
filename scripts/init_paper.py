"""paper-writing-agent: one-command paper directory initializer.

Bootstraps a TMLR paper project from the bundled assets and the official
TMLR LaTeX template (templates/tmlr/): creates the directory skeleton,
copies the anonymous submission template (no package option -> double-blind,
per official semantics), neutralizes the template's sample author block,
and lays down CLAIM_LEDGER.md, WORKING_NOTES.md, protocol.md, a G8 OpenReview
form checklist, gates config (with anti-regression stale-marker placeholders),
round-report template, and an initial evidence manifest.

The generated protocol.md and gates_config.json bake in the failure-mode
lessons from the research-writer demo (FM-15..FM-23): statistics must be
recomputed by one canonical script from per-seed data, coefficients must
carry explicit values, simulated data must be disclosed, dataset licenses
must be traceable to first-party sources, and stale values must be pinned
in the acceptance gates. The machine-check scripts are copied into the
project's own scripts/ directory and the gates reference them by RELATIVE
path, so the acceptance gates are portable across machines (FM-24 / R11);
a requirements.txt template is generated so the "requirements lock present"
gate passes from the start (FM-22).

Usage:
  python init_paper.py <paper_dir> [--title "Title"] [--round-report]

Exit 0 on success. Idempotent per file: existing files are never overwritten.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = SKILL_ROOT / "templates" / "tmlr"
ASSETS_DIR = SKILL_ROOT / "assets"
SCRIPTS_DIR = SKILL_ROOT / "scripts"

MANUSCRIPT_FILES = ["main.tex", "main.bib", "math_commands.tex",
                    "tmlr.sty", "tmlr.bst", "fancyhdr.sty"]


def balanced_brace(text: str, start: int) -> int:
    """Return index just past the balanced { } group beginning at start."""
    i = start
    depth = 0
    while i < len(text):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return len(text)


def neutralize_author_block(tex: str) -> str:
    """Replace the sample \\author{...} block with an anonymous placeholder.

    The official template ships real example names; G3 would flag them. The
    anonymous submission uses \\usepackage{tmlr} with NO option, so we drop
    the author block entirely and leave instructions for the camera-ready.
    """
    m = re.search(r"\\author\s*\{", tex)
    if not m:
        return tex
    end = balanced_brace(tex, m.start() + len(m.group(0)) - 1)
    placeholder = ("% Authors are hidden in the anonymous submission (TMLR G3).\n"
                   "% Restore the real name block only for the camera-ready\n"
                   "% version using \\\\usepackage[accepted]{tmlr}.\n")
    return tex[:m.start()] + placeholder + tex[end:]


def neutralize_camera_ready_defs(tex: str) -> str:
    """Comment out camera-ready-only \\def lines (month/year/openreview).

    These carry a forum-id placeholder URL that the G4 scanner would flag in
    a double-blind submission; they belong to the accepted version only.
    """
    return re.sub(r"(?m)^(?P<def>\\def\\(?:month|year|openreview)\b.*)$",
                  r"% \g<def>", tex)


def render_main_tex(title: str | None) -> str:
    src = (TEMPLATE_DIR / "main.tex").read_text(encoding="utf-8")
    tex = neutralize_camera_ready_defs(src)
    tex = neutralize_author_block(tex)
    if title:
        tex = re.sub(r"\\title\{[^}]*\}", lambda _: f"\\title{{{title}}}", tex, count=1)
    return tex


def write_once(path: Path, content: str, label: str) -> None:
    if path.exists():
        print(f"SKIP {label}: exists -> {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"WROTE {label}: {path}")


WORKING_NOTES = """# WORKING_NOTES.md

- 论文标题: {title}
- Phase: 0 收据
- 范围 / 假设:
- 开放问题:
- 证据包入口:
"""

PROTOCOL = """# 实验协议 protocol.md

- 研究问题 / 假设（可证伪）:
- 实验设计（组别 / 配置 / 消融）:
- 分析计划（检验、效应量、CI、多重比较校正）:
  - 统计口径（FM-16/17 教训）: 每个统计量必须能由唯一分析脚本从逐种子原始数据重算；
    mean(d) 必须等于组间均值差（用 assert 强制）；W/p/r 由同一次调用产出。
  - 效应量公式（FM-17 教训）: 明确 r = z/sqrt(2n) 与 rank-biserial = 1-2W/S 的口径与符号约定。
- 排除标准:
- 种子数 / 样本量口径（唯一事实源）: 全文统一，摘要/正文/表格/caption 同口径。
- 预注册链接（如适用）:
- 评测协议: 数据集/指标/分箱数/校准集划分/后处理基线拟合方式，全部写明。
- 训练细节: 优化器/学习率/batch/增强/weight decay/温度与 λ 系数（FM-20 教训: 参数必须给取值）。
- 数据披露（FM-21 教训）: 若数据为模拟/合成/演示性质，必须在此与正文 Setup 显式声明，
  不得以真实实验口吻呈现；正式投稿前替换为真实数据。
- 数据集合规: 数据集许可/版本（FM-23 教训: 只写可溯源的一手来源，禁止编造官方声明）；
  人类受试者/IRB 状态。
- 环境: Python 版本 + requirements.txt 位置（FM-22 教训: 锁文件必须真实存在）。
- 可复现编译: 用 `SOURCE_DATE_EPOCH=<固定值，如 1723600000> pdflatex` 编译，使 PDF
  字节级可复现，并把实际使用的 epoch 值与预期 PDF 哈希记入本协议
  （FM 教训: 不设则时间戳漂移导致哈希假阳性）。
- 工具输出可复现（FM-25 教训）: 扫描/验证脚本的报告必须渲染相对路径（不内嵌
  绝对路径），否则"按标准流程重跑"会改变报告字节、破坏 manifest 对账；从不同
  cwd 运行同一扫描应得到字节一致的报告。
- 生成统计量的唯一脚本: analysis.py（只读重算，不在脚本内 np.random 合成数据）。
"""

G8_CHECKLIST = """# TMLR G8 OpenReview 表单核对记录

> G8 门要求：OpenReview 提交表单的 profiles / COI / AE 建议 / funding / IRB 逐项核对。
> 本文件是作者侧核对清单（不随稿件提交，但正式投稿前必须完成）。

| 表单项 | 状态 | 填写内容/理由 |
|---|---|---|
| 作者 OpenReview profiles 完整 | ⏳ 待填 | 真实作者注册时核对 |
| COI 声明 | ⏳ 待填 | 与 AE/审稿人的潜在冲突 |
| AE 建议 | ⏳ 待填 | 按 TMLR AE 列表提名 |
| Funding 声明 | ⏳ 待填 | 如实填写 |
| IRB / 人类受试者 | ⏳ 待填 | N/A 或说明 |
| 补充材料 ≤100MB | ⏳ 待填 | 数据/代码包 <100MB |
"""

GATES_CONFIG_BOOTSTRAP = {
  "checks": [
    {"type": "file_exists", "name": "main.tex present", "path": "paper/main.tex"},
    {"type": "file_exists", "name": "evidence present", "path": "results/e1.json"},
    {"type": "file_exists", "name": "analysis script present", "path": "analysis.py"},
    {"type": "file_exists", "name": "data generator present", "path": "generate_data.py"},
    {"type": "file_exists", "name": "requirements lock present", "path": "requirements.txt"},
    # FM-17/22/23 教训: 把已知旧错值加入 stale-marker 门，防止修改轮复活。
    # 示例: {"type": "stale_marker_absent", "name": "no stale values", "path": "paper/main.tex", "markers": ["旧值A", "旧值B"]},
    {"type": "script_runs", "name": "canonical analysis recomputes evidence", "cmd": ["python", "analysis.py", "."], "cwd": ".", "timeout": 300},
    # FM-24 教训: manifest 哈希对账作为可执行门（防止改文件后忘重建清单）。
    # 相对路径 scripts/...：init_paper 会把技能脚本复制进新项目 scripts/ 目录，
    # 使验收门跨机器可复跑（不依赖本机技能安装位置）。
    {"type": "script_runs", "name": "manifest hash reconciliation", "cmd": ["python", "scripts/build_evidence_manifest.py", ".", "--verify", "evidence_manifest.json"], "cwd": ".", "timeout": 300},
    {"type": "script_runs", "name": "ledger verifier", "cmd": ["python", "scripts/verify_claim_ledger.py", "."], "cwd": ".", "timeout": 300}
  ]
}

WORKING_NOTES = """# WORKING_NOTES.md

- 论文标题: {title}
- Phase: 0 收据
- 范围 / 假设:
- 开放问题:
- 证据包入口:
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paper_dir", help="paper project directory to create")
    ap.add_argument("--title", default="", help="paper title (also written to main.tex)")
    ap.add_argument("--round-report", action="store_true",
                    help="also copy revision_round_report.template.md to ROUND_R0.md")
    args = ap.parse_args()

    root = Path(args.paper_dir).resolve()
    paper = root / "paper"
    for d in [root, paper, root / "results", root / "reports", root / "evidence"]:
        d.mkdir(parents=True, exist_ok=True)
    print(f"Created skeleton under {root}")

    if not TEMPLATE_DIR.is_dir():
        print(f"ERROR: TMLR template missing at {TEMPLATE_DIR}", file=sys.stderr)
        return 1

    # 0. Copy the machine-check scripts into the project's own scripts/ dir so
    # the acceptance gates use RELATIVE paths and stay portable across machines
    # (FM-24 / R11 lesson: never depend on the skill install location).
    scripts_dir = root / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    for script in ["build_evidence_manifest.py", "verify_claim_ledger.py",
                   "scan_number_consistency.py", "scan_stats_consistency.py",
                   "check_writing_style.py", "check_tmlr_compliance.py",
                   "run_acceptance_gates.py", "scanner_regression.py",
                   "test_pyramid.py", "make_run_record.py", "verify_tree_diff.py", "seal_run.py", "test_evidence_protection.py", "check_submit_ready.py", "release.py",
                   "compile_gate.py", "scan_figure_claims.py", "verify_taint.py",
                   "verify_labels.py", "gate_citations.py", "check_literature_freshness.py",
                   "check_judge_calibration.py", "log_writing_session.py",
                   "scan_hallucination.py", "stats.py", "power_analysis.py",
                   "validate_judge_output.py", "suggest_experiments.py",
                   "prepare_submission.py", "run_experiment_plan.py", "switch_project.py",
                   "check_submission_package.py", "draft_rebuttal.py", "make_camera_ready.py"]:
        src = SCRIPTS_DIR / script
        if src.exists():
            write_once(scripts_dir / script, src.read_text(encoding="utf-8"), f"script {script}")
        else:
            print(f"WARN script not found: {src}")

    # 0b. requirements.txt template (FM-22: the lock file must really exist,
    # because the gates include a "requirements lock present" check).
    write_once(root / "requirements.txt",
               ("# {title} environment lock file (FM-22)\n"
                "# Fill in the pinned versions of your analysis dependencies, e.g.:\n"
                "numpy==2.5.1\nscipy==1.16.0\n").format(title=args.title or "paper"),
               "requirements.txt")

    # 1. anonymous TMLR manuscript (no package option => double-blind)
    main_tex = paper / "main.tex"
    if main_tex.exists():
        print(f"SKIP manuscript: exists -> {main_tex}")
    else:
        (paper / "main.tex").write_text(render_main_tex(args.title or None), encoding="utf-8")
        print(f"WROTE manuscript: {paper / 'main.tex'} (anonymous, no tmlr option)")
    for f in MANUSCRIPT_FILES[1:]:
        write_once(paper / f, (TEMPLATE_DIR / f).read_text(encoding="utf-8"), f"manuscript {f}")

    # 2. author-side working documents
    write_once(root / "WORKING_NOTES.md", WORKING_NOTES.format(title=args.title or "(未定)"), "WORKING_NOTES.md")
    write_once(root / "evidence" / "protocol.md", PROTOCOL, "protocol.md")
    write_once(root / "evidence" / "G8_form_checklist.md", G8_CHECKLIST, "G8_form_checklist.md")
    write_once(root / "CLAIM_LEDGER.md",
               (ASSETS_DIR / "claim_ledger.template.md").read_text(encoding="utf-8"), "CLAIM_LEDGER.md")
    write_once(root / "STATE_SNAPSHOT.md",
               (ASSETS_DIR / "state_snapshot.template.md").read_text(encoding="utf-8"), "STATE_SNAPSHOT.md")
    write_once(root / "gates_config.json",
               json.dumps(GATES_CONFIG_BOOTSTRAP, indent=2, ensure_ascii=False), "gates_config.json")
    if args.round_report:
        write_once(root / "ROUND_R0.md",
                   (ASSETS_DIR / "revision_round_report.template.md").read_text(encoding="utf-8"), "ROUND_R0.md")

    # 3. bootstrap manifest via the sibling builder
    manifest = root / "evidence_manifest.json"
    if manifest.exists():
        print(f"SKIP manifest: exists -> {manifest}")
    else:
        manifest.write_text(json.dumps({
            "paper": "PAPER_TITLE",
            "version": "R0",
            "created": "",
            "files": [],
            "notes": "Run: python scripts/build_evidence_manifest.py <paper_dir> --out evidence_manifest.json",
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"WROTE manifest bootstrap: {manifest} (run build_evidence_manifest.py to fill hashes)")

    print("\nNext steps (paper-writing-agent phases):")
    print(f"  1. Put experiment outputs under {root / 'results'}")
    print(f"  2. python scripts/build_evidence_manifest.py {root} --out {manifest.name}  (or from {root}: scripts/build_evidence_manifest.py . --out evidence_manifest.json)")
    print(f"  3. Edit CLAIM_LEDGER.md (Phase 1), draft (Phase 2), then run all machine checks (Phase 3).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
