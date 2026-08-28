"""v3.2 同基线政策实验与弹性 Rcap 推荐逻辑。

本模块复用已经回归验证的离散规划器，但把 v3.2 的实际资产共同起点、
存量豁免和 Rcap 推荐逻辑固定在正式入口之外，避免旧归一化基线重新渗入。
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from src.v3_planner import (
    PATH_OPT_STRICT,
    PATH_OPT_UNBOUNDED,
    optimize_path,
    validate_path_inclusion,
)


class V32ModelError(ValueError):
    """v3.2 共同基线、政策路径或推荐前沿不满足发布条件。"""


def apply_common_planning_baseline(
    annual: pd.DataFrame,
    processed_root: Path,
    *,
    baseline_clr: float = 2.0,
    applies_to_voltage_kv: Iterable[int] = (110,),
) -> pd.DataFrame:
    """为正式政策比较层生成实际 2021 在役资产共同基线。

    ``baseline_capacity_mva`` 是历史存量实物容量，不被 Rcap 反向改写；
    ``reported_baseline_capacity_mva`` 只是复用旧求解器约束列的内部别名。
    ``baseline_clr`` 仍保留为兼容参数，但不参与正式 v3.2 起点计算。
    """
    if not math.isfinite(float(baseline_clr)) or float(baseline_clr) <= 0:
        raise V32ModelError("baseline_clr must be positive and finite")
    applied_voltages = {int(value) for value in applies_to_voltage_kv}
    if not applied_voltages:
        raise V32ModelError("at least one formal voltage level is required")
    required = {
        "year",
        "region_id",
        "voltage_kv",
        "baseline_capacity_mva",
        "positive_peak_mw",
    }
    missing = required - set(annual.columns)
    if missing:
        raise V32ModelError(f"annual frame missing {sorted(missing)}")

    out = annual.copy()
    out["planning_baseline_capacity_mva"] = pd.to_numeric(
        out["baseline_capacity_mva"], errors="raise"
    )
    if (out["planning_baseline_capacity_mva"] <= 0).any():
        raise V32ModelError("actual 2021 planning baseline capacity must be positive")

    # Planner compatibility alias. Both policy paths receive the same actual base.
    out["reported_baseline_capacity_mva"] = out["planning_baseline_capacity_mva"]
    return out


def _merge_policy_outputs(parts: list[dict[str, pd.DataFrame]]) -> dict[str, pd.DataFrame]:
    return {
        name: pd.concat(
            [part[name] for part in parts],
            ignore_index=True,
            sort=False,
        )
        for name in (
            "path_year_results",
            "path_action_results",
            "path_cost_breakdown",
        )
    }


def _attach_v32_planning_columns(
    result: dict[str, pd.DataFrame],
    annual: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    years = result["path_year_results"].copy()
    baseline = annual[
        ["region_id", "voltage_kv", "planning_baseline_capacity_mva"]
    ].drop_duplicates()
    years = years.merge(
        baseline,
        on=["region_id", "voltage_kv"],
        how="left",
        validate="many_to_one",
    )
    if "reported_capacity_mva" in years.columns:
        years["planning_capacity_mva"] = years["reported_capacity_mva"]
    else:
        years["planning_capacity_mva"] = years["clr"] * years["p_plus_mw"]
    result = dict(result)
    result["path_year_results"] = years
    return result


def run_common_baseline_policy_paths(
    annual: pd.DataFrame,
    candidates: pd.DataFrame,
    *,
    planner_kwargs: dict[str, Any],
) -> dict[str, pd.DataFrame]:
    """求解同基线弹性/刚性政策路径并验证可行域包含关系。

    110 kV：刚性路径额外施加 R<=2.0；
    35 kV：沿用辅助分析定位，不施加唯一刚性上界。
    """
    if "planning_baseline_capacity_mva" not in annual.columns:
        raise V32ModelError("common planning baseline must be applied before policy optimization")
    if "reported_baseline_capacity_mva" not in annual.columns:
        raise V32ModelError("planner compatibility baseline column is missing")

    from src.v32_policy import run_actual_asset_policy_paths

    merged = run_actual_asset_policy_paths(
        annual,
        candidates,
        planner_kwargs=planner_kwargs,
        rigid_rcap=2.0,
    )
    return _attach_v32_planning_columns(merged, annual)


def _numeric_feasible_frontier(frontier: pd.DataFrame, region_id: str) -> pd.DataFrame:
    required = {
        "rcap",
        "region_id",
        "cumulative_in_service_eac_wanyuan",
        "storage_modules",
        "feasible",
    }
    missing = required - set(frontier.columns)
    if missing:
        raise V32ModelError(f"frontier missing {sorted(missing)}")
    sub = frontier[
        frontier["region_id"].astype(str).eq(str(region_id))
        & frontier["feasible"].astype(bool)
    ].copy()
    sub["rcap_numeric"] = pd.to_numeric(sub["rcap"], errors="coerce")
    sub["cost_numeric"] = pd.to_numeric(
        sub["cumulative_in_service_eac_wanyuan"], errors="coerce"
    )
    clr_column = (
        "physical_clr_2025" if "physical_clr_2025" in sub.columns else "clr_2025"
    )
    if clr_column not in sub.columns:
        raise V32ModelError("frontier missing physical_clr_2025")
    sub["clr_numeric"] = pd.to_numeric(sub[clr_column], errors="coerce")
    return sub[
        sub["rcap_numeric"].notna()
        & sub["cost_numeric"].notna()
        & sub["clr_numeric"].notna()
    ].copy()


def _capacity_action_series(frame: pd.DataFrame) -> pd.Series:
    if "capacity_action_delta_mva" in frame.columns:
        return pd.to_numeric(frame["capacity_action_delta_mva"], errors="coerce")
    if "expansion_mva" in frame.columns:
        return pd.to_numeric(frame["expansion_mva"], errors="coerce")
    return pd.Series([float("nan")] * len(frame), index=frame.index, dtype=float)


def recommended_rcap_interval(
    frontier: pd.DataFrame,
    *,
    region_id: str,
    near_optimal_band: float = 0.05,
) -> dict[str, Any]:
    """提取同一场景的 Rcap 近优带，并单独记录实现 CLR 审计范围。

    返回的 ``realized_clr_2025_*`` 仅用于结果解释和审计，不能与 Rcap
    区间求交，也不参与推荐区间的形成。
    """
    if not (0 <= float(near_optimal_band) < 1):
        raise V32ModelError("near_optimal_band must be in [0, 1)")
    valid = _numeric_feasible_frontier(frontier, region_id)
    if valid.empty:
        return {
            "region_id": region_id,
            "rcap_interval_low": None,
            "rcap_interval_high": None,
            "rcap_point_estimate": None,
            "realized_clr_2025_low": None,
            "realized_clr_2025_high": None,
            "rcap_points": [],
            "interval_only": True,
            "measure_flip": False,
            "reason": "no_feasible_numeric_rcap",
        }

    unbounded = frontier[
        frontier["region_id"].astype(str).eq(str(region_id))
        & frontier["rcap"].astype(str).eq("unbounded")
        & frontier["feasible"].astype(bool)
    ]
    best = (
        float(pd.to_numeric(unbounded["cumulative_in_service_eac_wanyuan"], errors="raise").iloc[0])
        if len(unbounded) == 1
        else float(valid["cost_numeric"].min())
    )
    band = valid[
        valid["cost_numeric"] <= best * (1.0 + float(near_optimal_band)) + 1e-9
    ].copy()
    if band.empty:
        return {
            "region_id": region_id,
            "rcap_interval_low": None,
            "rcap_interval_high": None,
            "rcap_point_estimate": None,
            "realized_clr_2025_low": None,
            "realized_clr_2025_high": None,
            "rcap_points": [],
            "interval_only": True,
            "measure_flip": False,
            "best_cost_wanyuan": best,
            "near_optimal_band": float(near_optimal_band),
            "reason": "no_finite_rcap_within_near_optimal_band",
        }
    rcap_points = sorted(
        {round(float(value), 10) for value in band["rcap_numeric"]}
    )
    low = min(rcap_points)
    high = max(rcap_points)
    realized_low = float(band["clr_numeric"].min())
    realized_high = float(band["clr_numeric"].max())
    capacity_actions = _capacity_action_series(band)
    storage = pd.to_numeric(band["storage_modules"], errors="coerce")
    flipped = bool(
        storage.dropna().nunique() > 1
        or capacity_actions.dropna().round(6).nunique() > 1
    )
    point = low if len(rcap_points) == 1 and not flipped else None
    return {
        "region_id": region_id,
        "rcap_interval_low": low,
        "rcap_interval_high": high,
        "rcap_point_estimate": point,
        "realized_clr_2025_low": realized_low,
        "realized_clr_2025_high": realized_high,
        "rcap_points": rcap_points,
        "interval_only": point is None,
        "measure_flip": flipped,
        "best_numeric_rcap": float(
            valid.loc[valid["cost_numeric"].idxmin(), "rcap_numeric"]
        ),
        "near_optimal_band": float(near_optimal_band),
        "reason": "near_optimal_rcap_band",
    }


def robust_rcap_interval(
    base_frontier: pd.DataFrame,
    sensitivity_frontiers: dict[str, pd.DataFrame],
    *,
    region_id: str,
    near_optimal_band: float = 0.05,
) -> dict[str, Any]:
    """在同一 Rcap 维度上求基准/敏感性近优带的稳健交集。"""
    scenarios: dict[str, dict[str, Any]] = {
        "base": recommended_rcap_interval(
            base_frontier,
            region_id=region_id,
            near_optimal_band=near_optimal_band,
        )
    }
    for label, frame in sensitivity_frontiers.items():
        scenarios[str(label)] = recommended_rcap_interval(
            frame,
            region_id=region_id,
            near_optimal_band=near_optimal_band,
        )

    point_sets = [
        {round(float(value), 10) for value in result["rcap_points"]}
        for result in scenarios.values()
    ]
    if not point_sets or any(not points for points in point_sets):
        robust_points: list[float] = []
    else:
        robust_points = sorted(set.intersection(*point_sets))
    return {
        "region_id": region_id,
        "robust": bool(robust_points),
        "robust_rcap_points": robust_points,
        "robust_rcap_interval_low": min(robust_points) if robust_points else None,
        "robust_rcap_interval_high": max(robust_points) if robust_points else None,
        "scenario_results": scenarios,
        "near_optimal_band": float(near_optimal_band),
        "reason": (
            "same_dimension_rcap_intersection"
            if robust_points
            else "no_common_near_optimal_rcap_across_scenarios"
        ),
    }
