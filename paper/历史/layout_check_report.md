# Layout Check Report — epg-nsga-ii-paper_revised

## 1. Files Checked
- Revised DOCX: `paper/epg-nsga-ii-paper_revised.docx` (424 KB)
- Revised PDF:  `paper/epg-nsga-ii-paper_revised.pdf` (247 KB, from LibreOffice `--convert-to pdf`)
- Rendered pages: page-1/2/3 PNG at 150–200 dpi (`pdftoppm`), inspected visually
- OCR / text: **OCR engine (tesseract) was unavailable in the environment (no install privileges);
  layout was checked using rendered page images and PDF text extraction (`pdftotext`, `python-docx`),
  which for this born-digital PDF is at least as reliable as OCR.**

## 2. Page Count
- Revised paper page count: **3**
- Reference short-paper page count: 2 (the three IEEE-CIS references) / 3 accepted by template
- Result: 3 pages. Kept at 3 (not 2) because the revision strengthened the model (8 numbered equations)
  and pseudocode (2 algorithm boxes), which the spec says must not be cut to save space (§16, §21).
  No blank page, no orphaned equation, no mid-column full-width break issue.

## 3. Per-Page Recognition Summary
| Page | Main content confirmed | Problems found | Action |
|---|---|---|---|
| 1 | Title, author block, Abstract (bold, `Abstract—`), Index Terms (bold), I. Introduction (4 paras), II-A Problem Formulation with eqs (1)-(6) | `L_j^*` superscript asterisk + `\underline/\overline{R}` rendered as garbled glyphs | Switched `L_j^*`→`L_j^p` (roman superscript) and band bounds to explicit 1.8/2.2; re-rendered, clean |
| 2 | II-B objectives eqs (7)-(8); III EPG-NSGA-II with Algorithm 1 (main) and Algorithm 2 (RepairProjection); IV-A Setup; IV-B Efficiency/Ablation; Table I caption | none after the eq fix | Verified clean at 200 dpi |
| 3 | Table I (three-line, all rows), IV-C application, Fig. 1 (2 panels), V. Conclusion, References [1]-[8] | none | Verified clean |

## 4. §11.4 Checklist
1. Page count: revised 3 / reference 2 → within accepted 3-page envelope.
2. Title block: title, author, affiliation/e-mail placeholder all centered and complete.
3. Abstract + Index Terms: both on page 1, `Abstract—` and `Index Terms—` IEEE format, bold.
4. Section headings: I–V recognized, IEEE-numbered, order correct.
5. Equations: numbers (1)-(8) present and continuous; no isolated equation at a page top; no overflow;
   consistent spacing (spacer paragraphs between adjacent equation tables).
6. Algorithm: Algorithm 1 and Algorithm 2 titles recognized; line numbers readable; blocks not broken
   across columns (`cantSplit`).
7. Table: Table I title recognized; readable at 8 pt; no split/clipped rows; placed full-width, page-3 top.
8. Figure: Fig. 1 caption recognized; two sub-panels; internal text (R values, storage, axes) readable;
   no clipping.
9. References: begin in the REFERENCES section, IEEE-numbered [1]-[8], italic journal names, readable,
   two-column continuous; no large blank area.
10. Overall: no overlap, no clipped text, no abnormal blank page, no single formula/table orphan.

## 5. Comparison with Template and References
| Item | Expected (template / refs) | Revised | Pass/Fail |
|---|---|---|---|
| Page size / margins | Letter, T0.75/B1.0/L·R0.62 in | same | Pass |
| Two-column body | Yes | Yes (0.25 in gap) | Pass |
| Title block | Centered, ~24 pt, not bold | 22 pt (long title), centered | Pass |
| Abstract | Page-1 top, bold, `Abstract—` | Yes | Pass |
| Index Terms | 4-6 keywords, bold | 5 keywords, bold | Pass |
| Equations | In-column, numbered, no overflow | Yes (native OMML) | Pass |
| Algorithm | Block, readable line numbers | 2 three-line boxes | Pass |
| Table | Page top/bottom, readable | Full-width, page-3 top | Pass |
| Figure | Readable internal text | 2-panel, readable | Pass |
| References | IEEE numbered, italic venue | Yes | Pass |

## 6. Remaining Risks / Notes for the Author
- **27.8% vs the real number**: see `revision_log.md` §0. The paper uses the real, data-backed result
  (≈5-12× fewer function evaluations), not the spec's assumed 27.8%. Author to confirm the claim.
- Rendering was validated in **LibreOffice** (PDF). The intended review tool is **Microsoft Word**;
  Word renders OMML with Cambria Math and may differ slightly. A final pass in Word is advised.
- Author/affiliation/e-mail are placeholders and must be completed before submission.
- Page count is 3; if the venue mandates 2 pages, compress per spec §16 (trim intro, shorten captions,
  prune references) without cutting equations or pseudocode, or confirm the MIND short-paper page limit.
- `c_R`, `c_P`, and the EENS evaluator are described structurally; the paper does not include full LCC
  discounting or a closed-form EENS probability model (consistent with a short paper and with the actual
  simulator). Numerical cost/reliability coefficients remain the author's to verify against the code.
