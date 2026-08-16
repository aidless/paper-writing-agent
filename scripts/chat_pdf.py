"""chat_pdf.py - lightweight Chat-with-PDF (SciSpace-style, offline).

Extracts text from a PDF (via pdftotext if available), splits it into
numbered chunks, and answers questions with cited chunk references using a
simple keyword/overlap retriever. No external embeddings needed.

Usage:
    python chat_pdf.py <paper.pdf> --ask "what is the ECE of temperature scaling?" [--chunk 400]
    python chat_pdf.py <paper.pdf> --index                      # just build the chunk index

Output is a markdown report (or console answer) with cited chunk numbers so
the user can verify against the source page.
"""
from __future__ import annotations
import argparse
import re
import subprocess
import sys
from pathlib import Path


def pdf_to_text(pdf: Path) -> str:
    """Extract text via pdftotext (poppler). Raises if unavailable."""
    try:
        r = subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf), "-"],
                           capture_output=True, timeout=120)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.decode("utf-8", errors="replace")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    raise RuntimeError("pdftotext not available or produced no text "
                      "(install poppler-utils)")


def chunk_text(text: str, size: int = 400, overlap: int = 40) -> list[str]:
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if len(cur) + len(p) > size and cur:
            chunks.append(cur)
            cur = p[:overlap] + " "
            cur += p
        else:
            cur += p + " "
    if cur.strip():
        chunks.append(cur)
    return chunks


def retrieve(query: str, chunks: list[str], k: int = 3) -> list[tuple[int, str, float]]:
    q_terms = [t.lower() for t in re.findall(r"[a-zA-Z0-9]+", query) if len(t) > 2]
    scored = []
    for i, c in enumerate(chunks):
        c_low = c.lower()
        score = sum(c_low.count(t) for t in q_terms)
        # penalty for section headers / boilerplate
        if "references" in c_low[:200]:
            score *= 0.5
        if score > 0:
            scored.append((i, c, score))
    scored.sort(key=lambda x: -x[2])
    return scored[:k]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", help="path to PDF")
    ap.add_argument("--ask", default=None, help="question to answer")
    ap.add_argument("--chunk", type=int, default=400)
    ap.add_argument("--k", type=int, default=3)
    args = ap.parse_args()

    pdf = Path(args.pdf).resolve()
    if not pdf.exists():
        print(f"PDF not found: {pdf}", file=sys.stderr)
        return 1
    text = pdf_to_text(pdf)
    chunks = chunk_text(text, args.chunk)

    if not args.ask:
        print(f"{pdf.name}: {len(chunks)} chunks, {len(text)} chars")
        return 0

    hits = retrieve(args.ask, chunks, args.k)
    if not hits:
        print(f"No relevant chunk found for: {args.ask}")
        print("(try different wording — this is a keyword retriever, not semantic)")
        return 0

    print(f"Q: {args.ask}\n")
    for i, c, score in hits:
        snippet = re.sub(r"\s+", " ", c)[:300]
        print(f"[chunk {i} | score {score:.0f}]\n  {snippet}\n")
    print(f"(k={len(hits)} of {len(chunks)} chunks — verify against source)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
