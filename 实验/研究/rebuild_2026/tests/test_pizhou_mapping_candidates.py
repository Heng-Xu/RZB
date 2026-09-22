from collections import Counter
from pathlib import Path

from rebuild_2026.pizhou_mapping_candidates import build_mapping_candidates


DATA = Path(__file__).resolve().parents[2] / "data/tuomin"


def test_candidate_mapping_separates_voltage_without_claiming_approval():
    rows = build_mapping_candidates(
        DATA / "电网建模数据_Agent整合版_V1.2/110（35）kv设备明细.xlsx",
        Path(__file__).resolve().parents[1]
        / "source_audit/pizhou_2025_column_profile.csv",
    )
    assert len(rows) == 58
    assert Counter(row["candidate_voltage_kv"] for row in rows) == {110: 42, 35: 16}
    assert {row["mapping_status"] for row in rows} == {"provisional"}
    by_column = {row["source_column"]: row for row in rows}
    assert by_column[12]["candidate_station_id"] == "BDZ-00290"
    assert by_column[13]["candidate_station_id"] == "BDZ-00290"
    assert by_column[28]["candidate_station_id"] == "BDZ-00247"
    assert by_column[29]["candidate_station_id"] == "BDZ-00247"
    assert by_column[58]["data_status"] == "sparse_all_zero"
