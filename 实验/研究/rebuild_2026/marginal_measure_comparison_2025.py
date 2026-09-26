"""同一 2024 主变路径起点下，对照 2025 年主变或储能单措施投资。"""

import argparse
from collections import defaultdict
from pathlib import Path

from .baseline_2021 import read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR


STORAGE_SCREEN = OUTPUT_DIR / "static_storage_need_screen_2025.csv"
TRANSFORMER_CAPEX = OUTPUT_DIR / "transformer_only_capex_layer_2022_2025.csv"


def build_marginal_measure_comparison(
    storage_source: Path = STORAGE_SCREEN,
    transformer_source: Path = TRANSFORMER_CAPEX,
) -> list[dict]:
    storage_by_layer = defaultdict(list)
    for row in read_csv(storage_source):
        if row["capacity_case"] == "hold_2024_transformer_path_capacity":
            storage_by_layer[row["study_region_id"], int(row["voltage_kv"])].append(row)
    transformer = {
        (row["study_region_id"], int(row["voltage_kv"])): row
        for row in read_csv(transformer_source)
        if int(row["year"]) == 2025 and row["reverse_variant"] == "night_central"
    }
    result = []
    for key, storage_rows in sorted(storage_by_layer.items()):
        upgrade = transformer[key]
        storage_cost = sum(float(row["replicated_package_capex_10k_cny"]) for row in storage_rows)
        upgrade_cost = float(upgrade["base_capex_10k_cny"])
        result.append({
            "study_region_id": key[0],
            "voltage_kv": key[1],
            "year": 2025,
            "prior_path_year": 2024,
            "station_count": len(storage_rows),
            "storage_only_need_station_count": sum(int(row["required_modules_scenario_proxy"]) > 0 for row in storage_rows),
            "storage_only_modules_sum": sum(int(row["required_modules_scenario_proxy"]) for row in storage_rows),
            "storage_only_stations_above_ten_module_quote": sum(int(row["required_modules_scenario_proxy"]) > 10 for row in storage_rows),
            "storage_only_simulated_capex_10k_cny": round(storage_cost, 6),
            "transformer_only_replaced_unit_count": int(upgrade["upgraded_transformer_count"]),
            "transformer_only_purchased_mva": float(upgrade["purchased_transformer_mva"]),
            "transformer_only_simulated_capex_10k_cny": upgrade_cost,
            "storage_minus_transformer_capex_10k_cny": round(storage_cost - upgrade_cost, 6),
            "investment_scope": "2025_incremental_investment_only_from_same_2024_transformer_path",
            "technical_scope": "independent_station_peak_proxy_not_joint_operation_or_guide_feasibility",
            "cost_scope": "storage_above_ten_package_rule_unverified_no_lifecycle_cost",
            "conclusion_scope": "diagnostic_comparison_not_optimal_measure_or_recommended_clr",
        })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="并列输出 2025 年储能/主变单措施新增投资初筛")
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR / "marginal_measure_comparison_2025.csv")
    args = parser.parse_args()
    rows = build_marginal_measure_comparison()
    write_csv(rows, args.output)
    print(f"已输出 {len(rows)} 个片区—电压层的 2025 年单措施增量投资对照；不构成全寿命最优方案。")


if __name__ == "__main__":
    main()
