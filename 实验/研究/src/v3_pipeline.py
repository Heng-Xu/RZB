"""真实数据 v3 端到端流水线。"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.io_loader import adapt_real_2021_2025
from src.real_costs import annualized_eac_wanyuan, build_real_cost_library, storage_capex_wanyuan
from src.v3_outputs import build_v3_artifacts
from src.v3_planner import (
    PATH_OPT_STRICT,
    PATH_OPT_UNBOUNDED,
    optimize_path,
)
from src.v3_time_physics import V3TimePhysicsEvaluator
from src.v3_voltage_cases import combine_local_cases


class V3PipelineError(ValueError):
    """v3 端到端步骤或发布门禁不满足。"""


def _timeseries_gate(processed_root: Path) -> dict[str, Any]:
    manifest_path = processed_root / "manifest.json"
    if not manifest_path.is_file():
        return {"grade_a_ready": False, "formal_hourly_use_allowed": False}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return dict(manifest.get("timeseries_gate", {}))


def _annual_input(processed_root: Path) -> pd.DataFrame:
    reference = pd.read_csv(processed_root / "annual_reference.csv")
    decision = reference[reference["year"].isin([2022, 2023, 2024, 2025])].copy()
    decision = decision.rename(
        columns={
            "official_capacity_mva": "actual_capacity_anchor_mva",
            "official_positive_peak_mw": "positive_peak_mw",
        }
    )
    baseline = reference[reference["year"].eq(2021)][
        ["region_id", "voltage_kv", "official_capacity_mva"]
    ].rename(columns={"official_capacity_mva": "baseline_capacity_mva"})
    decision = decision.merge(
        baseline,
        on=["region_id", "voltage_kv"],
        how="left",
        validate="many_to_one",
    )
    if decision["baseline_capacity_mva"].isna().any():
        raise V3PipelineError("2021 common capacity baseline is incomplete")
    # Keep the factual annual capacity anchor for audit only.  The optimizer's
    # installed-capacity state starts from the 2021 baseline in every decision
    # year and changes only through selected counterfactual actions.
    decision["capacity_mva"] = decision["baseline_capacity_mva"]
    decision["reverse_peak_mw"] = 0.0
    decision["reverse_beta"] = 0.8
    return decision[
        [
            "year",
            "region_id",
            "voltage_kv",
            "capacity_mva",
            "baseline_capacity_mva",
            "actual_capacity_anchor_mva",
            "positive_peak_mw",
            "reverse_peak_mw",
            "reverse_beta",
        ]
    ].sort_values(["region_id", "voltage_kv", "year"], kind="stable")


def _actual_path_year_results(processed_root: Path) -> pd.DataFrame:
    """把官方年度总量锚点写成事实路径；不把它送入优化排名。"""
    reference = pd.read_csv(processed_root / "annual_reference.csv")
    rows: list[dict[str, Any]] = []
    for row in reference.sort_values(["region_id", "voltage_kv", "year"], kind="stable").itertuples(index=False):
        capacity = float(row.official_capacity_mva)
        peak = float(row.official_positive_peak_mw)
        rows.append(
            {
                "year": int(row.year),
                "region_id": str(row.region_id),
                "voltage_kv": int(row.voltage_kv),
                "path_id": "PATH_ACTUAL_2021_2025",
                "status": "fact",
                "reason": "official_annual_anchor_not_ranked",
                "complete_path_status": "fact",
                "complete_path_reason": "official_fact_path_not_ranked",
                "installed_capacity_mva": capacity,
                "storage_modules": 0,
                "storage_power_mw": 0.0,
                "p_plus_mw": peak,
                "p_minus_mw": float("nan"),
                "clr": capacity / peak if peak > 0 else float("inf"),
                "positive_capacity_gap_mw": "未识别",
                "reverse_hosting_gap_mw": "未识别",
                "annual_capex_wanyuan": "未识别",
                "annual_in_service_eac_wanyuan": "未识别",
                "cumulative_capex_wanyuan": "未识别",
                "cumulative_in_service_eac_wanyuan": "未识别",
            }
        )
    return pd.DataFrame(rows)


def _actual_path_actions(processed_root: Path) -> pd.DataFrame:
    """把设备级实际行动台账接入事实路径，未知成本保持为“未识别”。"""
    source = pd.read_csv(processed_root / "actual_asset_actions_2021_2025.csv")
    return source.rename(
        columns={
            "capacity_delta_mva": "delta_capacity_mva",
            "capex_wanyuan_2025": "capex_wanyuan",
            "eac_wanyuan_per_year": "eac_wanyuan_per_year",
        }
    ).assign(
        path_id="PATH_ACTUAL_2021_2025",
        candidate_id="",
        storage_modules_delta=0,
        cost_basis=lambda frame: frame["cost_closure_status"],
        source_ref=lambda frame: frame["source_ref"],
    )[
        [
            "path_id",
            "year",
            "region_id",
            "voltage_kv",
            "action_id",
            "candidate_id",
            "action_type",
            "delta_capacity_mva",
            "storage_modules_delta",
            "capex_wanyuan",
            "eac_wanyuan_per_year",
            "cost_basis",
            "source_ref",
            "action_status",
            "cost_closure_status",
        ]
    ].sort_values(["region_id", "voltage_kv", "year", "action_id"], kind="stable")


def _actual_path_cost_breakdown(processed_root: Path) -> pd.DataFrame:
    """为事实路径保留成本未闭合的明确行，不参与优化路径比较。"""
    actions = pd.read_csv(processed_root / "actual_asset_actions_2021_2025.csv")
    grouped = actions.groupby(["region_id", "voltage_kv"], as_index=False).agg(
        selected_action_count=("action_id", "nunique"),
        cost_closure_status=("cost_closure_status", lambda values: ";".join(sorted(set(values.astype(str))))),
    )
    grouped.insert(0, "path_id", "PATH_ACTUAL_2021_2025")
    grouped.insert(3, "status", "not_ranked_fact")
    grouped.insert(4, "cumulative_in_service_eac_wanyuan", "未识别")
    return grouped


def _retirement_candidates(processed_root: Path, cost_library: pd.DataFrame) -> pd.DataFrame:
    """从现有离散主变设备生成可追溯整台退役组合候选。

    每个县区/电压的 ``candidate_group`` 是互斥的 N 台退役选项；每个 N 的
    transformer_uid 列表来自年度运行白名单，因而不是连续虚构容量。没有
    同电压成本范围的 35 kV 退役候选留在问题台账中，不进入可排名解。
    """
    master = pd.read_csv(processed_root / "transformer_master.csv")
    whitelist = pd.read_csv(processed_root / "annual_asset_whitelist.csv")
    operating = whitelist[
        whitelist["year"].eq(2025)
        & whitelist["asset_scope_id"].eq("operating_2025")
        & whitelist["in_annual_operating_whitelist"].astype(str).str.lower().eq("true")
    ][["transformer_uid"]]
    master = master.merge(operating, on="transformer_uid", how="inner")
    rows: list[dict[str, Any]] = []
    for (region, voltage), group in master.groupby(["region_id", "voltage_kv"], sort=True):
        if int(voltage) != 110:
            continue
        group = group.sort_values(["capacity_mva", "transformer_uid"], ascending=[False, True], kind="stable")
        costs: list[tuple[float, float, str]] = []
        for row in group.itertuples(index=False):
            pool = cost_library[cost_library["voltage_kv"].eq(int(voltage))].copy()
            if pool.empty:
                continue
            pool["distance"] = (pool["new_capacity_mva"] - float(row.capacity_mva)).abs()
            match = pool.sort_values(["distance", "new_capacity_mva"], kind="stable").iloc[0]
            capex = match.get("capex_center_wanyuan")
            eac = match.get("eac_center_wanyuan_per_year")
            basis = "center"
            if pd.isna(capex) or pd.isna(eac):
                capex = match.get("capex_high_wanyuan")
                eac = match.get("eac_high_wanyuan_per_year")
                basis = "range_high_for_feasibility"
            if pd.isna(capex) or pd.isna(eac):
                continue
            costs.append((float(capex), float(eac), basis))
        if not costs:
            continue
        selected_uids: list[str] = []
        delta = 0.0
        capex_total = 0.0
        eac_total = 0.0
        for index, (row, cost) in enumerate(zip(group.itertuples(index=False), costs, strict=True), start=1):
            selected_uids.append(str(row.transformer_uid))
            delta -= float(row.capacity_mva)
            capex_total += cost[0]
            eac_total += cost[1]
            rows.append(
                {
                    "candidate_id": f"RETIRE-{region}-{int(voltage)}-{index:03d}",
                    "candidate_group": f"RETIREMENT_POOL|{region}|{int(voltage)}",
                    "region_id": region,
                    "voltage_kv": int(voltage),
                    "candidate_type": "retirement",
                    "station_id": "MULTI_STATION_RETIREMENT_POOL",
                    "transformer_uids": json.dumps(selected_uids, ensure_ascii=False),
                    "available_year": 2022,
                    "delta_capacity_mva": delta,
                    "capex_base_wanyuan": capex_total,
                    "eac_base_wanyuan_per_year": eac_total,
                    "cost_status": "cost_center_and_range_available" if cost[2] == "center" else "cost_range_high_used_no_point_estimate",
                    "source_ref": "SRC02+SRC03+SRC10:" + ";".join(selected_uids),
                    "source_version": "电网建模数据_Agent整合版_V1.2",
                    "transformation": "enumerate mutually exclusive whole-transformer retirement combinations from annual operating whitelist; symmetric same-voltage cost",
                    "scenario_id": "real_2021_2025",
                    "quality_flag": "discrete_retirement_candidate" if cost[2] == "center" else "discrete_retirement_cost_range",
                    "approval_status": "counterfactual_candidate_available_from_2022_model_assumption",
                }
            )
    return pd.DataFrame(rows)


def _physical_gap_matrix(processed_root: Path) -> pd.DataFrame:
    master = pd.read_csv(processed_root / "transformer_master.csv")
    static = pd.read_csv(processed_root / "transformer_static_load.csv")
    whitelist = pd.read_csv(processed_root / "annual_asset_whitelist.csv")
    operating = whitelist[
        whitelist["year"].eq(2025)
        & whitelist["asset_scope_id"].eq("operating_2025")
        & whitelist["in_annual_operating_whitelist"].astype(str).str.lower().eq("true")
    ][["transformer_uid"]]
    data = master.merge(operating, on="transformer_uid", how="inner").merge(
        static[["transformer_uid", "annual_max_net_load_mw", "annual_min_net_load_mw"]],
        on="transformer_uid",
        how="left",
        validate="one_to_one",
    )
    data["positive_gap"] = (data["annual_max_net_load_mw"].clip(lower=0) - data["capacity_mva"] * 0.95).clip(lower=0)
    data["reverse_gap"] = ((-data["annual_min_net_load_mw"]).clip(lower=0) - data["capacity_mva"] * 0.95 * 0.8).clip(lower=0)
    result = data.groupby(["region_id", "voltage_kv"], as_index=False).agg(
        positive_capacity_gap_mw=("positive_gap", "sum"),
        reverse_hosting_gap_mw=("reverse_gap", "sum"),
        positive_gap_device_count=("positive_gap", lambda values: int((values > 1e-9).sum())),
        reverse_gap_device_count=("reverse_gap", lambda values: int((values > 1e-9).sum())),
    )
    result["measure_trigger_constraint"] = result.apply(
        lambda row: ";".join(
            item
            for item, condition in (
                ("positive_capacity_gap", row["positive_capacity_gap_mw"] > 1e-9),
                ("reverse_hosting_gap", row["reverse_hosting_gap_mw"] > 1e-9),
            )
            if condition
        ) or "none",
        axis=1,
    )
    return result


def _matrix(
    processed_root: Path,
    annual: pd.DataFrame,
    planner: dict[str, pd.DataFrame],
    voltage: int,
    sensitivity_results: dict[float, pd.DataFrame] | None = None,
    synchronized_base_peaks: dict[tuple[str, int], tuple[float, float]] | None = None,
    elasticity_frontier: pd.DataFrame | None = None,
) -> pd.DataFrame:
    reference = pd.read_csv(processed_root / "annual_reference.csv")
    reference_2025 = reference[reference["year"].eq(2025) & reference["voltage_kv"].eq(voltage)].copy()
    gaps = _physical_gap_matrix(processed_root)
    gaps = gaps[gaps["voltage_kv"].eq(voltage)]
    mapping_gate = _timeseries_gate(processed_root)
    mapping_quality_flag = (
        "mapping_approved_with_scope_exceptions_or_empirical_duration_transfer"
        if bool(mapping_gate.get("formal_hourly_use_allowed"))
        else "mapping_pending_or_empirical_duration_transfer"
    )
    years = planner["path_year_results"]
    costs = planner["path_cost_breakdown"]
    actions = planner["path_action_results"]
    rows: list[dict[str, Any]] = []
    for row in reference_2025.sort_values("region_id").itertuples(index=False):
        region = str(row.region_id)
        path_2025 = years[(years["year"].eq(2025)) & (years["region_id"].astype(str).eq(region)) & (years["voltage_kv"].eq(voltage))]
        unbounded = path_2025[path_2025["path_id"].eq(PATH_OPT_UNBOUNDED)]
        strict = path_2025[path_2025["path_id"].eq(PATH_OPT_STRICT)]
        unbounded_cost = costs[(costs["region_id"].astype(str).eq(region)) & costs["voltage_kv"].eq(voltage) & costs["path_id"].eq(PATH_OPT_UNBOUNDED)]
        strict_cost = costs[(costs["region_id"].astype(str).eq(region)) & costs["voltage_kv"].eq(voltage) & costs["path_id"].eq(PATH_OPT_STRICT)]
        unbounded_value = float(unbounded_cost.iloc[0]["cumulative_in_service_eac_wanyuan"]) if not unbounded_cost.empty and math.isfinite(float(unbounded_cost.iloc[0]["cumulative_in_service_eac_wanyuan"])) else "不可行"
        strict_value = float(strict_cost.iloc[0]["cumulative_in_service_eac_wanyuan"]) if not strict_cost.empty and math.isfinite(float(strict_cost.iloc[0]["cumulative_in_service_eac_wanyuan"])) else "不可行"
        # 3.1.0：严格路径起点为归一约定状态，与不限制路径起点不同，
        # 跨口径 EAC 增量比较废止（原 A008）；字段改为口径说明。
        incremental = (
            "跨口径不可比（严格路径起点为容载比2.0归一约定状态，见manifest path_comparison_note）"
            if isinstance(strict_value, float)
            else strict_value
        )
        chosen_actions = actions[(actions["path_id"].eq(PATH_OPT_UNBOUNDED)) & actions["region_id"].astype(str).eq(region) & actions["voltage_kv"].eq(voltage)] if not actions.empty else pd.DataFrame()
        measure = "无"
        if not chosen_actions.empty:
            measure = ";".join(sorted(set(chosen_actions["action_type"].astype(str))))
        gap = gaps[gaps["region_id"].astype(str).eq(region)]
        gap_row = gap.iloc[0] if not gap.empty else pd.Series(dtype=object)
        clr_unbounded = float(unbounded.iloc[0]["clr"]) if not unbounded.empty and unbounded.iloc[0].get("status") == "feasible" else float("nan")
        clr_strict = float(strict.iloc[0]["clr"]) if not strict.empty and strict.iloc[0].get("status") == "feasible" else float("nan")
        sensitivity_clrs = [clr_unbounded]
        for sensitivity_frame in (sensitivity_results or {}).values():
            sensitivity_row = sensitivity_frame[
                sensitivity_frame["year"].eq(2025)
                & sensitivity_frame["region_id"].astype(str).eq(region)
                & sensitivity_frame["voltage_kv"].eq(voltage)
            ]
            if not sensitivity_row.empty and sensitivity_row.iloc[0].get("status") == "feasible":
                value = float(sensitivity_row.iloc[0]["clr"])
                if math.isfinite(value):
                    sensitivity_clrs.append(value)
        finite_sensitivity_clrs = [value for value in sensitivity_clrs if math.isfinite(value)]
        recommendation_available = math.isfinite(clr_unbounded) and bool(finite_sensitivity_clrs)
        interval = (
            f"{min(finite_sensitivity_clrs):.3f}–{max(finite_sensitivity_clrs):.3f}"
            if recommendation_available
            else "不可行"
        )
        recommended_center: float | str = clr_unbounded if recommendation_available else "未形成推荐"
        interval_sample_count = len(finite_sensitivity_clrs) if recommendation_available else 0
        interval_method = (
            "不限制容载比成本最小可行结果+cos_phi敏感性（0.90、0.95、1.00）"
            if recommendation_available
            else "未形成推荐"
        )
        # 3.1.0：110 kV 层优先采用弹性前沿近优带区间，并与敏感性区间取交。
        frontier_interval = None
        if voltage == 110 and elasticity_frontier is not None and not elasticity_frontier.empty:
            from src.v3_outputs import recommended_clr_interval

            frontier_result = recommended_clr_interval(
                elasticity_frontier, region_id=region
            )
            if frontier_result.get("interval_low") is not None:
                lo, hi = frontier_result["interval_low"], frontier_result["interval_high"]
                frontier_interval = (lo, hi)
                interval = f"{lo:.2f}–{hi:.2f}"
                interval_sample_count = len(frontier_result.get("near_optimal_rcap_points", []))
                interval_method = (
                    "弹性扫描前沿近优带（Rcap=1.5~3.0 步长0.1，最低成本5%内）"
                    + ("；措施翻转，仅给区间" if frontier_result["interval_only"] else "")
                )
                if recommendation_available:
                    sens_lo, sens_hi = min(finite_sensitivity_clrs), max(finite_sensitivity_clrs)
                    cross_lo, cross_hi = max(lo, sens_lo), min(hi, sens_hi)
                    if cross_lo <= cross_hi:
                        interval = f"{cross_lo:.2f}–{cross_hi:.2f}"
                        interval_method += "∩cos_phi敏感性"
                    else:
                        interval_method += "（与敏感性区间无交集，保留前沿区间）"
                recommended_center = (
                    frontier_result["point_estimate"]
                    if frontier_result.get("point_estimate") is not None
                    else "未形成唯一中心值（给区间）"
                )
        rows.append(
            {
                "region_id": region,
                "voltage_kv": voltage,
                "evidence_grade": (
                    "EVIDENCE_A"
                    if region == "QX-00005"
                    and voltage == 110
                    and bool(mapping_gate.get("formal_hourly_use_allowed"))
                    else "EVIDENCE_C"
                    if region == "QX-00005"
                    else "EVIDENCE_B"
                ),
                "asset_scope_id": "operating_2025",
                "recommended_clr_interval": interval,
                "recommended_clr_center": recommended_center,
                "recommended_clr_interval_effective_samples": interval_sample_count,
                "recommended_clr_interval_method": interval_method,
                "capacity_base_mva": float(row.official_capacity_mva),
                "positive_peak_base_mw": float(row.official_positive_peak_mw),
                "reverse_peak_base_mw": (
                    float(synchronized_base_peaks[(region, voltage)][1])
                    if synchronized_base_peaks
                    and (region, voltage) in synchronized_base_peaks
                    else "未形成同步反向峰值"
                ),
                "PATH_ACTUAL_2021_2025_clr_2025": float(row.official_capacity_mva) / float(row.official_positive_peak_mw),
                "PATH_OPT_CLR_UNBOUNDED_clr_2025": clr_unbounded,
                "PATH_OPT_CLR_LE_2_clr_2025": clr_strict,
                "PATH_ACTUAL_2021_2025_cumulative_eac": "未识别",
                "PATH_OPT_CLR_UNBOUNDED_cumulative_eac": unbounded_value,
                "PATH_OPT_CLR_LE_2_cumulative_eac": strict_value,
                "strict_path_incremental_cost": incremental,
                "positive_capacity_gap_mw": float(gap_row.get("positive_capacity_gap_mw", float("nan"))),
                "reverse_hosting_gap_mw": float(gap_row.get("reverse_hosting_gap_mw", float("nan"))),
                "positive_gap_device_count": int(gap_row.get("positive_gap_device_count", 0)),
                "reverse_gap_device_count": int(gap_row.get("reverse_gap_device_count", 0)),
                "measure_trigger_constraint": str(gap_row.get("measure_trigger_constraint", "data_not_identified")),
                "recommended_measure": measure,
                "source_ref": "SRC08+annual_asset_whitelist+v3_path_results",
                "source_version": "电网建模数据_Agent整合版_V1.2",
                "transformation": "2025 same-voltage official anchor plus path-specific optimized result; actual cost remains unidentified until gross actions close",
                "scenario_id": "real_2021_2025",
                "quality_flag": mapping_quality_flag,
                "source_sha256": str(row.source_sha256),
            }
        )
    return pd.DataFrame(rows)


def _network_screen(processed_root: Path) -> pd.DataFrame:
    lines = pd.read_csv(processed_root / "network_lines_110kv.csv")
    result = lines.copy()
    result["screen_type"] = "internal_capacity_network_screen"
    result["n_minus_1_method"] = "capacity_network_contingency_screen"
    result["precise_ac_or_dc_claim"] = False
    result["visible_in_client_matrix"] = False
    result["screen_status"] = "screen_only_without_impedance"
    return result[
        [
            "region_id",
            "voltage_kv",
            "line_id",
            "from_node",
            "to_node",
            "current_limit_a",
            "max_loading_pct",
            "screen_type",
            "n_minus_1_method",
            "precise_ac_or_dc_claim",
            "visible_in_client_matrix",
            "screen_status",
        ]
    ]


def _apply_strict_baseline(annual: pd.DataFrame, processed_root: Path) -> pd.DataFrame:
    """严格路径起点约定（2026-08-24 定版口径，记账式归一）。

    ``S0 = min(S_2021, 2 × min(P_2021, min决策年峰))`` 仅作为**报告口径**：
    写入新列 ``reported_baseline_capacity_mva``，用于严格路径的 CLR 计算
    与逐年 ``R<=2`` 检查；物理容量 ``baseline_capacity_mva`` 保持 2021 实际
    状态不动——设备级缺口、储能定容和网络筛查仍按真实资产评估。
    峰值保持 SRC08 官方锚点原值；起点调整不计入决策期成本。
    """
    reference = pd.read_csv(processed_root / "annual_reference.csv")
    base_peak = (
        reference[reference["year"].eq(2021)]
        .set_index(["region_id", "voltage_kv"])["official_positive_peak_mw"]
    )
    key = ["region_id", "voltage_kv"]
    decision_min = annual.groupby(key)["positive_peak_mw"].min().rename("decision_min_peak")
    s2021 = annual.groupby(key)["baseline_capacity_mva"].first().rename("s2021")
    norm = pd.concat([base_peak.rename("p2021"), decision_min, s2021], axis=1).reset_index()
    if norm[["p2021", "decision_min_peak", "s2021"]].isna().any().any():
        raise V3PipelineError("strict baseline normalization missing reference rows")
    safe_peak = norm[["p2021", "decision_min_peak"]].min(axis=1)
    norm["reported_baseline_capacity_mva"] = pd.concat(
        [norm["s2021"], 2.0 * safe_peak], axis=1
    ).min(axis=1)
    out = annual.merge(
        norm[key + ["reported_baseline_capacity_mva"]], on=key, how="left", validate="many_to_one"
    )
    if out["reported_baseline_capacity_mva"].isna().any():
        raise V3PipelineError("strict baseline normalization incomplete for all region-voltage groups")
    return out


def _run_formal_paths(
    annual: pd.DataFrame,
    strict_annual: pd.DataFrame,
    candidates: pd.DataFrame,
    planner_kwargs: dict[str, Any],
) -> dict[str, pd.DataFrame]:
    """分别求解两条优化路径并合并为统一输出结构。

    不限制路径使用实际 2021 基准；严格路径使用归一后的约定起点。
    110 kV 正式层保留逐年 ``R<=2.0`` 安全网；35 kV 辅助层按 AGENTS §5
    仅作辅助分析、不做唯一最优声明，故不施加逐年上界（``clr_limit=inf``），
    避免年度峰值剧烈回落造成的结构性不可行。
    """
    unbounded = optimize_path(annual, candidates, path_id=PATH_OPT_UNBOUNDED, **planner_kwargs)
    strict_parts = []
    for voltage_kv, limit in ((110, 2.0), (35, math.inf)):
        sub = strict_annual[strict_annual["voltage_kv"].eq(voltage_kv)]
        if sub.empty:
            continue
        strict_parts.append(
            optimize_path(sub, candidates, path_id=PATH_OPT_STRICT, clr_limit=limit, **planner_kwargs)
        )
    merged: dict[str, pd.DataFrame] = {}
    for name in ("path_year_results", "path_action_results", "path_cost_breakdown"):
        merged[name] = pd.concat(
            [unbounded[name], *(part[name] for part in strict_parts)],
            ignore_index=True,
            sort=False,
        )
    return merged


def _validate_formal_paths_present(cost_breakdown: pd.DataFrame) -> bool:
    """校验每个片区/电压两条优化路径齐备。

    严格路径起点经归一约定后与不限制路径起点不同，两路径 EAC 表征各自
    口径下的最优演进成本，因此不再做跨路径 EAC 大小比较（原 A008）。
    """
    required = {
        "path_id",
        "region_id",
        "voltage_kv",
        "cumulative_in_service_eac_wanyuan",
    }
    if not required <= set(cost_breakdown.columns):
        raise V3PipelineError(f"cost breakdown missing {sorted(required - set(cost_breakdown.columns))}")
    for (region_id, voltage_kv), group in cost_breakdown.groupby(["region_id", "voltage_kv"], sort=True):
        present = set(group["path_id"])
        missing = {PATH_OPT_UNBOUNDED, PATH_OPT_STRICT} - present
        if missing:
            raise V3PipelineError(f"formal optimization paths missing for {region_id}|{voltage_kv}: {sorted(missing)}")
    return True


def _solve_sweep_point(
    rcap: float,
    sub: pd.DataFrame,
    candidates: pd.DataFrame,
    baselines: pd.Series,
    planner_kwargs: dict[str, Any],
) -> list[dict[str, Any]]:
    """求解单个 Rcap 点并汇总各片区 2025 年终态结果。"""
    label = "unbounded" if math.isinf(rcap) else rcap
    result = optimize_path(
        sub,
        candidates,
        path_id=PATH_OPT_STRICT,
        clr_limit=rcap,
        **planner_kwargs,
    )
    years = result["path_year_results"]
    point_rows: list[dict[str, Any]] = []
    for region_id, group in years.groupby("region_id", sort=True):
        # 可行性以 2025 年终态为准；仅中间年可行的"年度前缀"不算可行，
        # 避免把 2024 累计成本误标为完整路径结果。
        final_row = group[group["year"].eq(2025) & group["status"].eq("feasible")]
        if final_row.empty:
            reason_rows = group[group["status"].ne("feasible")]
            point_rows.append({
                "rcap": label,
                "region_id": region_id,
                "cumulative_in_service_eac_wanyuan": None,
                "clr_2025": None,
                "storage_modules": None,
                "expansion_mva": None,
                "feasible": False,
                "note": str(reason_rows.iloc[-1].get("reason", "infeasible")) if len(reason_rows) else "infeasible_2025",
            })
            continue
        final = final_row.iloc[0]
        expansion = float(final["installed_capacity_mva"]) - float(baselines[region_id])
        point_rows.append({
            "rcap": label,
            "region_id": region_id,
            "cumulative_in_service_eac_wanyuan": float(final["cumulative_in_service_eac_wanyuan"]),
            "clr_2025": float(final["clr"]),
            "storage_modules": int(final["storage_modules"]),
            "expansion_mva": expansion,
            "feasible": True,
            "note": "",
        })
    return point_rows


def _run_elasticity_sweep(
    strict_annual: pd.DataFrame,
    candidates: pd.DataFrame,
    planner_kwargs: dict[str, Any],
    contract: dict[str, Any],
) -> pd.DataFrame | None:
    """第三类实验：容载比上限弹性扫描（继承 2026-08-09 冻结方案，3.1.0 恢复）。

    在 110 kV 正式层以同一归一起点逐点求最优演进成本，产出
    「Rcap—累计在役EAC」前沿；无上限点即不限制路径口径。

    注：曾尝试多进程并行各 Rcap 点，但时序回放评估器在 fork 子进程中
    状态失效，导致回放类片区紧约束点被误判不可行（2026-08-25 第六轮
    端到端发现），已回退串行。正确性优先；如需加速应先将评估器改造为
    可跨进程序列化的无状态实现。
    """
    sweep_cfg = contract.get("elasticity_sweep") or {}
    points = [float(value) for value in sweep_cfg.get("rcap_points", [])]
    if not points:
        return None
    if sweep_cfg.get("include_unbounded_point", True):
        points.append(math.inf)
    sub = strict_annual[strict_annual["voltage_kv"].eq(110)]
    if sub.empty:
        return None
    baselines = sub.groupby("region_id")["baseline_capacity_mva"].first()
    rows: list[dict[str, Any]] = []
    for rcap in points:
        rows.extend(_solve_sweep_point(rcap, sub, candidates, baselines, planner_kwargs))
    return pd.DataFrame(rows)


def run_v3_pipeline(
    project_root: Path,
    processed_root: Path,
    run_dir: Path,
    contract_path: Path,
    *,
    existing_tie_case_options: Path | None = None,
    new_tie_line_case_options: Path | None = None,
) -> dict[str, Any]:
    project_root = Path(project_root).resolve()
    processed_root = Path(processed_root).resolve()
    run_dir = Path(run_dir).resolve()
    contract_path = Path(contract_path).resolve()
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    if contract["contract"]["version"] != "3.1.0":
        raise V3PipelineError("v3 pipeline requires model contract 3.1.0")
    if not (processed_root / "manifest.json").is_file():
        adapt_real_2021_2025(
            project_root / "data/tuomin/电网建模数据_Agent整合版_V1.2",
            processed_root,
            contract_path,
        )
    run_dir.mkdir(parents=True, exist_ok=True)
    cost_manifest = build_real_cost_library(processed_root, run_dir / "cost_library", contract_path)
    annual = _annual_input(processed_root)
    physical_gaps = _physical_gap_matrix(processed_root)
    annual = annual.merge(physical_gaps, on=["region_id", "voltage_kv"], how="left", validate="many_to_one")
    annual["forward_requirement_mw"] = annual["positive_peak_mw"]
    annual["reverse_requirement_mw"] = annual["capacity_mva"] * 0.95 * annual["reverse_beta"]
    current_year = annual["year"].eq(2025)
    annual.loc[current_year, "forward_requirement_mw"] += annual.loc[current_year, "positive_capacity_gap_mw"].fillna(0.0)
    annual.loc[current_year, "reverse_requirement_mw"] += annual.loc[current_year, "reverse_hosting_gap_mw"].fillna(0.0)
    annual["measure_trigger_required"] = (
        annual["positive_capacity_gap_mw"].fillna(0.0).gt(1e-9)
        | annual["reverse_hosting_gap_mw"].fillna(0.0).gt(1e-9)
    ) & current_year
    annual = annual.drop(columns=["positive_capacity_gap_mw", "reverse_hosting_gap_mw", "positive_gap_device_count", "reverse_gap_device_count", "measure_trigger_constraint"])
    cost_library = pd.read_csv(run_dir / "cost_library" / "expansion_cost_library.csv")
    if "available_year" not in cost_library.columns:
        cost_library["available_year"] = 2022
        cost_library["quality_flag"] = (
            cost_library["quality_flag"].astype(str)
            + ";counterfactual_candidate_available_from_2022_model_assumption"
        )
    retirements = _retirement_candidates(processed_root, cost_library)
    candidates = pd.concat([cost_library, retirements], ignore_index=True, sort=False)
    time_physics = V3TimePhysicsEvaluator(
        processed_root,
        run_dir / "time_physics",
        candidates,
        contract_path,
    )

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

    planner_kwargs = {
        "cos_phi": float(contract["technical_parameters"]["cos_phi"]["baseline"]),
        "module_power_mw": float(contract["storage"]["module"]["power_mw"]),
        "storage_capex_wanyuan_for_modules": storage_action_capex,
        "storage_eac_wanyuan_for_modules": storage_action_eac,
        "state_physics_evaluator": time_physics.evaluator(
            float(contract["technical_parameters"]["cos_phi"]["baseline"])
        ),
    }
    strict_annual = _apply_strict_baseline(annual, processed_root)
    planner = _run_formal_paths(
        annual,
        strict_annual,
        candidates,
        planner_kwargs,
    )
    _validate_formal_paths_present(planner["path_cost_breakdown"])
    elasticity_frontier = _run_elasticity_sweep(
        strict_annual,
        candidates,
        planner_kwargs,
        contract,
    )
    if elasticity_frontier is not None and not elasticity_frontier.empty:
        elasticity_frontier.to_csv(
            run_dir / "elasticity_frontier.csv",
            index=False,
            encoding="utf-8-sig",
        )
    actual_years = _actual_path_year_results(processed_root)
    actual_actions = _actual_path_actions(processed_root)
    actual_costs = _actual_path_cost_breakdown(processed_root)
    output_years = pd.concat(
        [actual_years, planner["path_year_results"]],
        ignore_index=True,
        sort=False,
    )
    output_actions = pd.concat(
        [actual_actions, planner["path_action_results"]],
        ignore_index=True,
        sort=False,
    )
    output_costs = pd.concat(
        [actual_costs, planner["path_cost_breakdown"]],
        ignore_index=True,
        sort=False,
    )
    sensitivity_results = {
        cos_phi: optimize_path(
            annual,
            candidates,
            path_id=PATH_OPT_UNBOUNDED,
            **{
                **planner_kwargs,
                "cos_phi": cos_phi,
                "state_physics_evaluator": time_physics.evaluator(cos_phi),
            },
        )["path_year_results"]
        for cos_phi in (0.90, 1.00)
    }
    physics_artifacts = time_physics.write_selected_artifacts(
        planner,
        run_dir,
        cos_phi=float(contract["technical_parameters"]["cos_phi"]["baseline"]),
    )
    matrix_110 = _matrix(
        processed_root,
        annual,
        planner,
        110,
        sensitivity_results,
        time_physics.synchronized_base_peaks,
        elasticity_frontier=elasticity_frontier,
    )
    matrix_35 = _matrix(
        processed_root,
        annual,
        planner,
        35,
        sensitivity_results,
        time_physics.synchronized_base_peaks,
        elasticity_frontier=None,
    )
    timeseries_gate = _timeseries_gate(processed_root)
    problem_lines = [
        (
            "- 跨年时序映射已由项目负责人审批：56 列批准；BDZ-00056 两列因仅为 2025 年末新增而排除出 "
            "2025 年 QX-00005 110 kV 运行白名单，正式门禁按 40 台运行设备通过。"
            if bool(timeseries_gate.get("formal_hourly_use_allowed"))
            else "- 跨年时序映射当前为项目负责人审批前状态，正式 Grade A 门禁保持关闭。"
        ),
        "- 2024 三个异常值已在 `data_quality_issues.csv` 中保留原值并隔离。",
        "- 非 QX-00005 县区使用静态年度锚点和经验时长转移，证据等级不高于 EVIDENCE_B。",
        "- 两条反事实路径容量严格按 2021 官方共同基准加路径自身累计离散动作传播；2022—2025 实际容量变化只属于事实路径，不免费带入优化。",
        "- 2025 年优化终态已接入站级储能站址、充放电方向和日循环 SOC 门禁；QX-00005 110 kV 使用官方正峰校准后的 8760 点同步回放。",
        "- 2021—2024 逐站设备资产范围未闭合，不冒充正式站级历史 8760 约束；中间年负荷使用官方同步峰值锚点，2025 站级设备范围只作终端物理筛查。",
        "- 扩容/退役候选缺少源数据最早可用年，反事实路径暂按 2022 年可用的模型假设计算，不冒充历史实际项目时序。",
        "- 实际路径设备级毛动作成本尚未闭合，正式成本写为“未识别”，没有写 0。",
    ]
    if existing_tie_case_options or new_tie_line_case_options:
        problem_lines.append("- 局部 10 kV 案例接口已接收为独立外部输入；未获显式兼容审批时不并入主体优化。")
    manifest = build_v3_artifacts(
        run_dir,
        matrix_110,
        matrix_35,
        output_years,
        output_actions,
        output_costs,
        contract_path,
        problem_log="\n".join(problem_lines),
        network_check=_network_screen(processed_root),
    )
    manifest.update(
        {
            "processed_manifest_sha256": _sha256(processed_root / "manifest.json"),
            "cost_manifest": cost_manifest,
            "path_cost_inclusion_validated": False,
            "elasticity_sweep_completed": bool(elasticity_frontier is not None and not elasticity_frontier.empty),
            "elasticity_frontier_points": (int(elasticity_frontier["rcap"].nunique()) if elasticity_frontier is not None else 0),
            "path_comparison_note": (
                "严格路径起点为初始基准年容载比 2.0 的归一约定状态（S0=min(S2021, 2×min(P2021, min决策年峰))，"
                "仅容量侧记账、不计成本，峰值保持官方锚点），与不限制路径（2021 实际基准）起点不同；两路径 EAC "
                "表征各自口径下的最优演进成本，不做跨口径增量比较。110 kV 正式层保留逐年 R≤2.0 安全网；"
                "35 kV 辅助层按 AGENTS §5 仅作辅助分析、不施加逐年上界。"
            ),
            "timeseries_grade_a_ready": bool(timeseries_gate.get("grade_a_ready")),
            "timeseries_formal_hourly_use_allowed": bool(timeseries_gate.get("formal_hourly_use_allowed")),
            "timeseries_gate": timeseries_gate,
            "strict_path_feasible_110kv_rows": int(matrix_110["PATH_OPT_CLR_LE_2_clr_2025"].notna().sum()),
            "strict_path_feasible_35kv_rows": int(matrix_35["PATH_OPT_CLR_LE_2_clr_2025"].notna().sum()),
            "sensitivity_cos_phi": [0.90, 0.95, 1.00],
            "time_physics_hard_gate_2025": True,
            "time_physics_qx00005_110kv_method": "approved_2025_8760_station_playback_scaled_to_official_positive_peak",
            "time_physics_other_regions_method": "three_nonprobabilistic_empirical_duration_scenarios",
            "time_physics_scenario_manifest": time_physics.scenario_manifest,
            "time_physics_artifacts": physics_artifacts,
        }
    )
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def _sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
