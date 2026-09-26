"""以 2025 实测站级反送检验 2021 仿真容量若保持不变时的风险。"""

import argparse
from collections import defaultdict
from pathlib import Path

from .baseline_2021 import POWER_FACTOR, STATION_INPUTS, build_baseline, read_csv, read_selected_baseline
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR


BETA_UPPER_SCREEN = 0.8


def build_reverse_screen(station_source: Path = STATION_INPUTS) -> tuple[list[dict], list[dict]]:
    baseline_stations = (read_selected_baseline() if station_source == STATION_INPUTS
                         else build_baseline(station_source=station_source)[0])
    baselines = {
        (row["study_region_id"], row["voltage_kv"], row["model_station_id"]): row
        for row in baseline_stations
    }
    stations = []
    grouped = defaultdict(list)
    for source in read_csv(station_source):
        key = source["study_region_id"], int(source["voltage_kv"]), source["model_station_id"]
        capacity = baselines[key]["simulation_capacity_mva_2021"]
        reverse_peak = float(source["reverse_peak_mw"])
        reverse_limit = BETA_UPPER_SCREEN * POWER_FACTOR * capacity
        shortfall = max(0.0, reverse_peak - reverse_limit)
        row = {
            "study_region_id": key[0],
            "voltage_kv": key[1],
            "model_station_id": key[2],
            "stress_year": 2025,
            "capacity_case": "2021_simulation_candidate_held_unchanged_to_2025",
            "candidate_capacity_mva": capacity,
            "observed_station_reverse_peak_mw": reverse_peak,
            "reverse_peak_scope": "station_independent_2025_net_export_peak",
            "power_factor_assumption": POWER_FACTOR,
            "beta_assumed_upper_screen": BETA_UPPER_SCREEN,
            "screening_reverse_limit_mw": round(reverse_limit, 6),
            "screening_shortfall_mw": round(shortfall, 6),
            "screen_status": "exceeds_even_at_beta_0_8" if shortfall > 1e-9 else "not_exceeded_at_beta_0_8_not_certified",
            "guide_sd_status": "not_computed_missing_same_time_gross_load_dg_output_and_operation_mode",
        }
        stations.append(row)
        grouped[key[:2]].append(row)
    layers = []
    for key, rows in sorted(grouped.items()):
        failed = [row for row in rows if row["screen_status"] == "exceeds_even_at_beta_0_8"]
        layers.append(
            {
                "study_region_id": key[0],
                "voltage_kv": key[1],
                "stress_year": 2025,
                "station_count": len(rows),
                "reverse_station_count": sum(row["observed_station_reverse_peak_mw"] > 0 for row in rows),
                "exceeds_even_at_beta_0_8_count": len(failed),
                "sum_independent_shortfalls_mw_not_synchronous": round(sum(row["screening_shortfall_mw"] for row in failed), 6),
                "capacity_case": "2021_simulation_candidate_held_unchanged_to_2025",
                "guide_sd_status": "not_computed_missing_same_time_gross_load_dg_output_and_operation_mode",
            }
        )
    return stations, layers


def main() -> None:
    parser = argparse.ArgumentParser(description="核对 2025 站级反送对未增容起点的压力")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    stations, layers = build_reverse_screen()
    write_csv(stations, args.output_dir / "reverse_station_screen_2025.csv")
    write_csv(layers, args.output_dir / "reverse_layer_screen_2025.csv")
    for row in layers:
        print(f"{row['study_region_id']} {row['voltage_kv']} kV：{row['reverse_station_count']} 站有反送，{row['exceeds_even_at_beta_0_8_count']} 站超出 0.8 初筛上界")


if __name__ == "__main__":
    main()
