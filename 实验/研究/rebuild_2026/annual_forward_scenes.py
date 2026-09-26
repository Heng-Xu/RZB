"""用 2025 年同步正向峰值模板和年度比例构造 2021—2025 静态正向场景。"""

import argparse
from collections import defaultdict
from pathlib import Path

from .baseline_2021 import ANNUAL, CITY_SCENARIOS, PIZHOU_SCENARIOS, read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR


PIZHOU_STATION_SCENES = OUTPUT_DIR / "pizhou_2025_station_values_at_district_scenes.csv"
CITY_STATION_SCENES = OUTPUT_DIR / "city_2025_station_values_at_district_scenes.csv"


def build_annual_forward_scenes(
    annual_source: Path = ANNUAL,
    pizhou_layer_source: Path = PIZHOU_SCENARIOS,
    city_layer_source: Path = CITY_SCENARIOS,
    pizhou_station_source: Path = PIZHOU_STATION_SCENES,
    city_station_source: Path = CITY_STATION_SCENES,
) -> tuple[list[dict], list[dict]]:
    official = {
        (row["region_id"], int(row["voltage_kv"]), int(row["year"])): float(row["reported_downward_load_mw"])
        for row in read_csv(annual_source)
    }
    template_layers = {}
    for row in read_csv(pizhou_layer_source):
        key = row["region_id"], int(row["voltage_kv"])
        template_layers[key] = (float(row["forward_peak_mw"]), row["forward_peak_time"])
    city = next(
        row for row in read_csv(city_layer_source)
        if row["model_station_id"] == "__DISTRICT__" and row["variant"] == "observed"
    )
    template_layers[("QX-00007", 110)] = (float(city["forward_peak_mw"]), city["forward_peak_time"])

    template_stations = defaultdict(list)
    for path, station_field in (
        (pizhou_station_source, "station_id"),
        (city_station_source, "model_station_id"),
    ):
        for row in read_csv(path):
            if row["scenario_kind"] != "district_forward_peak":
                continue
            key = row["region_id"], int(row["voltage_kv"])
            template_stations[key].append((row[station_field], float(row["station_net_load_mw"])))

    stations = []
    layers = []
    for key, (template_peak, template_time) in sorted(template_layers.items()):
        for year in range(2021, 2026):
            if key[0] == "QX-00005":
                factor = official[key + (year,)] / template_peak
                basis = "official_target_year_peak_over_2025_study_sample_peak"
            else:
                factor = official[key + (year,)] / official[key + (2025,)]
                basis = "official_target_year_over_2025_growth_ratio_for_29_station_sample"
            peak = template_peak * factor
            layer = {
                "study_region_id": key[0],
                "voltage_kv": key[1],
                "year": year,
                "station_count": len(template_stations[key]),
                "template_year": 2025,
                "template_forward_peak_time": template_time,
                "template_forward_peak_mw": template_peak,
                "annual_scale": round(factor, 9),
                "scale_basis": basis,
                "estimated_synchronous_forward_peak_mw": round(peak, 6),
                "time_status": ("2025_observed_time_rescaled_to_official_annual_peak"
                                if year == 2025 and key[0] == "QX-00005" else
                                "observed_2025" if year == 2025 else
                                "2025_time_template_not_observed_in_target_year"),
                "reverse_scenario_status": "not_derived_from_forward_scaling",
            }
            layers.append(layer)
            for station_id, template_net in template_stations[key]:
                stations.append(
                    {
                        "study_region_id": key[0],
                        "voltage_kv": key[1],
                        "year": year,
                        "model_station_id": station_id,
                        "scenario_kind": "synchronous_district_forward_peak_proxy",
                        "template_forward_peak_time": template_time,
                        "template_station_net_load_mw": template_net,
                        "annual_scale": round(factor, 9),
                        "estimated_station_net_load_mw": round(template_net * factor, 6),
                        "estimated_district_forward_peak_mw": round(peak, 6),
                        "time_status": layer["time_status"],
                    }
                )
    return stations, layers


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 2021—2025 年同步正向峰值静态代理场景")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    stations, layers = build_annual_forward_scenes()
    write_csv(stations, args.output_dir / "annual_forward_station_scenes_2021_2025.csv")
    write_csv(layers, args.output_dir / "annual_forward_layer_scenes_2021_2025.csv")
    print(f"已生成 {len(stations)} 条站级场景和 {len(layers)} 条片区场景；非 2025 年时刻均为模板代理。")


if __name__ == "__main__":
    main()
