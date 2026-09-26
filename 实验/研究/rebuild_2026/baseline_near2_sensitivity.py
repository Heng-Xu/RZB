"""Select a near-2.0 counterfactual 2021 baseline and retain the minimum case."""

import argparse
from itertools import combinations_with_replacement
from pathlib import Path

from .annual_no_tie_investment_submodel import LinearModel
from .baseline_2021 import build_virtual_city_sensitivity, read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .joint_lifecycle_optimizer import cost_factors, load_inputs, solve_layer


LAYERS = (("QX-00005", 35), ("QX-00005", 110), ("QX-00007", 110))
def near_two_baseline(baseline: dict, catalog: dict,
                      capacity_upper_override: dict | None = None) -> tuple[dict, list[dict]]:
    layers = {(r["study_region_id"], int(r["voltage_kv"])): r
              for r in read_csv(OUTPUT_DIR / "baseline_2021_minimum_layer_check.csv")}
    alternative = {key: dict(value) for key, value in baseline.items()}
    detail = []
    for layer in LAYERS:
        stations = sorted(key for key in baseline if key[:2] == layer)
        model = LinearModel()
        variables, options = {}, {}
        for station in stations:
            source_cell = baseline[station]["source_capacity_mva_2025"]
            existing = float(baseline[station]["simulation_unit_1_mva"]) + float(baseline[station]["simulation_unit_2_mva"])
            source = float(source_cell) if source_cell else existing
            required = float(baseline[station]["estimated_forward_peak_mw_2021"]) / 0.95
            pairs = [pair for pair in combinations_with_replacement(catalog[layer], 2)
                     if required - 1e-8 <= sum(pair) <= source + 1e-8]
            if not pairs:
                raise ValueError(f"{station} 无不超过 2025 台账容量的候选")
            options[station] = pairs
            for pair in pairs:
                variables[station, pair] = model.variable((source - sum(pair)) ** 2 / source)
            model.constraint({variables[station, pair]: 1 for pair in pairs}, lower=1, upper=1)
        peak = float(layers[layer]["estimated_district_peak_mw_2021"])
        cap = min(2 * peak, (capacity_upper_override or {}).get(layer, 2 * peak))
        model.constraint({variables[station, pair]: sum(pair)
                          for station in stations for pair in options[station]}, upper=cap)
        solution, _ = model.solve()
        for station in stations:
            pair = next(pair for pair in options[station] if solution[variables[station, pair]] > 0.5)
            original = baseline[station]
            source_cell = original["source_capacity_mva_2025"]
            alternative[station]["simulation_unit_1_mva"] = pair[0]
            alternative[station]["simulation_unit_2_mva"] = pair[1]
            detail.append({
                "study_region_id": layer[0], "voltage_kv": layer[1],
                "model_station_id": station[2],
                "original_minimum_baseline_mva": float(original["simulation_unit_1_mva"]) + float(original["simulation_unit_2_mva"]),
                "near_two_baseline_unit_1_mva": pair[0],
                "near_two_baseline_unit_2_mva": pair[1],
                "near_two_baseline_mva": sum(pair),
                "source_capacity_mva_2025_proxy_ceiling": source_cell or "",
                "capacity_ceiling_basis": "2025_asset_snapshot" if source_cell else "original_simulation_pair_no_verified_asset",
                "status": "counterfactual_2021_not_historical_station_capacity",
            })
    return alternative, detail


def compare() -> tuple[list[dict], list[dict], list[dict]]:
    _, scene, durations, peaks, catalog, coefficients = load_inputs()
    baseline = {(r["study_region_id"], int(r["voltage_kv"]), r["model_station_id"]): r
                for r in read_csv(OUTPUT_DIR / "baseline_2021_minimum_station_candidates.csv")}
    factors = cost_factors()
    layers = {(r["study_region_id"], int(r["voltage_kv"])): r
              for r in read_csv(OUTPUT_DIR / "baseline_2021_minimum_layer_check.csv")}
    overrides, search = {}, []
    for layer in LAYERS:
        first_peak = float(layers[layer]["estimated_district_peak_mw_2021"])
        minimum = sum(float(r["simulation_unit_1_mva"]) + float(r["simulation_unit_2_mva"])
                      for s, r in baseline.items() if s[:2] == layer)
        caps = [2 * first_peak] + list(range(int(2 * first_peak), int(minimum) - 1, -1))
        for cap in caps:
            candidate, _ = near_two_baseline(baseline, catalog, {**overrides, layer: cap})
            selected = sum(float(r["simulation_unit_1_mva"]) + float(r["simulation_unit_2_mva"])
                           for s, r in candidate.items() if s[:2] == layer)
            try:
                solve_layer(layer, candidate, scene, durations, peaks, catalog, coefficients,
                            factors, 2.0, True)
                feasible = True
            except ValueError as exc:
                if "infeasible" not in str(exc):
                    raise
                feasible = False
            search.append({"study_region_id": layer[0], "voltage_kv": layer[1],
                           "tested_initial_capacity_upper_mva": cap,
                           "selected_initial_capacity_mva": selected,
                           "full_horizon_rigid_feasible": feasible,
                           "selection_rule": "first_feasible_integer_mva_cap_descending"})
            if feasible:
                overrides[layer] = cap
                break
        else:
            raise ValueError(f"{layer} 没有找到完整刚性路径可行的 2021 起点")
    alternative, detail = near_two_baseline(baseline, catalog, overrides)
    rows = []
    for layer in LAYERS:
        first_peak = float(layers[layer]["estimated_district_peak_mw_2021"])
        for baseline_name, candidate in (("minimum_capacity", baseline), ("near_two_counterfactual", alternative)):
            capacity = sum(float(candidate[s]["simulation_unit_1_mva"]) +
                           float(candidate[s]["simulation_unit_2_mva"])
                           for s in candidate if s[:2] == layer)
            for name, cap, ties in (("rigid_formal", 2.0, True),
                                    ("elastic_formal", 3.0 if layer[0] == "QX-00007" else 4.0, False),
                                    ("rigid_same_scope_no_ties", 2.0, False)):
                _, years, transfers, summary = solve_layer(
                    layer, candidate, scene, durations, peaks, catalog, coefficients,
                    factors, cap, name == "rigid_formal", tie_allowed=ties)
                rows.append({
                    "study_region_id": layer[0], "voltage_kv": layer[1],
                    "baseline_scenario": baseline_name,
                    "2021_planning_capacity_mva": capacity,
                    "2021_clr": round(capacity / first_peak, 9),
                    "scheme_or_control": name, "scan_cap": cap,
                    "ties_allowed": ties and layer[1] == 110,
                    "objective_npv_10k_cny": summary["objective_npv_10k_cny"],
                    "max_actual_clr_2022_2025": summary["max_actual_clr"],
                    "2025_capacity_mva": years[-1]["selected_capacity_mva"],
                    "tie_transfer_event_count": len(transfers),
                    "status": "baseline_sensitivity_not_validated_2021_equipment_plan",
                })
    return rows, detail, search


def main() -> None:
    parser = argparse.ArgumentParser(description="2021 最小容量与近 2.0 起点反事实对照")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    rows, detail, search = compare()
    write_csv(rows, args.output_dir / "baseline_near2_sensitivity.csv")
    write_csv(detail, args.output_dir / "baseline_near2_station_candidates.csv")
    write_csv(search, args.output_dir / "baseline_near2_full_horizon_search.csv")
    selected = {(r["study_region_id"], int(r["voltage_kv"]), r["model_station_id"]): r for r in detail}
    stations = []
    for row in read_csv(args.output_dir / "baseline_2021_minimum_station_candidates.csv"):
        key = row["study_region_id"], int(row["voltage_kv"]), row["model_station_id"]
        choice = selected[key]
        updated = dict(row)
        updated["simulation_unit_1_mva"] = choice["near_two_baseline_unit_1_mva"]
        updated["simulation_unit_2_mva"] = choice["near_two_baseline_unit_2_mva"]
        updated["simulation_capacity_mva_2021"] = choice["near_two_baseline_mva"]
        updated["forward_loading_fraction"] = round(
            float(row["estimated_forward_peak_mw_2021"]) /
            (0.95 * float(choice["near_two_baseline_mva"])), 9)
        updated["baseline_selection_rule"] = "near_two_with_2025_asset_proxy_and_full_horizon_rigid_feasibility"
        stations.append(updated)
    layers = []
    for row in read_csv(args.output_dir / "baseline_2021_minimum_layer_check.csv"):
        updated = dict(row)
        matching = [station for station in stations
                    if (station["study_region_id"], int(station["voltage_kv"])) ==
                    (row["study_region_id"], int(row["voltage_kv"]))]
        total = sum(float(station["simulation_capacity_mva_2021"]) for station in matching)
        updated["simulation_capacity_mva_2021"] = total
        updated["baseline_clr"] = round(total / float(row["estimated_district_peak_mw_2021"]), 9)
        updated["baseline_selection_rule"] = "near_two_with_full_horizon_rigid_feasibility"
        layers.append(updated)
    write_csv(stations, args.output_dir / "baseline_2021_station_candidates.csv")
    write_csv(layers, args.output_dir / "baseline_2021_layer_check.csv")
    write_csv(build_virtual_city_sensitivity(stations, layers),
              args.output_dir / "baseline_2021_virtual_city_sensitivity.csv")
    print(f"输出 {len(rows)} 条成本对照、{len(detail)} 条站级仿真起点")


if __name__ == "__main__":
    main()
