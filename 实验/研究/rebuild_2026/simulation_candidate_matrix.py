"""从可减容预算前沿构造三单元逐年条件方案表。"""

from pathlib import Path

from .baseline_2021 import read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR


def build(output_dir: Path = OUTPUT_DIR / "capacity_release_simulation/final_policy_frontier_v3") -> list[dict]:
    output_dir = Path(output_dir)
    summaries = read_csv(output_dir / "summary.csv")
    by_layer = {}
    for row in summaries:
        layer = row["study_region_id"], int(row["voltage_kv"])
        by_layer.setdefault(layer, []).append(row)
    result = []
    for layer, rows in sorted(by_layer.items()):
        rigid = min((r for r in rows if r["planning_scenario"].startswith("rigid")),
                    key=lambda r: float(r["capacity_growth_budget_fraction"]))
        elastic = next(r for r in rows if r["planning_scenario"] == "elastic")
        selected = min((rigid, elastic), key=lambda r: float(r["objective_npv_10k_cny"]))
        scenario = selected["planning_scenario"]
        stem = f"{scenario}_{layer[0]}_{layer[1]}"
        annual = read_csv(output_dir / f"{stem}_years.csv")
        rigid_annual = {int(r["year"]): r for r in read_csv(
            output_dir / f"{rigid['planning_scenario']}_{layer[0]}_{layer[1]}_years.csv")}
        elastic_annual = {int(r["year"]): r for r in read_csv(
            output_dir / f"elastic_{layer[0]}_{layer[1]}_years.csv")}
        ties_path = output_dir / f"{stem}_ties.csv"
        ties = read_csv(ties_path) if ties_path.exists() else []
        for year in annual:
            rigid_year = rigid_annual[int(year["year"])]
            elastic_year = elastic_annual[int(year["year"])]
            transfer = sum(float(t["transfer_mw"]) for t in ties
                           if int(t["year"]) == int(year["year"]) and t["scenario"] == "forward")
            result.append({"study_region_id": layer[0], "voltage_kv": layer[1],
                           "year": year["year"], "reference_rigid_budget_fraction":
                           rigid["capacity_growth_budget_fraction"],
                           "selected_scheme": "rigid" if scenario.startswith("rigid") else "elastic",
                           "selected_scenario": scenario,
                           "rigid_path_cost_npv_10k_cny": rigid["objective_npv_10k_cny"],
                           "elastic_path_cost_npv_10k_cny": elastic["objective_npv_10k_cny"],
                           "selected_path_cost_npv_10k_cny": selected["objective_npv_10k_cny"],
                           "reference_peak_basis": ("official_reported_downward_load"
                                                    if layer[0] == "QX-00005" else
                                                    "29_station_sample_scaled_by_official_growth"),
                           "year_net_peak_mw": year["synchronous_forward_peak_mw"],
                           "rigid_year_capacity_mva": rigid_year["selected_capacity_mva"],
                           "rigid_year_clr": rigid_year["actual_clr"],
                           "rigid_storage_modules": rigid_year["storage_modules_in_service"],
                           "elastic_year_capacity_mva": elastic_year["selected_capacity_mva"],
                           "elastic_year_clr": elastic_year["actual_clr"],
                           "elastic_storage_modules": elastic_year["storage_modules_in_service"],
                           "year_capacity_mva": year["selected_capacity_mva"],
                           "year_planning_reference_clr": year["actual_clr"],
                           "storage_modules_in_service": year["storage_modules_in_service"],
                           "forward_tie_transfer_mw": round(transfer, 6),
                           "new_line_built": year["line_built"],
                           "status": "conditional_three_unit_recommendation_simulation"})
    write_csv(result, output_dir / "candidate_annual_matrix.csv")
    return result


if __name__ == "__main__":
    print(f"生成 {len(build())} 条逐年条件方案")
