#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V5 承载力热力图(README §9.4):站×2断面(正/反向峰) loading_pct,
数据来自 verify_flow.csv 的主变(X_*)N-1 元件;末行加"全网N-1最大值"汇总。
M1 声明:verify_flow.csv 只含全年P⁺/P⁻两个断面(非逐月),非"站×月"完整版,
按 README 精神降级为"站×2断面"并如实标注。用法:python scripts/fig_V5_heatmap.py --run synthetic-m1
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts._common import parse_args, load_run, setup_fonts, save_fig, PALETTE


def main() -> None:
    args = parse_args("V5 承载力热力图(占位版,合成数据)")
    ctx = load_run(args.run)
    data, vflow = ctx["data"], ctx["verify_flow"]
    setup_fonts()

    xfmr = vflow[vflow["element_id"].str.startswith("X_")].copy()
    xfmr["station_id"] = xfmr["element_id"].str.split("_").str[1]
    snapshots = sorted(vflow["snapshot"].unique())
    col_labels = [f"断面{i + 1}(t={t})" for i, t in enumerate(snapshots)]
    stations = sorted(data.stations)

    mat = np.full((len(stations) + 1, len(snapshots)), np.nan)
    for si, sid in enumerate(stations):
        for ci, t in enumerate(snapshots):
            sub = xfmr[(xfmr["station_id"] == sid) & (xfmr["snapshot"] == t)]
            if len(sub):
                mat[si, ci] = sub["loading_pct"].max()
    for ci, t in enumerate(snapshots):
        mat[-1, ci] = vflow.loc[vflow["snapshot"] == t, "loading_pct"].max()
    row_labels = stations + ["全网N-1最大值(线路+主变)"]

    fig, ax = plt.subplots(figsize=(6, 8))
    vmax = max(120.0, float(np.nanmax(mat)))
    im = ax.imshow(mat, cmap="RdYlGn_r", vmin=0, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(col_labels))); ax.set_xticklabels(col_labels, rotation=20)
    ax.set_yticks(range(len(row_labels))); ax.set_yticklabels(row_labels)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            if not np.isnan(mat[i, j]):
                ax.text(j, i, f"{mat[i, j]:.0f}", ha="center", va="center", fontsize=8,
                        color="white" if mat[i, j] > vmax * 0.6 else "black")
    ax.axhline(len(stations) - 0.5, color=PALETTE["blue"], linewidth=1.5)
    fig.colorbar(im, ax=ax, label="N-1后主变负载率(%)")
    ax.set_title("V5 承载力热力图(站×2断面,>100%越限)")
    fig.tight_layout()

    df = pd.DataFrame(mat, index=row_labels, columns=col_labels).reset_index(names="row")
    save_fig(fig, "fig_V5_heatmap", df)
    print("V5 写入 figures/fig_V5_heatmap.png/.data.csv")


if __name__ == "__main__":
    main()
