import csv
from pathlib import Path

import pytest

from rebuild_2026.official_annual import read_official_annual, write_official_annual


SOURCE = (
    Path(__file__).resolve().parents[2]
    / "data/tuomin/电网建模数据_Agent整合版_V1.2/近5年容载比.xlsx"
)


def test_reads_only_confirmed_layers_and_converts_wan_units():
    rows = read_official_annual(SOURCE)
    assert len(rows) == 15
    assert {(r["region_id"], r["voltage_kv"]) for r in rows} == {
        ("QX-00005", 110),
        ("QX-00005", 35),
        ("QX-00007", 110),
    }

    pizhou_2025 = next(
        r for r in rows
        if (r["region_id"], r["voltage_kv"], r["year"]) == ("QX-00005", 110, 2025)
    )
    assert pizhou_2025["capacity_mva"] == 2139.5
    assert pizhou_2025["reported_downward_load_mw"] == pytest.approx(956.45)
    assert pizhou_2025["reported_clr"] == 2.24
    assert pizhou_2025["source_row"] == 19

    city_2021 = next(
        r for r in rows
        if (r["region_id"], r["voltage_kv"], r["year"]) == ("QX-00007", 110, 2021)
    )
    assert city_2021["capacity_mva"] == 3113.5
    assert city_2021["reported_downward_load_mw"] == pytest.approx(1449.77)
    assert city_2021["source_row"] == 9
    assert all(
        abs(r["capacity_mva"] / r["reported_downward_load_mw"] - r["reported_clr"])
        < 0.005
        for r in rows
    )


def test_writes_a_traceable_annual_csv(tmp_path):
    target = tmp_path / "official_annual.csv"
    write_official_annual(SOURCE, target)
    with target.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 15
    assert rows[0]["source_sheet"] == "Sheet1"
    assert len(rows[0]["source_sha256"]) == 64
    assert rows[0]["source_file"].endswith("近5年容载比.xlsx")
    assert rows[1]["reported_downward_load_mw"] == "1432.369977"
    assert b"\r\n" not in target.read_bytes()
