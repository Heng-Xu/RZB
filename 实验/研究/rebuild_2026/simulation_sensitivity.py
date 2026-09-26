"""可减容仿真的价格与措施范围敏感性；仅生成条件案例。"""

from pathlib import Path

from .baseline_2021 import read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .joint_lifecycle_optimizer import cost_factors, load_inputs, solve_layer


def run(output_dir: Path = OUTPUT_DIR / "capacity_release_simulation/final_policy_frontier_v3") -> list[dict]:
    baseline = {
        (r["study_region_id"], int(r["voltage_kv"]), r["model_station_id"]): r
        for r in read_csv(OUTPUT_DIR / "planning_2021_common_baseline_stations.csv")
    }
    _, scenes, durations, peaks, catalog, coefficients = load_inputs()
    cases = [
        ("pizhou_35_base", ("QX-00005", 35), 1.0, 1.0, False, 0.30),
        ("pizhou_35_transformer_half", ("QX-00005", 35), 0.5, 1.0, False, 0.30),
        ("pizhou_35_storage_double", ("QX-00005", 35), 1.0, 2.0, False, 0.30),
        ("pizhou_110_no_tie", ("QX-00005", 110), 1.0, 1.0, False, 0.05),
        ("pizhou_110_existing_tie", ("QX-00005", 110), 1.0, 1.0, True, 0.05),
        ("city_110_base", ("QX-00007", 110), 1.0, 1.0, False, 0.01),
    ]
    rows = []
    for case_id, layer, transformer_scale, storage_scale, tie_allowed, budget in cases:
        for scheme, cap in (("rigid", 2.0), ("elastic", 2.4)):
            _, years, _, summary = solve_layer(
                layer, baseline, scenes, durations, peaks, catalog, coefficients,
                cost_factors(), cap, scheme == "rigid", tie_allowed=tie_allowed,
                transformer_cost_scale=transformer_scale, storage_cost_scale=storage_scale,
                policy_peak_basis="annual", max_storage_modules=50,
                allow_capacity_release=True,
                capacity_growth_budget_fraction=budget if scheme == "rigid" else None,
                require_existing_tie_operation=False,
                canonicalize_tie_dispatch=True,
            )
            rows.append({"case_id": case_id, "study_region_id": layer[0],
                         "voltage_kv": layer[1], "scheme": scheme,
                         "transformer_cost_scale": transformer_scale,
                         "storage_cost_scale": storage_scale,
                         "tie_allowed": tie_allowed,
                         "gross_expansion_budget_fraction": budget if scheme == "rigid" else "",
                         "cost_npv_10k_cny": summary["objective_npv_10k_cny"],
                         "max_actual_clr": summary["max_actual_clr"],
                         "2023_actual_clr": next(r["actual_clr"] for r in years if r["year"] == 2023),
                         "2025_capacity_mva": years[-1]["selected_capacity_mva"],
                         "2025_storage_modules": years[-1]["storage_modules_in_service"],
                         "status": "paired_policy_sensitivity_with_same_tie_scope"})
    write_csv(rows, Path(output_dir) / "sensitivity.csv")
    return rows


if __name__ == "__main__":
    for row in run():
        print(row["case_id"], row["scheme"], row["cost_npv_10k_cny"], row["max_actual_clr"])
