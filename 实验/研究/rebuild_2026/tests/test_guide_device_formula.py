import pytest

from rebuild_2026.guide_device_formula import (
    device_hosting_interval_mw,
    device_open_capacity_intervals_mw,
)


def test_guide_63_keeps_new_storage_outside_tau_denominator():
    lower, upper = device_hosting_interval_mw(
        load_mw=20,
        other_generation_mw=5,
        existing_storage_charge_mw=0,
        transformer_rating_mva=10,
        power_factor=0.95,
        max_reverse_loading_rate=0.8,
        dg_max_output_factor=0.8,
        planned_new_storage_min_mw=0,
        planned_new_storage_max_mw=2,
    )
    assert lower == pytest.approx((20 - 5 + 10 * 0.95 * 0.8) / 0.8)
    assert upper == pytest.approx(lower + 2)


def test_guide_63_existing_charge_is_in_numerator_not_added_twice():
    without = device_hosting_interval_mw(20, 5, 0, 10, 0.95, 0.8, 0.8)[0]
    with_existing = device_hosting_interval_mw(20, 5, 1, 10, 0.95, 0.8, 0.8)[0]
    assert with_existing - without == pytest.approx(1 / 0.8)
    with pytest.raises(ValueError, match="τ_max"):
        device_hosting_interval_mw(20, 5, 0, 10, 0.95, 0.8, 0)


def test_guide_85_keeps_negative_open_capacity_for_classification():
    grid, registration = device_open_capacity_intervals_mw(8, 12, 10, 3)
    assert grid == (-2, 2)
    assert registration == (-5, -1)
