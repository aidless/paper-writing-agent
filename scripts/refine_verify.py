"""refine_verify.py - Phase 2: verify best train-time configs with multiple seeds.

Takes the top-N configs from the sweep and trains each with multiple seeds
at the FULL epoch budget (60), producing per-seed ECE/NLL/Brier/acc plus
paired statistics. Every config gets its own sealed-style run record.

Usage: python refine_verify.py <paper_dir> --seeds 5 --epochs 60
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

# top configs from sweep (ordered by potential): cell4 (T2 lamT0.1), cell1 (T1.5 lamT0.5),
# cell6 (T2 lamT0.5 lamH0.05) + two boundary cells probing lamT->0
TOP = [
    (2.0, 0.1, 0.1),   # cell 4: best so far
    (2.0, 0.05, 0.1),  # probe lamT smaller
    (1.5, 0.1, 0.1),   # probe T smaller with low lamT
    (2.0, 0.1, 0.3),   # probe lamH larger with low lamT
]


def run_one(paper_dir: Path, T: float, lam_T: float, lam_H: float,
            epochs: int, seed: int, dataset: str = "cifar10") -> dict:
    code = f"""
import sys; sys.path.insert(0, r"{paper_dir}")
import numpy as np, json, torch
import train_cifar as tc
tc.T_FIXED = {T}; tc.LAM_T = {lam_T}; tc.LAM_H = {lam_H}
dev = torch.device("cuda")
d = tc.CifarData(tc.Path(r"F:\\deepseek\\.datasets"), {seed}, dev, dataset="{dataset}")
n_cls = 100 if "{dataset}" == "cifar100" else 10
m = tc.make_model(n_cls).to(dev)
tc.train_one(m, d, epochs={epochs}, seed={seed}, mode="ours")
torch.cuda.synchronize()
loader = d.tst_loader(128)
p, y = tc.predict(m, loader, dev)
out = {{
  "T": {T}, "lam_T": {lam_T}, "lam_H": {lam_H}, "seed": {seed},
  "ours_ece": float(tc.ece_15(p, y)),
  "acc": float((p.argmax(1) == y).mean()),
  "brier": float(tc.brier_nll(p, y)[0]),
  "nll": float(tc.brier_nll(p, y)[1]),
}}
print(json.dumps(out))
"""
    r = subprocess.run([sys.executable, "-c", code], capture_output=True,
                       text=True, timeout=10800)
    if r.returncode != 0:
        return {"T": T, "lam_T": lam_T, "lam_H": lam_H, "seed": seed, "error": r.stderr[-400:]}
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    try:
        return json.loads(lines[-1])
    except Exception:
        return {"T": T, "lam_T": lam_T, "lam_H": lam_H, "seed": seed, "error": r.stdout[-300:]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="paper dir")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--dataset", default="cifar10")
    ap.add_argument("--configs", type=str, default="",
                    help="comma list of TOP indices")
    args = ap.parse_args()

    root = Path(args.target)
    out_dir = root / "results" / "refine"
    out_dir.mkdir(parents=True, exist_ok=True)
    res_path = out_dir / f"refine_{args.dataset}.json"
    results = []
    if res_path.exists():
        try:
            results = json.loads(res_path.read_text(encoding="utf-8"))
        except Exception:
            results = []
    done = {(r.get("T"), r.get("lam_T"), r.get("lam_H"), r.get("seed")) for r in results if "error" not in r}

    cfg_idx = [int(c) for c in args.configs.split(",")] if args.configs else range(len(TOP))
    for ci in cfg_idx:
        T, lt, lh = TOP[ci]
        for seed in [1000 + i for i in range(args.seeds)]:
            key = (T, lt, lh, seed)
            if key in done:
                continue
            print(f"\n=== cfg{ci} T={T} lam_T={lt} lam_H={lh} seed={seed} ===", flush=True)
            t0 = time.time()
            res = run_one(root, T, lt, lh, args.epochs, seed, args.dataset)
            res["cfg"] = ci
            res["elapsed_min"] = round((time.time() - t0) / 60, 1)
            results.append(res)
            print(f"    -> {json.dumps({k: v for k, v in res.items() if k != 'error'})}", flush=True)
            res_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    # summary per config
    print("\n=== REFINE SUMMARY ===")
    for ci in cfg_idx:
        T, lt, lh = TOP[ci]
        rows = [r for r in results if r.get("cfg") == ci and "error" not in r]
        if not rows:
            print(f"cfg{ci} (T={T} lamT={lt} lamH={lh}): no results")
            continue
        eces = [r["ours_ece"] for r in rows]
        accs = [r["acc"] for r in rows]
        print(f"cfg{ci} (T={T} lamT={lt} lamH={lh}) n={len(eces)}: "
              f"ECE {np.mean(eces):.4f}±{np.std(eces, ddof=1):.4f} acc {np.mean(accs):.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
