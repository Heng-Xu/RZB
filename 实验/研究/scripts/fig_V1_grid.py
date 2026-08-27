#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V1 分区接线示意图(README §9.4):220边界—110站—联络通道;
节点大小∝容量,颜色=分区卡边方向(fwd蓝/rev橙),城乡底色(浅灰/浅绿),
按分区分簇聚合布局。用法:python scripts/fig_V1_grid.py --run synthetic-m1
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from scripts._common import parse_args, load_run, setup_fonts, save_fig, PALETTE

GRID220 = "220kV边界"
ZONE_CENTERS = {"Z1": (0, 6.4), "Z2": (0, 3.2), "Z3": (0, 0), "Z4": (5.2, 4.8), "Z5": (5.2, 1.6)}


def _mother(zone):
    return min(zone.stations, key=lambda s: (-s.cap_mva, s.station_id)).station_id


def main() -> None:
    args = parse_args("V1 分区接线示意图(占位版,合成数据)")
    ctx = load_run(args.run)
    data, clr = ctx["data"], ctx["clr"]
    setup_fonts()

    g = nx.Graph()
    g.add_node(GRID220)
    mothers = {z: _mother(data.zones[z]) for z in data.zones}
    for z, zone in data.zones.items():
        for s in zone.stations:
            g.add_node(s.station_id, zone=z, cap=s.cap_mva, area=zone.area_type)
        g.add_edge(mothers[z], GRID220, kind="boundary")
    for t in data.ties:
        if t.usable:
            g.add_edge(t.station_a, t.station_b, kind="tie", w=t.n_channels * t.ampacity_mw)

    pos: dict[str, tuple[float, float]] = {}
    for z, zone in data.zones.items():
        sub = g.subgraph([s.station_id for s in zone.stations])
        local = nx.spring_layout(sub, seed=20260721, k=0.8)
        cx, cy = ZONE_CENTERS[z]
        for n, (x, y) in local.items():
            pos[n] = (cx + x, cy + y)
    pos[GRID220] = (2.6, 8)

    fig, ax = plt.subplots(figsize=(10, 9))
    for z, zone in data.zones.items():
        cx, cy = ZONE_CENTERS[z]
        color = "#e8e8e8" if zone.area_type == "urban" else "#dff0d8"
        ax.add_patch(mpatches.Circle((cx, cy), 1.3, color=color, zorder=0))
        ax.text(cx, cy + 1.45, f"{z}({'城' if zone.area_type == 'urban' else '乡'})",
                ha="center", fontsize=9, color=PALETTE["gray"])

    tie_edges = [(u, v) for u, v, d in g.edges(data=True) if d.get("kind") == "tie"]
    bnd_edges = [(u, v) for u, v, d in g.edges(data=True) if d.get("kind") == "boundary"]
    widths = [0.5 + g[u][v].get("w", 10) / 10 for u, v in tie_edges]
    nx.draw_networkx_edges(g, pos, edgelist=tie_edges, width=widths, edge_color=PALETTE["gray"], ax=ax)
    nx.draw_networkx_edges(g, pos, edgelist=bnd_edges, style="dashed",
                            edge_color=PALETTE["gray"], ax=ax)

    node_colors, node_sizes, labels = [], [], {}
    for n in g.nodes:
        if n == GRID220:
            node_colors.append("black"); node_sizes.append(400); labels[n] = "220kV"
            continue
        zid = g.nodes[n]["zone"]
        binding = clr.loc[zid, "binding"]
        node_colors.append(PALETTE["orange"] if binding == "reverse" else PALETTE["blue"])
        node_sizes.append(80 + g.nodes[n]["cap"] * 4)
        labels[n] = n
    nx.draw_networkx_nodes(g, pos, node_color=node_colors, node_size=node_sizes, ax=ax)
    nx.draw_networkx_labels(g, pos, labels=labels, font_size=7, ax=ax)

    ax.text(0.02, 0.02, "节点色:蓝=正向卡边 橙=反向卡边(见Z2)  底色:浅灰=城 浅绿=乡",
            transform=ax.transAxes, fontsize=8)
    ax.set_title("V1 分区接线示意图(220kV边界—110kV站—10kV联络,合成网架)")
    ax.axis("off")

    node_df = pd.DataFrame(
        [{"station_id": n, "zone": g.nodes[n].get("zone", "—"), "x": pos[n][0], "y": pos[n][1],
          "cap_mva": g.nodes[n].get("cap", 0)} for n in g.nodes])
    save_fig(fig, "fig_V1_grid", node_df)
    print("V1 写入 figures/fig_V1_grid.png/.data.csv")


if __name__ == "__main__":
    main()
