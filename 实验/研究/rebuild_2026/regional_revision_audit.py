"""从落盘明细独立核对区域规划结果的容量、转移和成本。"""

import json
from collections import defaultdict
from pathlib import Path

from .annual_no_tie_investment_submodel import storage_effective_power_per_module
from .baseline_2021 import read_csv
from .joint_lifecycle_optimizer import load_inputs
from .regional_revision_run import OUTPUT, LINE_CAPACITY_MW
from .planning_load_profile import apply_pizhou_weighted_growth


def audit(directory: Path = OUTPUT) -> dict:
    directory = Path(directory)
    annual = read_csv(directory / "annual_measures.csv")
    assumptions_file = directory / "assumptions.json"
    assumptions = json.loads(assumptions_file.read_text(encoding="utf-8")) if assumptions_file.exists() else {}
    line_capacity = float(assumptions.get("new_line_capacity_mw_each", LINE_CAPACITY_MW))
    line_capacity_by_year = assumptions.get("line_capacity_mw_by_year") or {}
    existing_capacity = assumptions.get("existing_transfer_capacity_mw")
    existing_capacity_by_year = assumptions.get("existing_transfer_capacity_mw_by_year") or {}
    existing_pair = assumptions.get("existing_station_pair")
    new_pair = assumptions.get("new_line_station_pair")
    pairwise = bool(assumptions.get("pairwise_transfer"))
    minimum_clr = assumptions.get("minimum_clr_by_year") or {}
    margin_fraction = float(assumptions.get("baseline_margin_fraction", 1.0))
    summaries = {r["case_id"]: r for r in read_csv(directory / "summary.csv")}
    initial_file = directory / "initial_state_2021.csv"
    initial = {(r["study_region_id"], int(r["voltage_kv"]), r["model_station_id"]): r
               for r in read_csv(initial_file)} if initial_file.exists() else {}
    for start in initial.values():
        capacity = float(start["simulation_capacity_mva"])
        assert .95 * capacity + 1e-5 >= float(start["estimated_forward_peak_mw"])
        assert .8 * .95 * capacity + 1e-5 >= float(start["estimated_reverse_screen_mw"])
    _, scenes, durations, peaks, _, _ = load_inputs()
    if assumptions.get("load_scenario") == "weighted_4y_growth":
        baseline_for_growth = {key: dict(value,
                              estimated_forward_peak_mw_2021=value["estimated_forward_peak_mw"])
                               for key, value in initial.items()}
        scenes, peaks, _, _ = apply_pizhou_weighted_growth(baseline_for_growth, scenes, peaks)
    checked = 0
    for case in summaries:
        stations = read_csv(directory / f"{case}_stations.csv")
        transfer_file = directory / f"{case}_transfers.csv"
        transfers = read_csv(transfer_file) if transfer_file.exists() else []
        by_year = {int(r["year"]): r for r in annual if r["case_id"] == case}
        assert len(by_year) == 4
        prior_built_pairs = set()
        assert abs(sum(float(r["year_lifecycle_npv_10k_cny"]) for r in by_year.values()) -
                   float(summaries[case]["objective_npv_10k_cny"])) < 1e-3
        fraction = float(summaries[case]["initial_transfer_fraction"])
        maximum = float(summaries[case]["maximum_transfer_fraction"])
        for year, row in by_year.items():
            local = [r for r in stations if int(r["year"]) == year]
            assert len(local) == int(row["station_count"])
            capacity = sum(float(r["selected_capacity_mva"]) for r in local)
            assert abs(capacity - float(row["selected_capacity_mva"])) < 1e-5
            assert abs(capacity / float(row["net_peak_mw"]) - float(row["clr"])) < 1e-8
            assert float(row["clr"]) <= float(summaries[case]["clr_cap"]) + 1e-7
            lower_clr = float(minimum_clr.get(str(year), minimum_clr.get(year, 0.0)))
            if case == "pizhou_elastic_target" and year == 2025:
                lower_clr = max(lower_clr, float(assumptions.get("elastic_target_2025_clr") or 0.0))
            assert float(row["clr"]) + 1e-7 >= lower_clr
            assert abs(float(row["net_peak_mw"]) - peaks[(row["study_region_id"], 110, year)]) < 1e-5
            annual_ties = [t for t in transfers if int(t["year"]) == year]
            if pairwise:
                built_pairs = {tuple(sorted((t["donor_station_id"], t["receiver_station_id"])))
                               for t in annual_ties if t["scenario"] == "infrastructure"
                               and t["tie_id"] == "REGIONAL-new-build"}
                assert len(built_pairs) == int(row["new_lines_in_service"])
                assert prior_built_pairs <= built_pairs
                assert len(built_pairs - prior_built_pairs) == int(row["new_lines_commissioned"])
                prior_built_pairs = built_pairs
            for scenario in ("forward", "reverse"):
                for kind in ("existing", "new"):
                    kind_rows = [t for t in annual_ties if t["scenario"] == scenario
                                 and t["tie_id"] == f"REGIONAL-{kind}"]
                    if pairwise:
                        sent = sum(float(t["transfer_mw"]) for t in kind_rows)
                        by_pair = defaultdict(float)
                        for tie in kind_rows:
                            assert tie["donor_station_id"] != tie["receiver_station_id"]
                            by_pair[tuple(sorted((tie["donor_station_id"],
                                                  tie["receiver_station_id"])))] += float(tie["transfer_mw"])
                    else:
                        sent = sum(float(t["transfer_mw"]) for t in kind_rows
                                   if t["receiver_station_id"] == "REGIONAL-HUB")
                        received = sum(float(t["transfer_mw"]) for t in kind_rows
                                       if t["donor_station_id"] == "REGIONAL-HUB")
                        assert abs(sent - received) < 1e-4
                    expected = float(row[f"{'existing_transfer' if kind == 'existing' else 'new_line_transfer'}_{scenario}_mw"])
                    assert abs(sent - expected) < 1e-4
                    if kind == "new":
                        limit = float(line_capacity_by_year.get(str(year), line_capacity_by_year.get(year, line_capacity)))
                        assert sent <= int(row["new_lines_in_service"]) * limit + 1e-5
                        if pairwise:
                            assert len(by_pair) <= int(row["new_lines_in_service"])
                            assert all(value <= limit + 1e-5 for value in by_pair.values())
                            assert set(by_pair) <= built_pairs
                    elif existing_capacity is not None:
                        limit = float(existing_capacity_by_year.get(str(year), existing_capacity_by_year.get(year, existing_capacity)))
                        assert sent <= limit + 1e-5
                    pair = existing_pair if kind == "existing" else new_pair
                    if pair and row["study_region_id"] == "QX-00005":
                        if pairwise:
                            assert all({t["donor_station_id"], t["receiver_station_id"]} == set(pair)
                                       for t in kind_rows)
                        else:
                            assert all(t["donor_station_id"] in pair for t in kind_rows
                                       if t["receiver_station_id"] == "REGIONAL-HUB"
                                       and float(t["transfer_mw"]) > 1e-5)
                            assert all(t["receiver_station_id"] in pair for t in kind_rows
                                       if t["donor_station_id"] == "REGIONAL-HUB"
                                       and float(t["transfer_mw"]) > 1e-5)
            for station in local:
                key = (row["study_region_id"], 110, station["model_station_id"])
                selected_capacity = float(station["selected_capacity_mva"])
                modules = int(station["storage_modules_in_service"])
                if summaries[case].get("baseline_mode") in ("planning_2021", "near2_2021"):
                    assert key in initial
                    assert float(station["selected_unit_1_mva"]) + 1e-6 >= float(station["prior_unit_1_mva"])
                    assert float(station["selected_unit_2_mva"]) + 1e-6 >= float(station["prior_unit_2_mva"])
                    if year == 2022:
                        assert abs(float(station["prior_unit_1_mva"]) -
                                   float(initial[key]["simulation_unit_1_mva"])) < 1e-6
                        assert abs(float(station["prior_unit_2_mva"]) -
                                   float(initial[key]["simulation_unit_2_mva"])) < 1e-6
                for scenario in ("forward", "reverse"):
                    field = "estimated_station_forward_peak_mw" if scenario == "forward" else "reverse_screen_mw"
                    demand = float(scenes[key, year][field])
                    duration = int(durations[key][f"{scenario}_d95_max_run_hours"])
                    factor = .95 if scenario == "forward" else .8 * .95
                    outgoing, incoming = 0.0, 0.0
                    for tie in annual_ties:
                        if tie["scenario"] != scenario:
                            continue
                        flow = float(tie["transfer_mw"])
                        if tie["donor_station_id"] == key[2]:
                            outgoing += flow
                        if tie["receiver_station_id"] == key[2]:
                            incoming += flow
                        if tie["donor_station_id"] == key[2]:
                            if not pairwise:
                                bound_fraction = fraction if tie["tie_id"] == "REGIONAL-existing" else maximum - fraction
                                assert flow <= bound_fraction * max(0.0, demand) + 1e-5
                    if pairwise:
                        assert outgoing <= max(0.0, demand) + 1e-5
                    margin = 0.0
                    if scenario == "forward" and summaries[case].get("preserve_baseline_forward_margin") in ("True", True):
                        start = initial[key]
                        margin = margin_fraction * max(0.0, .95 * float(start["simulation_capacity_mva"]) -
                                                        float(start["estimated_forward_peak_mw"]))
                    assert factor * selected_capacity + modules * storage_effective_power_per_module(duration) + outgoing - incoming >= demand + margin - 1e-4
                    checked += 1
    result = {"status": "PASS", "cases": len(summaries), "annual_rows": len(annual),
              "station_scenario_constraints_checked": checked,
              "scope": "station_aggregate_static_scenarios_and_lifecycle_cost_reconstruction"}
    (directory / "audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                                           encoding="utf-8")
    return result


if __name__ == "__main__":
    print(audit())
