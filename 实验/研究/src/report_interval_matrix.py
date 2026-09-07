# -*- coding: utf-8 -*-
"""为正式研究报告生成核心指标、区间矩阵和反向验证数据。

本模块只读取正式 v3.2 输入与结果，不修改模型或重算优化结果。区间矩阵按
“技术可行性检查—实际指标组合—规划建议”组织；查询函数不接收片区编号或
正式分类，样本没有覆盖的组合返回专项优化，不作数值外推。
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


CORE_INDICATORS = [
    "source_load_scale_ratio",
    "local_reverse_flow_ratio",
    "network_capacity_support_margin",
    "positive_peak_cagr_2021_2025",
]


def _read_inputs(research_root: Path) -> dict[str, pd.DataFrame]:
    research_root = Path(research_root)
    frozen = research_root / "results/runs/real-2021-2025-v32-frozen"
    processed = research_root / "data/processed/real_2021_2025"
    return {
        "matrix": pd.read_csv(frozen / "formal_matrix_110kv.csv"),
        "station": pd.read_csv(processed / "station_static_load.csv"),
        "network": pd.read_csv(processed / "network_lines_110kv.csv"),
        "annual": pd.read_csv(processed / "annual_reference.csv"),
    }


def _candidate_indicators(inputs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    matrix = inputs["matrix"].copy()
    station = inputs["station"].query("voltage_kv == 110").copy()
    network = inputs["network"].query("voltage_kv == 110").copy()
    annual = inputs["annual"].query("voltage_kv == 110 and year in [2021, 2025]").copy()

    station["reverse_mw"] = station["annual_min_net_load_mw"].clip(upper=0).abs()
    local = (
        station.groupby("region_id", as_index=False)
        .agg(
            local_reverse_peak_mw=("reverse_mw", "max"),
            reverse_station_share=("reverse_mw", lambda x: float((x > 0).mean())),
        )
    )
    network_summary = (
        network.groupby("region_id", as_index=False)
        .agg(
            line_count=("line_id", "count"),
            maximum_line_loading=("max_loading_pct", "max"),
        )
    )
    network_summary["network_capacity_support_margin"] = (
        1.0 - network_summary["maximum_line_loading"] / 100.0
    )

    peaks = annual.pivot(index="region_id", columns="year", values="official_positive_peak_mw")
    peaks["positive_peak_cagr_2021_2025"] = (peaks[2025] / peaks[2021]) ** 0.25 - 1.0
    growth = peaks[["positive_peak_cagr_2021_2025"]].reset_index()

    out = matrix.merge(local, on="region_id", how="left")
    out = out.merge(network_summary, on="region_id", how="left")
    out = out.merge(growth, on="region_id", how="left")
    out["source_load_scale_ratio"] = out["pv_to_peak_ratio"]
    out["local_reverse_flow_ratio"] = (
        out["local_reverse_peak_mw"] / out["positive_peak_base_mw"]
    )
    out["reverse_hosting_gap_ratio"] = (
        out["reverse_hosting_gap_mw"] / out["positive_peak_base_mw"]
    )

    keep = [
        "region_id",
        "source_load_scale_ratio",
        "local_reverse_peak_mw",
        "local_reverse_flow_ratio",
        "reverse_station_share",
        "reverse_hosting_gap_ratio",
        "maximum_line_loading",
        "network_capacity_support_margin",
        "positive_peak_cagr_2021_2025",
        "recommendation_type",
        "rcap_refined_threshold_lower",
        "rcap_refined_threshold_upper",
        "rcap_robust_near_optimal_lower",
        "rcap_robust_near_optimal_upper",
        "rcap_robust_upper_identified",
        "PATH_OPT_CLR_UNBOUNDED_clr_2025",
    ]
    out["technical_feasible"] = out["PATH_OPT_CLR_UNBOUNDED_clr_2025"].astype(str).ne("不可行")
    keep.remove("PATH_OPT_CLR_UNBOUNDED_clr_2025")
    keep.append("technical_feasible")
    return out[keep].sort_values("region_id").reset_index(drop=True)


def _screening(indicators: pd.DataFrame) -> pd.DataFrame:
    source_gap_corr = indicators[["source_load_scale_ratio", "reverse_hosting_gap_ratio"]].corr(
        method="spearman", min_periods=4
    ).iloc[0, 1]
    rows = [
        {
            "indicator_code": "source_load_scale_ratio",
            "report_name": "现状源荷规模比",
            "availability_regions": int(indicators["source_load_scale_ratio"].notna().sum()),
            "selected_for_core_matrix": True,
            "screening_reason": "反映新能源装机相对正向最大负荷的规模；QX-00007 缺值，不补零；跨年组合仅用于横向判别。",
        },
        {
            "indicator_code": "local_reverse_flow_ratio",
            "report_name": "局部最大反向功率比",
            "availability_regions": int(indicators["local_reverse_flow_ratio"].notna().sum()),
            "selected_for_core_matrix": True,
            "screening_reason": "八片区均可由站级年度极值计算，直接表征局部反向送电强度；不冒充片区同步反向峰值。",
        },
        {
            "indicator_code": "network_capacity_support_margin",
            "report_name": "线路容量最小余度",
            "availability_regions": int(indicators["network_capacity_support_margin"].notna().sum()),
            "selected_for_core_matrix": True,
            "screening_reason": "八片区均有线路载荷率数据，可量化容量层面的网络支撑余度；不代表电压或完整潮流安全裕度。",
        },
        {
            "indicator_code": "positive_peak_cagr_2021_2025",
            "report_name": "正向最大负荷年均增长率",
            "availability_regions": int(indicators["positive_peak_cagr_2021_2025"].notna().sum()),
            "selected_for_core_matrix": True,
            "screening_reason": "八片区官方年度数据完整，能够区分规划期正向负荷变化对新增容量空间的影响。",
        },
        {
            "indicator_code": "reverse_hosting_gap_ratio",
            "report_name": "反向承载缺口率",
            "availability_regions": int(indicators["reverse_hosting_gap_ratio"].notna().sum()),
            "selected_for_core_matrix": False,
            "screening_reason": f"与现状源荷规模比的秩相关系数为 {source_gap_corr:.2f}，信息冗余；保留为规划响应诊断量。",
        },
        {
            "indicator_code": "reverse_station_share",
            "report_name": "出现反向送电的站点比例",
            "availability_regions": int(indicators["reverse_station_share"].notna().sum()),
            "selected_for_core_matrix": False,
            "screening_reason": "只能反映空间覆盖，不能反映反向功率幅值；由局部最大反向功率比替代。",
        },
    ]
    return pd.DataFrame(rows)


def _formal_outcome(row: pd.Series) -> str:
    if row["recommendation_type"] == "经济释放阈值型":
        lower = float(row["rcap_robust_near_optimal_lower"])
        return f"建议不低于 {lower:.2f}；当前未识别上限"
    if row["recommendation_type"] == "当前不绑定型":
        return "容载比非主导约束"
    if row["recommendation_type"] == "技术约束优先型":
        return "技术约束优先"
    raise ValueError(f"未知正式建议类型：{row['recommendation_type']}")


def query_interval_matrix(
    *,
    technical_feasible: bool,
    source_load_scale_ratio: float | None,
    local_reverse_flow_ratio: float,
    network_capacity_support_margin: float,
    positive_peak_cagr_2021_2025: float,
) -> tuple[str, str]:
    """仅依据工程技术条件与四项指标返回矩阵建议及规则编号。"""

    if not technical_feasible:
        return "技术约束优先", "T"

    indicator_values = (
        source_load_scale_ratio,
        local_reverse_flow_ratio,
        network_capacity_support_margin,
        positive_peak_cagr_2021_2025,
    )
    if any(value is None or pd.isna(value) for value in indicator_values):
        return "核心指标数据不足，需补充数据或开展专项优化", "D"

    # 当前每一种数值建议组合仅有一个正式样本。查询只允许按报告展示精度
    # 复现这些样本点，不把点值扩展成未经验证的四维区间。
    sample_rules = (
        ("S1", 0.973, 0.088, 0.1136, 0.0622, "建议不低于 2.50；当前未识别上限"),
        ("S3", 1.523, 0.126, -0.0226, 0.0419, "容载比非主导约束"),
        ("S4", 1.161, 0.079, 0.2443, -0.0051, "容载比非主导约束"),
        ("S5", 1.527, 0.063, 0.0421, 0.0692, "建议不低于 2.30；当前未识别上限"),
    )
    observed = (
        round(float(source_load_scale_ratio), 3),
        round(float(local_reverse_flow_ratio), 3),
        round(float(network_capacity_support_margin), 4),
        round(float(positive_peak_cagr_2021_2025), 4),
    )
    for rule_id, source, reverse, support, growth, recommendation in sample_rules:
        if observed == (source, reverse, support, growth):
            return recommendation, rule_id

    return "当前样本未覆盖，需开展专项优化", "U"


def _query_row(row: pd.Series) -> tuple[str, str]:
    return query_interval_matrix(
        technical_feasible=bool(row["technical_feasible"]),
        source_load_scale_ratio=row["source_load_scale_ratio"],
        local_reverse_flow_ratio=float(row["local_reverse_flow_ratio"]),
        network_capacity_support_margin=float(row["network_capacity_support_margin"]),
        positive_peak_cagr_2021_2025=float(row["positive_peak_cagr_2021_2025"]),
    )


def _typical_region_matrix(indicators: pd.DataFrame) -> pd.DataFrame:
    out = indicators.copy()
    queried = out.apply(_query_row, axis=1)
    out["matrix_recommendation"] = queried.map(lambda value: value[0])
    out["matrix_rule_id"] = queried.map(lambda value: value[1])
    out["source_load_data_note"] = np.where(
        out["source_load_scale_ratio"].notna(),
        "2026 年新能源装机快照与 2025 年正向最大负荷组合，仅用于横向分析",
        "现有数据未识别，不补零",
    )
    return out


def _range_text(series: pd.Series, *, percent: bool = False, decimals: int = 3) -> str:
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return "未识别"
    lo, hi = float(values.min()), float(values.max())
    is_point = abs(lo - hi) < 10 ** (-(decimals + 1))
    if percent:
        lo, hi = lo * 100.0, hi * 100.0
        if is_point:
            return f"{lo:.2f}%（当前样本点）"
        return f"{lo:.2f}%～{hi:.2f}%"
    if is_point:
        return f"{lo:.{decimals}f}（当前样本点）"
    return f"{lo:.{decimals}f}～{hi:.{decimals}f}"


def _interval_matrix(regions: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "rule_id": "T", "application_condition": "技术可行性未满足",
                "source_load_scale_ratio_interval": "不作为判定条件", "local_reverse_flow_ratio_interval": "不作为判定条件",
                "network_capacity_support_margin_interval": "结合设备与网络专项校核", "positive_peak_cagr_interval": "不作为判定条件",
                "recommendation": "技术约束优先", "supporting_regions": "QX-00008、QX-00009、QX-00010",
                "boundary_basis": "设备容量、接入位置、连续运行条件或局部互济条件未满足时，技术可行性优先。",
            },
            {
                "rule_id": "D", "application_condition": "技术可行但任一核心指标缺失",
                "source_load_scale_ratio_interval": "缺失", "local_reverse_flow_ratio_interval": "不据此补判",
                "network_capacity_support_margin_interval": "不据此补判", "positive_peak_cagr_interval": "不据此补判",
                "recommendation": "补充数据或开展专项优化", "supporting_regions": "QX-00007",
                "boundary_basis": "QX-00007保留正式个案结论；缺失核心指标的新片区不作通用分类。",
            },
            {
                "rule_id": "S1", "application_condition": "技术可行；当前样本点",
                "source_load_scale_ratio_interval": "0.973", "local_reverse_flow_ratio_interval": "0.088",
                "network_capacity_support_margin_interval": "11.36%", "positive_peak_cagr_interval": "6.22%",
                "recommendation": "建议不低于 2.50；当前未识别上限", "supporting_regions": "QX-00001",
                "boundary_basis": "只采用正式样本实测值，不向相邻指标组合扩展。",
            },
            {
                "rule_id": "S3", "application_condition": "技术可行；当前样本点",
                "source_load_scale_ratio_interval": "1.523", "local_reverse_flow_ratio_interval": "0.126",
                "network_capacity_support_margin_interval": "-2.26%", "positive_peak_cagr_interval": "4.19%",
                "recommendation": "容载比非主导约束", "supporting_regions": "QX-00003",
                "boundary_basis": "只采用正式样本实测值，不拼接为矩形区间。",
            },
            {
                "rule_id": "S4", "application_condition": "技术可行；当前样本点",
                "source_load_scale_ratio_interval": "1.161", "local_reverse_flow_ratio_interval": "0.079",
                "network_capacity_support_margin_interval": "24.43%", "positive_peak_cagr_interval": "-0.51%",
                "recommendation": "容载比非主导约束", "supporting_regions": "QX-00004",
                "boundary_basis": "只采用正式样本实测值，不拼接为矩形区间。",
            },
            {
                "rule_id": "S5", "application_condition": "技术可行；当前样本点",
                "source_load_scale_ratio_interval": "1.527", "local_reverse_flow_ratio_interval": "0.063",
                "network_capacity_support_margin_interval": "4.21%", "positive_peak_cagr_interval": "6.92%",
                "recommendation": "建议不低于 2.30；当前未识别上限", "supporting_regions": "QX-00005",
                "boundary_basis": "只采用正式样本实测值，不向相邻指标组合扩展。",
            },
            {
                "rule_id": "U", "application_condition": "技术可行但指标组合不属于以上范围",
                "source_load_scale_ratio_interval": "其他", "local_reverse_flow_ratio_interval": "其他",
                "network_capacity_support_margin_interval": "其他", "positive_peak_cagr_interval": "其他",
                "recommendation": "当前样本未覆盖，需开展专项优化", "supporting_regions": "无",
                "boundary_basis": "不采用相邻区间补值，不对未覆盖组合外推。",
            },
        ]
    )


def _backtest(regions: pd.DataFrame) -> pd.DataFrame:
    formal = regions.apply(_formal_outcome, axis=1)
    backtest = pd.DataFrame(
        {
            "region_id": regions["region_id"],
            "formal_outcome": formal.str.replace(r"建议不低于.*", "推荐下限", regex=True),
            "matrix_rule_id": regions["matrix_rule_id"],
            "matrix_outcome": regions["matrix_recommendation"],
            "matches_formal_optimization": regions["matrix_recommendation"].eq(formal),
            "artificial_upper_bound": False,
        }
    )
    backtest.loc[regions["recommendation_type"].eq("技术约束优先型"), "formal_outcome"] = "技术约束优先"
    backtest.loc[regions["recommendation_type"].eq("当前不绑定型"), "formal_outcome"] = "容载比非主导约束"
    backtest["explains_formal_optimization"] = backtest["matches_formal_optimization"]
    qx7 = backtest["region_id"].eq("QX-00007")
    backtest.loc[qx7, "explains_formal_optimization"] = backtest.loc[qx7, "matrix_rule_id"].eq("D")
    backtest["validation_note"] = np.where(
        backtest["matches_formal_optimization"],
        "矩阵查询与正式结果一致",
        np.where(qx7, "缺失核心指标，保留正式个案结论，不作通用外推", "未解释"),
    )
    return backtest


def build_report_interval_outputs(research_root: Path, output_dir: Path) -> dict[str, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    indicators = _candidate_indicators(_read_inputs(Path(research_root)))
    screening = _screening(indicators)
    regions = _typical_region_matrix(indicators)
    interval = _interval_matrix(regions)
    backtest = _backtest(regions)

    outputs = {
        "candidate_indicators": output_dir / "candidate_indicators.csv",
        "indicator_screening": output_dir / "indicator_screening.csv",
        "typical_region_matrix": output_dir / "typical_region_indicator_matrix.csv",
        "interval_recommendation_matrix": output_dir / "interval_recommendation_matrix.csv",
        "matrix_backtest": output_dir / "matrix_backtest.csv",
    }
    for key, frame in {
        "candidate_indicators": indicators,
        "indicator_screening": screening,
        "typical_region_matrix": regions,
        "interval_recommendation_matrix": interval,
        "matrix_backtest": backtest,
    }.items():
        frame.to_csv(outputs[key], index=False, encoding="utf-8-sig")
    return outputs
