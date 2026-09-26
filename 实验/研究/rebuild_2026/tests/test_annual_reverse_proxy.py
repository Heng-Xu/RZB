from collections import Counter
from datetime import datetime
from math import isclose

import pytest

from rebuild_2026.annual_reverse_proxy import build_annual_reverse_proxy
from rebuild_2026.baseline_2021 import STATION_INPUTS, read_csv


@pytest.fixture(scope="module")
def reverse_proxy():
    return build_annual_reverse_proxy()


def test_reverse_proxy_reconstructs_2025_and_keeps_historical_assumptions_visible(reverse_proxy):
    stations, layers = reverse_proxy
    assert len(stations) == 57 * 5 * 4
    assert len(layers) == 3 * 5 * 4
    keys = [(row["study_region_id"], row["voltage_kv"], row["model_station_id"], row["year"], row["variant"]) for row in stations]
    assert len(keys) == len(set(keys))
    known_reverse = {
        (row["study_region_id"], int(row["voltage_kv"]), row["model_station_id"]): float(row["reverse_peak_mw"])
        for row in read_csv(STATION_INPUTS)
    }
    for row in stations:
        hour = datetime.fromisoformat(row["template_time_2025"])
        assert hour.month in (3, 4, 5, 9, 10, 11)
        assert hour.weekday() < 5 and 10 <= hour.hour <= 15
        assert row["night_sample_hours_2025"] > 0
        assert row["pv_output_proxy_mw_2025"] >= 0
        assert isclose(
            row["net_at_2025_template_proxy_mw"],
            row["annual_load_scale"] * row["gross_load_proxy_mw_2025"] - row["annual_pv_scale"] * row["pv_output_proxy_mw_2025"],
            abs_tol=2e-6,
        )
        if row["year"] == 2025:
            # 邳州以甲方年度净峰校准2025样本，毛负荷比例不必等于1。
            # 出力比例为1时，校准前后净负荷的差应仅来自毛负荷校准项。
            assert row["annual_pv_scale"] == 1.0
            correction = ((row["annual_load_scale"] - 1)
                          * row["gross_load_proxy_mw_2025"])
            assert isclose(row["net_at_2025_template_proxy_mw"],
                           row["observed_net_at_template_mw_2025"] + correction,
                           abs_tol=2e-6)
            assert row["reverse_at_template_proxy_mw"] <= (
                known_reverse[row["study_region_id"], row["voltage_kv"], row["model_station_id"]]
                + max(0, -correction) + 2e-6)
        elif row["year"] in (2021, 2022):
            assert row["pv_scale_basis"] in (
                "geometric_backcast_from_2023_2024_county_values",
                "2023_county_same_month_level_held_back_as_early_high_stress",
            )
            assert row["scenario_status"] == "historical_simulation_proxy_not_observed"
    summary = {(row["study_region_id"], row["voltage_kv"], row["year"], row["variant"]): row for row in layers}
    assert all(row["baseline_upper_bound_exceed_count"] == 0 for row in layers if row["year"] == 2021)
    assert summary[("QX-00005", 35, 2024, "night_central")]["baseline_upper_bound_exceed_count"] == 3
    assert summary[("QX-00005", 110, 2025, "night_central")]["baseline_upper_bound_exceed_count"] == 4
    assert Counter(row["station_count"] for row in layers) == {8: 20, 20: 20, 29: 20}


def test_early_high_pv_stress_is_no_less_than_backcast_at_same_station(reverse_proxy):
    stations, _ = reverse_proxy
    values = {
        (row["study_region_id"], row["voltage_kv"], row["model_station_id"], row["year"], row["variant"]): row
        for row in stations
    }
    for row in stations:
        if row["year"] not in (2021, 2022) or row["variant"] != "night_central":
            continue
        alternative = values[row["study_region_id"], row["voltage_kv"], row["model_station_id"], row["year"], "early_pv_high"]
        assert alternative["annual_pv_scale"] >= row["annual_pv_scale"]
        assert alternative["net_at_2025_template_proxy_mw"] <= row["net_at_2025_template_proxy_mw"] + 1e-6
