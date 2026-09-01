from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.v32_actual_pipeline import (
    scale_annual_net_load_input,
    scale_expansion_candidate_costs,
)
from scripts.run_v32_sensitivity_suite import (
    BASELINE_CONTROL_SCENARIO_ID,
    BASELINE_PARAMETERS,
    FORMAL_SCENARIOS,
    INTERACTION_SCENARIOS,
    ONE_FACTOR_SCENARIOS,
    PHYSICAL_SCENARIOS,
    SCENARIO_FAMILIES,
    select_scenario_names,
)
from src.v32_sensitivity import validate_sensitivity_manifest_parameters


ROOT = Path(__file__).resolve().parents[1]


def test_net_load_sensitivity_scales_peaks_but_not_actual_asset_baseline() -> None:
    annual = pd.DataFrame(
        [
            {
                "region_id": "QX-A",
                "voltage_kv": 110,
                "year": 2025,
                "baseline_capacity_mva": 100.0,
                "positive_peak_mw": 40.0,
                "reverse_peak_mw": 5.0,
            }
        ]
    )
    result = scale_annual_net_load_input(annual, 1.10)
    assert result["positive_peak_mw"].iloc[0] == pytest.approx(44.0)
    assert result["reverse_peak_mw"].iloc[0] == pytest.approx(5.5)
    assert result["baseline_capacity_mva"].iloc[0] == pytest.approx(100.0)
    assert annual["positive_peak_mw"].iloc[0] == pytest.approx(40.0)


def test_expansion_cost_sensitivity_scales_scenario_copy_only() -> None:
    candidates = pd.DataFrame(
        [
            {
                "candidate_id": "EXP-A",
                "delta_capacity_mva": 50.0,
                "capex_low_wanyuan": 10.0,
                "capex_center_wanyuan": 12.0,
                "capex_high_wanyuan": 14.0,
                "eac_low_wanyuan_per_year": 1.0,
                "eac_center_wanyuan_per_year": 1.2,
                "eac_high_wanyuan_per_year": 1.4,
            }
        ]
    )
    result = scale_expansion_candidate_costs(candidates, 0.80)
    assert result["delta_capacity_mva"].iloc[0] == pytest.approx(50.0)
    assert result["capex_center_wanyuan"].iloc[0] == pytest.approx(9.6)
    assert result["eac_center_wanyuan_per_year"].iloc[0] == pytest.approx(0.96)
    assert candidates["capex_center_wanyuan"].iloc[0] == pytest.approx(12.0)


def test_formal_sensitivity_uses_a_small_non_cartesian_interaction_set() -> None:
    assert set(INTERACTION_SCENARIOS) == {
        "high_load_high_storage",
        "high_load_low_expansion",
        "high_load_high_expansion",
        "low_beta_high_load",
        "high_storage_low_expansion",
        "low_storage_high_expansion",
    }
    assert len(INTERACTION_SCENARIOS) == 6

    baseline = {
        "cos_phi": 0.95,
        "reverse_beta": 0.80,
        "net_load_scale": 1.0,
        "storage_cost_multiplier": 1.0,
        "expansion_cost_multiplier": 1.0,
    }
    for name, parameters in INTERACTION_SCENARIOS.items():
        changed = {
            key
            for key, value in parameters.items()
            if value != pytest.approx(baseline[key])
        }
        assert len(changed) >= 2, name
        assert not any("pv" in key.lower() for key in parameters), name


def test_formal_sensitivity_registry_covers_physical_oat_and_interactions() -> None:
    expected = {
        **PHYSICAL_SCENARIOS,
        **ONE_FACTOR_SCENARIOS,
        **INTERACTION_SCENARIOS,
    }
    assert FORMAL_SCENARIOS == expected
    assert len(FORMAL_SCENARIOS) == 17


def test_scenario_all_defaults_to_all_formal_parameter_scenarios() -> None:
    names = select_scenario_names("all")
    assert names == list(FORMAL_SCENARIOS)
    assert len(names) == 17
    assert len(set(names)) == 17


def test_explicit_sensitivity_families_keep_their_declared_sizes() -> None:
    assert len(select_scenario_names("all", family="physical")) == 5
    assert len(select_scenario_names("all", family="one-factor")) == 6
    assert len(select_scenario_names("all", family="interaction")) == 6
    assert set(SCENARIO_FAMILIES) == {"physical", "one-factor", "interaction", "formal"}


def test_formal_registry_has_exactly_one_baseline_reproduction_control() -> None:
    controls = [
        name for name, parameters in FORMAL_SCENARIOS.items()
        if parameters == BASELINE_PARAMETERS
    ]
    assert controls == [BASELINE_CONTROL_SCENARIO_ID]


def test_packaged_baseline_control_reproduces_main_frontier_core_results() -> None:
    frozen = ROOT / "results/runs/real-2021-2025-v32-frozen"
    main = pd.read_csv(frozen / "elasticity_frontier_v32_actual_coarse.csv")
    control = pd.read_csv(frozen / "rcap_sensitivity_frontiers_coarse.csv")
    control = control[control["scenario_id"].eq("pf0.95_beta0.80")].copy()
    shared = [
        "rcap",
        "rcap_numeric",
        "region_id",
        "voltage_kv",
        "feasible",
        "status",
        "cumulative_in_service_eac_wanyuan",
        "capacity_action_delta_mva",
        "action_types",
        "candidate_ids",
        "selected_action_count",
        "policy_basis",
        "retirement_candidates_enabled",
        "physical_clr_2025",
        "policy_control_ratio_2025",
        "installed_capacity_mva_2025",
        "storage_modules",
        "p_plus_mw_2025",
        "p_minus_mw_2025",
    ]
    assert len(control) == len(main)
    main_core = main[shared].sort_values(
        ["region_id", "rcap_numeric"], na_position="last"
    ).reset_index(drop=True)
    control_core = control[shared].sort_values(
        ["region_id", "rcap_numeric"], na_position="last"
    ).reset_index(drop=True)
    pd.testing.assert_frame_equal(main_core, control_core, check_dtype=False)

    assert control["cos_phi"].eq(BASELINE_PARAMETERS["cos_phi"]).all()
    assert control["reverse_beta"].eq(BASELINE_PARAMETERS["reverse_beta"]).all()
    for field in (
        "net_load_scale",
        "storage_cost_multiplier",
        "expansion_cost_multiplier",
    ):
        assert control[field].eq(BASELINE_PARAMETERS[field]).all()


def test_scenario_manifest_reconstructs_all_transmitted_parameter_fields() -> None:
    manifest = {
        "cos_phi": 0.95,
        "reverse_beta": 0.80,
        "net_load_scale": 1.05,
        "storage_cost_multiplier": 1.20,
        "expansion_cost_multiplier": 0.80,
        "parameters": {
            "cos_phi": 0.95,
            "reverse_beta": 0.80,
            "net_load_scale": 1.05,
            "storage_cost_multiplier": 1.20,
            "expansion_cost_multiplier": 0.80,
        },
    }
    assert validate_sensitivity_manifest_parameters(manifest) == manifest["parameters"]
