from rebuild_2026.source_load_scan_ceiling import build_research_rows, scan_ceiling


def test_scan_ceiling_is_outward_half_step() -> None:
    assert scan_ceiling(2.07, 1956.069053725234, 1099.23) == 4.0
    assert scan_ceiling(2.07, 1619.46968083569, 1307.315366) == 3.0


def test_research_proxy_scope_and_reconstruction() -> None:
    rows = {row["region_id"]: row for row in build_research_rows()}
    assert rows["QX-00005"]["voltage_scope"] == "110_and_35_combined"
    assert rows["QX-00005"]["observed_common_hours"] == 8759
    assert rows["QX-00007"]["observed_common_hours"] == 8339
    assert rows["QX-00005"]["policy_double_pv_ratio_stress"] > 1.5
    assert rows["QX-00007"]["policy_double_pv_ratio_stress"] < 0.7
    assert rows["QX-00005"]["rooftop_gross_area_m2"] > 89_000_000
    assert rows["QX-00005"]["equivalent_roof_fraction_for_2x_installed_proxy"] > 0.34
    assert 1.8 < rows["QX-00005"]["rooftop_40pct_nameplate_to_gross_load_proxy"] < 1.9
    assert rows["QX-00007"]["rooftop_scope_warning"] == "urban_core_three_districts_not_29_station_supply_boundary"
