# Scientific chart choices

The user retained the five-page structure and requested better visual quality and a scientific tone. Template and design choices were previously delegated. Chart positions are settled: P02 supplies station context and P04 supplies experimental evidence.

The profiler read convergence data (33,600 rows × 5 columns) and station data (20 rows × 8 columns). K has four levels, algorithm five, and each K/algorithm has three independent runs. Generations are repeated observations within runs, not independent replicates. Unequal row counts reflect 400/800 generation budgets. No run, method or station is dropped. No route cutoff, density estimation or binning is used.

The paper's selected claims govern the figures: K=40 EPG mean final normalized HV is 1.048, repair-only 1.048, seeding-only 0.998, NSGA-III 0.985 and NSGA-II 1.000. EPG's mean crosses the reference at generation 84. In the reported K=20 design, station CLR spans 1.55–2.64 across source-load ratios 1.809–3.492. These values were computed before drawing.

1. Station context: relationship plus variation. Choose a scatter with all 20 stations and the 2.0 cap reference. A station-ranked dot plot is an alternative but hides the source-load relationship. Reject a heatmap because color weakens quantitative precision, bubbles because storage adds another area encoding, and a fitted line because no regression claim is needed.
2. Search dynamics: trend plus uncertainty. Choose mean curves with sample-SD envelopes, n=3 independent runs, and reference HV=1.0. EPG/NSGA-II occupy the main panel; all five methods remain in the adjacent ablation. Raw trajectories are an alternative. Reject terminal bars alone because they conceal convergence and a five-curve overlay because repair/full overlap obscures the component result. EPG ends at generation 400; baseline at 800.
3. Ablation: comparison plus uncertainty. Choose all three terminal run points per method, with a distinct mean tick. The 0.96–1.07 scale is explicit. A table is an alternative. Reject a mean-only bar because it hides raw n=3 and cannot legitimately use that truncated scale, and a violin because three values do not support a density.

No spatial coordinates exist. SD is descriptive, not a confidence interval; no significance claim is made. The ablation uses positions rather than lengths. All generations determine means/SD; native path simplification stays below 0.45 slide pixels, without statistical smoothing. Full-resolution standalone vectors and source arrays are retained.

Native-ready decisions are object-specific: marker-only station scatter plus an independently dashed cap; lower-and-upper SD envelopes; and jittered runs plus mean-tick glyphs. These forms stay editable DrawingML geometry rather than being simplified to the exporter's closed native Chart payload. Two equations use native Office Math.

Anti-pattern review found no truncated bars, hidden replicates, fabricated traces, missing runs, undisclosed intervals, dual axes or perspective marks. The graphical abstract uses equal symbolic decision nodes and contains no invented device ratings. Destination is conference slides, not a claim of compliance with an unverified journal specification.
