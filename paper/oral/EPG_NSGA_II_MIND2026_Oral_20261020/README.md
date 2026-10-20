# EPG-NSGA-II oral presentation workspace

The current files are linked from [the delivery directory](../README.md).
The scientific source is `sources/EPG-NSGA-II_MIND2026_CameraReady_v4.pdf`.
Recovered historical model code and CSV results are in `sources/historical_model/`;
`sources/historical_model_manifest.json` records original paths and hashes.

## Maintained files

- `design_spec.md`, `spec_lock.md`: approved five-slide design and content contract.
- `svg_output/`: hand-authored editable slide sources with exact LaTeX markers.
- `notes/`: frozen English script and per-slide speaker notes.
- `prepare_research_figures.py`: full-data figure computation and vector exports.
- `prepare_formula_previews.py`: vector math fragments; does not author slides.
- `package_delivery.py`: creates PDF/script, copies the newest native PPTX and
  verifies source hashes, result values, native objects and speaker notes.
- `figures/`, `analysis/`: figure resources, plotting data and provenance.
- `validation/`: quality/chart checks, actual-PDF review, delivery hashes and
  2560×1440 renders with enlarged mathematical details.
- `.review/`: independent per-page visual findings and the cover-label backup.
- `exports/`: timestamped native exports; current delivery hashes are recorded
  in `validation/delivery_audit.json`.
- `backup/`, `archive/`: earlier sources and superseded deliverables.

## Rebuild

Use the installed `ppt-master` workflow and its absolute tool paths. Run its
attribution guard first. Do not replace these sources with a historical deck generator.

After source edits, run the final canonical SVG quality checker, affected chart
checks and visual review, then `finalize_svg.py` and `svg_to_pptx.py` in order.
Split notes only when `notes/total.md` changes.

Packaging requires Python with PyMuPDF, python-docx and Playwright, plus its
Chromium browser. The local command, from this workspace, is:

```bash
env PYTHONPATH=/tmp/pptmaster-render-deps /home/xh/anaconda3/envs/xuzhou110kv_clr/bin/python package_delivery.py
```

Install dependencies in a durable environment when rebuilding elsewhere.
The native exporter also needs `python-pptx` and `xlsxwriter`; its local command
uses `PYTHONPATH=/tmp/pptmaster-deps`. Temporary dependency directories are
machine state and are not project sources.

Read the actual final PDF after packaging. Chromium is required: CairoSVG
collapses script positioning in this deck. Formula previews use vector paths
and are replaced by editable Office Math during native PPTX export.

Native Microsoft PowerPoint rendering was not available locally; WPS is outside
the native-math renderer contract. No optimization was rerun. Archived CSV
values reproduce the paper, but their selection labels do not independently
establish the paper's common knee-point selection history. The exact
qualification is retained in `validation/delivery_audit.json`.
