"""由已求解设备路径形成分电压条件矩阵；历史 H95 留空。"""

import argparse
from collections import defaultdict
from pathlib import Path

from .baseline_2021 import read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .incremental_cost import replacement_cost_coefficients, storage_capex_10k_cny


def build_matrices(source: Path = OUTPUT_DIR) -> dict[int, list[dict]]:
    recommended = read_csv(source / "joint_lifecycle_conditional_recommendations.csv")
    rigid = {(r["study_region_id"], int(r["voltage_kv"]), int(r["year"])): r
             for r in read_csv(source / "joint_lifecycle_rigid_years.csv")}
    annual = {(r["study_region_id"], int(r["voltage_kv"]), int(r["year"])): r
              for r in read_csv(source / "annual_forward_layer_scenes_2021_2025.csv")}
    pressure = {r["region_id"]: r for r in read_csv(source / "source_load_scan_ceiling_research.csv")}
    station_reverse = defaultdict(list)
    for row in read_csv(source / "annual_reverse_station_proxy_2021_2025.csv"):
        if row["variant"] == "night_central":
            station_reverse[row["study_region_id"], int(row["voltage_kv"]), int(row["year"])].append(
                float(row["reverse_at_template_proxy_mw"]))
    coefficients = {row["voltage_kv"]: row["base_coefficient_10k_cny_per_purchased_mva"]
                    for row in replacement_cost_coefficients()}
    storage_per_mw = storage_capex_10k_cny(10)  # 10 × 0.1 MW; capital cost only.
    pizhou_h95 = {int(r["voltage_kv"]): r for r in read_csv(source / "pizhou_2025_scenarios_evidence.csv")}
    out = {35: [], 110: []}
    for r in recommended:
        region, voltage, year = r["study_region_id"], int(r["voltage_kv"]), int(r["year"])
        base = rigid[region, voltage, year]
        prior_peak = float(annual[region, voltage, year - 1]["estimated_synchronous_forward_peak_mw"])
        peak = float(r["synchronous_forward_peak_mw"])
        initial_peak = float(annual[region, voltage, 2021]["estimated_synchronous_forward_peak_mw"])
        if region == "QX-00005":
            h95 = pizhou_h95[voltage]
            forward_h95, reverse_h95 = h95["forward_h95_observed"], h95["reverse_h95_observed"]
            h95_scope = "2025_observed_Pizhou_layer_template"
        else:
            # 29 站市区样本聚合，逐时表的观测峰值 95% 小时数单独核算。
            hourly = read_csv(source / "city_2025_aggregate_hourly.csv")
            values = [float(v["observed_mw"]) for v in hourly if v["observed_mw"]]
            observed_peak = max(values)
            forward_h95 = sum(value >= 0.95 * observed_peak for value in values)
            reverse_h95 = 0 if min(values) >= 0 else ""
            h95_scope = "2025_observed_city_29_station_sample_template"
        rigid_cost = float(next(x["objective_npv_10k_cny"] for x in read_csv(source / "joint_lifecycle_rigid_layers.csv")
                                if x["study_region_id"] == region and int(x["voltage_kv"]) == voltage))
        elastic_cost = float(r["minimum_lifecycle_npv_10k_cny"])
        out[voltage].append({
            "study_region_id": region, "voltage_kv": voltage, "year": year,
            "annual_net_peak_growth_vs_previous": round(peak / prior_peak - 1, 6),
            "net_peak_cagr_from_2021": round((peak / initial_peak) ** (1 / (year - 2021)) - 1, 6),
            "annual_synchronous_forward_net_peak_mw": round(peak, 6),
            "largest_station_reverse_proxy_mw": round(max(station_reverse[region, voltage, year]), 6),
            "reverse_extreme_scope": "station_extreme_at_individual_template_time_not_synchronous_layer_extreme",
            "source_to_gross_load_ratio_2025_regional_proxy": pressure[region]["pv_to_gross_load_ratio_proxy"],
            "source_load_ratio_scope": "2025_regional_proxy_not_voltage_specific_or_historical_observation",
            "forward_h95_hours_2025_template": forward_h95,
            "reverse_h95_hours_2025_template": reverse_h95,
            "h95_scope": h95_scope,
            "rigid_actual_clr": base["actual_clr"],
            "elastic_actual_clr": r["recommended_actual_clr_under_selected_path"],
            "elastic_least_cost_scan_cap": r["least_cost_scan_cap"],
            "rigid_lifecycle_npv_10k_cny": round(rigid_cost, 6),
            "elastic_lifecycle_npv_10k_cny": round(elastic_cost, 6),
            "elastic_cost_to_rigid_cost": round(elastic_cost / rigid_cost, 6),
            "storage_to_transformer_unit_capex_ratio": round(
                storage_per_mw / (float(coefficients[voltage]) / 0.95), 6),
            "unit_cost_ratio_scope": "exogenous_10_cabinet_1MW_capex_vs_purchased_transformer_1MW_active_capacity;not_lifecycle_or_tie_cost",
            "optimized_cost_ratio_role": "comparison_outcome_not_recommendation_predictor",
            "measure_scope_note": "Pizhou_110_rigid_has_ties_elastic_has_no_ties" if region == "QX-00005" and voltage == 110 else "same_measure_boundary",
            "recommendation_scope": "conditional_case_only_not_universal_threshold",
        })
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 35 kV 与 110 kV 两张独立条件推荐矩阵")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    matrices = build_matrices(args.output_dir)
    for voltage, rows in matrices.items():
        write_csv(rows, args.output_dir / f"joint_lifecycle_conditional_matrix_{voltage}kv.csv")
        print(f"{voltage} kV: {len(rows)} 条片区×年条件记录")


if __name__ == "__main__":
    main()
