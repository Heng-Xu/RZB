"""把真实 C0/A/B 求解结果整理为 110 kV 正式矩阵和 35 kV 辅助矩阵。"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml


MATRIX_VERSION = "1.1.0"
LINEAGE_FIELDS = (
    "source_ref",
    "source_version",
    "transformation",
    "scenario_id",
    "quality_flag",
    "source_sha256",
)


class RealMatrixError(ValueError):
    """矩阵输入、字段或发布门禁不满足。"""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _combined_hash(paths: list[Path]) -> str:
    payload = {path.name: _sha256(path) for path in sorted(paths, key=lambda item: item.name)}
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def _read(root: Path, filename: str, required: set[str]) -> pd.DataFrame:
    path = root / filename
    if not path.is_file():
        raise RealMatrixError(f"required matrix input missing: {path}")
    frame = pd.read_csv(path)
    missing = required - set(frame.columns)
    if missing:
        raise RealMatrixError(f"{filename}: missing columns {sorted(missing)}")
    return frame


def _parent_mapping(master: pd.DataFrame, source_hash: str, source_version: str) -> pd.DataFrame:
    local_110 = {
        region: set(group["station_id"].astype(str))
        for region, group in master[master["voltage_kv"].eq(110)].groupby("region_id")
    }
    rows: list[dict[str, Any]] = []
    for (region, station_id), group in master[master["voltage_kv"].eq(35)].groupby(
        ["region_id", "station_id"], sort=True
    ):
        parent_ids = sorted(set(group["parent_supply_id"].dropna().astype(str)))
        ordered = group.sort_values("equipment_source_row", kind="stable")
        primary_values = ordered["parent_supply_id"].dropna().astype(str)
        if not parent_ids:
            parent_id = None
            scope = "parent_missing"
            status = "incomplete"
        else:
            # SRC03 按主变逐行填写上级；冻结合同中的 4+4 是站级主供电
            # 口径，取 SRC03 站首行（equipment_source_row 最小）作为 primary，同时保留全部
            # 上级 ID，混合供电对象不得据此做跨层联合枚举。
            parent_id = str(primary_values.iloc[0])
            scope = (
                "in_scope_110kv"
                if parent_id in local_110.get(str(region), set())
                else "external_upstream"
            )
            status = (
                "complete_primary_parent_mixed_unit_context"
                if len(parent_ids) > 1
                else "complete_anonymized_parent_id"
            )
        rows.append(
            {
                "region_id": str(region),
                "voltage_kv": 35,
                "station_id": str(station_id),
                "parent_supply_id": parent_id,
                "all_parent_supply_ids": ";".join(parent_ids) if parent_ids else None,
                "mixed_unit_parent_supply": len(parent_ids) > 1,
                "parent_scope": scope,
                "parent_mapping_status": status,
                "cross_layer_enumeration_status": (
                    "eligible_but_not_enumerated_without_synchronous_transfer_and_35kv_discrete_candidates"
                    if scope == "in_scope_110kv" and len(parent_ids) == 1
                    else "mixed_unit_parent_not_eligible_for_joint_enumeration"
                    if len(parent_ids) > 1
                    else "outside_in_scope_110kv_joint_enumeration"
                ),
                "cross_layer_cost_aggregated": False,
                "source_ref": "transformer_master.csv:parent_supply_id",
                "source_version": source_version,
                "transformation": "classify anonymized 35-kV parent against same-region in-scope 110-kV station IDs",
                "scenario_id": "real_2025_cross_voltage_mapping",
                "quality_flag": (
                    "primary_parent_contract_context_secondary_parent_preserved"
                    if len(parent_ids) > 1
                    else "mapping_complete_no_cost_propagation"
                    if status.startswith("complete")
                    else "mapping_gap"
                ),
                "source_sha256": source_hash,
            }
        )
    return pd.DataFrame(rows)


def _scheme_action(solution: pd.Series) -> str:
    if solution["status"] != "feasible":
        return f"infeasible:{solution['status_reason']}"
    try:
        ids = json.loads(str(solution["selected_candidate_ids"]))
    except json.JSONDecodeError:
        ids = []
    return ";".join(ids) if ids else "none"


def _solution_action_mode(solution: pd.Series) -> str:
    """返回所选离散解的真实措施类型，而不是默认写成联合措施。"""
    declared = solution.get("action_mode")
    valid = {
        "ACTION_NONE",
        "ACTION_EXPANSION_ONLY",
        "ACTION_STORAGE_ONLY",
        "ACTION_COMBINED_EXPANSION_STORAGE",
    }
    if pd.notna(declared) and str(declared) in valid:
        return str(declared)
    try:
        ids = json.loads(str(solution.get("selected_candidate_ids", "[]")))
    except json.JSONDecodeError:
        ids = []
    delta = pd.to_numeric(pd.Series([solution.get("expansion_delta_mva", 0.0)]), errors="coerce").iloc[0]
    modules = pd.to_numeric(pd.Series([solution.get("storage_modules", 0.0)]), errors="coerce").iloc[0]
    has_expansion = bool(ids) or (pd.notna(delta) and float(delta) > 1e-9)
    has_storage = pd.notna(modules) and float(modules) > 0
    if has_expansion and has_storage:
        return "ACTION_COMBINED_EXPANSION_STORAGE"
    if has_expansion:
        return "ACTION_EXPANSION_ONLY"
    if has_storage:
        return "ACTION_STORAGE_ONLY"
    return "ACTION_NONE"


def _choose_current_solution(c0: pd.Series, a: pd.Series, b: pd.Series) -> dict[str, Any]:
    """按 C0 零成本优先、否则在 A/B 可行解中取最低 EAC。"""
    if str(c0["status"]) == "compliant":
        return {
            "scheme": "SCHEME_C0",
            "action": "ACTION_NONE",
            "clr": float(c0["clr_after"]),
            "eac": 0.0,
            "measure": "SCHEME_C0;ACTION_NONE",
        }
    if str(c0["status"]) == "not_identifiable":
        return {
            "scheme": "NOT_IDENTIFIABLE",
            "action": "NOT_IDENTIFIABLE",
            "clr": np.nan,
            "eac": np.nan,
            "measure": "not_identifiable_or_data_gap",
        }
    candidates = []
    for scheme, solution in (("SCHEME_A", a), ("SCHEME_B", b)):
        if str(solution["status"]) == "feasible" and pd.notna(solution["incremental_eac_wanyuan_per_year"]):
            candidates.append((float(solution["incremental_eac_wanyuan_per_year"]), 0 if scheme == "SCHEME_B" else 1, scheme, solution))
    if not candidates:
        return {
            "scheme": "NO_FEASIBLE_SOLUTION",
            "action": "NOT_IDENTIFIABLE",
            "clr": np.nan,
            "eac": np.nan,
            "measure": "infeasible",
        }
    _eac, _tie, scheme, chosen = min(candidates, key=lambda item: item[:2])
    action = _solution_action_mode(chosen)
    ids = _scheme_action(chosen)
    return {
        "scheme": scheme,
        "action": action,
        "clr": float(chosen["clr_after"]),
        "eac": float(chosen["incremental_eac_wanyuan_per_year"]),
        "measure": f"{scheme};{action};{ids};storage_modules={int(chosen['storage_modules'])}",
    }


def _range_text(low: Any, high: Any, unit: str) -> str:
    if pd.isna(low) or pd.isna(high):
        return "not_available"
    return f"{float(low):.3f}-{float(high):.3f} {unit}"


def _physical_gap_summary(stations: pd.DataFrame) -> pd.DataFrame:
    """按县区/电压汇总设备级物理缺口，不把不同站的峰值相加。

    缺口最大值用于解释措施触发，缺口设备数用于说明影响范围。静态输入缺失时
    优先返回 ``data_not_identified``，避免把未知状态误写成“不合规”。
    """
    required = {
        "region_id",
        "voltage_kv",
        "forward_peak_static_mw",
        "forward_limit_mw",
        "reverse_gap_parallel_static_mw",
    }
    missing = required - set(stations.columns)
    if missing:
        raise RealMatrixError(f"station baseline missing physical-gap fields {sorted(missing)}")
    frame = stations.copy()
    frame["forward_known"] = frame["forward_peak_static_mw"].notna() & frame["forward_limit_mw"].notna()
    frame["reverse_known"] = frame["reverse_gap_parallel_static_mw"].notna()
    frame["positive_capacity_gap_mw"] = (
        frame["forward_peak_static_mw"] - frame["forward_limit_mw"]
    ).clip(lower=0)
    frame["reverse_hosting_gap_mw"] = frame["reverse_gap_parallel_static_mw"].clip(lower=0)
    frame["positive_gap_flag"] = frame["forward_known"] & frame["positive_capacity_gap_mw"].gt(1e-9)
    frame["reverse_gap_flag"] = frame["reverse_known"] & frame["reverse_hosting_gap_mw"].gt(1e-9)

    def summarize(group: pd.DataFrame) -> pd.Series:
        positive_count = int(group["positive_gap_flag"].sum())
        reverse_count = int(group["reverse_gap_flag"].sum())
        data_gap_count = int((~group["forward_known"] | ~group["reverse_known"]).sum())
        if data_gap_count:
            trigger = "data_not_identified"
        elif positive_count and reverse_count:
            trigger = "positive_and_reverse_gap"
        elif positive_count:
            trigger = "positive_capacity_gap"
        elif reverse_count:
            trigger = "reverse_hosting_gap"
        else:
            trigger = "no_material_physical_gap"
        return pd.Series(
            {
                "positive_capacity_gap_mw": float(group["positive_capacity_gap_mw"].max(skipna=True))
                if group["forward_known"].any()
                else np.nan,
                "reverse_hosting_gap_mw": float(group["reverse_hosting_gap_mw"].max(skipna=True))
                if group["reverse_known"].any()
                else np.nan,
                "positive_gap_device_count": positive_count,
                "reverse_gap_device_count": reverse_count,
                "data_gap_device_count": data_gap_count,
                "measure_trigger_constraint": trigger,
            }
        )

    return (
        frame.groupby(["region_id", "voltage_kv"], sort=True)
        .apply(summarize, include_groups=False)
        .reset_index()
    )


def _technical_gap_by_county(stations: pd.DataFrame) -> pd.Series:
    """返回县区技术缺口最大值，供 35 kV 成本范围估算使用。"""
    summary = _physical_gap_summary(stations).copy()
    summary["technical_gap_mw"] = summary[["positive_capacity_gap_mw", "reverse_hosting_gap_mw"]].max(axis=1, skipna=True)
    return summary.set_index(["region_id", "voltage_kv"])["technical_gap_mw"]


def _duration_summary(index: pd.DataFrame) -> pd.DataFrame:
    return (
        index.groupby(["region_id", "voltage_kv"], as_index=False)
        .agg(
            duration_min_hours=("equivalent_reverse_duration_hours", "min"),
            duration_max_hours=("equivalent_reverse_duration_hours", "max"),
            duration_sample_count=("matched_sample_count", "max"),
        )
    )


def _matrix_rows(
    voltage_kv: int,
    baseline: pd.DataFrame,
    solutions: pd.DataFrame,
    candidates: pd.DataFrame,
    duration: pd.DataFrame,
    parent: pd.DataFrame,
    technical_gap: pd.Series,
    physical_gaps: pd.DataFrame,
    cost_cases: pd.DataFrame,
    source_hash: str,
    source_version: str,
) -> pd.DataFrame:
    base = baseline[baseline["voltage_kv"].eq(voltage_kv)].set_index("region_id")
    by_scheme = {
        scheme: solutions[
            solutions["voltage_kv"].eq(voltage_kv) & solutions["scheme"].eq(scheme)
        ].set_index("region_id")
        for scheme in ("C0", "A", "B")
    }
    duration_lookup = duration[duration["voltage_kv"].eq(voltage_kv)].set_index("region_id")
    gap_lookup = physical_gaps[physical_gaps["voltage_kv"].eq(voltage_kv)].set_index("region_id")
    candidate_delta = (
        candidates[candidates["voltage_kv"].eq(voltage_kv)]
        .groupby("region_id")["delta_capacity_mva"]
        .sum()
    )
    if voltage_kv == 35:
        local = cost_cases[cost_cases["voltage_kv"].eq(35)].copy()
        local["dynamic_wanyuan_per_mva"] = (
            local["dynamic_capex_wanyuan"] / local["project_capacity_mva"]
        )
        cost_rate_low = float(local["dynamic_wanyuan_per_mva"].min())
        cost_rate_high = float(local["dynamic_wanyuan_per_mva"].max())
    else:
        cost_rate_low = cost_rate_high = float("nan")

    rows: list[dict[str, Any]] = []
    for region_id in sorted(base.index):
        row = base.loc[region_id]
        c0 = by_scheme["C0"].loc[region_id]
        a = by_scheme["A"].loc[region_id]
        b = by_scheme["B"].loc[region_id]
        capacity = float(row["capacity_base_mva"])
        peak = float(row["positive_peak_base_mw"])
        maximum_delta = float(candidate_delta.get(region_id, 0.0))
        candidate_clr_min = capacity / peak
        candidate_clr_max = (capacity + maximum_delta) / peak
        if region_id in duration_lookup.index:
            duration_row = duration_lookup.loc[region_id]
            duration_text = (
                f"empirical_short/central/long; equivalent reverse duration "
                f"{duration_row['duration_min_hours']:.3f}-{duration_row['duration_max_hours']:.3f} h; "
                f"matched sample count {int(duration_row['duration_sample_count'])}"
            )
        else:
            duration_text = "not_available_due_to_static_or_mapping_gap"
        b_action = _scheme_action(b)
        chosen = _choose_current_solution(c0, a, b)
        recommendation = chosen["measure"]
        gap = gap_lookup.loc[region_id] if region_id in gap_lookup.index else pd.Series(dtype=object)
        quality_notes = (
            f"{row['quality_notes']}; C0={c0['status']}; A={a['status']}({a['status_reason']}); "
            f"B={b['status']}({b['status_reason']})"
        )
        result: dict[str, Any] = {
            "region_id": region_id,
            "voltage_kv": voltage_kv,
            "evidence_grade": row["evidence_grade"],
            "asset_scope_id": row["asset_scope_id"],
            "capacity_base_mva": capacity,
            "positive_peak_base_mw": peak,
            "reverse_peak_base_mw": row["reverse_peak_base_mw"],
            "clr_model_base": row["clr_model_base"],
            "clr_official_reference": row["clr_official_reference"],
            "pv_capacity_snapshot_mw": row["pv_capacity_snapshot_mw"],
            "C0_status": c0["status"],
            "C0_capex_wanyuan": 0.0,
            "A_status": a["status"],
            "A_expansion_action": _scheme_action(a),
            "A_storage_modules": a["storage_modules"],
            "A_capex_wanyuan": a["incremental_capex_wanyuan"],
            "A_eac_wanyuan_per_year": a["incremental_eac_wanyuan_per_year"],
            "A_clr_after": a["clr_after"],
            "B_status": b["status"],
            "B_expansion_action": b_action,
            "B_storage_modules": b["storage_modules"],
            "B_capex_wanyuan": b["incremental_capex_wanyuan"],
            "B_eac_wanyuan_per_year": b["incremental_eac_wanyuan_per_year"],
            "B_clr_after": b["clr_after"],
            "delta_C_A0": a["incremental_eac_wanyuan_per_year"],
            "delta_C_B0": b["incremental_eac_wanyuan_per_year"],
            "delta_C_redline": (
                a["incremental_eac_wanyuan_per_year"]
                - b["incremental_eac_wanyuan_per_year"]
                if a["status"] == b["status"] == "feasible"
                else float("nan")
            ),
            "candidate_clr_range": f"{candidate_clr_min:.4f}-{candidate_clr_max:.4f}",
            "candidate_clr_min": candidate_clr_min,
            "candidate_clr_max": candidate_clr_max,
            "recommended_current_measure": recommendation,
            "recommended_scheme_code": chosen["scheme"],
            "recommended_action_mode": chosen["action"],
            "recommended_clr": chosen["clr"],
            "recommended_eac_wanyuan_per_year": chosen["eac"],
            "positive_capacity_gap_mw": gap.get("positive_capacity_gap_mw", np.nan),
            "reverse_hosting_gap_mw": gap.get("reverse_hosting_gap_mw", np.nan),
            "positive_gap_device_count": gap.get("positive_gap_device_count", np.nan),
            "reverse_gap_device_count": gap.get("reverse_gap_device_count", np.nan),
            "data_gap_device_count": gap.get("data_gap_device_count", np.nan),
            "measure_trigger_constraint": gap.get("measure_trigger_constraint", "data_not_identified"),
            "cost_sensitivity_range": _range_text(
                b["incremental_eac_low_wanyuan_per_year"],
                b["incremental_eac_high_wanyuan_per_year"],
                "wanyuan/year",
            ),
            "duration_sensitivity_range": duration_text,
            "quality_notes": quality_notes,
            "strict_stock_R_le_2_status": a["strict_stock_R_le_2_status"],
            "strict_r_lt_2_policy_status": c0.get("strict_r_lt_2_policy_status", "not_evaluated_current_C0AB_scope"),
            "a_expansion_limit_mva": a["a_expansion_limit_mva"],
            "source_ref": "county_baseline.csv+real_plan_county_solutions.csv+expansion_candidates.csv+empirical_scenario_index.csv",
            "source_version": source_version,
            "transformation": "join only identical region-voltage keys; never aggregate across voltage levels",
            "scenario_id": f"real_2025_matrix_{voltage_kv}kv",
            "quality_flag": f"evidence_grade_{row['evidence_grade']}",
            "source_sha256": source_hash,
        }
        if voltage_kv == 35:
            mapped = parent[parent["region_id"].eq(region_id)]
            counts = mapped["parent_scope"].value_counts().to_dict()
            gap = float(technical_gap.get((region_id, 35), 0.0))
            expansion_low = gap / 0.95 * cost_rate_low
            expansion_high = gap / 0.95 * cost_rate_high
            result.update(
                {
                    "parent_supply_mapping_status": (
                        f"in_scope_110kv={counts.get('in_scope_110kv', 0)}; "
                        f"external_upstream={counts.get('external_upstream', 0)}; "
                        f"incomplete={counts.get('parent_missing', 0) + counts.get('conflicting_parent_ids', 0)}"
                    ),
                    "technical_gap_mw": gap,
                    "expansion_cost_range_wanyuan": (
                        f"{expansion_low:.3f}-{expansion_high:.3f} indicative local-case range"
                    ),
                    "recommendation_basis": "auxiliary_technical_requirement_not_unique_discrete_optimum",
                    "A_expansion_action": "no_35kv_station_candidate; technical requirement only",
                    "B_expansion_action": "no_35kv_station_candidate; technical requirement only",
                    "recommended_current_measure": (
                        "auxiliary technical requirement only; no unique discrete optimum; "
                        + recommendation
                    ),
                }
            )
        rows.append(result)
    return pd.DataFrame(rows)


def _write_csv(path: Path, frame: pd.DataFrame, sort_by: list[str]) -> None:
    missing = set(LINEAGE_FIELDS) - set(frame.columns)
    if missing:
        raise RealMatrixError(f"{path.name}: missing lineage fields {sorted(missing)}")
    frame.sort_values(sort_by, kind="stable").reset_index(drop=True).to_csv(
        path, index=False, lineterminator="\n", float_format="%.10g"
    )


def build_real_matrices(
    processed_root: Path,
    run_dir: Path,
    contract_path: Path,
) -> dict[str, Any]:
    """生成并验证 110/35 kV 两套互不跨级聚合的矩阵。"""
    processed_root = Path(processed_root).resolve()
    run_dir = Path(run_dir).resolve()
    contract_path = Path(contract_path).resolve()
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    input_paths = [
        run_dir / "county_baseline.csv",
        run_dir / "station_baseline.csv",
        run_dir / "real_plan_county_solutions.csv",
        run_dir / "empirical_scenario_index.csv",
        processed_root / "transformer_master.csv",
        processed_root / "expansion_candidates.csv",
        processed_root / "cost_cases.csv",
        contract_path,
    ]
    baseline = _read(
        run_dir,
        "county_baseline.csv",
        {"region_id", "voltage_kv", "capacity_base_mva", "positive_peak_base_mw", "quality_notes"},
    )
    stations = _read(
        run_dir,
        "station_baseline.csv",
        {"region_id", "voltage_kv", "forward_peak_static_mw", "forward_limit_mw", "reverse_gap_parallel_static_mw"},
    )
    solutions = _read(
        run_dir,
        "real_plan_county_solutions.csv",
        {"region_id", "voltage_kv", "scheme", "status", "positive_peak_base_mw"},
    )
    duration_index = _read(
        run_dir,
        "empirical_scenario_index.csv",
        {"region_id", "voltage_kv", "equivalent_reverse_duration_hours", "matched_sample_count"},
    )
    master = _read(
        processed_root,
        "transformer_master.csv",
        {"region_id", "voltage_kv", "station_id", "parent_supply_id", "equipment_source_row"},
    )
    candidates = _read(
        processed_root,
        "expansion_candidates.csv",
        {"candidate_id", "region_id", "voltage_kv", "delta_capacity_mva"},
    )
    cost_cases = _read(
        processed_root,
        "cost_cases.csv",
        {"voltage_kv", "project_capacity_mva", "dynamic_capex_wanyuan"},
    )
    source_hash = _combined_hash(input_paths)
    source_version = "+".join(sorted(set(master["source_version"].dropna().astype(str))))
    parent = _parent_mapping(master, source_hash, source_version)
    duration = _duration_summary(duration_index)
    technical_gap = _technical_gap_by_county(stations)
    physical_gaps = _physical_gap_summary(stations)
    matrix_110 = _matrix_rows(
        110,
        baseline,
        solutions,
        candidates,
        duration,
        parent,
        technical_gap,
        physical_gaps,
        cost_cases,
        source_hash,
        source_version,
    )
    matrix_35 = _matrix_rows(
        35,
        baseline,
        solutions,
        candidates,
        duration,
        parent,
        technical_gap,
        physical_gaps,
        cost_cases,
        source_hash,
        source_version,
    )
    required = set(contract["outputs"]["formal_110_matrix"]["required_fields"])
    if len(matrix_110) != 8 or len(matrix_35) != 8:
        raise RealMatrixError("both voltage-separated matrices must contain eight regions")
    if required - set(matrix_110.columns):
        raise RealMatrixError(f"110-kV matrix missing contract fields {sorted(required - set(matrix_110.columns))}")

    run_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(run_dir / "matrix_110kv.csv", matrix_110, ["region_id"])
    _write_csv(run_dir / "matrix_35kv.csv", matrix_35, ["region_id"])
    _write_csv(run_dir / "parent_supply_mapping_35kv.csv", parent, ["region_id", "station_id"])
    (run_dir / "matrix_110kv.md").write_text(
        matrix_110.sort_values("region_id").to_markdown(index=False) + "\n", encoding="utf-8"
    )
    (run_dir / "matrix_35kv.md").write_text(
        matrix_35.sort_values("region_id").to_markdown(index=False) + "\n", encoding="utf-8"
    )

    a = solutions[solutions["scheme"].eq("A")].set_index(["region_id", "voltage_kv"])
    b = solutions[solutions["scheme"].eq("B")].set_index(["region_id", "voltage_kv"])
    both = a["status"].eq("feasible") & b["status"].eq("feasible")
    qx_parent = parent[parent["region_id"].eq("QX-00005")]
    hard_assertions = {
        "separate_eight_row_voltage_matrices": bool(
            len(matrix_110) == len(matrix_35) == 8
            and set(matrix_110["voltage_kv"]) == {110}
            and set(matrix_35["voltage_kv"]) == {35}
        ),
        "fixed_positive_peak_matches_baseline": bool(
            matrix_110.set_index("region_id")["positive_peak_base_mw"].equals(
                baseline[baseline["voltage_kv"].eq(110)].set_index("region_id")[
                    "positive_peak_base_mw"
                ]
            )
            and matrix_35.set_index("region_id")["positive_peak_base_mw"].equals(
                baseline[baseline["voltage_kv"].eq(35)].set_index("region_id")[
                    "positive_peak_base_mw"
                ]
            )
        ),
        "C0_zero_cost_noncompliance_visible": bool(
            matrix_110["C0_capex_wanyuan"].eq(0).all()
            and matrix_35["C0_capex_wanyuan"].eq(0).all()
        ),
        "B_eac_not_above_A_when_both_feasible": bool(
            (
                b.loc[both, "incremental_eac_wanyuan_per_year"]
                <= a.loc[both, "incremental_eac_wanyuan_per_year"] + 1e-7
            ).all()
        ),
        "no_cross_layer_cost_aggregation": bool(not parent["cross_layer_cost_aggregated"].any()),
        "qx00005_parent_4_plus_4_preserved": bool(
            len(qx_parent) == 8
            and qx_parent["parent_scope"].eq("in_scope_110kv").sum() == 4
            and qx_parent["parent_scope"].eq("external_upstream").sum() == 4
        ),
        "35kv_no_unique_discrete_optimum_claim": bool(
            matrix_35["recommendation_basis"].eq(
                "auxiliary_technical_requirement_not_unique_discrete_optimum"
            ).all()
        ),
        "strict_r_lt_2_policy_not_hidden": bool(
            solutions["strict_r_lt_2_policy_status"].eq(
                "requires_intervention_and_incremental_cost"
            ).all()
        ),
        "anonymized_region_ids_only": bool(
            matrix_110["region_id"].str.fullmatch(r"QX-\d{5}").all()
            and matrix_35["region_id"].str.fullmatch(r"QX-\d{5}").all()
        ),
    }
    if not all(hard_assertions.values()):
        failed = [key for key, value in hard_assertions.items() if not value]
        raise RealMatrixError(f"matrix release gates failed: {failed}")
    filenames = [
        "matrix_110kv.csv",
        "matrix_35kv.csv",
        "matrix_110kv.md",
        "matrix_35kv.md",
        "parent_supply_mapping_35kv.csv",
    ]
    manifest: dict[str, Any] = {
        "matrix_version": MATRIX_VERSION,
        "contract_sha256": _sha256(contract_path),
        "input_fingerprint": source_hash,
        "hard_assertions": hard_assertions,
        "output_files": {
            filename: {"sha256": _sha256(run_dir / filename), "bytes": (run_dir / filename).stat().st_size}
            for filename in filenames
        },
    }
    (run_dir / "matrix_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest
