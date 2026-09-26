"""构造可追溯的 2021 年双主变仿真起点；只核对正向供电与片区容载比。"""

import argparse
import csv
from collections import defaultdict
from itertools import combinations_with_replacement
from pathlib import Path

from .asset_2025 import read_assets
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR


STATION_INPUTS = OUTPUT_DIR / "model_station_inputs_2025.csv"
ANNUAL = OUTPUT_DIR / "official_annual.csv"
PIZHOU_SCENARIOS = OUTPUT_DIR / "pizhou_2025_scenarios_evidence.csv"
CITY_SCENARIOS = OUTPUT_DIR / "city_2025_scenario_sensitivity.csv"
SELECTED_BASELINE = OUTPUT_DIR / "baseline_2021_station_candidates.csv"
POWER_FACTOR = 0.95
TRANSFORMERS_PER_STATION = 2
BASELINE_CLR_CAP = 2.0


def read_csv(source: Path) -> list[dict]:
    with Path(source).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_selected_baseline(source: Path = SELECTED_BASELINE) -> list[dict]:
    """Read the recalibrated planning stock used by downstream model stages."""
    rows = read_csv(source)
    numeric = ("simulation_unit_1_mva", "simulation_unit_2_mva",
               "simulation_capacity_mva_2021", "estimated_forward_peak_mw_2021")
    for row in rows:
        row["voltage_kv"] = int(row["voltage_kv"])
        for key in numeric:
            row[key] = float(row[key])
    return rows


def local_unit_catalog() -> dict[tuple[str, int], list[float]]:
    units = defaultdict(set)
    for asset in read_assets():
        if asset["capacity_mva"] > 0:
            units[(asset["region_id"], asset["voltage_kv"])].add(asset["capacity_mva"])
    return {key: sorted(values) for key, values in units.items()}


def select_two_units(
    required_mva: float,
    unit_sizes: list[float],
    minimum_pair: tuple[float, float] | None = None,
) -> tuple[float, float]:
    candidates = [
        pair for pair in combinations_with_replacement(unit_sizes, TRANSFORMERS_PER_STATION)
        if sum(pair) + 1e-9 >= required_mva
        and (minimum_pair is None or all(
            new + 1e-9 >= old for old, new in zip(sorted(minimum_pair), pair)
        ))
    ]
    if not candidates:
        raise ValueError(f"本地双主变容量规格无法满足正向需求 {required_mva:.3f} MVA")
    return min(candidates, key=lambda pair: (sum(pair), pair[1] - pair[0], pair))


def build_baseline(
    station_source: Path = STATION_INPUTS,
    annual_source: Path = ANNUAL,
    pizhou_source: Path = PIZHOU_SCENARIOS,
    city_source: Path = CITY_SCENARIOS,
) -> tuple[list[dict], list[dict]]:
    annual = {
        (row["region_id"], int(row["voltage_kv"]), int(row["year"])): float(row["reported_downward_load_mw"])
        for row in read_csv(annual_source)
    }
    observed_peak = {
        ("QX-00005", int(row["voltage_kv"])): float(row["forward_peak_mw"])
        for row in read_csv(pizhou_source)
    }
    observed_peak[("QX-00007", 110)] = next(
        float(row["forward_peak_mw"])
        for row in read_csv(city_source)
        if row["model_station_id"] == "__DISTRICT__" and row["variant"] == "observed"
    )
    catalog = local_unit_catalog()
    factors = {}
    for key, peak_2025 in observed_peak.items():
        if key[0] == "QX-00005":
            factors[key] = (
                annual[key + (2021,)] / peak_2025,
                "2021_official_peak_over_2025_study_sample_observed_peak",
            )
        else:
            factors[key] = (
                annual[key + (2021,)] / annual[key + (2025,)],
                "2021_over_2025_official_growth_ratio_applied_to_29_station_sample",
            )
    stations = []
    grouped = defaultdict(list)
    for source in read_csv(station_source):
        key = (source["study_region_id"], int(source["voltage_kv"]))
        scale, scale_basis = factors[key]
        estimated_peak = float(source["forward_peak_mw"]) * scale
        required_mva = estimated_peak / POWER_FACTOR
        units = select_two_units(required_mva, catalog[key])
        row = {
            "study_region_id": key[0],
            "voltage_kv": key[1],
            "year": 2021,
            "model_station_id": source["model_station_id"],
            "source_capacity_mva_2025": source["source_capacity_mva_2025"],
            "scenario_scale": round(scale, 9),
            "scenario_scale_basis": scale_basis,
            "estimated_forward_peak_mw_2021": round(estimated_peak, 6),
            "power_factor_assumption": POWER_FACTOR,
            "minimum_required_capacity_mva": round(required_mva, 6),
            "simulation_transformer_count": TRANSFORMERS_PER_STATION,
            "simulation_unit_1_mva": units[0],
            "simulation_unit_2_mva": units[1],
            "simulation_capacity_mva_2021": sum(units),
            "forward_loading_fraction": round(estimated_peak / (POWER_FACTOR * sum(units)), 9),
            "capacity_kind": "simulation_planning_baseline_not_historical_asset",
            "reverse_2021_status": "not_evaluated_no_2021_station_pv_output",
        }
        stations.append(row)
        grouped[key].append(row)
    layers = []
    for key, rows in sorted(grouped.items()):
        district_peak = observed_peak[key] * factors[key][0]
        total_capacity = sum(row["simulation_capacity_mva_2021"] for row in rows)
        clr = total_capacity / district_peak
        layers.append(
            {
                "study_region_id": key[0],
                "voltage_kv": key[1],
                "year": 2021,
                "station_count": len(rows),
                "observed_district_peak_mw_2025": observed_peak[key],
                "scenario_scale": round(factors[key][0], 9),
                "estimated_district_peak_mw_2021": round(district_peak, 6),
                "simulation_capacity_mva_2021": total_capacity,
                "baseline_clr": round(clr, 9),
                "clr_cap": BASELINE_CLR_CAP,
                "forward_and_ratio_status": "forward_ratio_screen_pass" if clr <= BASELINE_CLR_CAP + 1e-9 else "clr_cap_exceeded",
                "reverse_2021_status": "not_evaluated_no_2021_station_pv_output",
            }
        )
    return stations, layers


def build_virtual_city_sensitivity(stations: list[dict], layers: list[dict]) -> list[dict]:
    """仅变动三座市区仿真站的同规格双主变，其他 26 站保持基准方案。"""
    city_layer = next(row for row in layers if row["study_region_id"] == "QX-00007")
    virtual = [row for row in stations if row["model_station_id"].startswith("SIM-CITY-")]
    fixed_capacity = float(city_layer["simulation_capacity_mva_2021"]) - sum(
        float(row["simulation_capacity_mva_2021"]) for row in virtual
    )
    peak = float(city_layer["estimated_district_peak_mw_2021"])
    cases = []
    for unit in local_unit_catalog()[("QX-00007", 110)]:
        capacity = fixed_capacity + len(virtual) * TRANSFORMERS_PER_STATION * unit
        ratio = capacity / peak
        cases.append(
            {
                "study_region_id": "QX-00007",
                "voltage_kv": 110,
                "year": 2021,
                "virtual_station_count": len(virtual),
                "unit_mva_each": unit,
                "transformers_per_virtual_station": TRANSFORMERS_PER_STATION,
                "capacity_mva_each_virtual_station": TRANSFORMERS_PER_STATION * unit,
                "fixed_26_station_capacity_mva": fixed_capacity,
                "study_layer_capacity_mva": capacity,
                "estimated_district_peak_mw_2021": peak,
                "baseline_clr": round(ratio, 9),
                "clr_cap": BASELINE_CLR_CAP,
                "ratio_status": "within_cap" if ratio <= BASELINE_CLR_CAP + 1e-9 else "exceeds_cap",
                "reverse_2021_status": "not_evaluated_no_2021_station_pv_output",
            }
        )
    return cases


def main() -> None:
    parser = argparse.ArgumentParser(description="构造 2021 年仿真容量起点")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    stations, layers = build_baseline()
    write_csv(stations, args.output_dir / "baseline_2021_minimum_station_candidates.csv")
    write_csv(layers, args.output_dir / "baseline_2021_minimum_layer_check.csv")
    write_csv(stations, args.output_dir / "baseline_2021_station_candidates.csv")
    write_csv(layers, args.output_dir / "baseline_2021_layer_check.csv")
    write_csv(build_virtual_city_sensitivity(stations, layers), args.output_dir / "baseline_2021_virtual_city_sensitivity.csv")
    for row in layers:
        print(f"{row['study_region_id']} {row['voltage_kv']} kV：{row['station_count']} 站，仿真容量 {row['simulation_capacity_mva_2021']} MVA，R={row['baseline_clr']:.3f}，{row['forward_and_ratio_status']}")


if __name__ == "__main__":
    main()
