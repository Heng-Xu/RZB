"""检查无转供、无储能的双主变逐年容量路径与 R≤2.0 是否相容。"""

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


REVERSE_PROXY = OUTPUT_DIR / "annual_reverse_station_proxy_2021_2025.csv"
VARIANTS = ("night_central", "early_pv_high")


def build_transformer_only_path(
    reverse_source: Path = REVERSE_PROXY,
    station_source: Path = STATION_INPUTS,
) -> tuple[list[dict], list[dict]]:
    reverse = {
        (row["study_region_id"], int(row["voltage_kv"]), row["model_station_id"], int(row["year"]), row["variant"]): row
        for row in read_csv(reverse_source)
        if row["variant"] in VARIANTS
    }
    _, forward_layers = build_annual_forward_scenes()
    forward = {
        (row["study_region_id"], row["voltage_kv"], row["year"]): row
        for row in forward_layers
    }
    baseline = (read_selected_baseline() if station_source == STATION_INPUTS
                else build_baseline(station_source=station_source)[0])
    starting_pairs = {
        (row["study_region_id"], row["voltage_kv"], row["model_station_id"]):
        (row["simulation_unit_1_mva"], row["simulation_unit_2_mva"])
        for row in baseline
    }
    catalog = local_unit_catalog()
    station_rows = []
    grouped = defaultdict(list)
    for variant in VARIANTS:
        for source in read_csv(station_source):
            region = source["study_region_id"]
            voltage = int(source["voltage_kv"])
            station_id = source["model_station_id"]
            key = region, voltage, station_id
            pair = starting_pairs[key]
            for year in range(2021, 2026):
                scale = forward[region, voltage, year]["annual_scale"]
                forward_peak = float(source["forward_peak_mw"]) * scale
                proxy_reverse = float(reverse[region, voltage, station_id, year, variant]["reverse_at_template_proxy_mw"])
                reverse_peak = max(proxy_reverse, float(source["reverse_peak_mw"])) if year == 2025 else proxy_reverse
                prior_pair = pair
                required = max(
                    forward_peak / POWER_FACTOR,
                    reverse_peak / (POWER_FACTOR * BETA_UPPER_SCREEN),
                    sum(prior_pair),
                )
                if sum(pair) + 1e-9 < required:
                    pair = select_two_units(required, catalog[region, voltage], minimum_pair=prior_pair)
                row = {
                    "study_region_id": region,
                    "voltage_kv": voltage,
                    "year": year,
                    "model_station_id": station_id,
                    "reverse_variant": variant,
                    "estimated_station_forward_peak_mw": round(forward_peak, 6),
                    "reverse_screen_mw": round(reverse_peak, 6),
                    "reverse_basis": "observed_2025_independent_station_peak" if year == 2025 else "historical_typical_window_proxy",
                    "prior_unit_1_mva": prior_pair[0],
                    "prior_unit_2_mva": prior_pair[1],
                    "selected_unit_1_mva": pair[0],
                    "selected_unit_2_mva": pair[1],
                    "selected_capacity_mva": sum(pair),
                    "capacity_increment_mva": round(sum(pair) - sum(prior_pair), 6),
                    "equipment_change_not_costed": "yes" if pair != prior_pair else "no",
                    "technical_status": "transformer_only_aggregate_screen_not_guide_feasibility",
                }
                station_rows.append(row)
                grouped[region, voltage, year, variant].append(row)
    layer_rows = []
    for (region, voltage, year, variant), rows in sorted(grouped.items()):
        capacity = sum(row["selected_capacity_mva"] for row in rows)
        peak = forward[region, voltage, year]["estimated_synchronous_forward_peak_mw"]
        ratio = capacity / peak
        layer_rows.append(
            {
                "study_region_id": region,
                "voltage_kv": voltage,
                "year": year,
                "reverse_variant": variant,
                "station_count": len(rows),
                "estimated_synchronous_forward_peak_mw": peak,
                "transformer_only_capacity_mva": capacity,
                "year_capacity_increment_mva": round(sum(row["capacity_increment_mva"] for row in rows), 6),
                "transformer_only_clr": round(ratio, 9),
                "clr_cap": BASELINE_CLR_CAP,
                "ratio_status": "within_cap" if ratio <= BASELINE_CLR_CAP + 1e-9 else "exceeds_cap",
                "technical_status": "transformer_only_aggregate_screen_not_guide_feasibility",
            }
        )
    return station_rows, layer_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="检查主变单措施逐年容量与容载比上限")
    parser.add_argument("--reverse-source", type=Path, default=REVERSE_PROXY)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    stations, layers = build_transformer_only_path(args.reverse_source)
    write_csv(stations, args.output_dir / "transformer_only_path_station_2021_2025.csv")
    write_csv(layers, args.output_dir / "transformer_only_path_layer_2021_2025.csv")
    conflicts = [row for row in layers if row["ratio_status"] == "exceeds_cap"]
    print(f"已生成 {len(stations)} 条站级路径、{len(layers)} 条片区年度结果；R>2.0 的情景 {len(conflicts)} 条。")
    for row in conflicts:
        print(f"冲突：{row['study_region_id']} {row['voltage_kv']} kV {row['year']} {row['reverse_variant']}，R={row['transformer_only_clr']:.3f}")


if __name__ == "__main__":
    main()
