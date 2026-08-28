"""v3.2 实际资产主模型的 cosφ / 反向承载系数敏感性。

同一敏感性场景内复用候选、时序适配器及缓存，再顺序扫描给定 Rcap 点；
不修改正式 ``model_contract.yaml``，而是在运行目录写场景合同副本。
"""
from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path
from typing import Iterable

import pandas as pd
import yaml

from src.v3_pipeline import _annual_input, _timeseries_gate
from src.v3_planner import PATH_OPT_STRICT, PATH_OPT_UNBOUNDED, optimize_path
from src.v32_actual_pipeline import _planner_kwargs, _prepare_expansion_candidates
from src.v32_contract import load_v32_contract
from src.v32_frontier import _attach_metrics, _summarize_point
from src.v32_policy import apply_actual_asset_policy_baseline, prepare_grandfathered_rcap_control
from src.v32_time_physics import V32TimePhysicsEvaluator


class V32SensitivityError(ValueError):
    """敏感性场景参数或求解结果不满足要求。"""


def _write_scenario_contract(
    base_contract_path: Path,
    output_path: Path,
    *,
    reverse_beta: float,
) -> Path:
    raw = yaml.safe_load(Path(base_contract_path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise V32SensitivityError("base model contract must decode to a mapping")
    scenario = deepcopy(raw)
    scenario["technical_parameters"]["reverse_beta"]["split_or_single"] = float(reverse_beta)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        yaml.safe_dump(scenario, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )
    return output_path


def run_v32_parameter_frontier(
    project_root: Path,
    processed_root: Path,
    run_dir: Path,
    *,
    cos_phi: float,
    reverse_beta: float,
    rcap_points: Iterable[float],
    include_unbounded: bool = True,
) -> pd.DataFrame:
    """在一个参数场景下求给定 Rcap 前沿，返回 110 kV 汇总。"""
    if not math.isfinite(float(cos_phi)) or not (0 < float(cos_phi) <= 1):
        raise V32SensitivityError("cos_phi must be in (0,1]")
    if not math.isfinite(float(reverse_beta)) or not (0 <= float(reverse_beta) <= 1):
        raise V32SensitivityError("reverse_beta must be in [0,1]")
    points = sorted({round(float(value), 10) for value in rcap_points})
    if not points or any(not math.isfinite(value) or value <= 0 for value in points):
        raise V32SensitivityError("rcap_points must contain positive finite values")

    project_root = Path(project_root).resolve()
    processed_root = Path(processed_root).resolve()
    run_dir = Path(run_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    resolved = load_v32_contract(project_root)
    if not bool(_timeseries_gate(processed_root).get("formal_hourly_use_allowed")):
        raise V32SensitivityError("QX-00005 approved hourly evidence gate is not open")

    base_contract_path = project_root / "model_contract.yaml"
    scenario_contract = _write_scenario_contract(
        base_contract_path,
        run_dir / "scenario_contract.yaml",
        reverse_beta=float(reverse_beta),
    )
    candidates, _ = _prepare_expansion_candidates(
        processed_root, run_dir, base_contract_path
    )
    annual = _annual_input(processed_root)
    annual = annual[annual["voltage_kv"].astype(int).eq(110)].copy()
    annual["reverse_beta"] = float(reverse_beta)
    evaluator = V32TimePhysicsEvaluator(
        processed_root,
        run_dir / "time_physics",
        candidates,
        scenario_contract,
    )
    kwargs = _planner_kwargs(
        resolved, evaluator, cos_phi=float(cos_phi)
    )

    summaries: list[pd.DataFrame] = []
    sequence: list[float | None] = list(points)
    if include_unbounded:
        sequence.append(None)
    for rcap in sequence:
        if rcap is None:
            model_input = apply_actual_asset_policy_baseline(annual)
            result = optimize_path(
                model_input,
                candidates,
                path_id=PATH_OPT_UNBOUNDED,
                **kwargs,
            )
        else:
            model_input = prepare_grandfathered_rcap_control(
                annual,
                rcap=float(rcap),
                applies_to_voltage_kv=(110,),
            )
            result = optimize_path(
                model_input,
                candidates,
                path_id=PATH_OPT_STRICT,
                clr_limit=float(rcap),
                **kwargs,
            )
        years = _attach_metrics(result["path_year_results"])
        summary = _summarize_point(
            rcap=rcap,
            years=years,
            actions=result["path_action_results"],
            costs=result["path_cost_breakdown"],
        )
        summary["cos_phi"] = float(cos_phi)
        summary["reverse_beta"] = float(reverse_beta)
        summaries.append(summary)

    frontier = pd.concat(summaries, ignore_index=True, sort=False)
    frontier["scenario_id"] = (
        f"pf{float(cos_phi):.2f}_beta{float(reverse_beta):.2f}"
    )
    frontier.to_csv(run_dir / "parameter_frontier.csv", index=False)
    metadata = {
        "scenario_id": frontier["scenario_id"].iloc[0],
        "cos_phi": float(cos_phi),
        "reverse_beta": float(reverse_beta),
        "rcap_points": points,
        "include_unbounded": bool(include_unbounded),
        "physical_baseline": "actual_2021_installed_capacity",
        "retirement_candidates_enabled": False,
        "scenario_contract": str(scenario_contract.name),
    }
    (run_dir / "scenario_manifest.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return frontier
