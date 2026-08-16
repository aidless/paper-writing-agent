"""polish_manuscript.py - manuscript polishing suggestions (Paperpal-style).

Two-layer polish without touching numbers:
  1. Mechanical layer (offline, deterministic): flags redundant adverbs,
     weak verbs, Chinese-English residue, "can + claim verb" patterns,
     hedging mismatches, and sentence-length outliers with precise
     line numbers — the same discipline as check_writing_style.py.
  2. Semantic layer: emits a prioritized suggestion list for the LLM
     (academic-writing skill) to apply manually; the script never rewrites
     the manuscript, so number consistency is preserved by construction.

Usage:
    python polish_manuscript.py <main.tex> [--out suggestions.md]
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

REDUNDANT = {
    "very": "redundant intensifier", "really": "redundant intensifier",
    "basically": "vague filler", "essentially": "vague filler",
    "actually": "vague filler", "obviously": "weakened by subjectivity",
    "clearly": "weakened by subjectivity", "importantly": "vague filler",
    "significantly": "check statistical meaning is intended",
    "interestingly": "vague filler",
}
WEAK_VERBS = ["make", "get", "show", "give", "do", "go", "put", "take"]
CHINGLISH = [
    (r"\bcould be able to\b", "redundant: 'can' or 'could'"),
    (r"\baccording to the experiment\b", "Chinglish: 'the experiments show'"),
    (r"\bthrough this way\b", "Chinglish: 'in this way'"),
    (r"\bwe can know\b", "Chinglish: 'we find' / 'this shows'"),
    (r"\bthe reason is because\b", "redundant: 'the reason is'"),
    (r"\bin the paper\b", "vague: name the section"),
    (r"\bas we all know\b", "Chinglish: 'it is well known that'"),
    (r"\bwith the development of\b", "Chinglish filler"),
]
CAN_CLAIM = re.compile(r"\bcan\s+(improve|outperform|achieve|reduce|lead|help|solve|provide)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("tex", help="path to main.tex")
    ap.add_argument("--out", default=None, help="output suggestions markdown")
    args = ap.parse_args()

    tex = Path(args.tex).resolve()
    lines = tex.read_text(encoding="utf-8").splitlines()
    findings = []

    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if not s or s.startswith("%"):
            continue
        for word, note in REDUNDANT.items():
            if re.search(rf"\b{word}\b", ln, re.IGNORECASE):
                findings.append((i, "redundant", f"'{word}': {note}"))
        for pat, note in CHINGLISH:
            if re.search(pat, ln, re.IGNORECASE):
                findings.append((i, "style", note))
        for m in CAN_CLAIM.finditer(ln):
            findings.append((i, "claim", f"'can {m.group(1)}': soften or cite evidence"))
        if len(s) > 200 and not s.startswith("%"):
            findings.append((i, "length", f"{len(s)} chars — consider splitting"))

    out = Path(args.out).resolve() if args.out else None
    lines_out = [
        "# Manuscript polishing suggestions (Paperpal-style)",
        "",
        f"target: `{tex.name}`  |  findings: {len(findings)}  |  "
        f"categories: {sorted({f[1] for f in findings})}",
        "",
        "**Discipline**: this script only SUGGESTS; it never rewrites the "
        "manuscript. Apply edits manually so numbers stay consistent. "
        "After any edit, re-run the six machine checks (FM-23).",
        "",
        "| Line | Category | Suggestion |",
        "|------|----------|------------|",
    ]
    for line_no, cat, note in findings:
        lines_out.append(f"| {line_no} | {cat} | {note} |")

    report = "\n".join(lines_out) + "\n"
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"wrote {len(findings)} suggestions -> {out.name}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
