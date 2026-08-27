#!/usr/bin/env python3
"""CONSTRUCTED scenario (author-commissioned): a weakly-interconnected, high-PV
county, to illustrate when elastic capacity expansion (R>2.0) is warranted.
Knobs: weak ties CD=0.15, high penetration slr~U[1.8,3.5], elastic CLR band up
to 3.0. Reproducible (seed fixed). Traverse the whole front; keep the point with
the MOST stations R>2.0. NOT the representative case — a designed scenario."""
import sys, numpy as np, pandas as pd
from pathlib import Path
from collections import Counter
SC = Path("/home/roscy/ws_HengXU/徐州地区分布式新能源高渗透率地区110kV电网容载比弹性指标优化研究/实验/有EA/scripts")
sys.path.insert(0, str(SC))
import ea_county as ec
from ea_county import build_county, run_nsga2_enhanced, R_LO, R_HI, R220_DEFAULT
from county_model import eval_station, get_branch, load_cost_params, LCCSimulator
# comprehensive storage cost (per user: 现有配储成本不够全面): x2.5
#   = 10yr annualization (~1.74, vs the buggy 25yr) x replacement+degradation/augmentation (~1.4)
STORAGE_COST_FACTOR = 2.5
cost = load_cost_params()
cost["storage_BESS"]["energy_cost_yuan_per_kwh"] *= STORAGE_COST_FACTOR
cost["storage_BESS"]["power_cost_yuan_per_kw"] *= STORAGE_COST_FACTOR
SIM = LCCSimulator(cost); BRANCH = get_branch()
ec.SIM = SIM                             # EA evaluates cost with the higher (comprehensive) storage price
K = 20
CD_WEAK = 0.15                            # storage NOT quantity-limited (P_HI stays 6.0); cost raised instead
BAND = (1.8, 3.0)                         # elastic band: CLR upper to 3.0
rng = np.random.default_rng(7)
county = build_county(K, seed=0)          # base structure (peaks, buses)
for st in county:
    st.slr = round(float(rng.uniform(1.8, 3.5)), 3)   # high penetration
    st.pv_kwp = st.slr * st.peak_kw        # PV follows the new slr
# CD DECREASING with slr: high-PV stations are weakly interconnected (realistic)
_slr = np.array([s.slr for s in county]); _lo, _hi = _slr.min(), _slr.max()
for st in county:
    frac = (st.slr - _lo) / (_hi - _lo)               # 0 (low slr) .. 1 (high slr)
    st.cd = round(0.45 - 0.35 * frac, 3)              # 0.45 (low slr) -> 0.10 (high slr)

res = run_nsga2_enhanced(county, band=BAND, r220=None, pop=60, gen=120, seed=1)  # county-only, no upstream limit
if res.F is None or np.atleast_2d(res.F).shape[1] < 2:
    print("NO FEASIBLE FRONT — settings too tight"); sys.exit(1)
F = np.atleast_2d(res.F); X = np.atleast_2d(res.X)
o = np.lexsort((F[:, 1], F[:, 0])); F = F[o]; X = X[o]
def npoint(i):
    R = np.clip(X[i, :K], R_LO, R_HI); return int((R > 2.0).sum())
hist = Counter(npoint(i) for i in range(len(X)))
print("front R>2.0 histogram:", dict(sorted(hist.items())), flush=True)

slr_all = np.array([st.slr for st in county])
best = None
for i in range(len(X)):
    R = np.clip(X[i, :K], R_LO, R_HI); P = np.clip(X[i, K:], 0, ec.P_HI)
    n = int((R > 2.0).sum()); cost = float(F[i, 0])
    feasN = sum(eval_station(SIM, BRANCH, st, float(R[j]), float(P[j]))["feasible"]
                for j, st in enumerate(county))
    align = float(np.dot(R, slr_all - slr_all.mean()))   # reward high R where slr is high
    key = (round(align, 1), n, feasN, -cost)             # primary: high-slr -> high-R alignment
    if best is None or key > best['key']:
        best = dict(key=key, n=n, cost=cost, eens=float(F[i, 1]), feasN=feasN,
                    R=R.copy(), P=P.copy(), i=i)
R, P = best['R'], best['P']
rows = []
for j, st in enumerate(county):
    Rj, Pj = float(R[j]), float(P[j])
    route = ("capacity-expansion" if Rj > 2.0 + 1e-6 else ("storage" if Pj > 0.05 else "tie-line"))
    feas = eval_station(SIM, BRANCH, st, Rj, Pj)["feasible"]
    rows.append(dict(station=st.sid, slr=round(st.slr, 3), cd=round(st.cd, 3), peak_kw=round(st.peak_kw),
                     R_star=round(Rj, 2), P_BESS_MW=round(Pj, 2), route=route, feasible=bool(feas)))
df = pd.DataFrame(rows)
df.to_csv(SC.parent / "results" / "ea_county_strategy_cdslr.csv", index=False)
corr = float(np.corrcoef(slr_all, R)[0, 1])
print(f"CD-DECREASING(slr)  band={BAND} P_HI={ec.P_HI} storageX={STORAGE_COST_FACTOR}  front={len(F)}  "
      f"BEST @{best['i']}: R>2.0={best['n']} maxR={R.max():.2f} feasible={best['feasN']}/{K} "
      f"corr(slr,R)={corr:.2f} cost={best['cost']:.0f}万 eens={best['eens']:.1f}MWh")
print("R>2.0 (slr,R,P):", "; ".join(f"{r['slr']}/{r['R_star']}/{r['P_BESS_MW']}" for r in rows if r['R_star'] > 2.0))
