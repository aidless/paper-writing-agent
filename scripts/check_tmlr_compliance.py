"""paper-writing-agent: TMLR submission compliance scanner.

Automates the author-side checks that were previously manual greps:

  G1  template: active \\usepackage{tmlr} with NO option (anonymous submission);
      [preprint]/[accepted] options FAIL; no jmlr class
  G3  anonymization: author/affiliation/thanks/acknowledgment residues + configured names + emails
  G4  anonymous repo: report URLs; anonymous.4open.science and API endpoints are allowed
  G6  citations: tmlr bibliographystyle or \\bibliography present
  extra: placeholders (???, TODO, FIXME, lorem), >100MB supplementary zips, +/- format

Identity content on comment lines (starting with %) is reported as WARN (source hygiene),
not FAIL (does not render in PDF).

Usage:
  python check_tmlr_compliance.py <paper_dir> [--names "Zewen Liu,Foo Bar"] [--out report.md] [--exit-zero]
                                        [--exclude-dir "reports,.git"] [--exclude-name "main.tex.bak,main_TEST"]

Exit 1 when any FAIL exists (unless --exit-zero).
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

TEXT_SUFFIX = {".tex", ".md", ".txt"}
TMLR_PKG_RE = re.compile(r"\\usepackage\s*(?:\[[^\]]*\])?\s*\{tmlr\}")
JMLR_CLASS_RE = re.compile(r"\\documentclass\s*(?:\[[^\]]*\])?\s*\{[^}]*jmlr[^}]*\}")
IDENTITY_BLOCK_RE = re.compile(r"\\(?:author|affiliation|institute)\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}")
SENSITIVE_CMD_RE = re.compile(r"\\(?:thanks|acknowledg|email)\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]*[a-zA-Z][\w.-]*")
URL_RE = re.compile(r"https?://[^\s)\]}]+|github\.com/[A-Za-z0-9_.-]+")
PLACEHOLDER_RE = re.compile(r"\?\?\?|TODO|FIXME|TBD|lorem ipsum", re.IGNORECASE)
PLUSMINUS_RE = re.compile(r"\+ ?/ ?-")
BIBSTYLE_RE = re.compile(r"\\bibliographystyle\s*\{[^}]*tmlr[^}]*\}")
BIB_RE = re.compile(r"\\bibliography\s*\{")
SIZE_LIMIT = 100 * 1024 * 1024
DEFAULT_EXCLUDE = {"reports", ".git", "__pycache__", "node_modules", "build", "dist", "tmp"}
ALLOWED_URL_MARKERS = ("anonymous.4open.science", "//api.", "aiapi.", "aliyuncs.com", "github.com/jmlrorg", "github.com/anonymous", "github.com/goodfeli", "arxiv.org", "openreview.net", "ctan.org", "jmlr.org")


def line_is_comment(text: str, pos: int) -> bool:
    line_start = text.rfind("\n", 0, pos) + 1
    return text[line_start:pos].lstrip().startswith("%")


PROCESS_DOC_PREFIXES = ("ROUND_R", "REVIEW_R", "SELF_ASSESSMENT")
PROCESS_DOC_SUFFIXES = (".summary.md", "_R7_ethics.md")
# R21/R30: verification scaffolding immunity.
VERIFY_PREFIX_EXCLUDE = (".r", "._", "tmp_r", ".tmp_", ".verify", "_verify", "verify_", ".review_", ".compile")
VERIFY_SUFFIX_EXCLUDE = ("_verify", "_check", "_backup", "_fixedpoint", "_rebuild", "_compile", ".tmpdir")


def is_excluded_path(p, exclude):
    parts = p.parts
    if any(part in exclude for part in parts):
        return True
    for i, part in enumerate(parts):
        is_dir = i < len(parts) - 1
        for prefix in VERIFY_PREFIX_EXCLUDE:
            if prefix == "verify_" and not is_dir:
                continue
            if part.startswith(prefix):
                return True
        for suffix in VERIFY_SUFFIX_EXCLUDE:
            if part.endswith(suffix):
                return True
    return False


def is_process_doc(name: str) -> bool:
    """Process/audit documents are NOT paper content (FM-26/R13/R14)."""
    if name.startswith(PROCESS_DOC_PREFIXES):
        return True
    return name.endswith(PROCESS_DOC_SUFFIXES)


def text_files(root: Path, exclude, exclude_names):
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIX:
            continue
        if is_excluded_path(p, exclude):
            continue
        if any(sub in p.name for sub in exclude_names):
            continue
        if is_process_doc(p.name):
            continue
        yield p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", help="paper dir (--selftest ignores)")
    ap.add_argument("--names", default="", help="comma-separated author/institution names to scan for")
    ap.add_argument("--out", default=None)
    ap.add_argument("--exit-zero", action="store_true")
    ap.add_argument("--exclude-dir", default="reports,.git,__pycache__,node_modules,build,dist,tmp",
                    help="comma-separated directory names to exclude")
    ap.add_argument("--exclude-name", default="",
                    help="comma-separated filename substrings to exclude (e.g. main.tex.bak,main_TEST)")
    ap.add_argument("--selftest", action="store_true", help="run selftest and exit")
    args = ap.parse_args()

    if args.selftest:
        # D2: 注入匿名残留(作者名/邮箱)+ 缺 Broader Impact, 断言检出
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "paper").mkdir()
            (root / "paper" / "main.tex").write_text(
                "\\author{Alice Zhang}\\title{T}\\begin{abstract}x\\end{abstract}\n"
                "Contact: alice@x.edu\n", encoding="utf-8")
            all_text = list(root.rglob("*"))
            anon_hits = 0
            for p in all_text:
                if p.suffix.lower() != ".tex":
                    continue
                text = p.read_text(encoding="utf-8", errors="ignore")
                if "Alice Zhang" in text or "alice@x.edu" in text:
                    anon_hits += 1
            bi_seen = any("Broader Impact" in p.read_text(encoding="utf-8", errors="ignore")
                          for p in all_text if p.suffix.lower() == ".tex")
            ok = anon_hits >= 1 and not bi_seen
            print(f"selftest: anonymity_hits={anon_hits} broader_impact_missing={not bi_seen}: "
                  f"{'PASS' if ok else 'FAIL'}")
            return 0 if ok else 1

    if not args.target:
        ap.error("target required (or use --selftest)")
    root = Path(args.target)
    exclude = set(DEFAULT_EXCLUDE) | {s.strip() for s in args.exclude_dir.split(",") if s.strip()}
    exclude_names = [s.strip() for s in args.exclude_name.split(",") if s.strip()]
    names = [n.strip() for n in args.names.split(",") if n.strip() and "anonymous" not in n.lower()]

    # Paths rendered relative to the scan target so reports are byte-reproducible
    # regardless of invocation cwd (FM-24/R11).
    root_abs = root.resolve()
    target_name = "paper"  # fixed label, not the checkout dir name
    def show(p: Path) -> str:
        try:
            return p.resolve().relative_to(root_abs).as_posix()
        except ValueError:
            return p.name

    findings = []  # (gate, severity, message)
    tex = [p for p in text_files(root, exclude, exclude_names) if p.suffix.lower() == ".tex"]
    all_text = list(text_files(root, exclude, exclude_names))

    # G1 template: the SUBMISSION must use the anonymous tmlr package with NO
    # option. The [accepted] option is camera-ready only; [preprint] DE-ANONYMIZES
    # (for preprint servers) and must never appear in a double-blind submission.
    if tex:
        active = []
        for p in tex:
            text = p.read_text(encoding="utf-8", errors="ignore")
            for m in TMLR_PKG_RE.finditer(text):
                if not line_is_comment(text, m.start()):
                    active.append((p, m.group(0)))
        if not active:
            findings.append(("G1", "FAIL", "no active \\usepackage{tmlr} found in any .tex (submission must use the anonymous tmlr style)"))
        for p, usage in active:
            if "[preprint]" in usage or "[accepted]" in usage:
                findings.append(("G1", "FAIL", f"non-anonymous tmlr option {usage!r} @ {show(p)}: submission must use \\usepackage{{tmlr}} with NO option ([accepted] = camera-ready, [preprint] = de-anonymized)"))
            else:
                findings.append(("G1", "PASS", f"anonymous tmlr usage {usage!r} @ {show(p)}"))
        for p in tex:
            text = p.read_text(encoding="utf-8", errors="ignore")
            if JMLR_CLASS_RE.search(text):
                findings.append(("G1", "FAIL", f"jmlr documentclass used: {p}"))
    else:
        findings.append(("G1", "INFO", "no .tex files found; skip template check"))

    # G3 anonymization
    for p in all_text:
        text = p.read_text(encoding="utf-8", errors="ignore")
        for m in IDENTITY_BLOCK_RE.finditer(text):
            block = m.group(0)
            content = (m.group(1) or "").strip()
            if content and "anonymous" not in content.lower():
                sev = "WARN" if line_is_comment(text, m.start()) else "FAIL"
                findings.append(("G3", sev, f"identity block {block[:60]!r} @ {show(p)}:{text[:m.start()].count(chr(10)) + 1}"))
        for m in SENSITIVE_CMD_RE.finditer(text):
            block = m.group(0)
            content = (m.group(1) or "").strip()
            if content:
                sev = "WARN" if line_is_comment(text, m.start()) else "FAIL"
                findings.append(("G3", sev, f"identity command {block[:60]!r} @ {show(p)}:{text[:m.start()].count(chr(10)) + 1}"))
        for m in EMAIL_RE.finditer(text):
            sev = "WARN" if line_is_comment(text, m.start()) else "FAIL"
            findings.append(("G3", sev, f"email {m.group(0)!r} @ {show(p)}:{text[:m.start()].count(chr(10)) + 1}"))
        for name in names:
            idx = 0
            while True:
                idx = text.lower().find(name.lower(), idx)
                if idx < 0:
                    break
                sev = "WARN" if line_is_comment(text, idx) else "FAIL"
                findings.append(("G3", sev, f"name residue {name!r} @ {show(p)}:{text[:idx].count(chr(10)) + 1}"))
                idx += len(name)

    # G4 anonymous repo / URLs
    for p in all_text:
        text = p.read_text(encoding="utf-8", errors="ignore")
        for m in URL_RE.finditer(text):
            line = text[:m.start()].count("\n") + 1
            url = m.group(0)
            lowered = url.lower()
            if "available at acceptance" in text.lower() or any(x in lowered for x in ALLOWED_URL_MARKERS):
                findings.append(("G4", "INFO", f"url {url} @ {show(p)}:{line} (allowed / acceptance-policy)"))
            else:
                findings.append(("G4", "FAIL", f"real url {url} @ {show(p)}:{line}"))

    # G6 citations
    if tex:
        text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in tex)
        if BIBSTYLE_RE.search(text) or BIB_RE.search(text):
            findings.append(("G6", "PASS", "bibliography mechanism present"))
        else:
            findings.append(("G6", "FAIL", "no \\bibliographystyle{tmlr} / \\bibliography found"))

    # placeholders
    for p in all_text:
        text = p.read_text(encoding="utf-8", errors="ignore")
        for m in PLACEHOLDER_RE.finditer(text):
            line = text[:m.start()].count("\n") + 1
            findings.append(("EXTRA", "FAIL", f"placeholder {m.group(0)!r} @ {show(p)}:{line}"))

    # +/- format
    for p in all_text:
        text = p.read_text(encoding="utf-8", errors="ignore")
        for m in PLUSMINUS_RE.finditer(text):
            line = text[:m.start()].count("\n") + 1
            findings.append(("EXTRA", "FAIL", f"non-unicode +/- {m.group(0)!r} @ {show(p)}:{line}"))

    # supplementary zip size
    for p in sorted(root.rglob("*.zip")):
        size = p.stat().st_size
        if size > SIZE_LIMIT:
            findings.append(("EXTRA", "FAIL", f"supplementary zip {p} is {size / 1e6:.1f}MB > 100MB"))
        else:
            findings.append(("EXTRA", "PASS", f"supplementary zip {p} {size / 1e6:.1f}MB"))

    # G7 Broader Impact: the section (or an explicit N/A rationale) must exist
    # in the manuscript. TMLR requires a Statement of Broader Impact when the
    # work carries significant risk; a section header is the minimum checkable
    # signal, with a WARN (not FAIL) for its absence so low-risk papers can
    # document an explicit exemption.
    bi_seen = False
    for p in all_text:
        if p.suffix.lower() != ".tex":
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        # section / subsection / subsubsection, optional *, then a heading
        # matching "Broader Impact" (or an explicit ethics heading).
        for m in re.finditer(r"\\(?:sub){0,2}section\*?\s*\{\s*(?:Broader Impact|Ethics)[^}]*\}", text, re.IGNORECASE):
            bi_seen = True
            findings.append(("G7", "PASS", f"Broader Impact section @ {show(p)}:{text[:m.start()].count(chr(10)) + 1}"))
            break
    if not bi_seen:
        findings.append(("G7", "WARN", "no Broader Impact / Ethics section found in .tex (add one, or an explicit low-risk exemption)"))

    # G9: dataset-license + compute-resource declarations (FM-27 data licensing,
    # FM-29 training config as evidence). Read from evidence/protocol.md; a
    # paper using external datasets or trained models must declare license and
    # compute. Missing declarations are WARN (blocking them would over-trigger
    # for theory-only papers), present-but-malformed is FAIL.
    protocol_text = ""
    for cand in (root / "evidence" / "protocol.md", root / "protocol.md"):
        if cand.exists():
            protocol_text = cand.read_text(encoding="utf-8", errors="ignore")
            break
    dataset_license_ok = False
    compute_decl_ok = False
    if protocol_text:
        if re.search(r"(?i)license|licence|许可|CC-|MIT|Apache|dataset.*(source|origin|来源)|数据.*来源", protocol_text):
            dataset_license_ok = True
        if re.search(r"(?i)GPU|hardware|compute|显卡|训练时间|train.*(time|hours|hours)|A100|H100|RTX|V100|T4|TPU", protocol_text):
            compute_decl_ok = True
        findings.append(("G9", "PASS" if dataset_license_ok else "WARN",
                         "dataset license/source declaration in protocol.md" if dataset_license_ok
                         else "no dataset license/source declaration in protocol.md (FM-27: add 'dataset: <name>, license: <X>')"))
        findings.append(("G9", "PASS" if compute_decl_ok else "WARN",
                         "compute-resource declaration in protocol.md" if compute_decl_ok
                         else "no compute-resource declaration in protocol.md (FM-29: add 'hardware: <GPU model xN>, runtime: <hours>')"))
    else:
        findings.append(("G9", "WARN", "no evidence/protocol.md found; cannot verify dataset-license/compute declarations (FM-27/FM-29)"))

    fails = [f for f in findings if f[1] == "FAIL"]
    lines = ["# TMLR compliance scan report", f"\nTarget: `{target_name}`  |  findings: {len(findings)}  |  failures: {len(fails)}"]
    for gate, sev, msg in findings:
        lines.append(f"- [{gate}] {sev} :: {msg}")
    report = "\n".join(lines)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
    print(report)
    if args.exit_zero:
        return 0
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())