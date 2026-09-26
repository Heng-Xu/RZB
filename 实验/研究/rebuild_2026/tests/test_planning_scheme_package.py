import pytest

from rebuild_2026.baseline_2021 import read_csv
from rebuild_2026.planning_scheme_package import build_package, solve_planning_cases


def test_common_baseline_and_tie_attribution(tmp_path) -> None:
    # 求解器输入来自正式审计目录，产物写入独立目录，避免测试覆盖研究结果。
    solve_planning_cases(tmp_path)
    _, feasibility = build_package(tmp_path)
    baseline = read_csv(tmp_path / "planning_2021_common_baseline_layers.csv")
    assert all(float(r["simulated_clr"]) <= 2.0 for r in baseline)
    attribution = read_csv(tmp_path / "planning_tie_attribution.csv")[0]
    assert float(attribution["modeled_saving_10k_cny"]) > 0
    assert feasibility[0]["optimized_transfer_mw"] == pytest.approx(4.49651196)
    assert feasibility[0]["static_transfer_upper_mw"] >= 4.49651196
    assert feasibility[0]["transfer_control"] == "binary_whole_section_not_continuously_dispatchable"
    assert feasibility[0]["capacity_difference_vs_elastic_mva"] == pytest.approx(11.5)
    assert feasibility[0]["avoided_capacity_vs_same_rigid_no_tie_mva"] == pytest.approx(10.0)
    assert feasibility[0]["operation_status"] == "simulated_dispatch_not_observed_operation"
