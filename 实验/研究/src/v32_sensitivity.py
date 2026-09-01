"""v3.2 实际资产主模型的 cosφ / 反向承载系数敏感性。

同一敏感性场景内复用候选、时序适配器及缓存，再顺序扫描给定 Rcap 点；
不修改正式 ``model_contract.yaml``，而是在运行目录写场景合同副本。
"""
from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

import pandas as pd
import yaml

from src.v3_pipeline import _annual_input, _timeseries_gate
from src.v3_planner import PATH_OPT_STRICT, PATH_OPT_UNBOUNDED, optimize_path
from src.v32_actual_pipeline import (
    _planner_kwargs,
    _prepare_expansion_candidates,
    scale_annual_net_load_input,
)
from src.v32_contract import load_v32_contract, validation_commit_sha
from src.v32_annualization import (
    ANNUALIZATION_FIELDS,
    apply_annualization_overrides,
    validate_annualization_overrides,
)
from src.v32_frontier import _attach_metrics, _summarize_point
from src.v32_policy import apply_actual_asset_policy_baseline, prepare_grandfathered_rcap_control
from src.v32_time_physics import V32TimePhysicsEvaluator


class V32SensitivityError(ValueError):
    """敏感性场景参数或求解结果不满足要求。"""


SENSITIVITY_PARAMETER_FIELDS = (
    "cos_phi",
    "reverse_beta",
    "net_load_scale",
    "storage_cost_multiplier",
    "expansion_cost_multiplier",
)


def validate_sensitivity_manifest_parameters(manifest: Mapping[str, Any]) -> dict[str, float]:
    """确保场景清单逐字段反映实际传入求解器的五个参数。"""
    nested = manifest.get("parameters")
    if not isinstance(nested, Mapping):
        raise V32SensitivityError("scenario manifest parameters mapping is required")
    result: dict[str, float] = {}
    for field in SENSITIVITY_PARAMETER_FIELDS:
        if field not in manifest or field not in nested:
            raise V32SensitivityError(f"scenario manifest is missing {field}")
        top = float(manifest[field])
        value = float(nested[field])
        if not math.isclose(top, value, rel_tol=0, abs_tol=1e-12):
            raise V32SensitivityError(
                f"scenario manifest parameter mismatch for {field}: {top} != {value}"
            )
        result[field] = value
    return result


def _write_scenario_contract(
    base_contract_path: Path,
    output_path: Path,
    *,
    reverse_beta: float,
    annualization_overrides: Mapping[str, Any] | None = None,
) -> Path:
    raw = yaml.safe_load(Path(base_contract_path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise V32SensitivityError("base model contract must decode to a mapping")
    scenario = deepcopy(raw)
    scenario["technical_parameters"]["reverse_beta"]["split_or_single"] = float(reverse_beta)
    if annualization_overrides:
        annual = scenario.setdefault("costs", {}).setdefault("annualization", {})
        annual.update(annualization_overrides)
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
    net_load_scale: float = 1.0,
    storage_cost_multiplier: float = 1.0,
    expansion_cost_multiplier: float = 1.0,
    annualization_overrides: Mapping[str, Any] | None = None,
    scenario_name: str | None = None,
    region_ids: Iterable[str] | None = None,
) -> pd.DataFrame:
    """在一个参数场景下求给定 Rcap 前沿，返回 110 kV 汇总。"""
    if not math.isfinite(float(cos_phi)) or not (0 < float(cos_phi) <= 1):
        raise V32SensitivityError("cos_phi must be in (0,1]")
    if not math.isfinite(float(reverse_beta)) or not (0 <= float(reverse_beta) <= 1):
        raise V32SensitivityError("reverse_beta must be in [0,1]")
    for name, value in (
        ("net_load_scale", net_load_scale),
        ("storage_cost_multiplier", storage_cost_multiplier),
        ("expansion_cost_multiplier", expansion_cost_multiplier),
    ):
        if not math.isfinite(float(value)) or float(value) <= 0:
            raise V32SensitivityError(f"{name} must be positive finite")
    points = sorted({round(float(value), 10) for value in rcap_points})
    if not points or any(not math.isfinite(value) or value <= 0 for value in points):
        raise V32SensitivityError("rcap_points must contain positive finite values")

    project_root = Path(project_root).resolve()
    processed_root = Path(processed_root).resolve()
    run_dir = Path(run_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    resolved = load_v32_contract(project_root)
    annualization = validate_annualization_overrides(
        resolved,
        annualization_overrides or {},
    )
    if not bool(_timeseries_gate(processed_root).get("formal_hourly_use_allowed")):
        raise V32SensitivityError("QX-00005 approved hourly evidence gate is not open")

    base_contract_path = project_root / "model_contract.yaml"
    scenario_contract = _write_scenario_contract(
        base_contract_path,
        run_dir / "scenario_contract.yaml",
        reverse_beta=float(reverse_beta),
        annualization_overrides=annualization,
    )
    scenario_contract_values = apply_annualization_overrides(resolved, annualization)
    scenario_contract_values["technical_parameters"]["reverse_beta"]["split_or_single"] = float(reverse_beta)
    candidates, _ = _prepare_expansion_candidates(
        processed_root,
        run_dir,
        scenario_contract,
        expansion_cost_multiplier=float(expansion_cost_multiplier),
        source_root=project_root,
    )
    annual = _annual_input(processed_root)
    annual = annual[annual["voltage_kv"].astype(int).eq(110)].copy()
    selected_regions = None
    if region_ids is not None:
        selected_regions = sorted({str(region_id) for region_id in region_ids})
        if not selected_regions:
            raise V32SensitivityError("region_ids must not be empty when provided")
        annual = annual[annual["region_id"].astype(str).isin(selected_regions)].copy()
        if annual.empty:
            raise V32SensitivityError(f"region_ids are absent from annual input: {selected_regions}")
    annual = scale_annual_net_load_input(annual, float(net_load_scale))
    annual["reverse_beta"] = float(reverse_beta)
    evaluator = V32TimePhysicsEvaluator(
        processed_root,
        run_dir / "time_physics",
        candidates,
        scenario_contract,
        net_load_scale=float(net_load_scale),
    )
    kwargs = _planner_kwargs(
        scenario_contract_values,
        evaluator,
        cos_phi=float(cos_phi),
        storage_cost_multiplier=float(storage_cost_multiplier),
    )

    summaries: list[pd.DataFrame] = []
    action_parts: list[pd.DataFrame] = []
    cost_parts: list[pd.DataFrame] = []
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
        summary["net_load_scale"] = float(net_load_scale)
        summary["storage_cost_multiplier"] = float(storage_cost_multiplier)
        summary["expansion_cost_multiplier"] = float(expansion_cost_multiplier)
        summaries.append(summary)
        action = result["path_action_results"].copy()
        action["rcap"] = "unbounded" if rcap is None else float(rcap)
        action["rcap_numeric"] = math.nan if rcap is None else float(rcap)
        action_parts.append(action)
        cost = result["path_cost_breakdown"].copy()
        cost["rcap"] = "unbounded" if rcap is None else float(rcap)
        cost["rcap_numeric"] = math.nan if rcap is None else float(rcap)
        cost_parts.append(cost)

    frontier = pd.concat(summaries, ignore_index=True, sort=False)
    scenario_id = f"pf{float(cos_phi):.2f}_beta{float(reverse_beta):.2f}"
    if not math.isclose(float(net_load_scale), 1.0):
        scenario_id += f"_nl{float(net_load_scale):.2f}"
    if not math.isclose(float(storage_cost_multiplier), 1.0):
        scenario_id += f"_sc{float(storage_cost_multiplier):.2f}"
    if not math.isclose(float(expansion_cost_multiplier), 1.0):
        scenario_id += f"_ec{float(expansion_cost_multiplier):.2f}"
    if annualization and scenario_name:
        scenario_id = str(scenario_name)
    frontier["scenario_id"] = scenario_id
    frontier.to_csv(run_dir / "parameter_frontier.csv", index=False)
    actions = pd.concat(action_parts, ignore_index=True, sort=False)
    actions["scenario_id"] = scenario_id
    actions.to_csv(run_dir / "parameter_action_results.csv", index=False)
    costs = pd.concat(cost_parts, ignore_index=True, sort=False)
    costs["scenario_id"] = scenario_id
    costs.to_csv(run_dir / "parameter_cost_breakdown.csv", index=False)
    annualization_full = dict(scenario_contract_values["costs"]["annualization"])
    annualization_full = {
        field: annualization_full[field] for field in ANNUALIZATION_FIELDS
    }
    metadata = {
        "scenario_id": frontier["scenario_id"].iloc[0],
        "scenario_name": scenario_name,
        "validation_commit_sha": validation_commit_sha(project_root),
        "cos_phi": float(cos_phi),
        "reverse_beta": float(reverse_beta),
        "net_load_scale": float(net_load_scale),
        "storage_cost_multiplier": float(storage_cost_multiplier),
        "expansion_cost_multiplier": float(expansion_cost_multiplier),
        "parameters": {
            "cos_phi": float(cos_phi),
            "reverse_beta": float(reverse_beta),
            "net_load_scale": float(net_load_scale),
            "storage_cost_multiplier": float(storage_cost_multiplier),
            "expansion_cost_multiplier": float(expansion_cost_multiplier),
        },
        "rcap_points": points,
        "include_unbounded": bool(include_unbounded),
        "physical_baseline": "actual_2021_installed_capacity",
        "retirement_candidates_enabled": False,
        "scenario_contract": str(scenario_contract.name),
        "annualization": annualization_full,
        "annualization_overrides": annualization,
        "region_ids": selected_regions,
        "baseline_control": bool(
            math.isclose(float(cos_phi), 0.95)
            and math.isclose(float(reverse_beta), 0.80)
            and math.isclose(float(net_load_scale), 1.0)
            and math.isclose(float(storage_cost_multiplier), 1.0)
            and math.isclose(float(expansion_cost_multiplier), 1.0)
            and not annualization
        ),
    }
    validate_sensitivity_manifest_parameters(metadata)
    (run_dir / "scenario_manifest.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return frontier
