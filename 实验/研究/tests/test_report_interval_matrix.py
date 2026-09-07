# -*- coding: utf-8 -*-
"""研究报告核心指标、区间矩阵和反向验证的回归测试。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.report_interval_matrix import build_report_interval_outputs, query_interval_matrix


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESEARCH_ROOT = PROJECT_ROOT / "实验/研究"


def test_candidate_indicators_are_physical_traceable_and_complete_where_claimed(tmp_path):
    outputs = build_report_interval_outputs(RESEARCH_ROOT, tmp_path)
    indicators = pd.read_csv(outputs["candidate_indicators"])

    assert set(indicators["region_id"]) == {
        "QX-00001", "QX-00003", "QX-00004", "QX-00005",
        "QX-00007", "QX-00008", "QX-00009", "QX-00010",
    }
    assert indicators["local_reverse_flow_ratio"].notna().all()
    assert indicators["network_capacity_support_margin"].notna().all()
    assert indicators["positive_peak_cagr_2021_2025"].notna().all()

    qx5 = indicators.set_index("region_id").loc["QX-00005"]
    assert abs(qx5["source_load_scale_ratio"] - 1.527447645) < 1e-9
    assert abs(qx5["local_reverse_flow_ratio"] - 59.90 / 956.45) < 1e-12
    assert abs(qx5["network_capacity_support_margin"] - 0.0421) < 1e-12
    assert pd.isna(indicators.set_index("region_id").loc["QX-00007", "source_load_scale_ratio"])


def test_screening_keeps_four_core_indicators_and_rejects_redundant_gap_ratio(tmp_path):
    outputs = build_report_interval_outputs(RESEARCH_ROOT, tmp_path)
    screening = pd.read_csv(outputs["indicator_screening"])
    selected = screening.loc[screening["selected_for_core_matrix"], "indicator_code"].tolist()
    assert selected == [
        "source_load_scale_ratio",
        "local_reverse_flow_ratio",
        "network_capacity_support_margin",
        "positive_peak_cagr_2021_2025",
    ]
    gap = screening.set_index("indicator_code").loc["reverse_hosting_gap_ratio"]
    assert not bool(gap["selected_for_core_matrix"])
    assert "冗余" in gap["screening_reason"]


def test_recommendations_preserve_lower_bound_nonbinding_and_technical_priority(tmp_path):
    outputs = build_report_interval_outputs(RESEARCH_ROOT, tmp_path)
    regions = pd.read_csv(outputs["typical_region_matrix"]).set_index("region_id")
    assert regions.loc["QX-00001", "matrix_recommendation"] == "建议不低于 2.50；当前未识别上限"
    assert regions.loc["QX-00005", "matrix_recommendation"] == "建议不低于 2.30；当前未识别上限"
    assert regions.loc["QX-00003", "matrix_recommendation"] == "容载比非主导约束"
    assert regions.loc["QX-00007", "matrix_recommendation"] == "核心指标数据不足，需补充数据或开展专项优化"
    assert regions.loc["QX-00010", "matrix_recommendation"] == "技术约束优先"
    assert not regions["matrix_recommendation"].str.contains(r"2\.50[～—-]", regex=True).any()
    assert not regions["matrix_recommendation"].str.contains(r"2\.30[～—-]", regex=True).any()


def test_interval_matrix_backtest_explains_all_regions_without_hiding_missing_data(tmp_path):
    outputs = build_report_interval_outputs(RESEARCH_ROOT, tmp_path)
    backtest = pd.read_csv(outputs["matrix_backtest"])
    assert len(backtest) == 8
    assert backtest["matches_formal_optimization"].sum() == 7
    assert backtest["explains_formal_optimization"].all()
    assert not backtest.set_index("region_id").loc["QX-00007", "matches_formal_optimization"]
    assert backtest["artificial_upper_bound"].eq(False).all()
    assert set(backtest.loc[backtest["formal_outcome"] == "技术约束优先", "region_id"]) == {
        "QX-00008", "QX-00009", "QX-00010"
    }


def test_matrix_query_uses_only_engineering_conditions_and_indicators():
    qx1 = query_interval_matrix(
        technical_feasible=True,
        source_load_scale_ratio=0.9727670554,
        local_reverse_flow_ratio=0.0883114498,
        network_capacity_support_margin=0.1136,
        positive_peak_cagr_2021_2025=0.0621827534,
    )
    assert qx1 == ("建议不低于 2.50；当前未识别上限", "S1")

    missing = query_interval_matrix(
        technical_feasible=True,
        source_load_scale_ratio=None,
        local_reverse_flow_ratio=0.021069,
        network_capacity_support_margin=-0.0506,
        positive_peak_cagr_2021_2025=0.013361,
    )
    assert missing == ("核心指标数据不足，需补充数据或开展专项优化", "D")

    uncovered = query_interval_matrix(
        technical_feasible=True,
        source_load_scale_ratio=0.70,
        local_reverse_flow_ratio=0.02,
        network_capacity_support_margin=0.20,
        positive_peak_cagr_2021_2025=0.08,
    )
    assert uncovered == ("当前样本未覆盖，需开展专项优化", "U")


def test_any_missing_core_indicator_returns_data_insufficient():
    complete = [0.973, 0.088, 0.1136, 0.0622]
    for missing_index in range(4):
        values = complete.copy()
        values[missing_index] = None
        result = query_interval_matrix(
            technical_feasible=True,
            source_load_scale_ratio=values[0],
            local_reverse_flow_ratio=values[1],
            network_capacity_support_margin=values[2],
            positive_peak_cagr_2021_2025=values[3],
        )
        assert result == ("核心指标数据不足，需补充数据或开展专项优化", "D")
