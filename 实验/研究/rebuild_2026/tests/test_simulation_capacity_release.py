"""验证年度低谷下，仿真减容会进入实际容载比分子。"""

import pytest

from rebuild_2026.joint_lifecycle_optimizer import cost_factors, solve_layer


def test_release_restores_strict_annual_ratio_feasibility():
    layer = ("TEST", 35)
    station = (*layer, "S1")
    baseline = {station: {"simulation_unit_1_mva": 8,
                          "simulation_unit_2_mva": 8,
                          "estimated_forward_peak_mw_2021": 8}}
    loads = {2022: 10, 2023: 6, 2024: 10, 2025: 10}
    scenes = {(station, year): {"estimated_station_forward_peak_mw": load,
                                "reverse_screen_mw": 0}
              for year, load in loads.items()}
    durations = {station: {"forward_d95_max_run_hours": 1,
                           "reverse_d95_max_run_hours": 1}}
    peaks = {(*layer, 2021): 8, **{(*layer, year): load for year, load in loads.items()}}
    arguments = (layer, baseline, scenes, durations, peaks,
                 {layer: [4, 8, 10]}, {35: 1}, cost_factors(), 2.0, True)
    options = {"tie_allowed": False, "require_existing_tie_operation": False,
               "policy_peak_basis": "annual"}

    with pytest.raises(ValueError, match="infeasible"):
        solve_layer(*arguments, **options)

    stations, years, _, _ = solve_layer(*arguments, **options,
                                        allow_capacity_release=True)
    assert any(float(row["released_capacity_mva"]) > 0 for row in stations)
    assert all(float(row["actual_clr"]) <= 2.0 for row in years)
    assert next(row for row in years if row["year"] == 2023)["selected_capacity_mva"] == 12
