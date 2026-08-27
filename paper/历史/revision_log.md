# Revision Log — epg-nsga-ii-paper

Revision driven by `paper/初稿修正建议.md`. Source of truth for content = `paper/build_paper_docx.py`
(re-run to regenerate). Outputs: `epg-nsga-ii-paper_revised.docx`, `epg-nsga-ii-paper_revised.pdf`.

## 0. Headline divergence from the spec (author sign-off needed)
The spec (§3.2, §4.1, §7.3, §12.1) assumes the paper reports a **"27.8% reduction in function
evaluations."** That number appears **nowhere** in the project's data or the original draft (verified by
searching `03_EA实验结果摘要.md`, `05_论文图表清单`, `ea_converge.csv`, and the source `.md`).
The real, data-backed efficiency result is an **iso-quality speedup of 4.8–11.8× fewer generations**
(equivalently function evaluations, since pop is fixed) to reach each baseline's generation-800
hypervolume. Per the spec's own no-fabrication rule (§3.2), **27.8% was NOT inserted**; instead the real
result is expressed in the spec's unit ("about 5 to 12 times fewer function evaluations… a comparable
converged Pareto front"), down-toned to the tested setting. Note the mismatch direction: the true
reduction is **larger** than 27.8%, not smaller. **Author must confirm which figure to claim.**

## 1. Model and Equations (Section II, faithful to the actual simulator/repair code)
- Split Method into **II. Problem Formulation** (A. Decision Variables and Planning Constraints;
  B. Cost-Risk Objectives) and **III. Engineering-Prior-Guided NSGA-II** (§13).
- Defined planning-year peak load `L_j^p = L_j(1+g)^n` (eq 2). **Load caliber corrected in the
  truthfulness audit (2026-07-05)**: the code sizes capacity as `tx = R·peak` against the CURRENT peak
  and applies growth only inside the N-1 EENS, so eqs (4)-(7) use current peak `L_j` and only the EENS
  objective (8) uses `L_j^p`. See `truthfulness_audit.md` §1.
- Added **residual reverse power** `r̃_j(P_j) = max{0, r_j^0 − P_j}` (eq 3), so the storage variable
  `P_j` now genuinely enters the reverse-power constraints (this closes the variable↔constraint gap
  flagged in spec §5; it matches the code `rev = max(0, 0.9·pv − 0.3·peak − P·1000)`).
- Station reverse-power gate `r̃_j(P_j) ≤ β R_j L_j^p` (eq 5) and upstream limit
  `η Σ r̃_j(P_j) ≤ β R_220 δ Σ L_j^p` (eq 6) now use the residual and are fully parameter-explained
  (β=0.85, R_220=1.8, η=1.0, δ=0.85).
- Aggregate ratio written as a load-weighted average within `[1.8, 2.2]` (eq 4).
- Objectives: annualized cost `f_1` with capacity, storage, bidirectional-loss, and O&M terms (eq 7);
  N-1 risk `f_2 = Σ EENS_j(R_j, P_j, T_j, L_j^p)` (eq 8), making EENS explicitly depend on ratio,
  storage, tie-line support `T_j` (= the model's per-station 联络度/CD, exogenous), and future load.
- **Tie-line support** now appears in the model (`T_j`, eq 8) before it is used in the results,
  removing the earlier gap where "tie-line" appeared only in the results text.
- Equations rendered as native Word math (OMML). Fixed a renderer glyph issue: `L_j^*` superscript
  asterisk garbled in LibreOffice, switched to `L_j^p` (roman "p", planning-year); band bounds written
  as explicit 1.8/2.2 instead of `\underline/\overline{R}`.

## 2. Algorithm (Section III)
- **Algorithm 1 (EPG-NSGA-II main loop)**: warm start → repair on the initial population → per-generation
  loop with `RepairProjection` **after** selection/crossover/mutation → constraint-domination
  environmental selection → returns the **feasible** non-dominated set.
- **Algorithm 2 (RepairProjection)**: explicit repair order — clip; rescale aggregate ratio into band;
  per-station gate (raise storage first, raise ratio only if storage saturates); upstream greedy storage;
  **re-check the aggregate band**; and, when bounds prevent full repair, **keep the residual violation for
  the constraint-domination rule** (no false feasibility claim).
- WarmStartSampling described with concrete engineering logic (sample ratios in bounds → project weighted
  aggregate into band → allocate storage by residual reverse-power pressure `r_j^0/(R_j L_j^p)`).

## 3. Language (down-toned, case-limited; spec §3.3, §3.4, §12)
- Removed over-strong claims: "the gain is genuine" → "unlikely to be explained solely by delayed baseline
  convergence within the tested budget"; "this operator drives the speedup" → "the ablation … suggests …
  contributes most"; dropped "least-cost". "guarantee" now appears only in the negation "does not
  guarantee it".
- "public-data county benchmark" → "public-data-informed synthetic county case"; results framed as
  "in the tested setting / in this case".
- Contributions rewritten as "The main contributions are as follows." (no AI-template phrasing).
- "wall-clock time equals function evaluations" → "when objective evaluation dominates runtime,
  wall-clock time is expected to track function evaluations."
- Retained (unchanged, real) numbers: 13.1% cost saving vs uniform R=2.0 at equal EENS; 4.8–11.8× fewer
  generations/FE; K=20 synthetic case; converged-HV ratios; max R* = 1.96.

## 4. Layout
- Kept the official-template page setup (US Letter; margins T0.75/B1.0/L·R0.62 in; two columns;
  papertitle 24→22pt to fit the longer revised title; author 11pt; Abstract 9pt bold with `Abstract—`;
  small-caps section headings; references 8pt, IEEEtran style with italic journal names).
- Full-width Table I (three-line) and full-width Fig. 1 placed via section breaks; algorithm boxes kept
  in-column with `cantSplit` so they never break across a column.
- Converted DOCX → PDF (LibreOffice), rendered every page to PNG, and inspected page-by-page; see
  `layout_check_report.md`. Result is a clean 3-page paper (references included).

## 5. Condensation pass (2026-07-05, author-selected directions 1-2 of the audit §5 + figure)
Three edits, one file (`build_paper_docx.py`), verified by rebuild + full-page render:
- **Equations 8 → 6.** Merged the two reverse-power constraints (old 5+6) into one eq (5) as two
  stacked display lines under a single number, and the two objectives (old 7+8) into one eq (6) as a
  three-line block `min (f_1, f_2)` / `f_1=…` / `f_2=…`. Implemented by extending `eq()` to accept a
  list of LaTeX lines, each rendered as its own **single-line `oMathPara`** (the already-Word-verified
  display primitive — no `aligned`/`m:eqArr`, so zero new rendering risk). Renumbering is clean: (1)
  decision vector, (2) L_j^p, (3) residual reverse, (4) aggregate band, (5) reverse constraints
  [merged], (6) objectives [merged]. Prose updated: the objective explanation now merges the old
  `AFTER_F1`+`AFTER_F2` into one paragraph; equation-number references corrected to "(3) and (5)" and
  "the variable bounds and (4), (5)"; no stale (7)/(8)/(4)-(6) remain. Structural assert: 9 display
  `oMathPara` lines, 6 numbers.
- **Two algorithm boxes → one.** `RepairProjection` (old Algorithm 2) is now the `Repair` procedure
  inside a single **Algorithm 1** box, continuous numbering 1-17 (main loop 1-10; a bold, top-ruled
  `procedure Repair(x = {(R_j, P_j)}):` divider; repair steps 11-17). `algo_box` gained `proc_head`/
  `proc_lines`: the procedure sits in its own table row so the box may break **only at the procedure
  boundary** (avoids a tall `cantSplit` block jumping a whole column — no column gap in the render).
  Prose: III-C now reads "the repair projection (Algorithm 1, lines 11-17)". Repair steps kept faithful
  (clip+rescale, per-station gate raising storage then ratio, upstream greedy, re-check band + keep
  residual for constraint-domination), just denser lines — no logic cut (spec §16/§21).
- **Fig. 1 enlarged** from 11.0 cm to 17.0 cm (full text width). Each of the two sub-panels is now
  ≈ one column wide (≈ 8.5 cm), effective 567 dpi; render confirms axis labels, tick text, the knee
  annotation, and the ratio-matrix cell/colorbar text are all legible.
- **Net:** page count stays **3**; all retained numbers intact (13.1% / 5-12× / 1.048 / 4.8% / 1.96 /
  18,882 / 114 / 2.35); body em/en-dash count still 0 (the two `—` are the IEEE `Abstract—`/`Index
  Terms—` tokens). Acceptance target is Word: the merged blocks reuse the Word-verified single-line
  `oMathPara`, so no new Word-rendering risk was introduced.
