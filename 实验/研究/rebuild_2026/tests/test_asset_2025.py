from rebuild_2026.asset_2025 import read_assets, reconcile_capacity, reconcile_station_stats


def test_equipment_capacity_is_not_silently_substituted_for_annual_statistics():
    assets = read_assets()
    checks = {(r["region_id"], r["voltage_kv"]): r for r in reconcile_capacity(assets)}

    assert len(assets) == 121
    assert (checks["QX-00005", 35]["asset_station_count"], checks["QX-00005", 35]["asset_capacity_mva"]) == (8, 275)
    assert (checks["QX-00005", 110]["asset_station_count"], checks["QX-00005", 110]["asset_capacity_mva"]) == (21, 2239.5)
    assert checks["QX-00005", 110]["asset_minus_official_mva"] == 100
    assert checks["QX-00007", 110]["asset_station_count"] == 30
    assert checks["QX-00007", 110]["zero_capacity_placeholder_rows"] == 2
    assert checks["QX-00007", 110]["asset_minus_official_mva"] == 13
    assert all(r["voltage_kv"] == 110 for r in assets if r["region_id"] == "QX-00007")


def test_station_source_bridge_identifies_exact_pizhou_disagreements():
    rows = reconcile_station_stats(read_assets())
    assert len(rows) == 60
    differences = {(r["region_id"], r["voltage_kv"], r["station_id"]): r for r in rows if r["station_status"] != "match"}
    assert set(differences) == {
        ("QX-00005", 110, "BDZ-00005"),
        ("QX-00005", 35, "BDZ-00247"),
    }
    assert differences["QX-00005", 110, "BDZ-00005"]["asset_minus_load_stats_mva"] == 18.5
    assert differences["QX-00005", 35, "BDZ-00247"]["load_stats_capacity_mva"] == ""
