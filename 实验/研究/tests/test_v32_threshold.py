from __future__ import annotations

import math

import pandas as pd
import pytest

from src.v32_threshold import classify_economic_release_thresholds


def _rows(region: str, costs: list[float | None], *, unbounded: float | None) -> list[dict]:
    points = [1.5, 2.0, 2.5]
    result = []
    for rcap, cost in zip(points, costs, strict=True):
        result.append(
            {
                "rcap": rcap,
                "rcap_numeric": rcap,
                "region_id": region,
                "voltage_kv": 110,
                "feasible": cost is not None,
                "cumulative_in_service_eac_wanyuan": math.nan if cost is None else cost,
                "retirement_candidates_enabled": False,
            }
        )
    result.append(
        {
            "rcap": "unbounded",
            "rcap_numeric": math.nan,
            "region_id": region,
            "voltage_kv": 110,
            "feasible": unbounded is not None,
            "cumulative_in_service_eac_wanyuan": math.nan if unbounded is None else unbounded,
            "retirement_candidates_enabled": False,
        }
    )
    return result


def test_threshold_classifies_binding_bracket_without_using_scan_high_as_upper_recommendation() -> None:
    frame = pd.DataFrame(_rows("QX-A", [150.0, 120.0, 100.0], unbounded=100.0))
    row = classify_economic_release_thresholds(frame, near_optimal_band=0.05).iloc[0]
    assert row["threshold_status"] == "binding_threshold_bracketed"
    assert row["coarse_release_threshold_lower"] == pytest.approx(2.0)
    assert row["coarse_release_threshold_upper"] == pytest.approx(2.5)
    assert row["minimum_near_optimal_rcap_on_grid"] == pytest.approx(2.5)
    assert bool(row["requires_local_refinement"]) is True


def test_threshold_marks_fully_flat_frontier_as_nonbinding_not_scan_lower_recommendation() -> None:
    frame = pd.DataFrame(_rows("QX-B", [100.0, 100.0, 100.0], unbounded=100.0))
    row = classify_economic_release_thresholds(frame).iloc[0]
    assert row["threshold_status"] == "non_binding_not_identified_in_horizon"
    assert math.isnan(row["coarse_release_threshold_lower"])
    assert math.isnan(row["coarse_release_threshold_upper"])
    assert bool(row["requires_local_refinement"]) is False


def test_threshold_does_not_form_when_unbounded_physics_is_infeasible() -> None:
    frame = pd.DataFrame(_rows("QX-C", [None, None, None], unbounded=None))
    row = classify_economic_release_thresholds(frame).iloc[0]
    assert row["threshold_status"] == "not_formed_physical_infeasible"
    assert bool(row["requires_local_refinement"]) is False
