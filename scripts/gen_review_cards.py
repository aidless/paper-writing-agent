"""gen_review_cards.py - generate deepseek-eyes review cards for all PDF pages
with tables/figures, ready for the R8 figures reviewer role.

Scans the PDF page count (via pdfinfo if available, else estimates from
pdftotext), and runs describe_image.py on each page. The main agent picks
the table/figure pages (usually table pages and result figures) and passes
the cards into the adversarial-review workflow as args.reviewCard.

Usage:
    python gen_review_cards.py <main.pdf> --out <cards_dir> [--pages 2,3]
"""
from __future__ import annotations
import argparse
import subprocess
import sys
import os
from pathlib import Path

DESCRIBE = Path(os.environ.get(
    "PWA_DESCRIBE_SCRIPT",
    Path.home() / ".agents" / "skills" / "deepseek-eyes" / "scripts" / "describe_image.py",
))


def pdf_pages(pdf: Path) -> int:
    try:
        r = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, timeout=30)
        for line in r.stdout.splitlines():
            if line.lower().startswith("pages:"):
                return int(line.split(":")[1].strip())
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", help="path to main.pdf")
    ap.add_argument("--out", required=True, help="output cards directory")
    ap.add_argument("--pages", default="", help="comma-separated 0-based page indices; default: all")
    args = ap.parse_args()

    pdf = Path(args.pdf).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    pages = pdf_pages(pdf)
    if not pages:
        print("cannot determine page count (pdfinfo missing); pass --pages explicitly")
        return 1
    if args.pages:
        targets = [int(x) for x in args.pages.split(",") if x.strip()]
    else:
        targets = list(range(pages))
    print(f"{pdf.name}: {pages} pages, generating cards for {len(targets)} pages")

    for pg in targets:
        card = out / f"card_p{pg}.md"
        r = subprocess.run([sys.executable, str(DESCRIBE), "--image", str(pdf),
                            "--page", str(pg), "--mode", "paper", "--output", str(card)],
                           capture_output=True, timeout=300)
        ok = r.returncode == 0 and card.exists()
        print(f"  page {pg}: {'OK' if ok else 'FAIL'}")
        if not ok:
            print(r.stderr.decode("utf-8", errors="replace")[:300])
    print(f"cards -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
