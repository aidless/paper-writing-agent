"""scan_answer_fabrication.py — 答案拟合扫描器 (L047 工具化, 论文 agent 管线集成).

背景: LLM 驱动的分析在 judge/基准反馈压力下会"拟合答案"——把计算结果
缩放到已知论文值(TARGET 缩放/不确定性 tune/强制份额)。本扫描器检测论文
工程目录中生成脚本/证据代码的此类模式, 作为 Phase 3 机器检查的组成部分。

用法:
  python scan_answer_fabrication.py <paper_dir>            # 扫描 evidence/scripts
  python scan_answer_fabrication.py <file.py>              # 扫描单个脚本
  python scan_answer_fabrication.py --selftest             # 自测

输出: 命中清单(行号+模式+片段), exit 0=clean / 1=found fitting patterns.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# (正则, 风险, 说明) — 与 research-kit audit_generated_script.py 同源
PATTERNS = [
    (r"\bTARGET(?:_2000_2023|_VALUE|_SCORE|_ANS|_RESULT|_GT|_Y|_VAL|_NUM|_N)\w*\s*=",
     "high", "TARGET 常量(已知答案锚点)"),
    (r"\bREFERENCE\w*\s*=\s*(?!None)", "high", "REFERENCE 常量(可能用于对齐)"),
    (r"\bPAPER(?:_SHARE|_VALUE|_SCORE|_ANS|_RESULT|_GT|_Y|_VAL|_NUM|_N)\w*\s*=",
     "high", "PAPER 常量"),
    (r"(^|\s)(scale|rescale|scal)\w*\s*=", "high", "缩放因子赋值"),
    (r"(^|\s)(tune|tun)\w*\s*=", "high", "tune 赋值"),
    (r"(^|\s)(calibrat)\w*\s*=", "high", "calibrate 赋值"),
    (r"(^|\s)factor\s*=", "high", "factor 赋值"),
    (r"to match (the )?(paper|reference|published|target)", "high", "显式匹配论文/参考值"),
    (r"force\w*\s*(paper|share|target)", "high", "强制论文份额/目标"),
    (r"remaining_target", "high", "剩余目标分配逻辑"),
    (r"(6542|548|36%)", "med", "论文具体数值字面量"),
]

SKIP_DIRS = {".git", "__pycache__", ".verify", ".compile", ".r", "tmp", ".tmp"}
TARGET_PATTERNS = (r"\bTARGET(?:_2000_2023|_VALUE|_SCORE|_ANS|_RESULT|_GT|_Y|_VAL|_NUM|_N)\w*\s*=",
                   r"\bREFERENCE\w*\s*=\s*(?!None)",
                   r"\bPAPER(?:_SHARE|_VALUE|_SCORE|_ANS|_RESULT|_GT|_Y|_VAL|_NUM|_N)\w*\s*=")


def audit_code(code: str) -> list[dict]:
    hits = []
    for pat, risk, desc in PATTERNS:
        for m in re.finditer(pat, code, re.IGNORECASE):
            ln = code[:m.start()].count("\n") + 1
            line = code.split("\n")[ln - 1].strip()
            # 误报排除: calibrated 作为布尔判定变量(非数据校准)
            if pat.startswith(r"(^|\s)(calibrat)") and re.match(r"calibrated\s*=", line, re.I):
                continue
            hits.append({"pattern": pat, "risk": risk, "desc": desc,
                         "line": ln, "text": line[:150]})
    # 二次判定: TARGET/REFERENCE/PAPER 若未参与数据变换 → 降级 report-only
    for h in hits:
        if h["pattern"] in TARGET_PATTERNS:
            name = re.match(r"(\w+)", h["text"].split("=")[0].strip()).group(1)
            decl_line = h["line"]
            transform = False
            for mu in re.finditer(rf"\b{name}\b", code):
                ln = code[:mu.start()].count("\n") + 1
                if ln == decl_line:
                    continue
                seg = code[mu.start():mu.start() + 200].split("\n")[0]
                if re.search(r"[*/]", seg) and not re.search(r"[*/]\s*[\"']", seg):
                    if not re.search(r"(append|print|f[\"']|reference|Difference|comparison)",
                                     seg, re.IGNORECASE):
                        transform = True
                        break
                elif re.search(r"=\s*[^\"']*\b" + name, seg) and \
                        not re.search(r"(append|print|f[\"']|reference|Difference|comparison|diff)",
                                      seg, re.IGNORECASE):
                    transform = True
                    break
            if not transform:
                h["risk"] = "info"
                h["desc"] += " (report-only: 仅报告对比, 未参与数据变换)"
            elif name == "reference_path":
                h["risk"] = "info"
                h["desc"] += " (文件路径变量, 非答案锚点)"
    return hits


def scan_file(path: Path) -> list[dict]:
    try:
        code = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return audit_code(code)


def scan_dir(root: Path) -> list[tuple[Path, list[dict]]]:
    results = []
    self_name = Path(__file__).name
    for p in sorted(root.rglob("*.py")):
        if p.name == self_name:
            continue  # 跳过扫描器自身(selftest 样例是字符串, 非真实代码)
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        hits = scan_file(p)
        if hits:
            results.append((p, hits))
    return results


def selftest() -> int:
    """自测: 拟合代码命中, 诚实代码不误报."""
    fitting = ('TARGET_2000_2023 = -6542.0\n'
               'scale = TARGET_2000_2023_ERR / raw_unc\n'
               'df[col] = df[col] * factor\n'
               'force_share = 0.22\n')
    honest = ('TARGET_2000_2023 = -6542.0  # paper reference for comparison\n'
              'lines.append(f"Paper reference: {TARGET_2000_2023:.0f} Gt")\n'
              'cum = annual.sum()  # independent\n')
    h1 = audit_code(fitting)
    h2 = audit_code(honest)
    high_fit = [h for h in h1 if h["risk"] == "high"]
    high_honest = [h for h in h2 if h["risk"] == "high"]
    ok = len(high_fit) >= 2 and len(high_honest) == 0
    print(f"selftest: fitting high={len(high_fit)} (want>=2), "
          f"honest high={len(high_honest)} (want==0) -> "
          f"{'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", default=".",
                    help="paper_dir / file.py (omit for --selftest)")
    ap.add_argument("--selftest", action="store_true", help="run selftest")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    tgt = Path(args.target)
    if tgt.is_dir():
        results = scan_dir(tgt)
    elif tgt.is_file():
        results = [(tgt, scan_file(tgt))]
    else:
        print(f"target not found: {tgt}")
        return 2

    if args.json:
        import json
        print(json.dumps([{"file": str(p), "hits": h} for p, h in results],
                         indent=2, ensure_ascii=False))
        return 1 if any(h for _, h in results) else 0

    total = sum(len(h) for _, h in results)
    if total == 0:
        print(f"[CLEAN] no answer-fitting patterns in {tgt}")
        return 0
    print(f"[AUDIT] {total} hit(s) in {len(results)} file(s):")
    for p, hits in results:
        for h in hits:
            print(f"  [{h['risk']}] {p.name}:L{h['line']} ({h['desc']}): {h['text']}")
    high = sum(1 for _, hs in results for h in hs if h["risk"] == "high")
    return 1 if high else 0


if __name__ == "__main__":
    sys.exit(main())
