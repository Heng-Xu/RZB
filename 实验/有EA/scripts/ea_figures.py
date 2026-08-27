#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""县级 FG-NSGA-II 实验图（英文标签，IEEE 投稿级）。读 results/*.csv → results/figures/*.{pdf,png}。
用法：python3 ea_figures.py（自动跳过缺失 CSV）。

发表规范（render-only，数据口径不变）：
- Liberation Serif（Times 度量兼容，配 IEEEtran 正文）；stix 数学字体。
- Okabe-Ito 色觉友好配色；单栏 3.5in / 双栏 7.16in。
- 同时输出矢量 PDF（LaTeX 交付）+ 600dpi PNG（预览）；pdf/ps.fonttype=42（IEEE PDF eXpress 拒收 Type-3）。
- 图内标题由 SHOW_TITLE 开关控制：投稿时置 False，说明交由图注（Fig. N.）承担。
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
FIG = RES / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# ---- 发表样式 -------------------------------------------------------------
SHOW_TITLE = True          # 投稿终稿置 False（图注承担说明）
COL = 3.5                  # IEEE 单栏宽 (in)
DCOL = 7.16                # IEEE 双栏（整幅）宽 (in)
mpl.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Liberation Serif", "Nimbus Roman", "Times New Roman", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 6.8,
    "axes.linewidth": 0.7, "grid.alpha": 0.35, "grid.linewidth": 0.5,
    "axes.grid": True, "lines.linewidth": 1.4, "lines.markersize": 4,
    "legend.frameon": True, "legend.framealpha": 0.9, "legend.edgecolor": "0.7",
    "legend.fancybox": False, "legend.borderpad": 0.35, "legend.handlelength": 1.8,
    "figure.dpi": 150, "savefig.dpi": 600, "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02, "pdf.fonttype": 42, "ps.fonttype": 42,
})
# Okabe-Ito 色觉友好调色板
C = dict(black="#000000", orange="#E69F00", sky="#56B4E9", green="#009E73",
         yellow="#F0E442", blue="#0072B2", verm="#D55E00", purple="#CC79A7")


def _save(fig, name):
    for ext in ("pdf", "png"):
        p = FIG / f"{name}.{ext}"
        fig.savefig(p)
    plt.close(fig)
    print(f"[fig] {FIG / name}.{{pdf,png}}")


def _title(ax, t):
    if SHOW_TITLE:
        ax.set_title(t)


def fig_pareto():
    f = RES / "ea_county_pareto.csv"
    if not f.exists():
        return
    df = pd.read_csv(f)
    fig, ax = plt.subplots(figsize=(COL, COL * 0.78))
    ax.plot(df.f1_wan, df.f2_eens_mwh, "-", color=C["verm"], lw=1.3, zorder=2)
    ax.scatter(df.f1_wan, df.f2_eens_mwh, s=11, color=C["verm"], zorder=3,
               label="FG-NSGA-II front")
    knee = df[df.is_knee]
    if len(knee):
        ax.scatter(knee.f1_wan, knee.f2_eens_mwh, s=150, marker="*",
                   color=C["black"], edgecolor="white", lw=0.6, zorder=5,
                   label="Knee (recommended)")
        kx, ky = float(knee.f1_wan.iloc[0]), float(knee.f2_eens_mwh.iloc[0])
        ax.annotate(f"$f_1$={kx:.0f}, $f_2$={ky:.0f}", (kx, ky),
                    xytext=(10, 14), textcoords="offset points", fontsize=6.5,
                    ha="left", arrowprops=dict(arrowstyle="-", lw=0.5, color="0.4"))
    ax.set_xlabel(r"County annualized cost $f_1$ (10$^4$ CNY/yr)")
    ax.set_ylabel(r"County $N\!-\!1$ risk $f_2$ (MWh EENS/yr)")
    ax.margins(x=0.04, y=0.06)
    _title(ax, "County cost–risk Pareto front")
    ax.legend(loc="upper right")
    _save(fig, "fig_county_pareto")


def fig_strategy():
    f = RES / "ea_county_strategy_knee.csv"
    if not f.exists():
        return
    df = pd.read_csv(f)
    fig, ax = plt.subplots(figsize=(COL, COL * 0.74))
    routes = {"配储为主": (C["blue"], "o", "Storage"),
              "低容载比+强联络": (C["green"], "s", "Low-$R$ + interconnection"),
              "升容载比增容": (C["verm"], "^", "Uprate $R$")}
    for zh, (c, mk, en) in routes.items():
        sub = df[df.route == zh]
        if len(sub):
            ax.scatter(sub.slr, sub.cd, c=c, marker=mk, s=42, label=en,
                       edgecolor="white", lw=0.5, zorder=3)
    for _, r in df.iterrows():
        ax.annotate(f"$R${r.R_star:g}", (r.slr, r.cd), fontsize=5.6, color="0.35",
                    xytext=(3.5, 2.5), textcoords="offset points", zorder=2)
    ax.set_xlabel("Generation-to-load ratio (PV / peak load)")
    ax.set_ylabel("Tie-line interconnection level")
    ax.margins(0.10)
    _title(ax, "Per-substation strategy at the knee")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.19), ncol=2, frameon=False)
    _save(fig, "fig_strategy")


def fig_scaling():
    f = RES / "ea_scaling.csv"
    if not f.exists():
        return
    df = pd.read_csv(f).sort_values("K")
    fig, ax1 = plt.subplots(figsize=(COL, COL * 0.74))
    ax2 = ax1.twinx()
    ax2.grid(False)
    combos = df.enum_combos.astype(float).clip(lower=1)
    l1, = ax1.semilogy(df.K, combos, "s--", color=C["verm"], lw=1.6, ms=5,
                       label="Enumeration combinations")
    l2, = ax2.plot(df.K, df.ea_seconds, "o-", color=C["blue"], lw=1.6, ms=5,
                   label="NSGA-II runtime")
    ax1.set_xlabel("Number of substations $K$")
    ax1.set_ylabel("Enumeration combinations (log)", color=C["verm"])
    ax2.set_ylabel("NSGA-II runtime (s)", color=C["blue"])
    ax1.tick_params(axis="y", colors=C["verm"])
    ax2.tick_params(axis="y", colors=C["blue"])
    _title(ax1, "Enumeration explodes; NSGA-II stays tractable")
    ax1.legend([l1, l2], [l1.get_label(), l2.get_label()], loc="center right")
    _save(fig, "fig_scaling")


def fig_band():
    f = RES / "ea_band_effect.csv"
    if not f.exists():
        return
    df = pd.read_csv(f)
    x = np.arange(len(df))
    # 可行解 EENS 全为 0 → 成本下限(线) + 可行前沿点数(线) 双轴。
    fig, ax1 = plt.subplots(figsize=(COL, COL * 0.74))
    ax2 = ax1.twinx()
    ax2.grid(False)
    l1, = ax1.plot(x, df.min_cost_wan, "o-", color=C["blue"], lw=1.8, ms=5,
                   label="Min county cost")
    for xi, v in zip(x, df.min_cost_wan):
        ax1.annotate(f"{v:.0f}", (xi, v), textcoords="offset points",
                     xytext=(0, 8), ha="center", fontsize=6.2, color=C["blue"])
    ax1.set_xticks(x)
    ax1.set_xticklabels(df.band)
    ax1.set_xlabel("County capacity–load-ratio band")
    ax1.set_ylabel(r"Min county cost (10$^4$ CNY/yr)", color=C["blue"])
    ax1.tick_params(axis="y", colors=C["blue"])
    l2, = ax2.plot(x, df.n_front, "s--", color=C["verm"], lw=1.6, ms=5,
                   label="Pareto front size")
    for xi, n in zip(x, df.n_front):
        ax2.annotate(f"{int(n)}", (xi, n), textcoords="offset points",
                     xytext=(0, -12), ha="center", fontsize=6.2, color=C["verm"])
    ax2.set_ylabel("Pareto front size (# points)", color=C["verm"])
    ax2.tick_params(axis="y", colors=C["verm"])
    ax2.set_ylim(0, df.n_front.max() * 1.35)
    ax1.margins(x=0.10)
    _title(ax1, "Effect of the capacity–load-ratio band")
    ax1.legend([l1, l2], [l1.get_label(), l2.get_label()], loc="center left")
    _save(fig, "fig_band_effect")


def fig_system_constraint():
    """E7：加上级系统潮流约束后前沿外移（成本下限升高，本合成县近乎不绑定）。"""
    f = RES / "ea_system_fronts.csv"
    if not f.exists():
        return
    df = pd.read_csv(f)
    # 前沿单调：按 f1 排序后再连线，避免 CSV 原序造成的锯齿。
    unc = df[["f1_unc", "f2_unc"]].dropna().sort_values("f1_unc")
    con = df[["f1_con", "f2_con"]].dropna().sort_values("f1_con")
    fig, ax = plt.subplots(figsize=(COL, COL * 0.78))
    ax.plot(unc.f1_unc, unc.f2_unc, "-", color=C["green"], lw=1.5,
            label="Without system constraint")
    ax.plot(con.f1_con, con.f2_con, "--", color=C["verm"], lw=1.5,
            label="With system power-flow constraint")
    ax.set_xlabel(r"County annualized cost $f_1$ (10$^4$ CNY/yr)")
    ax.set_ylabel(r"County $N\!-\!1$ risk $f_2$ (MWh EENS/yr)")
    ax.margins(x=0.04, y=0.06)
    _title(ax, "Effect of the upstream system constraint")
    ax.legend(loc="upper right")
    _save(fig, "fig_system_constraint")


def fig_scaling_gap():
    """FG-NSGA-II 收敛加速（预算无关效率度量）：iso-quality speedup —— FG 达 baseline
    gen800 收敛质量所需代数 g*，加速比=800/g*（≈5–12×）。避免任意固定预算点口径。"""
    f = RES / "ea_converge.csv"
    if not f.exists():
        return
    df = pd.read_csv(f)
    Ks = sorted(df.K.unique())
    mg = df.groupby("algo").gen.max().to_dict()
    sp = {"classic": [], "nsga3": []}
    for K in Ks:                                    # ---- 计算逻辑冻结 ----
        s = df[df.K == K]
        fgc = s[s.algo == "fg"].groupby("gen").hv.mean()
        for base in ("classic", "nsga3"):
            b = s[(s.algo == base) & (s.gen == mg[base])].hv.mean()
            reached = fgc[fgc >= b]
            g = int(reached.index.min()) if len(reached) else mg["fg"]
            sp[base].append(mg[base] / g)
    fig, ax = plt.subplots(figsize=(COL, COL * 0.78))
    ax.plot(Ks, sp["classic"], "o-", color=C["verm"], lw=1.8, ms=5,
            label="vs. classic NSGA-II")
    ax.plot(Ks, sp["nsga3"], "^-", color=C["orange"], lw=1.8, ms=5,
            label="vs. NSGA-III")
    for K, v in zip(Ks, sp["classic"]):
        ax.annotate(f"{v:.1f}×", (K, v), textcoords="offset points",
                    xytext=(0, 7), ha="center", fontsize=6.8, color=C["verm"])
    for K, v in zip(Ks, sp["nsga3"]):
        ax.annotate(f"{v:.1f}×", (K, v), textcoords="offset points",
                    xytext=(0, -12), ha="center", fontsize=6.8, color=C["orange"])
    ax.axhline(1.0, color="0.5", ls=":", lw=0.9)
    ax.text(Ks[0], 1.0, " parity (1×)", fontsize=6.3, color="0.4",
            va="bottom", ha="left")
    ax.set_xlabel("Number of substations $K$  (decision dim. $=2K$)")
    ax.set_ylabel("Iso-quality speedup\n(baseline gens / FG gens to equal HV)")
    ax.set_xticks(Ks)
    ax.set_ylim(0, max(sp["nsga3"]) * 1.18)
    ax.margins(x=0.06)
    _title(ax, "Convergence speedup vs. scale")
    ax.legend(loc="upper left")
    _save(fig, "fig_scaling_gap")


def fig_enhanced_convergence():
    """各 K 上 5 变体 HV 收敛（mean±std over seeds）：FG-NSGA-II 领先且更稳；
    repair_only 紧贴 FG（修复=主驱动），warmstart_only 早期抬升、收敛贴近 classic（热启动=早期加速）。"""
    f = RES / "ea_converge.csv"
    if not f.exists():
        return
    df = pd.read_csv(f)
    Ks = sorted(df.K.unique())
    style = [("classic", C["blue"], "-", "Classic NSGA-II"),
             ("nsga3", C["green"], "-", "NSGA-III"),
             ("warmstart_only", C["purple"], ":", "Warm-start only"),
             ("repair_only", C["orange"], "--", "Repair only"),
             ("fg", C["verm"], "-", "FG-NSGA-II (ours)")]
    n = len(Ks); ncol = 2; nrow = (n + 1) // 2
    fig, axes = plt.subplots(nrow, ncol, figsize=(DCOL, 2.5 * nrow),
                             squeeze=False, sharex=True)
    axes = axes.reshape(-1)
    tags = "abcdefgh"
    for i, (ax, K) in enumerate(zip(axes, Ks)):
        d = df[df.K == K]
        for algo, c, ls, lab in style:
            s = d[d.algo == algo].groupby("gen").hv.agg(["mean", "std"]).reset_index()
            if not len(s):
                continue
            lw = 1.9 if algo == "fg" else 1.2
            z = 5 if algo == "fg" else 3
            ax.plot(s.gen, s["mean"], ls, color=c, lw=lw, zorder=z, label=lab)
            ax.fill_between(s.gen, s["mean"] - s["std"].fillna(0),
                            s["mean"] + s["std"].fillna(0), color=c, alpha=0.10, lw=0)
        sf = ScalarFormatter(useMathText=True)
        sf.set_powerlimits((0, 0))
        ax.yaxis.set_major_formatter(sf)
        ax.yaxis.get_offset_text().set_fontsize(6.3)
        ax.set_title(f"({tags[i]}) $K$ = {K}", loc="left", fontsize=8)
        if i // ncol == nrow - 1:
            ax.set_xlabel("Generation")
        if i % ncol == 0:
            ax.set_ylabel("Hypervolume")
    for ax in axes[n:]:
        ax.axis("off")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=5,
               bbox_to_anchor=(0.5, -0.02), frameon=False, fontsize=7)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    _save(fig, "fig_enhanced_convergence")


if __name__ == "__main__":
    # fig_convergence（旧 E5 NSGA-II vs MOEAD）与 fig_front_compare（前沿叠加图）已弃：
    # 效率型创新用收敛曲线 + iso-quality 加速比 + 收敛 HV 表刻画。
    fig_pareto(); fig_strategy(); fig_scaling(); fig_band()
    fig_system_constraint(); fig_scaling_gap(); fig_enhanced_convergence()
    print("[figures done]")
