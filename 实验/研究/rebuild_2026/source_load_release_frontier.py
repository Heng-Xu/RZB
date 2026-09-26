"""Refine the first relaxed-cap saving for positive base-price stress cases."""

import argparse
from pathlib import Path

from .baseline_2021 import read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .joint_lifecycle_optimizer import cost_factors, load_inputs, solve_layer


LAYER = ("QX-00005", 35)


def release_frontier() -> list[dict]:
    baseline, original, durations, base_peaks, catalog, coefficients = load_inputs()
    reverse = {
        ((r["study_region_id"], int(r["voltage_kv"]), r["model_station_id"]), int(r["year"])): r
        for r in read_csv(OUTPUT_DIR / "annual_reverse_station_proxy_2021_2025.csv")
        if r["variant"] == "night_central" and int(r["year"]) >= 2022
    }
    candidates = [r for r in read_csv(OUTPUT_DIR / "source_load_sensitivity_summary.csv")
                  if (r["study_region_id"], int(r["voltage_kv"])) == LAYER
                  and r["price_case"] == "base" and float(r["saving_10k_cny"]) > 1e-4]
    rows = []
    for candidate in candidates:
        gross = float(candidate["gross_demand_factor_2022_2025"])
        pv = float(candidate["pv_output_factor_2022_2025"])
        scene = {k: dict(v) for k, v in original.items()}
        peaks = dict(base_peaks)
        for key, station in scene.items():
            if key[0][:2] != LAYER:
                continue
            proxy = reverse[key]
            station["estimated_station_forward_peak_mw"] = (
                float(station["estimated_station_forward_peak_mw"]) * gross)
            station["reverse_screen_mw"] = max(
                0.0, float(station["reverse_screen_mw"])
                - (gross - 1) * float(proxy["annual_load_scale"]) * float(proxy["gross_load_proxy_mw_2025"])
                + (pv - 1) * float(proxy["annual_pv_scale"]) * float(proxy["pv_output_proxy_mw_2025"]),
            )
            peaks[LAYER + (key[1],)] = base_peaks[LAYER + (key[1],)] * gross
        factors = cost_factors()
        cache = {}

        def evaluate(cap):
            if cap not in cache:
                cache[cap] = solve_layer(LAYER, baseline, scene, durations, peaks,
                                         catalog, coefficients, factors, cap, False,
                                         tie_allowed=False)
            return cache[cap]

        rigid_cost = evaluate(2.0)[3]["objective_npv_10k_cny"]
        low, high = 2.0, 4.0
        for _ in range(19):
            mid = (low + high) / 2
            if evaluate(mid)[3]["objective_npv_10k_cny"] < rigid_cost - 1e-4:
                high = mid
            else:
                low = mid
        first = evaluate(high)
        rows.append({
            "scenario_id": candidate["scenario_id"],
            "gross_demand_factor": gross, "pv_output_factor": pv,
            "first_cost_release_cap_approx": round(high, 8),
            "bracket_width": high - low,
            "first_release_saving_10k_cny": round(
                rigid_cost - first[3]["objective_npv_10k_cny"], 6),
            "first_release_max_actual_clr": first[3]["max_actual_clr"],
            "minimum_cost_at_cap_4_10k_cny": candidate["relaxed_npv_10k_cny"],
            "saving_at_cap_4_10k_cny": candidate["saving_10k_cny"],
            "scope": "hypothetical_joint_pressure_same_no_tie_measures",
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    rows = release_frontier()
    write_csv(rows, args.output_dir / "source_load_release_frontier_35kv.csv")
    for row in rows:
        print(row["scenario_id"], row["first_cost_release_cap_approx"], row["first_release_saving_10k_cny"])


if __name__ == "__main__":
    main()
