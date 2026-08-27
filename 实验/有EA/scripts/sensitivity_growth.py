#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
负荷增长敏感性分析（论文§4.4，最关键的稳健性检验）：
  容载比"下探空间"（降容载比方向）与联络度梯度（X3）经 N-1 充裕度对**未来峰荷**
  peak×(1+g)^n 校核，故对负荷增长率 g 与校核年限 n 敏感。本脚本扫描 (g,n) 网格，
  考察三条结论各自的稳健性：
    - 升容载比（高渗透→R≥2.3）：由反送/弃光驱动，**预期对 g 稳健**；
    - 降容载比（低渗透 floor<2.0）：由 N-1 驱动，**预期随 g 漂移**（条件性结论）；
    - 联络度梯度（弱/中/强）：同上，仅在中等 g 带呈清晰单调。

判R依据：在候选 R∈{1.5..2.6} 中取年化成本最小者（=决策矩阵的选择）。
解析判据（cd=0.45, 2台主变, n1_overload=1.0）：R 付可靠性代价 ⟺ R < 2·((1+g)^n − cd)。

输出：
- results/sensitivity_growth.csv
- results/figures/fig9_growth_sensitivity.png
"""

from __future__ import annotations

import math
import sys
from itertools import product
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lcc_simulator import LCCSimulator, load_cost_params, load_ieee33
from sweep_experiments import build_candidate, CANDIDATE_R, select_by_gate

G_LIST = [0.02, 0.03, 0.05, 0.07, 0.08]
N_LIST = [3, 5, 10]
# 高渗透点取源荷比≈2.69(PV=10000)：校核下 R_min=2.6 仍可行（纯主变升容载比），
# 便于检验"升方向高R对负荷增长是否稳健"；PV=12000(源荷比3.2)会被承载力一刀切为配储而失去该检验意义
PV_LOW, PV_MID, PV_HIGH = 2000, 6000, 10000   # 低/中/高渗透代表点
CD_MED = 0.45


def _floor(sim, bus, branch, pv, pm, pk, cd):
    """经反向承载力校核两阶段选优后的推荐容载比（与主结果一致）。"""
    return select_by_gate(sim, bus, branch, pv, pm, pk, cd)["best"].capacity_load_ratio


def run() -> pd.DataFrame:
    bus, branch = load_ieee33()
    pk = float(bus["p_load_kw"].sum())
    pm = math.hypot(pk, bus["q_load_kvar"].sum()) / 1000
    pf = pk / (pm * 1000)                       # 有功口径定容下，判据含 1/(overload·pf)
    overload = load_cost_params()["reliability"]["n1_overload_factor"]
    rows = []
    for g, n in product(G_LIST, N_LIST):
        cost = load_cost_params()
        cost["reliability"]["load_growth_rate"] = g
        cost["reliability"]["growth_horizon_years"] = n
        sim = LCCSimulator(cost)
        # 有功口径(tx=R·P_MW)+短时过载：R 付可靠性代价 ⟺ R < 2·((1+g)^n − cd)/(overload·pf)
        cutoff = 2 * ((1 + g) ** n - CD_MED) / (overload * pf)
        rows.append({
            "load_growth_pct": int(g * 100),
            "horizon_years": n,
            "reliab_cutoff_R": round(cutoff, 3),
            "low_pen_floor": _floor(sim, bus, branch, PV_LOW, pm, pk, CD_MED),
            "mid_pen_floor": _floor(sim, bus, branch, PV_MID, pm, pk, CD_MED),
            "x3_weak_cd15": _floor(sim, bus, branch, PV_LOW, pm, pk, 0.15),
            "x3_med_cd45": _floor(sim, bus, branch, PV_LOW, pm, pk, 0.45),
            "x3_strong_cd80": _floor(sim, bus, branch, PV_LOW, pm, pk, 0.80),
            "high_pen_R": _floor(sim, bus, branch, PV_HIGH, pm, pk, CD_MED),
        })
    df = pd.DataFrame(rows)
    out = ROOT / "results" / "sensitivity_growth.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"[OK] {out}: {len(df)} rows")

    # 稳健性判定
    up_robust = (df["high_pen_R"] >= 2.3).all()
    down_set = sorted(df["low_pen_floor"].unique())
    print(f"升容载比(高渗透≥2.3)稳健: {up_robust}")
    print(f"降容载比(低渗透floor)随(g,n)取值集合: {down_set}  → {'条件性' if len(down_set)>1 else '稳健'}")
    return df


def plot(df: pd.DataFrame):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from generate_figures import setup_fonts, L
    setup_fonts()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    for n, marker in zip(N_LIST, ["o", "s", "^"]):
        s = df[df["horizon_years"] == n].sort_values("load_growth_pct")
        ax1.plot(s["load_growth_pct"], s["low_pen_floor"], marker=marker, lw=2,
                 label=L(f"校核年限 n={n}", f"horizon n={n}"))
        ax2.plot(s["load_growth_pct"], s["high_pen_R"], marker=marker, lw=2,
                 label=L(f"校核年限 n={n}", f"horizon n={n}"))
    ax1.axhline(2.0, color="gray", ls="--", lw=1)
    ax1.set_title(L("降容载比floor随负荷增长漂移（条件性）",
                    "Down-floor drifts with load growth (conditional)"))
    ax2.set_title(L("升容载比对负荷增长稳健", "Up-elasticity robust to load growth"))
    for ax in (ax1, ax2):
        ax.set_xlabel(L("年负荷增长率 (%)", "Annual load growth (%)"))
        ax.set_ylabel(L("推荐容载比 R", "Recommended R"))
        ax.set_ylim(1.3, 2.8); ax.grid(alpha=0.3); ax.legend()
    plt.tight_layout()
    out = ROOT / "results" / "figures" / "fig9_growth_sensitivity.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


if __name__ == "__main__":
    df = run()
    plot(df)
