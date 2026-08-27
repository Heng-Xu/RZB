#!/usr/bin/env python3
"""Fig. 1 (breach->pull-back) for the EPG-NSGA-II 2-page short paper.

Shows, per 110-kV substation (sorted by source-load ratio), the capacity-load
ratio R that would be REQUIRED to carry reverse power with NO storage
(= repair-operator formula, ea_county line 135/141 with P=0) versus the
OPTIMIZED R chosen by EPG-NSGA-II (storage does the work). Nine high-PV
stations would need R up to 3.17 (> the rigid 2.0 limit); the recommended
storage power pulls every one back into the <=2.0 planning band.

No fabricated numbers: R_req_noStorage is the exact model formula with P=0;
R_star and the storage power come from results/ea_county_strategy_knee.csv.
Out: results/figures/fig1_over2.{pdf,png,svg}
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import county_model as cm
from ea_county import build_county, REVERSE_TX_LIMIT
PV_PEAK = getattr(cm, "PV_PEAK_FACTOR")
REV_LOAD = getattr(cm, "REVERSE_LOAD_FACTOR")

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

LIMIT = 2.0            # rigid uniform planning limit
BAND = (1.8, 2.2)      # aggregate planning band


def main():
    county = build_county(20, seed=0)
    knee = pd.read_csv(RES / "ea_county_strategy_knee.csv")
    rows = []
    for st in county:
        rev0 = max(0.0, PV_PEAK * st.pv_kwp - REV_LOAD * st.peak_kw)   # reverse flow, P=0
        Rreq = rev0 / (REVERSE_TX_LIMIT * st.peak_kw) if st.peak_kw > 0 else 0.0
        rows.append({"station": st.sid, "slr": st.slr, "R_req": Rreq})
    df = pd.DataFrame(rows).merge(knee[["station", "R_star", "P_BESS_MW"]], on="station")
    df = df.sort_values("slr").reset_index(drop=True)
    x = np.arange(len(df))
    Rreq = df.R_req.to_numpy()
    Rstar = df.R_star.to_numpy()
    P = df.P_BESS_MW.to_numpy()
    breach = Rreq > LIMIT

    fig, ax = plt.subplots(figsize=(COL, COL * 0.86))
    # aggregate planning band shading
    ax.axhspan(BAND[0], BAND[1], color="0.90", zorder=0)
    ax.axhline(LIMIT, ls="--", lw=0.9, color="#b2182b", zorder=1)
    ax.text(0.35, LIMIT + 0.03, "rigid $R=2.0$ limit", ha="left", va="bottom",
            fontsize=7, color="#b2182b")

    # stems: required-R (no storage) down to optimized-R
    for i in range(len(df)):
        c = "#b2182b" if breach[i] else "0.70"
        ax.plot([x[i], x[i]], [Rstar[i], Rreq[i]], color=c,
                lw=1.1 if breach[i] else 0.8, zorder=2)
    ax.scatter(x, Rreq, s=22, marker="o", facecolor="none",
               edgecolor=np.where(breach, "#b2182b", "0.70"), linewidths=1.0,
               zorder=3, label=r"required $R$, no storage")
    ax.scatter(x, Rstar, s=20, marker="s", color="#2166ac", zorder=4,
               label=r"optimized $R$ (with storage)")

    # recommended storage annotation on breaching stations (left of stem, MW)
    for i in np.where(breach)[0]:
        ax.annotate(f"+{P[i]:.1f} MW", (x[i], (Rreq[i] + Rstar[i]) / 2), xytext=(-4, 0),
                    textcoords="offset points", fontsize=5.0, color="#2166ac",
                    ha="right", va="center", rotation=90)

    n_breach = int(breach.sum())
    ax.set_ylim(1.0, 3.35)
    ax.set_xlim(-0.7, len(df) - 0.3)
    ax.set_xticks([])
    ax.set_xlabel(r"110-kV substations, low $\rightarrow$ high source-load ratio", fontsize=8)
    ax.set_ylabel(r"capacity-load ratio $R$", fontsize=8)
    ax.text(0.02, 0.97,
            f"{n_breach}/20 stations would need $R>2.0$ without storage\n"
            r"(+ MW = recommended storage power that restores $R\leq2.0$)",
            transform=ax.transAxes, fontsize=6.6, va="top", ha="left")
    ax.legend(loc="lower right", fontsize=6.6, frameon=False, handletextpad=0.4,
              borderaxespad=0.3)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    for ext in ("pdf", "png", "svg"):
        fig.savefig(FIG / f"fig1_over2.{ext}")
    plt.close(fig)
    print(f"[fig] {FIG/'fig1_over2'}.{{pdf,png,svg}}")
    print(f"  stations={len(df)}  need R>2.0 (no storage)={n_breach}  "
          f"max req R={Rreq.max():.2f}  all pulled to <=2.0: {bool((Rstar[breach]<=2.0).all())}")


if __name__ == "__main__":
    main()
