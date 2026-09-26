from collections import defaultdict

import pytest

from rebuild_2026.annual_no_tie_investment_submodel import (
    build_annual_no_tie_investment_submodel, storage_effective_power_per_module,
)
from rebuild_2026.joint_lifecycle_optimizer import (
    cost_factors, load_inputs, run_model, solve_layer, tie_edges,
)
from rebuild_2026.joint_lifecycle_cashflow import build_cashflows
from rebuild_2026.joint_lifecycle_result_matrix import build_matrices


def test_lifecycle_model_reduces_to_investment_only_when_om_and_renewals_absent() -> None:
    factors = cost_factors(transformer_life=25, line_life=25, storage_life=25,
                           network_om=0, storage_om=0)
    _, _, _, joint = run_model(factors=factors, rigid=False)
    _, _, investment = build_annual_no_tie_investment_submodel()
    by_layer = {(r["study_region_id"], r["voltage_kv"]): r for r in investment}
    for row in joint:
        expected = by_layer[row["study_region_id"], row["voltage_kv"]]["investment_npv_10k_cny"]
        assert row["objective_npv_10k_cny"] == pytest.approx(expected, abs=1e-3)


def test_rigid_solution_respects_station_and_shared_feeder_static_bounds() -> None:
    stations, years, transfers, summaries = run_model(rigid=True)
    _, _, durations, _, _, _ = load_inputs()
    edges, feeders = tie_edges()
    by_station = {(r["study_region_id"], r["voltage_kv"], r["model_station_id"], r["year"]): r
                  for r in stations}
    used = defaultdict(float)
    receiver_used = defaultdict(float)
    direction = defaultdict(set)
    for move in transfers:
        assert move["tie_id"] in {e["tie_id"] for e in edges}
        key = move["year"], move["scenario"]
        used[key, move["donor_feeder_id"]] += move["transfer_mw"]
        receiver_used[key, move["receiver_feeder_id"]] += move["transfer_mw"]
        direction[move["year"]].add((move["donor_station_id"], move["receiver_station_id"]))
    for (key, feeder), magnitude in used.items():
        assert magnitude <= float(feeders[feeder]["current_equivalent_active_power_mw"]) + 1e-6
    for (key, feeder), magnitude in receiver_used.items():
        assert magnitude <= float(feeders[feeder]["receiving_current_headroom_mw"]) + 1e-6
    assert all(len(directions) <= 1 for directions in direction.values())
    planned = [r for r in transfers if r["year"] == 2025 and r["scenario"] == "forward"
               and r["tie_id"] == "T01"]
    assert len(planned) == 1
    assert planned[0]["donor_feeder_id"] == "PZXL-00092"
    assert planned[0]["receiver_feeder_id"] == "PZXL-00161"
    assert planned[0]["transfer_mw"] == pytest.approx(4.49651196)
    assert planned[0]["operation_basis"] == "original_pdf_switch28_whole_downstream_section_2025_load_seed"
    for row in stations:
        station = row["model_station_id"]
        key = row["study_region_id"], row["voltage_kv"], station
        for scenario in ("forward", "reverse"):
            shift = sum(move["transfer_mw"] * (1 if move["donor_station_id"] == station else -1)
                        for move in transfers if move["year"] == row["year"]
                        and move["scenario"] == scenario
                        and station in (move["donor_station_id"], move["receiver_station_id"]))
            factor = 0.95 if scenario == "forward" else 0.8 * 0.95
            duration = int(durations[key][f"{scenario}_d95_max_run_hours"])
            storage_effect = storage_effective_power_per_module(duration)
            demand = row["forward_screen_mw" if scenario == "forward" else "reverse_screen_mw"]
            assert factor * row["selected_capacity_mva"] + storage_effect * row["storage_modules_in_service"] + shift >= demand - 1e-6
    for row in years:
        assert row["actual_clr"] <= row["clr_cap"] + 1e-8
    assert len({(r["study_region_id"], r["voltage_kv"]) for r in summaries}) == 3


def test_delivered_cashflows_and_voltage_matrices_reconcile() -> None:
    events, annual = build_cashflows()
    matrices = build_matrices()
    assert len(events) == 690
    assert len(annual) == 160
    assert len(matrices[35]) == 4
    assert len(matrices[110]) == 8
    assert {row["study_region_id"] for row in matrices[35]} == {"QX-00005"}
    assert all(int(row["voltage_kv"]) == 110 for row in matrices[110])


def test_common_measure_price_scale_preserves_optimal_cost_homogeneity() -> None:
    inputs = load_inputs()
    factors = cost_factors()
    base = solve_layer(("QX-00005", 35), *inputs, factors, 2.4, False)[3]
    doubled = solve_layer(("QX-00005", 35), *inputs, factors, 2.4, False,
                          transformer_cost_scale=2.0, storage_cost_scale=2.0)[3]
    assert doubled["objective_npv_10k_cny"] == pytest.approx(
        2 * base["objective_npv_10k_cny"], abs=1e-4)


def test_relaxed_clr_cap_cannot_raise_optimal_cost_with_same_measure_scope() -> None:
    _, _, _, rigid = run_model(rigid=True, tie_allowed=True)
    _, _, _, elastic = run_model(
        rigid=False, tie_allowed=True,
        caps={("QX-00005", 35): 4.0, ("QX-00005", 110): 4.0,
              ("QX-00007", 110): 3.0})
    by_layer = {(r["study_region_id"], r["voltage_kv"]): r for r in rigid}
    for row in elastic:
        assert row["objective_npv_10k_cny"] <= (
            by_layer[row["study_region_id"], row["voltage_kv"]]["objective_npv_10k_cny"] + 1e-5)
