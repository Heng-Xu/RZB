from __future__ import annotations

import pandas as pd
import pytest
import yaml
from pathlib import Path

from src.v32_actual_pipeline import _policy_cost_comparison
from src.v32_policy import validate_path_inclusion


def test_v32_contract_and_policy_paths_use_actual_baseline() -> None:
    contract = yaml.safe_load((Path(__file__).resolve().parents[1] / "model_contract.yaml").read_text(encoding="utf-8"))
    assert contract["contract"]["version"] == "3.2.0"
    assert contract["planning_baseline"]["formula"] == "S0 = actual_2021_installed_capacity"
    assert contract["optimization"]["direct_policy_cost_comparison_allowed"] is True
    assert contract["optimization"]["retirement_candidates_in_primary_policy_model"] is False


def test_v32_cost_comparison_is_only_direct_when_both_paths_are_feasible() -> None:
    costs = pd.DataFrame(
        [
            {"path_id": "PATH_OPT_CLR_UNBOUNDED", "region_id": "QX-A", "voltage_kv": 110, "status": "feasible", "cumulative_in_service_eac_wanyuan": 100.0},
            {"path_id": "PATH_OPT_CLR_LE_2", "region_id": "QX-A", "voltage_kv": 110, "status": "feasible", "cumulative_in_service_eac_wanyuan": 125.0},
            {"path_id": "PATH_OPT_CLR_UNBOUNDED", "region_id": "QX-B", "voltage_kv": 110, "status": "infeasible", "cumulative_in_service_eac_wanyuan": float("nan")},
            {"path_id": "PATH_OPT_CLR_LE_2", "region_id": "QX-B", "voltage_kv": 110, "status": "infeasible", "cumulative_in_service_eac_wanyuan": float("nan")},
        ]
    )
    result = _policy_cost_comparison(costs).set_index("region_id")
    assert bool(result.loc["QX-A", "direct_comparison_allowed"]) is True
    assert result.loc["QX-A", "rigid_minus_elastic_eac_wanyuan"] == pytest.approx(25.0)
    assert bool(result.loc["QX-B", "direct_comparison_allowed"]) is False
    assert pd.isna(result.loc["QX-B", "rigid_minus_elastic_eac_wanyuan"])


def test_v32_path_inclusion_is_checked_on_same_actual_baseline() -> None:
    costs = pd.DataFrame(
        [
            {"path_id": "PATH_OPT_CLR_UNBOUNDED", "region_id": "QX-A", "voltage_kv": 110, "status": "feasible", "cumulative_in_service_eac_wanyuan": 100.0},
            {"path_id": "PATH_OPT_CLR_LE_2", "region_id": "QX-A", "voltage_kv": 110, "status": "feasible", "cumulative_in_service_eac_wanyuan": 125.0},
        ]
    )
    assert validate_path_inclusion(costs) is True
