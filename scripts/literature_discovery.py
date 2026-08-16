"""literature_discovery.py - arXiv semantic discovery (Elicit-style).

Queries the arXiv API for a research question, dedupes, ranks by relevance
to a seed-query fingerprint, and extracts a structured table (title/authors/
year/venue/url/one-line contribution/relevance) into a markdown report.

Usage:
    python literature_discovery.py <out.md> --query "calibration neural networks training-time" [--max 20]

Report paths are rendered RELATIVE to the output file so the report is
byte-identical regardless of cwd / checkout dir (FM-25). The script never
reads its own output (FM-26).
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


def arxiv_search(query: str, max_results: int = 20, retries: int = 3) -> list[dict]:
    params = urllib.parse.urlencode({
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
    })
    url = f"{API}?{params}"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "research-agent/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                root = ET.fromstring(r.read())
            entries = []
            for e in root.findall("atom:entry", NS):
                title = re.sub(r"\s+", " ", e.findtext("atom:title", "", NS)).strip()
                summary = re.sub(r"\s+", " ", e.findtext("atom:summary", "", NS)).strip()
                authors = [a.findtext("atom:name", "", NS).strip()
                           for a in e.findall("atom:author", NS)]
                published = e.findtext("atom:published", "", NS)[:4]
                link = e.findtext("atom:id", "", NS).strip()
                entries.append({
                    "title": title,
                    "authors": authors,
                    "year": published,
                    "url": link,
                    "summary": summary,
                })
            return entries
        except Exception as exc:
            if attempt == retries - 1:
                print(f"arxiv search failed after {retries} tries: {exc}", file=sys.stderr)
                return []
            time.sleep(2 * (attempt + 1))
    return []


def relevance_score(entry: dict, terms: list[str]) -> float:
    text = (entry["title"] + " " * 3 + entry["summary"]).lower()
    hits = sum(text.count(t.lower()) for t in terms)
    title_hits = sum(entry["title"].lower().count(t.lower()) for t in terms)
    return title_hits * 3.0 + hits


def dedupe(entries: list[dict]) -> list[dict]:
    seen, out = set(), []
    for e in entries:
        key = e["title"].lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(e)
    return out


def semantic_scholar_search(query: str, limit: int = 10) -> list[dict]:
    """Fallback source: Semantic Scholar Graph API (no key required for
    basic search). Returns entries in the same shape as arxiv_search."""
    import urllib.request as _ur
    import urllib.parse as _up
    import json as _json
    url = "https://api.semanticscholar.org/graph/v1/paper/search?" + _up.urlencode({
        "query": query, "limit": min(limit, 20),
        "fields": "title,authors,year,externalIds,abstract",
    })
    try:
        req = _ur.Request(url, headers={"User-Agent": "research-agent/1.0"})
        with _ur.urlopen(req, timeout=30) as r:
            data = _json.loads(r.read().decode("utf-8"))
        out = []
        for p in data.get("data", []):
            arxiv_id = (p.get("externalIds") or {}).get("ArXiv", "")
            url_s = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else (
                f"https://www.semanticscholar.org/paper/{p.get('paperId', '')}")
            out.append({
                "title": p.get("title", ""),
                "authors": [a.get("name", "") for a in p.get("authors", [])],
                "year": str(p.get("year", "") or ""),
                "url": url_s,
                "summary": (p.get("abstract") or "")[:300],
            })
        return out
    except Exception as exc:
        print(f"semantic scholar search failed: {exc}", file=sys.stderr)
        return []


def show(rel: str) -> str:
    return rel


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out", help="output markdown report path")
    ap.add_argument("--query", required=True, help="arXiv search query string")
    ap.add_argument("--terms", default="", help="comma-separated relevance terms")
    ap.add_argument("--max", type=int, default=20)
    args = ap.parse_args()

    out_path = Path(args.out).resolve()
    terms = [t.strip() for t in args.terms.split(",") if t.strip()] or \
            [t.strip() for t in args.query.split() if len(t.strip()) > 3]

    entries = dedupe(arxiv_search(args.query, args.max))
    # Multi-source fallback (Modex scholar_fetch design): if arXiv returns
    # nothing useful, try Semantic Scholar Graph API.
    if len(entries) < 3:
        extra = semantic_scholar_search(args.query, args.max)
        entries = dedupe(entries + extra)
    for e in entries:
        e["score"] = relevance_score(e, terms)
    entries.sort(key=lambda e: -e["score"])

    lines = [
        "# Literature discovery report",
        "",
        f"query: `{args.query}`  |  terms: {', '.join(terms)}  |  results: {len(entries)}",
        "",
        "| # | Title | Authors | Year | Venue/URL | Contribution | Relevance |",
        "|---|-------|---------|------|-----------|--------------|-----------|",
    ]
    for i, e in enumerate(entries, 1):
        authors = ", ".join(e["authors"][:4]) + (" et al." if len(e["authors"]) > 4 else "")
        contrib = e["summary"][:140].replace("|", "/").replace("\n", " ")
        lines.append(f"| {i} | {e['title'][:80].replace('|', '/')} | {authors} | "
                     f"{e['year']} | {e['url'].replace('http://arxiv.org/abs/', '')} | "
                     f"{contrib}... | {e['score']:.1f} |")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {len(entries)} entries -> {show(out_path.name)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
