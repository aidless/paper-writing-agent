#!/usr/bin/env python3
"""FM index generator: parse references/failure-modes.md headings into the INDEX section.

Usage:
  python scripts/fm_index.py --check     # CI mode: exit 1 if INDEX out of sync
  python scripts/fm_index.py --write     # regenerate INDEX in place
  python scripts/fm_index.py             # print index to stdout

Rules (see references/failure-modes.md FM 入库协议):
  - Heading form: '## FM-<N> <title>'
  - INDEX section is delimited by '## INDEX' ... (next '## ' heading or EOF)
  - Each index line: '| FM-N | title |'
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FM = ROOT / "references" / "failure-modes.md"
HEAD = "## INDEX（由 scripts/fm_index.py 自动生成，勿手改）"
ROW_RE = re.compile(r"^## (FM-\d+) (.+?)\s*$", re.M)


def parse(text: str):
    entries = [(m.group(1), m.group(2)) for m in ROW_RE.finditer(text)]
    return entries


def render(entries) -> str:
    lines = [HEAD, "", "| 编号 | 一句话标题 |", "|---|---|"]
    lines += [f"| {n} | {t} |" for n, t in entries]
    lines.append("")
    return "\n".join(lines)


def section_bounds(text: str):
    start = text.find(HEAD)
    if start == -1:
        return None
    nxt = text.find("\n## ", start + len(HEAD))
    end = len(text) if nxt == -1 else nxt + 1
    return start, end


def main() -> int:
    text = FM.read_text(encoding="utf-8")
    entries = parse(text)
    idx = render(entries)
    bounds = section_bounds(text)
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "--check":
        if bounds is None:
            print("FAIL: INDEX section missing")
            return 1
        cur = text[bounds[0]:bounds[1]].rstrip()
        want = idx.rstrip()
        if cur != want:
            print(f"FAIL: INDEX out of sync ({len(entries)} entries) — run: make fm-index")
            return 1
        print(f"OK: INDEX in sync ({len(entries)} entries)")
        return 0
    if mode == "--write":
        if bounds is None:
            # insert protocol-style INDEX right before first FM heading
            first = text.find("\n## FM-1 ")
            assert first != -1, "FM-1 not found"
            text = text[:first] + "\n" + idx + text[first:]
        else:
            s, e = bounds
            text = text[:s] + idx + text[e:]
        FM.write_text(text, encoding="utf-8")
        print(f"written: INDEX regenerated ({len(entries)} entries)")
        return 0
    print(idx)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
