import pytest

from rebuild_2026.baseline_2021 import read_csv
from rebuild_2026.hourly_source_profile import OUTPUT_DIR
from rebuild_2026.joint_lifecycle_optimizer import PIZHOU_110, cost_factors, load_inputs, solve_layer
from rebuild_2026.new_line_section_audit import designed_new_line_section


def test_designed_section_is_reproducible_from_feeder_topology() -> None:
    section = designed_new_line_section()
    assert section["new_isolation_switch_span"] == "dzhen线23杆—dzhen线24杆"
    assert section["isolated_section_nodes"] == 25
    assert section["2025_feeder_stress_section_load_seed_mw"] == pytest.approx(7.49106117)
    assert section["2025_feeder_stress_section_load_seed_mw"] < section["2025_feeder_total_load_seed_mw"]


def test_new_line_is_selected_only_when_its_static_benefit_covers_cost() -> None:
    baseline = {(r["study_region_id"], int(r["voltage_kv"]), r["model_station_id"]): r
                for r in read_csv(OUTPUT_DIR / "planning_2021_common_baseline_stations.csv")}
    _, scene, durations, peaks, catalog, coefficients = load_inputs()
    def solve(extra):
        return solve_layer(
            PIZHOU_110, baseline, scene, durations, peaks, catalog, coefficients,
            cost_factors(), 2.0, True, include_new_line=True,
            new_line_variant="designed_bus", line_km=3.0,
            line_extra_capex_10k_cny=extra, existing_tie_allowed=False,
            preserve_baseline_forward_margin=True, policy_peak_basis="rolling_max",
            max_storage_modules=50, require_existing_tie_operation=False,
        )
    _, years, ties, summary = solve(0.0)
    assert years[-1]["line_built"] == 1
    assert ties[-1]["transfer_mw"] == pytest.approx(7.49106117)
    # 成本随校准后的源数据变化；核验经济性，不锁定前阶段成本快照。
    assert summary["objective_npv_10k_cny"] > 0
    _, years_expensive, _, summary_expensive = solve(300.0)
    assert years_expensive[-1]["line_built"] == 0
    assert summary_expensive["objective_npv_10k_cny"] > summary["objective_npv_10k_cny"]
