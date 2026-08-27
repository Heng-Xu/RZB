"""v3.2 储能年度连续时序验证。"""
from __future__ import annotations

import numpy as np

from src.milp_planner import minimum_storage_modules
from src.v32_storage import (
    minimum_storage_modules_continuous,
    playback_continuous_storage,
)


def _contract() -> dict:
    return {
        "storage": {
            "module": {"power_mw": 1.0, "energy_mwh": 2.0},
            "efficiency": {"charge": 1.0, "discharge": 1.0},
            "soc": {"min_fraction": 0.0, "max_fraction": 1.0},
        }
    }


def test_continuous_chronology_can_transfer_energy_between_days() -> None:
    day_charge = np.zeros(24)
    day_charge[12] = -2.0  # 反向限额 1 MW -> 必须充 1 MWh
    day_discharge = np.zeros(24)
    day_discharge[12] = 2.0  # 正向限额 1 MW -> 必须放 1 MWh

    # 独立日循环要求每一天自身能量闭合，因此两个单向日不可能单独通过。
    daily = minimum_storage_modules(
        [day_charge, day_discharge],
        forward_limit_mw=1.0,
        reverse_limit_mw=1.0,
        contract=_contract(),
        max_modules=20,
    )
    assert daily is None

    # 连续 48h 时序允许第1天吸收能量、第2天释放，并只要求整个周期首尾闭合。
    profile = np.concatenate([day_charge, day_discharge])
    continuous = minimum_storage_modules_continuous(
        profile,
        forward_limit_mw=1.0,
        reverse_limit_mw=1.0,
        contract=_contract(),
        max_modules=20,
    )
    assert continuous == 1

    playback = playback_continuous_storage(
        profile,
        storage_modules=1,
        forward_limit_mw=1.0,
        reverse_limit_mw=1.0,
        contract=_contract(),
    )
    assert playback.feasible is True
    assert np.max(playback.net_after_mw) <= 1.0 + 1e-8
    assert -np.min(playback.net_after_mw) <= 1.0 + 1e-8
    assert abs(playback.soc_residual_mwh) <= 1e-8


def test_continuous_storage_preserves_no_cross_zero_dispatch_rule() -> None:
    profile = np.array([-2.0, -0.5, 0.0, 0.5, 2.0] + [0.0] * 43)
    result = playback_continuous_storage(
        profile,
        storage_modules=2,
        forward_limit_mw=1.0,
        reverse_limit_mw=1.0,
        contract=_contract(),
    )
    if result.feasible:
        assert (result.charge_mw[profile >= 0] <= 1e-8).all()
        assert (result.discharge_mw[profile <= 0] <= 1e-8).all()
        assert not ((result.charge_mw > 1e-8) & (result.discharge_mw > 1e-8)).any()
