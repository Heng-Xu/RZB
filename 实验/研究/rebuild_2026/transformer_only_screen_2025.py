"""不采取转供或储能时，求 2025 年双主变的宽松离散容量筛查值。"""

import argparse
from collections import defaultdict
from pathlib import Path

from .annual_forward_scenes import build_annual_forward_scenes
from .baseline_2021 import (
    BASELINE_CLR_CAP,
    POWER_FACTOR,
    STATION_INPUTS,
    build_baseline,
    local_unit_catalog,
    read_csv,
    read_selected_baseline,
    select_two_units,
)
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .reverse_screen_2025 import BETA_UPPER_SCREEN


def build_transformer_only_screen(station_source: Path = STATION_INPUTS) -> tuple[list[dict], list[dict]]:
    baseline = (read_selected_baseline() if station_source == STATION_INPUTS
                else build_baseline(station_source=station_source)[0])
    baseline_by_station = {
        (row["study_region_id"], row["voltage_kv"], row["model_station_id"]): row
        for row in baseline
    }
    _, forward_layers = build_annual_forward_scenes()
    peaks = {
        (row["study_region_id"], row["voltage_kv"]): row["estimated_synchronous_forward_peak_mw"]
        for row in forward_layers if row["year"] == 2025
    }
    catalogs = local_unit_catalog()
    stations = []
    grouped = defaultdict(list)
    for source in read_csv(station_source):
        key = source["study_region_id"], int(source["voltage_kv"])
        station_key = key + (source["model_station_id"],)
        capacity_2021 = baseline_by_station[station_key]["simulation_capacity_mva_2021"]
        forward = float(source["forward_peak_mw"])
        reverse = max(0.0, float(source["reverse_peak_mw"]))
        positive_required = forward / POWER_FACTOR
        reverse_required = reverse / (POWER_FACTOR * BETA_UPPER_SCREEN)
        pair = select_two_units(max(capacity_2021, positive_required, reverse_required), catalogs[key])
        capacity = sum(pair)
        row = {
            "study_region_id": key[0],
            "voltage_kv": key[1],
            "year": 2025,
            "model_station_id": source["model_station_id"],
            "baseline_capacity_mva_2021": capacity_2021,
            "observed_station_forward_peak_mw_2025": forward,
            "observed_station_reverse_peak_mw_2025": reverse,
            "forward_minimum_mva_continuous": round(positive_required, 6),
            "reverse_minimum_mva_continuous_at_beta_0_8": round(reverse_required, 6),
            "screening_beta_upper": BETA_UPPER_SCREEN,
            "power_factor_assumption": POWER_FACTOR,
            "selected_unit_1_mva": pair[0],
            "selected_unit_2_mva": pair[1],
            "transformer_only_screen_capacity_mva": capacity,
            "capacity_increment_from_2021_mva": round(capacity - capacity_2021, 6),
            "technical_status": "transformer_only_aggregate_screen_not_guide_feasibility",
        }
        stations.append(row)
        grouped[key].append(row)
    layers = []
    for key, rows in sorted(grouped.items()):
        capacity = sum(row["transformer_only_screen_capacity_mva"] for row in rows)
        peak = peaks[key]
        ratio = capacity / peak
        layers.append(
            {
                "study_region_id": key[0],
                "voltage_kv": key[1],
                "year": 2025,
                "station_count": len(rows),
                "observed_synchronous_forward_peak_mw_2025": peak,
                "transformer_only_screen_capacity_mva": capacity,
                "capacity_increment_from_2021_mva": round(sum(row["capacity_increment_from_2021_mva"] for row in rows), 6),
                "transformer_only_clr": round(ratio, 9),
                "clr_cap": BASELINE_CLR_CAP,
                "ratio_screen_status": "within_cap" if ratio <= BASELINE_CLR_CAP + 1e-9 else "exceeds_cap",
                "technical_status": "transformer_only_aggregate_screen_not_guide_feasibility",
            }
        )
    return stations, layers


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 2025 年不采取转供或储能的双主变容量初筛")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    stations, layers = build_transformer_only_screen()
    write_csv(stations, args.output_dir / "transformer_only_station_screen_2025.csv")
    write_csv(layers, args.output_dir / "transformer_only_layer_screen_2025.csv")
    for row in layers:
        print(f"{row['study_region_id']} {row['voltage_kv']} kV：筛查容量 {row['transformer_only_screen_capacity_mva']} MVA，R={row['transformer_only_clr']:.3f}，{row['ratio_screen_status']}")


if __name__ == "__main__":
    main()
