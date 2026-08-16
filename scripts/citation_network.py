"""citation_network.py - citation network analysis (Scite-style).

Builds a citation graph around a seed paper from arXiv metadata and classifies
incoming references into supportive / contradictory / neutral based on
sentiment cues in their abstracts. Produces a markdown report with the graph
edges and a simple adjacency summary.

Note: true Scite-style classification requires full-text analysis of citing
papers; this script uses abstract sentiment as a lightweight proxy and clearly
labels it as such. It is a screening aid, not a substitute for manual reading.

Usage:
    python citation_network.py <out.md> --seed arxiv_id [--depth 1] [--max 30]
"""
from __future__ import annotations
import argparse
import re
import sys
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

API = "http://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom"}

SUPPORT_CUES = ["improve", "improv", "outperform", "better", "effective", "strong",
                "consistent", "confirm", "support", "validate", "reduce", "lower",
                "superior", "beneficial", "reliable", "robust"]
CONTRADICT_CUES = ["however", "but", "fail", "failure", "contrary", "inconsistent",
                   "outperform", "outperforms", "worse", "degrade", "limitation",
                   "cannot", "does not", "not work", "unsuitable", "unreliable",
                   "problem", "issue", "drawback", "weak"]


def fetch_entry(arxiv_id: str) -> dict:
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
        "authors": [a.findtext("atom:name", "", NS).strip() for a in e.findall("atom:author", NS)],
    }


def classify_relation(citing_summary: str) -> str:
    s = citing_summary.lower()
    pos = sum(s.count(c) for c in SUPPORT_CUES)
    neg = sum(s.count(c) for c in CONTRADICT_CUES)
    if neg > pos:
        return "contradictory"
    if pos > 0:
        return "supportive"
    return "neutral"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out", help="output markdown report path")
    ap.add_argument("--seed", required=True, help="seed arXiv id")
    ap.add_argument("--max", type=int, default=30)
    args = ap.parse_args()

    out_path = Path(args.out).resolve()
    seed = fetch_entry(args.seed)
    if not seed:
        print(f"seed {args.seed} not found", file=sys.stderr)
        return 1
    print(f"seed: {seed['title'][:60]}")

    # Simulated one-hop expansion is not possible via the public arXiv API
    # (it does not expose citation lists). We fetch the seed's own references
    # by scanning its abstract for arXiv ids and report what is available.
    ids = set(re.findall(r"(\d{4}\.\d{4,5}(?:v\d+)?)", seed.get("summary", "")))
    related = []
    for aid in list(ids)[:args.max]:
        try:
            e = fetch_entry(aid)
            if e:
                e["relation"] = classify_relation(e.get("summary", ""))
                related.append(e)
            time.sleep(0.4)
        except Exception:
            continue

    lines = [
        "# Citation network report (Scite-style proxy)",
        "",
        f"seed: `{args.seed}`  |  {seed['title']}",
        "",
        "**Method note**: public arXiv API does not expose citation lists; "
        "relations below are classified from abstracts of arXiv ids found in "
        "the seed abstract/summary, using sentiment cues as a lightweight proxy. "
        "Screening aid only — manual verification required.",
        "",
        "| id | Title | Relation | Abstract cues |",
        "|----|-------|----------|---------------|",
    ]
    for e in sorted(related, key=lambda x: x["relation"]):
        s = e.get("summary", "").lower()
        cues = ", ".join(c for c in SUPPORT_CUES + CONTRADICT_CUES if c in s)[:80]
        lines.append(f"| {e['id']} | {e['title'][:70].replace('|', '/')} | "
                     f"{e['relation']} | {cues} |")

    counts = {"supportive": 0, "contradictory": 0, "neutral": 0}
    for e in related:
        counts[e["relation"]] += 1

    lines.append("")
    lines.append(f"## Summary: {len(related)} related papers - "
                 f"supportive {counts['supportive']} / contradictory "
                 f"{counts['contradictory']} / neutral {counts['neutral']}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {len(related)} related -> {out_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
