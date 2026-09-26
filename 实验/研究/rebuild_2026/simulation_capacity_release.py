"""仿真容量可退出情景：同一起点，逐年按需求重选站级容量。"""

from pathlib import Path

from .baseline_2021 import read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .joint_lifecycle_optimizer import (
    DESIGNED_NEW_LINE_KM, PIZHOU_110, cost_factors, load_inputs, solve_layer,
)


def run(output_dir: Path = OUTPUT_DIR / "capacity_release_simulation/final_policy_frontier_v3") -> list[dict]:
    output_dir = Path(output_dir)
    baseline = {
        (r["study_region_id"], int(r["voltage_kv"]), r["model_station_id"]): r
        for r in read_csv(OUTPUT_DIR / "planning_2021_common_baseline_stations.csv")
    }
    _, scenes, durations, peaks, catalog, coefficients = load_inputs()
    results = []
    infeasible = []
    budget_grid = {
        ("QX-00005", 35): (0.20, 0.30, 0.40, 0.50, 0.60),
        ("QX-00005", 110): (0.00, 0.01, 0.02, 0.03, 0.04, 0.05),
        ("QX-00007", 110): (0.00, 0.005, 0.01, 0.02),
    }
    for layer in sorted({s[:2] for s in baseline}):
        cases = [(f"rigid_budget_{round(b * 1000):03d}permille", 2.0, True, b)
                 for b in budget_grid[layer]] + [("elastic", 2.4, False, None)]
        for scenario, cap, ties, budget in cases:
            try:
                stations, years, transfers, summary = solve_layer(
                    layer, baseline, scenes, durations, peaks, catalog, coefficients,
                    cost_factors(), cap, scenario.startswith("rigid"),
                    include_new_line=ties and layer == PIZHOU_110,
                    new_line_variant="designed_bus", line_km=DESIGNED_NEW_LINE_KM,
                    tie_allowed=ties, policy_peak_basis="annual",
                    preserve_baseline_forward_margin=False,
                    preserve_prior_year_forward_margin=False,
                    capacity_growth_budget_fraction=budget,
                    max_storage_modules=50,
                    require_existing_tie_operation=False,
                    tie_year_basis="annual_station_scaled",
                    canonicalize_tie_dispatch=True,
                    allow_capacity_release=True,
                )
            except ValueError as exc:
                if "infeasible" not in str(exc).lower():
                    raise
                infeasible.append({"planning_scenario": scenario, "study_region_id": layer[0],
                                   "voltage_kv": layer[1], "capacity_growth_budget_fraction": budget,
                                   "status": "infeasible_under_stated_static_constraints",
                                   "solver_detail": str(exc)})
                continue
            if scenario.startswith("rigid") and any(float(y["actual_clr"]) > 2.0 + 1e-8 for y in years):
                raise ValueError(f"{layer} 刚性实际容载比超过 2.0")
            stem = f"{scenario}_{layer[0]}_{layer[1]}"
            for name, rows in (("stations", stations), ("years", years), ("ties", transfers)):
                if rows:
                    write_csv(rows, output_dir / f"{stem}_{name}.csv")
            summary["status"] = "conditional_three_unit_policy_simulation"
            summary["planning_scenario"] = scenario
            results.append(summary)
    write_csv(results, output_dir / "summary.csv")
    if infeasible:
        write_csv(infeasible, output_dir / "infeasible.csv")
    return results


if __name__ == "__main__":
    for row in run():
        print(row["study_region_id"], row["voltage_kv"], row["planning_scenario"],
              row["objective_npv_10k_cny"], row["max_actual_clr"])
