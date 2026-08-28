from __future__ import annotations

import numpy as np

from src.v32_storage import playback_continuous_storage
from src.v32_time_physics import (
    continuous_playback_row_audit,
    summarize_continuous_playback,
)


def _contract() -> dict:
    return {
        "storage": {
            "module": {"power_mw": 1.0, "energy_mwh": 2.0},
            "efficiency": {"charge": 1.0, "discharge": 1.0},
            "soc": {"min_fraction": 0.0, "max_fraction": 1.0},
        }
    }


def test_continuous_playback_summary_records_8760_audit_fields() -> None:
    profile = np.array([-2.0, 2.0, 0.0, 0.0])
    playback = playback_continuous_storage(
        profile,
        storage_modules=1,
        forward_limit_mw=1.0,
        reverse_limit_mw=1.0,
        contract=_contract(),
    )

    summary = summarize_continuous_playback(
        playback,
        profile,
        storage_modules=1,
        module_energy_mwh=2.0,
        soc_min_fraction=0.0,
        soc_max_fraction=1.0,
    )

    assert playback.feasible is True
    assert summary["continuous_points"] == 4
    assert summary["soc_min_mwh"] >= 0.0
    assert summary["soc_max_mwh"] <= 2.0 + 1e-8
    assert summary["soc_initial_mwh"] == summary["soc_final_mwh"]
    assert abs(summary["soc_residual_mwh"]) <= 1e-8
    assert summary["max_charge_mw"] <= 1.0 + 1e-8
    assert summary["max_discharge_mw"] <= 1.0 + 1e-8
    assert summary["physical_violation"] is False


def test_continuous_playback_row_audit_marks_direction_violation() -> None:
    flags = continuous_playback_row_audit(
        1.0,
        0.2,
        0.0,
        0.5,
        storage_energy_mwh=2.0,
        soc_min_fraction=0.0,
        soc_max_fraction=1.0,
    )
    assert flags["cross_zero_violation"] is True
    assert flags["physical_violation"] is True
