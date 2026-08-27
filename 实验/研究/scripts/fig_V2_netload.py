#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2 净负荷时序(README §9.4):Z2反向峰日+Z1正向峰日两联,标注P+/P-;
右下小图占位"M2"(5年鸭子曲线演化需多年数据,M1 只有基准年)。
用法:python scripts/fig_V2_netload.py --run synthetic-m1
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.pyplot as plt
import pandas as pd

from scripts._common import parse_args, load_run, setup_fonts, save_fig, PALETTE


def _zone_series(data, zid):
    return data.pnet[[s.station_id for s in data.zones[zid].stations]].sum(axis=1)


def _plot_day(ax, series: pd.Series, day_start, title: str, mark: str, color: str) -> None:
    day = series.loc[day_start:day_start + pd.Timedelta(hours=23)]
    hours = range(len(day))
    ax.plot(hours, day.to_numpy(), color=color, marker="o", markersize=3)
    ax.axhline(0, color=PALETTE["gray"], linewidth=0.8)
    idx = int(day.to_numpy().argmax()) if mark == "P+" else int(day.to_numpy().argmin())
    ax.annotate(f"{mark}={day.iloc[idx]:.1f}MW", xy=(idx, day.iloc[idx]),
                xytext=(idx, day.iloc[idx] + (15 if mark == "P+" else -15)),
                color=PALETTE["red"], fontsize=8,
                arrowprops=dict(arrowstyle="->", color=PALETTE["red"]))
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("小时"); ax.set_ylabel("净负荷(MW)")


def main() -> None:
    args = parse_args("V2 净负荷时序(占位版,合成数据)")
    ctx = load_run(args.run)
    data = ctx["data"]
    setup_fonts()

    z1 = _zone_series(data, "Z1")
    z2 = _zone_series(data, "Z2")
    z1_fwd_day = z1.idxmax().normalize()
    z2_rev_day = z2.idxmin().normalize()

    fig = plt.figure(figsize=(11, 6))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 1], height_ratios=[3, 1.3])
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax_note = fig.add_subplot(gs[1, 0])
    ax_small = fig.add_subplot(gs[1, 1])

    _plot_day(ax1, z1, z1_fwd_day, f"Z1 正向峰日({z1_fwd_day.date()})", "P+", PALETTE["blue"])
    _plot_day(ax2, z2, z2_rev_day, f"Z2 反向峰日({z2_rev_day.date()})", "P-", PALETTE["orange"])

    ax_note.axis("off")
    ax_note.text(0.02, 0.5, "P+=正向(受电)峰,P-=反向(送出)峰;\n两分区取各自全年最不利日,非同一天。",
                 fontsize=9, va="center")

    ax_small.set_facecolor("#f5f5f5")
    ax_small.text(0.5, 0.5, "M2\n(5年鸭子曲线演化,\n需多年逐时数据)",
                  ha="center", va="center", fontsize=10, color=PALETTE["gray"])
    ax_small.set_xticks([]); ax_small.set_yticks([])
    for spine in ax_small.spines.values():
        spine.set_edgecolor(PALETTE["gray"])

    fig.suptitle("V2 净负荷时序:正/反向峰日对照", fontsize=13)
    fig.tight_layout()

    data_df = pd.concat([
        z1.loc[z1_fwd_day:z1_fwd_day + pd.Timedelta(hours=23)].rename("Z1_fwd_day").reset_index(),
        z2.loc[z2_rev_day:z2_rev_day + pd.Timedelta(hours=23)].rename("Z2_rev_day").reset_index(),
    ], axis=1)
    save_fig(fig, "fig_V2_netload", data_df)
    print("V2 写入 figures/fig_V2_netload.png/.data.csv")


if __name__ == "__main__":
    main()
