from __future__ import annotations

import pytest

from src.net_model import Station, Transformer


def _station(capacities: list[float], mode: str = "parallel") -> Station:
    transformers = [
        Transformer("BDZ-T", f"#{idx}", capacity, mode)
        for idx, capacity in enumerate(capacities, start=1)
    ]
    return Station("BDZ-T", "QX-T", "QX-T-110", "test", transformers)


def test_two_equal_parallel_transformers_beta_is_one_unit_out_ratio() -> None:
    station = _station([50.0, 50.0])
    assert station.beta_eff({"split_mode": 0.8}) == pytest.approx(0.5)


def test_unequal_parallel_transformers_use_largest_unit_not_unit_count() -> None:
    station = _station([40.0, 30.0, 30.0])
    assert station.beta_eff({"split_mode": 0.8}) == pytest.approx(0.6)


def test_split_transformers_keep_per_device_beta() -> None:
    station = _station([50.0, 50.0], mode="split")
    assert station.beta_eff({"split_mode": 0.8}) == pytest.approx(0.8)
