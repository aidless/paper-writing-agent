"""Lock README counts and known silent-pass paths to the tree.

Stdlib unittest only. pytest is not a dependency; pytest_collected stays 0.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import gate_citations  # noqa: E402
import scanner_regression  # noqa: E402

INV_RE = re.compile(
    r"<!-- inventory: scripts=(\d+) regression_cases=(\d+) fixture_cases=(\d+) "
    r"families=(\d+) reference_docs=(\d+) script_lines=(\d+) drift_tests=(\d+) "
    r"pytest_collected=(\d+) -->"
)
PROBLEM_RE = re.compile(r"<!-- problem-start -->\n(.*?)<!-- problem-end -->", re.S)


def _script_names() -> list[str]:
    return sorted(p.name for p in (ROOT / "scripts").glob("*.py"))


def _script_lines() -> int:
    total = 0
    for p in (ROOT / "scripts").glob("*.py"):
        with p.open(encoding="utf-8", errors="replace") as fh:
            total += sum(1 for _ in fh)
    return total


def _case_names() -> list[tuple[str, str]]:
    names = []
    for fam, spec in scanner_regression.FAMILIES.items():
        for case in spec["manifest"]:
            names.append((fam, case))
    return names


class _OkHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, fmt, *args):
        return


class InventoryDriftTest(unittest.TestCase):
    def test_root_scripts_index_matches_tree(self):
        rc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "gen_scripts_index.py"), "--check"],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(rc.returncode, 0, rc.stdout + rc.stderr)
        index = (ROOT / "SCRIPTS.md").read_text(encoding="utf-8")
        for name in _script_names():
            self.assertIn(f"`{name}`", index)

    def test_hand_indexes_name_every_script(self):
        for rel in ("scripts/SCRIPTS.md", "scripts/SCRIPTS_EN.md"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            missing = [n for n in _script_names() if n not in text]
            self.assertEqual(missing, [], rel)

    def test_readme_inventory_matches_tree(self):
        cases = _case_names()
        families = scanner_regression.FAMILIES
        fixture_dirs = []
        for fam in families:
            fam_dir = ROOT / "assets" / "scanner_fixtures" / fam
            kids = sorted(p.name for p in fam_dir.iterdir() if p.is_dir())
            self.assertEqual(kids, sorted(families[fam]["manifest"]), fam)
            fixture_dirs.extend(kids)
        expected = {
            "scripts": len(_script_names()),
            "regression_cases": len(cases),
            "fixture_cases": len(fixture_dirs),
            "families": len(families),
            "reference_docs": len(list((ROOT / "references").glob("*.md"))),
            "script_lines": _script_lines(),
            "drift_tests": len(re.findall(r"^\s*def test_", Path(__file__).read_text(encoding="utf-8"), re.M)),
            "pytest_collected": 0,
        }
        self.assertNotIn("pytest", (ROOT / "requirements.txt").read_text(encoding="utf-8").lower())
        for rel in ("README.md", "README_EN.md"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            m = INV_RE.search(text)
            self.assertIsNotNone(m, rel)
            got = {
                "scripts": int(m.group(1)),
                "regression_cases": int(m.group(2)),
                "fixture_cases": int(m.group(3)),
                "families": int(m.group(4)),
                "reference_docs": int(m.group(5)),
                "script_lines": int(m.group(6)),
                "drift_tests": int(m.group(7)),
                "pytest_collected": int(m.group(8)),
            }
            self.assertEqual(got, expected, rel)
            self.assertIn(f"regression_cases-{expected['regression_cases']}-blue", text)
            self.assertNotIn("25/25", text)
            self.assertNotIn("PASS-brightgreen", text)

    def test_no_static_pass_or_pypi_badge(self):
        for rel in ("README.md", "README_EN.md", ".github/CI_README.md", "Makefile", "scripts/run_ci.py"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertNotIn("25/25", text, rel)
            self.assertNotIn("pypi.org", text.lower(), rel)
            self.assertNotIn("badge/pypi", text.lower(), rel)

    def test_no_unevidenced_benchmark_scores(self):
        for rel in ("README.md", "README_EN.md"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertNotIn("0.3785", text, rel)
            self.assertNotIn("12/13", text, rel)

    def test_status_is_work_in_progress(self):
        for rel in ("README.md", "README_EN.md"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("STATUS: WORK-IN-PROGRESS — not A yet.", text, rel)
            self.assertRegex(text, r"no writing-quality evaluation|没有写作质量评估")

    def test_problem_statement_is_three_lines(self):
        for rel in ("README.md", "README_EN.md"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            m = PROBLEM_RE.search(text)
            self.assertIsNotNone(m, rel)
            lines = [ln for ln in m.group(1).splitlines() if ln.strip()]
            self.assertLessEqual(len(lines), 3, rel)
            self.assertGreaterEqual(len(lines), 1, rel)

    def test_empty_draft_content_scanners_exit_zero(self):
        """Content scanners report 'nothing found' on a blank manuscript.

        That exit 0 is a known limit, not a submission clearance.
        check_tmlr_compliance fails once any .tex exists without the anonymous package.
        """
        commands = [
            ["scripts/scan_number_consistency.py", "--fail-on-stale"],
            ["scripts/scan_stats_consistency.py", "--fail-on-error"],
            ["scripts/scan_hallucination.py", "--fail-on-error"],
            ["scripts/scan_figure_claims.py", "--fail-on-error"],
            ["scripts/scan_answer_fabrication.py"],
            ["scripts/check_writing_style.py"],
        ]
        probe = ROOT / "_drift_empty"
        if probe.exists():
            shutil.rmtree(probe)
        probe.mkdir()
        try:
            for sub, tex in (("emptydir", None), ("blank", "\\documentclass{article}\n\\begin{document}\n\\end{document}\n")):
                d = probe / sub
                d.mkdir()
                if tex is not None:
                    (d / "main.tex").write_text(tex, encoding="utf-8")
                for cmd in commands:
                    r = subprocess.run(
                        [sys.executable, str(ROOT / cmd[0]), str(d), *cmd[1:]],
                        cwd=ROOT, capture_output=True, text=True, timeout=30,
                    )
                    self.assertEqual(r.returncode, 0, f"{cmd[0]} {sub}\n{r.stdout}\n{r.stderr}")
            empty = probe / "emptydir"
            blank = probe / "blank"
            tmlr_empty = subprocess.run(
                [sys.executable, str(ROOT / "scripts/check_tmlr_compliance.py"), str(empty)],
                cwd=ROOT, capture_output=True, text=True, timeout=30,
            )
            tmlr_blank = subprocess.run(
                [sys.executable, str(ROOT / "scripts/check_tmlr_compliance.py"), str(blank)],
                cwd=ROOT, capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(tmlr_empty.returncode, 0, tmlr_empty.stdout)
            self.assertEqual(tmlr_blank.returncode, 1, tmlr_blank.stdout)
            self.assertIn("no .tex files found", tmlr_empty.stdout)
        finally:
            shutil.rmtree(probe, ignore_errors=True)

    def test_regression_summary_does_not_count_skip_as_pass(self):
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts/scanner_regression.py")],
            cwd=ROOT, capture_output=True, text=True, timeout=120,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        m = re.search(
            r"scanner regression: (\d+) PASS, (\d+) SKIP, (\d+) FAIL \((\d+) cases\)",
            r.stdout,
        )
        self.assertIsNotNone(m, r.stdout)
        passed, skipped, failed, total = (int(m.group(i)) for i in range(1, 5))
        self.assertEqual(failed, 0)
        self.assertEqual(passed + skipped, total)
        self.assertEqual(total, len(_case_names()))
        skip_when = 0
        for spec in scanner_regression.FAMILIES.values():
            for case in spec["manifest"].values():
                if case.get("skip_when"):
                    skip_when += 1
        if shutil.which("pdflatex") and shutil.which("bibtex"):
            self.assertEqual(skipped, 0)
        else:
            self.assertEqual(skipped, skip_when)
            self.assertIn("[SKIP] compile-gate/compile-error", r.stdout)
            self.assertIn("[SKIP] compile-gate/multiply-label", r.stdout)
        self.assertNotRegex(r.stdout, r"scanner regression: \d+/\d+ PASS")

    def test_missing_citation_verifier_is_exit_2(self):
        env = os.environ.copy()
        env.pop("CITATION_VERIFIER_PATH", None)
        env.pop("PWA_RESEARCH_KIT", None)
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            paper = Path(d)
            (paper / "main.bib").write_text(
                "@article{k, title={T}, author={A}, year={2020}}\n", encoding="utf-8")
            r = subprocess.run(
                [sys.executable, str(ROOT / "scripts/gate_citations.py"), str(paper),
                 "--fail-on-suspicious",
                 "--verifier", str(paper / "missing_verify_citations.py")],
                cwd=ROOT, capture_output=True, text=True, env=env, timeout=30,
            )
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("不是 PASS", r.stderr)
        self.assertIn("不是 Manual_needed", r.stderr)
        self.assertNotIn(str(Path.home()), r.stderr)

    def test_manual_needed_is_not_labeled_pass(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), _OkHandler)
        port = server.server_address[1]
        import threading
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory(dir=ROOT) as d:
                paper = Path(d)
                (paper / "main.bib").write_text(
                    "@article{k, title={T}, author={A}, year={2020}}\n", encoding="utf-8")
                verifier = paper / "verify_citations.py"
                verifier.write_text(
                    "import json, sys\n"
                    "out = sys.argv[sys.argv.index('--json') + 1]\n"
                    "json.dump([{'key': 'k', 'status': 'manual_needed', 'detail': 'human'}],\n"
                    "          open(out, 'w', encoding='utf-8'))\n",
                    encoding="utf-8",
                )
                r = subprocess.run(
                    [sys.executable, str(ROOT / "scripts/gate_citations.py"), str(paper),
                     "--verifier", str(verifier),
                     "--fail-on-suspicious",
                     "--probe-host", f"http://127.0.0.1:{port}",
                     "--probe-timeout", "2"],
                    cwd=ROOT, capture_output=True, text=True, timeout=30,
                )
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("门禁结论: MANUAL_REVIEW", r.stdout)
        self.assertNotIn("门禁结论: PASS", r.stdout)

    def test_compile_skip_is_not_labeled_pass(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            paper = Path(d)
            (paper / "main.tex").write_text(
                "\\documentclass{article}\n\\begin{document}\n\\end{document}\n",
                encoding="utf-8",
            )
            out = paper / "compile.md"
            r = subprocess.run(
                [sys.executable, str(ROOT / "scripts/compile_gate.py"), str(paper),
                 "--no-tex", "--out", str(out)],
                cwd=ROOT, capture_output=True, text=True, timeout=30,
            )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("## Compile skipped: 1", r.stdout)
        self.assertIn("**STATIC_ONLY**", r.stdout)
        self.assertNotIn("**PASS**", r.stdout)

    def test_citation_resolver_does_not_use_home(self):
        code = (
            "import os, sys\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, 'scripts')\n"
            "os.environ.pop('CITATION_VERIFIER_PATH', None)\n"
            "os.environ.pop('PWA_RESEARCH_KIT', None)\n"
            "import gate_citations\n"
            "p = gate_citations.resolve_default_verifier()\n"
            "home = str(Path.home())\n"
            "if str(p).startswith(home):\n"
            "    raise SystemExit('resolver used home: ' + str(p))\n"
            "print(p)\n"
        )
        r = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("tools/citation-verifier/verify_citations.py", r.stdout.replace("\\", "/"))

    def test_failure_modes_documents_silent_paths(self):
        text = (ROOT / "FAILURE_MODES.md").read_text(encoding="utf-8")
        for needle in (
            "scan_number_consistency.py",
            "Manual_needed",
            "STATIC_ONLY",
            "compile-error",
            "multiply-label",
            "exits 2",
            "PWA_RESEARCH_KIT",
        ):
            self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()
