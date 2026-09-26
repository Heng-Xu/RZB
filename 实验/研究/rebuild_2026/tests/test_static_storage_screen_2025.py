from collections import Counter

import pytest

from rebuild_2026.incremental_cost import storage_replicated_package_capex_10k_cny
from rebuild_2026.static_storage_screen_2025 import (
    build_static_storage_screen,
    module_count_for_peak,
)


def test_rectangular_d95_proxy_sizes_power_and_nominal_energy_separately():
    assert module_count_for_peak(0, 3) == (0, 0, 0, 0)
    assert module_count_for_peak(0.12, 2) == (2, 2, 2, pytest.approx(0.24))
    assert module_count_for_peak(1.0, 3) == (10, 14, 14, pytest.approx(3.0))


def test_station_screen_is_three_capacity_cases_for_the_same_57_stations():
    rows = build_static_storage_screen()
    assert len(rows) == 171
    assert Counter(row["capacity_case"] for row in rows) == {
        "hold_2021_simulation_capacity": 57,
        "hold_2024_transformer_path_capacity": 57,
        "transformer_only_2025_capacity": 57,
    }
    assert len({(row["study_region_id"], row["voltage_kv"], row["model_station_id"]) for row in rows}) == 57
    assert all(row["year"] == 2025 for row in rows)
    assert all("no_SOC_site_or_guide_certification" in row["technical_status"] for row in rows)
    assert all(row["forward_h95_hours"] >= row["forward_d95_max_run_hours"] for row in rows)
    assert all(row["reverse_h95_hours"] >= row["reverse_d95_max_run_hours"] for row in rows)
    assert sum(
        row["required_modules_scenario_proxy"] > 0
        for row in rows if row["capacity_case"] == "hold_2024_transformer_path_capacity"
    ) == 11


def test_storage_screen_cost_and_station_peak_are_explicit_scenario_proxies():
    rows = build_static_storage_screen()
    by_case = {(row["model_station_id"], row["capacity_case"]): row for row in rows}
    held = by_case["BDZ-00246", "hold_2021_simulation_capacity"]
    upgraded = by_case["BDZ-00246", "transformer_only_2025_capacity"]
    assert held["forward_power_shortfall_mw"] == pytest.approx(26.7 - 0.95 * 24)
    assert held["forward_rectangular_energy_proxy_mwh"] == pytest.approx(held["forward_power_shortfall_mw"] * 3)
    assert held["required_modules_scenario_proxy"] == 70
    assert held["replicated_package_capex_10k_cny"] == pytest.approx(storage_replicated_package_capex_10k_cny(70), abs=1e-6)
    assert held["price_basis"] == "ten_cabinet_package_replication_assumption"
    assert upgraded["required_modules_scenario_proxy"] == 0
    assert upgraded["replicated_package_capex_10k_cny"] == 0
    assert upgraded["price_basis"] == "zero_no_incremental_investment"
