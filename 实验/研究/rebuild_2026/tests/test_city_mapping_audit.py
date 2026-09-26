from collections import Counter

import pytest

from rebuild_2026.city_mapping_audit import CITY_SOURCE, MAPPING_SOURCE, audit_city_mapping


def test_city_mapping_uses_hourly_cohort_and_preserves_boundary_conflicts():
    if not CITY_SOURCE.exists() or not MAPPING_SOURCE.exists():
        pytest.skip("新交付市区时序或对应表未安装")
    rows, coverage = audit_city_mapping()
    assert len(rows) == 33
    assert Counter(row["matching_status"] for row in rows) == {
        "matched_city_110": 24,
        "confirmed_city_110_source_region_conflict": 2,
        "confirmed_city_110_no_station_id": 3,
        "known_220_out_of_scope": 2,
        "known_but_not_city_110": 1,
        "duplicate_series": 1,
    }
    assert sum(row["in_study_cohort"] for row in rows) == 29
    by_file = {row["archive_member"].rsplit("/", 1)[-1]: row for row in rows}
    assert by_file["zu.xlsx"]["station_id"] == "BDZ-00183"
    assert by_file["jh.xlsx"]["station_id"] == "BDZ-00055"
    assert by_file["zu.xlsx"]["source_asset_region_id"] == "QX-00003"
    assert by_file["jh.xlsx"]["source_asset_region_id"] == "QX-00009"
    assert all(by_file[name]["user_scope_confirmation"] for name in ("jh.xlsx", "kl.xlsx", "xsz.xlsx", "yq.xlsx", "zu.xlsx"))
    assert all(by_file[name]["study_region_id"] == "QX-00007" for name in ("jh.xlsx", "kl.xlsx", "xsz.xlsx", "yq.xlsx", "zu.xlsx"))
    assert all(not by_file[name]["station_id"] for name in ("kl.xlsx", "xsz.xlsx", "yq.xlsx"))
    assert {by_file[name]["simulation_station_id"] for name in ("kl.xlsx", "xsz.xlsx", "yq.xlsx")} == {
        "SIM-CITY-KL", "SIM-CITY-XSZ", "SIM-CITY-YQ"
    }
    assert all(by_file[name]["station_identity_basis"] == "simulation" for name in ("kl.xlsx", "xsz.xlsx", "yq.xlsx"))
    model_ids = [row["model_station_id"] for row in rows if row["in_study_cohort"]]
    assert len(model_ids) == len(set(model_ids)) == 29
    assert all(by_file[name]["voltage_evidence"] == "user_confirmation" for name in ("kl.xlsx", "xsz.xlsx", "yq.xlsx"))
    assert all(by_file[name]["voltage_kv"] == 110 for name in ("kl.xlsx", "xsz.xlsx", "yq.xlsx"))
    assert not by_file["ft.xlsx"]["in_study_cohort"]
    assert not by_file["qh.xlsx"]["in_study_cohort"]
    assert by_file["ft.xlsx"]["voltage_kv"] == 220
    assert len(coverage) == 30
    assert sum(row["coverage_status"] == "in_hourly_cohort" for row in coverage) == 24
    assert sum(row["asset_capacity_mva"] for row in coverage if row["coverage_status"] == "outside_hourly_cohort") == 632
    assert all(row["extrema_within_annual"] for row in rows if row["matching_status"] == "matched_city_110")
