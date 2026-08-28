from __future__ import annotations

import math

import pandas as pd
import pytest

from src.v32_frontier_aggregate import (
    V32FrontierAggregateError,
    build_coarse_recommendations,
    validate_frontier_nested,
)


def _frontier() -> pd.DataFrame:
    rows = [
        {
            "rcap": "unbounded",
            "rcap_numeric": math.nan,
            "region_id": "QX-A",
            "voltage_kv": 110,
            "feasible": True,
            "cumulative_in_service_eac_wanyuan": 100.0,
            "physical_clr_2025": 2.60,
            "storage_modules": 10,
            "capacity_action_delta_mva": 50.0,
            "action_types": "new_third_transformer;storage",
            "candidate_ids": "EXP-A",
            "retirement_candidates_enabled": False,
        },
        {
            "rcap": 1.5,
            "rcap_numeric": 1.5,
            "region_id": "QX-A",
            "voltage_kv": 110,
            "feasible": False,
            "cumulative_in_service_eac_wanyuan": math.nan,
            "physical_clr_2025": math.nan,
            "storage_modules": math.nan,
            "capacity_action_delta_mva": math.nan,
            "action_types": "none",
            "candidate_ids": "",
            "retirement_candidates_enabled": False,
        },
        {
            "rcap": 2.0,
            "rcap_numeric": 2.0,
            "region_id": "QX-A",
            "voltage_kv": 110,
            "feasible": True,
            "cumulative_in_service_eac_wanyuan": 110.0,
            "physical_clr_2025": 2.30,
            "storage_modules": 30,
            "capacity_action_delta_mva": 0.0,
            "action_types": "storage",
            "candidate_ids": "",
            "retirement_candidates_enabled": False,
        },
        {
            "rcap": 2.1,
            "rcap_numeric": 2.1,
            "region_id": "QX-A",
            "voltage_kv": 110,
            "feasible": True,
            "cumulative_in_service_eac_wanyuan": 104.0,
            "physical_clr_2025": 2.35,
            "storage_modules": 20,
            "capacity_action_delta_mva": 0.0,
            "action_types": "storage",
            "candidate_ids": "",
            "retirement_candidates_enabled": False,
        },
        {
            "rcap": 2.2,
            "rcap_numeric": 2.2,
            "region_id": "QX-A",
            "voltage_kv": 110,
            "feasible": True,
            "cumulative_in_service_eac_wanyuan": 100.0,
            "physical_clr_2025": 2.60,
            "storage_modules": 10,
            "capacity_action_delta_mva": 50.0,
            "action_types": "new_third_transformer;storage",
            "candidate_ids": "EXP-A",
            "retirement_candidates_enabled": False,
        },
    ]
    return pd.DataFrame(rows)


def test_frontier_validates_nested_feasible_set_and_nonincreasing_cost() -> None:
    assert validate_frontier_nested(_frontier()) is True


def test_coarse_recommendation_stays_on_rcap_dimension() -> None:
    result = build_coarse_recommendations(_frontier(), near_optimal_band=0.05).iloc[0]
    assert result["coarse_rcap_low"] == pytest.approx(2.1)
    assert result["coarse_rcap_high"] == pytest.approx(2.2)
    assert result["coarse_near_optimal_points"] == "2.1;2.2"
    # 实现 CLR 明显高于 Rcap，也不得拿实现 CLR 去截断 Rcap 推荐带。
    assert result["realized_physical_clr_2025_low"] == pytest.approx(2.35)
    assert result["realized_physical_clr_2025_high"] == pytest.approx(2.60)
    assert bool(result["measure_flip"]) is True


def test_frontier_rejects_feasible_then_infeasible_when_rcap_relaxes() -> None:
    frame = _frontier()
    frame.loc[frame["rcap_numeric"].eq(2.2), "feasible"] = False
    with pytest.raises(V32FrontierAggregateError, match="not nested"):
        validate_frontier_nested(frame)


def test_frontier_rejects_cost_increase_when_rcap_relaxes() -> None:
    frame = _frontier()
    frame.loc[frame["rcap_numeric"].eq(2.2), "cumulative_in_service_eac_wanyuan"] = 106.0
    with pytest.raises(V32FrontierAggregateError, match="cost rises"):
        validate_frontier_nested(frame)
