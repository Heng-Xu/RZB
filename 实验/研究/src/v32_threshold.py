"""把单调 Rcap 前沿转换为可解释的“经济释放阈值”诊断。

对存量豁免模型，近优集通常从某一最小 Rcap 开始一直延伸到扫描上界，
因此不把扫描上界误报成推荐区间上限，而识别“再收紧就显著增本”的最小
非惩罚 Rcap。若从扫描下界起即完全非绑定，则明确标记为本规划期不可识别。
"""
from __future__ import annotations

import math
from typing import Any

import pandas as pd

from src.v32_frontier_aggregate import validate_frontier_nested


class V32ThresholdError(ValueError):
    pass


def classify_economic_release_thresholds(
    frontier: pd.DataFrame,
    *,
    near_optimal_band: float = 0.05,
) -> pd.DataFrame:
    if not (0 <= float(near_optimal_band) < 1):
        raise V32ThresholdError("near_optimal_band must be in [0,1)")
    validate_frontier_nested(frontier)
    frame = frontier.copy()
    frame["rcap_num"] = pd.to_numeric(frame["rcap_numeric"], errors="coerce")
    frame["cost_num"] = pd.to_numeric(
        frame["cumulative_in_service_eac_wanyuan"], errors="coerce"
    )
    if frame["feasible"].dtype == bool:
        frame["feasible_bool"] = frame["feasible"]
    else:
        frame["feasible_bool"] = (
            frame["feasible"].astype(str).str.strip().str.lower().isin({"true", "1", "yes"})
        )

    rows: list[dict[str, Any]] = []
    for region_id, group in frame.groupby("region_id", sort=True):
        unbounded = group[group["rcap"].astype(str).eq("unbounded")]
        if len(unbounded) != 1:
            raise V32ThresholdError(f"{region_id}: missing unique unbounded row")
        unbounded_row = unbounded.iloc[0]
        numeric = group[group["rcap_num"].notna()].sort_values("rcap_num", kind="stable")
        if numeric.empty:
            raise V32ThresholdError(f"{region_id}: numeric Rcap scan is empty")
        scan_low = float(numeric["rcap_num"].min())
        scan_high = float(numeric["rcap_num"].max())
        base: dict[str, Any] = {
            "region_id": str(region_id),
            "voltage_kv": 110,
            "near_optimal_band": float(near_optimal_band),
            "scan_rcap_low": scan_low,
            "scan_rcap_high": scan_high,
        }
        if not bool(unbounded_row["feasible_bool"]):
            base.update(
                {
                    "threshold_status": "not_formed_physical_infeasible",
                    "coarse_release_threshold_lower": math.nan,
                    "coarse_release_threshold_upper": math.nan,
                    "minimum_near_optimal_rcap_on_grid": math.nan,
                    "unbounded_cost_wanyuan": math.nan,
                    "cost_below_threshold_wanyuan": math.nan,
                    "cost_at_or_above_threshold_wanyuan": math.nan,
                    "requires_local_refinement": False,
                    "interpretation": "无上限方案仍物理不可行，不形成Rcap经济阈值",
                }
            )
            rows.append(base)
            continue

        unbounded_cost = float(unbounded_row["cost_num"])
        threshold_cost = unbounded_cost * (1.0 + float(near_optimal_band))
        feasible = numeric[numeric["feasible_bool"]].copy()
        near = feasible[feasible["cost_num"] <= threshold_cost + 1e-7].copy()
        if near.empty:
            base.update(
                {
                    "threshold_status": "not_reached_within_scan",
                    "coarse_release_threshold_lower": scan_high,
                    "coarse_release_threshold_upper": math.nan,
                    "minimum_near_optimal_rcap_on_grid": math.nan,
                    "unbounded_cost_wanyuan": unbounded_cost,
                    "cost_below_threshold_wanyuan": math.nan,
                    "cost_at_or_above_threshold_wanyuan": math.nan,
                    "requires_local_refinement": False,
                    "interpretation": "扫描上界内仍未进入近优成本带",
                }
            )
            rows.append(base)
            continue

        minimum = float(near["rcap_num"].min())
        if math.isclose(minimum, scan_low, abs_tol=1e-12):
            # 从最紧扫描点起就已不增本，说明本规划期没有由新增容量触发的
            # 经济识别力；不能把扫描下界当推荐值。
            base.update(
                {
                    "threshold_status": "non_binding_not_identified_in_horizon",
                    "coarse_release_threshold_lower": math.nan,
                    "coarse_release_threshold_upper": math.nan,
                    "minimum_near_optimal_rcap_on_grid": minimum,
                    "unbounded_cost_wanyuan": unbounded_cost,
                    "cost_below_threshold_wanyuan": math.nan,
                    "cost_at_or_above_threshold_wanyuan": float(
                        near.loc[near["rcap_num"].eq(minimum), "cost_num"].iloc[0]
                    ),
                    "requires_local_refinement": False,
                    "interpretation": "扫描范围内Rcap均不改变最优投资组合，本规划期不识别唯一阈值",
                }
            )
            rows.append(base)
            continue

        below = numeric[numeric["rcap_num"] < minimum].tail(1)
        if below.empty:
            raise V32ThresholdError(f"{region_id}: binding threshold has no lower bracket")
        lower = float(below.iloc[0]["rcap_num"])
        base.update(
            {
                "threshold_status": "binding_threshold_bracketed",
                "coarse_release_threshold_lower": lower,
                "coarse_release_threshold_upper": minimum,
                "minimum_near_optimal_rcap_on_grid": minimum,
                "unbounded_cost_wanyuan": unbounded_cost,
                "cost_below_threshold_wanyuan": (
                    float(below.iloc[0]["cost_num"])
                    if bool(below.iloc[0]["feasible_bool"])
                    else math.nan
                ),
                "cost_at_or_above_threshold_wanyuan": float(
                    near.loc[near["rcap_num"].eq(minimum), "cost_num"].iloc[0]
                ),
                "requires_local_refinement": True,
                "interpretation": "该区间内存在最小非惩罚Rcap；再收紧将使最优技术组合或成本发生实质变化",
            }
        )
        rows.append(base)
    return pd.DataFrame(rows)
