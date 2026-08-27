#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V4 R-成本曲线(README §9.4):方案A 红线上限 r_cap∈[1.6,1.8,2.0,2.2,2.4] 逐点重解,
标注拐点。依赖 src.milp_planner.solve_scheme 的 r_cap/write 参数(Task 8 新增,
默认值不变、不影响既有 58 项基线测试)。用法:python scripts/fig_V4_rcost.py --run synthetic-m1
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.pyplot as plt
import pandas as pd

from scripts._common import parse_args, load_run, setup_fonts, save_fig, PALETTE
from src.milp_planner import solve_scheme
from src.typical_days import reduce_days

R_CAPS = [1.6, 1.8, 2.0, 2.2, 2.4]


def main() -> None:
    args = parse_args("V4 R-成本曲线(占位版,合成数据)")
    ctx = load_run(args.run)
    data, links, sol_b = ctx["data"], ctx["links"], ctx["sol_b"]
    setup_fonts()

    k = int(data.params["milp"]["typical_days"])
    tdays = reduce_days(data.pnet.sum(axis=1), k)

    rows = []
    for rc in R_CAPS:
        bundle = solve_scheme(data, links, tdays, "A", r_cap=rc, write=False)
        rows.append({"r_cap": rc, "total_cost": bundle.total_cost, "status": bundle.status})
        print(f"  r_cap={rc}: status={bundle.status} cost={bundle.total_cost:.2f}万元/年")

    df = pd.DataFrame(rows)
    ok = df[df["status"] == "ok"]  # 只画可行点(低 r_cap 可能因红线过紧不可行)
    b_cost = sol_b["total_cost_wanyuan_per_year"]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(ok["r_cap"], ok["total_cost"], marker="o", color=PALETTE["blue"],
            label="方案A(红线可调)")
    ax.axhline(b_cost, color=PALETTE["orange"], linestyle="--", label=f"方案B(无上限,{b_cost:.1f}万元)")

    if len(ok) >= 3:
        # 拐点=下降速率突变最剧烈处(二阶差分绝对值最大),而非单步最大跌幅
        # (后者在本曲线上恒落在最陡的第一段,掩盖了真正"由陡转平"的膝点)。
        curvature = ok["total_cost"].diff().diff().abs()
        knee = ok.loc[curvature.idxmax()]
        ax.annotate(f"拐点≈{knee['r_cap']:.1f}(红线在此附近失去约束力)",
                    xy=(knee["r_cap"], knee["total_cost"]),
                    xytext=(knee["r_cap"] - 0.35, knee["total_cost"] + 200),
                    arrowprops=dict(arrowstyle="->", color=PALETTE["red"]), color=PALETTE["red"])

    ax.set_xlabel("方案A红线上限 r_cap"); ax.set_ylabel("年化总成本(万元/年)")
    ax.set_title("V4 R-成本曲线(红线放松→成本下降,拐点=Z2实际绑定点附近)")
    ax.legend(); ax.grid(alpha=0.3)

    save_fig(fig, "fig_V4_rcost", df)
    print("V4 写入 figures/fig_V4_rcost.png/.data.csv")


if __name__ == "__main__":
    main()
