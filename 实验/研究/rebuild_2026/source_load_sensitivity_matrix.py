"""Full-path synthetic gross-demand and PV-pressure scenarios for three fixed units."""

import argparse
from pathlib import Path

from .baseline_2021 import read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .joint_lifecycle_optimizer import cost_factors, load_inputs, solve_layer


LAYERS = (("QX-00005", 35), ("QX-00005", 110), ("QX-00007", 110))
DEMAND_FACTORS = (1.0, 1.05, 1.1)
PV_FACTORS = (0.8, 1.0, 1.2)
PRICES = (("base", 1.0, 1.0), ("transformer_half", 0.5, 1.0),
          ("storage_double", 1.0, 2.0))


def build_scenarios() -> tuple[list[dict], list[dict], list[dict]]:
    baseline, base_scene, durations, base_peaks, catalog, coefficients = load_inputs()
    reverse = {
        ((r["study_region_id"], int(r["voltage_kv"]), r["model_station_id"]), int(r["year"])): r
        for r in read_csv(OUTPUT_DIR / "annual_reverse_station_proxy_2021_2025.csv")
        if r["variant"] == "night_central" and int(r["year"]) >= 2022
    }
    factors = cost_factors()
    summaries, annual, measures = [], [], []
    for layer in LAYERS:
        for demand_factor in DEMAND_FACTORS:
            for pv_factor in PV_FACTORS:
                scene = {k: dict(v) for k, v in base_scene.items()}
                peaks = dict(base_peaks)
                for key, row in scene.items():
                    station, year = key
                    if station[:2] != layer:
                        continue
                    proxy = reverse[key]
                    extra_gross = ((demand_factor - 1) * float(proxy["annual_load_scale"])
                                   * float(proxy["gross_load_proxy_mw_2025"]))
                    extra_pv = ((pv_factor - 1) * float(proxy["annual_pv_scale"])
                                * float(proxy["pv_output_proxy_mw_2025"]))
                    row["estimated_station_forward_peak_mw"] = (
                        float(row["estimated_station_forward_peak_mw"]) * demand_factor)
                    row["reverse_screen_mw"] = max(
                        0.0, float(row["reverse_screen_mw"]) - extra_gross + extra_pv)
                    peaks[layer + (year,)] = base_peaks[layer + (year,)] * demand_factor
                for price_name, transformer_scale, storage_scale in PRICES:
                    if layer != ("QX-00005", 35) and price_name != "base":
                        continue
                    scenario_id = (f"{layer[0]}_{layer[1]}_gross{demand_factor:.2f}"
                                   f"_pv{pv_factor:.2f}_{price_name}")
                    options = dict(transformer_cost_scale=transformer_scale,
                                   storage_cost_scale=storage_scale, tie_allowed=False)
                    rigid = solve_layer(layer, baseline, scene, durations, peaks, catalog,
                                        coefficients, factors, 2.0, False, **options)
                    relaxed_cap = 3.0 if layer[0] == "QX-00007" else 4.0
                    relaxed = solve_layer(layer, baseline, scene, durations, peaks, catalog,
                                          coefficients, factors, relaxed_cap, False, **options)
                    saving = rigid[3]["objective_npv_10k_cny"] - relaxed[3]["objective_npv_10k_cny"]
                    summaries.append({
                        "scenario_id": scenario_id, "study_region_id": layer[0], "voltage_kv": layer[1],
                        "gross_demand_factor_2022_2025": demand_factor,
                        "pv_output_factor_2022_2025": pv_factor,
                        "price_case": price_name,
                        "transformer_cost_scale": transformer_scale,
                        "storage_cost_scale": storage_scale,
                        "rigid_cap": 2.0, "relaxed_cap": relaxed_cap,
                        "rigid_npv_10k_cny": rigid[3]["objective_npv_10k_cny"],
                        "relaxed_npv_10k_cny": relaxed[3]["objective_npv_10k_cny"],
                        "saving_10k_cny": round(saving, 6),
                        "rigid_max_actual_clr": rigid[3]["max_actual_clr"],
                        "relaxed_max_actual_clr": relaxed[3]["max_actual_clr"],
                        "same_measure_scope": True,
                        "scenario_scope": "2025_template_hypothetical_gross_and_pv_pressure_not_observed_years",
                    })
                    for label, result in (("cap_2", rigid), ("relaxed", relaxed)):
                        for row in result[1]:
                            annual.append({
                                "scenario_id": scenario_id, "scheme": label, "year": row["year"],
                                "scan_cap": row["clr_cap"], "annual_forward_net_peak_mw": row["synchronous_forward_peak_mw"],
                                "actual_clr": row["actual_clr"],
                                "selected_capacity_mva": row["selected_capacity_mva"],
                                "storage_modules_in_service": row["storage_modules_in_service"],
                                "tie_transfer_event_count": len(result[2]),
                            })
                        for row in result[0]:
                            if row["transformer_capex_10k_cny"] > 1e-8 or row["new_storage_modules"] > 0:
                                measures.append({
                                    "scenario_id": scenario_id, "scheme": label, "year": row["year"],
                                    "model_station_id": row["model_station_id"],
                                    "prior_unit_1_mva": row["prior_unit_1_mva"],
                                    "prior_unit_2_mva": row["prior_unit_2_mva"],
                                    "selected_unit_1_mva": row["selected_unit_1_mva"],
                                    "selected_unit_2_mva": row["selected_unit_2_mva"],
                                    "new_storage_modules": row["new_storage_modules"],
                                    "transformer_capex_10k_cny": row["transformer_capex_10k_cny"],
                                    "storage_capex_10k_cny": row["storage_capex_10k_cny"],
                                })
    return summaries, annual, measures


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    summaries, annual, measures = build_scenarios()
    write_csv(summaries, args.output_dir / "source_load_sensitivity_summary.csv")
    write_csv(annual, args.output_dir / "source_load_sensitivity_annual.csv")
    write_csv(measures, args.output_dir / "source_load_sensitivity_measures.csv")
    print(f"{len(summaries)} scenarios; {len(annual)} annual rows; {len(measures)} measures")


if __name__ == "__main__":
    main()
