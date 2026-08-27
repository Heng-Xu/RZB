from __future__ import annotations

from pathlib import Path

import numpy as np
import yaml

from src.v3_time_physics import evaluate_station_profiles


ROOT = Path(__file__).resolve().parents[1]


def _contract() -> dict:
    return yaml.safe_load((ROOT / "model_contract.yaml").read_text(encoding="utf-8"))


def test_station_profile_requires_an_approved_connection_site() -> None:
    profile = np.array([-70.0] + [20.0] * 4 + [0.0] * 19)

    result = evaluate_station_profiles(
        [profile],
        unit_capacities_mva=[40.0, 40.0],
        operation_modes={"split"},
        site_available=False,
        contract=_contract(),
    )

    assert result.required_storage_modules > 0
    assert result.feasible is False
    assert result.reason == "storage_required_but_no_available_connection_bay"


def test_station_profile_enforces_daily_soc_energy_balance() -> None:
    profile = np.array([-40.0] * 18 + [1.0] * 6)

    result = evaluate_station_profiles(
        [profile],
        unit_capacities_mva=[20.0, 20.0],
        operation_modes={"parallel"},
        site_available=True,
        contract=_contract(),
    )

    assert result.feasible is False
    assert result.reason == "daily_storage_dispatch_infeasible"


def test_discrete_expansion_can_remove_storage_dispatch_requirement() -> None:
    profile = np.array([-70.0] + [20.0] * 4 + [0.0] * 19)

    base = evaluate_station_profiles(
        [profile],
        unit_capacities_mva=[40.0, 40.0],
        operation_modes={"split"},
        site_available=True,
        contract=_contract(),
    )
    expanded = evaluate_station_profiles(
        [profile],
        unit_capacities_mva=[40.0, 40.0, 50.0],
        operation_modes={"split"},
        site_available=True,
        contract=_contract(),
    )

    assert base.feasible is True
    assert base.required_storage_modules > 0
    assert expanded.feasible is True
    assert expanded.required_storage_modules == 0
