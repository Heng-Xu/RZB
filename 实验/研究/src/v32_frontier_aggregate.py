"""v3.2 实际资产 Rcap 前沿汇总、嵌套性校验与粗网格推荐带。"""
from __future__ import annotations

import math
from typing import Any

import pandas as pd


class V32FrontierAggregateError(ValueError):
    """Rcap 前沿不满足嵌套可行域或发布前置条件。"""


def _bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes"})


def validate_frontier_nested(frontier: pd.DataFrame, *, tolerance: float = 1e-7) -> bool:
    required = {
        "rcap",
        "rcap_numeric",
        "region_id",
        "voltage_kv",
        "feasible",
        "cumulative_in_service_eac_wanyuan",
        "retirement_candidates_enabled",
    }
    missing = required - set(frontier.columns)
    if missing:
        raise V32FrontierAggregateError(f"frontier missing {sorted(missing)}")
    frame = frontier.copy()
    if not frame["voltage_kv"].astype(int).eq(110).all():
        raise V32FrontierAggregateError("formal frontier must contain 110 kV rows only")
    if _bool_series(frame["retirement_candidates_enabled"]).any():
        raise V32FrontierAggregateError("primary frontier must not enable retirement candidates")
    if frame.duplicated(["region_id", "rcap"]).any():
        raise V32FrontierAggregateError("duplicate region-Rcap frontier rows")

    for region_id, group in frame.groupby("region_id", sort=True):
        unbounded = group[group["rcap"].astype(str).eq("unbounded")]
        if len(unbounded) != 1:
            raise V32FrontierAggregateError(
                f"{region_id}: expected exactly one unbounded reference row"
            )
        unbounded_feasible = bool(_bool_series(unbounded["feasible"]).iloc[0])
        unbounded_cost = pd.to_numeric(
            unbounded["cumulative_in_service_eac_wanyuan"], errors="coerce"
        ).iloc[0]
        numeric = group[pd.to_numeric(group["rcap_numeric"], errors="coerce").notna()].copy()
        numeric["rcap_num"] = pd.to_numeric(numeric["rcap_numeric"], errors="raise")
        numeric["feasible_bool"] = _bool_series(numeric["feasible"])
        numeric["cost_num"] = pd.to_numeric(
            numeric["cumulative_in_service_eac_wanyuan"], errors="coerce"
        )
        numeric = numeric.sort_values("rcap_num", kind="stable")

        # Rcap 越大约束越松：可行性一旦出现，后续更宽松点不得再次不可行。
        seen_feasible = False
        for row in numeric.itertuples(index=False):
            if bool(row.feasible_bool):
                seen_feasible = True
            elif seen_feasible:
                raise V32FrontierAggregateError(
                    f"{region_id}: feasible set is not nested at Rcap={row.rcap_num}"
                )

        feasible = numeric[numeric["feasible_bool"]].copy()
        if not feasible.empty:
            costs = feasible["cost_num"].to_numpy(dtype=float)
            if not pd.Series(costs).map(math.isfinite).all():
                raise V32FrontierAggregateError(
                    f"{region_id}: feasible numeric Rcap has non-finite cost"
                )
            # 约束放松后最优成本不得上升。
            if any(costs[i + 1] > costs[i] + tolerance for i in range(len(costs) - 1)):
                raise V32FrontierAggregateError(
                    f"{region_id}: optimal cost rises when Rcap is relaxed"
                )
            if unbounded_feasible:
                if not math.isfinite(float(unbounded_cost)):
                    raise V32FrontierAggregateError(
                        f"{region_id}: feasible unbounded reference has non-finite cost"
                    )
                if (feasible["cost_num"] < float(unbounded_cost) - tolerance).any():
                    raise V32FrontierAggregateError(
                        f"{region_id}: constrained solution is cheaper than unbounded optimum"
                    )
        if not unbounded_feasible and not feasible.empty:
            raise V32FrontierAggregateError(
                f"{region_id}: finite Rcap feasible while unbounded reference is infeasible"
            )
    return True


def build_coarse_recommendations(
    frontier: pd.DataFrame,
    *,
    near_optimal_band: float = 0.05,
) -> pd.DataFrame:
    """在同一实际资产基线上，从粗网格提取近优 Rcap 带。

    这里不把实现 CLR 与 Rcap 相交；实现 CLR 仅作为近优方案的结果范围。
    最终推荐仍需经过局部细化与参数敏感性后才能发布。
    """
    if not (0 <= float(near_optimal_band) < 1):
        raise V32FrontierAggregateError("near_optimal_band must be in [0,1)")
    validate_frontier_nested(frontier)
    frame = frontier.copy()
    frame["feasible_bool"] = _bool_series(frame["feasible"])
    frame["rcap_num"] = pd.to_numeric(frame["rcap_numeric"], errors="coerce")
    frame["cost_num"] = pd.to_numeric(
        frame["cumulative_in_service_eac_wanyuan"], errors="coerce"
    )
    rows: list[dict[str, Any]] = []
    for region_id, group in frame.groupby("region_id", sort=True):
        unbounded = group[group["rcap"].astype(str).eq("unbounded")].iloc[0]
        if not bool(unbounded["feasible_bool"]):
            rows.append(
                {
                    "region_id": str(region_id),
                    "voltage_kv": 110,
                    "recommendation_status": "not_formed_unbounded_physical_infeasible",
                    "coarse_rcap_low": math.nan,
                    "coarse_rcap_high": math.nan,
                    "coarse_rcap_point_estimate": math.nan,
                    "coarse_near_optimal_points": "",
                    "realized_physical_clr_2025_low": math.nan,
                    "realized_physical_clr_2025_high": math.nan,
                    "measure_flip": False,
                    "unbounded_cost_wanyuan": math.nan,
                    "near_optimal_cost_threshold_wanyuan": math.nan,
                    "near_optimal_band": float(near_optimal_band),
                    "requires_local_refinement": False,
                    "requires_parameter_sensitivity": False,
                }
            )
            continue
        base_cost = float(unbounded["cost_num"])
        threshold = base_cost * (1.0 + float(near_optimal_band))
        numeric = group[
            group["rcap_num"].notna() & group["feasible_bool"]
        ].copy()
        band = numeric[numeric["cost_num"] <= threshold + 1e-7].copy()
        if band.empty:
            rows.append(
                {
                    "region_id": str(region_id),
                    "voltage_kv": 110,
                    "recommendation_status": "no_finite_rcap_within_near_optimal_band",
                    "coarse_rcap_low": math.nan,
                    "coarse_rcap_high": math.nan,
                    "coarse_rcap_point_estimate": math.nan,
                    "coarse_near_optimal_points": "",
                    "realized_physical_clr_2025_low": math.nan,
                    "realized_physical_clr_2025_high": math.nan,
                    "measure_flip": False,
                    "unbounded_cost_wanyuan": base_cost,
                    "near_optimal_cost_threshold_wanyuan": threshold,
                    "near_optimal_band": float(near_optimal_band),
                    "requires_local_refinement": False,
                    "requires_parameter_sensitivity": True,
                }
            )
            continue
        band = band.sort_values("rcap_num", kind="stable")
        points = [float(value) for value in band["rcap_num"]]
        signatures = (
            band["action_types"].astype(str)
            + "|"
            + band["candidate_ids"].fillna("").astype(str)
            + "|storage="
            + pd.to_numeric(band["storage_modules"], errors="coerce").fillna(-1).astype(int).astype(str)
            + "|capacity="
            + pd.to_numeric(band["capacity_action_delta_mva"], errors="coerce").round(6).astype(str)
        )
        measure_flip = signatures.nunique() > 1
        physical = pd.to_numeric(band["physical_clr_2025"], errors="coerce").dropna()
        point_estimate = points[0] if len(points) == 1 and not measure_flip else math.nan
        rows.append(
            {
                "region_id": str(region_id),
                "voltage_kv": 110,
                "recommendation_status": "coarse_near_optimal_band_only",
                "coarse_rcap_low": min(points),
                "coarse_rcap_high": max(points),
                "coarse_rcap_point_estimate": point_estimate,
                "coarse_near_optimal_points": ";".join(f"{value:.1f}" for value in points),
                "realized_physical_clr_2025_low": float(physical.min()) if not physical.empty else math.nan,
                "realized_physical_clr_2025_high": float(physical.max()) if not physical.empty else math.nan,
                "measure_flip": bool(measure_flip),
                "unbounded_cost_wanyuan": base_cost,
                "near_optimal_cost_threshold_wanyuan": threshold,
                "near_optimal_band": float(near_optimal_band),
                "requires_local_refinement": True,
                "requires_parameter_sensitivity": True,
            }
        )
    return pd.DataFrame(rows)
