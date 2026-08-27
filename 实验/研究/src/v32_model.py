"""v3.2 同基线政策实验与弹性 Rcap 推荐逻辑。

本模块先作为 v3.2 候选实现层复用已经回归验证的 v3 离散规划器，避免在
科学口径尚在升级阶段复制求解核心。主要变化：

1. 两条政策路径共享 ``S0_plan = 2 * P+_2021``；
2. 物理资产基准与规划控制基准显式分层；
3. 恢复同基线路径成本包含关系；
4. 推荐量明确为 Rcap，实际 CLR 只作为对应实现结果。
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

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
) -> pd.DataFrame:
    """为所有政策路径生成同一个 2021 规划控制基线。

    ``planning_baseline_capacity_mva = baseline_clr * P+_2021``。
    只读取 2021 年官方同步正向最大负荷，不读取任何决策期峰值，因此不会
    产生“用未来实际最低峰反推初始容量”的信息泄漏。

    ``baseline_capacity_mva`` 是物理资产状态，保持原值；为了复用 v3.1
    求解器，临时兼容列 ``reported_baseline_capacity_mva`` 与规划基线等值。
    正式 v3.2 输出使用 ``planning_*`` 术语，不对甲方暴露旧兼容命名。
    """
    if not math.isfinite(float(baseline_clr)) or float(baseline_clr) <= 0:
        raise V32ModelError("baseline_clr must be positive and finite")
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

    reference_path = Path(processed_root) / "annual_reference.csv"
    if not reference_path.is_file():
        raise V32ModelError("annual_reference.csv is required for the 2021 planning baseline")
    reference = pd.read_csv(reference_path)
    reference_required = {
        "year",
        "region_id",
        "voltage_kv",
        "official_positive_peak_mw",
    }
    ref_missing = reference_required - set(reference.columns)
    if ref_missing:
        raise V32ModelError(f"annual_reference.csv missing {sorted(ref_missing)}")

    base = reference[reference["year"].eq(2021)][
        ["region_id", "voltage_kv", "official_positive_peak_mw"]
    ].copy()
    if base.empty:
        raise V32ModelError("2021 official positive-peak reference is empty")
    if base.duplicated(["region_id", "voltage_kv"]).any():
        raise V32ModelError("2021 reference has duplicate region-voltage rows")
    base["planning_baseline_capacity_mva"] = (
        float(baseline_clr) * pd.to_numeric(base["official_positive_peak_mw"], errors="raise")
    )
    if (base["planning_baseline_capacity_mva"] <= 0).any():
        raise V32ModelError("2021 positive peak must be positive for every modeled group")

    out = annual.copy()
    out["region_id"] = out["region_id"].astype(str)
    base["region_id"] = base["region_id"].astype(str)
    out = out.merge(
        base[
            [
                "region_id",
                "voltage_kv",
                "planning_baseline_capacity_mva",
            ]
        ],
        on=["region_id", "voltage_kv"],
        how="left",
        validate="many_to_one",
    )
    if out["planning_baseline_capacity_mva"].isna().any():
        missing_groups = (
            out.loc[
                out["planning_baseline_capacity_mva"].isna(),
                ["region_id", "voltage_kv"],
            ]
            .drop_duplicates()
            .astype(str)
            .agg("|".join, axis=1)
            .tolist()
        )
        raise V32ModelError(
            "2021 planning baseline reference missing for groups: "
            + ", ".join(missing_groups)
        )

    # v3.1 planner compatibility alias.  Both paths receive the exact same column.
    out["reported_baseline_capacity_mva"] = out[
        "planning_baseline_capacity_mva"
    ]
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

    unbounded = optimize_path(
        annual,
        candidates,
        path_id=PATH_OPT_UNBOUNDED,
        **planner_kwargs,
    )
    parts: list[dict[str, pd.DataFrame]] = [unbounded]
    for voltage_kv, limit in ((110, 2.0), (35, math.inf)):
        sub = annual[annual["voltage_kv"].astype(int).eq(voltage_kv)]
        if sub.empty:
            continue
        parts.append(
            optimize_path(
                sub,
                candidates,
                path_id=PATH_OPT_STRICT,
                clr_limit=limit,
                **planner_kwargs,
            )
        )
    merged = _merge_policy_outputs(parts)
    validate_path_inclusion(merged["path_cost_breakdown"])
    return _attach_v32_planning_columns(merged, annual)


def _numeric_feasible_frontier(frontier: pd.DataFrame, region_id: str) -> pd.DataFrame:
    required = {
        "rcap",
        "region_id",
        "cumulative_in_service_eac_wanyuan",
        "clr_2025",
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
    sub["clr_numeric"] = pd.to_numeric(sub["clr_2025"], errors="coerce")
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
    """从一个场景的前沿提取 Rcap 近优带及对应实现 CLR 范围。"""
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

    best = float(valid["cost_numeric"].min())
    band = valid[
        valid["cost_numeric"] <= best * (1.0 + float(near_optimal_band)) + 1e-9
    ].copy()
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
