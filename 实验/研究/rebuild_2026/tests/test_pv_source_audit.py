from math import isclose

from rebuild_2026.pv_source_audit import read_asset_pv_coverage, read_hourly_pv_metadata, read_monthly_pv


def test_monthly_pv_source_has_growth_ratios_but_no_2021_station_mw():
    monthly, coverage = read_monthly_pv()
    assert len(monthly) == 84
    by_key = {(row["region_id"], row["year"], row["month"]): row for row in monthly}
    assert len(by_key) == len(monthly)
    assert not any(row["year"] in (2021, 2022) for row in monthly)
    assert all(row["source_value_unit"] == "not_stated_in_workbook" for row in monthly)
    assert isclose(by_key[("QX-00005", 2023, 5)]["source_value"], 32.3639)
    assert isclose(by_key[("QX-00005", 2025, 5)]["source_value"], 130.592)
    assert isclose(
        by_key[("QX-00005", 2023, 5)]["relative_to_2025_same_month"],
        32.3639 / 130.592,
        abs_tol=1e-9,
    )
    assert all(by_key[("QX-00007", 2025, month)]["relative_to_2025_same_month"] == 1 for month in range(1, 13))
    assert len(coverage) == 12
    assert [row["coverage_status"] for row in coverage if row["region_id"] == "QX-00005"] == [
        "missing", "missing", "full_12_months", "full_12_months", "full_12_months", "partial"
    ]


def test_2026_station_pv_sheet_cannot_fill_2021_2025_city_stations():
    coverage = {(row["region_id"], row["voltage_kv"]): row for row in read_asset_pv_coverage()}
    assert coverage[("QX-00005", 35)]["station_count"] == 8
    assert coverage[("QX-00005", 110)]["station_count"] == 21
    assert coverage[("QX-00007", 110)]["row_count"] == 0
    assert coverage[("QX-00007", 35)]["row_count"] == 0
    assert coverage[("QX-00005", 110)]["typical_time_years"] == "2026"


def test_hourly_coefficient_is_a_remapped_generator_scenario_not_station_observation():
    row = read_hourly_pv_metadata()[0]
    assert row["hour_count"] == 8760
    assert row["generator_capacity_mw"] == 3408
    assert row["original_year_scenario"] == "1/1"
    assert row["role_for_study"] == "system_generator_profile_not_observed_2025_station_distributed_pv"
