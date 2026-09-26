"""刚性方案中既有联络受限后的新线与储能替代前沿。"""

from pathlib import Path

from .baseline_2021 import read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .joint_lifecycle_optimizer import (
    DESIGNED_NEW_LINE_ID, DESIGNED_NEW_LINE_KM, PIZHOU_110,
    cost_factors, load_inputs, solve_layer,
)


def run(output_dir: Path = OUTPUT_DIR / "capacity_release_simulation/final_policy_frontier_v3") -> list[dict]:
    baseline = {
        (r["study_region_id"], int(r["voltage_kv"]), r["model_station_id"]): r
        for r in read_csv(OUTPUT_DIR / "planning_2021_common_baseline_stations.csv")
    }
    _, scenes, durations, peaks, catalog, coefficients = load_inputs()
    rows = []
    for transfer_fraction in (1.0, 0.9, 0.8):
        _, years, transfers, summary = solve_layer(
            PIZHOU_110, baseline, scenes, durations, peaks, catalog, coefficients,
            cost_factors(), 2.0, True,
            include_new_line=True, new_line_variant="designed_bus",
            line_km=DESIGNED_NEW_LINE_KM, tie_allowed=True,
            tie_transfer_limit_scale=transfer_fraction,
            policy_peak_basis="annual", capacity_growth_budget_fraction=0.05,
            max_storage_modules=50, require_existing_tie_operation=False,
            tie_year_basis="annual_station_scaled",
            canonicalize_tie_dispatch=True, allow_capacity_release=True,
        )
        rows.append({
            "existing_and_new_path_limit_fraction": transfer_fraction,
            "cost_npv_10k_cny": summary["objective_npv_10k_cny"],
            "max_planning_clr": summary["max_actual_clr"],
            "new_line_built_2025": years[-1]["line_built"],
            "new_line_length_km_assumed": DESIGNED_NEW_LINE_KM,
            "storage_modules_2025": years[-1]["storage_modules_in_service"],
            "existing_tie_forward_mw_2025": round(sum(
                float(r["transfer_mw"]) for r in transfers
                if r["year"] == 2025 and r["scenario"] == "forward" and r["tie_id"] != DESIGNED_NEW_LINE_ID
            ), 6),
            "new_line_forward_mw_2025": round(sum(
                float(r["transfer_mw"]) for r in transfers
                if r["year"] == 2025 and r["scenario"] == "forward" and r["tie_id"] == DESIGNED_NEW_LINE_ID
            ), 6),
            "status": "conditional_static_simulation_new_line_not_engineering_design",
        })
    write_csv(rows, Path(output_dir) / "line_sensitivity.csv")
    return rows


if __name__ == "__main__":
    for row in run():
        print(row)
