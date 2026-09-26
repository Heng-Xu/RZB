"""从已证明可行的完整路径中整理条件推荐值与跨情景范围。"""

from collections import defaultdict
from pathlib import Path

from .baseline_2021 import read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR


def build_recommendations(matrix_path: Path | None = None) -> tuple[list[dict], list[dict]]:
    matrix = read_csv(matrix_path or OUTPUT_DIR / "planning_conditional_matrix.csv")
    by_case = defaultdict(list)
    for row in matrix:
        by_case[(row["scenario_id"], row["study_region_id"], row["voltage_kv"], row["year"])].append(row)
    conditional = []
    for case, rows in sorted(by_case.items()):
        choice = rows[0]["preferred_scheme_by_full_path_cost"]
        selected = rows if choice == "cost_tie" else [r for r in rows if r["scheme"] == choice.replace("_only_feasible", "")]
        if not selected:
            raise ValueError(f"{case} 没有与推荐选择相符的方案")
        template = selected[0]
        ratio_values = [float(r["simulated_clr"]) for r in selected]
        conditional.append({
            "scenario_id": case[0], "study_region_id": case[1],
            "voltage_kv": case[2], "year": case[3],
            "preferred_scheme": choice,
            "source_load_ratio_2025_region_shared_proxy": template["source_load_ratio_2025_region_shared_proxy"],
            "net_peak_mw": template["net_peak_mw"],
            "net_peak_cagr_from_2021_fraction": template["net_peak_cagr_from_2021_fraction"],
            "normalized_transformer_to_storage_price_scale": template["normalized_transformer_to_storage_price_scale"],
            "tie_transfer_limit_scale": template["tie_transfer_limit_scale"],
            "forward_h95_scenario_hours": template["forward_h95_scenario_hours"],
            "recommended_simulated_clr_min": round(min(ratio_values), 9),
            "recommended_simulated_clr_max": round(max(ratio_values), 9),
            "selected_capacity_mva": "/".join(str(r["simulated_capacity_mva"]) for r in selected),
            "selected_storage_modules": "/".join(str(r["storage_modules_in_service"]) for r in selected),
            "selected_forward_tie_mw": "/".join(str(r["forward_tie_transfer_mw"]) for r in selected),
            "selected_new_line_built": "/".join(str(r.get("new_line_built", "0")) for r in selected),
            "policy_control_clr": "/".join(str(r.get("policy_control_clr", "")) for r in selected),
            "source_case_count": 1,
            "status": "conditional_model_recommendation_not_empirical_generalization",
        })
    by_layer_year = defaultdict(list)
    for row in conditional:
        by_layer_year[(row["study_region_id"], row["voltage_kv"], row["year"])].append(row)
    ranges = []
    for (region, voltage, year), rows in sorted(by_layer_year.items()):
        ranges.append({
            "study_region_id": region, "voltage_kv": voltage, "year": year,
            "scenario_count": len(rows),
            "preferred_rigid_count": sum(r["preferred_scheme"] == "rigid" for r in rows),
            "preferred_elastic_count": sum(r["preferred_scheme"] in ("elastic", "elastic_only_feasible") for r in rows),
            "cost_tie_count": sum(r["preferred_scheme"] == "cost_tie" for r in rows),
            "rigid_infeasible_count": sum(r["preferred_scheme"] == "elastic_only_feasible" for r in rows),
            "conditional_clr_range_min": min(float(r["recommended_simulated_clr_min"]) for r in rows),
            "conditional_clr_range_max": max(float(r["recommended_simulated_clr_max"]) for r in rows),
            "range_interpretation": "envelope_of_selected_discrete_simulation_paths_not_statistical_confidence_interval",
        })
    return conditional, ranges


def main() -> None:
    conditional, ranges = build_recommendations()
    write_csv(conditional, OUTPUT_DIR / "planning_conditional_recommendation_matrix.csv")
    write_csv(ranges, OUTPUT_DIR / "planning_conditional_recommendation_ranges.csv")
    print(f"已写入 {len(conditional)} 条条件推荐和 {len(ranges)} 条年度范围")


if __name__ == "__main__":
    main()
