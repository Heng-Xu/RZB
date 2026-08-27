#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fig.1 —— FG-NSGA-II 融合框架 / 可行性修复流程示意（IEEE 投稿级，英文标签）。
纯示意图（无数据），样式对齐 ea_figures.py：Liberation Serif + Okabe-Ito + Type-42。
输出：results/figures/fig_framework.{pdf,png}。用法：python3 draw_framework.py
"""
from __future__ import annotations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

SHOW_TITLE = True
DCOL = 7.16
mpl.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Liberation Serif", "Nimbus Roman", "Times New Roman", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "savefig.dpi": 600, "savefig.bbox": "tight", "savefig.pad_inches": 0.03,
    "figure.dpi": 150,
})
C = dict(black="#000000", orange="#E69F00", sky="#56B4E9", green="#009E73",
         yellow="#F0E442", blue="#0072B2", verm="#D55E00", purple="#CC79A7")


def box(ax, cx, cy, w, h, text, fc="white", ec=C["blue"], fs=7.0, bold=False,
        rounding=0.12, lw=1.0, tc="black"):
    x, y = cx - w / 2, cy - h / 2
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={rounding*h}",
                       linewidth=lw, edgecolor=ec, facecolor=fc, zorder=3)
    ax.add_patch(p)
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, zorder=4,
            color=tc, fontweight="bold" if bold else "normal", linespacing=1.15)


def arrow(ax, p1, p2, color="0.25", lw=1.2, style="-|>", ls="-", rad=0.0, mut=9):
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=mut, lw=lw,
                        color=color, linestyle=ls,
                        connectionstyle=f"arc3,rad={rad}", zorder=2,
                        shrinkA=1.5, shrinkB=1.5)
    ax.add_patch(a)


def main():
    fig = plt.figure(figsize=(DCOL, 4.35))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

    # ---- 外围：输入 / 物理评价器 / 输出 ----
    box(ax, 13, 88, 24, 15,
        "Input: county of $K$ stations\n(generation-to-load ratio,\ntie-line interconnection level,\npeak load, reverse-feed hours)",
        fc="#EAF7F0", ec=C["green"], fs=6.6)
    box(ax, 47, 90, 32, 11,
        "Physical evaluator — Z4-LCC compute\n(3.8 ms/eval, deterministic; no surrogate)",
        fc="#EAF4FB", ec=C["blue"], fs=6.8)

    # ---- 优化器容器 ----
    cont = FancyBboxPatch((5, 27), 76, 46, boxstyle="round,pad=0,rounding_size=2.2",
                          linewidth=1.1, edgecolor="0.55", facecolor="#F7F7F7", zorder=1)
    ax.add_patch(cont)
    ax.text(43, 69.5, "FG-NSGA-II optimizer", ha="center", va="center",
            fontsize=8.5, fontweight="bold", color=C["black"], zorder=4)

    # 上排 A1→A2→A3
    box(ax, 18, 57, 21, 12, "Feasible\nwarm-start\ninitialization", fc="#FFF9EC", ec=C["orange"], fs=6.8)
    box(ax, 43, 57, 18, 12, "Evaluate\n$f_1$ cost, $f_2$ EENS", fc="white", ec=C["blue"], fs=6.8)
    box(ax, 68, 57, 22, 12, "Non-dominated sort\n+ crowding\n+ feasibility-first", fc="white", ec=C["blue"], fs=6.6)
    # 下排 B3←B2←B1
    box(ax, 68, 38, 22, 11, "Crossover &\nmutation", fc="white", ec=C["blue"], fs=6.8)
    box(ax, 43, 38, 18, 11, "Feasibility\nrepair", fc=C["orange"], ec=C["verm"], fs=7.2, bold=True)
    box(ax, 18, 38, 21, 11, "Environmental\nselection", fc="white", ec=C["blue"], fs=6.8)

    # 循环箭头
    arrow(ax, (28.5, 57), (34, 57))          # A1->A2
    arrow(ax, (52, 57), (57, 57))            # A2->A3
    arrow(ax, (68, 51), (68, 43.5))          # A3->B3 (down)
    arrow(ax, (57, 38), (52, 38))            # B3->B2
    arrow(ax, (34, 38), (28.5, 38))          # B2->B1
    arrow(ax, (18, 43.5), (39.5, 51.5), color=C["blue"], ls=(0, (4, 2)), rad=-0.25)  # B1->A2 loop
    ax.text(24.5, 49.2, "next\ngeneration", ha="center", va="center",
            fontsize=6.0, style="italic", color=C["blue"], zorder=4)

    # 评价器 <-> Evaluate 双向
    arrow(ax, (47, 84.5), (44, 63.2), color=C["blue"], style="<|-|>", mut=8)
    arrow(ax, (13, 80.5), (16.5, 63.2))      # Input->A1

    # ---- 输出 ----
    box(ax, 18, 12, 26, 12,
        "Output: Pareto front\n+ per-station policy\n(one-station-one-strategy)",
        fc="#EAF7F0", ec=C["green"], fs=6.8)
    arrow(ax, (18, 32.5), (18, 18.2))        # selection -> output

    # ---- 修复子流程（callout）----
    arrow(ax, (48.5, 34), (57, 22.3), color=C["verm"], ls=(0, (3, 2)), rad=0.15)
    ax.text(50.5, 30.0, "repair detail\n(one forward pass)", ha="left", va="center",
            fontsize=6.0, style="italic", color=C["verm"], zorder=4)
    sub = [("(1) scale $R$ into\ncapacity-load band", 57),
           ("(2) add BESS / raise $R$\npast reverse-feed limit", 75),
           ("(3) add BESS to meet\nsystem constraint", 93)]
    for txt, cx in sub:
        box(ax, cx, 16, 14, 12, txt, fc="#FDF6E3", ec=C["orange"], fs=6.0)
    arrow(ax, (64, 16), (68, 16), color="0.3", mut=8)
    arrow(ax, (82, 16), (86, 16), color="0.3", mut=8)
    ax.text(76.5, 6.5, "Repair calls no objective  →  no evaluation budget spent",
            ha="center", va="center", fontsize=6.4, style="italic", color=C["verm"], zorder=4)

    if SHOW_TITLE:
        ax.text(43, 98.5, "FG-NSGA-II: feasibility-guided search framework",
                ha="center", va="center", fontsize=8.5, fontweight="bold")

    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_framework.{ext}")
    plt.close(fig)
    print("wrote", FIG / "fig_framework.pdf", "and .png")


if __name__ == "__main__":
    main()
