"""v3.2 同基线政策对照的核心不变量。"""
from __future__ import annotations

import pandas as pd
import pytest

from src.v32_model import apply_common_planning_baseline, run_common_baseline_policy_paths


def _write_reference(tmp_path) -> None:
    rows = [
        (2021, "QX-A", 110, 100.0, 40.0),
        (2022, "QX-A", 110, 105.0, 30.0),
        (2023, "QX-A", 110, 110.0, 45.0),
        (2024, "QX-A", 110, 115.0, 50.0),
        (2025, "QX-A", 110, 120.0, 55.0),
    ]
    pd.DataFrame(
        rows,
        columns=[
            "year",
            "region_id",
            "voltage_kv",
            "official_capacity_mva",
            "official_positive_peak_mw",
        ],
    ).to_csv(tmp_path / "annual_reference.csv", index=False)


def _annual() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "year": [2022, 2023, 2024, 2025],
            "region_id": ["QX-A"] * 4,
            "voltage_kv": [110] * 4,
            "capacity_mva": [100.0] * 4,
            "baseline_capacity_mva": [100.0] * 4,
            "positive_peak_mw": [30.0, 45.0, 50.0, 55.0],
            "reverse_peak_mw": [0.0] * 4,
            "reverse_beta": [0.8] * 4,
        }
    )


def _retirement_candidate() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "candidate_id": "RETIRE-20",
                "candidate_group": "RETIRE-GROUP",
                "region_id": "QX-A",
                "voltage_kv": 110,
                "candidate_type": "retirement",
                "delta_capacity_mva": -20.0,
                "capex_base_wanyuan": 20.0,
                "eac_base_wanyuan_per_year": 10.0,
                "cost_status": "cost_center_and_range_available",
                "source_ref": "unit-test",
                "available_year": 2022,
            }
        ]
    )


def test_common_baseline_uses_2021_peak_only_and_has_no_future_information_leakage(tmp_path) -> None:
    _write_reference(tmp_path)
    source = _annual()
    out = apply_common_planning_baseline(source, tmp_path)

    # 2021 P+=40 MW -> S0_plan=2*40=80 MVA。
    # 2022 实际峰只有 30 MW；如果错误引用未来最小峰则会得到 60 MVA。
    assert out["planning_baseline_capacity_mva"].tolist() == pytest.approx([80.0] * 4)
    assert out["reported_baseline_capacity_mva"].tolist() == pytest.approx([80.0] * 4)

    # 物理资产状态不被连续缩放或伪造。
    assert out["baseline_capacity_mva"].tolist() == pytest.approx([100.0] * 4)
    assert out["positive_peak_mw"].tolist() == pytest.approx([30.0, 45.0, 50.0, 55.0])


def test_both_policy_paths_share_exactly_the_same_planning_baseline(tmp_path) -> None:
    _write_reference(tmp_path)
    annual = apply_common_planning_baseline(_annual(), tmp_path)
    result = run_common_baseline_policy_paths(
        annual,
        _retirement_candidate(),
        planner_kwargs={},
    )

    years = result["path_year_results"]
    elastic = years[years["path_id"].eq("PATH_OPT_CLR_UNBOUNDED")].sort_values("year")
    rigid = years[years["path_id"].eq("PATH_OPT_CLR_LE_2")].sort_values("year")

    # 两方案起点相同；差异只来自是否施加 R<=2.0。
    assert elastic.iloc[0]["planning_baseline_capacity_mva"] == pytest.approx(80.0)
    assert rigid.iloc[0]["planning_baseline_capacity_mva"] == pytest.approx(80.0)

    costs = result["path_cost_breakdown"].set_index("path_id")
    assert costs.loc["PATH_OPT_CLR_UNBOUNDED", "status"] == "feasible"
    assert costs.loc["PATH_OPT_CLR_LE_2", "status"] == "feasible"
    assert (
        costs.loc["PATH_OPT_CLR_UNBOUNDED", "cumulative_in_service_eac_wanyuan"]
        <= costs.loc["PATH_OPT_CLR_LE_2", "cumulative_in_service_eac_wanyuan"] + 1e-9
    )


def test_common_baseline_requires_a_2021_reference_for_every_group(tmp_path) -> None:
    _write_reference(tmp_path)
    annual = pd.concat(
        [
            _annual(),
            pd.DataFrame(
                [
                    {
                        "year": 2022,
                        "region_id": "QX-MISSING",
                        "voltage_kv": 110,
                        "capacity_mva": 50.0,
                        "baseline_capacity_mva": 50.0,
                        "positive_peak_mw": 25.0,
                        "reverse_peak_mw": 0.0,
                        "reverse_beta": 0.8,
                    }
                ]
            ),
        ],
        ignore_index=True,
    )
    with pytest.raises(ValueError, match="2021"):
        apply_common_planning_baseline(annual, tmp_path)
