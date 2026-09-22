from rebuild_2026.feeder_2025 import read_feeders, read_spans


def test_six_feeder_boundary_comes_from_original_table():
    feeders = read_feeders()
    assert len(feeders) == 6
    assert {row["station_id"] for row in feeders} == {"BDZ-00027", "BDZ-00048"}
    assert {row["feeder_id"] for row in feeders if row["station_id"] == "BDZ-00027"} == {
        "PZXL-00092", "PZXL-00097", "PZXL-00099"
    }
    hdong = next(row for row in feeders if row["feeder_id"] == "PZXL-00154")
    assert hdong["reported_2025_max_active_power_mw"] == 0
    assert hdong["reported_2025_max_current_a"] == 544.57


def test_original_span_lengths_retain_50_and_60_meters():
    spans, summaries = read_spans()
    summary = {row["feeder_id"]: row for row in summaries}
    assert len(spans) == 1124
    assert sum(row["length_50m_count"] for row in summaries) == 935
    assert sum(row["length_60m_count"] for row in summaries) == 189
    assert summary["PZXL-00173"]["length_50m_count"] == 49
    assert summary["PZXL-00173"]["length_60m_count"] == 189
    assert all(row["other_length_count"] == 0 for row in summaries)
