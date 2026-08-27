#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
三地对照算例（论文§4.2）：徐州 / 嘉兴(浙江) / 莱芜(山东)

用真实PVGIS 16年小时曲线为每个地区计算：
  - 年发电量、容量因子
  - 区域专属的年反送小时数 t_rev（PV曲线 + 简化日负荷叠加）
然后以区域校准参数运行方案A/B对比，展示"一片一策"跨区域差异。

输出：
- results/regional_cases.csv
- results/figures/fig8_regional.png
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lcc_simulator import (
    LCCSimulator, load_cost_params, load_ieee33,
    make_plan_a, make_plan_b, DEFAULT_PV_BUSES, DEFAULT_CD,
)
from pv_profile_analyzer import load_pv, basic_stats, reverse_hours

REGIONS = {
    "徐州": ROOT / "datasets" / "pv_profiles" / "xuzhou_tmy.csv",
    "嘉兴": ROOT / "datasets" / "pv_profiles" / "jiaxing_tmy.csv",
    "莱芜": ROOT / "datasets" / "pv_profiles" / "laiwu_tmy.csv",
}

PV_KWP = 9500          # 源荷比≈2.56：反向承载力校核下 R_min=2.6，正处"升容载比增容↔配储"翻转带，
                       # 故反送时长 t_rev 能决定治理路线（短→增容、长→配储）；PV=11000(源荷比3)会被承载力一刀切
LOAD_PEAK_KW = 3715    # 与IEEE33峰荷一致
LOAD_MIN_KW = LOAD_PEAK_KW * 0.3


def _two_options(sim, bus, branch, peak, t_rev):
    """返回(纯主变升容载比增容最优, 刚性2.0+配储)两方案在给定反送时长下的结果。"""
    from sweep_experiments import build_candidate, build_storage_plan, CANDIDATE_R
    results = {r: sim.compute(bus, branch,
                   build_candidate(r, PV_KWP, peak, LOAD_PEAK_KW, DEFAULT_CD),
                   loss_hours_rev=t_rev) for r in CANDIDATE_R}
    feas = {r: res for r, res in results.items() if res.reverse_check_passed}
    elastic = (min(feas.values(), key=lambda x: x.annualized_cost_yuan_per_year)
               if feas else None)
    storage = sim.compute(bus, branch,
                  build_storage_plan(PV_KWP, peak, LOAD_PEAK_KW, DEFAULT_CD),
                  loss_hours_rev=t_rev)
    return elastic, storage


def run():
    cost = load_cost_params()
    bus, branch = load_ieee33()
    sim = LCCSimulator(cost)
    peak = math.hypot(bus["p_load_kw"].sum(), bus["q_load_kvar"].sum()) / 1000

    # 1) 三地实测反送时长（PVGIS 16年）
    regions = {}
    for region, csv_path in REGIONS.items():
        if not csv_path.exists():
            print(f"[SKIP] {region}: {csv_path} 不存在")
            continue
        pv_df = load_pv(csv_path)
        stats = basic_stats(pv_df, installed_kwp=PV_KWP)
        rev = reverse_hours(pv_df, PV_KWP, LOAD_PEAK_KW, LOAD_MIN_KW)
        regions[region] = {
            "t_rev": rev["reverse_hours_per_year"],
            "rev_energy_mwh": rev["reverse_energy_kwh_per_year"] / 1000,
            "yield": stats["annual_yield_per_kwp"],
            "cf": stats["capacity_factor_pct"],
        }

    # 2) 反送时长扫描（固定 PV，源荷比≈2.56）：升容载比增容 vs 刚性2.0+配储 的成本翻转
    grid = list(range(1000, 3601, 200))
    sweep = []
    for tr in grid:
        el, st = _two_options(sim, bus, branch, peak, tr)
        el_ann = el.annualized_cost_yuan_per_year / 1e4 if el else float("nan")
        st_ann = st.annualized_cost_yuan_per_year / 1e4
        sweep.append({
            "t_rev": tr,
            "elastic_R": (el.capacity_load_ratio if el else None),
            "elastic_annual_wan": round(el_ann, 2),
            "storage_annual_wan": round(st_ann, 2),
            "winner": ("升容载比增容" if (el and el_ann < st_ann) else "刚性2.0+配储"),
        })
    sweep_df = pd.DataFrame(sweep)
    (ROOT / "results").mkdir(parents=True, exist_ok=True)
    sweep_df.to_csv(ROOT / "results" / "regional_trev_sweep.csv", index=False)

    # 3) 三地按各自实测 t_rev 落点
    rows = []
    for region, info in regions.items():
        el, st = _two_options(sim, bus, branch, peak, info["t_rev"])
        el_ann = el.annualized_cost_yuan_per_year / 1e4 if el else float("nan")
        st_ann = st.annualized_cost_yuan_per_year / 1e4
        win_storage = not (el and el_ann < st_ann)
        rows.append({
            "region": region,
            "annual_yield_kwh_per_kwp": info["yield"],
            "capacity_factor_pct": info["cf"],
            "reverse_hours_per_year": round(info["t_rev"], 0),
            "reverse_energy_mwh_per_year": round(info["rev_energy_mwh"], 1),
            "feasible_min_R": (el.capacity_load_ratio if el else None),
            "best_tech": ("刚性2.0+配储(方案A)" if win_storage
                          else f"升容载比{el.capacity_load_ratio:g}增容"),
            "best_annual_wan": round(st_ann if win_storage else el_ann, 2),
        })
    df = pd.DataFrame(rows)
    df.to_csv(ROOT / "results" / "regional_cases.csv", index=False)
    flips = [(sweep[i-1]["t_rev"], sweep[i]["t_rev"]) for i in range(1, len(sweep))
             if sweep[i-1]["winner"] != sweep[i]["winner"]]
    print(f"[OK] regional_cases.csv + regional_trev_sweep.csv "
          f"(PV={PV_KWP}, 源荷比≈{PV_KWP/LOAD_PEAK_KW:.2f}); 翻转区间t_rev={flips}")
    print(df.to_string(index=False))
    return sweep_df, df, regions


def plot(sweep_df, region_df, regions):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from generate_figures import setup_fonts, L
    setup_fonts()

    t = sweep_df["t_rev"]
    el = sweep_df["elastic_annual_wan"]
    st = sweep_df["storage_annual_wan"]
    r_el = sweep_df["elastic_R"].dropna()
    r_label = f"{r_el.iloc[0]:g}" if len(r_el) else "2.6"

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.plot(t, el, "o-", color="#e67e22", lw=2,
            label=L(f"升容载比增容（纯主变 R={r_label}）", f"Elastic uprate (R={r_label})"))
    ax.plot(t, st, "s-", color="#2980b9", lw=2,
            label=L("刚性2.0+配储（方案A）", "Rigid 2.0 + storage (Plan A)"))

    # 翻转点
    win = sweep_df["winner"].tolist(); tv = sweep_df["t_rev"].tolist()
    flip = next(((tv[i-1]+tv[i])/2 for i in range(1, len(win)) if win[i] != win[i-1]), None)
    if flip is not None:
        ax.axvline(flip, color="grey", ls="--", lw=1)
        ax.text(flip, ax.get_ylim()[1]*0.999, L(f"翻转≈{flip:.0f}h", f"flip≈{flip:.0f}h"),
                ha="center", va="top", fontsize=9, color="grey")

    # 三地按实测 t_rev 标线（按 t_rev 排序后竖排错位，避免相近标签重叠）
    cols = {"徐州": "#c0392b", "嘉兴": "#27ae60", "莱芜": "#8e44ad"}
    ylo, yhi = ax.get_ylim()
    for k, (region, info) in enumerate(sorted(regions.items(), key=lambda kv: kv[1]["t_rev"])):
        ax.axvline(info["t_rev"], color=cols.get(region, "#555"), ls=":", lw=1.5, alpha=0.85)
        yy = ylo + (yhi - ylo) * (0.06 + 0.10 * k)
        ax.text(info["t_rev"], yy, f"{region} {info['t_rev']:.0f}h",
                rotation=90, va="bottom", ha="right", fontsize=8.5,
                color=cols.get(region, "#555"))

    ax.set_xlabel(L("年反送时长 t_rev (h)", "Annual reverse-flow hours t_rev"))
    ax.set_ylabel(L("年化成本 (万元/年)", "Annualized cost (10k CNY/yr)"))
    ax.set_title(L(f"反送时长决定治理路线（源荷比≈{PV_KWP/LOAD_PEAK_KW:.2f}，校核下 R_min={r_label}）",
                   "Reverse-flow duration determines the treatment route"), fontsize=12)
    ax.legend(loc="upper left")
    plt.tight_layout()
    out = ROOT / "results" / "figures" / "fig8_regional.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


if __name__ == "__main__":
    sweep_df, region_df, regions = run()
    if regions:
        plot(sweep_df, region_df, regions)
