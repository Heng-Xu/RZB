from collections import Counter, defaultdict
from datetime import datetime, timedelta

import pytest

from rebuild_2026.city_scenarios import CITY_SOURCE, MAPPING_AUDIT, build_city_scenarios, weekly_analogs


def test_weekly_analog_uses_nearest_available_week_on_each_side():
    hour = datetime(2025, 11, 6)
    observed = {hour - timedelta(weeks=3): 10.0, hour + timedelta(weeks=3): 20.0}
    assert weekly_analogs(hour, observed) == [10.0, 20.0]


def test_city_scenarios_keep_observed_and_imputed_results_separate():
    if not CITY_SOURCE.exists() or not MAPPING_AUDIT.exists():
        pytest.skip("市区原始时序或映射审计未安装")
    summary, hourly, station_scenes = build_city_scenarios()
    assert len(summary) == 4 * 30  # 29 站和 1 个同步片区汇总
    assert len(hourly) == 8760
    assert Counter(row["data_status"] for row in hourly) == {
        "observed": 8339,
        "weekly_analog_estimate": 421,
    }
    district = {row["variant"]: row for row in summary if row["model_station_id"] == "__DISTRICT__"}
    assert district["observed"]["forward_peak_mw"] == 1307.315366
    assert district["observed"]["forward_peak_time"] == "2025-08-21 21:00:00"
    assert district["observed"]["minimum_net_load_mw"] == 241.690265
    assert district["observed"]["reverse_peak_mw"] == 0
    assert district["observed"]["forward_h95_hours"] == 11
    assert district["weekly_mean"]["scenario_status"] == "planning_estimate"
    assert all(row["forward_peak_mw"] == 1307.315366 and row["forward_h95_hours"] == 11 for row in district.values())
    assert len(station_scenes) == 58
    by_kind = defaultdict(list)
    for row in station_scenes:
        by_kind[row["scenario_kind"]].append(row)
    assert set(by_kind) == {"district_forward_peak", "district_minimum_net_load"}
    for rows in by_kind.values():
        assert len(rows) == 29
        assert abs(sum(row["station_net_load_mw"] for row in rows) - rows[0]["district_net_load_mw"]) < 0.0001
