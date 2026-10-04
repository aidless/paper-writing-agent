#!/usr/bin/env python3
"""SCRIPTS.md generator: rebuild the script index from docstring first lines."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HEAD = (
    "# SCRIPTS.md — 脚本全索引（自动生成）\n\n"
    "> 由 `scripts/` 下各文件的 docstring 首行自动生成。用法细节以 `python scripts/<name>.py --help` 为准。\n"
)


def main() -> int:
    rows = []
    for p in sorted((ROOT / "scripts").glob("*.py")):
        if p.name == "__init__.py":
            continue
        m = re.search(r'"""(.+?)("""|$)', p.read_text(encoding="utf-8"), re.S)
        doc = (m.group(1).strip().splitlines()[0] if m and m.group(1).strip() else "(no docstring)")
        # 剥与文件名重复的前缀（如 'compile_gate.py — '）
        doc = re.sub(rf"^{re.escape(p.stem)}\s*[:：\-—]+\s*", "", doc).strip()
        rows.append(f"| `{p.name}` | {doc} |")
    tbl = HEAD + "\n| 脚本 | 用途 |\n|---|---|\n" + "\n".join(rows) + "\n"
    out = ROOT / "SCRIPTS.md"
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        print("OK: SCRIPTS.md in sync" if out.read_text(encoding="utf-8") == tbl
              else f"FAIL: SCRIPTS.md out of sync — run: python3 scripts/{Path(__file__).name}")
        return 0 if out.read_text(encoding="utf-8") == tbl else 1
    out.write_text(tbl, encoding="utf-8")
    print(f"SCRIPTS.md regenerated ({len(rows)} scripts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
