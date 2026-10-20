#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""统一收敛扫描（FG-NSGA-II）——一次产出 速度/质量/消融/应用(K=20收敛) 全部结果。

Part A 规模/算法：5 变体 × 4 K × 3 seed，跑到收敛，记录逐代 HV。
Part B 应用变体@K=20 收敛：E3(带) / E6(县) / E7(系统约束)。
Part C（复用现有函数，口径不变）：E2 验证 / E4 规模。
运行级并行（进程池，每 worker 本地建县+跑，只回传纯 list），**单写入者**。

用法：
  python3 ea_converge.py            # 正式（后台跑，勿与其它写 results/ 的任务并发）
  python3 ea_converge.py smoke      # 极小预算冒烟，验证管线
之后：python3 ea_figures.py 出图。"""
from __future__ import annotations

import sys
import time
from multiprocessing import Pool

import numpy as np
import pandas as pd
from pymoo.indicators.hv import HV

import county_model as cm  # noqa: F401  （worker fork 时需已初始化 SIM/BRANCH）
import ea_county as e

RESULTS = e.RESULTS
N_WORKERS = 10
POP = 100
APP_K = 20                       # 应用主算例规模（E1/E2b/E3/E6/E7 都在此 K）
K_LIST = (10, 20, 30, 40)
SEEDS = (1, 2, 3)
GEN_B = 400                      # Part B（K=20 fg）收敛预算
# 慢收敛 baseline 给足代数看是否追上；快收敛变体给较小代数（足够到平台）
GEN = {"classic": 800, "nsga3": 800, "fg": 400, "repair_only": 400, "warmstart_only": 400}
ALGOS = ("classic", "nsga3", "fg", "repair_only", "warmstart_only")
RUNNERS = {
    "classic": e.run_nsga2, "nsga3": e.run_nsga3, "fg": e.run_nsga2_enhanced,
    "repair_only": e.run_repair_only, "warmstart_only": e.run_warmstart_only,
}
E3_BANDS = [(1.6, 1.9), (1.8, 2.1), (2.0, 2.3), (2.2, 2.5)]
E7_R220 = [None, 1.6, 1.8, 2.0]


def _run_one(cfg):
    """worker：本地建县 + 跑 + 只回传纯 list（避免跨进程 pickle pymoo 对象）。"""
    county = e.build_county(cfg["K"], seed=cfg["county_seed"])
    res = RUNNERS[cfg["algo"]](county, band=tuple(cfg["band"]), r220=cfg["r220"],
                               pop=POP, gen=cfg["gen"], seed=cfg["seed"], save_hist=cfg["hist"])
    Fraw = None if res.F is None else np.atleast_2d(res.F)
    out = {k: cfg[k] for k in ("tag", "kind", "K", "algo", "seed", "band", "r220", "county_seed")}
    out["dump_x"] = bool(cfg.get("dump_x"))
    out["finalF"] = [] if (Fraw is None or len(Fraw) == 0) else Fraw.tolist()
    if cfg["hist"]:
        hist = []
        for h in res.history:
            F = h.opt.get("F")
            hist.append(None if (F is None or len(F) == 0) else np.atleast_2d(F).tolist())
        out["hist"] = hist
        out["term_gen"] = len(res.history)
    if cfg.get("dump_x"):
        out["finalX"] = [] if res.X is None else np.atleast_2d(res.X).tolist()
    return out


def build_configs():
    cfgs = []
    for K in K_LIST:                                   # Part A
        for algo in ALGOS:
            for s in SEEDS:
                cfgs.append(dict(tag=f"A|{algo}|K{K}|s{s}", kind="A", K=K, algo=algo, seed=s,
                                 gen=GEN[algo], band=e.DEFAULT_BAND, r220=e.R220_DEFAULT,
                                 county_seed=0, hist=True,
                                 dump_x=(K == APP_K and algo == "fg" and s == SEEDS[0])))
    for band in E3_BANDS:                              # Part B-E3
        cfgs.append(dict(tag=f"E3|{band}", kind="E3", K=APP_K, algo="fg", seed=SEEDS[0], gen=GEN_B,
                         band=band, r220=e.R220_DEFAULT, county_seed=0, hist=False))
    for cs in range(6):                                # Part B-E6
        cfgs.append(dict(tag=f"E6|c{cs}", kind="E6", K=APP_K, algo="fg", seed=SEEDS[0], gen=GEN_B,
                         band=e.DEFAULT_BAND, r220=e.R220_DEFAULT, county_seed=cs, hist=False))
    for r in E7_R220:                                  # Part B-E7
        cfgs.append(dict(tag=f"E7|r{r}", kind="E7", K=APP_K, algo="fg", seed=SEEDS[0], gen=GEN_B,
                         band=e.DEFAULT_BAND, r220=r, county_seed=0, hist=False))
    return cfgs


def _arr(F):
    F = np.array(F, float)
    return F if (F.ndim == 2 and len(F)) else np.empty((0, 2))


def _savings(county, F):
    rb1, rb2, rbR = e.baseline_rigid(county, 2.0)
    cand = F[F[:, 1] <= rb2 + 1e-6] if len(F) else F
    eac = float(cand[:, 0].min()) if len(cand) else (float(F[:, 0].min()) if len(F) else rb1)
    return rb1, rb2, rbR, eac, (rb1 - eac) / rb1 * 100


def assemble(results):
    by_tag = {r["tag"]: r for r in results}
    partA = [r for r in results if r["kind"] == "A"]

    # ── ea_converge.csv：逐代 HV（每 K 共同参考点，5 变体所有末代前沿定 nadir）──
    rows = []
    for K in K_LIST:
        finals = [f for f in (_arr(r["finalF"]) for r in partA if r["K"] == K) if len(f)]
        hv = HV(ref_point=e.ref_point(*finals))
        for r in (x for x in partA if x["K"] == K):
            for g, Fg in enumerate(r["hist"], 1):
                rows.append({"K": K, "algo": r["algo"], "seed": r["seed"], "gen": g,
                             "hv": round(0.0 if Fg is None else float(hv(_arr(Fg))), 2)})
    pd.DataFrame(rows).to_csv(RESULTS / "ea_converge.csv", index=False)
    pd.DataFrame([{"K": r["K"], "algo": r["algo"], "seed": r["seed"], "term_gen": r["term_gen"]}
                  for r in partA]).to_csv(RESULTS / "ea_converge_termgen.csv", index=False)
    print(f"[converge] ea_converge.csv {len(rows)} 行", flush=True)

    # ── K=APP_K fg 应用：E1 前沿 + 拐点一站一策 + E2b 省% ──
    app = next(r for r in partA if r.get("dump_x"))
    F = _arr(app["finalF"]); X = np.array(app["finalX"], float)
    order = np.lexsort((F[:, 1], F[:, 0])); F, X = F[order], X[order]
    ideal, nadir = F.min(axis=0), F.max(axis=0)
    span = np.where(nadir > ideal, nadir - ideal, 1)
    ki = int(np.linalg.norm((F - ideal) / span, axis=1).argmin())
    pd.DataFrame([{"point": i, "f1_wan": round(F[i, 0], 1), "f2_eens_mwh": round(F[i, 1], 1),
                   "is_knee": i == ki} for i in range(len(F))]
                 ).to_csv(RESULTS / "ea_county_pareto.csv", index=False)
    county = e.build_county(APP_K, seed=0); kx = X[ki]
    pd.DataFrame([{"station": st.sid, "slr": st.slr, "cd": st.cd, "peak_kw": round(st.peak_kw),
                   "R_star": round(float(kx[j]), 2), "P_BESS_MW": round(float(kx[APP_K + j]), 2),
                   "route": ("升容载比增容" if kx[j] > 2.0 + 1e-6 else
                             ("配储为主" if kx[APP_K + j] > 0.05 else "低容载比+强联络"))}
                  for j, st in enumerate(county)]).to_csv(RESULTS / "ea_county_strategy_knee.csv", index=False)
    per = e.evaluate_county(county, kx[:APP_K], kx[APP_K:], e.DEFAULT_BAND)
    rb1, rb2, rbR, eac, save = _savings(county, F)
    pd.DataFrame([{"K": APP_K, "rigid_f1_wan": round(rb1, 1), "rigid_f2_mwh": round(rb2, 1),
                   "rigid_agg_R": round(rbR, 2), "ea_f1_at_same_risk_wan": round(eac, 1),
                   "ea_cost_saving_pct": round(save, 1)}]).to_csv(RESULTS / "ea_baseline.csv", index=False)
    print(f"[E1收敛] 前沿{len(F)}点 拐点 f1={F[ki,0]:.0f}万 f2={F[ki,1]:.0f}MWh 聚合R={per['agg_R']:.2f}；"
          f"[E2b] 刚性2.0 {rb1:.0f}万→EA {eac:.0f}万 省{save:.1f}%", flush=True)

    # ── E3 带效应 ──
    e3 = []
    for band in E3_BANDS:
        F3 = _arr(by_tag[f"E3|{band}"]["finalF"])
        e3.append({"band": f"[{band[0]},{band[1]}]", "n_front": len(F3),
                   "min_cost_wan": round(float(F3[:, 0].min()), 1) if len(F3) else None,
                   "min_eens_mwh": round(float(F3[:, 1].min()), 1) if len(F3) else None})
    pd.DataFrame(e3).to_csv(RESULTS / "ea_band_effect.csv", index=False)

    # ── E6 鲁棒性（6 县省%）──
    e6 = [{"county_seed": cs,
           "saving_pct": round(_savings(e.build_county(APP_K, seed=cs), _arr(by_tag[f"E6|c{cs}"]["finalF"]))[4], 1)}
          for cs in range(6)]
    df6 = pd.DataFrame(e6); df6.to_csv(RESULTS / "ea_robustness.csv", index=False)
    print(f"[E6收敛] 6县 省% {df6.saving_pct.mean():.1f}±{df6.saving_pct.std():.1f} 范围[{df6.saving_pct.min()},{df6.saving_pct.max()}]", flush=True)

    # ── E7 系统约束 ──
    names = {None: "unconstrained(no system)", 1.8: "constrained R220=1.8",
             1.6: "constrained R220=1.6", 2.0: "constrained R220=2.0"}
    fronts = {r: _arr(by_tag[f"E7|r{r}"]["finalF"]) for r in E7_R220}
    hv7 = HV(ref_point=e.ref_point(*[f for f in fronts.values() if len(f)]))
    pd.DataFrame([{"case": names[r],
                   "min_cost_wan": round(float(fronts[r][:, 0].min()), 1) if len(fronts[r]) else None,
                   "min_eens_mwh": round(float(fronts[r][:, 1].min()), 1) if len(fronts[r]) else None,
                   "HV": round(float(hv7(fronts[r])), 1) if len(fronts[r]) else None}
                  for r in E7_R220]).to_csv(RESULTS / "ea_system_constraint.csv", index=False)
    Fu, Fc = fronts[None], fronts[1.8]
    pd.DataFrame({"f1_unc": pd.Series(Fu[:, 0] if len(Fu) else []), "f2_unc": pd.Series(Fu[:, 1] if len(Fu) else []),
                  "f1_con": pd.Series(Fc[:, 0] if len(Fc) else []), "f2_con": pd.Series(Fc[:, 1] if len(Fc) else [])}
                 ).to_csv(RESULTS / "ea_system_fronts.csv", index=False)
    dcost = (float(Fc[:, 0].min()) - float(Fu[:, 0].min())) if (len(Fc) and len(Fu)) else float("nan")
    print(f"[E7收敛] 加约束成本下限 Δ={dcost:.0f}万", flush=True)


def main():
    global POP, K_LIST, SEEDS, GEN, GEN_B, APP_K
    smoke = len(sys.argv) > 1 and sys.argv[1] == "smoke"
    if smoke:
        POP, K_LIST, SEEDS, APP_K, GEN_B = 12, (4, 6), (1,), 6, 8
        GEN = {k: 8 for k in GEN}
        print("[SMOKE] 极小预算冒烟", flush=True)
    t0 = time.perf_counter()
    cfgs = build_configs()
    print(f"[converge] 共 {len(cfgs)} 个 run，{N_WORKERS} worker 并行，POP={POP} GEN={GEN}", flush=True)
    with Pool(N_WORKERS) as pool:
        results = pool.map(_run_one, cfgs)
    print(f"[converge] 全部 run 完成，用时 {(time.perf_counter()-t0)/3600:.2f} h", flush=True)
    assemble(results)
    if not smoke:                                    # Part C：口径不变，复用现有函数刷新（smoke 跳过）
        print(">>> E2 求解器验证", flush=True); e.E2_validation()
        print(">>> E4 规模动机", flush=True); e.E4_scaling()
    print(f"[converge] DONE 总用时 {(time.perf_counter()-t0)/3600:.2f} h", flush=True)


if __name__ == "__main__":
    main()
