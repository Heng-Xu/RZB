# Layout Check Report V2

## 1. Files Checked

- Revised DOCX: `paper/epg-nsga-ii-paper_revised_v2.docx` (≈ 279 KB)
- Revised PDF:  `paper/epg-nsga-ii-paper_revised_v2.pdf` (≈ 210 KB)
- Rendered pages: `scratchpad/fin-1.png`, `p2b-2.png` (120 dpi), plus 200 dpi eq-crop checks.

Method note (per §16.3): `tesseract` was unavailable in this environment, so the readability check was
done by rendering every page (`pdftoppm`) and inspecting the PNGs directly (visual OCR by the author),
plus `pdftotext` extraction for the numeric/citation integrity checks.

## 2. Page Count

- Page count: **2**
- Target: 2 (MIND 2026 short-paper hard limit, incl. all text, figures, and references)
- Result: **PASS**

## 3. OCR / Visual Readability Check

| Item | Result | Notes |
|---|---|---|
| Title block | Pass | Title, author, affiliation (uniform placeholders), centered. |
| Abstract / Index Terms | Pass | `Abstract—` / `Index Terms—` bold-italic; the only two em-dashes in the file. |
| Equation layout | Pass | (1)-(7) all present and numbered; none overflow the column after eq (7) was rewritten (`max{0,…}` replaced the garbled `[·]₊`). |
| Algorithm 1 | Pass | `Input:` / `Output:` on separate lines; lines 1-12 legible; `RepairProjection` appears at init (line 2) and after variation (line 6), each with an assignment. |
| Table I | Pass | Short title ("Ablation on the K=40 synthetic case…"); 4 methods (EPG / Repair-only / Warm-start-only / NSGA-II); three-line rule; not split across the column. |
| Fig. 1 | Pass | Full 20-station matrix; per-station R and storage text legible; short axis label; caption carries the detail. No "0 substations" artifact. |
| References | Pass | [1]-[11] continuous across the two columns; hanging indent; no orphan. |

## 4. Integrity Spot-Check (pdftotext)

- Numbers intact: 13.1%, 188.82 million CNY/yr, 9.5× / generation 84, aggregate ratio 1.80,
  coincident ratio 2.35, max R 1.96, EENS 114 MWh/yr, HV 0.772 / 0.738 / 0.952 / 0.954 / 1.000.
- Citations [1]-[11] all present; equation numbers (1)-(7) all present.
- Em-dash count = 2 (the two IEEE tokens only); en-dash = 0.
- "NSGA-III" absent (baseline dropped); no stale "2.35 forces", "5 to 12 times", "exact-front",
  "one forward pass".

## 5. Remaining Layout Risks

- **Renderer caveat:** verification used LibreOffice for DOCX→PDF. Equations are 8 pt in the file;
  Word renders them at 8 pt, but a LibreOffice/WPS preview ignores per-run math sizes and may show them
  larger. Confirm the equations and Algorithm 1 in Microsoft Word before submission.
- **Body font 8.6 pt** (below the ~10 pt template default) and tight spacing were required to hold 2
  pages after the mandated additions; readable but small. If a larger font is required, trim content.
- Fig. 1 in-figure text is legible at the ~6.9 cm placement but is dense (20 cells); check on the final
  print medium.

## 6. Third-round updates (Table I / Fig. 1 / typography / author)

- **Page count still 2** after the changes below (re-rendered and inspected).
- **Table I** is now a K ∈ {10,20,30,40} matrix with a two-level header ("HV at gen. 100" | "HV at
  convergence", each over NSGA-II / Warm / Repair, EPG = 1.000 reference in caption). Verified: the two-row
  header merges render correctly, no value wraps (tight cell margins), and the table does not split across
  the column break (kept together). All 24 numbers match `ea_converge.csv`.
- **Fig. 1** exported without image downsampling (`ReduceImageResolution=false`, MaxImageResolution 1200):
  the verification PDF is now crisp. DOCX embeds the full-res 600-dpi PNG; standalone `fig1_matrix.pdf` and
  `fig1_matrix.svg` are provided for manual vector insertion in Word.
- **Typography matched to the Swarm exemplar:** title 24 pt regular (was 22), affiliation 10 pt italic black
  (was 9 pt gray), section headings regular small-caps (was bold). Body 8.6 pt — the exemplar's 10 pt does
  not fit 2 pages with this content density (would be 3 pages); flagged for the author.
- **Author block** now real: Heng Xu / School of Electrical Engineering / China University of Mining and
  Technology / Xuzhou, Jiangsu, China / ts24230188p31@cumt.edu.cn.
- **Renderer caveat (important):** the crispness fix is in the LibreOffice export command, not the DOCX.
  When exporting the DOCX to PDF, either open in Microsoft Word (preserves the full-res image) or use the
  no-downsample export option; a plain LibreOffice "export to PDF" may soften the figure again.
