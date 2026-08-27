from __future__ import annotations

import pandas as pd
import pytest

from src.v3_planner import (
    StatePhysicsResult,
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
    strict = result["path_year_results"].query("path_id == 'PATH_OPT_CLR_LE_2'").sort_values("year")
    actions = result["path_action_results"].query("path_id == 'PATH_OPT_CLR_LE_2'")

    assert set(actions["candidate_id"]) == {"RETIRE-T1"}
    assert actions["year"].tolist() == [2022]
    assert strict["installed_capacity_mva"].tolist() == pytest.approx([80.0] * 4)
    assert strict["clr"].tolist() == pytest.approx([2.0, 80.0 / 42.0, 80.0 / 45.0, 1.6])
    assert strict["annual_in_service_eac_wanyuan"].tolist() == pytest.approx([10.0] * 4)
    assert strict["annual_capex_wanyuan"].tolist() == pytest.approx([20.0, 0.0, 0.0, 0.0])
    assert costs.loc["PATH_OPT_CLR_LE_2", "cumulative_in_service_eac_wanyuan"] == pytest.approx(40.0)
    assert costs.loc["PATH_OPT_CLR_UNBOUNDED", "cumulative_in_service_eac_wanyuan"] == pytest.approx(0.0)


def test_counterfactual_capacity_uses_2021_common_baseline_not_actual_annual_capacity() -> None:
    annual = _annual().assign(
        capacity_mva=[110.0, 120.0, 130.0, 140.0],
        baseline_capacity_mva=100.0,
    )

    result = optimize_joint_paths(annual, pd.DataFrame())
    unbounded = result["path_year_results"].query(
        "path_id == 'PATH_OPT_CLR_UNBOUNDED'"
    ).sort_values("year")

    assert unbounded["installed_capacity_mva"].tolist() == pytest.approx(
        [100.0] * 4
    )


def test_joint_optimizer_enforces_cost_inclusion_and_yearly_strict_limit() -> None:
    result = optimize_joint_paths(_annual(), _candidates())
    validate_path_inclusion(result["path_cost_breakdown"])
    strict = result["path_year_results"].query("path_id == 'PATH_OPT_CLR_LE_2'")
    assert (strict["clr"] <= 2.0 + 1e-9).all()
    assert set(result["path_year_results"]["path_id"]) == {
        "PATH_OPT_CLR_UNBOUNDED",
        "PATH_OPT_CLR_LE_2",
    }


def test_year_rows_replay_final_path_instead_of_rolling_prefix_optima() -> None:
    annual = pd.DataFrame(
        {
            "year": [2022, 2023, 2024, 2025],
            "region_id": ["QX-00005"] * 4,
            "voltage_kv": [110] * 4,
            "capacity_mva": [100.0] * 4,
            "positive_peak_mw": [45.0, 40.0, 40.0, 40.0],
            "reverse_peak_mw": [0.0] * 4,
            "reverse_beta": [0.8] * 4,
        }
    )
    candidates = pd.DataFrame(
        [
            {
                "candidate_id": "RETIRE-SMALL",
                "candidate_group": "RETIRE-GROUP",
                "region_id": "QX-00005",
                "voltage_kv": 110,
                "candidate_type": "retirement",
                "delta_capacity_mva": -10.0,
                "capex_base_wanyuan": 10.0,
                "eac_base_wanyuan_per_year": 1.0,
                "cost_status": "cost_center_and_range_available",
                "source_ref": "synthetic-test-source",
            },
            {
                "candidate_id": "RETIRE-LARGE",
                "candidate_group": "RETIRE-GROUP",
                "region_id": "QX-00005",
                "voltage_kv": 110,
                "candidate_type": "retirement",
                "delta_capacity_mva": -20.0,
                "capex_base_wanyuan": 20.0,
                "eac_base_wanyuan_per_year": 2.0,
                "cost_status": "cost_center_and_range_available",
                "source_ref": "synthetic-test-source",
            },
        ]
    )

    result = optimize_joint_paths(annual, candidates)
    strict = result["path_year_results"].query(
        "path_id == 'PATH_OPT_CLR_LE_2'"
    ).sort_values("year")
    actions = result["path_action_results"].query(
        "path_id == 'PATH_OPT_CLR_LE_2'"
    )
    cost = result["path_cost_breakdown"].query(
        "path_id == 'PATH_OPT_CLR_LE_2'"
    ).iloc[0]

    assert actions["candidate_id"].tolist() == ["RETIRE-LARGE"]
    assert actions["year"].tolist() == [2022]
    assert strict["installed_capacity_mva"].tolist() == pytest.approx([80.0] * 4)
    assert strict["annual_in_service_eac_wanyuan"].tolist() == pytest.approx([2.0] * 4)
    assert strict["cumulative_in_service_eac_wanyuan"].tolist() == pytest.approx(
        [2.0, 4.0, 6.0, 8.0]
    )
    assert strict.iloc[-1]["cumulative_in_service_eac_wanyuan"] == pytest.approx(
        cost["cumulative_in_service_eac_wanyuan"]
    )


def test_storage_action_uses_nonlinear_block_cost_for_module_delta() -> None:
    annual = pd.DataFrame(
        {
            "year": [2022, 2023, 2024, 2025],
            "region_id": ["QX-00005"] * 4,
            "voltage_kv": [110] * 4,
            "capacity_mva": [100.0] * 4,
            "positive_peak_mw": [50.0] * 4,
            "reverse_peak_mw": [77.1] * 4,
            "reverse_beta": [0.8] * 4,
        }
    )

    def storage_capex(modules: int) -> float:
        return 0.0 if modules == 0 else 6.8382 + 20.3618 * modules

    def storage_eac(modules: int) -> float:
        return storage_capex(modules) * 0.2

    result = optimize_joint_paths(
        annual,
        pd.DataFrame(),
        storage_capex_wanyuan_for_modules=storage_capex,
        storage_eac_wanyuan_for_modules=storage_eac,
    )
    actions = result["path_action_results"].query(
        "path_id == 'PATH_OPT_CLR_UNBOUNDED' and action_type == 'storage'"
    )
    cost = result["path_cost_breakdown"].query(
        "path_id == 'PATH_OPT_CLR_UNBOUNDED'"
    ).iloc[0]

    assert actions["storage_modules_delta"].tolist() == [11]
    assert actions["capex_wanyuan"].tolist() == pytest.approx([storage_capex(11)])
    assert actions["eac_wanyuan_per_year"].tolist() == pytest.approx([storage_eac(11)])
    assert cost["cumulative_in_service_eac_wanyuan"] == pytest.approx(
        storage_eac(11) * 4
    )


def test_aggregate_power_gap_does_not_fake_synchronous_clr_denominator() -> None:
    annual = _annual().assign(
        capacity_mva=100.0,
        positive_peak_mw=80.0,
        forward_requirement_mw=100.0,
    )

    result = optimize_joint_paths(annual, pd.DataFrame())
    unbounded = result["path_year_results"].query(
        "path_id == 'PATH_OPT_CLR_UNBOUNDED'"
    )

    assert unbounded["storage_modules"].tolist() == [50] * 4
    assert unbounded["p_plus_mw"].tolist() == pytest.approx([80.0] * 4)
    assert unbounded["clr"].tolist() == pytest.approx([1.25] * 4)


def test_state_physics_callback_controls_terminal_storage_and_synchronous_peak() -> None:
    calls: list[tuple[str, int, int, tuple[str, ...]]] = []

    def state_physics(
        region_id: str,
        voltage_kv: int,
        year: int,
        selected_candidate_ids: tuple[str, ...],
    ) -> StatePhysicsResult:
        calls.append((region_id, voltage_kv, year, selected_candidate_ids))
        if year != 2025:
            return StatePhysicsResult(feasible=True, required_storage_modules=0)
        return StatePhysicsResult(
            feasible=True,
            required_storage_modules=7,
            p_plus_mw=48.0,
            p_minus_mw=3.0,
            reason="full_playback_feasible",
        )

    result = optimize_joint_paths(
        _annual(),
        _candidates(),
        state_physics_evaluator=state_physics,
    )
    unbounded = result["path_year_results"].query(
        "path_id == 'PATH_OPT_CLR_UNBOUNDED'"
    ).sort_values("year")

    assert unbounded["storage_modules"].tolist() == [0, 0, 0, 7]
    assert unbounded.iloc[-1]["p_plus_mw"] == pytest.approx(48.0)
    assert unbounded.iloc[-1]["p_minus_mw"] == pytest.approx(3.0)
    assert any(year == 2025 for _region, _voltage, year, _ids in calls)


def test_state_physics_callback_can_reject_a_candidate_state() -> None:
    def state_physics(
        _region_id: str,
        _voltage_kv: int,
        year: int,
        selected_candidate_ids: tuple[str, ...],
    ) -> StatePhysicsResult:
        if year == 2025 and not selected_candidate_ids:
            return StatePhysicsResult(
                feasible=False,
                required_storage_modules=0,
                reason="storage_required_but_no_available_connection_bay",
                repair_candidate_ids=("RETIRE-T1",),
            )
        return StatePhysicsResult(feasible=True, required_storage_modules=0)

    result = optimize_joint_paths(
        _annual(),
        _candidates(),
        state_physics_evaluator=state_physics,
    )
    unbounded_actions = result["path_action_results"].query(
        "path_id == 'PATH_OPT_CLR_UNBOUNDED'"
    )

    assert set(unbounded_actions["candidate_id"]) == {"RETIRE-T1"}


def test_candidate_cannot_be_commissioned_before_available_year() -> None:
    candidates = _candidates().copy()
    candidates.loc[candidates["candidate_id"].eq("RETIRE-T1"), "available_year"] = 2025

    result = optimize_joint_paths(_annual(), candidates)
    strict_cost = result["path_cost_breakdown"].query(
        "path_id == 'PATH_OPT_CLR_LE_2'"
    ).iloc[0]

    assert strict_cost["status"] == "infeasible"


def test_terminal_physics_branches_compare_expansion_against_storage_cost() -> None:
    candidates = pd.DataFrame(
        [
            {
                "candidate_id": "FIX-SITE",
                "region_id": "QX-00005",
                "voltage_kv": 110,
                "candidate_type": "new_third_transformer",
                "delta_capacity_mva": 1.0,
                "capex_base_wanyuan": 5.0,
                "eac_base_wanyuan_per_year": 1.0,
                "cost_status": "cost_center_and_range_available",
            }
        ]
    )

    def state_physics(
        _region_id: str,
        _voltage_kv: int,
        year: int,
        selected_candidate_ids: tuple[str, ...],
    ) -> StatePhysicsResult:
        if year != 2025 or "FIX-SITE" in selected_candidate_ids:
            return StatePhysicsResult(True, 0)
        return StatePhysicsResult(
            True,
            10,
            improvement_candidate_ids=("FIX-SITE",),
        )

    result = optimize_joint_paths(
        _annual(),
        candidates,
        module_eac_wanyuan_per_year=10.0,
        state_physics_evaluator=state_physics,
    )
    actions = result["path_action_results"].query(
        "path_id == 'PATH_OPT_CLR_UNBOUNDED'"
    )

    assert actions["candidate_id"].tolist() == ["FIX-SITE"]


def test_path_inclusion_is_checked_per_region_voltage_group() -> None:
    costs = pd.DataFrame(
        [
            {
                "path_id": "PATH_OPT_CLR_UNBOUNDED",
                "region_id": "QX-00001",
                "voltage_kv": 110,
                "status": "feasible",
                "cumulative_in_service_eac_wanyuan": 20.0,
            },
            {
                "path_id": "PATH_OPT_CLR_LE_2",
                "region_id": "QX-00001",
                "voltage_kv": 110,
                "status": "feasible",
                "cumulative_in_service_eac_wanyuan": 10.0,
            },
            {
                "path_id": "PATH_OPT_CLR_UNBOUNDED",
                "region_id": "QX-00003",
                "voltage_kv": 110,
                "status": "infeasible",
                "cumulative_in_service_eac_wanyuan": float("inf"),
            },
            {
                "path_id": "PATH_OPT_CLR_LE_2",
                "region_id": "QX-00003",
                "voltage_kv": 110,
                "status": "infeasible",
                "cumulative_in_service_eac_wanyuan": float("inf"),
            },
        ]
    )

    with pytest.raises(ValueError, match="QX-00001.*110"):
        validate_path_inclusion(costs)


def test_terminal_infeasibility_preserves_prefix_diagnostics_but_rejects_complete_path() -> None:
    def state_physics(
        _region_id: str,
        _voltage_kv: int,
        year: int,
        _selected_candidate_ids: tuple[str, ...],
    ) -> StatePhysicsResult:
        if year == 2025:
            return StatePhysicsResult(
                False,
                0,
                reason="terminal_soc_infeasible",
            )
        return StatePhysicsResult(True, 0)

    result = optimize_joint_paths(
        _annual().assign(positive_peak_mw=60.0),
        pd.DataFrame(),
        state_physics_evaluator=state_physics,
    )

    for _path_id, group in result["path_year_results"].groupby("path_id"):
        assert group["year"].tolist() == [2022, 2023, 2024, 2025]
        assert group["status"].tolist() == [
            "feasible",
            "feasible",
            "feasible",
            "infeasible",
        ]
        assert set(group["complete_path_status"]) == {"infeasible"}
        assert set(group["complete_path_reason"]) == {
            "no_complete_2022_2025_feasible_path"
        }
