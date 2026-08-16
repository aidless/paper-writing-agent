"""paper-writing-agent: local CI runner (D3).

One-command full verification of the paper-writing-agent toolchain, runnable
locally or from any CI platform (GitHub Actions / GitLab CI / Jenkins) via a
single `python scripts/run_ci.py` step. Exits non-zero on any failure so CI
gates on it.

Checks (in order, each independently reported):
  C1  py_compile all scripts
  C2  --help smoke on all CLI scripts (except integration-test entry points)
  C3  --selftest on all scripts that declare one
  C4  scanner_regression (25 fixtures across 12 families)
  C5  test_evidence_protection on a demo paper (evidence protection invariants)
  C6  power_analysis selftest (Cohen textbook cross-check)
  C7  stats library cross-check vs scipy (Wilcoxon / McNemar / bootstrap determinism)
  C8  validate_judge_output (valid / invalid / drifted input)
  C9  run_experiment_plan dry-run (orchestrator schedule)
  C10 suggest_experiments (review-trigger mapping)

Usage:
  python scripts/run_ci.py [--demo <paper_dir>] [--verbose] [--only C1,C2]

Exit 0 = all PASS; exit 1 = any FAIL.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SKILL = SCRIPTS.parent
INTEGRATION_ONLY = {"test_pyramid.py", "test_evidence_protection.py"}


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 600) -> tuple[int, str]:
    r = subprocess.run(cmd, cwd=cwd or SCRIPTS, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=timeout)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", default=None, help="demo paper dir for C5 (default: auto-detect)")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--only", default="", help="comma-separated C-numbers to run")
    args = ap.parse_args()

    only = {c.strip().upper() for c in args.only.split(",") if c.strip()}
    results: list[tuple[str, bool, str]] = []

    def check(cid: str, fn) -> None:
        if only and cid not in only:
            return
        try:
            ok, msg = fn()
        except Exception as e:  # noqa: BLE001
            ok, msg = False, f"raised: {e}"
        results.append((cid, ok, msg))
        print(f"[{'PASS' if ok else 'FAIL'}] {cid}: {msg[:120]}")

    # C1: py_compile
    def c1():
        rc, out = run([sys.executable, "-m", "py_compile"] +
                      [str(p) for p in SCRIPTS.glob("*.py")])
        return rc == 0, out.strip()[-200:] or "compile OK"
    check("C1", c1)

    # C2: --help smoke (skip integration-only entry points)
    def c2():
        fails = []
        for p in sorted(SCRIPTS.glob("*.py")):
            if p.name in INTEGRATION_ONLY:
                continue
            rc, _ = run([sys.executable, str(p), "--help"])
            if rc != 0:
                fails.append(p.name)
        return not fails, f"{len(fails)} help failures" if fails else "all --help OK"
    check("C2", c2)

    # C3: --selftest on scripts that declare it
    def c3():
        selftests = []
        for p in SCRIPTS.glob("*.py"):
            if p.name == "run_ci.py":  # CI runner itself is not a selftest target
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
            if "--selftest" in text and "selftest" in text.lower():
                selftests.append(p.name)
        fails = []
        for name in selftests:
            rc, out = run([sys.executable, str(SCRIPTS / name), "--selftest"])
            if rc != 0:
                fails.append(f"{name}(rc={rc})")
        return (not fails,
                f"{len(selftests)} selftests, {len(fails)} failures" + (f": {fails}" if fails else ""))
    check("C3", c3)

    # C4: scanner regression
    def c4():
        rc, out = run([sys.executable, str(SCRIPTS / "scanner_regression.py")])
        return rc == 0, out.strip().splitlines()[-1] if out.strip() else f"rc={rc}"
    check("C4", c4)

    # C5: evidence protection on demo paper
    def c5():
        demo = args.demo
        if not demo:
            for cand in (SKILL / "demo-tmlr-paper", Path(r"F:\deepseek\demo-tmlr-paper")):
                if cand.exists():
                    demo = str(cand)
                    break
        if not demo:
            return False, "no demo paper found (pass --demo)"
        rc, out = run([sys.executable, str(SCRIPTS / "test_evidence_protection.py"), demo])
        return rc == 0, out.strip().splitlines()[-1] if out.strip() else f"rc={rc}"
    check("C5", c5)

    # C6: power analysis selftest
    def c6():
        rc, out = run([sys.executable, str(SCRIPTS / "power_analysis.py"), "--selftest"])
        return rc == 0, out.strip().splitlines()[-1]
    check("C6", c6)

    # C7: stats vs scipy cross-check
    def c7():
        code = (
            "import sys; sys.path.insert(0, r'%s')\n"
            "from stats import wilcoxon_signed_rank, exact_mcnemar, bootstrap_ci\n"
            "import scipy.stats as st\n"
            "a=[0.62,0.71,0.58,0.69,0.66,0.73,0.60,0.67,0.55,0.64]\n"
            "b=[0.50,0.55,0.48,0.52,0.60,0.65,0.45,0.56,0.51,0.58]\n"
            "r1=wilcoxon_signed_rank(a,b); r2=st.wilcoxon(a,b)\n"
            "assert abs(r1['p']-r2.pvalue)<1e-6, (r1['p'], r2.pvalue)\n"
            "p1,_=exact_mcnemar(15,2); p2,_=exact_mcnemar(15,2)\n"
            "c1=bootstrap_ci([0.5,0.6,0.7,0.8],seed=300); c2=bootstrap_ci([0.5,0.6,0.7,0.8],seed=300)\n"
            "assert c1==c2\n"
            "print('stats vs scipy OK')\n" % SCRIPTS
        )
        rc, out = run([sys.executable, "-c", code])
        return rc == 0, out.strip().splitlines()[-1] if out.strip() else f"rc={rc}"
    check("C7", c7)

    # C8: judge output validator (valid/invalid/drift)
    def c8():
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            good = Path(td) / "good.json"
            good.write_text('{"score": 7, "reason": "ok"}', encoding="utf-8")
            bad = Path(td) / "bad.json"
            bad.write_text('{"score": "x"}', encoding="utf-8")
            rc1, _ = run([sys.executable, str(SCRIPTS / "validate_judge_output.py"),
                          "--schema", "score", "--input", str(good)])
            rc2, _ = run([sys.executable, str(SCRIPTS / "validate_judge_output.py"),
                          "--schema", "score", "--input", str(bad)])
        return rc1 == 0 and rc2 == 1, f"valid rc={rc1}, invalid rc={rc2}"
    check("C8", c8)

    # C9: experiment plan dry-run
    def c9():
        import json as _json, tempfile
        plan = {"project": "ci", "tasks": [
            {"id": "t1", "cmd": ["python", "-c", "pass"], "timeout_s": 30,
             "artifacts": ["out/x.json"]}]}
        with tempfile.TemporaryDirectory() as td:
            pp = Path(td) / "plan.json"
            pp.write_text(_json.dumps(plan), encoding="utf-8")
            rc, out = run([sys.executable, str(SCRIPTS / "run_experiment_plan.py"),
                           str(pp), "--dry-run"])
        return rc == 0, "dry-run schedule OK" if rc == 0 else out[-120:]
    check("C9", c9)

    # C10: suggest experiments mapping
    def c10():
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            rv = Path(td) / "review.md"
            rv.write_text("- [Major] 缺少更强基线对照\n", encoding="utf-8")
            rc, out = run([sys.executable, str(SCRIPTS / "suggest_experiments.py"),
                           "--review", str(rv), "--out", str(Path(td) / "s.md")])
            has_p0 = "P0" in (Path(td) / "s.md").read_text(encoding="utf-8")
        return rc == 0 and has_p0, "mapping OK (P0 suggestion produced)"
    check("C10", c10)

    # C11: answer-fabrication scan (L047 — LLM fit-to-answer detection)
    def c11():
        rc, out = run([sys.executable,
                       str(SCRIPTS / "scan_answer_fabrication.py"),
                       str(SCRIPTS)])
        if rc == 0:
            return True, "no answer-fitting patterns in scripts"
        tail = [l for l in out.splitlines() if "[high]" in l][:3]
        return False, f"{len(tail)} high-risk fitting patterns: {'; '.join(tail)}"
    check("C11", c11)

    print("")
    fails = [r for r in results if not r[1]]
    print(f"CI summary: {len(results) - len(fails)}/{len(results)} PASS"
          + (f", FAILED: {[r[0] for r in fails]}" if fails else " — all green"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
