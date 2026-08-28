"""真实数据 v3.2 候选流水线（不覆盖 v3.1 正式结果）。

目标：在不改写已验证成本库、离散候选与基础数据适配器的前提下，完成
同基线政策比较、QX-00005 连续 8760 h 时序门禁、110 kV Rcap 前沿及
站级物理缺口诊断。敏感性扫描在基准流水线通过后由独立阶段追加。
"""
from __future__ import annotations

import hashlib
import json
import math
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
    _retirement_candidates,
    _timeseries_gate,
)
from src.v3_planner import PATH_OPT_STRICT, optimize_path
from src.v32_contract import load_v32_contract, write_resolved_v32_contract
from src.v32_model import (
    apply_common_planning_baseline,
    recommended_rcap_interval,
    run_common_baseline_policy_paths,
)
from src.v32_physics import build_station_gap_diagnostics
from src.v32_time_physics import V32TimePhysicsEvaluator


class V32PipelineError(ValueError):
    """v3.2 正式候选流水线未满足发布前置条件。"""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _prepare_candidates(
    processed_root: Path,
    run_dir: Path,
    base_contract_path: Path,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    cost_manifest = build_real_cost_library(
        processed_root,
        run_dir / "cost_library",
        base_contract_path,
    )
    cost_library = pd.read_csv(run_dir / "cost_library" / "expansion_cost_library.csv")
    if "available_year" not in cost_library.columns:
        cost_library["available_year"] = 2022
        cost_library["quality_flag"] = (
            cost_library["quality_flag"].astype(str)
            + ";counterfactual_candidate_available_from_2022_model_assumption"
        )
    retirements = _retirement_candidates(processed_root, cost_library)
    candidates = pd.concat([cost_library, retirements], ignore_index=True, sort=False)
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
        if "PATH_OPT_CLR_UNBOUNDED" not in lookup.index or "PATH_OPT_CLR_LE_2" not in lookup.index:
            raise V32PipelineError(
                f"policy paths missing for {region_id}|{voltage_kv}"
            )
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
            raise V32PipelineError(
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
                "comparison_basis": "identical_2021_physical_and_planning_control_baselines",
            }
        )
    return pd.DataFrame(rows)


def _selected_candidate_ids(
    actions: pd.DataFrame,
    path_id: str,
    region_id: str,
    voltage_kv: int,
) -> tuple[str, ...]:
    sub = actions[
        actions["path_id"].astype(str).eq(path_id)
        & actions["region_id"].astype(str).eq(region_id)
        & actions["voltage_kv"].astype(int).eq(int(voltage_kv))
    ]
    if "candidate_id" not in sub.columns:
        return ()
    return tuple(
        sorted(
            {
                str(value)
                for value in sub["candidate_id"].dropna().astype(str)
                if str(value)
            }
        )
    )


def _solve_frontier(
    annual: pd.DataFrame,
    candidates: pd.DataFrame,
    planner_kwargs: dict[str, Any],
    rcap_points: list[float],
) -> pd.DataFrame:
    sub = annual[annual["voltage_kv"].astype(int).eq(110)].copy()
    baselines = sub.groupby("region_id")["baseline_capacity_mva"].first()
    rows: list[dict[str, Any]] = []
    for rcap in rcap_points:
        result = optimize_path(
            sub,
            candidates,
            path_id=PATH_OPT_STRICT,
            clr_limit=float(rcap),
            **planner_kwargs,
        )
        years = result["path_year_results"]
        actions = result["path_action_results"]
        costs = result["path_cost_breakdown"]
        for region_id in sorted(sub["region_id"].astype(str).unique()):
            region_years = years[years["region_id"].astype(str).eq(region_id)]
            final = region_years[region_years["year"].eq(2025)]
            cost_row = costs[costs["region_id"].astype(str).eq(region_id)]
            if final.empty or cost_row.empty or str(cost_row.iloc[0]["status"]) != "feasible":
                reason = (
                    str(final.iloc[0].get("reason", "infeasible"))
                    if not final.empty
                    else "missing_2025_result"
                )
                rows.append(
                    {
                        "rcap": float(rcap),
                        "region_id": region_id,
                        "cumulative_in_service_eac_wanyuan": None,
                        "clr_2025": None,
                        "storage_modules": None,
                        "capacity_action_delta_mva": None,
                        "feasible": False,
                        "selected_candidate_ids": "",
                        "note": reason,
                    }
                )
                continue
            row = final.iloc[0]
            region_actions = actions[
                actions["region_id"].astype(str).eq(region_id)
            ]
            candidate_ids = tuple(
                sorted(
                    {
                        str(value)
                        for value in region_actions.get(
                            "candidate_id", pd.Series(dtype=str)
                        ).dropna().astype(str)
                        if str(value)
                    }
                )
            )
            rows.append(
                {
                    "rcap": float(rcap),
                    "region_id": region_id,
                    "cumulative_in_service_eac_wanyuan": float(
                        cost_row.iloc[0]["cumulative_in_service_eac_wanyuan"]
                    ),
                    "clr_2025": float(row["clr"]),
                    "storage_modules": int(row["storage_modules"]),
                    "capacity_action_delta_mva": float(row["installed_capacity_mva"])
                    - float(baselines[region_id]),
                    "feasible": True,
                    "selected_candidate_ids": ";".join(candidate_ids),
                    "note": "",
                }
            )
    return pd.DataFrame(rows)


def _recommendation_matrix(
    frontier: pd.DataFrame,
    policy_years: pd.DataFrame,
    policy_costs: pd.DataFrame,
    *,
    near_optimal_band: float,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    cost_cmp = policy_costs.set_index(["region_id", "voltage_kv"])
    for region_id in sorted(frontier["region_id"].astype(str).unique()):
        rec = recommended_rcap_interval(
            frontier,
            region_id=region_id,
            near_optimal_band=float(near_optimal_band),
        )
        final = policy_years[
            policy_years["region_id"].astype(str).eq(region_id)
            & policy_years["voltage_kv"].astype(int).eq(110)
            & policy_years["year"].eq(2025)
        ].set_index("path_id")
        cmp_row = cost_cmp.loc[(region_id, 110)]
        rows.append(
            {
                "region_id": region_id,
                "voltage_kv": 110,
                "recommended_rcap_low": rec["rcap_interval_low"],
                "recommended_rcap_high": rec["rcap_interval_high"],
                "recommended_rcap_center": rec["rcap_point_estimate"],
                "realized_clr_2025_low": rec["realized_clr_2025_low"],
                "realized_clr_2025_high": rec["realized_clr_2025_high"],
                "measure_flip": rec["measure_flip"],
                "near_optimal_band": float(near_optimal_band),
                "elastic_clr_2025": (
                    float(final.loc["PATH_OPT_CLR_UNBOUNDED", "clr"])
                    if "PATH_OPT_CLR_UNBOUNDED" in final.index
                    else None
                ),
                "rigid_clr_2025": (
                    float(final.loc["PATH_OPT_CLR_LE_2", "clr"])
                    if "PATH_OPT_CLR_LE_2" in final.index
                    else None
                ),
                "elastic_cumulative_eac_wanyuan": cmp_row[
                    "elastic_cumulative_eac_wanyuan"
                ],
                "rigid_cumulative_eac_wanyuan": cmp_row[
                    "rigid_cumulative_eac_wanyuan"
                ],
                "rigid_minus_elastic_eac_wanyuan": cmp_row[
                    "rigid_minus_elastic_eac_wanyuan"
                ],
                "recommendation_dimension": "Rcap",
                "realized_clr_separate": True,
                "recommendation_reason": rec["reason"],
            }
        )
    return pd.DataFrame(rows)


def run_v32_pipeline(
    project_root: Path,
    processed_root: Path,
    run_dir: Path,
) -> dict[str, Any]:
    project_root = Path(project_root).resolve()
    processed_root = Path(processed_root).resolve()
    run_dir = Path(run_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)

    resolved = load_v32_contract(project_root)
    base_contract_path = project_root / "model_contract.yaml"
    resolved_contract_path = write_resolved_v32_contract(
        project_root, run_dir / "model_contract_v3_2_resolved.yaml"
    )
    if not (processed_root / "manifest.json").is_file():
        raise V32PipelineError(
            "v3.2 requires the already-audited real_2021_2025 processed dataset"
        )
    gate = _timeseries_gate(processed_root)
    if not bool(gate.get("formal_hourly_use_allowed")):
        raise V32PipelineError("QX-00005 approved hourly evidence gate is not open")

    candidates, cost_manifest = _prepare_candidates(
        processed_root, run_dir, base_contract_path
    )
    annual = _annual_input(processed_root)
    annual = apply_common_planning_baseline(
        annual,
        processed_root,
        baseline_clr=float(resolved["planning_baseline"]["baseline_clr"]),
        applies_to_voltage_kv=resolved["planning_baseline"]["applies_to_voltage_kv"],
    )

    # v3.2 不再把旧静态设备缺口叠加进年度 aggregate requirement；最终
    # 工程措施由站级时序物理门禁决定。静态极值仅作为独立诊断输出。
    station_diag, gap_summary = build_station_gap_diagnostics(
        processed_root,
        resolved,
        cos_phi=float(resolved["technical_parameters"]["cos_phi"]["baseline"]),
        reverse_beta=float(resolved["technical_parameters"]["reverse_beta"]["split_or_single"]),
    )
    station_diag.to_csv(run_dir / "station_gap_diagnostics.csv", index=False)
    gap_summary.to_csv(run_dir / "region_gap_summary.csv", index=False)

    evaluator = V32TimePhysicsEvaluator(
        processed_root,
        run_dir / "time_physics",
        candidates,
        base_contract_path,
    )
    cos_phi = float(resolved["technical_parameters"]["cos_phi"]["baseline"])
    planner_kwargs = _planner_kwargs(resolved, evaluator, cos_phi=cos_phi)
    planner = run_common_baseline_policy_paths(
        annual,
        candidates,
        planner_kwargs=planner_kwargs,
    )
    planner["path_year_results"].to_csv(
        run_dir / "policy_path_year_results.csv", index=False
    )
    planner["path_action_results"].to_csv(
        run_dir / "policy_path_action_results.csv", index=False
    )
    planner["path_cost_breakdown"].to_csv(
        run_dir / "policy_path_cost_breakdown.csv", index=False
    )

    cost_comparison = _policy_cost_comparison(planner["path_cost_breakdown"])
    cost_comparison.to_csv(run_dir / "policy_cost_comparison.csv", index=False)

    rcap_points = [
        float(value) for value in resolved["elasticity_sweep"]["rcap_points"]
    ]
    frontier = _solve_frontier(annual, candidates, planner_kwargs, rcap_points)
    frontier.to_csv(run_dir / "elasticity_frontier_v32.csv", index=False)
    recommendations = _recommendation_matrix(
        frontier,
        planner["path_year_results"],
        cost_comparison,
        near_optimal_band=float(resolved["elasticity_sweep"]["near_optimal_band"]),
    )
    recommendations.to_csv(run_dir / "recommendation_matrix_v32_base.csv", index=False)

    chronology_parts: list[pd.DataFrame] = []
    for path_id in ("PATH_OPT_CLR_UNBOUNDED", "PATH_OPT_CLR_LE_2"):
        selected = _selected_candidate_ids(
            planner["path_action_results"], path_id, "QX-00005", 110
        )
        comparison = evaluator.chronology_comparison(selected, cos_phi=cos_phi)
        comparison.insert(0, "path_id", path_id)
        chronology_parts.append(comparison)
    chronology = pd.concat(chronology_parts, ignore_index=True)
    chronology.to_csv(run_dir / "qx00005_chronology_comparison.csv", index=False)

    actual_years = _actual_path_year_results(processed_root)
    actual_actions = _actual_path_actions(processed_root)
    actual_costs = _actual_path_cost_breakdown(processed_root)
    actual_years.to_csv(run_dir / "actual_path_year_results.csv", index=False)
    actual_actions.to_csv(run_dir / "actual_path_action_results.csv", index=False)
    actual_costs.to_csv(run_dir / "actual_path_cost_breakdown.csv", index=False)

    manifest = {
        "model_version": "3.2.0-candidate",
        "status": "baseline_formal_run_before_sensitivity",
        "base_contract_sha256": _sha256(base_contract_path),
        "resolved_contract_sha256": _sha256(resolved_contract_path),
        "processed_manifest_sha256": _sha256(processed_root / "manifest.json"),
        "cost_manifest": cost_manifest,
        "timeseries_formal_hourly_use_allowed": True,
        "planning_baseline_formula": "S_plan_0 = 2.0 * P_plus_2021",
        "planning_baseline_voltage_kv": resolved["planning_baseline"]["applies_to_voltage_kv"],
        "physical_asset_baseline_separate": True,
        "direct_policy_cost_comparison_allowed": True,
        "qx00005_110kv_time_method": "approved_8760_continuous_soc_primary_plus_daily_cyclic_reference",
        "other_regions_time_method": "three_nonprobabilistic_empirical_duration_scenarios",
        "rcap_frontier_points": rcap_points,
        "near_optimal_band": float(resolved["elasticity_sweep"]["near_optimal_band"]),
        "sensitivity_completed": False,
        "report_update_allowed": False,
    }
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest
