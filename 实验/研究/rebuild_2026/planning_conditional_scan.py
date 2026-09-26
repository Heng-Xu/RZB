"""在共同仿真起点上扫描源荷代理、成本与联络能力，形成条件矩阵底表。"""

from copy import deepcopy
from pathlib import Path

from .baseline_2021 import read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .joint_lifecycle_optimizer import YEARS, cost_factors, load_inputs, solve_layer


SCENARIOS = (
    ("base", "reference", 0.0, 1.0, 1.0, 1.0, 1.0, 1.0),
    ("forward_growth_minus10pct", "net_forward_growth_stress", -0.10, 1.0, 1.0, 1.0, 1.0, 1.0),
    ("forward_growth_plus10pct", "net_forward_growth_stress", 0.10, 1.0, 1.0, 1.0, 1.0, 1.0),
    ("transformer_price_70pct", "price_stress", 0.0, 0.70, 1.0, 1.0, 1.0, 1.0),
    ("transformer_price_150pct", "price_stress", 0.0, 1.50, 1.0, 1.0, 1.0, 1.0),
    ("storage_price_70pct", "price_stress", 0.0, 1.0, 0.70, 1.0, 1.0, 1.0),
    ("storage_price_150pct", "price_stress", 0.0, 1.0, 1.50, 1.0, 1.0, 1.0),
    ("tie_capacity_40pct", "tie_capacity_stress", 0.0, 1.0, 1.0, 0.40, 1.0, 1.0),
    ("tie_capacity_70pct", "tie_capacity_stress", 0.0, 1.0, 1.0, 0.70, 1.0, 1.0),
    ("tie_capacity_90pct", "tie_capacity_stress", 0.0, 1.0, 1.0, 0.90, 1.0, 1.0),
    ("tie_capacity_95pct", "tie_capacity_stress", 0.0, 1.0, 1.0, 0.95, 1.0, 1.0),
    ("forward_duration_double", "duration_stress", 0.0, 1.0, 1.0, 1.0, 2.0, 1.0),
    ("pv_source_pressure_plus25pct", "joint_pv_reverse_stress", 0.0, 1.0, 1.0, 1.0, 1.0, 1.25),
)


def build_scan(output_dir: Path = OUTPUT_DIR,
               growth_rebuild: bool = False) -> tuple[list[dict], list[dict]]:
    output_dir = Path(output_dir)
    baseline = {(r["study_region_id"], int(r["voltage_kv"]), r["model_station_id"]): r
                for r in read_csv(output_dir / "planning_2021_common_baseline_stations.csv")}
    _, scene_base, durations_base, peaks_base, catalog, coefficients = load_inputs()
    peak_2021 = {(r["study_region_id"], int(r["voltage_kv"])): float(r["net_forward_peak_mw"])
                 for r in read_csv(output_dir / "planning_2021_common_baseline_layers.csv")}
    source_ratio = {r["region_id"]: float(r["pv_to_gross_load_ratio_proxy"])
                    for r in read_csv(output_dir / "source_load_scan_ceiling_research.csv")}
    h95_template = {(r["region_id"], int(r["voltage_kv"])): int(r["forward_h95_observed"])
                    for r in read_csv(output_dir / "pizhou_2025_scenarios_evidence.csv")}
    h95_template[("QX-00007", 110)] = next(
        int(r["forward_h95_hours"])
        for r in read_csv(output_dir / "city_2025_scenario_sensitivity.csv")
        if r["model_station_id"] == "__DISTRICT__" and r["variant"] == "observed")
    factors = cost_factors()
    matrix, inventory, feasibility = [], [], []
    for scenario_id, family, growth, transformer_price, storage_price, tie_scale, duration_scale, reverse_scale in SCENARIOS:
        source_scale = 1.25 if family == "joint_pv_reverse_stress" else 1.0
        scene = deepcopy(scene_base)
        durations = deepcopy(durations_base)
        peaks = dict(peaks_base)
        for (station, year), row in scene.items():
            forward_factor = 1 + growth * (year - 2021) / 4
            row["estimated_station_forward_peak_mw"] = float(row["estimated_station_forward_peak_mw"]) * forward_factor
            row["reverse_screen_mw"] = float(row["reverse_screen_mw"]) * reverse_scale
        for (region, voltage, year), peak in list(peaks.items()):
            peaks[region, voltage, year] = peak * (1 + growth * (year - 2021) / 4)
        if duration_scale != 1:
            for row in durations.values():
                row["forward_d95_max_run_hours"] = max(1, round(float(row["forward_d95_max_run_hours"]) * duration_scale))
        inventory.append({"scenario_id": scenario_id, "family": family,
                          "net_forward_2025_change_fraction": growth,
                          "transformer_cost_scale": transformer_price,
                          "storage_cost_scale": storage_price,
                          "tie_transfer_limit_scale": tie_scale,
                          "forward_d95_duration_scale": duration_scale,
                          "reverse_peak_scale": reverse_scale,
                          "source_load_ratio_proxy_scale": source_scale,
                          "status": "counterfactual_simulation_not_new_observation"})
        for layer in sorted(peak_2021):
            results = {}
            for scheme in ("rigid", "elastic"):
                cap = 2.0 if scheme == "rigid" else 2.4
                try:
                    results[scheme] = solve_layer(
                        layer, baseline, scene, durations, peaks, catalog, coefficients,
                        factors, cap, scheme == "rigid",
                        transformer_cost_scale=transformer_price,
                        storage_cost_scale=storage_price,
                        tie_transfer_limit_scale=tie_scale,
                        include_new_line=growth_rebuild and scheme == "rigid" and layer == ("QX-00005", 110),
                        new_line_variant="designed_bus" if growth_rebuild else "legacy",
                        line_km=3.0 if growth_rebuild else 2.5,
                        capacity_first=scheme == "rigid" and not growth_rebuild,
                        preserve_baseline_forward_margin=growth_rebuild,
                        policy_peak_basis="rolling_max" if growth_rebuild else "annual",
                        max_storage_modules=50 if growth_rebuild else 10,
                        tie_year_basis="annual_station_scaled" if growth_rebuild else "2025_only",
                        canonicalize_tie_dispatch=growth_rebuild,
                        preserve_prior_year_forward_margin=False,
                        require_existing_tie_operation=not growth_rebuild)
                    status = "feasible_optimum"
                    detail = ""
                except ValueError as exc:
                    if "infeasible" not in str(exc).lower():
                        raise
                    results[scheme] = None
                    status = "infeasible_under_annual_clr_and_capacity_constraints"
                    detail = str(exc)
                feasibility.append({"scenario_id": scenario_id, "study_region_id": layer[0],
                                    "voltage_kv": layer[1], "scheme": scheme,
                                    "status": status, "solver_detail": detail})
            rigid_cost = (results["rigid"][3]["objective_npv_10k_cny"]
                          if results["rigid"] else None)
            elastic_cost = (results["elastic"][3]["objective_npv_10k_cny"]
                            if results["elastic"] else None)
            if rigid_cost is None and elastic_cost is None:
                preferred = "neither_feasible"
            elif rigid_cost is None:
                preferred = "elastic_only_feasible"
            elif elastic_cost is None:
                preferred = "rigid_only_feasible"
            else:
                preferred = "rigid" if rigid_cost < elastic_cost - 1e-5 else (
                    "elastic" if elastic_cost < rigid_cost - 1e-5 else "cost_tie")
            for scheme, result in results.items():
                if result is None:
                    continue
                stations, years, ties, summary = result
                for row in years:
                    year = row["year"]
                    forward_ties = sum(float(t["transfer_mw"]) for t in ties
                                       if t["year"] == year and t["scenario"] == "forward")
                    matrix.append({
                        "scenario_id": scenario_id, "scenario_family": family,
                        "study_region_id": layer[0], "voltage_kv": layer[1], "year": year,
                        "scheme": scheme, "preferred_scheme_by_full_path_cost": preferred,
                        "source_load_ratio_2025_region_shared_proxy": round(source_ratio[layer[0]] * source_scale, 8),
                        "source_ratio_scope": "region_shared_2025_proxy_not_voltage_specific",
                        "net_peak_mw": row["synchronous_forward_peak_mw"],
                        "net_peak_growth_from_2021_fraction": round(float(row["synchronous_forward_peak_mw"]) / peak_2021[layer] - 1, 8),
                        "net_peak_cagr_from_2021_fraction": round(
                            (float(row["synchronous_forward_peak_mw"]) / peak_2021[layer]) ** (1 / (year - 2021)) - 1, 8),
                        "transformer_cost_scale": transformer_price,
                        "storage_cost_scale": storage_price,
                        "normalized_transformer_to_storage_price_scale": round(transformer_price / storage_price, 6),
                        "forward_h95_hours_2025_template": h95_template[layer],
                        "forward_h95_scenario_hours": round(h95_template[layer] * duration_scale),
                        "h95_status": "2025_template_simulation_not_target_year_observation",
                        "tie_transfer_limit_scale": tie_scale,
                        "forward_d95_duration_scale": duration_scale,
                        "reverse_peak_scale": reverse_scale,
                        "simulated_capacity_mva": row["selected_capacity_mva"],
                        "simulated_clr": row["actual_clr"],
                        "policy_control_peak_mw": row["policy_control_peak_mw"],
                        "policy_control_clr": row["policy_control_clr"],
                        "storage_modules_in_service": row["storage_modules_in_service"],
                        "forward_tie_transfer_mw": round(forward_ties, 6),
                        "new_line_built": row["line_built"],
                        "scheme_full_path_npv_10k_cny": summary["objective_npv_10k_cny"],
                        "cost_advantage_rigid_minus_elastic_10k_cny": (
                            round(rigid_cost - elastic_cost, 8)
                            if rigid_cost is not None and elastic_cost is not None else ""),
                        "matrix_status": ("growth_rebuild_pending_new_line_and_cost_review"
                                          if growth_rebuild else "conditional_simulation_not_universal_empirical_recommendation"),
                    })
    prefix = "growth_conditional" if growth_rebuild else "planning_conditional"
    write_csv(feasibility, output_dir / f"{prefix}_feasibility.csv")
    return matrix, inventory


def main() -> None:
    matrix, inventory = build_scan()
    write_csv(matrix, OUTPUT_DIR / "planning_conditional_matrix.csv")
    write_csv(inventory, OUTPUT_DIR / "planning_conditional_scenarios.csv")
    print(f"写入 {len(inventory)} 个条件情景、{len(matrix)} 条年度方案")


if __name__ == "__main__":
    main()
