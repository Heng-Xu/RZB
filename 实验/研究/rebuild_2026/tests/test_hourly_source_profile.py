from pathlib import Path

import pytest

from rebuild_2026.hourly_source_profile import (
    profile_city_archive,
    profile_pizhou_columns,
)


DATA = Path(__file__).resolve().parents[2] / "data/tuomin"


def test_pizhou_2025_columns_are_complete_but_not_auto_mapped():
    rows = profile_pizhou_columns(
        DATA / "电网建模数据_Agent整合版_V1.2/邳州主变负载率.xlsx"
    )
    assert len(rows) == 58
    assert {r["source_year"] for r in rows} == {2025}
    assert {r["unique_hours"] for r in rows} == {8760}
    assert sum(r["header_station_id"] == "BDZ-00005" for r in rows) == 4
    assert {r["voltage_assignment"] for r in rows} == {"unverified"}
    assert {r["first_missing_value_time"] for r in rows[:56]} == {"2025-03-09 02:00:00"}


def test_city_archive_profiles_all_members_without_trusting_excel_dimension():
    source = DATA / "补充数据/徐州市区脱敏.zip"
    if not source.is_file():
        pytest.skip("市区补充压缩包仅在本地收资目录提供")
    rows = profile_city_archive(source)
    assert len(rows) == 33
    assert {r["source_year"] for r in rows} == {2025}
    assert {r["voltage_assignment"] for r in rows} == {"unverified"}
    assert {r["unique_hours"] for r in rows} == {8339, 8531}
    assert max(r["longest_missing_run_hours"] for r in rows) == 120
    common = [r for r in rows if r["missing_hours"] == 421]
    assert len(common) == 32
    assert len({r["missing_mask_sha256"] for r in common}) == 1
    assert {r["longest_missing_start"] for r in common} == {"2025-11-17 00:00:00"}
    assert {r["longest_missing_end"] for r in common} == {"2025-11-21 23:00:00"}
    assert sum(bool(r["duplicate_of"]) for r in rows) == 1
    assert any(r["all_zero"] for r in rows)
