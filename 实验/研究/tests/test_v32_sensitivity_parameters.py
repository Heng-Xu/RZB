from __future__ import annotations

import pandas as pd
import pytest

from src.v32_actual_pipeline import (
    scale_annual_net_load_input,
    scale_expansion_candidate_costs,
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
