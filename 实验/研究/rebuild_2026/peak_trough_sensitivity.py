"""Diagnose dependence of the Pizhou 35 kV result on the 2023 net-peak trough."""

import argparse
from copy import deepcopy
from pathlib import Path

from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .joint_lifecycle_optimizer import cost_factors, load_inputs, solve_layer


LAYER = ("QX-00005", 35)


def run_sensitivity() -> list[dict]:
    original = load_inputs()
    factors = cost_factors()
    rows = []
    for scenario in ("original_official_peak", "neighbor_year_mean_forward_only"):
        baseline, scene, durations, peaks, catalog, coefficients = deepcopy(original)
        original_peak = peaks[LAYER + (2023,)]
        if scenario == "neighbor_year_mean_forward_only":
            replacement = (peaks[LAYER + (2022,)] + peaks[LAYER + (2024,)]) / 2
            scale = replacement / original_peak
            peaks[LAYER + (2023,)] = replacement
            for (station, year), record in scene.items():
                if station[:2] == LAYER and year == 2023:
                    record["estimated_station_forward_peak_mw"] = (
                        float(record["estimated_station_forward_peak_mw"]) * scale)
        for cap in (2.0, 2.4, 4.0):
            _, years, _, summary = solve_layer(
                LAYER, baseline, scene, durations, peaks, catalog, coefficients,
                factors, cap, False)
            row_2023 = next(row for row in years if row["year"] == 2023)
            rows.append({
                "scenario": scenario, "study_region_id": LAYER[0], "voltage_kv": LAYER[1],
                "official_2023_peak_mw": original_peak,
                "scenario_2023_peak_mw": round(peaks[LAYER + (2023,)], 6),
                "reverse_proxy_unchanged": True,
                "scan_cap": cap,
                "objective_npv_10k_cny": summary["objective_npv_10k_cny"],
                "max_actual_clr": summary["max_actual_clr"],
                "actual_clr_2023": row_2023["actual_clr"],
                "interpretation": ("official_source_anchor" if scenario == "original_official_peak"
                                   else "counterfactual_peak_sensitivity_not_correction_of_official_source"),
            })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="邳州 35 kV 2023 年峰值低谷敏感性")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    rows = run_sensitivity()
    write_csv(rows, args.output_dir / "peak_trough_sensitivity_35kv.csv")
    print(f"输出 {len(rows)} 条峰值低谷反事实诊断记录")


if __name__ == "__main__":
    main()
