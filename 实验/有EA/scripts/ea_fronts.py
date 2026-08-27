#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""捕获 经典 NSGA-II / NSGA-III / FG-NSGA-II 的帕累托前沿点（同县、同 seed、同预算），
供"前沿叠加对比图"。同等预算 gen400（FG 已收敛、baseline 仍在爬 → 同预算下 FG 前沿占优）；
额外存 gen100/gen200 快照。运行级并行，写 `ea_fronts_compare.csv`（**不覆盖既有结果**）。
用法：python3 ea_fronts.py [smoke]；之后 python3 ea_figures.py 出图。"""
from __future__ import annotations

import sys
import time
from multiprocessing import Pool

import numpy as np
import pandas as pd

import county_model as cm  # noqa: F401
import ea_county as e

RESULTS = e.RESULTS
POP, GEN, SEED = 100, 400, 1
K_LIST = (10, 20, 30, 40)
GTAGS = (100, 200, 400)
RUN = {"classic": e.run_nsga2, "nsga3": e.run_nsga3, "fg": e.run_nsga2_enhanced}


def _run(cfg):
    county = e.build_county(cfg["K"], seed=0)
    res = RUN[cfg["algo"]](county, band=e.DEFAULT_BAND, r220=e.R220_DEFAULT,
                           pop=POP, gen=GEN, seed=SEED, save_hist=True)
    hist = res.history
    out = {"K": cfg["K"], "algo": cfg["algo"], "fronts": {}}
    for g in GTAGS:
        h = hist[min(g, len(hist)) - 1]
        F = h.opt.get("F")
        out["fronts"][g] = [] if (F is None or len(F) == 0) else np.atleast_2d(F).tolist()
    return out


def main():
    global POP, GEN, K_LIST, GTAGS
    if len(sys.argv) > 1 and sys.argv[1] == "smoke":
        POP, GEN, K_LIST, GTAGS = 12, 8, (4, 6), (4, 8)
        print("[SMOKE]", flush=True)
    cfgs = [{"K": K, "algo": a} for K in K_LIST for a in RUN]
    t0 = time.perf_counter()
    print(f"[fronts] {len(cfgs)} runs, pop{POP}/gen{GEN}, {min(10, len(cfgs))} worker", flush=True)
    with Pool(min(10, len(cfgs))) as pool:
        res = pool.map(_run, cfgs)
    rows = []
    for r in res:
        for g, F in r["fronts"].items():
            for f1, f2 in F:
                rows.append({"K": r["K"], "algo": r["algo"], "gen": g,
                             "f1_wan": round(float(f1), 1), "f2_mwh": round(float(f2), 2)})
    pd.DataFrame(rows).to_csv(RESULTS / "ea_fronts_compare.csv", index=False)
    print(f"[fronts] ea_fronts_compare.csv {len(rows)} 行，用时 {(time.perf_counter()-t0)/3600:.2f}h", flush=True)


if __name__ == "__main__":
    main()
