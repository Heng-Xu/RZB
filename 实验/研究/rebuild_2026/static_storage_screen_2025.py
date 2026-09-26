"""用 2025 站级静态峰值与 D95 连续时段估算储能模块需求。"""

import argparse
from math import ceil
from pathlib import Path

from .baseline_2021 import POWER_FACTOR, read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .incremental_cost import (
    MODULE_ENERGY_MWH,
    MODULE_POWER_MW,
    storage_replicated_package_capex_10k_cny,
)


STATION_INPUTS = OUTPUT_DIR / "model_station_inputs_2025.csv"
BASELINE = OUTPUT_DIR / "baseline_2021_station_candidates.csv"
TRANSFORMER_PATH = OUTPUT_DIR / "transformer_only_path_station_2021_2025.csv"
PIZHOU_SCENES = OUTPUT_DIR / "pizhou_2025_station_scenarios_evidence.csv"
CITY_SCENES = OUTPUT_DIR / "city_2025_scenario_sensitivity.csv"
REVERSE_BETA_SCREEN = 0.8


def module_count_for_peak(shortfall_mw: float, run_hours: int) -> tuple[int, int, int, float]:
    """按峰值缺口持续 D95 最长连续时段的矩形场景估算，不是 SOC 模拟。"""
    if shortfall_mw <= 0:
        return 0, 0, 0, 0.0
    energy_mwh = shortfall_mw * run_hours
    by_power = ceil((shortfall_mw - 1e-12) / MODULE_POWER_MW)
    by_energy = ceil((energy_mwh - 1e-12) / MODULE_ENERGY_MWH)
    return by_power, by_energy, max(by_power, by_energy), energy_mwh


def build_static_storage_screen(
    station_source: Path = STATION_INPUTS,
    baseline_source: Path = BASELINE,
    transformer_source: Path = TRANSFORMER_PATH,
    pizhou_source: Path = PIZHOU_SCENES,
    city_source: Path = CITY_SCENES,
) -> list[dict]:
    durations = {
        ("QX-00005", int(row["voltage_kv"]), row["station_id"]): row
        for row in read_csv(pizhou_source)
    }
    durations.update({
        ("QX-00007", 110, row["model_station_id"]): row
        for row in read_csv(city_source)
        if row["variant"] == "weekly_mean" and row["model_station_id"] != "__DISTRICT__"
    })
    baseline = {
        (row["study_region_id"], int(row["voltage_kv"]), row["model_station_id"]): float(row["simulation_capacity_mva_2021"])
        for row in read_csv(baseline_source)
    }
    transformer = {
        (row["study_region_id"], int(row["voltage_kv"]), row["model_station_id"], int(row["year"])): float(row["selected_capacity_mva"])
        for row in read_csv(transformer_source)
        if int(row["year"]) in (2024, 2025) and row["reverse_variant"] == "night_central"
    }
    rows = []
    for source in read_csv(station_source):
        key = source["study_region_id"], int(source["voltage_kv"]), source["model_station_id"]
        duration = durations[key]
        forward_peak = float(source["forward_peak_mw"])
        reverse_peak = float(source["reverse_peak_mw"])
        forward_run = int(duration["forward_d95_max_run_hours"])
        reverse_run = int(duration["reverse_d95_max_run_hours"])
        for case, capacity in (
            ("hold_2021_simulation_capacity", baseline[key]),
            ("hold_2024_transformer_path_capacity", transformer[key + (2024,)]),
            ("transformer_only_2025_capacity", transformer[key + (2025,)]),
        ):
            forward_shortfall = max(0.0, forward_peak - POWER_FACTOR * capacity)
            reverse_shortfall = max(0.0, reverse_peak - REVERSE_BETA_SCREEN * POWER_FACTOR * capacity)
            forward_by_power, forward_by_energy, forward_modules, forward_energy = module_count_for_peak(forward_shortfall, forward_run)
            reverse_by_power, reverse_by_energy, reverse_modules, reverse_energy = module_count_for_peak(reverse_shortfall, reverse_run)
            modules = max(forward_modules, reverse_modules)
            rows.append({
                "study_region_id": key[0],
                "voltage_kv": key[1],
                "year": 2025,
                "model_station_id": key[2],
                "capacity_case": case,
                "station_capacity_mva": capacity,
                "forward_peak_mw": forward_peak,
                "reverse_peak_mw": reverse_peak,
                "forward_h95_hours": int(duration["forward_h95_hours"]),
                "reverse_h95_hours": int(duration["reverse_h95_hours"]),
                "forward_d95_max_run_hours": forward_run,
                "reverse_d95_max_run_hours": reverse_run,
                "forward_power_shortfall_mw": round(forward_shortfall, 6),
                "reverse_power_shortfall_mw": round(reverse_shortfall, 6),
                "forward_rectangular_energy_proxy_mwh": round(forward_energy, 6),
                "reverse_rectangular_energy_proxy_mwh": round(reverse_energy, 6),
                "forward_modules_by_power": forward_by_power,
                "forward_modules_by_nominal_energy": forward_by_energy,
                "reverse_modules_by_power": reverse_by_power,
                "reverse_modules_by_nominal_energy": reverse_by_energy,
                "required_modules_scenario_proxy": modules,
                "module_power_mw": MODULE_POWER_MW,
                "module_energy_mwh": MODULE_ENERGY_MWH,
                "replicated_package_capex_10k_cny": round(storage_replicated_package_capex_10k_cny(modules), 6),
                "price_basis": (
                    "zero_no_incremental_investment" if modules == 0
                    else "one_to_ten_case_interpolation" if modules <= 10
                    else "ten_cabinet_package_replication_assumption"
                ),
                "technical_status": "station_aggregate_rectangular_D95_proxy_no_SOC_site_or_guide_certification",
                "scenario_basis": source["scenario_basis"],
            })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="输出站级静态储能柜数及案例价格屏查")
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR / "static_storage_need_screen_2025.csv")
    args = parser.parse_args()
    rows = build_static_storage_screen()
    write_csv(rows, args.output)
    print(f"已输出 {len(rows)} 条站级容量情景储能需求；仅为静态 D95 矩形代理，不是可实施方案。")


if __name__ == "__main__":
    main()
