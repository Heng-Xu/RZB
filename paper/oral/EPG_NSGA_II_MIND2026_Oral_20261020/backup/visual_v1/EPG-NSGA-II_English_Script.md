# EPG-NSGA-II — English oral presentation script

Five slides · 578 spoken words · approximately 4–5 minutes.

The spoken text below matches the PowerPoint speaker notes.

## Slide 1: Cover

Hello everyone. Today I will present Engineering-Prior-Guided NSGA-II, or EPG-NSGA-II, for differentiated capacity-load ratio optimization in county-level 110-kilovolt grids with high distributed photovoltaic penetration. This work jointly plans transformer capacity and storage power. I will briefly explain the planning problem, our algorithm, and the main experimental results.

---

## Slide 2: Background and problem

High distributed PV penetration changes power flow. Electricity normally moves from the upstream grid toward local demand, but midday PV generation can create reverse flow through a substation. The planning challenge is that substations differ in PV penetration and transfer capability, while a fixed capacity-load ratio cap of two treats these differences uniformly.

We therefore optimize two quantities at each station: its capacity-load ratio, or CLR, and its storage power rating in megawatts. CLR is dimensionless and means planned transformer capacity divided by forecast peak load. The paper uses a five-year forecast with five percent annual growth.

The objectives are annualized cost, in million yuan per year, and expected energy not supplied, or EENS, in megawatt-hours per year. EENS measures supply inadequacy under N-minus-one contingencies. Feasibility is defined by station reverse-flow limits, an aggregate CLR band from one point eight to three, and an upstream reverse-flow limit when enabled.

---

## Slide 3: Proposed solution

Our solution adds engineering-prior seeding and feasibility repair to standard NSGA-II. The key change is how candidate plans are constructed and adjusted.

For the initial population, we sample station CLR values, start storage power at zero, and apply repair before evaluation. During evolution, standard variation produces offspring, the same repair adjusts them, and evaluation and selection form the next generation.

Repair has three priorities. First, a bounded common offset shifts station CLR values to satisfy the load-weighted aggregate band. Second, station-level repair increases storage power where residual reverse injection exceeds the transformer reverse-loading limit. Third, when the upstream constraint is enabled, storage is allocated in descending order of residual reverse injection, until the upstream limit is met or adjustable storage ratings reach their bounds.

Any remaining infeasibility is handled by constraint domination. Standard variation, non-dominated ranking, and environmental selection are retained. These engineering rules direct candidate construction toward feasibility while the evolutionary search explores the cost and adequacy trade-off.

---

## Slide 4: Results

The experiments use a public-data benchmark, with loads scaled from the IEEE thirty-three-bus system and PV profiles derived from PVGIS. Population size is one hundred, and results are averaged over three independent runs.

On the left, for forty substations, EPG-NSGA-II achieves four point eight percent higher mean final hypervolume than standard NSGA-II. Hypervolume is normalized to the standard baseline at termination using a common reference point. The baselines run for eight hundred generations, while EPG-NSGA-II and its ablations run for four hundred. Repair-only nearly matches the full method, while seeding-only remains close to the baseline. Repair is therefore the main contributor to the final gain. The paper also reports that the mean EPG curve reaches the standard baseline's final hypervolume by generation eighty-four.

On the right, the twenty-substation design comparison reduces annualized cost from two hundred thirty-six point four zero to two hundred twenty-eight point four three million yuan per year, a reduction of three point four percent. Modeled EENS falls from five hundred sixty-one to zero megawatt-hours per year relative to the two-point-zero-capped design.

These results apply to the current model. Storage energy and state-of-charge limits, together with real-grid calibration, remain future work.

---

## Slide 5: Thank you

The main takeaway is that engineering-prior seeding and repair support more effective constrained search and differentiated CLR and storage planning. Thank you for your attention. I welcome your questions.
