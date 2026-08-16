"""gate_reflection.py — Reflexion 式反思注入(科研论文 agent Phase 4 改造)。

机制(Reflexion + MISSION 纪律):
  run_acceptance_gates.py --record gates_history.jsonl 持续追加每次 gate 运行;
  本脚本扫描历史尾部,检测"同一 gate 连续 FAIL >= N 轮"的卡死门禁,
  产出一段结构化反思(Reflexion 缓冲 → 注入下一轮 ROUND 报告),指示修复路径;
  连续失败达到上限仍 FAIL → 升级用户(调整验收标准/跳过/中止,绝不静默无限重试)。

用法:
  python scripts/gate_reflection.py --history gates_history.jsonl \
      --consecutive 2 --max-consecutive 3 --out ROUND_Rn_reflection.md
  python scripts/gate_reflection.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_history(path: str | Path) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def detect_stuck(rows: list[dict], consecutive: int) -> list[dict]:
    """返回卡死门禁:[{name, fail_streak, last_ts, n_records}]。

    对每个 check 名,从历史尾部数连续 FAIL 轮数。
    expected_fail 门(设计性阻断,如 D3 证据未产出)不参与卡死检测——
    它们按设计持续 FAIL,不应触发 Reflexion 注入(配置见 run_acceptance_gates
    的 "expected_fail": true;旧记录无 expected 字段按非 expected 处理)。
    """
    by_name: dict[str, list[bool]] = {}
    for r in rows:
        for c in r.get("checks", []):
            if c.get("expected"):
                # 设计性阻断: 不计入连击, 且重置既有连击(标注后的最新语义为准;
                # 兼容标注前的旧历史——旧记录无 expected 字段按实际 passed 计入)
                by_name.setdefault(c.get("name", "?"), []).append(True)
            else:
                by_name.setdefault(c.get("name", "?"), []).append(bool(c.get("passed", False)))
    stuck = []
    for name, flags in by_name.items():
        streak = 0
        for f in reversed(flags):
            if f:
                break
            streak += 1
        if streak >= consecutive:
            last_ts = None
            for r in reversed(rows):
                if any(c.get("name") == name and not c.get("passed") for c in r.get("checks", [])):
                    last_ts = r.get("ts")
                    break
            stuck.append({"name": name, "fail_streak": streak,
                          "last_ts": last_ts, "n_records": len(flags)})
    return sorted(stuck, key=lambda s: -s["fail_streak"])


def render_reflection(stuck: list[dict], consecutive: int, max_consecutive: int) -> str:
    if not stuck:
        return ""
    lines = [
        "# Gate Reflection(Reflexion 注入块)",
        "",
        f"> 检测: 以下门禁连续 FAIL ≥ {consecutive} 轮(上限 {max_consecutive} 轮后升级用户)。",
        "> 处置: 先修复根因再改门;禁止为了过门而修改 gate 本身或验收标准。",
        "",
        "## 卡死门禁",
        "",
    ]
    for s in stuck:
        escalate = s["fail_streak"] >= max_consecutive
        lines += [
            f"### {s['name']}",
            f"- 连续 FAIL: {s['fail_streak']} 轮(共 {s['n_records']} 次记录)"
            + (f";最近一次: {s['last_ts']}" if s.get("last_ts") else ""),
            f"- 处置: {'**升级用户**(调整验收标准/跳过/中止,附 3 次纠正日志)' if escalate else '修复根因后重跑;本轮先输出失败证据与修复计划'}",
            "- 反捕获纪律: 若失败源于环境/工具瞬时问题,不得硬化为持久约束;先验证可复现再修",
            "",
        ]
    lines += [
        "## 注入下一轮",
        "- 把本节复制到 ROUND_R{n+1} 开头,按卡死门禁逐条: 复现失败 → 修复(改技能/配置/证据) → 重跑 gate → 记录到 GATES 日志",
        "- 连续失败达上限仍 FAIL → 升级用户,给选项(调整验收标准/跳过/中止),绝不静默无限重试",
    ]
    return "\n".join(lines)


def selftest() -> bool:
    import tempfile
    rows = []
    for i in range(1, 4):  # 3 轮历史
        rows.append({
            "ts": f"2026-08-15T00:0{i}:00", "config_sha256": "abc",
            "checks": [
                {"name": "four-scans-pass", "passed": True},
                {"name": "manifest-verified", "passed": i <= 1},  # 后 2 轮连续 FAIL
                {"name": "no-unreconciled", "passed": True},
            ],
        })
    stuck = detect_stuck(rows, consecutive=2)
    names = [s["name"] for s in stuck]
    assert names == ["manifest-verified"], names
    assert stuck[0]["fail_streak"] == 2, stuck
    text = render_reflection(stuck, 2, 3)
    assert "manifest-verified" in text and "**升级用户**" not in text, text
    # 达上限 → 升级
    rows.append({"ts": "2026-08-15T00:04:00", "config_sha256": "abc",
                 "checks": [{"name": "manifest-verified", "passed": False}]})
    stuck2 = detect_stuck(rows, consecutive=2)
    text2 = render_reflection(stuck2, 2, 3)
    assert "升级用户" in text2, text2
    print("[gate_reflection] consecutive-FAIL 检测 + 升级阈值 ✓")
    # expected_fail 门(设计性阻断)不触发卡死检测;且标注会重置既有连击——
    # "曾经真实 FAIL ×2 → 标注 expected ×2" 后不得再判卡死(最新语义为准)
    rows.append({"ts": "2026-08-15T00:05:00", "config_sha256": "abc",
                 "checks": [{"name": "evidence-pending", "passed": False}]})
    rows.append({"ts": "2026-08-15T00:06:00", "config_sha256": "abc",
                 "checks": [{"name": "evidence-pending", "passed": False}]})
    stuck3 = detect_stuck(rows, consecutive=2)
    assert "evidence-pending" in [s["name"] for s in stuck3], stuck3  # 标注前: 卡死
    rows.append({"ts": "2026-08-15T00:07:00", "config_sha256": "abc",
                 "checks": [{"name": "evidence-pending", "passed": False, "expected": True}]})
    rows.append({"ts": "2026-08-15T00:08:00", "config_sha256": "abc",
                 "checks": [{"name": "evidence-pending", "passed": False, "expected": True}]})
    stuck4 = detect_stuck(rows, consecutive=2)
    assert "evidence-pending" not in [s["name"] for s in stuck4], stuck4  # 标注后: 连击重置
    assert "manifest-verified" in [s["name"] for s in stuck4], stuck4  # 非 expected 门仍检出
    print("[gate_reflection] expected_fail 门不触发卡死检测 + 标注重置连击 ✓")
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "gates_history.jsonl"
        for r in rows:
            p.open("a", encoding="utf-8").write(json.dumps(r) + "\n")
        assert load_history(p) == rows
    print("[gate_reflection] history load ✓")
    return True


def main() -> int:
    # GBK 控制台无法编码 ✓ 等 UTF-8 字符(selftest 输出会崩);与族内脚本一致强制 UTF-8
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Reflexion 式 gate 反思注入")
    ap.add_argument("--history", default="gates_history.jsonl")
    ap.add_argument("--consecutive", type=int, default=2, help="连续 FAIL 轮数阈值")
    ap.add_argument("--max-consecutive", type=int, default=3, help="达到后升级用户")
    ap.add_argument("--out", default="")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return 0 if selftest() else 1
    rows = load_history(args.history)
    if not rows:
        print("history 为空: 先 run_acceptance_gates.py --record gates_history.jsonl", file=sys.stderr)
        return 1
    stuck = detect_stuck(rows, args.consecutive)
    text = render_reflection(stuck, args.consecutive, args.max_consecutive)
    if not text:
        print("无卡死门禁(全部 PASS 或未达连续失败阈值)")
        return 0
    print(text)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"\nreflection -> {out}")
    return 2 if any(s["fail_streak"] >= args.max_consecutive for s in stuck) else 0


if __name__ == "__main__":
    sys.exit(main())
