#!/usr/bin/env python3
"""Fig. 1 for the EPG-NSGA-II 2-page short paper.

Single double-column figure, two panels (K=20 main case):
  (a) cost-risk Pareto front + knee            <- results/ea_county_pareto.csv
  (b) elastic capacity-load-ratio matrix       <- results/ea_county_strategy_knee.csv
      20 stations sorted by generation-to-load ratio (slr), reshaped 4x5,
      cell color = per-station ratio R*, cell annotated with R* and storage P.
Style matches ea_figures.py (Liberation Serif / fonttype 42 / IEEE widths).
Out: results/figures/fig1_application.{pdf,png}
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "results"
FIG = RES / "figures"
FIG.mkdir(parents=True, exist_ok=True)

COL, DCOL = 3.5, 7.16
mpl.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Liberation Serif", "Nimbus Roman", "Times New Roman", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 6.8,
    "axes.linewidth": 0.7, "grid.alpha": 0.35, "grid.linewidth": 0.5,
    "lines.linewidth": 1.4, "lines.markersize": 4,
    "legend.frameon": True, "legend.framealpha": 0.9, "legend.edgecolor": "0.7",
    "figure.dpi": 150, "savefig.dpi": 600, "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02, "pdf.fonttype": 42, "ps.fonttype": 42,
})
C = dict(black="#000000", verm="#D55E00", blue="#0072B2", green="#009E73")
SHOW_TITLE = True


def main():
    par = pd.read_csv(RES / "ea_county_pareto.csv")
    st = pd.read_csv(RES / "ea_county_strategy_knee.csv").sort_values("slr").reset_index(drop=True)

    fig = plt.figure(figsize=(DCOL, DCOL * 0.36))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.28], wspace=0.28)

    # ---- (a) Pareto front + knee ----
    axa = fig.add_subplot(gs[0, 0])
    axa.grid(True)
    axa.plot(par.f1_wan, par.f2_eens_mwh, "-", color=C["verm"], lw=1.3, zorder=2)
    axa.scatter(par.f1_wan, par.f2_eens_mwh, s=10, color=C["verm"], zorder=3,
                label="EPG-NSGA-II front")
    knee = par[par.is_knee]
    if len(knee):
        kx, ky = float(knee.f1_wan.iloc[0]), float(knee.f2_eens_mwh.iloc[0])
        axa.scatter([kx], [ky], s=150, marker="*", color=C["black"],
                    edgecolor="white", lw=0.6, zorder=5, label="Knee (recommended)")
        axa.annotate(f"$f_1$={kx:.0f}, $f_2$={ky:.0f}\nagg. $R$=1.80", (kx, ky),
                     xytext=(12, 12), textcoords="offset points", fontsize=6.5,
                     ha="left", arrowprops=dict(arrowstyle="-", lw=0.5, color="0.4"))
    axa.set_xlabel(r"County annualized cost $f_1$ (10$^4$ CNY/yr)")
    axa.set_ylabel(r"County $N\!-\!1$ risk $f_2$ (MWh EENS/yr)")
    axa.margins(x=0.05, y=0.07)
    axa.legend(loc="upper right")
    if SHOW_TITLE:
        axa.set_title("(a) Cost-risk Pareto front (K=20)")

    # ---- (b) elastic capacity-load-ratio matrix (4x5, ordered by slr) ----
    axb = fig.add_subplot(gs[0, 1])
    axb.grid(False)
    nrow, ncol = 4, 5
    R = st.R_star.to_numpy()
    P = st.P_BESS_MW.to_numpy()
    slr = st.slr.to_numpy()
    grid = np.full(nrow * ncol, np.nan)
    grid[:len(R)] = R
    grid = grid.reshape(nrow, ncol)
    im = axb.imshow(grid, cmap="cividis", vmin=1.2, vmax=2.0, aspect="auto")
    for i in range(len(R)):
        r, c = divmod(i, ncol)
        # white text on dark (low R) cells, black on bright (high R) cells
        txt = "w" if R[i] < 1.65 else "k"
        axb.text(c, r - 0.16, f"$R$ {R[i]:.2f}", ha="center", va="center",
                 fontsize=6.3, color=txt)
        axb.text(c, r + 0.20, (f"+{P[i]:.1f} MW" if P[i] > 0.05 else "no BESS"),
                 ha="center", va="center", fontsize=5.4, color=txt)
    axb.set_xticks([]); axb.set_yticks([])
    axb.set_xlabel("20 substations ordered by generation-to-load ratio "
                   r"(low $\rightarrow$ high) $\Rightarrow$", fontsize=6.8)
    cb = fig.colorbar(im, ax=axb, fraction=0.046, pad=0.03)
    cb.set_label(r"Capacity-load ratio $R$  (uniform baseline = 2.0)", fontsize=6.8)
    cb.ax.tick_params(labelsize=6)
    if SHOW_TITLE:
        axb.set_title("(b) Elastic capacity-load-ratio matrix at the knee")

    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig1_application.{ext}")
    plt.close(fig)
    print(f"[fig] {FIG/'fig1_application'}.{{pdf,png}}")
    print(f"  stations={len(R)}  R range=[{R.min():.2f},{R.max():.2f}]  "
          f"storage-first={(P>0.05).sum()}  need R>2.0={(R>2.0).sum()}")


if __name__ == "__main__":
    main()
