#!/usr/bin/env python3
"""Fig. 1 (single-panel, single-column) for the EPG-NSGA-II 2-page short paper.

Only the elastic capacity-load-ratio matrix (former panel (b)); the cost-risk
Pareto front (former panel (a)) is dropped to fit the 2-page short-paper limit
(its knee numbers are given in the text). Two-panel version stays in
fig_short_paper.py for the long / slide versions.

  matrix  <- results/ea_county_strategy_knee.csv
      20 stations sorted by generation-to-load ratio (slr), reshaped 4x5,
      cell color = station capacity-load ratio R*, cell annotated with R* and storage P.
Out: results/figures/fig1_matrix.{pdf,png}
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

COL = 3.9
mpl.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Liberation Serif", "Nimbus Roman", "Times New Roman", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size": 9, "axes.titlesize": 9, "axes.labelsize": 9,
    "xtick.labelsize": 8, "ytick.labelsize": 8,
    "axes.linewidth": 0.7,
    "figure.dpi": 150, "savefig.dpi": 600, "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02, "pdf.fonttype": 42, "ps.fonttype": 42,
})


def main():
    st = pd.read_csv(RES / "ea_county_strategy_knee.csv").sort_values("slr").reset_index(drop=True)

    fig = plt.figure(figsize=(COL, COL * 0.88))
    ax = fig.add_subplot(1, 1, 1)
    ax.grid(False)
    nrow, ncol = 4, 5
    R = st.R_star.to_numpy()
    P = st.P_BESS_MW.to_numpy()
    grid = np.full(nrow * ncol, np.nan)
    grid[:len(R)] = R
    grid = grid.reshape(nrow, ncol)
    im = ax.imshow(grid, cmap="cividis", vmin=1.2, vmax=2.0, aspect="auto")
    for i in range(len(R)):
        r, c = divmod(i, ncol)
        txt = "w" if R[i] < 1.65 else "k"
        ax.text(c, r - 0.19, f"$R$ {R[i]:.2f}", ha="center", va="center",
                fontsize=8, color=txt)
        ax.text(c, r + 0.22, (f"+{P[i]:.1f} MW" if P[i] > 0.05 else "no BESS"),
                ha="center", va="center", fontsize=7, color=txt)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel(r"low $\rightarrow$ high generation-to-load ratio", fontsize=8)
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cb.set_label(r"capacity-load ratio $R$", fontsize=8)
    cb.ax.tick_params(labelsize=7)

    for ext in ("pdf", "png", "svg"):
        fig.savefig(FIG / f"fig1_matrix.{ext}")
    plt.close(fig)
    print(f"[fig] {FIG/'fig1_matrix'}.{{pdf,png}}")
    print(f"  stations={len(R)}  R range=[{R.min():.2f},{R.max():.2f}]  "
          f"storage-first={(P>0.05).sum()}  need R>2.0={(R>2.0).sum()}")


if __name__ == "__main__":
    main()
