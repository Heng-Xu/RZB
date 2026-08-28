"""v3.2 主模型：实际 2021 资产共同起点 + 存量豁免增量 Rcap。

本流水线只做两条主政策路径及基础物理/经济诊断。Rcap 前沿和敏感性在
主路径通过真实数据验证后由独立流水线计算，避免把长时间扫描与基础模型
正确性混在一起。
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.real_costs import (
    annualized_eac_wanyuan,
    build_real_cost_library,
    storage_capex_wanyuan,
)
from src.v3_pipeline import (
    _actual_path_actions,
    _actual_path_cost_breakdown,
    _actual_path_year_results,
    _annual_input,
    _timeseries_gate,
)
from src.v32_contract import load_v32_contract
from src.v32_physics import build_station_gap_diagnostics
from src.v32_policy import run_actual_asset_policy_paths
from src.v32_time_physics import V32TimePhysicsEvaluator


class V32ActualPipelineError(ValueError):
    """v3.2 实际资产主政策流水线不满足发布前置条件。"""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _prepare_expansion_candidates(
    processed_root: Path,
    run_dir: Path,
    base_contract_path: Path,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """主模型只保留可追溯扩建/新建候选，不生成“为压CLR而退役”候选。"""
    cost_manifest = build_real_cost_library(
        processed_root,
        run_dir / "cost_library",
        base_contract_path,
    )
    candidates = pd.read_csv(run_dir / "cost_library" / "expansion_cost_library.csv")
    if "available_year" not in candidates.columns:
        candidates["available_year"] = 2022
        candidates["quality_flag"] = (
            candidates["quality_flag"].astype(str)
            + ";counterfactual_candidate_available_from_2022_model_assumption"
        )
    retirement_mask = candidates["candidate_type"].astype(str).str.contains(
        "retire", case=False, na=False
    )
    if retirement_mask.any():
        raise V32ActualPipelineError(
            "primary expansion library unexpectedly contains retirement candidates"
        )
    return candidates, cost_manifest


def _planner_kwargs(
    contract: dict[str, Any],
    evaluator: V32TimePhysicsEvaluator,
    *,
    cos_phi: float,
) -> dict[str, Any]:
    def storage_action_capex(modules: int) -> float:
        return storage_capex_wanyuan(modules, contract)

    def storage_action_eac(modules: int) -> float:
        return annualized_eac_wanyuan(
            storage_action_capex(modules),
            float(contract["costs"]["annualization"]["discount_rate"]),
            int(contract["costs"]["annualization"]["storage_life_years"]),
            float(
                contract["costs"]["annualization"][
                    "storage_fixed_om_fraction_per_year"
                ]
            ),
        )

    return {
        "cos_phi": float(cos_phi),
        "module_power_mw": float(contract["storage"]["module"]["power_mw"]),
        "storage_capex_wanyuan_for_modules": storage_action_capex,
        "storage_eac_wanyuan_for_modules": storage_action_eac,
        "state_physics_evaluator": evaluator.evaluator(float(cos_phi)),
    }


def _policy_cost_comparison(costs: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (region_id, voltage_kv), group in costs.groupby(
        ["region_id", "voltage_kv"], sort=True
    ):
        lookup = group.set_index("path_id")
        elastic = lookup.loc["PATH_OPT_CLR_UNBOUNDED"]
        rigid = lookup.loc["PATH_OPT_CLR_LE_2"]
        both_feasible = (
            str(elastic["status"]) == "feasible"
            and str(rigid["status"]) == "feasible"
        )
        elastic_cost = (
            float(elastic["cumulative_in_service_eac_wanyuan"])
            if both_feasible
            else None
        )
        rigid_cost = (
            float(rigid["cumulative_in_service_eac_wanyuan"])
            if both_feasible
            else None
        )
        delta = None if not both_feasible else rigid_cost - elastic_cost
        if delta is not None and delta < -1e-7:
            raise V32ActualPipelineError(
                f"elastic feasible set inclusion violated for {region_id}|{voltage_kv}"
            )
        rows.append(
            {
                "region_id": str(region_id),
                "voltage_kv": int(voltage_kv),
                "elastic_status": str(elastic["status"]),
                "rigid_status": str(rigid["status"]),
                "elastic_cumulative_eac_wanyuan": elastic_cost,
                "rigid_cumulative_eac_wanyuan": rigid_cost,
                "rigid_minus_elastic_eac_wanyuan": delta,
                "direct_comparison_allowed": bool(both_feasible),
                "comparison_basis": "same_actual_2021_asset_baseline_grandfathered_incremental_rcap",
            }
        )
    return pd.DataFrame(rows)


def _final_policy_summary(
    years: pd.DataFrame,
    actions: pd.DataFrame,
    costs: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (region_id, voltage_kv, path_id), cost_group in costs.groupby(
        ["region_id", "voltage_kv", "path_id"], sort=True
    ):
        cost = cost_group.iloc[0]
        final = years[
            years["region_id"].astype(str).eq(str(region_id))
            & years["voltage_kv"].astype(int).eq(int(voltage_kv))
            & years["path_id"].astype(str).eq(str(path_id))
            & years["year"].eq(2025)
        ]
        selected_actions = actions[
            actions["region_id"].astype(str).eq(str(region_id))
            & actions["voltage_kv"].astype(int).eq(int(voltage_kv))
            & actions["path_id"].astype(str).eq(str(path_id))
        ]
        action_types = (
            ";".join(sorted(set(selected_actions["action_type"].astype(str))))
            if not selected_actions.empty
            else "none"
        )
        candidate_ids = (
            ";".join(
                sorted(
                    set(
                        selected_actions.get(
                            "candidate_id", pd.Series(dtype=str)
                        ).dropna().astype(str)
                    )
                )
            )
            if not selected_actions.empty
            else ""
        )
        if final.empty or str(cost["status"]) != "feasible":
            rows.append(
                {
                    "region_id": str(region_id),
                    "voltage_kv": int(voltage_kv),
                    "path_id": str(path_id),
                    "status": str(cost["status"]),
                    "physical_clr_2025": None,
                    "policy_control_ratio_2025": None,
                    "installed_capacity_mva_2025": None,
                    "storage_modules_2025": None,
                    "cumulative_in_service_eac_wanyuan": None,
                    "action_types": action_types,
                    "candidate_ids": candidate_ids,
                }
            )
            continue
        row = final.iloc[0]
        rows.append(
            {
                "region_id": str(region_id),
                "voltage_kv": int(voltage_kv),
                "path_id": str(path_id),
                "status": "feasible",
                "physical_clr_2025": float(row["physical_clr"]),
                "policy_control_ratio_2025": float(row["policy_control_ratio"]),
                "installed_capacity_mva_2025": float(row["installed_capacity_mva"]),
                "p_plus_mw_2025": float(row["p_plus_mw"]),
                "p_minus_mw_2025": float(row["p_minus_mw"]),
                "storage_modules_2025": int(row["storage_modules"]),
                "cumulative_in_service_eac_wanyuan": float(
                    cost["cumulative_in_service_eac_wanyuan"]
                ),
                "action_types": action_types,
                "candidate_ids": candidate_ids,
            }
        )
    return pd.DataFrame(rows)


def _chronology_comparison(
    evaluator: V32TimePhysicsEvaluator,
    actions: pd.DataFrame,
    *,
    cos_phi: float,
) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for path_id in ("PATH_OPT_CLR_UNBOUNDED", "PATH_OPT_CLR_LE_2"):
        sub = actions[
            actions["path_id"].astype(str).eq(path_id)
            & actions["region_id"].astype(str).eq("QX-00005")
            & actions["voltage_kv"].astype(int).eq(110)
        ]
        selected = tuple(
            sorted(
                {
                    str(value)
                    for value in sub.get(
                        "candidate_id", pd.Series(dtype=str)
                    ).dropna().astype(str)
                    if str(value)
                }
            )
        )
        comparison = evaluator.chronology_comparison(selected, cos_phi=float(cos_phi))
        comparison.insert(0, "path_id", path_id)
        parts.append(comparison)
    return pd.concat(parts, ignore_index=True)


def run_v32_actual_baseline(
    project_root: Path,
    processed_root: Path,
    run_dir: Path,
) -> dict[str, Any]:
    project_root = Path(project_root).resolve()
    processed_root = Path(processed_root).resolve()
    run_dir = Path(run_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)

    contract = load_v32_contract(project_root)
    base_contract_path = project_root / "model_contract.yaml"
    if not (processed_root / "manifest.json").is_file():
        raise V32ActualPipelineError(
            "v3.2 requires the audited real_2021_2025 processed dataset"
        )
    gate = _timeseries_gate(processed_root)
    if not bool(gate.get("formal_hourly_use_allowed")):
        raise V32ActualPipelineError("QX-00005 approved hourly evidence gate is not open")

    candidates, cost_manifest = _prepare_expansion_candidates(
        processed_root, run_dir, base_contract_path
    )
    annual = _annual_input(processed_root)
    cos_phi = float(contract["technical_parameters"]["cos_phi"]["baseline"])
    beta = float(contract["technical_parameters"]["reverse_beta"]["split_or_single"])

    station_diag, gap_summary = build_station_gap_diagnostics(
        processed_root,
        contract,
        cos_phi=cos_phi,
        reverse_beta=beta,
    )
    station_diag.to_csv(run_dir / "station_gap_diagnostics.csv", index=False)
    gap_summary.to_csv(run_dir / "region_gap_summary.csv", index=False)

    evaluator = V32TimePhysicsEvaluator(
        processed_root,
        run_dir / "time_physics",
        candidates,
        base_contract_path,
    )
    planner = run_actual_asset_policy_paths(
        annual,
        candidates,
        planner_kwargs=_planner_kwargs(contract, evaluator, cos_phi=cos_phi),
        rigid_rcap=2.0,
    )
    years = planner["path_year_results"]
    actions = planner["path_action_results"]
    costs = planner["path_cost_breakdown"]
    years.to_csv(run_dir / "policy_path_year_results.csv", index=False)
    actions.to_csv(run_dir / "policy_path_action_results.csv", index=False)
    costs.to_csv(run_dir / "policy_path_cost_breakdown.csv", index=False)

    cost_comparison = _policy_cost_comparison(costs)
    cost_comparison.to_csv(run_dir / "policy_cost_comparison.csv", index=False)
    summary = _final_policy_summary(years, actions, costs)
    summary.to_csv(run_dir / "policy_2025_summary.csv", index=False)
    chronology = _chronology_comparison(evaluator, actions, cos_phi=cos_phi)
    chronology.to_csv(run_dir / "qx00005_chronology_comparison.csv", index=False)

    _actual_path_year_results(processed_root).to_csv(
        run_dir / "actual_path_year_results.csv", index=False
    )
    _actual_path_actions(processed_root).to_csv(
        run_dir / "actual_path_action_results.csv", index=False
    )
    _actual_path_cost_breakdown(processed_root).to_csv(
        run_dir / "actual_path_cost_breakdown.csv", index=False
    )

    manifest = {
        "model_version": "3.2.0-candidate",
        "model_role": "primary_actual_asset_grandfathered_incremental_rcap",
        "status": "baseline_policy_paths_before_rcap_frontier_and_sensitivity",
        "processed_manifest_sha256": _sha256(processed_root / "manifest.json"),
        "base_contract_sha256": _sha256(base_contract_path),
        "cost_manifest": cost_manifest,
        "common_physical_baseline": "actual_2021_installed_capacity",
        "rigid_policy": "legacy_capacity_grandfathered_incremental_Rcap_2.0",
        "rigid_capacity_rule": "DeltaS <= max(2.0*P_plus_y - S_2021, 0)",
        "retirement_candidates_enabled": False,
        "direct_policy_cost_comparison_allowed": True,
        "formal_clr_output": "physical_clr = installed_capacity_mva / synchronized_positive_peak_mw",
        "policy_control_ratio_is_internal_audit_metric": True,
        "qx00005_110kv_time_method": "approved_8760_continuous_soc_primary_plus_daily_cyclic_reference",
        "timeseries_formal_hourly_use_allowed": True,
        "rcap_frontier_completed": False,
        "sensitivity_completed": False,
        "report_update_allowed": False,
    }
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest
