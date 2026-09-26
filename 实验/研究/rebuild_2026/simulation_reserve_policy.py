"""历史容量共同起点：成本最小且考虑停运恢复的刚弹条件方案。"""

from pathlib import Path

from .baseline_historical_proxy import build as build_baseline
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .joint_lifecycle_optimizer import (
    DESIGNED_NEW_LINE_KM, PIZHOU_110, cost_factors, load_inputs, solve_layer,
)


OUTPUT = OUTPUT_DIR / "capacity_release_simulation/reserve_policy_v4"
SETTINGS = {
    ("QX-00005", 35): {"rigid_budget": .30, "contingency_fraction": .60},
    ("QX-00005", 110): {"rigid_budget": .03, "contingency_fraction": .60},
    ("QX-00007", 110): {"rigid_budget": .01, "contingency_fraction": .45},
}


def run(output_dir: Path = OUTPUT) -> list[dict]:
    output_dir = Path(output_dir)
    station_baseline, layer_baseline = build_baseline()
    write_csv(station_baseline, output_dir / "baseline_stations.csv")
    write_csv(layer_baseline, output_dir / "baseline_layers.csv")
    baseline = {(r["study_region_id"], int(r["voltage_kv"]), r["model_station_id"]): r
                for r in station_baseline}
    _, scenes, durations, peaks, catalog, coefficients = load_inputs()
    summaries = []
    annual_matrix = []
    for layer, setting in SETTINGS.items():
        by_scheme = {}
        for scheme in ("rigid", "elastic"):
            rigid = scheme == "rigid"
            stations, years, transfers, summary = solve_layer(
                layer, baseline, scenes, durations, peaks, catalog, coefficients,
                cost_factors(), 2.0 if rigid else 3.2, rigid,
                include_new_line=layer == PIZHOU_110,
                new_line_variant="designed_bus", line_km=DESIGNED_NEW_LINE_KM,
                tie_allowed=layer == PIZHOU_110,
                policy_peak_basis="annual", max_storage_modules=50,
                allow_capacity_release=True,
                capacity_growth_budget_fraction=setting["rigid_budget"] if rigid else None,
                prefer_reserve_at_equal_cost=True,
                contingency_service_fraction=setting["contingency_fraction"],
                require_existing_tie_operation=False,
                tie_year_basis="annual_station_scaled",
                canonicalize_tie_dispatch=True,
            )
            stem = f"{scheme}_{layer[0]}_{layer[1]}"
            write_csv(stations, output_dir / f"{stem}_stations.csv")
            write_csv(years, output_dir / f"{stem}_years.csv")
            if transfers:
                write_csv(transfers, output_dir / f"{stem}_ties.csv")
            summary.update({"scheme": scheme, "study_status": "conditional_reserve_simulation",
                            "baseline_kind": "2021_reported_regional_capacity_allocated_to_stations",
                            "reference_peak_kind": ("official_annual_downward_load" if layer[0] == "QX-00005"
                                                    else "29_station_sample_scaled_by_official_growth"),
                            "rigid_budget_assumption": setting["rigid_budget"],
                            "contingency_fraction_assumption": setting["contingency_fraction"]})
            summaries.append(summary)
            by_scheme[scheme] = (years, transfers, summary)
        rigid_years, rigid_ties, rigid_summary = by_scheme["rigid"]
        elastic_years, elastic_ties, elastic_summary = by_scheme["elastic"]
        selected = ("elastic" if elastic_summary["objective_npv_10k_cny"] <=
                    rigid_summary["objective_npv_10k_cny"] + 1e-5 else "rigid")
        for ry, ey in zip(rigid_years, elastic_years):
            if ry["year"] != ey["year"]:
                raise ValueError("刚弹年度未对齐")
            chosen = ry if selected == "rigid" else ey
            annual_matrix.append({
                "study_region_id": layer[0], "voltage_kv": layer[1], "year": ry["year"],
                "reference_peak_mw": ry["synchronous_forward_peak_mw"],
                "reference_peak_kind": summary["reference_peak_kind"],
                "rigid_budget_fraction": setting["rigid_budget"],
                "contingency_fraction": setting["contingency_fraction"],
                "rigid_cost_npv_10k_cny": rigid_summary["objective_npv_10k_cny"],
                "elastic_cost_npv_10k_cny": elastic_summary["objective_npv_10k_cny"],
                "rigid_capacity_mva": ry["selected_capacity_mva"],
                "rigid_clr": ry["actual_clr"],
                "rigid_storage_modules": ry["storage_modules_in_service"],
                "elastic_capacity_mva": ey["selected_capacity_mva"],
                "elastic_clr": ey["actual_clr"],
                "elastic_storage_modules": ey["storage_modules_in_service"],
                "rigid_new_line_built": ry["line_built"],
                "rigid_existing_tie_mw": round(sum(float(t["transfer_mw"]) for t in rigid_ties
                                                    if t["year"] == ry["year"] and t["tie_id"] == "T01"), 6),
                "rigid_new_line_transfer_mw": round(sum(float(t["transfer_mw"]) for t in rigid_ties
                                                        if t["year"] == ry["year"] and t["tie_id"] != "T01"), 6),
                "elastic_new_line_built": ey["line_built"],
                "elastic_existing_tie_mw": round(sum(float(t["transfer_mw"]) for t in elastic_ties
                                                      if t["year"] == ey["year"] and t["tie_id"] == "T01"), 6),
                "elastic_new_line_transfer_mw": round(sum(float(t["transfer_mw"]) for t in elastic_ties
                                                         if t["year"] == ey["year"] and t["tie_id"] != "T01"), 6),
                "selected_scheme_by_incremental_cost": selected,
                "selected_planning_clr": chosen["actual_clr"],
                "status": "conditional_simulation_not_engineering_plan",
            })
    write_csv(summaries, output_dir / "summary.csv")
    write_csv(annual_matrix, output_dir / "annual_matrix.csv")
    return summaries


if __name__ == "__main__":
    for row in run():
        print(row["study_region_id"], row["voltage_kv"], row["scheme"],
              row["objective_npv_10k_cny"], row["max_actual_clr"])
