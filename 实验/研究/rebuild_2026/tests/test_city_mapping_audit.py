from collections import Counter

import pytest

from rebuild_2026.city_mapping_audit import CITY_SOURCE, MAPPING_SOURCE, audit_city_mapping


def test_city_mapping_separates_110_kv_coverage_from_other_series():
    if not CITY_SOURCE.exists() or not MAPPING_SOURCE.exists():
        pytest.skip("新交付市区时序或对应表未安装")
    rows, coverage = audit_city_mapping()
    assert len(rows) == 33
    assert Counter(row["matching_status"] for row in rows) == {
        "matched_city_110": 24,
        "name_absent_from_mapping": 4,
        "known_220_out_of_scope": 2,
        "known_but_not_city_110": 2,
        "duplicate_series": 1,
    }
    assert len(coverage) == 30
    assert sum(row["coverage_status"] == "matched_series" for row in coverage) == 24
    assert sum(row["asset_capacity_mva"] for row in coverage if row["coverage_status"] == "no_verified_series") == 632
    assert all(row["extrema_within_annual"] for row in rows if row["matching_status"] == "matched_city_110")
