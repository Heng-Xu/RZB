"""v3.2 主政策实验：实际资产共同起点与存量豁免 Rcap。"""
from __future__ import annotations

import pandas as pd
import pytest

from src.v3_planner import StatePhysicsResult
from src.v32_policy import (
    apply_actual_asset_policy_baseline,
    prepare_grandfathered_rcap_control,
    run_actual_asset_policy_paths,
)


def _annual(peaks=(40.0, 40.0, 40.0, 40.0)) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "year": [2022, 2023, 2024, 2025],
            "region_id": ["QX-A"] * 4,
            "voltage_kv": [110] * 4,
            "capacity_mva": [100.0] * 4,
            "baseline_capacity_mva": [100.0] * 4,
            "positive_peak_mw": list(peaks),
            "reverse_peak_mw": [0.0] * 4,
            "reverse_beta": [0.8] * 4,
        }
    )


def _expansion() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "candidate_id": "EXP-10",
                "candidate_group": "EXP-GROUP",
                "region_id": "QX-A",
                "voltage_kv": 110,
                "candidate_type": "new_third_transformer",
                "delta_capacity_mva": 10.0,
                "capex_base_wanyuan": 100.0,
                "eac_base_wanyuan_per_year": 10.0,
                "cost_status": "cost_center_and_range_available",
                "source_ref": "unit-test",
                "available_year": 2022,
            }
        ]
    )


def test_actual_asset_baseline_is_not_rewritten_to_target_clr() -> None:
    out = apply_actual_asset_policy_baseline(_annual())
    assert out["planning_baseline_capacity_mva"].tolist() == pytest.approx([100.0] * 4)
    assert out["reported_baseline_capacity_mva"].tolist() == pytest.approx([100.0] * 4)


def test_legacy_capacity_can_keep_physical_clr_above_rcap_without_forced_retirement() -> None:
    result = run_actual_asset_policy_paths(
        _annual(),
        pd.DataFrame(),
        planner_kwargs={},
        rigid_rcap=2.0,
    )
    rigid = result["path_year_results"].query(
        "path_id == 'PATH_OPT_CLR_LE_2'"
    ).sort_values("year")
    assert set(rigid["status"]) == {"feasible"}
    assert rigid["installed_capacity_mva"].tolist() == pytest.approx([100.0] * 4)
    # 真实资产 CLR=100/40=2.5，可高于 Rcap，因为这是 2021 已形成的存量。
    assert rigid["physical_clr"].tolist() == pytest.approx([2.5] * 4)
    # 内部政策控制状态只用于证明“新增容量空间为 0”，不冒充真实 CLR。
    assert rigid["policy_control_ratio"].tolist() == pytest.approx([2.0] * 4)
    actions = result["path_action_results"].query(
        "path_id == 'PATH_OPT_CLR_LE_2'"
    )
    assert actions.empty


def test_grandfather_transform_matches_incremental_capacity_envelope() -> None:
    annual = _annual((40.0, 45.0, 50.0, 55.0))
    controlled = prepare_grandfathered_rcap_control(annual, rcap=2.0)
    # reported_base=min(S2021,2P): 80,90,100,100。
    assert controlled["reported_baseline_capacity_mva"].tolist() == pytest.approx(
        [80.0, 90.0, 100.0, 100.0]
    )
    assert controlled["legacy_capacity_grandfathered"].tolist() == [True, True, False, False]
    # 对应允许的新增容量 max(2P-S2021,0): 0,0,0,10 MVA。
    allowed_delta = (
        2.0 * controlled["positive_peak_mw"] - controlled["baseline_capacity_mva"]
    ).clip(lower=0.0)
    assert allowed_delta.tolist() == pytest.approx([0.0, 0.0, 0.0, 10.0])


def test_expansion_required_before_load_catches_up_makes_rigid_policy_infeasible() -> None:
    def require_expansion(
        _region_id: str,
        _voltage_kv: int,
        year: int,
        selected_candidate_ids: tuple[str, ...],
    ) -> StatePhysicsResult:
        if year == 2025 and "EXP-10" not in selected_candidate_ids:
            return StatePhysicsResult(
                False,
                0,
                reason="terminal_physics_requires_expansion",
                repair_candidate_ids=("EXP-10",),
            )
        return StatePhysicsResult(True, 0)

    result = run_actual_asset_policy_paths(
        _annual(),
        _expansion(),
        planner_kwargs={"state_physics_evaluator": require_expansion},
        rigid_rcap=2.0,
    )
    costs = result["path_cost_breakdown"].set_index("path_id")
    assert costs.loc["PATH_OPT_CLR_UNBOUNDED", "status"] == "feasible"
    assert costs.loc["PATH_OPT_CLR_LE_2", "status"] == "infeasible"
    elastic_actions = result["path_action_results"].query(
        "path_id == 'PATH_OPT_CLR_UNBOUNDED'"
    )
    assert set(elastic_actions["candidate_id"]) == {"EXP-10"}


def test_same_expansion_is_allowed_after_load_creates_incremental_rcap_headroom() -> None:
    def require_expansion(
        _region_id: str,
        _voltage_kv: int,
        year: int,
        selected_candidate_ids: tuple[str, ...],
    ) -> StatePhysicsResult:
        if year == 2025 and "EXP-10" not in selected_candidate_ids:
            return StatePhysicsResult(
                False,
                0,
                reason="terminal_physics_requires_expansion",
                repair_candidate_ids=("EXP-10",),
            )
        return StatePhysicsResult(True, 0)

    # 2022—2024 无需提前投运，2025 P=55 MW 后 2P=110 MVA，恰好允许 +10 MVA。
    result = run_actual_asset_policy_paths(
        _annual((50.0, 50.0, 50.0, 55.0)),
        _expansion(),
        planner_kwargs={"state_physics_evaluator": require_expansion},
        rigid_rcap=2.0,
    )
    costs = result["path_cost_breakdown"].set_index("path_id")
    assert costs.loc["PATH_OPT_CLR_UNBOUNDED", "status"] == "feasible"
    assert costs.loc["PATH_OPT_CLR_LE_2", "status"] == "feasible"
    rigid_actions = result["path_action_results"].query(
        "path_id == 'PATH_OPT_CLR_LE_2'"
    )
    assert rigid_actions["candidate_id"].tolist() == ["EXP-10"]
    assert rigid_actions["year"].tolist() == [2025]


def test_elastic_cost_is_not_greater_when_both_policy_paths_are_feasible() -> None:
    result = run_actual_asset_policy_paths(
        _annual((50.0, 50.0, 50.0, 55.0)),
        pd.DataFrame(),
        planner_kwargs={},
        rigid_rcap=2.0,
    )
    costs = result["path_cost_breakdown"].set_index("path_id")
    assert (
        float(costs.loc["PATH_OPT_CLR_UNBOUNDED", "cumulative_in_service_eac_wanyuan"])
        <= float(costs.loc["PATH_OPT_CLR_LE_2", "cumulative_in_service_eac_wanyuan"])
        + 1e-9
    )
