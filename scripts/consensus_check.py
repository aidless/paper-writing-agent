"""consensus_check.py - evidence synthesis adjudicator (Consensus-style).

Takes a yes/no research question and a list of arXiv papers (from
literature_discovery.py or manually curated), extracts each paper's stance
toward the question from its abstract, and synthesizes a verdict
(YES / NO / MIXED / INSUFFICIENT) with evidence strength.

The stance extraction is cue-based from abstracts (supportive / contradictory /
neutral), clearly labeled as a screening aid. Manual reading required before
any decision is acted upon.

Usage:
    python consensus_check.py <out.md> --question "Does temperature scaling improve calibration?" --papers 1706.04599,2012.07923
"""
from __future__ import annotations
import argparse
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

API = "http://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom"}

YES_CUES = ["improve", "improves", "effective", "works", "help", "helps", "better",
            "reduce", "reduces", "lower", "outperform", "confirm", "support",
            "consistent", "reliable", "beneficial", "significant"]
NO_CUES = ["not improve", "does not", "cannot", "fail", "fails", "failure", "worse",
           "degrade", "no effect", "ineffective", "unsuitable", "problematic",
           "limitation", "contrary", "unreliable", "overfit", "overfitting"]


def fetch(arxiv_id: str) -> dict:
    url = f"{API}?id_list={arxiv_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "research-agent/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        root = ET.fromstring(r.read())
    e = root.find("atom:entry", NS)
    if e is None:
        return {}
    return {
        "id": arxiv_id,
        "title": re.sub(r"\s+", " ", e.findtext("atom:title", "", NS)).strip(),
        "summary": re.sub(r"\s+", " ", e.findtext("atom:summary", "", NS)).strip(),
    }


def stance(summary: str) -> tuple[str, float]:
    s = summary.lower()
    pos = sum(s.count(c) for c in YES_CUES)
    neg = sum(s.count(c) for c in NO_CUES)
    score = pos - neg
    if score >= 2:
        return "supports", score
    if score <= -2:
        return "contradicts", score
    return "neutral", score


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out", help="output markdown report path")
    ap.add_argument("--question", required=True, help="yes/no research question")
    ap.add_argument("--papers", required=True, help="comma-separated arXiv ids")
    args = ap.parse_args()

    out_path = Path(args.out).resolve()
    ids = [p.strip() for p in args.papers.split(",") if p.strip()]

    rows = []
    supports = contradicts = neutral = 0
    for aid in ids:
        e = fetch(aid)
        if not e:
            continue
        st, score = stance(e["summary"])
        if st == "supports":
            supports += 1
        elif st == "contradicts":
            contradicts += 1
        else:
            neutral += 1
        rows.append((aid, e["title"], st, score))
        time.sleep(0.4)

    total = len(rows)
    if total == 0:
        verdict = "INSUFFICIENT (no papers retrieved)"
    elif supports > 0 and contradicts == 0:
        verdict = "YES"
    elif contradicts > 0 and supports == 0:
        verdict = "NO"
    elif supports == 0 and contradicts == 0:
        verdict = "INSUFFICIENT (all neutral)"
    else:
        verdict = "MIXED"

    strength = "STRONG" if total >= 5 and (supports >= 4 or contradicts >= 4) else \
               ("MODERATE" if total >= 3 else "WEAK")

    lines = [
        "# Consensus check report (Consensus-style)",
        "",
        f"question: `{args.question}`",
        "",
        f"**VERDICT: {verdict}  |  evidence strength: {strength}** "
        f"(support {supports} / contradict {contradicts} / neutral {neutral}, n={total})",
        "",
        "**Method note**: stance extracted from abstracts via sentiment cues; "
        "screening aid only — read the papers before acting.",
        "",
        "| id | Title | Stance | Cue score |",
        "|----|-------|--------|-----------|",
    ]
    for aid, title, st, score in rows:
        lines.append(f"| {aid} | {title[:70].replace('|', '/')} | {st} | {score} |")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"VERDICT: {verdict} ({strength}) -> {out_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
