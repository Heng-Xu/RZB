from __future__ import annotations

from pathlib import Path

from src.v32_contract import load_v32_contract


ROOT = Path(__file__).resolve().parents[1]


def test_v32_contract_uses_actual_2021_asset_baseline_with_grandfathering() -> None:
    contract = load_v32_contract(ROOT)
    assert contract["contract"]["version"] == "3.2.0"
    baseline = contract["planning_baseline"]
    assert baseline["baseline_year"] == 2021
    assert baseline["formula"] == "S0 = actual_2021_installed_capacity"
    assert baseline["future_decision_year_information_allowed"] is False
    assert baseline["physical_and_planning_start_state_identical"] is True
    assert baseline["legacy_capacity_excess_treatment"] == (
        "grandfather_existing_capacity_without_forced_retirement"
    )
    assert baseline["retirement_to_meet_rcap_forbidden"] is True
    assert baseline["rigid_incremental_capacity_rule"] == (
        "DeltaS_y <= max(Rcap * P_plus_y - S_2021, 0)"
    )


def test_v32_contract_restores_same_actual_baseline_cost_comparison() -> None:
    contract = load_v32_contract(ROOT)
    optimization = contract["optimization"]
    assert optimization["shared_inputs"]["same_planning_baseline"] is True
    assert optimization["shared_inputs"]["same_physical_asset_baseline"] is True
    assert optimization["retirement_candidates_in_primary_policy_model"] is False
    assert optimization["direct_policy_cost_comparison_allowed"] is True
    assert optimization["policy_incremental_cost_formula"] == "C_rigid - C_elastic"
    assert "elastic_cost_not_greater_than_rigid_cost_when_both_feasible" in optimization["invariants"]


def test_v32_contract_keeps_rcap_and_physical_clr_separate() -> None:
    contract = load_v32_contract(ROOT)
    sweep = contract["elasticity_sweep"]
    assert sweep["recommendation_dimension"] == "Rcap"
    assert sweep["realized_clr_is_separate_output"] is True
    assert sweep["realized_clr_definition"] == (
        "physical_installed_capacity_mva / synchronized_positive_peak_mw"
    )
    assert sweep["forbidden_operation"] == "intersect_Rcap_interval_with_realized_CLR_interval"
    assert sweep["near_optimal_band_sensitivity"] == [0.02, 0.05, 0.10]
    assert contract["metrics"]["formal_clr"]["policy_control_ratio_is_formal_clr"] is False


def test_v32_contract_retains_normalized_clr2_baseline_as_secondary_benchmark_only() -> None:
    benchmark = load_v32_contract(ROOT)["standardized_policy_benchmark"]
    assert benchmark["enabled"] is True
    assert benchmark["formula"] == "S_norm_0 = 2.0 * P_plus_2021"
    assert benchmark["future_decision_year_information_allowed"] is False
    assert benchmark["direct_client_cost_conclusion_allowed"] is False
    assert benchmark["role"] == "secondary_sensitivity_only_not_primary_client_policy_model"


def test_v32_contract_requires_continuous_qx00005_validation_and_beta_sensitivity() -> None:
    contract = load_v32_contract(ROOT)
    assert contract["storage"]["continuous_validation"]["qx00005_110kv_required"] is True
    assert contract["storage"]["continuous_validation"]["chronology_hours"] == 8760
    assert contract["technical_parameters"]["reverse_beta"]["sensitivity"] == [0.60, 0.80, 1.00]
    assert contract["method_positioning"]["ahp"]["core_optimization_method"] is False
