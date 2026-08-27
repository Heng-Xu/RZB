# Truthfulness Audit — epg-nsga-ii-paper_revised

Audit of the revised paper against the **actual modeling scripts** (`实验/有EA/scripts/county_model.py`,
`ea_county.py`, `lcc_simulator`) and the **result CSVs** (`实验/有EA/results/*.csv`). Date: 2026-07-05.

## 1. Model equations vs. code (`county_model.py`, `ea_county.py`)
| Paper | Code ground truth | Verdict |
|---|---|---|
| x = {(R_j, P_j)}; R∈[1.2,3.0], P∈[0,6] MW, E_j=2P_j h (slave) (1) | `R_LO,R_HI=1.2,3.0`; `P_LO,P_HI=0,6`; `STORAGE_HOURS=2.0`, `e_mwh=2·p_mw` | **Faithful** |
| L_j^p = L_j(1+g)^n, g=5%, n=5 (2) | growth applied inside `lcc_simulator` for the N-1 EENS only; `build_county` peak has no growth | **Faithful (caliber clarified, see below)** |
| r̃_j(P_j)=max{0, r_j^0 − P_j} (3) | `station_reverse_injection = max(0, 0.9·pv − 0.3·peak − P·1000)` = storage genuinely absorbs reverse | **Faithful** |
| aggregate 1.8 ≤ Σ R_j L_j /(δ Σ L_j) ≤ 2.2, δ=0.85 (4) | `aggR = Σ(R·peak)/(0.85·Σpeak)`, `DEFAULT_BAND=(1.8,2.2)` — **current peak** | **Faithful (now uses L_j)** |
| station gate r̃_j ≤ β R_j L_j, β=0.85 (5) | `lim = REVERSE_TX_LIMIT·R·peak`, `REVERSE_TX_LIMIT=0.85` — **current peak** | **Faithful (now L_j)** |
| upstream η Σ r̃_j ≤ β R_220 δ Σ L_j, η=1.0, R_220=1.8 (6) | `L_rev = 0.85·r220·(0.85·Σpeak)`; `REVERSE_COINCIDENCE=1.0`; `R220=1.8` — **current peak** | **Faithful (now L_j)** |
| f_1 = Σ(c_R R_j L_j + c_P P_j + C_j^loss + C_j^om) (7) | `lcc_simulator.compute`: `annualized_cost = CRF·(Z1 substation + Z2 line + storage capex) + Z3 O&M + Z4 bidirectional loss − Z5 salvage`, then `f1 = annualized_cost − reliability`; Z1 ∝ tx=R·peak (current), storage capex ∝ P, Z4 flow-dependent | **Faithful (schematic; Z2 line ≈ const in the EA config, Z5 salvage a credit, folded)** |
| f_2 = Σ EENS_j(R_j, T_j, L_j^p) (8) | `_reliability`: `deficit = max(0, peak·(1+g)^n − n1_self(tx=R·peak) − cd·peak)`, `EENS = deficit·pf·n1_hours`. **Verified at engine level**: growth `(1+g)^n` (line 341) and tie-line `cd` (line 344) are used; **storage is NOT a `_reliability` argument** | **Faithful after correction: P_j removed from EENS** |
| tie-line support T_j exogenous | `cd` sampled per station in `build_county`, passed as `interconnection_cd` | **Faithful** (T_j = 联络度 CD) |
| constraint-domination / feasibility-first selection | `CountyProblem` returns G; pymoo NSGA-II constraint handling | **Faithful** |

### Corrections made this audit (two, both from reading the actual code)

**(ii) Storage removed from EENS.** Reading the engine `lcc_simulator._reliability(tx_mva, peak_mva,
peak_load_kw, cd)` showed it takes **no storage argument**: `deficit = max(0, peak·(1+g)^n − n1_self −
cd·peak)`. So storage `P_j` does **not** reduce N-1 EENS; it enters only the reverse-power constraints
(3),(5),(6) and the cost (7). The draft's `EENS(R_j, P_j, T_j, L_j^p)` (which the spec §5.10 had requested)
was corrected to `EENS(R_j, T_j, L_j^p)`, and the text now says storage relaxes the reverse-power
constraints rather than lowering risk. This is physically sensible: 2-hour storage absorbs midday reverse
PV but does not provide N-1 peak-supply backup, which comes from transformer capacity (R) and tie-line (cd).
Engine-level checks also **confirmed** growth `(1+g)^n` (line 341) and tie-line `cd` (line 344) are actually
computed, so eq (2) and the `T_j` term in eq (8) are grounded, not docstring-only.

### (i) Load caliber
The draft (following the spec's "unify to L_j^*") used **L_j^p everywhere**. The code sizes transformer
capacity as `tx = R·peak` against the **current** peak and applies growth `(1+g)^n` **only in the N-1
EENS**. So eqs (4)-(7) now use **current peak L_j**, and only (8) EENS keeps **planning-year peak L_j^p**;
the load definition text was updated to state this split explicitly. (For the aggregate ratio the growth
factor cancels, so this is exact; for the station gate and upstream limit, L_j^p had made the bounds
~1.28× too lenient.) This is the only substantive model-fidelity fix.

## 2. Numbers vs. result CSVs (all re-verified this session)
| Claim in paper | CSV source | Verified value |
|---|---|---|
| 13.1% cost saving vs uniform R=2.0 at equal EENS | `ea_baseline.csv` | rigid f1=21836, aggR=2.35, EENS=0; EA=18985 → **13.1%** ✓ |
| K=20 knee: cost 18,882×10⁴, EENS 114, aggR 1.80, 100 pts | `ea_county_pareto.csv` | f1=18882, f2=114, 100 pts ✓ |
| 11 storage / 0 above 2.0 / max R*=1.96 | `ea_county_strategy_knee.csv` | 20 stations, 11 storage, 0>2.0, max 1.96 ✓ |
| Converged HV ratio EPG/NSGA-II 1.007/1.007/1.009/1.048 | `ea_converge.csv` | exact ✓ |
| Converged HV ratio EPG/NSGA-III 1.009/1.016/1.030/1.064 | `ea_converge.csv` | exact ✓ |
| repair-only/EPG 0.997/0.998/0.999/1.000 | `ea_converge.csv` | exact ✓ |
| FE ratio vs NSGA-II 6.6/4.8/5.3/9.5× ; vs NSGA-III 7.5/9.1/11.1/11.8× | `ea_converge.csv` (iso-quality) | recomputed exact ✓ |
| "5 to 12 times fewer FE" | derived from 4.8-11.8× | ✓ |

**No fabricated numbers.** The spec's "27.8% fewer function evaluations" is **not** in the data and was
**not** used; the real result (4.8-11.8×) is stronger and is what the paper reports (see `revision_log.md` §0).

## 3. Experimental setup vs. code
- pop=100, K∈{10,20,30,40}, 3 optimization seeds, per-K common HV reference point — matches `ea_converge.py`.
- Baselines (plain NSGA-II, NSGA-III) to 800 generations; EPG-NSGA-II to 400 — matches.
- Benchmark = public-data-informed **synthetic** county from scaled IEEE 33-bus + PVGIS (three sites,
  reverse-hour anchors 2841/3017/3103 h) — matches `county_model.py` / `PVGIS_TREV`. Not real-grid data.
- "N-1", "equal EENS", "iso-quality speedup", "converged (gen-800)" framings all match the code/results.

## 4. Residual caveats (author to note, not defects)
- f_1 (7) is a **schematic decomposition** of the simulator's annualized LCC (capex→CRF annuity + Z4
  network loss + storage + O&M, minus the reliability term, which becomes f_2). It is not a closed-form:
  the bidirectional-loss term C_j^loss is power-flow dependent, and capex may involve discrete
  transformer sizing in the mixed-integer variant. Presented as "aggregates … terms" — honest at the
  schematic level; do not read c_R/c_P as calibrated coefficients.
- EENS_j is described by its dependencies (R, P, T_j, L_j^p) under N-1; the paper does not give a
  closed-form probability model (consistent with the short-paper scope and the simulator).
- Storage energy is E_j=2P_j h as a **slave** variable; energy-limited charge/discharge is not modeled
  (a stated limitation).
- Results are single-run per (K, seed) with 3 seeds; no formal significance test (stated as future work).

## 5. Text-condensation directions (1-2 APPLIED 2026-07-05; 3-5 remain optional)
Ranked by value; equations and pseudocode must not be cut (spec §16, §21).
1. **[APPLIED] Merge equations 8 → 6**: the two reverse constraints (old 5+6) are now one eq (5) as two
   stacked display lines under one number, and the two objectives (old 7+8) one eq (6) as a three-line
   `min (f_1, f_2)` / `f_1=…` / `f_2=…` block. Implemented via stacked single-line `oMathPara` (not
   `aligned`) to reuse the Word-verified primitive. All definitions kept; refs renumbered. See
   `revision_log.md` §5.
2. **[APPLIED] Single algorithm box**: `RepairProjection` folded into Algorithm 1 as the `Repair`
   procedure (lines 11-17) behind an internal divider; box breaks only at the procedure boundary.
   Steps are denser but no logic was cut. III-C prose updated to point at "Algorithm 1, lines 11-17".
3. **Merge Intro P1+P2**: both open on "uniform ratio inadequate"; fuse background and the
   existing-method gap into one paragraph. ~3 lines. *(not applied)*
4. **Results IV-B**: 3 paragraphs → 2 (fold "quality grows with scale" and the plateau sentence together). *(not applied)*
5. **Abstract**: ~180 → ~150 words by cutting one clause. *(not applied)*
The applied pass kept the paper at a clean **3 pages** while enlarging Fig. 1 (each sub-panel ≈ one
column wide). Directions 3-5 would only be needed if the venue mandates 2 pages — **recommend deciding
after confirming the MIND short-paper page limit.**

## 6. Bottom line
The revised paper's model, numbers, and experimental setup are **faithful to the code and results** after
two corrections found by reading the actual code (including the objective engine `lcc_simulator.py`):
(i) load caliber, eqs (4)-(7) use current peak `L_j`, EENS (8) uses `L_j^p`; and (ii) storage removed
from EENS (the engine's `_reliability` has no storage input). The f₁ composition, and EENS's use of
growth `(1+g)^n` and tie-line `cd`, were verified in the engine (not taken from docstrings). Author still
to confirm: (a) the 27.8%-vs-real efficiency framing (`revision_log.md` §0); (b) real author/affiliation;
(c) the MIND page limit (drives whether to apply the condensation directions in §5).
