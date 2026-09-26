from collections import Counter, defaultdict

from rebuild_2026.pizhou_station_scenarios import build_station_scenarios


def test_pizhou_station_scenes_reconcile_with_synchronous_district_peaks():
    stations, scenes = build_station_scenarios()
    assert len(stations) == 28
    assert Counter(row["voltage_kv"] for row in stations) == {110: 20, 35: 8}
    assert all(row["observed_hours"] == 8759 for row in stations)
    assert len(scenes) == 56
    by_scene = defaultdict(list)
    for row in scenes:
        by_scene[(row["voltage_kv"], row["scenario_kind"])].append(row)
    assert set(by_scene) == {
        (110, "district_forward_peak"), (110, "district_reverse_peak"),
        (35, "district_forward_peak"), (35, "district_reverse_peak"),
    }
    for rows in by_scene.values():
        assert abs(sum(row["station_net_load_mw"] for row in rows) - rows[0]["district_net_load_mw"]) < 0.0001
