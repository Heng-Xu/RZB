# Revision Log V2

Second-round revision driven by `paper/初稿修正建议.md`. Source of truth for content =
`paper/build_paper_docx.py` (re-run to regenerate). Outputs:
`epg-nsga-ii-paper_revised_v2.docx`, `epg-nsga-ii-paper_revised_v2.pdf` (v1 files left untouched).
Date: 2026-07-06. **No experimental numbers were fabricated or re-computed; every value is the same
data-backed number carried over from v1** (verified against `实验/有EA/results/*.csv`).

## 0. Key decision (author-confirmed): keep δ in the aggregate ratio
`初稿修正建议 §2` recommended removing δ from the aggregate capacity-load ratio and using a plain
load-weighted average with band [1.8, 2.2]. In the **actual model code** δ is not an arbitrary
constant: `county_model.py` sets `DIVERSITY_FACTOR = 0.85  # 县同时率`, and `ea_county.py` divides by
the **coincident** peak `0.85·Σpeak` in both the aggregate-ratio band and the upstream reverse limit.
Every reported number (knee aggregate ratio 1.80, uniform-baseline 2.35, 13.1% saving) was computed
with δ in place. Removing δ while keeping [1.8, 2.2] would move the knee to 1.80·0.85 = 1.53, below
the 1.8 lower bound (the knee would be self-infeasible), and would require **re-running the entire EA**.

**Author chose (AskUserQuestion): keep δ, reframe the baseline, no re-run.** δ is now explained as the
county load-coincidence factor (stations do not peak simultaneously); the regional ratio is
total capacity / county coincident peak. All numbers are unchanged and faithful to the code and to
the DL/T 5729 regional band. The 13.1% saving is a cost-vs-cost comparison at equal EENS
(`ea_baseline.csv`) and is independent of the ratio definition.

## 1. Model and Formula Corrections
- **δ / baseline (§2).** Kept δ in eq (4); deleted "forces an aggregate ratio of 2.35". The uniform
  R=2.0 case is now framed as "a regional coincident ratio of 2.35, above the elastic band, reflecting
  the over-provisioning that elastic planning removes" — a conventional reference, not an infeasible one.
- **Unified planning-year load L_j^p (§3).** eqs (4) aggregate ratio, (5) station + upstream reverse
  gates, and f_1 in (6) now all use L_j^p; the "current peak sizes capacity" split was removed. The
  growth factor (1+g)^n is common to all stations, so the aggregate-ratio value is numerically unchanged.
- **Cost objective f_1 (§4, Plan B).** No existing-capacity data, so the capacity-proxy form
  c_R R_j L_j^p is kept, with the added disclaimer "an annualized capacity proxy, not an
  incremental-investment accounting model."
- **Storage (§5, Plan A).** P_j = storage **power rating** for reverse-power absorption; explicit
  assumption added: "storage is counted only as reverse-power absorption and is not credited as firm
  N-1 backup", so f_2 excludes P_j (matches the engine `lcc_simulator._reliability`, which has no
  storage argument).
- **EENS definition (§6).** Added minimal computable form eq (7):
  `EENS_j = Σ_{s∈S_j} p_s h_s max{0, L_j^p − S_{j,s}}`, with S_j the single-element (N-1) outage-state
  set, p_s/h_s the state probability and duration, and S_{j,s} the available supply set by the
  transformer capacity and the exogenous tie-line support T_j.
- **Tie-line T_j (§7).** Stated as an exogenous, fixed input, not optimized in this short paper.
- Equation count 6 → 7; text equation references remain valid (3), (4), (5).

## 2. Algorithm Corrections (§8)
- **Algorithm 1 rewritten** to the required multi-line form: `Input:` and `Output:` on separate lines;
  initialization split into line 1 `WarmStartSampling`, line 2 `RepairProjection` (with assignment),
  line 3 `evaluate`; per-generation loop with `RepairProjection` after variation (line 6);
  `U ← P ∪ Q` (8), non-dominated sort + crowding select (9); line 11 `A ← feasible non-dominated
  individuals`, line 12 `return A`.
- **III-C prose.** Removed "one forward pass"; now "a constraint-ordered projection followed by a final
  feasibility check". Added the §8.6 fallback: if the final check still fails because all adjustable
  variables have reached their bounds, the residual violation is passed to the constraint-domination
  ranking. WarmStartSampling and RepairProjection order described (§8.4, §8.5).

## 3. Experiment Wording (§9, §10, §12, §13)
- **FE saving supported, not gutted (§9).** Defined the metric: the generation at which EPG-NSGA-II
  first reaches plain NSGA-II's converged (generation-800) hypervolume; population is fixed, so
  generations = function evaluations up to a constant. At K=40 this is generation 84, about **9.5×**
  fewer FE (recomputed from `ea_converge.csv`: 800/84). Reported K=40-specific to match Table I scope
  (§9.4 — no "across scales" claim). *(Per-K iso-quality speedups vs NSGA-II are 4.8–9.5× across
  K=10–40 in the data; a per-K column can be added if the reviewer wants it tabulated.)*
- Removed "matching an exact-front check" (§9.5).
- **NSGA-III dropped** as a baseline (§9.6, to hold 2 pages): Table I is now EPG / Repair-only /
  Warm-start-only / NSGA-II; abstract and body say "plain NSGA-II". (Restorable if space allows.)
- **Down-toned (§13):** cuts→reduces; "repair is the main driver"→"the ablation suggests the repair
  projection contributes most … in this setting"; abstract "5 to 12×"→"several times fewer"; 13.1%
  limited to the synthetic case.
- **Cost units (§12):** 18,882×10⁴ CNY/yr → "an annualized cost index of about 188.82 million CNY/yr".
- **Table I title shortened (§10.2)**; result interpretation moved to prose.

## 4. Layout and Formatting (§11, §16)
- **Fig. 1** regenerated with readable fonts (base 9 pt; per-cell R at 8 pt; colorbar label/ticks 8/7 pt),
  short axis label ("low → high generation-to-load ratio"), detail moved to caption; placed at 7.2 cm.
  Render confirms per-station R and storage text are legible. The figure source already reads
  "20 substations"; the earlier "0 substations" was an OCR/clip artifact, not present in the source.
- Fig. 1 caption shortened (§11.3).
- **Body font 9.0 → 8.6 pt** and inter-paragraph spacing removed (indent-only, IEEE style) to hold the
  2-page limit after the mandated additions (EENS equation, expanded 12-line pseudocode, +3 references,
  enlarged readable figure). References 7.7 pt, line spacing 0.86.
- Re-rendered DOCX → PDF and inspected both pages page-by-page. Fixed eq (7): the initial
  `\bigl[…\bigr]_+` form garbled/overflowed the column; rewritten as `max{0,…}` (the proven eq-(3)
  primitive) and it now fits. See `layout_check_report_v2.md`.

## 5. References (§14)
- Added **[9]** K. Deb et al., "NSGA-II," IEEE Trans. Evol. Comput., 2002 — cited in III-A.
- Added **[10]** M. E. Baran and F. F. Wu, IEEE Trans. Power Del., 1989 — for the scaled IEEE 33-bus
  feeders, cited in Setup.
- Added **[11]** PVGIS (EC JRC online database) — cited in Setup.
- NSGA-III reference not added (baseline dropped).

## 6. Author information (§15)
- Removed the mixed real-name + "(to be completed)" placeholders; uniform template placeholders now
  (First A. Author / Department, University / City, Country / email@example.com).
  **Author must fill in real information before submission.**

## 7. Deviations / author to confirm
- Body 8.6 pt (vs template ~10 pt) and tight spacing are the price of fitting all mandated additions in
  2 pages; equivalently, content could be trimmed to restore a larger font.
- Equations are 8 pt in the file; **Word honors this, a LibreOffice preview ignores per-run math sizes**
  (viewer quirk). Verify equations in Microsoft Word.
- FE saving is reported for K=40 (Table I scope); the K=10–40 range (4.8–9.5×) is in `ea_converge.csv`.
- Real author/affiliation and any real-grid calibration remain to be confirmed by the author; the case
  is a public-data-informed synthetic county, stated as such.

## 8. Third-round refinements (Table I / Fig. 1 / typography / author)
- **Table I redesigned to span county sizes.** Now K ∈ {10, 20, 30, 40} rows with a two-level header —
  "HV at gen. 100" (isolates the warm start's early acceleration) and "HV at convergence" (isolates the
  repair projection), each over NSGA-II / Warm-only / Repair-only, normalized to EPG-NSGA-II = 1.000 per K.
  All 24 values recomputed from `ea_converge.csv`. Shows both operators across scale: repair-only tracks the
  full method at convergence for every K (0.997→1.000); warm-start-only leads the baseline early for K ≥ 20
  by a widening margin (0.772 vs 0.738 at K=40) then relaxes. Prose corrected (warm start leads for K ≥ 20,
  not K=10 — at K=10 it is 0.990 vs the baseline's 0.994).
- **Fig. 1 clarity.** DOCX embeds the full-resolution PNG (600 dpi source). The softness seen before was
  LibreOffice's PDF export downsampling images to 300 dpi; the verification PDF is now exported with
  `ReduceImageResolution=false` (MaxImageResolution 1200), so the figure is crisp. Standalone vector copies
  `fig1_matrix.pdf` and `fig1_matrix.svg` are provided for manual insertion (Word 2016+ embeds SVG as
  vector). python-docx cannot embed EMF/PDF, so the automated pipeline keeps the high-res PNG.
- **Typography aligned to the exemplar** (`参考文献/对标期刊/短篇/Swarm…pdf`, measured with PyMuPDF:
  title 23.9 pt regular, body 10 pt, abstract 9 pt, affiliation 10 pt italic, headings/refs 8 pt, all
  Times/Nimbus Roman): title 22 → **24 pt** regular; affiliation 9 pt gray → **10 pt italic black**; section
  headings small-caps changed from **bold to regular**. Body is **8.6 pt** — the exemplar's 10 pt cannot
  co-exist with our denser content (7 equations, 12-line algorithm, multi-K table, figure, 11 references)
  inside the 2-page limit (10 pt → 3 pages). Closing this last gap needs a 3rd page or content cuts;
  flagged for the author.
- **Author block filled with real information:** Heng Xu; School of Electrical Engineering, China University
  of Mining and Technology; Xuzhou, Jiangsu, China; ts24230188p31@cumt.edu.cn (placeholder removed).
- Re-verified on the shipped PDF: 2 pages; em-dash 2 / en-dash 0; no §13 banned words; citations [1]-[11];
  equations (1)-(7); Table I's 24 values match the CSV.
