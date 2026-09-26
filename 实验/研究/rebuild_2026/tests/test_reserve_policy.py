"""验证较高容载比来自保留实有容量和停运承载约束。"""

from rebuild_2026.baseline_historical_proxy import build
from rebuild_2026.joint_lifecycle_optimizer import cost_factors, solve_layer


def test_reported_2021_regional_capacity_is_preserved_by_proxy():
    _, layers = build()
    by_layer = {(r["study_region_id"], r["voltage_kv"]): r for r in layers}
    assert by_layer["QX-00005", 35]["proxy_capacity_mva"] == 245.0
    assert by_layer["QX-00005", 110]["proxy_capacity_mva"] == 2027.0
    assert abs(by_layer["QX-00007", 110]["allocation_gap_mva"]) < 1.0


def test_equal_cost_prefers_retaining_capacity_and_contingency_changes_choice():
    layer = ("TEST", 35)
    station = (*layer, "S1")
    baseline = {station: {"simulation_unit_1_mva": 8,
                          "simulation_unit_2_mva": 8,
                          "estimated_forward_peak_mw_2021": 10}}
    scenes = {(station, year): {"estimated_station_forward_peak_mw": 10,
                                "reverse_screen_mw": 0}
              for year in (2022, 2023, 2024, 2025)}
    durations = {station: {"forward_d95_max_run_hours": 1,
                           "reverse_d95_max_run_hours": 1}}
    peaks = {(*layer, 2021): 10, **{(*layer, year): 10 for year in (2022, 2023, 2024, 2025)}}
    args = (layer, baseline, scenes, durations, peaks,
            {layer: [4, 8, 10]}, {35: 1}, cost_factors(), 2.4, False)
    common = {"tie_allowed": False, "allow_capacity_release": True,
              "require_existing_tie_operation": False,
              "prefer_reserve_at_equal_cost": True}
    _, years, _, summary = solve_layer(*args, **common)
    assert summary["objective_npv_10k_cny"] == 0
    assert all(r["selected_capacity_mva"] == 16 for r in years)
    assert all(r["actual_clr"] == 1.6 for r in years)

    weaker_baseline = {station: {"simulation_unit_1_mva": 4,
                                 "simulation_unit_2_mva": 8,
                                 "estimated_forward_peak_mw_2021": 10}}
    weaker_args = (layer, weaker_baseline, scenes, durations, peaks,
                   {layer: [4, 8, 10]}, {35: 1}, cost_factors(), 2.4, False)
    _, normal_years, _, _ = solve_layer(*weaker_args, **common)
    assert all(r["selected_capacity_mva"] == 12 for r in normal_years)
    stations, contingency_years, _, _ = solve_layer(
        *weaker_args, **common, contingency_service_fraction=0.7)
    assert all(r["selected_unit_1_mva"] >= 8 for r in stations)
    assert all(r["selected_capacity_mva"] >= 16 for r in contingency_years)
