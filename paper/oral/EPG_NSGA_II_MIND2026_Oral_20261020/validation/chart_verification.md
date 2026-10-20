# Research chart verification

verify-charts: 02_problem.svg | object=station-heterogeneity | type=scatter | mode=direct-calc | scale=x1.7..3.6,y1.2..3.0 (ticks) | calc=ran; all20 points recomputed | svg=unchanged

verify-charts: 04_results.svg | object=convergence-hv | type=line+SD | mode=decomposable-calc | scale=x0..800,y0..1.1 (ticks) | calc=ran; mean and SD fragments checked | svg=unchanged

verify-charts: 04_results.svg | object=ablation-hv | type=raw-runs+mean | mode=decomposable-calc | scale=x0.96..1.07 (ticks) | calc=x ran; nominal rows=371+43i, jitter=-4,0,4 | all15 points recomputed | svg=unchanged

Full-data normalization and sample SD are recorded in figures/provenance.json. Curve geometry simplification is bounded by 0.45 slide px, below the stroke width; no statistical smoothing is applied. EPG ends at generation 400.
