"""v3.2 主模型的实际资产 Rcap 前沿单点求解。

每个 Rcap 点独立求解 110 kV 正式层，保留年度状态、动作与成本底稿；
``rcap=None`` 表示无统一上限的弹性基准。主模型不生成退役候选。
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import pandas as pd

from src.v3_pipeline import _annual_input, _timeseries_gate
from src.v3_planner import PATH_OPT_STRICT, PATH_OPT_UNBOUNDED, optimize_path
from src.v32_actual_pipeline import _planner_kwargs, _prepare_expansion_candidates
from src.v32_contract import load_v32_contract
from src.v32_policy import apply_actual_asset_policy_baseline, prepare_grandfathered_rcap_control
from src.v32_time_physics import V32TimePhysicsEvaluator


class V32FrontierError(ValueError):
    """Rcap 前沿单点无法形成可审计结果。"""


def _point_label(rcap: float | None) -> str:
    return "unbounded" if rcap is None else f"{float(rcap):.4f}".rstrip("0").rstrip(".")


def _attach_metrics(years: pd.DataFrame) -> pd.DataFrame:
    out = years.copy()
    pplus = pd.to_numeric(out["p_plus_mw"], errors="coerce")
    installed = pd.to_numeric(out["installed_capacity_mva"], errors="coerce")
    out["physical_clr"] = installed / pplus.where(pplus > 0)
    out["policy_control_capacity_mva"] = pd.to_numeric(
        out.get("reported_capacity_mva"), errors="coerce"
    )
    out["policy_control_ratio"] = pd.to_numeric(out.get("clr"), errors="coerce")
    return out


def _summarize_point(
    *,
    rcap: float | None,
    years: pd.DataFrame,
    actions: pd.DataFrame,
    costs: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for region_id in sorted(costs["region_id"].astype(str).unique()):
        cost_row = costs[
            costs["region_id"].astype(str).eq(region_id)
            & costs["voltage_kv"].astype(int).eq(110)
        ]
        if cost_row.empty:
            raise V32FrontierError(f"missing 110 kV cost row for {region_id}")
        cost = cost_row.iloc[0]
        feasible = str(cost["status"]) == "feasible"
        final = years[
            years["region_id"].astype(str).eq(region_id)
            & years["voltage_kv"].astype(int).eq(110)
            & years["year"].eq(2025)
        ]
        selected = actions[
            actions["region_id"].astype(str).eq(region_id)
            & actions["voltage_kv"].astype(int).eq(110)
        ]
        action_types = sorted(set(selected["action_type"].astype(str))) if not selected.empty else []
        candidate_ids = sorted(
            {
                str(value)
                for value in selected.get("candidate_id", pd.Series(dtype=str)).dropna().astype(str)
                if str(value)
            }
        )
        capacity_delta = 0.0
        if not selected.empty and "delta_capacity_mva" in selected.columns:
            capacity_delta = float(
                pd.to_numeric(selected["delta_capacity_mva"], errors="coerce").fillna(0.0).sum()
            )
        record: dict[str, Any] = {
            "rcap": "unbounded" if rcap is None else float(rcap),
            "rcap_numeric": math.nan if rcap is None else float(rcap),
            "region_id": region_id,
            "voltage_kv": 110,
            "feasible": bool(feasible),
            "status": str(cost["status"]),
            "cumulative_in_service_eac_wanyuan": (
                float(cost["cumulative_in_service_eac_wanyuan"]) if feasible else math.nan
            ),
            "capacity_action_delta_mva": capacity_delta if feasible else math.nan,
            "action_types": ";".join(action_types) if action_types else "none",
            "candidate_ids": ";".join(candidate_ids),
            "selected_action_count": int(cost.get("selected_action_count", 0)),
            "policy_basis": (
                "actual_2021_asset_baseline_unbounded"
                if rcap is None
                else "actual_2021_asset_baseline_grandfathered_incremental_rcap"
            ),
            "retirement_candidates_enabled": False,
        }
        if feasible:
            if final.empty:
                raise V32FrontierError(f"missing feasible 2025 row for {region_id}")
            row = final.iloc[0]
            record.update(
                {
                    "physical_clr_2025": float(row["physical_clr"]),
                    "policy_control_ratio_2025": float(row["policy_control_ratio"]),
                    "installed_capacity_mva_2025": float(row["installed_capacity_mva"]),
                    "storage_modules": int(row["storage_modules"]),
                    "p_plus_mw_2025": float(row["p_plus_mw"]),
                    "p_minus_mw_2025": float(row["p_minus_mw"]),
                }
            )
        else:
            record.update(
                {
                    "physical_clr_2025": math.nan,
                    "policy_control_ratio_2025": math.nan,
                    "installed_capacity_mva_2025": math.nan,
                    "storage_modules": math.nan,
                    "p_plus_mw_2025": math.nan,
                    "p_minus_mw_2025": math.nan,
                }
            )
        rows.append(record)
    return pd.DataFrame(rows)


def run_v32_frontier_point(
    project_root: Path,
    processed_root: Path,
    run_dir: Path,
    *,
    rcap: float | None,
    cos_phi: float | None = None,
) -> pd.DataFrame:
    """求解一个 110 kV Rcap 点并写出完整审计底稿。"""
    project_root = Path(project_root).resolve()
    processed_root = Path(processed_root).resolve()
    run_dir = Path(run_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    if rcap is not None and (not math.isfinite(float(rcap)) or float(rcap) <= 0):
        raise V32FrontierError("rcap must be positive finite or None")

    contract = load_v32_contract(project_root)
    gate = _timeseries_gate(processed_root)
    if not bool(gate.get("formal_hourly_use_allowed")):
        raise V32FrontierError("QX-00005 approved hourly evidence gate is not open")
    base_contract_path = project_root / "model_contract.yaml"
    candidates, _ = _prepare_expansion_candidates(processed_root, run_dir, base_contract_path)
    annual = _annual_input(processed_root)
    annual_110 = annual[annual["voltage_kv"].astype(int).eq(110)].copy()
    if annual_110.empty:
        raise V32FrontierError("110 kV formal annual input is empty")

    pf = (
        float(contract["technical_parameters"]["cos_phi"]["baseline"])
        if cos_phi is None
        else float(cos_phi)
    )
    evaluator = V32TimePhysicsEvaluator(
        processed_root,
        run_dir / "time_physics",
        candidates,
        base_contract_path,
    )
    kwargs = _planner_kwargs(contract, evaluator, cos_phi=pf)
    if rcap is None:
        model_input = apply_actual_asset_policy_baseline(annual_110)
        path_id = PATH_OPT_UNBOUNDED
        result = optimize_path(model_input, candidates, path_id=path_id, **kwargs)
    else:
        model_input = prepare_grandfathered_rcap_control(
            annual_110, rcap=float(rcap), applies_to_voltage_kv=(110,)
        )
        path_id = PATH_OPT_STRICT
        result = optimize_path(
            model_input,
            candidates,
            path_id=path_id,
            clr_limit=float(rcap),
            **kwargs,
        )

    years = _attach_metrics(result["path_year_results"])
    actions = result["path_action_results"].copy()
    costs = result["path_cost_breakdown"].copy()
    years["frontier_rcap"] = _point_label(rcap)
    actions["frontier_rcap"] = _point_label(rcap)
    costs["frontier_rcap"] = _point_label(rcap)
    years.to_csv(run_dir / "path_year_results.csv", index=False)
    actions.to_csv(run_dir / "path_action_results.csv", index=False)
    costs.to_csv(run_dir / "path_cost_breakdown.csv", index=False)
    summary = _summarize_point(rcap=rcap, years=years, actions=actions, costs=costs)
    summary["cos_phi"] = pf
    summary.to_csv(run_dir / "frontier_point.csv", index=False)
    return summary
