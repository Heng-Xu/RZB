"""从 CSV 重算区域静态规划的逐站承载、措施和全寿命费用。"""

import json
from collections import defaultdict
from pathlib import Path

from .baseline_2021 import read_csv
from .joint_lifecycle_optimizer import cost_factors
from .regional_static_milp_v2 import (
    LINE_MW_2025, OUTPUT, STORAGE_MWH_PER_MW, STORAGE_MODULE_MWH, input_data,
)
from .station_grid_feasibility import AREA_RATINGS, grid_candidate_rows, station_metadata
from .station_transfer_equivalent import capacity_from_station_rate, new_line_increment_reference


def audit(directory: Path = OUTPUT) -> dict:
    directory = Path(directory)
    summaries = json.loads((directory / "summary.json").read_text(encoding="utf-8"))
    factors = cost_factors()
    results = []
    for summary in summaries:
        load_reallocation = summary.get("transfer_mode") == "load_reallocation"
        station_equivalent = summary.get("transfer_capacity_model") == "station_rate_equivalent"
        scheme = summary["scheme"]
        region = (summary["region_id"], int(summary["voltage_kv"]))
        years = read_csv(directory / f"{scheme}_years.csv")
        stations = read_csv(directory / f"{scheme}_stations.csv")
        transfer_file = directory / f"{scheme}_transfers.csv"
        transfers = read_csv(transfer_file) if transfer_file.exists() else []
        line_file = directory / f"{scheme}_new_lines.csv"
        lines = read_csv(line_file) if line_file.exists() else []
        outage_file = directory / f"{scheme}_outage_flows.csv"
        outages = read_csv(outage_file) if outage_file.exists() else []
        if load_reallocation:
            assert not outages, "正常负荷转接结果不得含事故恢复量"
            if not station_equivalent:
                assert summary["installed_transfer_target_enforced"] is False
        baseline, scenes, durations, peaks, _, _ = input_data(
            summary["load_scenario"], region, summary.get("city_baseline_cap_mva"))
        physical = station_metadata({station[2] for station in baseline})
        grid_pairs = {(row["station_a"], row["station_b"]): row for row in
                      grid_candidate_rows(set(physical))}
        if summary.get("annual_growth_rate_scenario") is not None:
            scenes, peaks = dict(scenes), dict(peaks)
            growth = float(summary["annual_growth_rate_scenario"])
            for year in (2022, 2023, 2024, 2025):
                factor = (1 + growth) ** (year - 2021)
                peaks[region + (year,)] = peaks[region + (2021,)] * factor
                for station in baseline:
                    row = dict(scenes[station, year])
                    row["estimated_station_forward_peak_mw"] = (
                        float(baseline[station]["estimated_forward_peak_mw_2021"]) * factor)
                    scenes[station, year] = row
        if summary.get("source_load_ratio_scenario") is not None:
            scenes = dict(scenes)
            multiplier = float(summary["source_load_ratio_scenario"]) / 1.630652935
            for station in baseline:
                for year in (2022, 2023, 2024, 2025):
                    row = dict(scenes[station, year])
                    row["reverse_screen_mw"] = float(row["reverse_screen_mw"]) * multiplier
                    scenes[station, year] = row
        by_station = {(r["year"], r["station"]): r for r in stations}
        assert len(years) == 4 and len(stations) == 4 * len(baseline)
        assert len(by_station) == len(stations)
        lines_by_pair = {tuple(sorted((r["station_a"], r["station_b"]))): int(r["commissioning_year"])
                         for r in lines}
        if station_equivalent:
            assert len({r["project_id"] for r in lines}) == len(lines)
            assert all(r["station_a"] != r["station_b"] for r in lines)
            assert all(r["route_status"] == "endpoint_pairing_for_unit_accounting_not_optimized_route"
                       for r in lines)
            reference_increment = new_line_increment_reference()["new_line_increment_mw"]
            assert abs(float(summary["new_line_increment_mw"]) - reference_increment) < 1e-8
            assert all(abs(float(r["screen_capacity_mw_2025"]) - reference_increment) < 1e-8
                       for r in lines)
            assert all(abs(float(r["construction_capex_10k"]) -
                           float(summary["line_price_10k_per_planned_pair"]) *
                           float(summary.get("line_scale", 1))) < 1e-6 for r in lines)
        else:
            assert len(lines_by_pair) == len(lines)
        if summary.get("use_shared_grid_candidates"):
            assert all(pair in grid_pairs for pair in lines_by_pair)
        if summary.get("require_both_spare_bays"):
            assert all(grid_pairs[pair]["both_have_spare_bay"] for pair in lines_by_pair)
        if scheme == "elastic" and not summary.get("elastic_allow_line_decisions"):
            assert not transfers and not lines
        previous_capacity = {station[2]: tuple(float(baseline[station][f"simulation_unit_{slot}_mva"])
                                               for slot in (1, 2)) for station in baseline}
        previous_energy = defaultdict(float)
        previous_third = defaultdict(float)
        total_cost = 0.0
        checked = 0
        for year_row in years:
            year = int(year_row["year"])
            local = [r for r in stations if int(r["year"]) == year]
            local_transfer = [r for r in transfers if int(r["year"]) == year]
            built_records = [r for r in lines if int(r["commissioning_year"]) <= year]
            built_now = ({r["project_id"] for r in built_records} if station_equivalent else
                         {pair for pair, first in lines_by_pair.items() if first <= year})
            newly_built = ({r["project_id"] for r in lines if int(r["commissioning_year"]) == year}
                          if station_equivalent else
                          {pair for pair, first in lines_by_pair.items() if first == year})
            assert len(built_now) == int(year_row["new_lines_in_service"])
            assert len(newly_built) == int(year_row["new_lines_commissioned"])
            assert abs(float(year_row["line_capex_10k"]) -
                       sum(float(r["construction_capex_10k"]) for r in lines
                           if int(r["commissioning_year"]) == year)) < 1e-4
            assert abs(float(year_row["capacity_mva"]) -
                       sum(float(r["capacity_mva"]) for r in local)) < 1e-5
            assert abs(float(year_row["clr"]) -
                       float(year_row["capacity_mva"]) / float(year_row["net_peak_proxy_mw"])) < 1e-7
            assert float(year_row["clr"]) <= float(summary["cap"]) + 1e-6
            assert float(year_row["clr"]) >= float(summary["min_clr"]) - 1e-6
            assert float(year_row["clr"]) >= float(
                summary.get("annual_clr_floor", {}).get(str(year), 0)) - 1e-6
            assert float(year_row["clr"]) <= float(
                summary.get("annual_clr_ceiling", {}).get(str(year), float(summary["cap"]))) + 1e-6
            assert abs(float(year_row["net_peak_proxy_mw"]) - peaks[region + (year,)]) < 1e-5
            assert abs(float(year_row["transformer_capex_10k"]) -
                       sum(float(r["transformer_capex_10k"]) for r in local)) < 1e-4
            assert abs(float(year_row["storage_capex_10k"]) -
                       sum(float(r["storage_capex_10k"]) for r in local)) < 1e-4
            if load_reallocation:
                assert abs(sum(float(r["post_transfer_forward_mw"]) for r in local) -
                           sum(float(r["forward_mw"]) for r in local)) < 1e-5
            total_cost += (float(year_row["transformer_capex_10k"]) * factors["transformer"][year]
                           + float(year_row["storage_capex_10k"]) * factors["storage"][year]
                           + float(year_row["line_capex_10k"]) * factors["line"][year])
            by_pair = defaultdict(float)
            by_station_out = defaultdict(float)
            by_station_increment = defaultdict(float)
            for transfer in local_transfer:
                amount = float(transfer["mw"])
                assert amount > 0
                donor, receiver = transfer["donor"], transfer["receiver"]
                assert donor != receiver
                by_station_out[donor] += amount
                pair = tuple(sorted((donor, receiver)))
                if station_equivalent and transfer["kind"] == "rate_increment":
                    by_station_increment[donor] += amount
                    assert transfer["allocation_basis"] == "post_solve_station_balance_allocation_not_line_route"
                elif transfer["kind"] == "new":
                    assert pair in built_now
                    by_pair[pair] += amount
                else:
                    assert transfer["kind"] == "existing"
                    by_pair["existing"] += amount
            scale = float(year_row["net_peak_proxy_mw"]) / peaks[region + (2025,)]
            line_limit = float(summary.get("new_line_increment_mw", LINE_MW_2025)) * (
                1 if station_equivalent else scale)
            if not station_equivalent:
                assert all(amount <= line_limit + 1e-5
                           for pair, amount in by_pair.items() if pair != "existing")
                assert by_pair["existing"] <= float(summary["existing_transfer_limit_2025_mw"]) * scale + 1e-5
            else:
                assert sum(by_station_increment.values()) <= len(built_now) * line_limit + 1e-5
            for station in baseline:
                sid = station[2]
                forward = float(scenes[station, year]["estimated_station_forward_peak_mw"])
                existing_out = sum(float(t["mw"]) for t in local_transfer
                                   if t["kind"] == "existing" and t["donor"] == sid)
                assert existing_out <= float(summary["existing_transfer_fraction"]) * forward + 1e-5
                if summary["installed_transfer_target_enforced"] and (
                        scheme == "rigid" or summary.get("elastic_allow_line_decisions")):
                    incident_capacity = (sum(line_limit for r in built_records
                                             if sid in (r["station_a"], r["station_b"]))
                                         if station_equivalent else
                                         sum(line_limit for pair in built_now if sid in pair))
                    assert (incident_capacity + 1e-5 >=
                            max(0, float(summary["target_transfer_fraction"]) -
                                float(summary["existing_transfer_fraction"])) * forward)
            for station in baseline:
                station_id = station[2]
                item = by_station[str(year), station_id]
                units = (float(item["unit_1_mva"]), float(item["unit_2_mva"]))
                third = float(item["unit_3_mva"])
                prior = previous_capacity[station_id]
                assert all(new + 1e-6 >= old for old, new in zip(prior, units))
                assert all(new <= float(summary.get("new_unit_cap_mva", 100)) + 1e-6
                           for old, new in zip(prior, units) if new > old + 1e-6)
                if summary.get("new_unit_rating_policy") == "BC_common":
                    assert all(new in (40.0, 50.0) for old, new in zip(prior, units)
                               if new > old + 1e-6)
                if summary.get("new_unit_rating_policy") == "by_source_class":
                    allowed = AREA_RATINGS[physical[station_id]["area_class"]]
                    assert all(new in allowed for old, new in zip(prior, units)
                               if new > old + 1e-6)
                assert units[0] <= units[1] + 1e-6
                assert third in (0, 50) and third + 1e-6 >= previous_third[station_id]
                assert abs(sum(units) + third - float(item["capacity_mva"])) < 1e-6
                replaced = sum(new for new, old in zip(units, prior) if new > old + 1e-6)
                new_third = third - previous_third[station_id]
                if summary.get("enforce_expansion_slot") and third:
                    assert physical[station_id]["available_third_slots"] >= 1
                    assert physical[station_id]["available_third_mva"] >= third
                bought = replaced + new_third
                assert abs(bought - float(item["purchased_unit_mva"])) < 1e-5
                assert abs(float(item["transformer_capex_10k"]) -
                           (replaced * float(summary["transformer_price_10k_per_purchased_mva"])
                            + (new_third / 50) * float(summary["third_50mva_project_price_10k"]))
                           * float(summary.get("transformer_scale", 1))) < 1e-4
                energy = float(item["storage_energy_mwh"])
                if "storage_upper_by_station_mwh" in summary:
                    assert energy <= float(summary["storage_upper_by_station_mwh"][station_id]) + 1e-6
                assert energy + 1e-6 >= previous_energy[station_id]
                assert abs(energy - int(item["storage_modules"]) * STORAGE_MODULE_MWH) < 1e-6
                assert abs(float(item["new_storage_energy_mwh"]) -
                           int(item["new_storage_modules"]) * STORAGE_MODULE_MWH) < 1e-6
                assert abs(float(item["storage_capex_10k"]) -
                           float(item["new_storage_energy_mwh"]) *
                           float(summary["storage_price_10k_per_mwh"]) *
                           float(summary.get("storage_scale", 1))) < 1e-4
                assert abs(energy - STORAGE_MWH_PER_MW * float(item["storage_power_mw"])) < 1e-5
                outgoing = by_station_out[station_id]
                if station_equivalent:
                    forward_base = float(scenes[station, year]["estimated_station_forward_peak_mw"])
                    units_in_service = sum(station_id in (r["station_a"], r["station_b"])
                                           for r in built_records)
                    capability = capacity_from_station_rate(
                        forward_base, float(summary["existing_transfer_fraction"]), units_in_service,
                        line_limit, float(summary["station_fraction_ceiling"][station_id]))
                    assert outgoing <= capability["capacity_mw"] + 1e-5
                    assert by_station_increment[station_id] <= capability["credited_new_capacity_mw"] + 1e-5
                    assert abs(by_station_increment[station_id] -
                               max(0, outgoing - capability["initial_capacity_mw"])) < 1e-5
                    assert abs(float(item["transfer_base_load_mw"]) - forward_base) < 1e-6
                    assert int(item["incident_new_line_units"]) == units_in_service
                    assert abs(float(item["effective_transfer_fraction"]) - capability["capacity_fraction"]) < 1e-8
                    assert abs(float(item["effective_transfer_capacity_mw"]) - capability["capacity_mw"]) < 1e-5
                    assert abs(float(item["credited_new_transfer_capacity_mw"]) - capability["credited_new_capacity_mw"]) < 1e-5
                    if summary["installed_transfer_target_enforced"]:
                        assert capability["capacity_fraction"] + 1e-7 >= float(summary["target_transfer_fraction"])
                transfer_fraction = summary.get("max_transfer_fraction")
                if transfer_fraction is not None:
                    assert outgoing <= float(transfer_fraction) * float(
                        scenes[station, year]["estimated_station_forward_peak_mw"]) + 1e-5
                incoming = sum(float(t["mw"]) for t in local_transfer
                               if t["receiver"] == station_id)
                forward = float(scenes[station, year]["estimated_station_forward_peak_mw"])
                reverse = float(scenes[station, year]["reverse_screen_mw"])
                post_forward = forward - outgoing + incoming
                if load_reallocation:
                    assert post_forward >= -1e-5
                    assert abs(float(item["normal_load_transferred_out_mw"]) - outgoing) < 1e-5
                    assert abs(float(item["normal_load_transferred_in_mw"]) - incoming) < 1e-5
                    assert abs(float(item["post_transfer_forward_mw"]) - post_forward) < 1e-5
                    assert abs(float(item["post_transfer_reverse_upper_mw"]) - reverse - outgoing) < 1e-5
                    reverse += outgoing
                assert outgoing <= max(0.0, forward) + 1e-5
                baseline_capacity = sum(float(baseline[station][f"simulation_unit_{slot}_mva"])
                                        for slot in (1, 2))
                initial_margin = max(0, .95 * baseline_capacity -
                                     float(baseline[station]["estimated_forward_peak_mw_2021"]))
                forward_effect = energy / max(STORAGE_MWH_PER_MW,
                                              int(durations[station]["forward_d95_max_run_hours"]))
                reverse_effect = energy / max(STORAGE_MWH_PER_MW,
                                              int(durations[station]["reverse_d95_max_run_hours"]))
                assert (.95 * (sum(units) + third) + forward_effect + outgoing - incoming + 1e-4 >=
                        forward + float(summary["baseline_margin_fraction"]) * initial_margin)
                assert (.95 * float(summary["reverse_capacity_fraction"]) * (sum(units) + third)
                        + reverse_effect + 1e-4 >= reverse)
                if summary.get("require_transformer_n1_static_proxy"):
                    recovered = sum(float(r["recoverable_mw"]) for r in outages
                                    if int(r["year"]) == year and r["failed_station"] == station_id)
                    if transfer_fraction is not None:
                        assert recovered <= float(transfer_fraction) * forward + 1e-5
                    assigned = post_forward if load_reallocation else forward
                    demand = (assigned if summary.get("n1_load_requirement", "full") == "full" or
                              physical[station_id]["area_class"] == "A" else
                              max(0, min(assigned - 12, assigned * 2 / 3)))
                    for failed_index in range(2 + int(third > 0)):
                        available = (sum(units) + third) - (units[failed_index] if failed_index < 2 else third)
                        assert .95 * available + forward_effect + recovered + 1e-4 >= demand
                        checked += 1
                previous_capacity[station_id] = units
                previous_third[station_id] = third
                previous_energy[station_id] = energy
                checked += 2
            if not load_reallocation and (float(summary.get("outage_recovery_fraction", 0)) or summary.get("require_transformer_n1_static_proxy")):
                for failed in baseline:
                    failed_id = failed[2]
                    recovery_rows = [r for r in outages if int(r["year"]) == year
                                     and r["failed_station"] == failed_id]
                    recovered = sum(float(r["recoverable_mw"]) for r in recovery_rows)
                    required = (float(summary["outage_recovery_fraction"]) *
                                float(scenes[failed, year]["estimated_station_forward_peak_mw"]))
                    assert recovered + 1e-5 >= required
                    by_receiver = defaultdict(float)
                    for recovery in recovery_rows:
                        recipient_id = recovery["receiver_station"]
                        assert recipient_id != failed_id
                        pair = tuple(sorted((failed_id, recipient_id)))
                        amount = float(recovery["recoverable_mw"])
                        if recovery["kind"] == "new":
                            assert pair in built_now
                            assert amount <= LINE_MW_2025 * scale + 1e-5
                        else:
                            assert recovery["kind"] == "existing_county_proxy"
                        by_receiver[recipient_id] += amount
                    existing_recovered = sum(float(r["recoverable_mw"]) for r in recovery_rows
                                             if r["kind"] == "existing_county_proxy")
                    assert existing_recovered <= (float(summary["existing_transfer_fraction"]) *
                                                  float(scenes[failed, year]["estimated_station_forward_peak_mw"])
                                                  + 1e-5)
                    for recipient_id, amount in by_receiver.items():
                        recipient = region + (recipient_id,)
                        receiver_row = by_station[str(year), recipient_id]
                        receiver_capacity = float(receiver_row["capacity_mva"])
                        receiver_energy = float(receiver_row["storage_energy_mwh"])
                        hours = int(durations[recipient]["forward_d95_max_run_hours"])
                        receiver_load = float(scenes[recipient, year]["estimated_station_forward_peak_mw"])
                        initial = baseline[recipient]
                        initial_margin = max(0, .95 * sum(float(initial[f"simulation_unit_{slot}_mva"])
                                                              for slot in (1, 2))
                                             - float(initial["estimated_forward_peak_mw_2021"]))
                        assert (.95 * receiver_capacity + receiver_energy / max(STORAGE_MWH_PER_MW, hours)
                                - receiver_load - float(summary["baseline_margin_fraction"]) * initial_margin
                                + 1e-4 >= amount)
                    checked += 1
        assert abs(total_cost - float(summary["objective_npv_10k"])) < 1e-3
        if "selected_primary_objective_10k" in summary:
            assert float(summary["selected_primary_objective_10k"]) <= (
                float(summary["minimum_primary_objective_10k"]) +
                float(summary["cost_tiebreak_tolerance_10k"]) + 1e-5)
        results.append({"scheme": scheme, "status": "PASS", "station_scenario_checks": checked,
                        "line_pairs": len(lines), "lifecycle_npv_10k": total_cost})
    (directory / "audit.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n",
                                           encoding="utf-8")
    return {"status": "PASS", "schemes": results}


if __name__ == "__main__":
    print(audit())
