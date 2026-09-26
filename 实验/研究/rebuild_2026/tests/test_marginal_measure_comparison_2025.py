import pytest

from rebuild_2026.marginal_measure_comparison_2025 import build_marginal_measure_comparison


def test_marginal_comparison_uses_same_2024_starting_path_and_keeps_limits_visible():
    rows = build_marginal_measure_comparison()
    assert len(rows) == 3
    by_layer = {(row["study_region_id"], row["voltage_kv"]): row for row in rows}
    pizhou_35 = by_layer["QX-00005", 35]
    pizhou_110 = by_layer["QX-00005", 110]
    city_110 = by_layer["QX-00007", 110]
    assert pizhou_35["storage_only_need_station_count"] == 7
    assert pizhou_35["storage_only_modules_sum"] == 284
    assert pizhou_35["storage_only_stations_above_ten_module_quote"] == 7
    assert pizhou_35["transformer_only_simulated_capex_10k_cny"] == pytest.approx(2662.56)
    assert pizhou_110["storage_only_need_station_count"] == 4
    assert pizhou_110["storage_only_modules_sum"] == 248
    assert pizhou_110["transformer_only_simulated_capex_10k_cny"] == pytest.approx(2394.846667)
    assert city_110["storage_only_need_station_count"] == 0
    assert city_110["transformer_only_replaced_unit_count"] == 0
    assert all(row["prior_path_year"] == 2024 for row in rows)
    assert all("not_optimal" in row["conclusion_scope"] for row in rows)
    assert all(row["storage_minus_transformer_capex_10k_cny"] == pytest.approx(
        row["storage_only_simulated_capex_10k_cny"] - row["transformer_only_simulated_capex_10k_cny"], abs=1e-6
    ) for row in rows)
