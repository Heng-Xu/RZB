from collections import defaultdict
from math import isclose

from rebuild_2026.annual_forward_scenes import build_annual_forward_scenes
from rebuild_2026.baseline_2021 import build_baseline


def test_annual_forward_scenes_keep_station_sums_and_sample_boundary():
    stations, layers = build_annual_forward_scenes()
    assert len(stations) == 285
    assert len(layers) == 15
    sums = defaultdict(float)
    counts = defaultdict(int)
    for row in stations:
        key = row["study_region_id"], row["voltage_kv"], row["year"]
        sums[key] += row["estimated_station_net_load_mw"]
        counts[key] += 1
        assert row["scenario_kind"] == "synchronous_district_forward_peak_proxy"
        expected_time_status = ("2025_observed_time_rescaled_to_official_annual_peak"
                                if row["year"] == 2025 and row["study_region_id"] == "QX-00005" else
                                "observed_2025" if row["year"] == 2025 else
                                "2025_time_template_not_observed_in_target_year")
        assert row["time_status"] == expected_time_status
    for row in layers:
        key = row["study_region_id"], row["voltage_kv"], row["year"]
        assert counts[key] == row["station_count"]
        assert isclose(sums[key], row["estimated_synchronous_forward_peak_mw"], abs_tol=0.0001)
        assert row["reverse_scenario_status"] == "not_derived_from_forward_scaling"
    by_key = {(row["study_region_id"], row["voltage_kv"], row["year"]): row for row in layers}
    assert by_key[("QX-00005", 110, 2021)]["estimated_synchronous_forward_peak_mw"] == 731.77
    assert by_key[("QX-00005", 35, 2021)]["estimated_synchronous_forward_peak_mw"] == 80.76
    assert by_key[("QX-00005", 110, 2025)]["estimated_synchronous_forward_peak_mw"] == 956.45
    assert by_key[("QX-00005", 35, 2025)]["estimated_synchronous_forward_peak_mw"] == 147.65
    assert by_key[("QX-00007", 110, 2025)]["estimated_synchronous_forward_peak_mw"] == 1307.315366
    assert by_key[("QX-00007", 110, 2021)]["estimated_synchronous_forward_peak_mw"] < 1449.77
    _, baseline_layers = build_baseline()
    for baseline in baseline_layers:
        key = baseline["study_region_id"], baseline["voltage_kv"], 2021
        assert by_key[key]["estimated_synchronous_forward_peak_mw"] == baseline["estimated_district_peak_mw_2021"]
