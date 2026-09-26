"""把刚性/弹性年度路径与既有联络规划运行校核写成可复核的基准包。"""

from pathlib import Path
from itertools import combinations_with_replacement

from .baseline_2021 import read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .joint_lifecycle_optimizer import (
    EXISTING_OPERATIONAL_DIRECTION, EXISTING_PATH_CAP_MW,
    EXISTING_OPERATIONAL_TIE, RIGID_2025_FORWARD_OPERATION_MW,
    cost_factors, load_inputs, solve_layer,
)
from .pizhou_existing_ties import build_feeder_headroom
from .tie_section_audit import transferable_section


PLANNING_STATION = ("QX-00005", 110, "BDZ-00027")
PLANNING_UNITS = (20.0, 40.0)


def solve_planning_cases(output_dir: Path = OUTPUT_DIR) -> list[dict]:
    """两方案共用 2021 规划起点；仅调整有已核实跨站联络的墩集变。"""
    output_dir = Path(output_dir)
    write_csv([transferable_section()], output_dir / "planning_10kv_transferable_section_audit.csv")
    baseline, scene, durations, peaks, catalog, coefficients = load_inputs()
    original = baseline[PLANNING_STATION]
    if (float(original["simulation_unit_1_mva"]),
            float(original["simulation_unit_2_mva"])) != (20.0, 50.0):
        raise ValueError("墩集变原始规划起点已变化，需重新审查站级分配")
    peak_2021 = float(original["estimated_forward_peak_mw_2021"])
    planning_peak = max([peak_2021] + [float(scene[PLANNING_STATION, y]["estimated_station_forward_peak_mw"])
                                       for y in (2022, 2023, 2024)])
    feasible_pairs = [p for p in combinations_with_replacement(catalog[PLANNING_STATION[:2]], 2)
                      if .95 * sum(p) >= planning_peak]
    if sum(PLANNING_UNITS) != min(sum(p) for p in feasible_pairs):
        raise ValueError("60 MVA 已非覆盖 2021—2024 年正向峰值的最小双主变容量")
    baseline[PLANNING_STATION] = dict(original,
                                      simulation_unit_1_mva=PLANNING_UNITS[0],
                                      simulation_unit_2_mva=PLANNING_UNITS[1],
                                      simulation_capacity_mva_2021=sum(PLANNING_UNITS),
                                      baseline_selection_rule="minimum_discrete_capacity_covering_2021_to_2024_backcast_common_to_both_schemes")
    write_csv(sorted(baseline.values(), key=lambda r: (r["study_region_id"], int(r["voltage_kv"]),
                                                     r["model_station_id"])),
              output_dir / "planning_2021_common_baseline_stations.csv")
    layer_baseline = read_csv(OUTPUT_DIR / "baseline_2021_layer_check.csv")
    layer_audit = []
    for row in layer_baseline:
        key = row["study_region_id"], int(row["voltage_kv"])
        capacity = sum(float(r["simulation_capacity_mva_2021"]) for s, r in baseline.items() if s[:2] == key)
        peak = float(row["estimated_district_peak_mw_2021"])
        if capacity / peak > 2 + 1e-9:
            raise ValueError(f"{key} 共同起点容载比超出 2.0")
        layer_audit.append({"study_region_id": key[0], "voltage_kv": key[1], "year": 2021,
                            "station_count": sum(s[:2] == key for s in baseline),
                            "capacity_mva": capacity, "net_forward_peak_mw": peak,
                            "simulated_clr": round(capacity / peak, 9),
                            "status": "counterfactual_common_planning_baseline"})
    write_csv(layer_audit, output_dir / "planning_2021_common_baseline_layers.csv")
    write_csv([
        {"candidate_id": "T01/TIE-002", "from_feeder_id": "PZXL-00092",
         "to_feeder_id": "PZXL-00161", "connection": "墩南线—河炮线",
         "normal_state": "OPEN", "shared_feeder_group": "PZXL-00161",
         "baseline_status": "enabled_switch28_whole_section_planning_simulation",
         "reason": "原PDF有墩南线28开关；逐段拓扑切出136节点，节点负荷种子4.49651196MW；旧路径包络4.75MW；下游潮流待核",
         "source": "10kv_case/source/10kv.7z::邳州_10kVdnan线.pdf; 10kv_case/data/physical_edges.csv; node_load_seed_pf095.csv"},
        {"candidate_id": "T02/TIE-001", "from_feeder_id": "PZXL-00099",
         "to_feeder_id": "PZXL-00154", "connection": "墩振线—河东线",
         "normal_state": "OPEN", "shared_feeder_group": "PZXL-00099,PZXL-00154",
         "baseline_status": "excluded_endpoint_unresolved",
         "reason": "送侧R005等图纸断点，端点未闭合；不得定量叠加",
         "source": "10kv_case/data/tie_master.csv; 10kv_case_reanalysis.md"},
        {"candidate_id": "T03/TIE-003", "from_feeder_id": "PZXL-00097",
         "to_feeder_id": "PZXL-00161", "connection": "墩西线—河炮线",
         "normal_state": "OPEN", "shared_feeder_group": "PZXL-00161",
         "baseline_status": "excluded_device_chain_unresolved",
         "reason": "与T01共用河炮线余量；河炮侧R020设备链未闭合",
         "source": "10kv_case/data/tie_master.csv; 10kv_case_reanalysis.md"},
        {"candidate_id": "NEWTIE-BDZ00027-BDZ00048-01",
         "from_feeder_id": "PZXL-00099", "to_feeder_id": "PZXL-00154",
         "connection": "墩振线—河东线新建候选，约2.5km",
         "normal_state": "NOT_BUILT", "shared_feeder_group": "PZXL-00099,PZXL-00154",
         "baseline_status": "excluded_route_and_cost_unverified",
         "reason": "旧候选走廊已恢复到代码；路径、开关和工程费用未闭合",
         "source": "10kv_case/new_tie_candidates.csv; 10kv_case_reanalysis.md"},
    ], output_dir / "planning_multiterminal_candidate_register.csv")
    audit = [{"study_region_id": PLANNING_STATION[0], "voltage_kv": 110,
              "model_station_id": PLANNING_STATION[2], "year": 2021,
              "original_units_mva": "20+50", "planning_units_mva": "20+40",
              "original_capacity_mva": 70, "planning_capacity_mva": 60,
              "peak_2021_mw": peak_2021,
              "forward_margin_2021_mw": round(.95 * 60 - peak_2021, 6),
              "planning_peak_2021_to_2024_mw": round(planning_peak, 6),
              "reason": "回看覆盖2021至2024年正向峰值的最小双主变容量；两方案同起点",
              "historical_status": "counterfactual_planning_capacity_not_2021_asset_record"}]
    write_csv(audit, output_dir / "planning_2021_common_baseline_adjustment.csv")
    factors = cost_factors()
    layers = sorted({s[:2] for s in baseline})
    for scheme, cap in (("rigid", 2.0), ("elastic", 2.4)):
        outputs = ([], [], [], [])
        for layer in layers:
            result = solve_layer(layer, baseline, scene, durations, peaks, catalog,
                                 coefficients, factors, cap, scheme == "rigid",
                                 capacity_first=scheme == "rigid")
            for target, rows in zip(outputs, result):
                target.extend(rows if isinstance(rows, list) else [rows])
        for row in outputs[0]:
            row["capacity_kind"] = "counterfactual_simulated_capacity_not_asset_record"
            source = baseline[row["study_region_id"], row["voltage_kv"], row["model_station_id"]]
            row["observed_2025_asset_capacity_mva"] = (
                source["source_capacity_mva_2025"] if row["year"] == 2025 else "")
        for row in outputs[1]:
            row["clr_kind"] = "ratio_of_simulated_capacity_to_modeled_net_peak"
            row["recommendation_status"] = "not_released_pending_guideline_and_transfer_validation"
        for row in outputs[3]:
            row["guide_verification_status"] = "static_screen_only_not_full_guide_assessment"
            row["recommendation_status"] = "not_released"
        for name, rows in zip(("stations", "years", "ties", "layers"), outputs):
            path = output_dir / f"planning_{scheme}_{name}.csv"
            if rows:
                write_csv(rows, path)
            elif name == "ties":
                import csv
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("w", newline="", encoding="utf-8-sig") as f:
                    csv.writer(f).writerow(("study_region_id", "voltage_kv", "year", "scenario",
                                            "tie_id", "donor_feeder_id", "receiver_feeder_id",
                                            "donor_station_id", "receiver_station_id", "transfer_mw",
                                            "operation_basis", "technical_scope"))
    without_tie = solve_layer(PLANNING_STATION[:2], baseline, scene, durations, peaks,
                              catalog, coefficients, factors, 2.0, True, tie_allowed=False,
                              capacity_first=True)
    for name, rows in zip(("stations", "years", "layers"),
                          (without_tie[0], without_tie[1], [without_tie[3]])):
        write_csv(rows, output_dir / f"planning_rigid_no_tie_{name}.csv")
    with_tie = next(r for r in read_csv(output_dir / "planning_rigid_layers.csv")
                    if r["study_region_id"] == "QX-00005" and r["voltage_kv"] == "110")
    without_cost = float(without_tie[3]["objective_npv_10k_cny"])
    write_csv([{"study_region_id": "QX-00005", "voltage_kv": 110,
                "rigid_with_tie_npv_10k_cny": with_tie["objective_npv_10k_cny"],
                "rigid_no_tie_npv_10k_cny": round(without_cost, 8),
                "modeled_saving_10k_cny": round(without_cost - float(with_tie["objective_npv_10k_cny"]), 8),
                "comparison": "same_2021_baseline_same_R_cap_same_prices_only_tie_permission_changes",
                "evidence_level": "planning_static_proxy_not_realized_operational_saving"}],
              output_dir / "planning_tie_attribution.csv")
    return audit


def build_package(output_dir: Path = OUTPUT_DIR) -> tuple[list[dict], list[dict]]:
    output_dir = Path(output_dir)
    combined = []
    for scheme in ("rigid", "elastic"):
        years = read_csv(output_dir / f"planning_{scheme}_years.csv")
        ties_path = output_dir / f"planning_{scheme}_ties.csv"
        ties = read_csv(ties_path) if ties_path.exists() else []
        for row in years:
            matched = [t for t in ties if t["study_region_id"] == row["study_region_id"]
                       and t["voltage_kv"] == row["voltage_kv"]
                       and t["year"] == row["year"] and t["scenario"] == "forward"]
            combined.append({
                "scheme": scheme, "study_region_id": row["study_region_id"],
                "voltage_kv": row["voltage_kv"], "year": row["year"],
                "station_count": row["station_count"],
                "synchronous_forward_peak_mw": row["synchronous_forward_peak_mw"],
                "selected_capacity_mva": row["selected_capacity_mva"],
                "simulated_clr": row["actual_clr"], "clr_cap": row["clr_cap"],
                "capacity_kind": "counterfactual_simulated_capacity_not_asset_record",
                "storage_modules_in_service": row["storage_modules_in_service"],
                "forward_tie_transfer_mw": round(sum(float(t["transfer_mw"]) for t in matched), 6),
                "new_line_built": row["line_built"],
                "year_lifecycle_npv_10k_cny": row["year_lifecycle_npv_10k_cny"],
                "status": "planning_case_not_recommendation_matrix",
            })
    rigid_ties = read_csv(output_dir / "planning_rigid_ties.csv")
    operation = [r for r in rigid_ties if r["tie_id"] == EXISTING_OPERATIONAL_TIE
                 and r["year"] == "2025" and r["scenario"] == "forward"
                 and (r["donor_feeder_id"], r["receiver_feeder_id"]) == EXISTING_OPERATIONAL_DIRECTION]
    if len(operation) != 1 or float(operation[0]["transfer_mw"]) < RIGID_2025_FORWARD_OPERATION_MW - 1e-6:
        raise ValueError("刚性方案未按规划运行目标形成既有联络转供")
    feeder = {r["feeder_id"]: r for r in build_feeder_headroom()}
    donor, receiver = (feeder[k] for k in EXISTING_OPERATIONAL_DIRECTION)
    stations = {r["model_station_id"]: r for r in read_csv(output_dir / "planning_rigid_stations.csv")
                if r["study_region_id"] == "QX-00005" and r["voltage_kv"] == "110"
                and r["year"] == "2025"}
    amount = float(operation[0]["transfer_mw"])
    source = stations[donor["station_id"]]
    host = stations[receiver["station_id"]]
    actual_assets = {r["model_station_id"]: float(r["source_capacity_mva_2025"])
                     for r in read_csv(output_dir / "planning_2021_common_baseline_stations.csv")
                     if r["study_region_id"] == "QX-00005" and r["voltage_kv"] == "110"}
    source_post = float(source["forward_screen_mw"]) - amount
    host_post = float(host["forward_screen_mw"]) + amount
    donor_forward_limit = .95 * float(source["selected_capacity_mva"])
    minimum_required_transfer = max(float(source["forward_screen_mw"]) - donor_forward_limit, 0)
    bounds = [float(donor["current_equivalent_active_power_mw"]),
              float(receiver["receiving_current_headroom_mw"]), EXISTING_PATH_CAP_MW]
    if amount > min(bounds) + 1e-6 or source_post > .95 * float(source["selected_capacity_mva"]) + 1e-6 \
            or host_post > .95 * float(host["selected_capacity_mva"]) + 1e-6:
        raise ValueError("2025 年既有联络运行目标越过静态容量包络")
    elastic_station = next(r for r in read_csv(output_dir / "planning_elastic_stations.csv")
                           if r["study_region_id"] == "QX-00005" and r["voltage_kv"] == "110"
                           and r["model_station_id"] == donor["station_id"] and r["year"] == "2025")
    no_tie_station = next(r for r in read_csv(output_dir / "planning_rigid_no_tie_stations.csv")
                          if r["model_station_id"] == donor["station_id"] and r["year"] == "2025")
    difference_vs_elastic = float(elastic_station["selected_capacity_mva"]) - float(source["selected_capacity_mva"])
    avoided_by_tie = float(no_tie_station["selected_capacity_mva"]) - float(source["selected_capacity_mva"])
    feasibility = [{
        "year": 2025, "scenario": "forward", "tie_id": EXISTING_OPERATIONAL_TIE,
        "old_case_id": "TIE-002", "donor_feeder_id": donor["feeder_id"],
        "receiver_feeder_id": receiver["feeder_id"],
        "donor_station_id": donor["station_id"], "receiver_station_id": receiver["station_id"],
        "required_planning_transfer_mw": RIGID_2025_FORWARD_OPERATION_MW,
        "minimum_transfer_to_avoid_upgrade_mw": round(minimum_required_transfer, 6),
        "optimized_transfer_mw": amount,
        "donor_source_end_power_proxy_mw": bounds[0],
        "receiver_source_end_headroom_mw": bounds[1],
        "old_case_path_envelope_mw": bounds[2],
        "static_transfer_upper_mw": min(bounds),
        "source_pdf_section_switch": "dnan线28开关",
        "source_pdf_switch_open_for_transfer": "YES_SIMULATED_OPERATION",
        "downstream_section_node_count": transferable_section()["section_node_count"],
        "downstream_allocated_feeder_stress_load_mw": RIGID_2025_FORWARD_OPERATION_MW,
        "transfer_control": "binary_whole_section_not_continuously_dispatchable",
        "minimum_required_fraction_of_static_upper": round(minimum_required_transfer / min(bounds), 6),
        "planned_fraction_of_static_upper": round(amount / min(bounds), 6),
        "station_net_peak_trigger_mw": round(donor_forward_limit, 6),
        "max_station_net_peak_with_planned_transfer_mw": round(donor_forward_limit + amount, 6),
        "max_station_net_peak_with_available_section_mw": round(donor_forward_limit + amount, 6),
        "donor_station_forward_peak_before_mw": source["forward_screen_mw"],
        "donor_station_forward_peak_after_mw": round(source_post, 6),
        "receiver_station_forward_peak_before_mw": host["forward_screen_mw"],
        "receiver_station_forward_peak_after_mw": round(host_post, 6),
        "donor_station_forward_margin_after_mw": round(.95 * float(source["selected_capacity_mva"]) - source_post, 6),
        "receiver_station_forward_margin_after_mw": round(.95 * float(host["selected_capacity_mva"]) - host_post, 6),
        "donor_station_simulated_capacity_mva": source["selected_capacity_mva"],
        "donor_station_observed_2025_asset_capacity_mva": actual_assets[donor["station_id"]],
        "receiver_station_simulated_capacity_mva": host["selected_capacity_mva"],
        "receiver_station_observed_2025_asset_capacity_mva": actual_assets[receiver["station_id"]],
        "simulated_station_forward_deficit_before_tie_mw": round(minimum_required_transfer, 6),
        "observed_asset_station_forward_deficit_proxy_mw": round(max(float(source["forward_screen_mw"]) - .95 * actual_assets[donor["station_id"]], 0), 6),
        "capacity_difference_vs_elastic_mva": round(difference_vs_elastic, 6),
        "avoided_capacity_vs_same_rigid_no_tie_mva": round(avoided_by_tie, 6),
        "evidence_level": "source_pdf_switch_and_topology_load_seed_static_screen_downstream_voltage_and_branch_flow_unverified",
        "operation_status": "simulated_dispatch_not_observed_operation",
    }]
    trigger_rows = []
    for row in read_csv(output_dir / "planning_rigid_stations.csv"):
        if row["study_region_id"] != "QX-00005" or row["voltage_kv"] != "110" \
                or row["model_station_id"] not in (donor["station_id"], receiver["station_id"]):
            continue
        for scenario, factor, demand_key in (("forward", .95, "forward_screen_mw"),
                                              ("reverse", .8 * .95, "reverse_screen_mw")):
            limit = factor * float(row["selected_capacity_mva"])
            demand = float(row[demand_key])
            deficit = max(demand - limit, 0)
            shifts = [r for r in rigid_ties if r["year"] == row["year"]
                      and r["scenario"] == scenario]
            outgoing = sum(float(r["transfer_mw"]) for r in shifts
                           if r["donor_station_id"] == row["model_station_id"])
            incoming = sum(float(r["transfer_mw"]) for r in shifts
                           if r["receiver_station_id"] == row["model_station_id"])
            trigger_rows.append({
                "year": row["year"], "scenario": scenario,
                "model_station_id": row["model_station_id"],
                "simulated_capacity_mva": row["selected_capacity_mva"],
                "modeled_net_peak_mw": demand, "screen_power_factor_or_reverse_factor": factor,
                "station_screen_limit_mw": round(limit, 6),
                "pre_tie_station_deficit_mw": round(deficit, 6),
                "planned_outgoing_tie_mw": round(outgoing, 6),
                "planned_incoming_tie_mw": round(incoming, 6),
                "post_tie_station_margin_mw": round(limit - demand + outgoing - incoming, 6),
                "trigger_status": "conditional_tie_needed" if deficit > 1e-9 else "no_station_deficit",
                "evidence_gate": ("section_load_allocated_at_feeder_stress_not_synchronous_station_peak_downstream_flow_unverified"
                                  if outgoing > 0 else "not_applicable"),
                "formula_origin": ("electrical_station_forward_balance_research_rule"
                                   if scenario == "forward" else "DLT2041_2025_section_6_3_derived_reverse_screen_only"),
            })
    write_csv(trigger_rows, output_dir / "planning_10kv_transfer_trigger.csv")
    return combined, feasibility


def main() -> None:
    solve_planning_cases()
    combined, feasibility = build_package()
    write_csv(combined, OUTPUT_DIR / "planning_rigid_elastic_annual_baseline.csv")
    write_csv(feasibility, OUTPUT_DIR / "planning_10kv_tie_feasibility.csv")
    print(f"已写入 {len(combined)} 条年度方案和 {len(feasibility)} 条联络校核")


if __name__ == "__main__":
    main()
