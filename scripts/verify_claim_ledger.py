"""paper-writing-agent: claim-ledger verifier.

Parses CLAIM_LEDGER.md and verifies every entry:
  - evidence file exists and JSON parses,
  - dot-path field resolves to a value,
  - numeric value in the entry matches the evidence value (within tolerance),
  - numbers in manuscript text without any ledger coverage (informational).

Evidence reference format in the ledger:
  results/e1.json -> gTV.mean / gTV.sd      (one file, several fields)
  results/e1.json -> gTV.mean; other.json -> x  (several files, ';' separated)

Usage:
  python verify_claim_ledger.py <paper_dir> [--ledger CLAIM_LEDGER.md] [--out report.md] [--exit-zero]

Exit 0 = all entries PASS (or --exit-zero); exit 1 = at least one FAIL.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

ROW_RE = re.compile(r"^\|\s*(C\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$")
NUM_RE = re.compile(r"[-+]?\d+\.\d+")
VALUE_NUM_RE = re.compile(r"[-+]?\d+(?:\.\d+)?")
TEXT_SUFFIX = {".tex", ".md", ".txt"}
TOL = 2e-5
DEFAULT_EXCLUDE = {"reports", ".git", "__pycache__", "node_modules"}
# R21/R30: verification scaffolding immunity (same as scan_number_consistency).
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


def strip_cell(s: str) -> str:
    return s.replace("`", "").strip()


def split_path(path: str):
    """Split a dotted path, honoring quoted bracket segments containing dots/pipes."""
    parts, cur = [], []
    in_bracket = False
    for ch in path:
        if ch == "[":
            if cur:
                parts.append("".join(cur)); cur = []
            continue
        if ch == '"':
            in_bracket = not in_bracket
            continue
        if ch == "." and not in_bracket:
            if cur:
                parts.append("".join(cur)); cur = []
            continue
        if ch == "]":
            continue
        cur.append(ch)
    if cur:
        parts.append("".join(cur))
    return parts


def resolve(obj, path: str):
    """Resolve a path whose keys may contain dots (qwen3.7-plus-...) or pipes (a|b|c).

    Supports: literal whole-key match, dotted traversal, [index] on lists, and
    quoted bracket segments: per_cell_mean["deepseek-v4-pro|Summ|auth|p0.8"].mean
    """
    if isinstance(obj, dict) and path in obj:
        return obj[path]
    rest = path
    while rest:
        if isinstance(obj, dict):
            if rest in obj:
                return obj[rest]
            found = None
            for i in range(len(rest) - 1, 0, -1):
                if rest[i] == "." and rest[:i] in obj:
                    found = rest[:i]
                    break
            if found is not None:
                obj = obj[found]
                rest = rest[len(found) + 1:]
                continue
            # bracket-aware segment parsing: per_cell_mean["a|b|c"].mean
            segs = split_path(rest)
            if segs and segs[0] in obj:
                obj = obj[segs[0]]
                rest = ".".join(segs[1:])
                continue
            return None
        if isinstance(obj, list):
            m = re.match(r"^\[?(\d+)\]?", rest)
            if not m:
                return None
            try:
                obj = obj[int(m.group(1))]
            except (IndexError, TypeError):
                return None
            rest = rest[m.end():].lstrip(".")
            continue
        return None
    return obj

def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def verify_ref(root: Path, ref: str):
    """Return (ok, message, resolved_values)."""
    ref = strip_cell(ref)
    if "->" in ref:
        path_s, fields_s = (p.strip() for p in ref.split("->", 1))
    elif ":" in ref and ref.count(":") == 1 and not ref.startswith("http"):
        path_s, fields_s = (p.strip() for p in ref.split(":", 1))
    else:
        path_s, fields_s = ref, ""
    p = root / path_s
    if not p.exists():
        return False, f"missing file {path_s}", []
    if p.suffix.lower() not in {".json"}:
        return True, f"file {path_s} exists (non-JSON)", []
    data = load_json(p)
    if data is None:
        return False, f"unparseable JSON {path_s}", []
    if not fields_s:
        return True, f"file {path_s} ok (no field)", []
    values = []
    fields = [f.strip() for f in fields_s.split(" / ") if f.strip()]
    for field in fields:
        val = resolve(data, field)
        if val is None:
            return False, f"field {field!r} not found in {path_s}", []
        values.append(val)
    return True, f"{path_s} -> {' / '.join(fields)} = {values}", values


PROCESS_DOC_PREFIXES = ("ROUND_R", "REVIEW_R", "SELF_ASSESSMENT")
PROCESS_DOC_SUFFIXES = (".summary.md", "_R7_ethics.md")


def is_process_doc(name: str) -> bool:
    """Process/audit documents (round reports, review summaries, self
    assessment) are NOT paper content. They grow and change every review
    round; including them makes the report depend on review history and never
    reach a fixed point (FM-26/R13/R14)."""
    if name.startswith(PROCESS_DOC_PREFIXES):
        return True
    return name.endswith(PROCESS_DOC_SUFFIXES)


def numbers_in_text(root: Path, exclude, exclude_names):
    vals: set[str] = set()
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in TEXT_SUFFIX:
            parts = p.relative_to(root).parts
            if is_excluded_path(p, exclude):
                continue
            if any(sub in p.name for sub in exclude_names):
                continue
            if is_process_doc(p.name):
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
            for m in NUM_RE.finditer(text):
                vals.add(m.group(0))
    return vals


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", help="paper directory (--selftest ignores)")
    ap.add_argument("--ledger", default="CLAIM_LEDGER.md")
    ap.add_argument("--out", default=None)
    ap.add_argument("--exit-zero", action="store_true", help="report only, always exit 0")
    ap.add_argument("--exclude-dir", default="reports,.git,__pycache__,node_modules,tmp",
                    help="comma-separated directory names to exclude")
    ap.add_argument("--exclude-name", default="", help="comma-separated filename substrings to exclude")
    ap.add_argument("--selftest", action="store_true", help="run selftest and exit")
    args = ap.parse_args()

    if args.selftest:
        # D2: 注入坏 ledger(缺文件/缺字段/值不匹配)与好 ledger, 断言检出
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "results").mkdir()
            (root / "results" / "e1.json").write_text(
                '{"gTV": {"mean": 29.4, "sd": 0.4}}', encoding="utf-8")
            bad = ("| ID | 声明 | 证据文件+字段 | 数值 | 如何验证 | 状态 |\n"
                   "|---|---|---|---|---|---|\n"
                   "| C01 | ok claim | results/e1.json -> gTV.mean | 29.4 | recompute | verified |\n"
                   "| C02 | missing file | nofile.json -> x | 1.0 | recompute | verified |\n"
                   "| C03 | mismatch | results/e1.json -> gTV.mean | 99.9 | recompute | verified |\n")
            (root / "CLAIM_LEDGER.md").write_text(bad, encoding="utf-8")
            fails, passes = 0, 0
            for line in (root / "CLAIM_LEDGER.md").read_text(encoding="utf-8").splitlines():
                m = ROW_RE.match(line.replace("\\|", "\u0001"))
                if not m:
                    continue
                cid, claim, evref, values, method, status = (
                    strip_cell(x).replace("\u0001", "|") for x in m.groups())
                if cid.lower().startswith("id") or "template" in status.lower():
                    continue
                ok_all, msgs, resolved = True, [], []
                for ref in evref.split(";"):
                    ref = ref.strip()
                    if not ref:
                        continue
                    ok, msg, vals = verify_ref(root, ref)
                    if not ok:
                        ok_all = False
                    msgs.append(msg)
                    for v in vals:
                        if isinstance(v, (int, float)) and not isinstance(v, bool):
                            resolved.append(float(v))
                if ok_all and resolved:
                    want = [float(x) for x in VALUE_NUM_RE.findall(values)]
                    missing = [b for b in want
                               if not any(abs(a - b) <= max(TOL, TOL * abs(b)) for a in resolved)]
                    if missing:
                        ok_all = False
                        msgs.append(f"value mismatch: claimed {missing}")
                if ok_all:
                    passes += 1
                else:
                    fails += 1
            ok = (passes == 1 and fails == 2)
            print(f"selftest: {passes} PASS / {fails} FAIL entries (expect 1/2): "
                  f"{'PASS' if ok else 'FAIL'}")
            return 0 if ok else 1

    if not args.target:
        ap.error("target required (or use --selftest)")
    root = Path(args.target)
    exclude = set(DEFAULT_EXCLUDE) | {s.strip() for s in args.exclude_dir.split(",") if s.strip()}
    exclude_names = [s.strip() for s in args.exclude_name.split(",") if s.strip()]
    ledger_path = root / args.ledger
    if not ledger_path.exists():
        print(f"FAIL missing ledger: {ledger_path}")
        return 1

    # Path rendered relative to the target root so reports are byte-reproducible
    # regardless of invocation cwd (FM-24/R11).
    try:
        ledger_display = ledger_path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        ledger_display = ledger_path.name
    lines_out = ["# Claim ledger verification report", f"\nLedger: `{ledger_display}`"]
    fails, passes, warnings = 0, 0, 0
    ledger_vals: set[str] = set()

    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        # protect escaped pipes (\\|) from table-column splitting, restore later
        guarded = line.replace("\\|", "\u0001")
        m = ROW_RE.match(guarded)
        if not m:
            continue
        cid, claim, evref, values, method, status = (strip_cell(x).replace("\u0001", "|") for x in m.groups())
        if cid.lower().startswith("id") or "template" in status.lower() or "example" in status.lower():
            continue
        ledger_vals.update(VALUE_NUM_RE.findall(values))
        is_inconclusive = "inconclusive" in status.lower()
        ok_all, msgs = True, []
        resolved = []
        if is_inconclusive:
            # E095: inconclusive is the explicit no-evidence outlet (SciAgentArena C5):
            # entry stays in the ledger, counts as WARN not FAIL, and the
            # "how to verify" cell (column 5) must name the missing evidence (failure mode).
            # Evidence references are intentionally NOT verified for inconclusive
            # entries -- that is the point: the claim is held without evidence.
            warnings += 1
            method_col = strip_cell(m.group(5))
            msgs.append("INCONCLUSIVE status - needs hedge wording in prose + named missing evidence (evidence not verified by design)")
            if len(method_col) < 10:
                msgs.append("WARN: inconclusive entry should name the missing evidence / upgrade condition")
        else:
            for ref in evref.split(";"):
                ref = ref.strip()
                if not ref:
                    continue
                ok, msg, vals = verify_ref(root, ref)
                if not ok:
                    ok_all = False
                msgs.append(msg)
                for v in vals:
                    if isinstance(v, (int, float)) and not isinstance(v, bool):
                        resolved.append(float(v))
            if ok_all and resolved:
                want = [float(x) for x in VALUE_NUM_RE.findall(values)]
                # ALL-match semantics: every claimed value must be traceable to a
                # resolved evidence value. A single unmatched claim (e.g. a stale
                # CI endpoint) fails the entry. TOL is tight (half a unit in the
                # 4th decimal) so drifted endpoints like 0.0275 vs 0.0274 are
                # caught instead of hidden by a loose tolerance.
                missing = [b for b in want
                           if not any(abs(a - b) <= max(TOL, TOL * abs(b)) for a in resolved)]
                if missing:
                    ok_all = False
                    msgs.append(f"value mismatch: claimed {missing} not in evidence {resolved}")
        if "blocked" in status.lower() and not is_inconclusive:
            warnings += 1
            msgs.append("BLOCKED status - keep out of manuscript")
        if ok_all or is_inconclusive:
            passes += 1
            lines_out.append(f"- PASS {cid}: {claim[:70]} :: {'; '.join(msgs)}")
        else:
            fails += 1
            lines_out.append(f"- FAIL {cid}: {claim[:70]} :: {'; '.join(msgs)}")

    text_vals = numbers_in_text(root, exclude, exclude_names)
    uncovered = sorted(v for v in text_vals if v not in ledger_vals)
    lines_out.append(f"\n## Summary: {passes} PASS, {fails} FAIL, {warnings} WARN")
    lines_out.append("\n## Inconclusive entries (hedge + name missing evidence): "
                     f"{sum(1 for l in lines_out if 'INCONCLUSIVE status' in l)}")
    lines_out.append(f"\n## Numeric literals in text without any ledger value: {len(uncovered)}")
    lines_out.append(", ".join(uncovered[:80]))

    report = "\n".join(lines_out)
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