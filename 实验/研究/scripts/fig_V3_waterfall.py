#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V3 成本瀑布图(README §9.4):方案A/B 分项成本对比条形 + 红线代价ΔC 标注。
用法:python scripts/fig_V3_waterfall.py --run synthetic-m1
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts._common import parse_args, load_run, setup_fonts, save_fig, PALETTE

CATS = ["储能", "开关+切分操作", "扩容", "弃光"]


def _bars(cb: dict) -> list[float]:
    return [cb["ess"], cb["switch"] + cb["eps_switch"], cb["expand"], cb["curtail"]]


def main() -> None:
    args = parse_args("V3 成本瀑布图(占位版,合成数据)")
    ctx = load_run(args.run)
    sol_a, sol_b = ctx["sol_a"], ctx["sol_b"]
    setup_fonts()

    a_vals = _bars(sol_a["cost_breakdown"])
    b_vals = _bars(sol_b["cost_breakdown"])
    a_total = sol_a["total_cost_wanyuan_per_year"]
    b_total = sol_b["total_cost_wanyuan_per_year"]
    delta_c = a_total - b_total

    x = np.arange(len(CATS) + 1)
    width = 0.35
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.bar(x - width / 2, a_vals + [a_total], width, label="方案A(红线R≤2.0)", color=PALETTE["blue"])
    ax.bar(x + width / 2, b_vals + [b_total], width, label="方案B(无上限)", color=PALETTE["orange"])
    ax.set_xticks(x)
    ax.set_xticklabels(CATS + ["合计"])
    ax.set_ylabel("年化成本(万元/年)")
    ax.set_title(f"V3 成本瀑布:方案A/B 分项对比(ΔC={delta_c:.2f}万元/年)")

    y_top = max(a_total, b_total) * 1.08
    ax.annotate("", xy=(x[-1] + width / 2, b_total), xytext=(x[-1] - width / 2, a_total),
                arrowprops=dict(arrowstyle="<->", color=PALETTE["red"]))
    ax.text(x[-1], y_top, f"红线代价 ΔC={delta_c:.2f}万元/年", ha="center",
            color=PALETTE["red"], fontsize=10)
    ax.set_ylim(0, y_top * 1.15)
    ax.legend()

    df = pd.DataFrame({"分项": CATS + ["合计"], "方案A": a_vals + [a_total],
                        "方案B": b_vals + [b_total]})
    save_fig(fig, "fig_V3_waterfall", df)
    print("V3 写入 figures/fig_V3_waterfall.png/.data.csv")


if __name__ == "__main__":
    main()
