Our solution adds engineering-prior seeding and feasibility repair to standard NSGA-II. The key change is how candidate plans are constructed and adjusted.

For the initial population, we sample station CLR values, start storage power at zero, and apply repair before evaluation. During evolution, standard variation produces offspring, the same repair adjusts them, and evaluation and selection form the next generation.

Repair has three priorities. First, a bounded common offset shifts station CLR values to satisfy the load-weighted aggregate band. Second, station-level repair increases storage power where residual reverse injection exceeds the transformer reverse-loading limit. Third, when the upstream constraint is enabled, storage is allocated in descending order of residual reverse injection, until the upstream limit is met or adjustable storage ratings reach their bounds.

Any remaining infeasibility is handled by constraint domination. Standard variation, non-dominated ranking, and environmental selection are retained. These engineering rules direct candidate construction toward feasibility while the evolutionary search explores the cost and adequacy trade-off.