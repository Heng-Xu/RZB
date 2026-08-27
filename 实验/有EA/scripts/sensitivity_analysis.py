#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
经济参数敏感性分析（论文§4.3）：
  - 折现率 4% / 5% / 6% / 7% / 8%（5档）
  - 储能成本系数 1.0 / 0.7 / 0.5（基线 / 30%下行 / 50%下行）
  - 在 3 个代表性渗透率水平（PV=2500/5000/8000 kWp）下做方案A/B对比

核心问题：储能成本大幅下行后，"刚性+配储"（方案A）是否会反超"弹性+增容"（方案B）？
这是审稿人必问的问题（分析/04 报告 S3 风险项），必须有定量回答。

输出：
- results/sensitivity_econ.csv
- results/figures/fig7_sensitivity_econ.png
"""

from __future__ import annotations

import math
import sys
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lcc_simulator import (
    LCCSimulator, load_cost_params, load_ieee33, DEFAULT_CD,
)
from sweep_experiments import build_candidate, CANDIDATE_R, select_by_gate


def run() -> pd.DataFrame:
    base_cost = load_cost_params()
    bus, branch = load_ieee33()
    peak_kw = float(bus["p_load_kw"].sum())
    peak = math.hypot(peak_kw, bus["q_load_kvar"].sum()) / 1000

    discount_rates = [0.04, 0.05, 0.06, 0.07, 0.08]
    storage_factors = [1.0, 0.7, 0.5]
    # PV档定位在"弹性活跃且配储参与比选"的带（源荷比≈2.42/2.56/2.69，校核下纯主变升容载比R2.3~2.6
    # 仍可行、与刚性2.0+配储竞争）——正好检验"储能降价后 刚性2.0+配储 能否抹平 升容载比增容 的优势"。
    # 源荷比≥2.96 时纯主变全越限、两者同为配储而节省恒0，不取。
    pv_levels = [9000, 9500, 10000]

    rows = []
    for dr, sf, pv in product(discount_rates, storage_factors, pv_levels):
        cost = load_cost_params()
        cost["economics"]["discount_rate"] = dr
        # 储能成本下行：直接缩放单价
        cost["storage_BESS"]["energy_cost_yuan_per_kwh"] = (
            base_cost["storage_BESS"]["energy_cost_yuan_per_kwh"] * sf)
        cost["storage_BESS"]["power_cost_yuan_per_kw"] = (
            base_cost["storage_BESS"]["power_cost_yuan_per_kw"] * sf)
        sim = LCCSimulator(cost)

        # 与主结果一致：经反向承载力校核的两阶段选优（纯主变过闸 + 配储方案）vs 严格刚性2.0
        sel = select_by_gate(sim, bus, branch, pv, peak, peak_kw, DEFAULT_CD)
        rigid = sel["rigid"]; adapt = sel["best"]; best_r = adapt.capacity_load_ratio
        saving = rigid.annualized_cost_yuan_per_year - adapt.annualized_cost_yuan_per_year
        rows.append({
            "discount_rate": dr,
            "storage_cost_factor": sf,
            "pv_kwp": pv,
            "energy_penetration_pct": round(rigid.energy_penetration * 100, 1),
            "rigid_annual_wan": round(rigid.annualized_cost_yuan_per_year / 1e4, 2),
            "adaptive_R": best_r,
            "adaptive_annual_wan": round(adapt.annualized_cost_yuan_per_year / 1e4, 2),
            "saving_wan_year": round(saving / 1e4, 2),
            "elastic_active": best_r != 2.0,
        })

    df = pd.DataFrame(rows)
    out = ROOT / "results" / "sensitivity_econ.csv"
    df.to_csv(out, index=False)
    print(f"[OK] {out}: {len(df)} rows")

    # 结论稳健性统计：自适应相对刚性2.0是否仍有节省、弹性是否仍激活
    n_active = df["elastic_active"].sum()
    print(f"弹性激活(自适应R≠2.0)组合：{n_active}/{len(df)} ({n_active/len(df)*100:.0f}%)")
    collapsed = df[~df["elastic_active"]]
    if not collapsed.empty:
        print("⚠ 弹性优势被抹平（自适应回落到刚性2.0）的组合：")
        print(collapsed[["discount_rate", "storage_cost_factor", "pv_kwp",
                         "saving_wan_year"]].to_string(index=False))
    else:
        print("✅ 全部组合自适应R均≠2.0（弹性优势对折现率与储能成本稳健）")
    print(f"   节省裕度范围：{df['saving_wan_year'].min():.1f} ~ "
          f"{df['saving_wan_year'].max():.1f} 万/年")
    return df


def plot(df: pd.DataFrame):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from generate_figures import setup_fonts, L
    setup_fonts()

    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
    for ax, pv in zip(axes, sorted(df["pv_kwp"].unique())):
        sub = df[df["pv_kwp"] == pv]
        for sf, color, marker in [(1.0, "#2c3e50", "o"), (0.7, "#e67e22", "s"),
                                  (0.5, "#c0392b", "^")]:
            s = sub[sub["storage_cost_factor"] == sf].sort_values("discount_rate")
            ax.plot(s["discount_rate"] * 100, s["saving_wan_year"], marker=marker,
                    color=color, lw=2,
                    label=L(f"储能成本×{sf}", f"BESS cost ×{sf}"))
        ax.axhline(0, color="gray", ls="--", lw=1)
        epen = sub["energy_penetration_pct"].iloc[0]
        ax.set_title(L(f"PV={pv}kWp（电量渗透率{epen:.0f}%）",
                       f"PV={pv}kWp (pen. {epen:.0f}%)"))
        ax.set_xlabel(L("折现率 (%)", "Discount rate (%)"))
        ax.grid(alpha=0.3)
    axes[0].set_ylabel(L("自适应相对刚性2.0节省 (万元/年)", "Saving vs Rigid 2.0 (10k CNY/yr)"))
    axes[0].legend()
    plt.suptitle(L("经济参数敏感性：折现率 × 储能成本下行 对自适应容载比节省的影响",
                   "Sensitivity: discount rate × BESS cost decline on adaptive saving"), fontsize=13)
    plt.tight_layout()
    out = ROOT / "results" / "figures" / "fig7_sensitivity_econ.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


if __name__ == "__main__":
    df = run()
    plot(df)
