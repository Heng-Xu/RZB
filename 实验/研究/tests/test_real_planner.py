from __future__ import annotations

import pandas as pd
import pytest

from src.v3_planner import (
    PATH_OPT_STRICT,
    PATH_OPT_UNBOUNDED,
    _candidate_frame,
    optimize_joint_paths,
    validate_path_inclusion,
)


def _annual() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "year": [2022, 2023, 2024, 2025],
            "region_id": ["QX-00005"] * 4,
            "voltage_kv": [110] * 4,
            "capacity_mva": [100.0] * 4,
            "positive_peak_mw": [40.0, 42.0, 45.0, 50.0],
            "reverse_peak_mw": [0.0] * 4,
            "reverse_beta": [0.8] * 4,
        }
    )


def _candidates() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "candidate_id": "RETIRE-T1",
                "region_id": "QX-00005",
                "voltage_kv": 110,
                "candidate_type": "retirement",
                "delta_capacity_mva": -20.0,
                "capex_base_wanyuan": 20.0,
                "eac_base_wanyuan_per_year": 10.0,
                "cost_status": "cost_center_and_range_available",
                "source_ref": "synthetic-test-source",
            },
            {
                "candidate_id": "EXPENSIVE-EXPANSION",
                "region_id": "QX-00005",
                "voltage_kv": 110,
                "candidate_type": "new_third_transformer",
                "delta_capacity_mva": 50.0,
                "capex_base_wanyuan": 1000.0,
                "eac_base_wanyuan_per_year": 100.0,
                "cost_status": "cost_center_and_range_available",
                "source_ref": "synthetic-test-source",
            },
        ]
    )


def test_joint_optimizer_carries_2022_action_into_each_later_year_eac() -> None:
    result = optimize_joint_paths(_annual(), _candidates())
    costs = result["path_cost_breakdown"].set_index("path_id")
    strict = result["path_year_results"].query("path_id == @PATH_OPT_STRICT").sort_values("year")
    actions = result["path_action_results"].query("path_id == @PATH_OPT_STRICT")

    assert set(actions["candidate_id"]) == {"RETIRE-T1"}
    assert actions["year"].tolist() == [2022]
    assert strict["installed_capacity_mva"].tolist() == pytest.approx([80.0] * 4)
    assert strict["clr"].tolist() == pytest.approx([2.0, 80.0 / 42.0, 80.0 / 45.0, 1.6])
    assert strict["annual_in_service_eac_wanyuan"].tolist() == pytest.approx([10.0] * 4)
    assert costs.loc[PATH_OPT_STRICT, "cumulative_in_service_eac_wanyuan"] == pytest.approx(40.0)
    assert costs.loc[PATH_OPT_UNBOUNDED, "cumulative_in_service_eac_wanyuan"] == pytest.approx(0.0)


def test_joint_optimizer_enforces_cost_inclusion_and_yearly_strict_limit() -> None:
    result = optimize_joint_paths(_annual(), _candidates())
    assert validate_path_inclusion(result["path_cost_breakdown"])
    strict = result["path_year_results"].query("path_id == @PATH_OPT_STRICT")
    assert (strict["clr"] <= 2.0 + 1e-9).all()
    assert set(result["path_year_results"]["path_id"]) == {
        PATH_OPT_UNBOUNDED,
        PATH_OPT_STRICT,
    }


def test_missing_candidate_group_does_not_make_unrelated_candidates_mutually_exclusive() -> None:
    frame = _candidates().iloc[[1]].copy()
    second = frame.copy()
    second["candidate_id"] = "EXPENSIVE-EXPANSION-2"
    candidates = pd.concat([frame, second], ignore_index=True)
    parsed = _candidate_frame(candidates)
    assert [candidate.candidate_group for candidate in parsed] == [
        "EXPENSIVE-EXPANSION",
        "EXPENSIVE-EXPANSION-2",
    ]
