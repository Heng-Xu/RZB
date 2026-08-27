# Engineering-Prior-Guided Multi-Objective Optimization of Capacity-Load-Ratio Elasticity in High-Penetration County Grids

*X. Hui and colleagues* (author block placeholder)

## Abstract

High-penetration distributed photovoltaics (PV) are turning county-level 110 kV substations into bidirectional power hubs, so the traditional uniform, fixed capacity-load ratio over-invests where local generation and load diversity differ across substations. This paper formulates *capacity-load-ratio elasticity* as a bi-objective planning problem that minimizes county annualized cost against N-1 expected energy not supplied (EENS), over per-station capacity-load ratios and battery storage power. We solve it with Engineering-Prior-Guided NSGA-II (EPG-NSGA-II), which injects grid engineering priors at the two stages where infeasibility arises: Feasibility-Preserving Warm-Start Sampling for initialization, and Constraint-Ordered Repair Projection, a single-pass closed-form projection of infeasible offspring back onto the feasible manifold. On a public-data county benchmark, EPG-NSGA-II reaches the converged hypervolume of NSGA-II and NSGA-III with about 5 to 12 times fewer generations at every scale; its quality advantage then grows monotonically with problem size, reaching a 4.8% higher hypervolume than NSGA-II at K=40. The recommended per-station elastic configuration saves 13.1% over a uniform ratio of 2.0 at equal risk.

*Index Terms:* Capacity-load ratio, distributed photovoltaics, multi-objective evolutionary optimization, constraint handling, energy storage.

## I. INTRODUCTION

High-penetration distributed PV is reshaping county-level 110 kV grids from passive radial feeders into bidirectionally operating active networks. When local PV output exceeds demand around midday, feeders and main transformers carry reverse power flow, and the net-load profile deforms into a duck curve with steep evening ramps [5], [6], [7]. In this setting the traditional uniform, fixed capacity-load ratio, a single county-wide value such as 2.0, is a weak planning proxy. It is defined against one-directional peak load, ignores the spatial heterogeneity of PV and network strength, and says nothing about reverse loading [1], [2]. A single macro band therefore over-invests at some substations while leaving others exposed to reverse overload, which argues for a spatially differentiated, elastic per-station ratio keyed to hosting capacity and N-1 supply capability [3], [4], [8], [9].

A per-station configuration suits multi-objective evolutionary algorithms, and NSGA-II variants already serve distribution planning and storage siting well [10], [11], [12], [13], [14]. Generic evolutionary search, however, spends most of its budget outside the narrow, non-separable feasible region that the aggregate capacity-load band, N-1 security, and reverse-power limits carve out, and it cannot use the engineering priors a planner already holds. The waste grows with problem size: a larger county has a tighter feasible region, and every candidate still needs an expensive reliability evaluation.

Infeasibility is created at two points, population initialization and offspring constraint handling. We inject engineering priors at exactly these two points, which yields Engineering-Prior-Guided NSGA-II (EPG-NSGA-II).

This paper makes three contributions. (1) We propose EPG-NSGA-II, which embeds two engineering-prior operators, *Feasibility-Preserving Warm-Start Sampling* and *Constraint-Ordered Repair Projection*, into NSGA-II, and calls the expensive objective inside neither. (2) We design the *Constraint-Ordered Repair Projection*, a single-pass closed-form projection that repairs constraints in order of coupling strength (county band, per-station reverse gate, upstream system, band refill) and adjusts execution variables (storage) before structural variables (capacity-load ratio). (3) We build a public-data county benchmark and show that EPG-NSGA-II reaches the baselines' converged quality with about 5 to 12 times fewer generations at every scale, and that its converged-front advantage grows with scale, with a component-wise ablation attributing the gain.

## II. THE PROPOSED EPG-NSGA-II

### A. Elastic Capacity-Load-Ratio Optimization Model

We define *capacity-load-ratio elasticity* as assigning each substation its own ratio R_j instead of a county-wide constant, so that installed capacity tracks local net load and reverse-power conditions. The decision vector jointly sizes per-station capacity-load ratio and battery storage,

  x = [R_1, ..., R_K, P_1, ..., P_K],  R_j in [1.2, 3.0],  P_j in [0, 6] MW,   (1)

with storage energy E_j = 2h x P_j fixed as a slave variable.

Two conflicting objectives are minimized. The first is the county annualized cost, summed over stations,

  f_1 = sum_j (annualized capital + bidirectional network loss + storage + O&M)  [10^4 CNY/yr],   (2)

and the second is the N-1 supply risk on a future peak load peak_j(1+g)^n (g=5%, n=5),

  f_2 = sum_j EENS_j  [MWh/yr].   (3)

Three engineering constraints define a narrow, non-separable feasible region. A per-station reverse-power gate limits each station's reverse injection,

  rev_j <= beta R_j peak_j,  beta = 0.85,   (4)

the county aggregate band couples all stations and makes the problem non-separable,

  aggR = sum_j R_j peak_j / (delta sum_j peak_j) in [1.8, 2.2],  delta = 0.85,   (5)

and an upstream system limit caps the aggregate reverse injection to the higher voltage level,

  sum_j rev_j eta <= beta R_220 delta sum_j peak_j,  R_220 = 1.8,  eta = 1.0.   (6)

### B. Engineering-Prior-Guided Search

EPG-NSGA-II keeps the NSGA-II backbone and replaces random initialization and blind constraint handling with two engineering-prior operators, as Algorithm 1 shows.

*Feasibility-Preserving Warm-Start Sampling* seeds the initial population with per-station, least-cost feasible solutions built directly from the constraints in (4) to (6), so the search starts on the feasible manifold rather than reaching it by chance. This operator acts as an early accelerator: it lifts the first generations sharply, and its isolated benefit fades once the run converges (Section III-B).

*Constraint-Ordered Repair Projection* maps each infeasible offspring back onto the feasible manifold in one forward pass, repairing constraints in order of coupling strength and never evaluating f_1 or f_2. It clips R and P to their bounds, then rescales R so that aggR enters the band (5), then walks the per-station gate (4) by first raising storage to absorb reverse power and lifting R only when storage saturates, then greedily adds storage at the largest reverse-power stations until the upstream limit (6) holds, and finally refills any band deficit that step three opened. Treating execution variables before structural ones keeps each later step from breaking an earlier one. This operator is the main driver of the speedup.

Because both operators keep the population near-feasible, the selection stage needs only constraint-domination (feasibility first), so the search concentrates on the cost against risk trade-off.

**Algorithm 1: EPG-NSGA-II**
```
Input : county of K stations, band [1.8, 2.2], R_220, pop = 100, gen
Output: Pareto front F and its knee (per-station policy)
1  P <- FeasibilityPreservingWarmStartSampling(stations, band, R_220)
2  evaluate (f_1, f_2) of P with the deterministic life-cycle-cost simulator
3  for t = 1 to gen:
4      Q <- crossover and mutation of P
5      Q <- ConstraintOrderedRepairProjection(Q)     // closed-form, no objective call
6      evaluate (f_1, f_2) of Q
7      P <- environmental selection on P U Q
             by non-dominated sorting, feasibility first, crowding distance
8  return non-dominated F of P and its knee solution
```

## III. EXPERIMENTAL STUDY

### A. Setup

The benchmark is a public-data county synthesized from scaled IEEE 33-bus feeders and PVGIS irradiance for three sites, with fixed random seeds for reproducibility. We use a population of 100, county sizes K in {10, 20, 30, 40}, and three optimization seeds per configuration; each K uses a common hypervolume (HV) reference point built from all variants' final fronts, so HV is comparable within a K but not across K. Because the population is fixed at 100, generations scale with the number of function evaluations (NFE = pop x gen) and with wall-clock time, so fewer generations means proportionally less computation. Baselines run to 800 generations, EPG-NSGA-II runs to 400.

### B. Efficiency, Scale-Growing Quality, and Ablation

EPG-NSGA-II reaches the converged (generation-800) hypervolume of both NSGA-II and NSGA-III with 4.8 to 11.8 times fewer generations at every scale (Table I). At half the budget (generation 400) it already surpasses both baselines at generation 800.

The quality advantage then grows with scale. The converged HV ratio over NSGA-II rises with K (1.007, 1.007, 1.009, 1.048 for K=10, 20, 30, 40), and the ratio over NSGA-III rises likewise (1.009, 1.016, 1.030, 1.064). At small and medium scale the methods are close, near parity against the fair baseline NSGA-II (about 0.7% at K<=20), consistent with an exact-front check on small cases where classic evolutionary search already recovers the true front. As the problem grows and the feasible region tightens, the gap widens, and at K=40 EPG-NSGA-II holds a 4.8% higher hypervolume than NSGA-II (a per-seed margin of 4.4%, 4.5%, and 5.5%, so it wins in all three seeds) and 6.4% over NSGA-III. The baselines gain about 0.2% over their last 100 generations, too flat to close this gap within the convergence budget, so the advantage is a genuine converged-quality gain rather than slower convergence. NSGA-III is a many-objective method and, on this bi-objective problem, a weaker baseline; it corroborates the trend but does not lead the claim.

A two-component ablation separates the priors. The repair-only variant nearly matches full EPG-NSGA-II at convergence (repair-only over EPG = 0.997 to 1.000), so Constraint-Ordered Repair Projection is the main driver. The warm-start-only variant leads in early generations (up to 1.046 over classic NSGA-II at generation 100 for large K) but is absorbed by convergence, so Feasibility-Preserving Warm-Start Sampling is an early accelerator.

TABLE I. EPG-NSGA-II vs. baselines across K. Converged hypervolume (HV) ratios grow with scale (near parity at small K, +4.8% over NSGA-II at K=40); the repair-only column confirms the repair operator is the main driver; iso-quality speedup is the generations EPG-NSGA-II needs to reach each baseline's generation-800 HV. With pop=100 fixed for all variants, the speedup in generations equals the speedup in function evaluations and wall-clock time.

| K  | HV EPG/NSGA-II | HV EPG/NSGA-III | repair-only/EPG | speedup vs NSGA-II | speedup vs NSGA-III |
|----|----------------|-----------------|-----------------|--------------------|---------------------|
| 10 | 1.007          | 1.009           | 0.997           | 6.6x               | 7.5x                |
| 20 | 1.007          | 1.016           | 0.998           | 4.8x               | 9.1x                |
| 30 | 1.009          | 1.030           | 0.999           | 5.3x               | 11.1x               |
| 40 | 1.048          | 1.064           | 1.000           | 9.5x               | 11.8x               |

### C. County-Level Application at K=20

At the main case K=20, EPG-NSGA-II returns a 100-point cost against risk Pareto front whose knee operates at an aggregate capacity-load ratio of 1.80, with cost f_1 = 18,882 x10^4 CNY/yr and risk f_2 = 114 MWh/yr (Fig. 1a). The knee is a spatially differentiated policy (Fig. 1b): 11 stations lead with storage, 9 stations take a low ratio backed by tie-line interconnection, and no station needs R>2.0, with a maximum R* of 1.96. Stations with a high generation-to-load ratio take storage (for example, a ratio of 2.94 maps to R=1.53 with 4.48 MW), while low-ratio stations stay at a low capacity-load ratio without storage (a ratio of 0.51 maps to R=1.20). Against a uniform ratio of 2.0, which forces an aggregate of 2.35 and over-invests, the elastic configuration saves 13.1% at equal risk (EENS = 0).

## IV. CONCLUSION

We presented EPG-NSGA-II, which embeds two engineering-prior operators into NSGA-II and turns capacity-load-ratio planning of high-penetration county grids into an efficient constrained bi-objective search. It converges faster at every scale and, as the county grows, reaches a better front than either baseline. Real-grid calibration, energy-limited storage, and formal significance testing over more seeds are left to an extended version.

## References

[1] J. Xiao, R. Liu, and M. Long, "Quantitative analysis of the relationship between substation capacity-load ratio and the next-level medium-voltage distribution network," *Electric Power Construction*, vol. 36, no. 11, pp. 45-50, 2015 (in Chinese).

[2] W. Liu et al., "Adequacy analysis of regional distribution networks based on capacity-load-ratio color bands," *Journal of North China Electric Power University*, vol. 49, no. 2, pp. 1-12, 2022 (in Chinese).

[3] W. Liu et al., "Capacity-load-ratio parameter optimization for refined planning," *Journal of Electrical Engineering*, vol. 20, no. 1, pp. 208-216, 2025 (in Chinese).

[4] K. Wang, Z. He, J. Ye, Y. Lin, and Y. Ma, "Capacity-load-ratio optimal configuration for coordinated planning of multi-voltage-level grids," *Southern Power System Technology*, vol. 19, no. 7, pp. 131-139, 2025 (in Chinese).

[5] Q. Hou, N. Zhang, E. Du, M. Miao, F. Peng, and C. Kang, "Probabilistic duck curve in high PV penetration power system: concept, modeling, and empirical analysis in China," *Applied Energy*, 2019.

[6] Y. Xie et al., "The phenomenon and suppression strategy of overvoltage caused by PV power reverse flow," *Frontiers in Energy Research*, vol. 12, art. 1495742, 2024.

[7] I. S. Pereira, G. C. Vergara, J. M. Lopez-Lezama, N. Munoz-Galeano, and L. P. Garces Negrete, "Strategies to mitigate reverse power flow under high penetration of solar PV," *Energies*, vol. 19, art. 1069, 2026.

[8] S. Wang, Z. Yin, and Q. Zhao, "Integrated fine assessment of distributed PV hosting capacity for MV-LV distribution networks considering multi-level coupling," *Transactions of China Electrotechnical Society*, vol. 40, no. 6, pp. 1930-1942, 2025 (in Chinese).

[9] T. Lin, G. Wu, S. Lai, H. Hu, and Z. Hu, "Calculation of distribution network PV hosting capacity considering source-load uncertainty and active management," *Electronics*, vol. 13, art. 4048, 2024.

[10] M. Nicolini, "Multi-objective genetic algorithms in designing redundant water distribution systems," in *Proc. 2025 IEEE Int. Conf. MIND*, 2025, doi: 10.1109/MIND67540.2025.11351874.

[11] R. Zhang, H. Liu, G. Zhang, X. Ge, and M. Yu, "Planning of flexible interconnection devices for low-voltage stations based on an improved supply-capability index," *Electric Power Construction*, vol. 46, no. 8, pp. 1-11, 2025 (in Chinese).

[12] F. Xu, K. Wang, and W. Wang, "Source-grid-storage coordinated expansion planning of medium-voltage distribution systems considering operational flexibility," *Electric Power*, vol. 57, no. 7, pp. 98-108, 2024 (in Chinese).

[13] R. Wang, H. Ji, P. Li, H. Yu et al., "Multi-resource dynamic coordinated planning of flexible distribution networks," *Nature Communications*, vol. 15, art. 4576, 2024.

[14] R. Gong, H. Li, and L. Xu, "Energy storage optimal configuration for comprehensive hosting-capacity improvement of distribution networks," *Power System Technology*, vol. 49, no. 9, pp. 3860-3869, 2025 (in Chinese).
