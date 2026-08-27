from __future__ import annotations

from pathlib import Path

from src.v32_contract import load_v32_contract


ROOT = Path(__file__).resolve().parents[1]


def test_v32_contract_uses_common_2021_clr2_planning_baseline() -> None:
    contract = load_v32_contract(ROOT)
    assert contract["contract"]["version"] == "3.2.0"
    baseline = contract["planning_baseline"]
    assert baseline["baseline_year"] == 2021
    assert baseline["baseline_clr"] == 2.0
    assert baseline["formula"] == "S_plan_0 = 2.0 * P_plus_2021"
    assert baseline["future_decision_year_peak_allowed_in_baseline"] is False
    assert baseline["physical_asset_state_separate"] is True


def test_v32_contract_restores_same_baseline_cost_comparison() -> None:
    contract = load_v32_contract(ROOT)
    optimization = contract["optimization"]
    assert optimization["shared_inputs"]["same_planning_baseline"] is True
    assert optimization["shared_inputs"]["same_physical_asset_baseline"] is True
    assert optimization["direct_policy_cost_comparison_allowed"] is True
    assert optimization["policy_incremental_cost_formula"] == "C_rigid - C_elastic"
    assert "elastic_cost_not_greater_than_rigid_cost_when_both_feasible" in optimization["invariants"]


def test_v32_contract_keeps_rcap_and_realized_clr_separate() -> None:
    sweep = load_v32_contract(ROOT)["elasticity_sweep"]
    assert sweep["recommendation_dimension"] == "Rcap"
    assert sweep["realized_clr_is_separate_output"] is True
    assert sweep["forbidden_operation"] == "intersect_Rcap_interval_with_realized_CLR_interval"
    assert sweep["near_optimal_band_sensitivity"] == [0.02, 0.05, 0.10]


def test_v32_contract_requires_continuous_qx00005_validation_and_beta_sensitivity() -> None:
    contract = load_v32_contract(ROOT)
    assert contract["storage"]["continuous_validation"]["qx00005_110kv_required"] is True
    assert contract["storage"]["continuous_validation"]["chronology_hours"] == 8760
    assert contract["technical_parameters"]["reverse_beta"]["sensitivity"] == [0.60, 0.80, 1.00]
    assert contract["method_positioning"]["ahp"]["core_optimization_method"] is False
