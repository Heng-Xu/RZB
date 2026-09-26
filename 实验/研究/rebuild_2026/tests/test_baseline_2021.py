from collections import Counter

import pytest

from rebuild_2026.baseline_2021 import (
    BASELINE_CLR_CAP,
    build_baseline,
    build_virtual_city_sensitivity,
    local_unit_catalog,
    read_csv,
    select_two_units,
)
from rebuild_2026.hourly_source_profile import OUTPUT_DIR


def test_minimum_two_unit_choice_uses_local_discrete_ratings():
    assert select_two_units(87.9, [40.0, 50.0, 63.0]) == (40.0, 50.0)
    assert select_two_units(80.0, [20.0, 40.0, 50.0], minimum_pair=(20.0, 50.0)) == (40.0, 50.0)
    with pytest.raises(ValueError, match="无法满足"):
        select_two_units(200.0, [40.0, 50.0, 63.0])


def test_2021_baseline_is_same_boundary_and_not_historical_capacity():
    stations, layers = build_baseline()
    assert len(stations) == 57
    assert Counter((row["study_region_id"], row["voltage_kv"]) for row in stations) == {
        ("QX-00005", 35): 8,
        ("QX-00005", 110): 20,
        ("QX-00007", 110): 29,
    }
    catalogs = local_unit_catalog()
    for row in stations:
        key = row["study_region_id"], row["voltage_kv"]
        assert row["simulation_transformer_count"] == 2
        assert row["simulation_unit_1_mva"] in catalogs[key]
        assert row["simulation_unit_2_mva"] in catalogs[key]
        assert row["forward_loading_fraction"] <= 1.0
        assert row["capacity_kind"] == "simulation_planning_baseline_not_historical_asset"
        assert row["reverse_2021_status"] == "not_evaluated_no_2021_station_pv_output"
    by_layer = {(row["study_region_id"], row["voltage_kv"]): row for row in layers}
    assert by_layer[("QX-00005", 35)]["estimated_district_peak_mw_2021"] == 80.76
    assert by_layer[("QX-00005", 110)]["estimated_district_peak_mw_2021"] == 731.77
    assert 1239 < by_layer[("QX-00007", 110)]["estimated_district_peak_mw_2021"] < 1240
    assert {key: row["simulation_capacity_mva_2021"] for key, row in by_layer.items()} == {
        ("QX-00005", 35): 128.0,
        ("QX-00005", 110): 1014.5,
        ("QX-00007", 110): 2403.0,
    }
    for key, row in by_layer.items():
        assert row["simulation_capacity_mva_2021"] == sum(
            station["simulation_capacity_mva_2021"]
            for station in stations
            if (station["study_region_id"], station["voltage_kv"]) == key
        )
        assert row["baseline_clr"] <= BASELINE_CLR_CAP
        assert row["forward_and_ratio_status"] == "forward_ratio_screen_pass"


def test_virtual_city_capacity_sensitivity_exposes_ratio_boundary():
    stations, layers = build_baseline()
    virtual = [row for row in stations if row["model_station_id"].startswith("SIM-CITY-")]
    assert {row["model_station_id"] for row in virtual} == {
        "SIM-CITY-KL", "SIM-CITY-XSZ", "SIM-CITY-YQ"
    }
    assert all(row["source_capacity_mva_2025"] == "" for row in virtual)
    cases = build_virtual_city_sensitivity(stations, layers)
    assert [row["unit_mva_each"] for row in cases] == [40.0, 50.0, 63.0, 80.0, 100.0]
    assert cases[0]["study_layer_capacity_mva"] == 2403.0
    assert cases[0]["ratio_status"] == "within_cap"
    assert cases[1]["ratio_status"] == "within_cap"
    assert cases[2]["ratio_status"] == "exceeds_cap"


def test_selected_near_two_baseline_has_audited_full_horizon_search():
    layers = read_csv(OUTPUT_DIR / "baseline_2021_layer_check.csv")
    search = read_csv(OUTPUT_DIR / "baseline_near2_full_horizon_search.csv")
    by_layer = {(r["study_region_id"], int(r["voltage_kv"])): r for r in layers}
    assert set(by_layer) == {("QX-00005", 35), ("QX-00005", 110), ("QX-00007", 110)}
    assert all(1.95 < float(r["baseline_clr"]) <= 2.0 for r in layers)
    for key, layer in by_layer.items():
        attempts = [r for r in search if (r["study_region_id"], int(r["voltage_kv"])) == key]
        assert attempts and attempts[-1]["full_horizon_rigid_feasible"] == "True"
        assert float(attempts[-1]["selected_initial_capacity_mva"]) == float(layer["simulation_capacity_mva_2021"])
        assert all(r["full_horizon_rigid_feasible"] == "False" for r in attempts[:-1])
