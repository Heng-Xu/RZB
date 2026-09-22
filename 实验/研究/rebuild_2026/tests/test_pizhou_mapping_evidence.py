from collections import Counter

from rebuild_2026.pizhou_mapping_evidence import match_evidence


def test_station_and_unit_mapping_are_cross_checked_against_extrema_and_peak_times():
    rows = match_evidence()
    assert len(rows) == 58
    assert Counter(row["station_status"] for row in rows) == {
        "supported_for_station_aggregation": 56,
        "late_station_sparse_all_zero": 2,
    }
    assert {row["resolved_station_id"] for row in rows} == {
        "BDZ-00005", "BDZ-00016", "BDZ-00021", "BDZ-00022", "BDZ-00026",
        "BDZ-00027", "BDZ-00028", "BDZ-00031", "BDZ-00037", "BDZ-00048",
        "BDZ-00056", "BDZ-00095", "BDZ-00096", "BDZ-00124", "BDZ-00135",
        "BDZ-00141", "BDZ-00146", "BDZ-00147", "BDZ-00162", "BDZ-00164",
        "BDZ-00172", "BDZ-00246", "BDZ-00247", "BDZ-00248", "BDZ-00255",
        "BDZ-00280", "BDZ-00290", "BDZ-00314", "BDZ-00325",
    }
    assert not any(row["unit_status"] == "ambiguous_between_two_units" for row in rows)
    timed = {row["resolved_station_id"] for row in rows if row["unit_status"] == "supported_by_peak_timestamp"}
    assert timed == {"BDZ-00247", "BDZ-00280", "BDZ-00325"}
    assert all(row["peak_time_margin_mw"] >= 2 for row in rows if row["unit_status"] == "supported_by_peak_timestamp")
    assert {row["resolved_station_id"] for row in rows if row["source_column"] in (12, 13)} == {"BDZ-00290"}
    assert {row["resolved_station_id"] for row in rows if row["source_column"] in (28, 29)} == {"BDZ-00247"}
