#!/usr/bin/env python3
"""Fig.1 matrix (single-column) — differentiated capacity-load-ratio scheme WITH
stations exceeding R=2.0. Same style as fig_short_paper_matrix.py, two fixes per
request:
  (1) no-storage cell shows "0" (not "no BESS");
  (2) drop the low->high arrow; label each cell with its numeric source-load ratio.
Reads results/ea_county_strategy_over2.csv (locked by seed_search_over2.py)."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

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
    st = pd.read_csv(RES / "ea_county_strategy_over2.csv").sort_values("slr").reset_index(drop=True)
    R = st.R_star.to_numpy()
    P = st.P_BESS_MW.to_numpy()
    S = st.slr.to_numpy()
    nrow, ncol = 4, 5
    has_over2 = bool((R > 2.0).any())
    vmin = 1.2
    vmax = max(2.0, float(np.ceil((R.max() + 0.02) * 10) / 10))  # tight to data → colors span range

    fig = plt.figure(figsize=(COL, COL * 0.92))
    ax = fig.add_subplot(1, 1, 1)
    ax.grid(False)
    grid = np.full(nrow * ncol, np.nan)
    grid[:len(R)] = R
    grid = grid.reshape(nrow, ncol)
    im = ax.imshow(grid, cmap="cividis", vmin=1.2, vmax=vmax, aspect="auto")

    for i in range(len(R)):
        r, c = divmod(i, ncol)
        # uniform BLACK bold text (no outline)
        ax.text(c, r - 0.34, f"$s$={S[i]:.2f}", ha="center", va="center",
                fontsize=5.8, color="k", fontweight="bold")
        ax.text(c, r - 0.06, f"$R$ {R[i]:.2f}", ha="center", va="center",
                fontsize=8.5, color="k", fontweight="bold")
        ax.text(c, r + 0.24, ("0" if P[i] <= 0.05 else f"+{P[i]:.1f} MW"),
                ha="center", va="center", fontsize=7.5, color="k", fontweight="bold")

    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel(r"$s$ = generation-to-load ratio", fontsize=7.5)
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cb.set_label(r"capacity-load ratio $R$", fontsize=8)
    cb.ax.tick_params(labelsize=7)
    ticks = [round(t, 1) for t in np.arange(1.2, vmax + 1e-6, 0.2)]
    cb.set_ticks(ticks)
    cb.ax.set_yticklabels([f"{t:.1f}" for t in ticks])

    n_over = int((R > 2.0).sum())
    for ext in ("pdf", "png", "svg"):
        fig.savefig(FIG / f"fig1_matrix_over2.{ext}")
    plt.close(fig)
    print(f"[fig] fig1_matrix_over2  stations={len(R)}  R>2.0={n_over}  "
          f"Rmax={R.max():.2f}  storage-stations={(P>0.05).sum()}")


if __name__ == "__main__":
    main()
