"""v3.2 主政策实验：实际资产共同起点 + 存量豁免的增量 Rcap 控制。

规划实践通常以“规划年负荷×目标容载比”形成目标容量，再与已有容量比较
得到新增容量需求。因此主政策对照不改写 2021 已有主变容量，也不为了让
历史 CLR 硬等于目标值而虚构退役。

刚性策略的 Rcap 作用于决策期新增容量：若 2021 存量容量已高于
``Rcap * P_y``，该存量被 grandfather（存量豁免），但不允许继续增加容量；
只有当负荷增长使 ``Rcap * P_y`` 超过存量基准后，才释放对应新增容量空间。
"""
from __future__ import annotations

import math
from typing import Any

import pandas as pd

from src.v3_planner import (
    PATH_OPT_STRICT,
    PATH_OPT_UNBOUNDED,
    optimize_path,
    validate_path_inclusion,
)


class V32PolicyError(ValueError):
    """实际资产共同基线政策实验不满足约束。"""


def apply_actual_asset_policy_baseline(annual: pd.DataFrame) -> pd.DataFrame:
    """把两条政策路径共同起点锁定为真实 2021 在役容量。"""
    required = {
        "region_id",
        "voltage_kv",
        "year",
        "baseline_capacity_mva",
        "positive_peak_mw",
    }
    missing = required - set(annual.columns)
    if missing:
        raise V32PolicyError(f"annual frame missing {sorted(missing)}")
    out = annual.copy()
    base = pd.to_numeric(out["baseline_capacity_mva"], errors="raise")
    if (base <= 0).any():
        raise V32PolicyError("physical 2021 baseline capacity must be positive")
    out["planning_baseline_capacity_mva"] = base
    # 对无上限路径，兼容列与真实物理基线相同，因此内部 CLR 也是物理 CLR。
    out["reported_baseline_capacity_mva"] = base
    return out


def prepare_grandfathered_rcap_control(
    annual: pd.DataFrame,
    *,
    rcap: float,
    applies_to_voltage_kv: tuple[int, ...] = (110,),
) -> pd.DataFrame:
    """把硬 CLR 检查转换为“存量豁免、只约束新增容量”的 Rcap 控制。

    v3 求解器内部约束为 ``reported_capacity <= rcap * P``。令
    ``reported_base_y = min(S_2021, rcap * P_y)``，则对动作增量 ``ΔS``：

    ``reported_base_y + ΔS <= rcap * P_y``

    等价于：
    ``ΔS <= max(rcap * P_y - S_2021, 0)``。

    因此无需改变真实物理容量，也不会强迫退役已有设备。
    ``reported_*`` 在本模块中仅是求解器约束辅助状态，正式输出使用
    ``policy_control_*`` 命名，并另列真实 ``physical_clr``。
    """
    if not math.isfinite(float(rcap)) or float(rcap) <= 0:
        raise V32PolicyError("rcap must be positive and finite")
    out = apply_actual_asset_policy_baseline(annual)
    voltage_set = {int(value) for value in applies_to_voltage_kv}
    mask = out["voltage_kv"].astype(int).isin(voltage_set)
    cap = float(rcap) * pd.to_numeric(out["positive_peak_mw"], errors="raise")
    base = pd.to_numeric(out["baseline_capacity_mva"], errors="raise")
    out.loc[mask, "reported_baseline_capacity_mva"] = pd.concat(
        [base[mask], cap[mask]], axis=1
    ).min(axis=1)
    out["policy_rcap"] = math.inf
    out.loc[mask, "policy_rcap"] = float(rcap)
    out["legacy_capacity_grandfathered"] = False
    out.loc[mask, "legacy_capacity_grandfathered"] = base[mask] > cap[mask] + 1e-9
    return out


def _merge(parts: list[dict[str, pd.DataFrame]]) -> dict[str, pd.DataFrame]:
    return {
        name: pd.concat(
            [part[name] for part in parts], ignore_index=True, sort=False
        )
        for name in (
            "path_year_results",
            "path_action_results",
            "path_cost_breakdown",
        )
    }


def _attach_physical_policy_metrics(
    result: dict[str, pd.DataFrame],
    annual: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    years = result["path_year_results"].copy()
    baseline = annual[
        ["region_id", "voltage_kv", "baseline_capacity_mva"]
    ].drop_duplicates()
    years = years.merge(
        baseline,
        on=["region_id", "voltage_kv"],
        how="left",
        validate="many_to_one",
        suffixes=("", "_common"),
    )
    pplus = pd.to_numeric(years["p_plus_mw"], errors="raise")
    installed = pd.to_numeric(years["installed_capacity_mva"], errors="raise")
    years["physical_clr"] = installed / pplus.where(pplus > 0)
    years["policy_control_capacity_mva"] = pd.to_numeric(
        years["reported_capacity_mva"], errors="coerce"
    )
    years["policy_control_ratio"] = pd.to_numeric(years["clr"], errors="coerce")
    result = dict(result)
    result["path_year_results"] = years
    return result


def validate_grandfathered_rcap(
    years: pd.DataFrame,
    *,
    rcap: float,
    voltage_kv: int = 110,
) -> bool:
    """验证刚性路径没有超过存量豁免后的新增容量空间。"""
    sub = years[
        years["path_id"].astype(str).eq(PATH_OPT_STRICT)
        & years["voltage_kv"].astype(int).eq(int(voltage_kv))
        & years["status"].astype(str).eq("feasible")
    ].copy()
    if sub.empty:
        return True
    allowed = pd.concat(
        [
            pd.to_numeric(sub["baseline_capacity_mva"], errors="raise"),
            float(rcap) * pd.to_numeric(sub["p_plus_mw"], errors="raise"),
        ],
        axis=1,
    ).max(axis=1)
    installed = pd.to_numeric(sub["installed_capacity_mva"], errors="raise")
    if (installed > allowed + 1e-7).any():
        bad = sub.loc[installed > allowed + 1e-7, ["region_id", "year"]]
        raise V32PolicyError(
            "grandfathered Rcap capacity envelope violated: "
            + ",".join(bad.astype(str).agg("|".join, axis=1))
        )
    return True


def run_actual_asset_policy_paths(
    annual: pd.DataFrame,
    candidates: pd.DataFrame,
    *,
    planner_kwargs: dict[str, Any],
    rigid_rcap: float = 2.0,
) -> dict[str, pd.DataFrame]:
    """求解主政策对照：同一真实资产起点，刚性方案仅限制新增容量。"""
    common = apply_actual_asset_policy_baseline(annual)
    elastic = optimize_path(
        common,
        candidates,
        path_id=PATH_OPT_UNBOUNDED,
        **planner_kwargs,
    )

    rigid_110_input = prepare_grandfathered_rcap_control(
        annual[annual["voltage_kv"].astype(int).eq(110)],
        rcap=float(rigid_rcap),
        applies_to_voltage_kv=(110,),
    )
    parts: list[dict[str, pd.DataFrame]] = [elastic]
    if not rigid_110_input.empty:
        parts.append(
            optimize_path(
                rigid_110_input,
                candidates,
                path_id=PATH_OPT_STRICT,
                clr_limit=float(rigid_rcap),
                **planner_kwargs,
            )
        )
    auxiliary = common[common["voltage_kv"].astype(int).eq(35)]
    if not auxiliary.empty:
        parts.append(
            optimize_path(
                auxiliary,
                candidates,
                path_id=PATH_OPT_STRICT,
                clr_limit=math.inf,
                **planner_kwargs,
            )
        )
    merged = _attach_physical_policy_metrics(_merge(parts), common)
    # 两方案物理起点、候选、约束和成本库一致，弹性可行域包含刚性可行域。
    validate_path_inclusion(merged["path_cost_breakdown"])
    validate_grandfathered_rcap(
        merged["path_year_results"], rcap=float(rigid_rcap), voltage_kv=110
    )
    return merged
