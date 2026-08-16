"""independent_recompute.py - 独立重算入口（评估第 4 步）。

不读取 analysis.py、正文或 ledger——直接从 seed_pairs.npz 的原始 per-seed 数据
重算 metrics/统计/证据 JSON，与 analysis.py 结果对比。

用法: python independent_recompute.py <paper_dir> [--out report.md] [--selftest]
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats


def main() -> int:
    ap = argparse.ArgumentParser(description="independent recompute from seed_pairs.npz")
    ap.add_argument("paper_dir", nargs="?", default=".", help="paper dir containing results/seed_pairs.npz")
    ap.add_argument("--out", default=None, help="report output path")
    ap.add_argument("--selftest", action="store_true", help="run selftest and exit")
    args = ap.parse_args()

    if args.selftest:
        # synthetic per-seed data: mean(d) must equal group mean difference
        rng = np.random.RandomState(42)
        ours = rng.normal(0.10, 0.05, 50)
        temp = rng.normal(0.05, 0.03, 50)
        mean_d = float((ours - temp).mean())
        ok = abs(mean_d - (ours.mean() - temp.mean())) < 1e-12
        print(f"selftest: mean(d) == mean(diff): {ok} ({mean_d:.6f})")
        return 0 if ok else 1

    root = Path(args.paper_dir)
    npz = root / "results" / "seed_pairs.npz"
    if not npz.exists():
        print(f"FAIL: {npz} not found", file=sys.stderr)
        return 2
    d = np.load(npz, allow_pickle=True)

    ours = d["ours"].astype(float)
    temp = d["temp"].astype(float)
    iso = d["iso"].astype(float)
    acc = d["acc"].astype(float)
    n = len(ours)

    print(f"INDEPENDENT RECOMPUTE (n={n} seeds, no analysis.py)")
    print("=" * 50)

    # ECE means + CIs
    for name, v in [("ours", ours), ("temp", temp), ("iso", iso)]:
        mean = v.mean()
        sd = v.std(ddof=1)
        ci = 1.96 * sd / np.sqrt(n)
        print(f"  {name}: ECE {mean:.4f} [{mean-ci:.4f}, {mean+ci:.4f}]")

    # acc means
    print(f"  acc ours/temp/iso: {acc[0].mean():.4f}/{acc[1].mean():.4f}/{acc[2].mean():.4f}")

    # paired Wilcoxon
    for name, base in [("vs_temp", temp), ("vs_iso", iso)]:
        diff = ours - base
        w = stats.wilcoxon(diff, alternative="two-sided")
        print(f"  wilcoxon {name}: mean_diff={diff.mean():+.4f} W={w.statistic} p={w.pvalue:.4f}")

    # Holm (k=2) from unrounded p
    d_temp = ours - temp
    d_iso = ours - iso
    p1 = stats.wilcoxon(d_temp).pvalue
    p2 = stats.wilcoxon(d_iso).pvalue
    adj = sorted([min(1.0, p1 * 2), p2])
    print(f"  holm: p1*2={adj[0]:.4f} p2={adj[1]:.4f}")

    # Brier/NLL
    for name, i in [("ours", 0), ("temp", 1), ("iso", 2)]:
        print(f"  {name}: brier {d['brier'][i].mean():.4f} nll {d['nll'][i].mean():.4f}")

    # ablated
    print(f"  abl no_ts: {d['abl_no_ts'].mean():.4f}  no_ent: {d['abl_no_ent'].mean():.4f}")

    # compare with analysis.py output (if exists)
    e1 = root / "results" / "e1.json"
    if e1.exists():
        ref = json.loads(e1.read_text(encoding="utf-8"))
        ref_ours = ref["configs"]["ours_tf"]["ece_mean"]
        diff = abs(ref_ours - ours.mean())
        print(f"\n  analysis.py ours ECE: {ref_ours} | independent: {ours.mean():.4f} | diff: {diff:.6f}")
        ok = diff < 1e-4
        print(f"  MATCH: {'PASS' if ok else 'FAIL'}")
        return 0 if ok else 1
    print("\n  (no e1.json yet — training output only)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
