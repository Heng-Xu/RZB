#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
县级多变电站容载比弹性 —— 多目标进化优化（NSGA-II）。MIND 2026。

决策向量 x = [R_1..R_K, P_1..P_K]（站容载比 + 站储能功率MW）。
目标 min (县总年化成本 f1[万元], 县 N-1 风险 f2[MWh EENS])。
约束 G≤0：每站过反向承载力硬闸；县聚合容载比 ∈ [R_lo, R_hi] 带。

实验：
  E1 代表县 Pareto 前沿 + 拐点「一站一策」      -> results/ea_county_pareto.csv
  E2 验证：小K穷举真前沿 vs NSGA-II(HV比, IGD) + 全县刚性2.0基线 -> results/ea_validation.csv
  E3 容载比带效应（扫 band）                      -> results/ea_band_effect.csv
  E4 可扩展性 K=3..40：穷举组合爆炸 vs NSGA-II耗时 -> results/ea_scaling.csv
  E5 算法对照 NSGA-II vs MOEA/D，多seed HV收敛     -> results/ea_convergence.csv

用法：python3 ea_county.py [e1 e2 e3 e4 e5 | all | core]
"""
from __future__ import annotations

import sys
import time
import itertools
from pathlib import Path

import numpy as np
import pandas as pd

from county_model import (
    build_county, make_sim, get_branch, eval_station, Station,
    aggregate_capacity_load_ratio, county_coincident_peak_kw,
    station_reverse_injection, upstream_reverse_limit,
    R_LO, R_HI, P_LO, P_HI, DEFAULT_BAND, DIVERSITY_FACTOR,
    REVERSE_COINCIDENCE, R220_DEFAULT,
)
from lcc_simulator import REVERSE_TX_LIMIT, PV_PEAK_FACTOR, REVERSE_LOAD_FACTOR

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.indicators.hv import HV
from pymoo.indicators.igd import IGD
from pymoo.operators.sampling.lhs import LHS
from pymoo.core.repair import Repair
from pymoo.core.sampling import Sampling

SIM = make_sim()
BRANCH = get_branch()


# ──────────────────────────────────────────────────────────────────────────────
# 评价：给定决策向量 -> (f1万元, f2 MWh, 约束违反)
# ──────────────────────────────────────────────────────────────────────────────
def evaluate_county(stations, R_arr, P_arr, band, r220=R220_DEFAULT):
    """返回目标与（归一化）约束。r220=None 关闭上级系统潮流约束（用于小K求解器验证）。
    约束统一归一化到 O(1)，避免不同量纲(kW vs 容载比)在 CV 聚合中互相压制。"""
    f1 = 0.0; f2 = 0.0; tx_list = []; gate_g = []; per = []; rev_sum = 0.0
    for st, R, P in zip(stations, R_arr, P_arr):
        e = eval_station(SIM, BRANCH, st, float(R), float(P))
        f1 += e["f1"]; f2 += e["eens"]; tx_list.append(e["tx_mva"])
        gate_g.append(e["overload_kw"] / max(1.0, st.peak_kw))     # 归一化相对越限
        rev_sum += station_reverse_injection(st, float(P))
        per.append(e)
    agg_R = aggregate_capacity_load_ratio(stations, tx_list)
    g_lo = (band[0] - agg_R) / band[0] if band[0] > 0 else (band[0] - agg_R)
    g_hi = (agg_R - band[1]) / band[1] if band[1] > 0 else (agg_R - band[1])
    if r220 is not None:
        L_rev = upstream_reverse_limit(stations, r220)
        g_up = (rev_sum * REVERSE_COINCIDENCE - L_rev) / max(1.0, L_rev)
    else:
        L_rev = None; g_up = None
    return {
        "f1_wan": f1 / 1e4, "f2_mwh": f2 / 1000.0, "agg_R": agg_R,
        "gate_g": gate_g, "band_g_lo": g_lo, "band_g_hi": g_hi,
        "g_up": g_up, "rev_sum": rev_sum, "L_rev": L_rev, "per": per,
    }


class CountyProblem(ElementwiseProblem):
    def __init__(self, stations, band=DEFAULT_BAND, r220=R220_DEFAULT):
        self.stations = stations
        self.band = band
        self.r220 = r220                       # None → 关闭上级系统潮流约束
        k = len(stations)
        self.k = k
        n_con = k + 2 + (1 if r220 is not None else 0)   # 逐站闸 + 带2 + (上级1)
        super().__init__(
            n_var=2 * k, n_obj=2, n_ieq_constr=n_con,
            xl=np.array([R_LO] * k + [P_LO] * k),
            xu=np.array([R_HI] * k + [P_HI] * k),
        )

    def _evaluate(self, x, out, *args, **kwargs):
        k = self.k
        res = evaluate_county(self.stations, x[:k], x[k:], self.band, self.r220)
        out["F"] = [res["f1_wan"], res["f2_mwh"]]
        G = res["gate_g"] + [res["band_g_lo"], res["band_g_hi"]]
        if self.r220 is not None:
            G = G + [res["g_up"]]
        out["G"] = G


def run_nsga2(stations, band=DEFAULT_BAND, r220=R220_DEFAULT, pop=60, gen=120, seed=1, save_hist=False):
    """经典 NSGA-II（baseline）。r220=None 关闭上级系统约束。"""
    prob = CountyProblem(stations, band, r220)
    algo = NSGA2(pop_size=pop, sampling=LHS())
    res = minimize(prob, algo, ("n_gen", gen), seed=seed, verbose=False,
                   save_history=save_hist)
    return res


# ──────────────────────────────────────────────────────────────────────────────
# 增强 NSGA-II（阶段三算法创新点）：修复算子 + 启发式热启动
# ──────────────────────────────────────────────────────────────────────────────
def _repair_one(x, stations, band, r220):
    """把决策向量投影到(近似)可行：①缩放R入容载比带；②逐站补储能/必要时升R过反送闸；
    ③补储能满足上级系统约束。储能步骤不改R、不破坏带。"""
    k = len(stations)
    R = np.clip(np.asarray(x[:k], float), R_LO, R_HI)
    P = np.clip(np.asarray(x[k:], float), P_LO, P_HI)
    peaks = np.array([s.peak_kw for s in stations])
    pv = np.array([s.pv_kwp for s in stations])
    sum_peak = peaks.sum(); denom = DIVERSITY_FACTOR * sum_peak
    # ① 带：缩放 R 使聚合容载比 ∈ [lo,hi]
    aggR = (R * peaks).sum() / denom
    if band[0] > 0 and aggR < band[0]:
        R = np.clip(R * (band[0] / aggR), R_LO, R_HI)
    elif band[1] < 1e8 and aggR > band[1]:
        R = np.clip(R * (band[1] / aggR), R_LO, R_HI)
    # ② 逐站反送闸：先补储能，储能到顶仍越限再升R
    rev = np.maximum(0.0, PV_PEAK_FACTOR * pv - REVERSE_LOAD_FACTOR * peaks - P * 1000.0)
    lim = REVERSE_TX_LIMIT * R * peaks
    for j in np.where(rev - lim > 0)[0]:
        P[j] = min(P_HI, P[j] + (rev[j] - lim[j]) / 1000.0)
        rev_j = max(0.0, PV_PEAK_FACTOR * pv[j] - REVERSE_LOAD_FACTOR * peaks[j] - P[j] * 1000.0)
        if rev_j > REVERSE_TX_LIMIT * R[j] * peaks[j]:
            R[j] = min(R_HI, rev_j / (REVERSE_TX_LIMIT * peaks[j]))
    # ③ 上级系统约束：Σrev_up·η ≤ L_rev，不足则给反送最大的站继续补储能
    if r220 is not None:
        L_rev = REVERSE_TX_LIMIT * r220 * denom
        rev = np.maximum(0.0, PV_PEAK_FACTOR * pv - REVERSE_LOAD_FACTOR * peaks - P * 1000.0)
        excess = rev.sum() * REVERSE_COINCIDENCE - L_rev
        for j in np.argsort(-rev):
            if excess <= 0:
                break
            cut = min((P_HI - P[j]) * 1000.0, rev[j], excess / REVERSE_COINCIDENCE)
            if cut <= 0:
                continue
            P[j] = min(P_HI, P[j] + cut / 1000.0); excess -= cut * REVERSE_COINCIDENCE
    # ④ 带下限补足（修正①里 R 触顶被裁剪造成的 agg_R 不足；升R只帮闸、不破坏闸/系统）
    aggR = (R * peaks).sum() / denom
    if band[0] > 0 and aggR < band[0]:
        room = R < R_HI - 1e-9
        if room.any():
            deficit = band[0] * denom - (R * peaks).sum()
            R[room] = np.clip(R[room] + deficit / peaks[room].sum(), R_LO, R_HI)
    return np.concatenate([np.clip(R, R_LO, R_HI), np.clip(P, P_LO, P_HI)])


class FeasRepair(Repair):
    def __init__(self, stations, band, r220):
        super().__init__(); self.stations = stations; self.band = band; self.r220 = r220
    def _do(self, problem, X, **kwargs):
        X = np.atleast_2d(X).astype(float)
        for i in range(len(X)):
            X[i] = _repair_one(X[i], self.stations, self.band, self.r220)
        return X


class WarmStartSampling(Sampling):
    """LHS 多样性 + 25% 注入「低R+0储」种子；全部经修复 → 初始种群即可行。"""
    def __init__(self, stations, band, r220):
        super().__init__(); self.stations = stations; self.band = band; self.r220 = r220
    def _do(self, problem, n_samples, random_state=None, **kwargs):
        # 复现性修复：把算法播种的 random_state 传给内部 LHS，否则 LHS 每次熵播种→不可复现
        X = LHS()._do(problem, n_samples, random_state=random_state).astype(float)
        k = len(self.stations)
        r_seed = max(R_LO, min(R_HI, self.band[0] * DIVERSITY_FACTOR)) if self.band[0] > 0 else R_LO
        for i in range(max(1, n_samples // 4)):
            X[i, :k] = r_seed; X[i, k:] = 0.0
        for i in range(n_samples):
            X[i] = _repair_one(X[i], self.stations, self.band, self.r220)
        return X


def run_nsga2_enhanced(stations, band=DEFAULT_BAND, r220=R220_DEFAULT, pop=60, gen=120,
                       seed=1, save_hist=False):
    """增强 NSGA-II = 经典 + 修复算子(始终可行) + 启发式热启动。同问题同预算下应更快/更优。"""
    np.random.seed(seed)   # 复现性修复：pymoo minimize(seed=) 在本版本未完全控住全局RNG，显式播种
    prob = CountyProblem(stations, band, r220)
    algo = NSGA2(pop_size=pop, sampling=WarmStartSampling(stations, band, r220),
                 repair=FeasRepair(stations, band, r220))
    res = minimize(prob, algo, ("n_gen", gen), seed=seed, verbose=False, save_history=save_hist)
    return res


def run_nsga3(stations, band=DEFAULT_BAND, r220=R220_DEFAULT, pop=60, gen=120, seed=1, save_hist=False):
    """NSGA-III（额外经典对照 baseline；2 目标下与 NSGA-II 同档，用以证明增益来自修复而非换算法）。
    用 das-dennis 参考方向，方向数=pop → pop_size=pop，预算与经典/增强严格相等(pop×gen)。"""
    from pymoo.algorithms.moo.nsga3 import NSGA3
    from pymoo.util.ref_dirs import get_reference_directions
    prob = CountyProblem(stations, band, r220)
    ref_dirs = get_reference_directions("das-dennis", 2, n_partitions=pop - 1)
    algo = NSGA3(ref_dirs=ref_dirs, sampling=LHS())
    res = minimize(prob, algo, ("n_gen", gen), seed=seed, verbose=False, save_history=save_hist)
    return res


def run_repair_only(stations, band=DEFAULT_BAND, r220=R220_DEFAULT, pop=60, gen=120, seed=1, save_hist=False):
    """消融：FG-NSGA-II 去掉热启动、仅保留修复算子（采样用普通 LHS + FeasRepair 每代修复）。"""
    prob = CountyProblem(stations, band, r220)
    algo = NSGA2(pop_size=pop, sampling=LHS(), repair=FeasRepair(stations, band, r220))
    res = minimize(prob, algo, ("n_gen", gen), seed=seed, verbose=False, save_history=save_hist)
    return res


def run_warmstart_only(stations, band=DEFAULT_BAND, r220=R220_DEFAULT, pop=60, gen=120, seed=1, save_hist=False):
    """消融：FG-NSGA-II 去掉修复、仅保留热启动（WarmStartSampling 造可行初始种群，进化中不再修复）。"""
    prob = CountyProblem(stations, band, r220)
    algo = NSGA2(pop_size=pop, sampling=WarmStartSampling(stations, band, r220))
    res = minimize(prob, algo, ("n_gen", gen), seed=seed, verbose=False, save_history=save_hist)
    return res


# ──────────────────────────────────────────────────────────────────────────────
# 真前沿（小 K 穷举，缓存每站选项后做笛卡尔积，避免重复 compute）
# ──────────────────────────────────────────────────────────────────────────────
def station_options(st: Station, nR=8, nP=6):
    Rs = np.linspace(R_LO, R_HI, nR); Ps = np.linspace(P_LO, P_HI, nP)
    opts = []
    for R in Rs:
        for P in Ps:
            e = eval_station(SIM, BRANCH, st, float(R), float(P))
            if e["feasible"]:
                opts.append((e["f1"], e["eens"], e["tx_mva"], float(R), float(P)))
    return opts


def nondominated(points):
    """points: list of (f1, f2, ...); 返回非支配子集。"""
    pts = sorted(points, key=lambda p: (p[0], p[1]))
    front = []; best_f2 = float("inf")
    for p in pts:
        if p[1] < best_f2 - 1e-9:
            front.append(p); best_f2 = p[1]
    return front


def station_pareto(st: Station, nR=60, nP=31):
    """单站 (f1, eens) 的可行非支配前沿（稠密网格≈真前沿）。返回 list[(f1, eens)]。"""
    Rs = np.linspace(R_LO, R_HI, nR); Ps = np.linspace(P_LO, P_HI, nP)
    pts = []
    for R in Rs:
        for P in Ps:
            e = eval_station(SIM, BRANCH, st, float(R), float(P))
            if e["feasible"]:
                pts.append((e["f1"], e["eens"]))
    return nondominated(pts)


def minkowski_true_front(stations, nR=60, nP=31):
    """无带约束(可分)县级真前沿 = 各站前沿的 Minkowski 和(逐站非支配剪枝)。返回[(f1万,f2MWh)]。"""
    acc = [(0.0, 0.0)]
    for st in stations:
        sf = station_pareto(st, nR, nP)
        acc = nondominated([(a + p[0], b + p[1]) for (a, b) in acc for p in sf])
    return [(a / 1e4, b / 1000.0) for (a, b) in acc]


def enumerate_true_front(stations, band=DEFAULT_BAND, nR=8, nP=6, cap=4_000_000):
    """笛卡尔积枚举县级方案，过 band 后取非支配真前沿。返回 (front, n_combos)。"""
    opt_tables = [station_options(st, nR, nP) for st in stations]
    n_combos = int(np.prod([len(o) for o in opt_tables])) if opt_tables else 0
    if n_combos == 0 or n_combos > cap:
        return None, n_combos
    coincident_mw = county_coincident_peak_kw(stations) / 1000.0
    county_pts = []
    for combo in itertools.product(*opt_tables):
        tx = sum(c[2] for c in combo)
        aggR = tx / coincident_mw
        if band[0] <= aggR <= band[1]:
            f1 = sum(c[0] for c in combo) / 1e4
            f2 = sum(c[1] for c in combo) / 1000.0
            county_pts.append((f1, f2, aggR))
    return nondominated(county_pts), n_combos


# ──────────────────────────────────────────────────────────────────────────────
# 基线
# ──────────────────────────────────────────────────────────────────────────────
def min_storage_to_pass(st: Station, R: float, pgrid=None):
    pgrid = pgrid if pgrid is not None else np.linspace(0, P_HI, 31)
    for P in pgrid:
        if eval_station(SIM, BRANCH, st, R, float(P))["feasible"]:
            return float(P)
    return None


def baseline_rigid(stations, R=2.0):
    """现行做法：全县统一刚性 R=2.0，越限站配最小储能过闸。返回 (f1_wan, f2_mwh, agg_R)。"""
    f1 = 0.0; f2 = 0.0; tx = []
    for st in stations:
        P = min_storage_to_pass(st, R) or P_HI
        e = eval_station(SIM, BRANCH, st, R, P)
        f1 += e["f1"]; f2 += e["eens"]; tx.append(e["tx_mva"])
    return f1 / 1e4, f2 / 1000.0, aggregate_capacity_load_ratio(stations, tx)


# ──────────────────────────────────────────────────────────────────────────────
# 指标
# ──────────────────────────────────────────────────────────────────────────────
def front_array(res):
    """非支配前沿目标数组；无可行解(res.F is None / 空)时返回空 (0,2) 数组。"""
    F = res.F
    if F is None or len(F) == 0:
        return np.empty((0, 2))
    F = np.atleast_2d(F)
    if F.shape[1] < 2:
        return np.empty((0, 2))
    return F[np.lexsort((F[:, 1], F[:, 0]))]


def ref_point(*fronts):
    allF = np.vstack([f for f in fronts if f is not None and len(f)])
    return allF.max(axis=0) * 1.1


# ──────────────────────────────────────────────────────────────────────────────
# 实验
# ──────────────────────────────────────────────────────────────────────────────
def E1_pareto(K=20, seed=0, pop=100, gen=200, solver=run_nsga2_enhanced):
    # 主结果用增强 NSGA-II（所提方法）；应用主算例 K=20
    county = build_county(K, seed=seed)
    res = solver(county, pop=pop, gen=gen, seed=1)
    F = front_array(res); X = np.atleast_2d(res.X)[np.lexsort((res.F[:, 1], res.F[:, 0]))]
    # knee：到理想点最小归一化距离
    ideal = F.min(axis=0); nadir = F.max(axis=0); span = np.where(nadir > ideal, nadir - ideal, 1)
    d = np.linalg.norm((F - ideal) / span, axis=1); ki = int(d.argmin())
    rows = [{"point": i, "f1_wan": round(F[i, 0], 1), "f2_eens_mwh": round(F[i, 1], 1),
             "is_knee": i == ki} for i in range(len(F))]
    pd.DataFrame(rows).to_csv(RESULTS / "ea_county_pareto.csv", index=False)
    # 拐点「一站一策」
    kx = X[ki]; per = evaluate_county(county, kx[:K], kx[K:], DEFAULT_BAND)
    strat = [{"station": st.sid, "slr": st.slr, "cd": st.cd, "peak_kw": round(st.peak_kw),
              "R_star": round(float(kx[j]), 2), "P_BESS_MW": round(float(kx[K + j]), 2),
              "route": ("升容载比增容" if kx[j] > 2.0 + 1e-6 else
                        ("配储为主" if kx[K + j] > 0.05 else "低容载比+强联络"))}
             for j, st in enumerate(county)]
    pd.DataFrame(strat).to_csv(RESULTS / "ea_county_strategy_knee.csv", index=False)
    print(f"[E1] K={K} 前沿 {len(F)} 点; 拐点 f1={F[ki,0]:.0f}万 f2={F[ki,1]:.0f}MWh "
          f"聚合容载比={per['agg_R']:.2f}")
    return county, res, F


def E2_validation(main_k=10, pop=100, gen=250, Ks=(3, 5), out="ea_validation.csv"):
    rows = []
    NO_BAND = (0.0, 1e9)
    # 求解器验证：『无带(可分)』小县上，所提(增强)与经典 NSGA-II 都应复现 Minkowski 真前沿（HV比≈1=parity）。
    for K in Ks:
        county = build_county(K, seed=0)
        TF = np.array(minkowski_true_front(county))            # 真前沿(无带)
        TF = TF[np.lexsort((TF[:, 1], TF[:, 0]))]
        for algo, runner in (("enhanced", run_nsga2_enhanced), ("classic", run_nsga2)):
            res = runner(county, band=NO_BAND, r220=None, pop=pop, gen=gen, seed=1)
            F = front_array(res); rp = ref_point(F, TF)
            hv_true = HV(ref_point=rp)(TF); hv_ea = HV(ref_point=rp)(F); igd = IGD(TF)(F)
            rows.append({"K": K, "algo": algo, "n_true_front": len(TF), "n_ea_front": len(F),
                         "HV_ratio": round(hv_ea / hv_true, 4) if hv_true else None,
                         "IGD": round(igd, 4)})
            print(f"[E2-验证] K={K} {algo}: 真前沿{len(TF)} EA{len(F)} "
                  f"HV比={hv_ea/hv_true:.4f} IGD={igd:.3f}", flush=True)
    pd.DataFrame(rows).to_csv(RESULTS / out, index=False)


def E2b_baseline(main_k=20):
    """刚性全县R=2.0基线 vs E1已存的(增强NSGA-II)前沿（复用，不重跑），输出节省%。K=20 与 E1 一致。"""
    county = build_county(main_k, seed=0)
    rb_f1, rb_f2, rb_R = baseline_rigid(county, 2.0)
    pf = pd.read_csv(RESULTS / "ea_county_pareto.csv")
    F = pf[["f1_wan", "f2_eens_mwh"]].values
    cand = F[F[:, 1] <= rb_f2 + 1e-6]                      # EA前沿上"风险≤刚性"的点
    ea_cost = float(cand[:, 0].min()) if len(cand) else float(F[:, 0].min())
    save = (rb_f1 - ea_cost) / rb_f1 * 100
    pd.DataFrame([{"K": main_k, "rigid_f1_wan": round(rb_f1, 1), "rigid_f2_mwh": round(rb_f2, 1),
                   "rigid_agg_R": round(rb_R, 2), "ea_f1_at_same_risk_wan": round(ea_cost, 1),
                   "ea_cost_saving_pct": round(save, 1)}]).to_csv(RESULTS / "ea_baseline.csv", index=False)
    print(f"[E2b] 刚性2.0: f1={rb_f1:.0f}万 f2={rb_f2:.0f}MWh 聚合R={rb_R:.2f}; "
          f"同风险下EA成本={ea_cost:.0f}万 节省{save:.1f}%")


def E3_band_effect(K=20, seed=0, pop=60, gen=120, solver=run_nsga2_enhanced):
    rows = []
    for band in [(1.6, 1.9), (1.8, 2.1), (2.0, 2.3), (2.2, 2.5)]:
        county = build_county(K, seed=seed)
        res = solver(county, band=band, pop=pop, gen=gen, seed=1)
        F = front_array(res)
        if len(F) == 0:        # 该带过紧/预算过小，未找到可行解
            rows.append({"band": f"[{band[0]},{band[1]}]", "n_front": 0,
                         "min_cost_wan": None, "min_eens_mwh": None, "knee_cost_wan": None})
            print(f"[E3] band[{band[0]},{band[1]}]: 无可行解")
            continue
        rows.append({"band": f"[{band[0]},{band[1]}]", "n_front": len(F),
                     "min_cost_wan": round(float(F[:, 0].min()), 1),
                     "min_eens_mwh": round(float(F[:, 1].min()), 1),
                     "knee_cost_wan": round(float(np.median(F[:, 0])), 1)})
        print(f"[E3] band[{band[0]},{band[1]}]: 前沿{len(F)}点 "
              f"成本下限{F[:,0].min():.0f}万 EENS下限{F[:,1].min():.0f}MWh")
    pd.DataFrame(rows).to_csv(RESULTS / "ea_band_effect.csv", index=False)


def E4_scaling(Ks=(2, 3, 5, 8, 12, 20, 40), pop=40, gen=40):
    rows = []
    for K in Ks:
        county = build_county(K, seed=0)
        # 穷举组合数（不实跑大K）：每站可行选项数^... 估计
        opt_counts = [len(station_options(st, 6, 5)) for st in county] if K <= 8 else None
        n_combos = int(np.prod(opt_counts)) if opt_counts else None
        t0 = time.perf_counter()
        run_nsga2(county, pop=pop, gen=gen, seed=1)
        dt = time.perf_counter() - t0
        rows.append({"K": K, "ea_seconds": round(dt, 1),
                     "enum_combos": n_combos,
                     "enum_note": "intractable(>1e8)" if (n_combos is None or n_combos > 1e8) else "tractable"})
        print(f"[E4] K={K}: NSGA-II {dt:.1f}s; 穷举组合={n_combos}")
    pd.DataFrame(rows).to_csv(RESULTS / "ea_scaling.csv", index=False)


def E5_convergence(K=8, seed=0, pop=60, gen=120, seeds=(1, 2, 3)):
    # 对照算法用 NSGA-III（同为约束可处理的 Pareto 类经典算法；pymoo 的 MOEAD 不支持约束）
    from pymoo.algorithms.moo.nsga3 import NSGA3
    from pymoo.util.ref_dirs import get_reference_directions
    county = build_county(K, seed=seed)
    # 共同参考点
    base = run_nsga2(county, pop=pop, gen=gen, seed=1)
    rp = ref_point(front_array(base))
    rows = []
    ref_dirs = get_reference_directions("das-dennis", 2, n_partitions=pop - 1)
    for algo_name in ("NSGA2", "NSGA3"):
        for s in seeds:
            prob = CountyProblem(county)
            if algo_name == "NSGA2":
                algo = NSGA2(pop_size=pop, sampling=LHS())
            else:
                algo = NSGA3(ref_dirs=ref_dirs, sampling=LHS())
            res = minimize(prob, algo, ("n_gen", gen), seed=s, verbose=False, save_history=True)
            hv_ind = HV(ref_point=rp)
            for h in res.history:
                F = h.opt.get("F")
                if F is not None and len(F):
                    rows.append({"algo": algo_name, "seed": s, "gen": h.n_gen,
                                 "hv": round(float(hv_ind(F)), 2)})
    pd.DataFrame(rows).to_csv(RESULTS / "ea_convergence.csv", index=False)
    df = pd.DataFrame(rows)
    fin = df[df.gen == df.gen.max()].groupby("algo")["hv"].agg(["mean", "std"])
    print(f"[E5] 末代 HV: \n{fin}")


def E6_robustness(seeds=range(6), K=20, pop=60, gen=120, solver=run_nsga2_enhanced):
    """多县实例鲁棒性（增强法，K=20）：跨随机县验证'相对刚性2.0的节省%'是否稳定。"""
    rows = []
    for s in seeds:
        county = build_county(K, seed=int(s))
        rb_f1, rb_f2, _ = baseline_rigid(county, 2.0)
        F = front_array(solver(county, pop=pop, gen=gen, seed=1))
        if len(F) == 0:
            continue
        cand = F[F[:, 1] <= rb_f2 + 1e-6]
        ea_cost = float(cand[:, 0].min()) if len(cand) else float(F[:, 0].min())
        save = (rb_f1 - ea_cost) / rb_f1 * 100
        rows.append({"seed": int(s), "rigid_f1_wan": round(rb_f1, 1),
                     "ea_f1_wan": round(ea_cost, 1), "saving_pct": round(save, 1)})
        print(f"[E6] county seed={s}: 省 {save:.1f}%", flush=True)
    df = pd.DataFrame(rows); df.to_csv(RESULTS / "ea_robustness.csv", index=False)
    sv = df["saving_pct"]
    print(f"[E6] {len(df)} 县：节省% mean {sv.mean():.1f} ± {sv.std():.1f}；"
          f"范围 [{sv.min():.1f}, {sv.max():.1f}]", flush=True)


def E7_system_constraint(K=20, seed=0, pop=100, gen=150):
    """系统潮流约束影响：未约束 vs 受约束前沿 + R220 敏感性（用增强求解器，收敛好、对比公平）。"""
    county = build_county(K, seed=seed)
    def solve(r220):
        return front_array(run_nsga2_enhanced(county, r220=r220, pop=pop, gen=gen, seed=1))
    F_unc = solve(None); F_con = solve(R220_DEFAULT)
    rp = ref_point(F_unc, F_con)
    rows = [{"case": "unconstrained(no system)", "min_cost_wan": round(float(F_unc[:, 0].min()), 1),
             "min_eens_mwh": round(float(F_unc[:, 1].min()), 1), "HV": round(HV(ref_point=rp)(F_unc), 1)},
            {"case": "constrained R220=1.8", "min_cost_wan": round(float(F_con[:, 0].min()), 1),
             "min_eens_mwh": round(float(F_con[:, 1].min()), 1), "HV": round(HV(ref_point=rp)(F_con), 1)}]
    for r in (1.6, 2.0):
        Fr = solve(r)
        rows.append({"case": f"constrained R220={r}", "min_cost_wan": round(float(Fr[:, 0].min()), 1),
                     "min_eens_mwh": round(float(Fr[:, 1].min()), 1), "HV": round(HV(ref_point=rp)(Fr), 1)})
    pd.DataFrame(rows).to_csv(RESULTS / "ea_system_constraint.csv", index=False)
    pd.DataFrame({"f1_unc": pd.Series(F_unc[:, 0]), "f2_unc": pd.Series(F_unc[:, 1]),
                  "f1_con": pd.Series(F_con[:, 0]), "f2_con": pd.Series(F_con[:, 1])}
                 ).to_csv(RESULTS / "ea_system_fronts.csv", index=False)
    dcost = float(F_con[:, 0].min()) - float(F_unc[:, 0].min())
    print(f"[E7] K={K}: 加系统约束后成本下限 {'+' if dcost>=0 else ''}{dcost:.0f}万（前沿外移）；R220敏感见csv", flush=True)


def _hv_curve(res, rp):
    hv = HV(ref_point=rp); out = []
    for h in res.history:
        F = h.opt.get("F")
        if F is not None and len(F):
            out.append((h.n_gen, float(hv(F))))
    return out


def E8_enhanced(K_list=(10, 20, 30, 40), pop=60, gen=100, seeds=(1, 2, 3)):
    """增强 vs 经典 NSGA-II vs NSGA-III（同问题含系统约束、同固定预算）：HV收敛曲线 + 末代HV比 随K扩大。"""
    rows = []
    for K in K_list:
        county = build_county(K, seed=0)
        res_map = {}; finals = []
        for algo, runner in (("classic", run_nsga2), ("nsga3", run_nsga3),
                             ("enhanced", run_nsga2_enhanced)):
            for s in seeds:
                res = runner(county, r220=R220_DEFAULT, pop=pop, gen=gen, seed=s, save_hist=True)
                res_map[(algo, s)] = res; finals.append(front_array(res))
        rp = ref_point(*finals)
        for (algo, s), res in res_map.items():
            for g, hv in _hv_curve(res, rp):
                rows.append({"K": K, "algo": algo, "seed": s, "gen": g, "hv": round(hv, 2)})
        sub = pd.DataFrame([r for r in rows if r["K"] == K]); fin = sub[sub.gen == sub.gen.max()]
        m = fin.groupby("algo").hv.mean()
        cl = float(m.get("classic", 0)); n3 = float(m.get("nsga3", 0)); en = float(m.get("enhanced", 0))
        print(f"[E8] K={K}: 末代HV 经典{cl:.0f} / NSGA-III{n3:.0f} / 增强{en:.0f}  "
              f"增强/经典={en/max(1.0,cl):.3f} 增强/NSGA3={en/max(1.0,n3):.3f}", flush=True)
        pd.DataFrame(rows).to_csv(RESULTS / "ea_enhanced.csv", index=False)   # 增量落盘，断点不丢


def E8c_fronts(K_list=(10, 20, 30, 40), pop=60, gen=100, seed=1):
    """捕获各 K 下 经典 / NSGA-III / 增强 的末代帕累托前沿点（同问题同固定预算同 seed），供前沿叠加对比图。"""
    rows = []
    for K in K_list:
        county = build_county(K, seed=0)
        for algo, runner in (("classic", run_nsga2), ("nsga3", run_nsga3),
                             ("enhanced", run_nsga2_enhanced)):
            F = front_array(runner(county, r220=R220_DEFAULT, pop=pop, gen=gen, seed=seed))
            for f1, f2 in F:
                rows.append({"K": K, "algo": algo, "f1_wan": round(float(f1), 1),
                             "f2_mwh": round(float(f2), 2)})
        print(f"[E8c] K={K}: 前沿点已捕获", flush=True)
        pd.DataFrame(rows).to_csv(RESULTS / "ea_enhanced_fronts.csv", index=False)


def dump_enhanced_summary():
    """从 ea_enhanced.csv 派生末代 HV 汇总（每 K：经典/增强 末代 HV mean±std + 比值），
    写 ea_enhanced_summary.csv —— 让头条比值有直接可读的源。"""
    f = RESULTS / "ea_enhanced.csv"
    if not f.exists():
        print("[summary] ea_enhanced.csv 不存在", flush=True); return
    df = pd.read_csv(f); rows = []
    for K, g in df.groupby("K"):
        fin = g[g.gen == g.gen.max()]; st = fin.groupby("algo").hv.agg(["mean", "std", "count"])
        cl = st.loc["classic"] if "classic" in st.index else None
        n3 = st.loc["nsga3"] if "nsga3" in st.index else None
        en = st.loc["enhanced"] if "enhanced" in st.index else None
        rows.append({"K": int(K), "n_seed": int(en["count"]) if en is not None else None,
                     "classic_HV_mean": round(cl["mean"], 1) if cl is not None else None,
                     "classic_HV_std": round(cl["std"], 1) if cl is not None else None,
                     "nsga3_HV_mean": round(n3["mean"], 1) if n3 is not None else None,
                     "nsga3_HV_std": round(n3["std"], 1) if n3 is not None else None,
                     "enhanced_HV_mean": round(en["mean"], 1) if en is not None else None,
                     "enhanced_HV_std": round(en["std"], 1) if en is not None else None,
                     "ratio_enh_over_cls": round(en["mean"] / cl["mean"], 3)
                     if (cl is not None and en is not None and cl["mean"]) else None,
                     "ratio_enh_over_nsga3": round(en["mean"] / n3["mean"], 3)
                     if (n3 is not None and en is not None and n3["mean"]) else None})
    pd.DataFrame(rows).to_csv(RESULTS / "ea_enhanced_summary.csv", index=False)
    print("[summary] -> results/ea_enhanced_summary.csv", flush=True)
    print(pd.DataFrame(rows).to_string(index=False), flush=True)


if __name__ == "__main__":
    what = sys.argv[1:] or ["core"]
    if what == ["quick"]:        # 仅验证管线/图表能跑通，预算极小，结果无意义
        E1_pareto(K=4, pop=16, gen=12)
        E2_validation(main_k=4, pop=16, gen=12)
        E3_band_effect(K=4, pop=16, gen=12)
        E4_scaling(Ks=(2, 3, 4), pop=12, gen=10)
        E5_convergence(K=4, pop=16, gen=12, seeds=(1, 2))
    elif what == ["core"]:       # 头条：E1 县级前沿 + E2 验证/基线
        E1_pareto(); E2_validation()
    elif what == ["all"]:
        E1_pareto(); E2_validation(); E3_band_effect(); E4_scaling(); E5_convergence()
    elif what == ["full"]:       # 顺序跑全部 + 基线 + 出图，一条命令到底
        print(">>> E1", flush=True); E1_pareto()
        print(">>> E2", flush=True); E2_validation()
        print(">>> E2b", flush=True); E2b_baseline()
        print(">>> E3", flush=True); E3_band_effect()
        print(">>> E4", flush=True); E4_scaling()
        # E5(NSGA-II vs NSGA-III) 已按用户决定剔除（不需要 NSGA-III）；算法对照走 E8 增强vs经典
        print(">>> FIGURES", flush=True)
        import ea_figures
        for fn in (ea_figures.fig_pareto, ea_figures.fig_strategy, ea_figures.fig_scaling,
                   ea_figures.fig_band):
            try:
                fn()
            except Exception as e:
                print(f"  fig error: {e}", flush=True)
        print(">>> FULL PIPELINE + FIGURES DONE", flush=True)
    elif what == ["stage3"]:     # 阶段三：系统约束影响(E7) + 增强vs经典(E8) + 出图
        print(">>> E7 系统约束影响", flush=True); E7_system_constraint()
        print(">>> E8 增强vs经典(大K)", flush=True); E8_enhanced()
        print(">>> E8c 前沿捕获", flush=True); E8c_fronts()
        print(">>> 汇总 HV", flush=True); dump_enhanced_summary()
        print(">>> FIGURES", flush=True)
        import ea_figures
        for fn in (ea_figures.fig_system_constraint, ea_figures.fig_scaling_gap,
                   ea_figures.fig_enhanced_convergence, ea_figures.fig_front_compare):
            try:
                fn()
            except Exception as e:
                print(f"  fig error: {e}", flush=True)
        print(">>> STAGE3 DONE", flush=True)
    else:
        fns = {"e1": E1_pareto, "e2": E2_validation, "e2b": E2b_baseline,
               "e3": E3_band_effect, "e4": E4_scaling, "e5": E5_convergence,
               "e6": E6_robustness, "e7": E7_system_constraint, "e8": E8_enhanced,
               "e8c": E8c_fronts, "summary": dump_enhanced_summary}
        for w in what:
            fns[w]()
    print("[done]")
