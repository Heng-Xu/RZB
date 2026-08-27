#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
扫描实验 v3（相关性修复版）：生成论文§4数据。

v3 修复（对应 分析/06 相关性背书 X1-X4）：
  - A/B扫描走 v3 的触发式 make_plan_a（低渗透A=纯主变，高渗透才配储）→
    曲线呈"低渗透A优 / 中高渗透B优 / 极高渗透回A"三区段，叙事与导则兼容
  - 候选R统一构造 build_candidate()：刚性档配储按反送超限量触发（X1）；
    所有候选传入联络度CD → 可靠性成本随CD变化（X3+X4）→ 推荐R对三轴都敏感
  - PV范围扩到源荷比≈4，完整覆盖三区段
  - 双口径（源荷比/电量渗透率）保留

输出：
- results/sweep_penetration.csv
- results/sweep_pv_tx.csv
- results/decision_matrix_raw.csv
"""

from __future__ import annotations

import argparse
import math
import sys
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lcc_simulator import (
    LCCSimulator, ScenarioConfig, load_cost_params, load_ieee33,
    make_plan_a, make_plan_b, DEFAULT_PV_BUSES, DEFAULT_CD,
    RIGID_RATIO, _reverse_overload_kw,
)


def _peak(bus):
    pk = float(bus["p_load_kw"].sum())
    pm = math.hypot(pk, bus["q_load_kvar"].sum()) / 1000
    return pk, pm


CANDIDATE_R = [1.5, 1.8, 2.0, 2.3, 2.6]


def build_candidate(r, pv_kwp, peak_mva, peak_kw, cd, link_km_if_rigid=2.0):
    """
    纯主变容载比R方案（矫正版：无自动配储、无弃光救济）：tx=R×峰荷(有功口径)。
    反送是否越限交由 compute() 的反向承载力校核判定——越限的纯主变方案将被准入硬闸淘汰。
    R>2.0 的增量按扩容系数计价。配储治反送作为独立方案 build_storage_plan（甲方方案A）单列，
    以消除"治理在R上自动不对称分配"的根因（旧版储能只给低R→任何硬闸都会反转升方向）。
    link_km_if_rigid 仅为向后兼容保留，纯主变不补联络线。
    """
    tx = (peak_kw / 1000) * r   # 有功口径定容（国标容载比 Rs=容量MVA/有功MW）
    expansion = (peak_kw / 1000) * RIGID_RATIO if r > RIGID_RATIO else 0.0
    return ScenarioConfig(
        name=f"R{r}_纯主变", tx_capacity_mva=tx, pv_kwp_total=pv_kwp,
        pv_buses=DEFAULT_PV_BUSES, with_storage=False, line_expansion_km=0.0,
        expansion_from_mva=expansion, interconnection_cd=cd)


def build_storage_plan(pv_kwp, peak_mva, peak_kw, cd, link_km=2.0, r=RIGID_RATIO):
    """甲方方案A：刚性R=2.0 + 配储(按反送超限量) + 联络。储能吸收反送→可过反向重载校核。"""
    tx = (peak_kw / 1000) * r
    mw = max(0.0, _reverse_overload_kw(pv_kwp, peak_kw, tx) / 1000)
    return ScenarioConfig(
        name="方案A_刚性2.0_配储", tx_capacity_mva=tx, pv_kwp_total=pv_kwp,
        pv_buses=DEFAULT_PV_BUSES, with_storage=(mw > 0),
        storage_mwh=mw * 2.0, storage_mw=mw,
        line_expansion_km=link_km, interconnection_cd=cd)


def select_by_gate(sim, bus, branch, pv_kwp, peak_mva, peak_kw, cd,
                   loss_hours_rev=None, link_km=2.0):
    """
    两阶段选优：① 纯主变各R先过"反向重载准入硬闸"，越限者淘汰；配储方案(方案A)恒可行；
                ② 在幸存方案里取年化成本最小。
    返回 dict：best_key/best/results/res_a/rigid/r_min_bare/voltage_exceed/n_feasible。
    """
    results = {r: sim.compute(bus, branch,
                              build_candidate(r, pv_kwp, peak_mva, peak_kw, cd),
                              loss_hours_rev=loss_hours_rev)
               for r in CANDIDATE_R}
    res_a = sim.compute(bus, branch,
                        build_storage_plan(pv_kwp, peak_mva, peak_kw, cd, link_km),
                        loss_hours_rev=loss_hours_rev)
    survivors = {f"R{r}": results[r] for r in CANDIDATE_R if results[r].reverse_check_passed}
    if res_a.reverse_check_passed or not survivors:
        survivors["A储"] = res_a            # 配储方案恒可行（兜底亦取它）
    best_key = min(survivors, key=lambda k: survivors[k].annualized_cost_yuan_per_year)
    passed_r = [r for r in CANDIDATE_R if results[r].reverse_check_passed]
    # 刚性2.0基线=严格执行2.0(纯主变可行则用之，否则用方案A配储)，对应甲方方案A口径
    rigid = results[RIGID_RATIO] if results[RIGID_RATIO].reverse_check_passed else res_a
    return {
        "best_key": best_key, "best": survivors[best_key],
        "results": results, "res_a": res_a, "rigid": rigid,
        "r_min_bare": (min(passed_r) if passed_r else None),
        "n_feasible": len(passed_r),
        "voltage_exceed": any(results[r].voltage_exceed for r in CANDIDATE_R),
    }


def sweep_penetration(out_dir, cd=DEFAULT_CD):
    """
    G0修复：主图改为"决策矩阵自适应R vs 刚性R=2.0"——真正检验"一片一策"方法。
    每个渗透点：在候选R{1.5..2.6}中取年化成本最小者(=决策矩阵的选择)，与刚性2.0对比。
    自适应在低渗透段选 R<2.0（小主变省钱）、高渗透段选 R>2.0（避反送/弃光），
    呈"弹性双向"；节省=刚性2.0成本−自适应成本（恒≥0，因2.0是候选之一）。
    旧版"固定2.0 vs 固定2.3"未调用决策方法，已废弃。
    """
    cost = load_cost_params(); bus, branch = load_ieee33(); sim = LCCSimulator(cost)
    pk, pm = _peak(bus)
    pv_list = [500, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000,
               9000, 10000, 11000, 12000, 13000, 14000]
    rows = []
    for pv in pv_list:
        sel = select_by_gate(sim, bus, branch, pv, pm, pk, cd)
        rigid, adapt = sel["rigid"], sel["best"]
        is_stor = sel["best_key"] == "A储"
        best_r = adapt.capacity_load_ratio
        saving = rigid.annualized_cost_yuan_per_year - adapt.annualized_cost_yuan_per_year
        direction = ("刚性2.0+配储" if is_stor else
                     "降容载比" if best_r < RIGID_RATIO else
                     "升容载比" if best_r > RIGID_RATIO else "维持2.0")
        rows.append({
            "pv_kwp": pv,
            "source_load_ratio": rigid.source_load_ratio,
            "energy_penetration_pct": round(adapt.energy_penetration * 100, 1),
            "rigid_R": RIGID_RATIO,
            "rigid_annual_wan": round(rigid.annualized_cost_yuan_per_year / 1e4, 2),
            "adaptive_R": round(best_r, 2),
            "adaptive_scheme": "刚性2.0+配储" if is_stor else f"纯主变R{best_r:g}",
            "adaptive_annual_wan": round(adapt.annualized_cost_yuan_per_year / 1e4, 2),
            "saving_wan_year": round(saving / 1e4, 2),
            "saving_pct": (round(saving / rigid.annualized_cost_yuan_per_year * 100, 2)
                           if rigid.annualized_cost_yuan_per_year else 0),
            "r_min_bare": sel["r_min_bare"],      # 纯主变承载力下限（过反向重载的最低R）
            "n_feasible_R": sel["n_feasible"],
            "voltage_exceed_flag": sel["voltage_exceed"],
            "adapt_storage_capex_wan": round(adapt.storage_capex_yuan / 1e4, 2),
            "direction": direction,
        })
    df = pd.DataFrame(rows)
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "sweep_penetration.csv", index=False)
    stor = df.adaptive_scheme.str.contains("配储").sum()
    allfail = df.r_min_bare.isna().sum()
    print(f"[OK] sweep_penetration.csv: {len(df)} rows; 配储胜出={stor}点; "
          f"纯主变全越限(需配储)={allfail}点; 最大节省={df.saving_wan_year.max():.1f}万/年")
    return df


def sweep_pv_tx(out_dir):
    cost = load_cost_params(); bus, branch = load_ieee33(); sim = LCCSimulator(cost)
    pk, pm = _peak(bus)
    pv_list = [2000, 4000, 6000, 8000, 10000, 12000, 14000]
    ratios = [1.5, 1.8, 2.0, 2.3, 2.6]
    rows = []
    for pv, r in product(pv_list, ratios):
        res = sim.compute(bus, branch, build_candidate(r, pv, pm, pk, DEFAULT_CD))
        rows.append({
            "pv_kwp": pv, "cap_load_ratio": r,
            "source_load_ratio": res.source_load_ratio,
            "energy_penetration_pct": round(res.energy_penetration * 100, 1),
            "reverse_check_passed": res.reverse_check_passed,    # 裸主变反向重载校核
            "reverse_overload_kw": res.reverse_overload_kw,
            "max_reverse_voltage_pu": res.max_reverse_voltage_pu,
            "Z1_wan": round(res.Z1_yuan / 1e4, 2),
            "Z4_transformer_wan": round(res.Z4_transformer_yuan / 1e4, 2),
            "Z4_rev_share_pct": round(res.Z4_reverse_share * 100, 2),
            "reliability_wan": round(res.reliability_yuan_per_year / 1e4, 2),
            "annual_cost_wan_year": round(res.annualized_cost_yuan_per_year / 1e4, 2),
        })
    df = pd.DataFrame(rows)
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "sweep_pv_tx.csv", index=False)
    print(f"[OK] sweep_pv_tx.csv: {len(df)} rows")
    return df


def build_decision_matrix(out_dir):
    """
    27格：(源荷比 × 电量渗透率档 × 联络度) → 最优容载比R + 推荐区间 + 技术方案。
    每格在候选R∈{1.5..2.6}中取年化成本最小者；CD经N-1可靠性影响低R可行性（X3）。
    basis如实标注"IEEE33参数扫描"；徐州实测/等百分位校验属B轨。
    """
    cost = load_cost_params(); bus, branch = load_ieee33(); sim = LCCSimulator(cost)
    pk, pm = _peak(bus)

    sl_axis = [("低", 0.6), ("中", 1.8), ("高", 3.2)]
    pe_axis = [("低", 1000), ("中", 1362), ("高", 1900)]   # 反送小时数代理电量渗透率档
    cd_axis = [("弱", 0.15), ("中", 0.45), ("强", 0.80)]
    candidate_r = [1.5, 1.8, 2.0, 2.3, 2.6]

    rows = []
    for (sl_l, sl_v), (pe_l, t_rev), (cd_l, cd_v) in product(sl_axis, pe_axis, cd_axis):
        pv_kwp = sl_v * pk
        # 联络度越强，配储方案补建联络越少
        link_km = {0.15: 3.0, 0.45: 2.0, 0.80: 0.8}[cd_v]
        sel = select_by_gate(sim, bus, branch, pv_kwp, pm, pk, cd_v,
                             loss_hours_rev=t_rev, link_km=link_km)
        best = sel["best"]; is_stor = sel["best_key"] == "A储"
        best_r = best.capacity_load_ratio
        r_low, r_high = max(1.5, best_r - 0.2), min(2.6, best_r + 0.2)

        if is_stor:
            tech = "刚性2.0+配储治反送（纯主变越限→方案A）"
        elif best_r > RIGID_RATIO:
            tech = "主变弹性增容"
        elif best_r < RIGID_RATIO:
            tech = "降容载比（强联络互济支撑）"
        else:
            tech = "维持刚性2.0"

        rows.append({
            "source_load_level": sl_l, "source_load_value": sl_v,
            "penetration_level": pe_l, "t_rev_hours": t_rev,
            "interconnection_level": cd_l, "interconnection_value": cd_v,
            "pv_kwp_eff": round(pv_kwp, 1),
            "best_cap_load_ratio": round(best_r, 2),
            "recommended_range": f"[{r_low:.1f}, {r_high:.1f}]",
            "best_annual_cost_wan": round(best.annualized_cost_yuan_per_year / 1e4, 2),
            "reliability_wan": round(best.reliability_yuan_per_year / 1e4, 2),
            "r_min_bare": sel["r_min_bare"],      # 反向承载力下限（过反向重载的最低纯主变R）
            "n_feasible_R": sel["n_feasible"],
            "gate_scheme": "配储(方案A)" if is_stor else "纯主变",
            "voltage_exceed_flag": sel["voltage_exceed"],
            "tech_scheme": tech,
            "basis": "IEEE33参数扫描·经反向承载力校核",
        })
    df = pd.DataFrame(rows)
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "decision_matrix_raw.csv", index=False)
    nR = df["best_cap_load_ratio"].nunique()
    stor = (df.gate_scheme == "配储(方案A)").sum()
    vflag = int(df.voltage_exceed_flag.sum())
    print(f"[OK] decision_matrix_raw.csv: {len(df)} cells, {nR} distinct R; "
          f"配储(方案A)胜出格={stor}/27; 电压旗标格={vflag}/27")
    return df


def dump_reverse_check(out_dir):
    """逐(PV×纯主变R)记录反向承载力校核明细：反向越限量、是否过闸、最大反送电压(片区旗标)。"""
    cost = load_cost_params(); bus, branch = load_ieee33(); sim = LCCSimulator(cost)
    pk, pm = _peak(bus)
    pv_list = [1000, 2000, 3000, 4000, 5000, 6000, 8000, 10000, 12000, 14000]
    rows = []
    for pv in pv_list:
        for r in CANDIDATE_R:
            res = sim.compute(bus, branch, build_candidate(r, pv, pm, pk, DEFAULT_CD))
            rows.append({
                "pv_kwp": pv, "source_load_ratio": round(pv / pk, 2),
                "cap_load_ratio": r,
                "reverse_overload_kw": res.reverse_overload_kw,
                "reverse_check_passed": res.reverse_check_passed,
                "max_reverse_voltage_pu": res.max_reverse_voltage_pu,
                "voltage_exceed": res.voltage_exceed,
            })
    df = pd.DataFrame(rows)
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "reverse_capacity_check.csv", index=False)
    print(f"[OK] reverse_capacity_check.csv: {len(df)} rows; "
          f"纯主变过反向重载闸={int(df.reverse_check_passed.sum())}/{len(df)}; "
          f"电压旗标越限={int(df.voltage_exceed.sum())}/{len(df)}")
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "results")
    ap.add_argument("--what", choices=["all", "pv_tx", "penetration", "matrix", "check"],
                    default="all")
    args = ap.parse_args()
    if args.what in ("all", "penetration"):
        sweep_penetration(args.out)
    if args.what in ("all", "pv_tx"):
        sweep_pv_tx(args.out)
    if args.what in ("all", "matrix"):
        build_decision_matrix(args.out)
    if args.what in ("all", "check"):
        dump_reverse_check(args.out)
    print("\n[DONE] sweep experiments (反向承载力校核版) complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
