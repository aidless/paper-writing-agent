"""sweep_coefficients.py - Phase 1 coefficient sweep (R52 plan).

Goal: find (T, lam_T, lam_H) windows where the training-time objective's
ECE beats post-hoc temperature scaling (currently 0.0090 on this data),
turning the negative result into a positive one if such a window exists.

Each grid cell: 1 seed x epochs, own run record, no modification of the
sealed original run. Uses module-attribute injection (tc.T_FIXED etc.).

Usage: python sweep_coefficients.py <paper_dir> --epochs 60 --seed 1000
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

# grid: T x lam_T x lam_H (8-12 cells). Focus T (biggest effect) and lam_T.
GRID = [
    # (T, lam_T, lam_H)
    (2.0, 0.5, 0.1),   # original (baseline of sweep)
    (1.5, 0.5, 0.1),
    (3.0, 0.5, 0.1),
    (4.0, 0.5, 0.1),
    (2.0, 0.1, 0.1),
    (2.0, 1.0, 0.1),
    (2.0, 0.5, 0.05),
    (2.0, 0.5, 0.3),
    (3.0, 0.1, 0.3),   # "soft regularizer" corner
    (1.5, 1.0, 0.05),  # "strong temp, weak ent" corner
]


def run_cell(paper_dir: Path, T: float, lam_T: float, lam_H: float,
             epochs: int, seed: int, out_dir: Path) -> dict:
    """Train one cell via a subprocess with injected coefficients, return ECE."""
    code = f"""
import sys; sys.path.insert(0, r"{paper_dir}")
import numpy as np, json, torch
import train_cifar as tc
tc.T_FIXED = {T}; tc.LAM_T = {lam_T}; tc.LAM_H = {lam_H}
dev = torch.device("cuda")
d = tc.CifarData(tc.Path(r"F:\\deepseek\\.datasets"), {seed}, dev)
m = tc.make_model().to(dev)
tc.train_one(m, d, epochs={epochs}, seed={seed}, mode="ours")
torch.cuda.synchronize()
# post-hoc baselines on the same model
bl = tc.predict_raw(m, d, dev)
cal_l = bl["cal"]
_, y_cal = d.cal_arrays()
temp = tc.fit_temperature(cal_l, y_cal.numpy())
p_cal = torch.nn.functional.softmax(cal_l, dim=1).numpy()
iso = tc.fit_isotonic(p_cal, y_cal.numpy())
loader = d.tst_loader(128)
p_base, y = tc.predict(m, loader, dev)
p_ts, _ = tc.predict(m, loader, dev, temp=temp)
p_iso, _ = tc.predict(m, loader, dev, iso_model=iso)
out = {{
  "T": {T}, "lam_T": {lam_T}, "lam_H": {lam_H},
  "ours_ece": float(tc.ece_15(p_base, y)),
  "ts_ece": float(tc.ece_15(p_ts, y)),
  "iso_ece": float(tc.ece_15(p_iso, y)),
  "acc": float((p_base.argmax(1) == y).mean()),
}}
print(json.dumps(out))
"""
    r = subprocess.run([sys.executable, "-c", code], capture_output=True,
                       text=True, timeout=7200)
    if r.returncode != 0:
        return {"T": T, "lam_T": lam_T, "lam_H": lam_H, "error": r.stderr[-500:]}
    try:
        # last non-empty stdout line is the json
        lines = [l for l in r.stdout.splitlines() if l.strip()]
        return json.loads(lines[-1])
    except Exception:
        return {"T": T, "lam_T": lam_T, "lam_H": lam_H, "error": r.stdout[-300:]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="paper dir")
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--cells", type=str, default="", help="comma list of cell indices")
    args = ap.parse_args()

    root = Path(args.target)
    out_dir = root / "results" / "sweep"
    out_dir.mkdir(parents=True, exist_ok=True)

    cells = [int(c) for c in args.cells.split(",")] if args.cells else range(len(GRID))
    results = []
    for i in cells:
        T, lt, lh = GRID[i]
        print(f"\n=== cell {i}: T={T} lam_T={lt} lam_H={lh} ===", flush=True)
        t0 = time.time()
        res = run_cell(root, T, lt, lh, args.epochs, args.seed, out_dir)
        res["cell"] = i
        res["elapsed_min"] = round((time.time() - t0) / 60, 1)
        results.append(res)
        print(f"    -> {json.dumps({k: v for k, v in res.items() if k != 'error'})}", flush=True)
        # incremental save (crash-safe)
        (out_dir / "sweep_results.json").write_text(
            json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    # summary table
    print("\n=== SWEEP SUMMARY ===")
    print(f"{'cell':<5}{'T':<6}{'lam_T':<7}{'lam_H':<7}{'ours':<9}{'ts':<9}{'iso':<9}{'win?':<6}")
    for r in results:
        if "error" in r:
            print(f"{r['cell']:<5}{r['T']:<6}{r['lam_T']:<7}{r['lam_H']:<7}ERROR")
            continue
        win = "YES" if r["ours_ece"] < r["ts_ece"] else ""
        print(f"{r['cell']:<5}{r['T']:<6}{r['lam_T']:<7}{r['lam_H']:<7}"
              f"{r['ours_ece']:.4f}  {r['ts_ece']:.4f}  {r['iso_ece']:.4f}  {win:<6}")
    winners = [r for r in results if "error" not in r and r["ours_ece"] < r["ts_ece"]]
    print(f"\nWindows where ours beats TS: {len(winners)}/{len(results)}")
    if winners:
        best = min(winners, key=lambda r: r["ours_ece"])
        print(f"BEST: cell {best['cell']} T={best['T']} lam_T={best['lam_T']} "
              f"lam_H={best['lam_H']} ours={best['ours_ece']:.4f} < ts={best['ts_ece']:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
