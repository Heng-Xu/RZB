#!/usr/bin/env python3
"""RIGID (R<=2.0) counterpart of the elastic Fig.1 scenario, for cost comparison.
Same constructed weak-tie high-PV case (CD decreasing with slr, storage x2.5),
but per-station CLR capped at 2.0. Reports the rigid scheme's annualized cost and
N-1 risk vs the elastic scheme (22843万, EENS=0)."""
import sys, numpy as np
from pathlib import Path
SC = Path("/home/roscy/ws_HengXU/徐州地区分布式新能源高渗透率地区110kV电网容载比弹性指标优化研究/实验/有EA/scripts")
sys.path.insert(0, str(SC))
import ea_county as ec
from ea_county import build_county, run_nsga2_enhanced, R_LO
from county_model import eval_station, get_branch, load_cost_params, LCCSimulator
cost = load_cost_params()
cost["storage_BESS"]["energy_cost_yuan_per_kwh"] *= 2.5   # same comprehensive storage cost
cost["storage_BESS"]["power_cost_yuan_per_kw"] *= 2.5
SIM = LCCSimulator(cost); BRANCH = get_branch(); ec.SIM = SIM
K = 20
ec.R_HI = 2.0                                             # RIGID: no station exceeds 2.0
BAND = (1.8, 2.0)
rng = np.random.default_rng(7)
county = build_county(K, seed=0)
for st in county:
    st.slr = round(float(rng.uniform(1.8, 3.5)), 3)
    st.pv_kwp = st.slr * st.peak_kw
_slr = np.array([s.slr for s in county]); _lo, _hi = _slr.min(), _slr.max()
for st in county:
    st.cd = round(0.45 - 0.35 * (st.slr - _lo) / (_hi - _lo), 3)

res = run_nsga2_enhanced(county, band=BAND, r220=None, pop=60, gen=120, seed=1)
if res.F is None or np.atleast_2d(res.F).shape[1] < 2:
    print("RIGID: no feasible front"); sys.exit(1)
F = np.atleast_2d(res.F); X = np.atleast_2d(res.X)
o = np.lexsort((F[:, 1], F[:, 0])); F = F[o]; X = X[o]

def stats(i):
    R = np.clip(X[i, :K], R_LO, 2.0); P = np.clip(X[i, K:], 0, 6.0)
    feasN = sum(eval_station(SIM, BRANCH, st, float(R[j]), float(P[j]))["feasible"]
                for j, st in enumerate(county))
    return F[i, 0], F[i, 1], int((R > 2.0).sum()), R.max(), feasN, P.sum()

ELAS_COST, ELAS_EENS = 22843.0, 0.0
print(f"front={len(F)}")
print("RIGID R<=2.0 (same scenario, storage x2.5):")
for lab, i in [("min-cost ", 0), ("min-EENS ", int(F[:, 1].argmin()))]:
    c, e, n, mx, fn, tp = stats(i)
    print(f"  {lab}: cost={c:.0f}万  EENS={e:.1f}MWh  maxR={mx:.2f}  feas={fn}/{K}  totStorage={tp:.1f}MW")
# fair comparison: rigid point matching elastic reliability (EENS<=0), else best-EENS
c_min, e_min = F[0, 0], F[0, 1]
ce, ee = F[int(F[:, 1].argmin()), 0], F[:, 1].min()
print(f"\nELASTIC (Fig.1): cost={ELAS_COST:.0f}万  EENS={ELAS_EENS:.1f}MWh")
if ee <= 1e-6:
    save = (ce - ELAS_COST) / ce * 100
    print(f"At EENS=0: rigid={ce:.0f}万 vs elastic={ELAS_COST:.0f}万  -> elastic saves {save:.1f}%")
else:
    print(f"RIGID cannot reach EENS=0 (best EENS={ee:.1f}MWh at cost {ce:.0f}万); "
          f"elastic achieves EENS=0 at {ELAS_COST:.0f}万 -> elastic dominates (cheaper AND more reliable)")

# save rigid min-EENS (20/20 feasible) point per-station data
import pandas as pd
i_best = int(F[:, 1].argmin())
Rb = np.clip(X[i_best, :K], R_LO, 2.0); Pb = np.clip(X[i_best, K:], 0, 6.0)
rows = [dict(station=st.sid, slr=round(st.slr, 3), cd=round(st.cd, 3), peak_kw=round(st.peak_kw),
             R_star=round(float(Rb[j]), 2), P_BESS_MW=round(float(Pb[j]), 2),
             feasible=bool(eval_station(SIM, BRANCH, st, float(Rb[j]), float(Pb[j]))["feasible"]))
        for j, st in enumerate(county)]
pd.DataFrame(rows).to_csv(SC.parent / "results" / "tables" / "scheme_rigid_Rle2_perstation.csv", index=False)
print("saved tables/scheme_rigid_Rle2_perstation.csv")
