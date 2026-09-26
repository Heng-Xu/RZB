"""从 2025 站级净负荷及分县光伏比例构造历史反向静态代理场景。"""

import argparse
from collections import defaultdict
from pathlib import Path
from statistics import median

from .annual_forward_scenes import build_annual_forward_scenes
from .baseline_2021 import POWER_FACTOR, read_selected_baseline
from .city_mapping_audit import write_csv
from .city_scenarios import CITY_SOURCE, MAPPING_AUDIT, read_city_series
from .hourly_source_profile import OUTPUT_DIR
from .pizhou_station_scenarios import read_pizhou_station_series
from .pv_source_audit import read_monthly_pv
from .reverse_screen_2025 import BETA_UPPER_SCREEN


VARIANTS = {"night_low": 0.8, "night_central": 1.0, "night_high": 1.2, "early_pv_high": 1.0}
TEMPLATE_MONTHS = {3, 4, 5, 9, 10, 11}


def pv_ratio(raw_monthly: dict[tuple[str, int, int], float], region: str, year: int, month: int) -> tuple[float, str]:
    reference = raw_monthly[region, 2025, month]
    if year >= 2023:
        value = raw_monthly[region, year, month]
        basis = "2025_reference" if year == 2025 else "observed_county_same_month_ratio"
    else:
        value_2023 = raw_monthly[region, 2023, month]
        value_2024 = raw_monthly[region, 2024, month]
        value = value_2023 * (value_2023 / value_2024) ** (2023 - year)
        basis = "geometric_backcast_from_2023_2024_county_values"
    return value / reference, basis


def build_annual_reverse_proxy() -> tuple[list[dict], list[dict]]:
    city_series, _ = read_city_series(CITY_SOURCE, MAPPING_AUDIT)
    series = {
        ("QX-00005", voltage, station_id): values
        for (voltage, station_id), values in read_pizhou_station_series().items()
    }
    series.update({("QX-00007", 110, station_id): values for station_id, values in city_series.items()})
    monthly, _ = read_monthly_pv()
    raw_monthly = {(row["region_id"], row["year"], row["month"]): row["source_value"] for row in monthly}
    _, forward_layers = build_annual_forward_scenes()
    load_scales = {
        (row["study_region_id"], row["voltage_kv"], row["year"]): row["annual_scale"]
        for row in forward_layers
    }
    baseline = read_selected_baseline()
    capacities = {
        (row["study_region_id"], row["voltage_kv"], row["model_station_id"]): row["simulation_capacity_mva_2021"]
        for row in baseline
    }
    rows = []
    grouped = defaultdict(list)
    for key, values in sorted(series.items()):
        region, voltage, station_id = key
        eligible = (
            (hour, net) for hour, net in values.items()
            if hour.month in TEMPLATE_MONTHS and hour.weekday() < 5 and 10 <= hour.hour <= 15
        )
        template_time, template_net = min(eligible, key=lambda item: item[1])
        night_values = [
            net for hour, net in values.items()
            if hour.month == template_time.month and (hour.hour < 6 or hour.hour >= 20)
        ]
        night_median = max(0.0, median(night_values))
        capacity = capacities[key]
        reverse_limit = capacity * POWER_FACTOR * BETA_UPPER_SCREEN
        for variant, multiplier in VARIANTS.items():
            gross_2025 = max(template_net, multiplier * night_median)
            pv_output_2025 = gross_2025 - template_net
            for year in range(2021, 2026):
                load_scale = load_scales[region, voltage, year]
                generation_scale, pv_basis = pv_ratio(raw_monthly, region, year, template_time.month)
                if variant == "early_pv_high" and year < 2023:
                    generation_scale, _ = pv_ratio(raw_monthly, region, 2023, template_time.month)
                    pv_basis = "2023_county_same_month_level_held_back_as_early_high_stress"
                projected_net = load_scale * gross_2025 - generation_scale * pv_output_2025
                reverse = max(0.0, -projected_net)
                row = {
                    "study_region_id": region,
                    "voltage_kv": voltage,
                    "year": year,
                    "model_station_id": station_id,
                    "variant": variant,
                    "template_rule": "spring_autumn_weekday_10_to_15_minimum_net_not_verified_dg_maximum",
                    "template_time_2025": template_time.isoformat(sep=" "),
                    "template_month": template_time.month,
                    "observed_net_at_template_mw_2025": round(template_net, 6),
                    "night_sample_hours_2025": len(night_values),
                    "night_median_net_load_mw_2025": round(night_median, 6),
                    "gross_load_proxy_mw_2025": round(gross_2025, 6),
                    "pv_output_proxy_mw_2025": round(pv_output_2025, 6),
                    "annual_load_scale": round(load_scale, 9),
                    "annual_pv_scale": round(generation_scale, 9),
                    "pv_scale_basis": pv_basis,
                    "net_at_2025_template_proxy_mw": round(projected_net, 6),
                    "reverse_at_template_proxy_mw": round(reverse, 6),
                    "baseline_reverse_limit_mw_at_beta_0_8": round(reverse_limit, 6),
                    "baseline_reverse_screen": "exceeds_upper_bound" if reverse > reverse_limit + 1e-9 else "within_upper_bound_not_certified",
                    "scenario_status": "2025_observed_window_template_net" if year == 2025 else "historical_simulation_proxy_not_observed",
                }
                rows.append(row)
                grouped[region, voltage, year, variant].append(row)
    summaries = []
    for (region, voltage, year, variant), stations in sorted(grouped.items()):
        summaries.append(
            {
                "study_region_id": region,
                "voltage_kv": voltage,
                "year": year,
                "variant": variant,
                "station_count": len(stations),
                "station_proxy_reverse_count": sum(row["reverse_at_template_proxy_mw"] > 0 for row in stations),
                "baseline_upper_bound_exceed_count": sum(row["baseline_reverse_screen"] == "exceeds_upper_bound" for row in stations),
                "aggregation_warning": "station_template_times_differ_not_a_synchronous_district_reverse_peak",
                "scenario_status": "2025_station_observed_window_minima" if year == 2025 else "historical_simulation_proxy_not_observed",
            }
        )
    return rows, summaries


def main() -> None:
    parser = argparse.ArgumentParser(description="生成历史年份站级反向静态代理及敏感性")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    stations, layers = build_annual_reverse_proxy()
    write_csv(stations, args.output_dir / "annual_reverse_station_proxy_2021_2025.csv")
    write_csv(layers, args.output_dir / "annual_reverse_layer_summary_2021_2025.csv")
    print(f"已生成 {len(stations)} 条站级代理和 {len(layers)} 条非同步片区摘要；2021—2024 年均非实测。")


if __name__ == "__main__":
    main()
