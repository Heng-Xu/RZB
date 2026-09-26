"""全寿命成本扫描；推荐记录实际设备容载比，不把上限档称作推荐值。"""

import argparse
from collections import defaultdict
from pathlib import Path

from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .joint_lifecycle_optimizer import cost_factors, run_model


CAPS = (2.0, 2.1, 2.2, 2.3, 2.31834, 2.4, 2.5, 3.0, 4.0)


def scan(factors: dict | None = None, reverse_variant: str = "night_central") -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    factors = factors or cost_factors()
    station_rows, year_rows, tie_rows, scan_rows = [], [], [], []
    for cap in CAPS:
        caps = {("QX-00005", 35): cap, ("QX-00005", 110): cap,
                ("QX-00007", 110): min(cap, 3.0)}
        stations, years, ties, summaries = run_model(reverse_variant, caps, factors, rigid=False)
        # 市区 3.0 为当前研究搜索域终点，不重复打印 4.0 档。
        for layer in summaries:
            if layer["study_region_id"] == "QX-00007" and cap > 3.0:
                continue
            scan_rows.append(layer)
            station_rows.extend(r for r in stations if r["study_region_id"] == layer["study_region_id"]
                                and r["voltage_kv"] == layer["voltage_kv"])
            year_rows.extend(r for r in years if r["study_region_id"] == layer["study_region_id"]
                             and r["voltage_kv"] == layer["voltage_kv"])
        tie_rows.extend(ties)
    return station_rows, year_rows, tie_rows, scan_rows


def recommend(scan_rows: list[dict], year_rows: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for row in scan_rows:
        groups[row["study_region_id"], row["voltage_kv"]].append(row)
    output = []
    for layer, rows in sorted(groups.items()):
        min_cost = min(r["objective_npv_10k_cny"] for r in rows)
        tied = [r for r in rows if abs(r["objective_npv_10k_cny"] - min_cost) <= 1e-5]
        # 只用最小可实现成本档展示一条设备路径；等成本扫描范围另列。
        chosen = min(tied, key=lambda r: r["clr_cap"])
        for row in year_rows:
            if (row["study_region_id"], row["voltage_kv"], row["clr_cap"]) != (*layer, chosen["clr_cap"]):
                continue
            output.append({
                "study_region_id": layer[0], "voltage_kv": layer[1], "year": row["year"],
                "least_cost_scan_cap": chosen["clr_cap"],
                "same_cost_scan_cap_max": max(r["clr_cap"] for r in tied),
                "recommended_actual_clr_under_selected_path": row["actual_clr"],
                "selected_capacity_mva": row["selected_capacity_mva"],
                "synchronous_forward_peak_mw": row["synchronous_forward_peak_mw"],
                "storage_modules_in_service": row["storage_modules_in_service"],
                "minimum_lifecycle_npv_10k_cny": min_cost,
                "sample_scope": "Pizhou_or_city_sample_only;voltage_separate",
                "recommendation_status": "conditional_simulation_case_not_universal_standard",
            })
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="弹性上限扫描及分电压条件推荐")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    stations, years, ties, scanned = scan()
    recommended = recommend(scanned, years)
    write_csv(scanned, args.output_dir / "joint_lifecycle_elastic_cap_scan.csv")
    write_csv(recommended, args.output_dir / "joint_lifecycle_conditional_recommendations.csv")
    write_csv(stations, args.output_dir / "joint_lifecycle_elastic_scan_stations.csv")
    write_csv(years, args.output_dir / "joint_lifecycle_elastic_scan_years.csv")
    print(f"扫描 {len(scanned)} 个片区×电压×档位；生成 {len(recommended)} 条逐年条件推荐。")
    for row in recommended:
        print(row)


if __name__ == "__main__":
    main()
