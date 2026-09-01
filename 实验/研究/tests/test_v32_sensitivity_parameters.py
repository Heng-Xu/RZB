from __future__ import annotations

import pandas as pd
import pytest

from src.v32_actual_pipeline import (
    scale_annual_net_load_input,
    scale_expansion_candidate_costs,
)
from scripts.run_v32_sensitivity_suite import (
    FORMAL_SCENARIOS,
    INTERACTION_SCENARIOS,
    ONE_FACTOR_SCENARIOS,
    PHYSICAL_SCENARIOS,
)


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
