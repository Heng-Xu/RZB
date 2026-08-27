#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V6 切分方案图(README §9.4):方案B(推荐)中 α≠0 的联络画箭头,
粗细∝|α|,文本框标季节+触发理由。方向裁决(M1 近似,solution 只落盘|α|未存
方向分量ap/an):取该联络所在分区的反向峰时刻两站净负荷,方向=更负(PV盈余
更大,越限更重)→较不紧张站,与milp_planner切分"缓解卡死约束"的建模意图一致。
用法:python scripts/fig_V6_split.py --run synthetic-m1
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.pyplot as plt
import pandas as pd

from scripts._common import parse_args, load_run, setup_fonts, save_fig, PALETTE

SEASON_CN = {"spring": "春秋方式", "winter": "冬夏方式"}


def main() -> None:
    args = parse_args("V6 切分方案图(占位版,合成数据)")
    ctx = load_run(args.run)
    data, clr, sol_b = ctx["data"], ctx["clr"], ctx["sol_b"]
    setup_fonts()

    active = [(tid, season, val) for season, m in sol_b["alpha"].items()
              for tid, val in m.items() if val > 1e-6]
    ties_by_id = {t.tie_id: t for t in data.ties}

    stations = sorted(data.stations)
    fig, ax = plt.subplots(figsize=(8, 6))
    xs = {sid: i for i, sid in enumerate(stations)}
    for sid in stations:
        zid = data.stations[sid].zone_id
        color = PALETTE["orange"] if clr.loc[zid, "binding"] == "reverse" else PALETTE["blue"]
        ax.scatter(xs[sid], 0, s=300, color=color, zorder=3)
        ax.text(xs[sid], 0.12, sid, ha="center", fontsize=9)

    if not active:
        ax.text(0.5, 0.5, "方案B 全年无净α≠0 的切分动作", ha="center", transform=ax.transAxes)
    for row_i, (tid, season, val) in enumerate(active):
        t = ties_by_id[tid]
        a, b = t.station_a, t.station_b
        zid = data.stations[a].zone_id
        pnet_zone = data.pnet[[s.station_id for s in data.zones[zid].stations]].sum(axis=1)
        t_ref = pnet_zone.idxmin() if clr.loc[zid, "binding"] == "reverse" else pnet_zone.idxmax()
        src, dst = (a, b) if data.pnet.loc[t_ref, a] <= data.pnet.loc[t_ref, b] else (b, a)
        ax.annotate("", xy=(xs[dst], 0), xytext=(xs[src], 0),
                     arrowprops=dict(arrowstyle="-|>", color=PALETTE["red"],
                                      lw=1 + val * 6, shrinkA=15, shrinkB=15,
                                      connectionstyle="arc3,rad=0.3"))
        reason = "O2反向过载(β·ΣS≥P-)" if clr.loc[zid, "binding"] == "reverse" else "O1正向N-1裕度"
        ax.text((xs[src] + xs[dst]) / 2, 0.4 + 0.15 * row_i,
                f"{tid}:{src}→{dst}  |α|={val:.2f}  {SEASON_CN[season]}\n触发:{reason},替代扩容",
                ha="center", fontsize=8,
                bbox=dict(boxstyle="round", fc="#fff7e6", ec=PALETTE["gray"]))

    y_top = 0.4 + 0.15 * max(len(active) - 1, 0) + 0.3
    ax.set_xlim(-1, len(stations)); ax.set_ylim(-0.3, max(y_top, 0.6))
    ax.axis("off")
    ax.set_title("V6 切分方案图(方案B,箭头=负荷转移方向,粗细∝|α|)")

    # 节点颜色图例(放在图的左下角,不遮挡数据)
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=PALETTE["orange"], edgecolor="black", label="反向卡边(PV盈余)"),
        Patch(facecolor=PALETTE["blue"], edgecolor="black", label="正向卡边(受电)")
    ]
    ax.legend(handles=legend_elements, loc="lower left", fontsize=8,
              framealpha=0.95, edgecolor="gray", title="节点卡边方向")

    df = pd.DataFrame(active, columns=["tie_id", "season", "alpha"])
    save_fig(fig, "fig_V6_split", df)
    print(f"V6 写入 figures/fig_V6_split.png/.data.csv(活跃切分 {len(active)} 项)")


if __name__ == "__main__":
    main()
