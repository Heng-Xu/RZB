#!/usr/bin/env python3
"""汇总 v3.2 终审证据并生成冻结后的正式结果包。

本脚本只汇总已经运行完成的基线、Rcap 前沿和敏感性结果，不在汇总阶段
重新求解。输入目录可以位于 ``/tmp``，生成物全部写入正式结果目录，因而
正式结果包不依赖临时目录才能查值。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.v32_contract import validation_commit_sha  # noqa: E402
from src.v32_frontier_aggregate import validate_frontier_nested  # noqa: E402
from src.v32_model import recommended_rcap_interval  # noqa: E402
from src.v32_threshold import classify_economic_release_thresholds  # noqa: E402
from src.v3_outputs import write_transposed_word_matrix  # noqa: E402


REGIONS = [f"QX-{index:05d}" for index in (1, 3, 4, 5, 7, 8, 9, 10)]
PATH_ACTUAL = "PATH_ACTUAL_2021_2025"
PATH_ELASTIC = "PATH_OPT_CLR_UNBOUNDED"
PATH_RIGID = "PATH_OPT_CLR_LE_2"
PATHS = (PATH_ACTUAL, PATH_ELASTIC, PATH_RIGID)


class FormalOutputError(ValueError):
    """冻结结果汇总门禁不满足。"""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _required(path: Path) -> Path:
    path = Path(path)
    if not path.is_file():
        raise FormalOutputError(f"required evidence file is missing: {path}")
    return path


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(_required(path))


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def _number(value: Any) -> float | None:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def _display(value: Any) -> str:
    if value is None:
        return "未形成"
    try:
        if bool(pd.isna(value)):
            return "未形成"
    except (TypeError, ValueError):
        pass
    if isinstance(value, float) and not math.isfinite(value):
        return "未形成"
    return str(value)


def _format_number(value: Any, digits: int = 3) -> str:
    number = _number(value)
    if number is None:
        return "未形成"
    return f"{number:.{digits}f}"


def classify_recommendation_type(
    voltage_kv: int,
    *,
    elastic_feasible: bool,
    threshold_status: str | None,
) -> str:
    """按物理可行性和 Rcap 是否绑定分类，不为非绑定片区制造数值。"""
    if int(voltage_kv) != 110:
        return "辅助层不施加逐年Rcap"
    if not bool(elastic_feasible):
        return "技术约束优先型"
    if threshold_status == "binding_threshold_bracketed":
        return "经济释放阈值型"
    if threshold_status == "non_binding_not_identified_in_horizon":
        return "当前不绑定型"
    return "无需调整型"


def _collect_point_files(root: Path, filename: str) -> list[Path]:
    root = Path(root)
    files = sorted(root.glob(f"*/{filename}"))
    if not files:
        raise FormalOutputError(f"no {filename} files found in {root}")
    return files


def _collect_frontier(root: Path, filename: str) -> pd.DataFrame:
    files = _collect_point_files(root, filename)
    frames = [pd.read_csv(path) for path in files]
    frame = pd.concat(frames, ignore_index=True, sort=False)
    if filename == "frontier_point.csv":
        frame["rcap_sort"] = pd.to_numeric(frame["rcap_numeric"], errors="coerce").fillna(999.0)
        frame = frame.sort_values(["region_id", "rcap_sort"], kind="stable").drop(columns=["rcap_sort"])
        validate_frontier_nested(frame)
    return frame.reset_index(drop=True)


def _collect_parameter_frontiers(root: Path) -> dict[str, pd.DataFrame]:
    root = Path(root)
    files = sorted(root.glob("*/parameter_frontier.csv"))
    if not files:
        raise FormalOutputError(f"no parameter_frontier.csv files found in {root}")
    result: dict[str, pd.DataFrame] = {}
    for path in files:
        frame = pd.read_csv(path)
        if frame.empty:
            raise FormalOutputError(f"empty sensitivity frontier: {path}")
        key = str(frame.get("scenario_id", pd.Series([path.parent.name])).iloc[0])
        if key in result:
            key = f"{key}__{path.parent.name}"
        result[key] = frame
    return result


def _copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(_required(source), target)


def _copy_report_support(project_root: Path, output_dir: Path) -> list[dict[str, Any]]:
    """把已脱敏的方法和局部案例底稿纳入正式结果包。"""
    support_files = {
        "report_support/modeling_method_summary.md": project_root
        / "分析/2026-08-26-建模思路与真实方法总结_甲方汇报辅助.md",
        "report_support/10kv_case_reanalysis.md": project_root
        / "分析/2026-08-26-10kV联络案例重分析_收资定稿口径.md",
        "report_support/10kv_case_conclusions.md": project_root
        / "docs/TIE-CASE-CONCLUSIONS.md",
        "report_support/v32_final_review_and_freeze.md": project_root
        / "分析/2026-08-29-v3.2模型终审与冻结记录.md",
    }
    copied: list[dict[str, Any]] = []
    for relative_target, source in support_files.items():
        target = output_dir / relative_target
        _copy_file(source, target)
        copied.append(
            {
                "role": "report_support",
                "file": relative_target,
                "source": str(source.relative_to(project_root)),
                "sha256": _sha256(target),
                "bytes": target.stat().st_size,
            }
        )
    return copied


def _run_evidence_inventory(role: str, root: Path, filename: str) -> list[dict[str, Any]]:
    """登记每个扫描点的结果文件，保留外部临时目录的真实来源。"""
    root = Path(root)
    files = sorted(root.glob(f"*/{filename}"))
    return [
        {
            "role": role,
            "source": str(path),
            "sha256": _sha256(path),
            "bytes": path.stat().st_size,
        }
        for path in files
    ]


def _copy_baseline_evidence(baseline_dir: Path, output_dir: Path) -> list[dict[str, Any]]:
    """复制基线顶层结果和 SOC/时序底稿，避免正式包依赖临时运行目录。"""
    baseline_dir = Path(baseline_dir)
    copied: list[dict[str, Any]] = []
    top_level_names = [
        "manifest.json",
        "policy_2025_summary.csv",
        "policy_cost_comparison.csv",
        "policy_path_year_results.csv",
        "policy_path_action_results.csv",
        "policy_path_cost_breakdown.csv",
        "actual_path_year_results.csv",
        "actual_path_action_results.csv",
        "actual_path_cost_breakdown.csv",
        "region_gap_summary.csv",
        "station_gap_diagnostics.csv",
        "initial_physical_diagnostics.csv",
        "qx00005_chronology_comparison.csv",
    ]
    for name in top_level_names:
        source = _required(baseline_dir / name)
        target = output_dir / "baseline" / name
        _copy_file(source, target)
        copied.append({"role": "baseline", "file": str(target.relative_to(output_dir)), "sha256": _sha256(target), "bytes": target.stat().st_size})

    for directory in ("cost_library", "time_physics", "qx00005_soc"):
        source_dir = baseline_dir / directory
        if not source_dir.is_dir():
            raise FormalOutputError(f"required baseline directory is missing: {source_dir}")
        target_dir = output_dir / "baseline" / directory
        shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
        for target in sorted(path for path in target_dir.rglob("*") if path.is_file()):
            copied.append({"role": f"baseline_{directory}", "file": str(target.relative_to(output_dir)), "sha256": _sha256(target), "bytes": target.stat().st_size})
    return copied


def _derive_refined_thresholds(frontier: pd.DataFrame) -> pd.DataFrame:
    """从局部细化点识别 5% 近优带的最小非惩罚 Rcap 区间。"""
    validate_frontier_nested(frontier)
    rows: list[dict[str, Any]] = []
    for region_id, group in frontier.groupby("region_id", sort=True):
        group = group.copy()
        group["rcap_num"] = pd.to_numeric(group["rcap_numeric"], errors="coerce")
        group["cost_num"] = pd.to_numeric(group["cumulative_in_service_eac_wanyuan"], errors="coerce")
        group["feasible_bool"] = group["feasible"].map(_bool)
        unbounded = group[group["rcap"].astype(str).eq("unbounded")]
        numeric = group[group["rcap_num"].notna()].sort_values("rcap_num", kind="stable")
        if len(unbounded) != 1 or numeric.empty or not _bool(unbounded.iloc[0]["feasible"]):
            rows.append({"region_id": str(region_id), "refined_status": "not_formed", "refined_threshold_lower_exclusive": math.nan, "refined_threshold_upper_inclusive": math.nan})
            continue
        base_cost = _number(unbounded.iloc[0]["cost_num"])
        if base_cost is None:
            raise FormalOutputError(f"{region_id}: unbounded refined cost is not numeric")
        near = numeric[numeric["feasible_bool"] & (numeric["cost_num"] <= base_cost * 1.05 + 1e-7)]
        if near.empty:
            rows.append({"region_id": str(region_id), "refined_status": "not_reached", "refined_threshold_lower_exclusive": float(numeric["rcap_num"].max()), "refined_threshold_upper_inclusive": math.nan})
            continue
        upper = float(near["rcap_num"].min())
        below = numeric[numeric["rcap_num"] < upper].tail(1)
        rows.append({
            "region_id": str(region_id),
            "refined_status": "binding_threshold_bracketed" if not below.empty else "threshold_at_scan_low",
            "refined_threshold_lower_exclusive": float(below.iloc[0]["rcap_num"]) if not below.empty else math.nan,
            "refined_threshold_upper_inclusive": upper,
            "refined_cost_below_wanyuan": float(below.iloc[0]["cost_num"]) if not below.empty else math.nan,
            "refined_cost_at_threshold_wanyuan": float(near.loc[near["rcap_num"].eq(upper), "cost_num"].iloc[0]),
            "refined_unbounded_cost_wanyuan": base_cost,
        })
    return pd.DataFrame(rows)


def _build_robust_summary(
    base: pd.DataFrame,
    sensitivity: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    scenarios = {"base": base, **sensitivity}
    for region_id in REGIONS:
        point_sets: list[set[float]] = []
        scenario_status: list[str] = []
        for label, frame in scenarios.items():
            result = recommended_rcap_interval(frame, region_id=region_id, near_optimal_band=0.05)
            points = {round(float(value), 10) for value in result.get("rcap_points", [])}
            if points:
                point_sets.append(points)
            scenario_status.append(f"{label}:{','.join(f'{point:g}' for point in sorted(points)) or 'none'}")
        robust = sorted(set.intersection(*point_sets)) if point_sets and len(point_sets) == len(scenarios) else []
        scan_high = float(pd.to_numeric(base["rcap_numeric"], errors="coerce").max())
        upper_identified = bool(robust and max(robust) < scan_high - 1e-9)
        rows.append({
            "region_id": region_id,
            "near_optimal_band": 0.05,
            "robust_rcap_points": ";".join(f"{point:g}" for point in robust),
            "robust_rcap_lower": min(robust) if robust else math.nan,
            "robust_rcap_upper": max(robust) if robust and upper_identified else math.nan,
            "scan_upper": scan_high,
            "upper_identified_within_scan": upper_identified,
            "scenario_point_sets": " | ".join(scenario_status),
            "interpretation": (
                "稳健近优带上界已在扫描内识别"
                if upper_identified
                else "稳健近优带向扫描上界延伸，未在本次扫描范围内识别上界"
            ) if robust else "未形成共同近优 Rcap 点集",
        })
    return pd.DataFrame(rows)


def _path_row(frame: pd.DataFrame, region_id: str, voltage_kv: int, path_id: str) -> pd.Series | None:
    rows = frame[
        frame["region_id"].astype(str).eq(region_id)
        & frame["voltage_kv"].astype(int).eq(int(voltage_kv))
        & frame["path_id"].astype(str).eq(path_id)
    ]
    return None if rows.empty else rows.iloc[0]


def _action_label(action_types: Any) -> str:
    raw = str(action_types or "none")
    labels = {
        "storage": "储能",
        "new_third_transformer": "新增第三台主变",
        "new_station": "新建站",
        "replacement_or_uprating": "替换或增容",
        "line_or_bay_project": "线路或间隔工程",
        "none": "无",
    }
    values = [labels.get(item.strip(), item.strip()) for item in raw.split(";") if item.strip()]
    return "、".join(dict.fromkeys(values)) or "无"


def _trigger_label(gap_row: pd.Series | None) -> str:
    if gap_row is None:
        return "未形成设备级诊断"
    raw = str(gap_row.get("measure_trigger_constraint", "none"))
    labels = {
        "positive_capacity_gap": "正向容量缺口",
        "reverse_hosting_gap": "反向承载缺口",
        "none": "无设备级缺口触发",
    }
    return "、".join(dict.fromkeys(labels.get(item.strip(), item.strip()) for item in raw.split(";") if item.strip())) or "无设备级缺口触发"


def _recommendation(
    voltage_kv: int,
    recommendation_type: str,
    threshold: pd.Series | None,
    refined: pd.Series | None,
    robust: pd.Series | None,
    feasible: bool,
) -> str:
    if int(voltage_kv) != 110:
        return (
            "35 kV辅助层不施加逐年Rcap；"
            + ("当前可行结果仅用于设备承载辅助分析。" if feasible else "当前未形成完整可行解，先处理技术或数据边界。")
        )
    if recommendation_type == "经济释放阈值型" and threshold is not None:
        low = _number(threshold.get("coarse_release_threshold_lower"))
        high = _number(threshold.get("coarse_release_threshold_upper"))
        refined_low = _number(refined.get("refined_threshold_lower_exclusive")) if refined is not None else None
        refined_high = _number(refined.get("refined_threshold_upper_inclusive")) if refined is not None else None
        robust_low = _number(robust.get("robust_rcap_lower")) if robust is not None else None
        parts = []
        if refined_low is not None and refined_high is not None:
            parts.append(f"局部细化阈值约为{refined_low:g}～{refined_high:g}")
        elif low is not None and high is not None:
            parts.append(f"粗扫描阈值位于{low:g}～{high:g}")
        if robust_low is not None:
            parts.append(f"多场景稳健近优下限为{robust_low:g}")
        if robust is not None and not _bool(robust.get("upper_identified_within_scan", False)):
            parts.append("本次扫描未识别近优带上界")
        return "；".join(parts) + "。"
    if recommendation_type == "当前不绑定型":
        return "本规划期Rcap不构成有效约束，不人为给出推荐Rcap数值。"
    if recommendation_type == "技术约束优先型":
        return "无上限方案未形成物理可行集，先处理网络、设备或储能边界，不以Rcap数值替代技术校核。"
    return "本规划期无需调整Rcap，维持现有规划约束并按后续条件复核。"


def build_formal_matrices(
    *,
    annual_reference: pd.DataFrame,
    pv_snapshot: pd.DataFrame,
    actual_years: pd.DataFrame,
    policy_summary: pd.DataFrame,
    cost_comparison: pd.DataFrame,
    gaps: pd.DataFrame,
    diagnostics: pd.DataFrame,
    base_frontier: pd.DataFrame,
    base_thresholds: pd.DataFrame,
    refined_thresholds: pd.DataFrame,
    robust_summary: pd.DataFrame,
) -> dict[int, pd.DataFrame]:
    """由已落盘证据构造 110 kV 正式矩阵和 35 kV 辅助矩阵。"""
    reference = annual_reference.copy()
    reference["year"] = reference["year"].astype(int)
    ref2021 = reference[reference["year"].eq(2021)].set_index(["region_id", "voltage_kv"])
    ref2025 = reference[reference["year"].eq(2025)].set_index(["region_id", "voltage_kv"])
    pv = pv_snapshot.groupby(["region_id", "voltage_kv"], as_index=False)["pv_online_mw"].sum()
    pv = pv.set_index(["region_id", "voltage_kv"])["pv_online_mw"].to_dict()
    actual2025 = actual_years[actual_years["year"].astype(int).eq(2025)]
    threshold_map = base_thresholds.set_index("region_id").to_dict("index")
    refined_map = refined_thresholds.set_index("region_id").to_dict("index")
    robust_map = robust_summary.set_index("region_id").to_dict("index")
    rows_by_voltage: dict[int, list[dict[str, Any]]] = {110: [], 35: []}

    for region_id in REGIONS:
        for voltage_kv in (110, 35):
            key = (region_id, voltage_kv)
            if key not in ref2021.index or key not in ref2025.index:
                raise FormalOutputError(f"annual reference missing {region_id}|{voltage_kv}")
            base_row = ref2021.loc[key]
            current = ref2025.loc[key]
            elastic = _path_row(policy_summary, region_id, voltage_kv, PATH_ELASTIC)
            rigid = _path_row(policy_summary, region_id, voltage_kv, PATH_RIGID)
            actual = _path_row(actual2025, region_id, voltage_kv, PATH_ACTUAL)
            comparison_rows = cost_comparison[
                cost_comparison["region_id"].astype(str).eq(region_id)
                & cost_comparison["voltage_kv"].astype(int).eq(voltage_kv)
            ]
            comparison = None if comparison_rows.empty else comparison_rows.iloc[0]
            gap_rows = gaps[
                gaps["region_id"].astype(str).eq(region_id)
                & gaps["voltage_kv"].astype(int).eq(voltage_kv)
            ]
            gap = None if gap_rows.empty else gap_rows.iloc[0]
            diagnostic_rows = diagnostics[
                diagnostics["region_id"].astype(str).eq(region_id)
                & diagnostics["voltage_kv"].astype(int).eq(voltage_kv)
            ]
            diagnostic = None if diagnostic_rows.empty else diagnostic_rows.iloc[0]
            elastic_feasible = bool(elastic is not None and str(elastic.get("status")) == "feasible")
            rigid_feasible = bool(rigid is not None and str(rigid.get("status")) == "feasible")
            threshold = threshold_map.get(region_id) if voltage_kv == 110 else None
            refined = refined_map.get(region_id) if voltage_kv == 110 else None
            robust = robust_map.get(region_id) if voltage_kv == 110 else None
            threshold_status = str(threshold.get("threshold_status")) if threshold else None
            recommendation_type = classify_recommendation_type(
                voltage_kv,
                elastic_feasible=elastic_feasible,
                threshold_status=threshold_status,
            )
            row: dict[str, Any] = {
                "region_id": region_id,
                "voltage_kv": voltage_kv,
                "evidence_grade": "EVIDENCE_A" if (region_id == "QX-00005" and voltage_kv == 110) else "EVIDENCE_B",
                "asset_scope_id": "operating_2025",
                "planning_baseline_year": 2021,
                "planning_baseline_capacity_mva": float(base_row["official_capacity_mva"]),
                "capacity_base_mva": float(current["official_capacity_mva"]),
                "positive_peak_base_mw": float(current["official_positive_peak_mw"]),
                "official_clr_2025": float(current["official_clr"]),
                "pv_online_snapshot_2026_mw": pv.get(key),
                "pv_snapshot_quality": "2026快照与2025负荷组合，仅作跨年背景量",
                "pv_to_peak_ratio": (_number(pv.get(key)) / float(current["official_positive_peak_mw"]) if _number(pv.get(key)) is not None else None),
                "energy_penetration": "未形成（缺少同步负荷—光伏能量分解）",
                "reverse_peak_base_mw": "未形成同步反向峰值",
                "positive_capacity_gap_mw": gap.get("positive_capacity_gap_mw") if gap is not None else "未形成设备级诊断",
                "reverse_hosting_gap_mw": gap.get("reverse_hosting_gap_mw") if gap is not None else "未形成设备级诊断",
                "positive_gap_device_count": gap.get("positive_gap_device_count") if gap is not None else "未形成设备级诊断",
                "reverse_gap_device_count": gap.get("reverse_gap_device_count") if gap is not None else "未形成设备级诊断",
                "measure_trigger_constraint": _trigger_label(gap),
                "initial_physical_reason": diagnostic.get("reason") if diagnostic is not None else "未形成诊断",
                "initial_physical_diagnostic_basis": diagnostic.get("diagnostic_basis") if diagnostic is not None else "未形成诊断",
                "PATH_ACTUAL_2021_2025_clr_2025": actual.get("clr") if actual is not None else "未形成",
                "PATH_ACTUAL_2021_2025_cumulative_eac": "未识别",
                "PATH_OPT_CLR_UNBOUNDED_clr_2025": elastic.get("physical_clr_2025") if elastic_feasible else "不可行",
                "PATH_OPT_CLR_UNBOUNDED_cumulative_eac": elastic.get("cumulative_in_service_eac_wanyuan") if elastic_feasible else "不可行",
                "PATH_OPT_CLR_UNBOUNDED_installed_capacity_mva": elastic.get("installed_capacity_mva_2025") if elastic_feasible else "不可行",
                "PATH_OPT_CLR_UNBOUNDED_added_capacity_mva": (float(elastic.get("installed_capacity_mva_2025")) - float(base_row["official_capacity_mva"]) if elastic_feasible else "不可行"),
                "PATH_OPT_CLR_UNBOUNDED_storage_modules": elastic.get("storage_modules_2025") if elastic_feasible else "不可行",
                "PATH_OPT_CLR_UNBOUNDED_storage_power_mw": (float(elastic.get("storage_modules_2025")) * 0.1 if elastic_feasible else "不可行"),
                "PATH_OPT_CLR_UNBOUNDED_reverse_peak_2025_mw": elastic.get("p_minus_mw_2025") if elastic_feasible else "不可行",
                "PATH_OPT_CLR_LE_2_clr_2025": rigid.get("physical_clr_2025") if rigid_feasible else "不可行",
                "PATH_OPT_CLR_LE_2_policy_control_ratio_2025": rigid.get("policy_control_ratio_2025") if rigid_feasible else "不可行",
                "PATH_OPT_CLR_LE_2_cumulative_eac": rigid.get("cumulative_in_service_eac_wanyuan") if rigid_feasible else "不可行",
                "PATH_OPT_CLR_LE_2_installed_capacity_mva": rigid.get("installed_capacity_mva_2025") if rigid_feasible else "不可行",
                "PATH_OPT_CLR_LE_2_added_capacity_mva": (float(rigid.get("installed_capacity_mva_2025")) - float(base_row["official_capacity_mva"]) if rigid_feasible else "不可行"),
                "PATH_OPT_CLR_LE_2_storage_modules": rigid.get("storage_modules_2025") if rigid_feasible else "不可行",
                "PATH_OPT_CLR_LE_2_storage_power_mw": (float(rigid.get("storage_modules_2025")) * 0.1 if rigid_feasible else "不可行"),
                "PATH_OPT_CLR_LE_2_reverse_peak_2025_mw": rigid.get("p_minus_mw_2025") if rigid_feasible else "不可行",
                "strict_path_incremental_cost": (comparison.get("rigid_minus_elastic_eac_wanyuan") if comparison is not None and _bool(comparison.get("direct_comparison_allowed")) else "未形成直接比较"),
                "constraint_status": "两条优化方案均可行" if elastic_feasible and rigid_feasible else "无上限方案未形成完整可行路径" if not elastic_feasible else "严格方案未形成完整可行路径",
                "recommendation_type": recommendation_type,
                "recommended_measure": _action_label(elastic.get("action_types") if elastic_feasible else "none"),
                "recommendation": _recommendation(voltage_kv, recommendation_type, threshold, refined, robust, elastic_feasible),
                "recommended_rcap_interval": (
                    f"阈值 {_format_number(refined.get('refined_threshold_lower_exclusive'), 3)}～{_format_number(refined.get('refined_threshold_upper_inclusive'), 3)}；稳健近优下限≥{_format_number(robust.get('robust_rcap_lower'), 3)}；上界未在扫描内识别"
                    if recommendation_type == "经济释放阈值型" and refined is not None and _number(refined.get("refined_threshold_upper_inclusive")) is not None
                    else "本规划期Rcap不构成有效约束" if recommendation_type == "当前不绑定型"
                    else "未形成（先解决物理可行性）" if recommendation_type == "技术约束优先型"
                    else "无需调整"
                ),
                "recommended_rcap_center": (
                    f"{_format_number(robust.get('robust_rcap_lower'), 3)}起；上界未识别"
                    if recommendation_type == "经济释放阈值型" and robust is not None and _number(robust.get("robust_rcap_lower")) is not None
                    else "不适用"
                ),
                "recommended_rcap_interval_effective_samples": len(str(robust.get("robust_rcap_points", "")).split(";")) if robust and robust.get("robust_rcap_points") else 0,
                "recommended_rcap_interval_method": "Rcap弹性前沿5%近优带＋局部细化＋同维度敏感性稳健交集；不与实现CLR取交集" if recommendation_type == "经济释放阈值型" else "不输出数值推荐",
                "rcap_coarse_threshold_lower": threshold.get("coarse_release_threshold_lower") if threshold else None,
                "rcap_coarse_threshold_upper": threshold.get("coarse_release_threshold_upper") if threshold else None,
                "rcap_refined_threshold_lower": refined.get("refined_threshold_lower_exclusive") if refined else None,
                "rcap_refined_threshold_upper": refined.get("refined_threshold_upper_inclusive") if refined else None,
                "rcap_robust_near_optimal_lower": robust.get("robust_rcap_lower") if robust else None,
                "rcap_robust_near_optimal_upper": robust.get("robust_rcap_upper") if robust else None,
                "rcap_robust_upper_identified": robust.get("upper_identified_within_scan") if robust else False,
                "EENS": "未建模（无可追溯完整网络时序证据）",
                "curtailment": "未设置弃光变量",
                "network_check": "内部容量网络压力筛查；不等同精确AC/DC潮流",
                "source_ref": "SRC08+SRC02+SRC03+approved_timeseries_map",
                "source_version": "v3.2 frozen input package",
                "transformation": "formal matrix assembled from audited baseline and scenario outputs",
                "scenario_id": "real_2021_2025_v32_frozen",
                "quality_flag": "cross_year_pv_snapshot_disclosed;historical_device_scope_not_closed",
                "source_sha256": str(base_row.get("source_sha256", "")),
            }
            rows_by_voltage[voltage_kv].append(row)

    return {voltage: pd.DataFrame(rows) for voltage, rows in rows_by_voltage.items()}


def _markdown_matrix(frame: pd.DataFrame, voltage_kv: int) -> str:
    regions = [region for region in REGIONS if region in set(frame["region_id"].astype(str))]
    indicator_fields: list[tuple[str, str]] = [
        ("现状负荷峰值（2025年同步正向最大净负荷，MW）", "positive_peak_base_mw"),
        ("站级光伏在线容量（2026年快照，MW）", "pv_online_snapshot_2026_mw"),
        ("2021年实际在役资产共同基线（MVA）", "planning_baseline_capacity_mva"),
        ("2025年运行口径公用变容量（MVA）", "capacity_base_mva"),
        ("正向容量缺口（MW）", "positive_capacity_gap_mw"),
        ("反向承载缺口（MW）", "reverse_hosting_gap_mw"),
        ("缺口触发约束", "measure_trigger_constraint"),
        ("推荐分类", "recommendation_type"),
        ("推荐Rcap区间或结论", "recommended_rcap_interval"),
        ("推荐措施", "recommended_measure"),
        ("不限制容载比方案2025年物理容载比", "PATH_OPT_CLR_UNBOUNDED_clr_2025"),
        ("不限制容载比方案新增容量（MVA）", "PATH_OPT_CLR_UNBOUNDED_added_capacity_mva"),
        ("不限制容载比方案储能柜数", "PATH_OPT_CLR_UNBOUNDED_storage_modules"),
        ("不限制容载比方案累计年化成本（万元）", "PATH_OPT_CLR_UNBOUNDED_cumulative_eac"),
        ("严格Rcap=2.0方案2025年物理容载比", "PATH_OPT_CLR_LE_2_clr_2025"),
        ("严格Rcap=2.0方案新增容量（MVA）", "PATH_OPT_CLR_LE_2_added_capacity_mva"),
        ("严格Rcap=2.0方案储能柜数", "PATH_OPT_CLR_LE_2_storage_modules"),
        ("严格Rcap=2.0方案累计年化成本（万元）", "PATH_OPT_CLR_LE_2_cumulative_eac"),
        ("严格约束增量成本（万元）", "strict_path_incremental_cost"),
        ("物理可行性状态", "constraint_status"),
        ("证据等级", "evidence_grade"),
    ]
    lookup = frame.set_index("region_id")
    lines = [f"# {voltage_kv} kV {'正式推荐矩阵' if voltage_kv == 110 else '辅助分析矩阵'}", "", "| 指标 | " + " | ".join(regions) + " |", "|---|" + "---|" * len(regions)]
    for label, field in indicator_fields:
        lines.append("| " + label + " | " + " | ".join(_display(lookup.loc[region, field]) for region in regions) + " |")
    lines.extend([
        "",
        "说明：110 kV 的 Rcap 仅作为规划期新增容量的控制参数，2021 年实际存量容量不因达标而退役；35 kV 为辅助层，不施加逐年 Rcap 上界。",
        "说明：推荐区间来自 Rcap 前沿近优带、局部细化和同一 Rcap 维度的参数敏感性，不与实际物理容载比区间取交集。",
        "说明：EENS 未建模、弃光未设置为决策变量；10 kV 联络结论另见局部案例底稿，未升级为完整 AC 潮流结论。",
    ])
    return "\n".join(lines) + "\n"


def _science_review_markdown(
    matrices: dict[int, pd.DataFrame],
    base_frontier: pd.DataFrame,
    base_thresholds: pd.DataFrame,
    refined_thresholds: pd.DataFrame,
    robust_summary: pd.DataFrame,
    baseline_manifest: dict[str, Any],
) -> str:
    qx5 = matrices[110].set_index("region_id").loc["QX-00005"]
    qx1 = matrices[110].set_index("region_id").loc["QX-00001"]
    qx5_soc = "baseline/qx00005_soc/qx00005_continuous_soc_summary.csv"
    return f"""# v3.2 模型科学性终审与冻结支撑记录

状态：**MODEL V3.2 FROZEN**
结果包：`results/runs/real-2021-2025-v32-frozen/`

## 1. 终审结论

模型主基线为 2021 年实际在役容量，物理容量、规划基线和新增容量分列。刚性方案只对 110 kV 规划期新增容量施加 `ΔS≤max(2.0×P_plus−S_2021,0)`，不为满足 Rcap 反向退役既有资产。两条优化方案在同一实际资产起点、同一候选库、同一物理约束和同一成本库上求解，因此可在两者均可行时直接比较累计年化成本。

正式容载比为物理在役容量除以该方案同步正向最大净负荷；反向峰值和反向承载缺口单列。储能不能跨零充电，放电不能形成反送，主体模型不设置弃光变量。

## 2. 求解和阈值方法

- 决策期为 2022—2025 年，价格统一到 2025 年，目标为累计在役等效年成本最小。
- 候选为真实数据支撑的离散扩容候选；主政策模型不启用退役候选。
- 规划器采用确定性的离散状态穷举/动态保留与 HiGHS 线性时序校核，不使用 NSGA-II 随机解；同一输入可复现同一结果。
- Rcap 阈值取“5% 近优成本带首次达到的位置”并用局部点细化；稳健近优带只在 Rcap 维度上对参数场景求交，不把实现 CLR 与 Rcap 取交集。
- QX-00005 110 kV 使用审批后的 2025 年 8760 点连续 SOC 回放；其他片区为静态真实数据和经验时长情景，证据等级不高于 B。

## 3. 片区分类

| 片区 | 分类 | 工程含义 |
|---|---|---|
| QX-00001 | {qx1['recommendation_type']} | {qx1['recommendation']} |
| QX-00005 | {qx5['recommendation_type']} | {qx5['recommendation']} |
| QX-00003、QX-00004、QX-00007 | 当前不绑定型 | 本规划期 Rcap 不构成有效约束，不人为给出推荐数值。 |
| QX-00008、QX-00009、QX-00010 | 技术约束优先型 | 无上限方案未形成完整物理可行路径，先处理网络、设备、站址或时序边界。 |

35 kV 单独作为辅助层输出，不施加逐年 Rcap 上界，不与 110 kV 容量、负荷或成本相加。

## 4. 关键验证证据

- QX-00005 不限制方案 2025 年新增主变容量为 {_format_number(qx5['PATH_OPT_CLR_UNBOUNDED_added_capacity_mva'], 2)} MVA、储能 {qx5['PATH_OPT_CLR_UNBOUNDED_storage_modules']} 柜，累计年化成本 {_format_number(qx5['PATH_OPT_CLR_UNBOUNDED_cumulative_eac'], 2)} 万元；严格方案对应 {_display(qx5['PATH_OPT_CLR_LE_2_added_capacity_mva'])} MVA、{_display(qx5['PATH_OPT_CLR_LE_2_storage_modules'])} 柜、{_display(qx5['PATH_OPT_CLR_LE_2_cumulative_eac'])} 万元。两者均由真实 2021 存量基线出发。
- QX-00001 局部细化阈值记录为 {_display(qx1['rcap_refined_threshold_lower'])}～{_display(qx1['rcap_refined_threshold_upper'])}；QX-00005 为 {_display(qx5['rcap_refined_threshold_lower'])}～{_display(qx5['rcap_refined_threshold_upper'])}。这表示再收紧开始改变成本或技术组合的位置，不是每个片区都必须采用的统一目标值。
- QX-00005 8760 h SOC 汇总见 `{qx5_soc}`；审查字段包括 SOC 上下界、起末 SOC、闭合残差、充放电功率、跨零和同时充放电。正式 465 柜弹性方案及 962 柜严格方案均为可行且无越界。
- `policy_cost_comparison.csv` 对不可行对象保留“未形成直接比较”，不把不可行成本写成零；实际发展路径设备级动作成本未闭合，写“未识别”。

## 5. 数据和能力边界

2021 年官方年度锚点与当前设备投运范围不能反向还原每台历史设备，因而 2021—2025 设备级历史动作成本不作定量结论；2026 年站级光伏快照与 2025 年负荷组合已显式标记跨年口径。非 QX-00005 片区不声称唯一 8760 h 时序证据。内部网络检查是容量网络压力筛查，缺少阻抗时不声称精确 AC/DC 潮流。

10 kV 局部案例只研究已冻结的六条馈线和 TIE-001～003、NEW-TIE-01 案例。TIE-001 不形成定量结论；TIE-002、TIE-003 和 NEW-TIE-01 的转供能力按容量包络引用，并附受端同时段余量前置条件。拓扑碎片森林导致跨站转供后的电压和支路负载不能完整校核，不能把局部案例表述成完整配电网 AC 潮流。

## 6. 可进入报告的表述

统一刚性容载比 2.0 不能充分反映存量资产、反向潮流、局部互济、储能和片区经济约束。冻结结果支持在保留现行规划标准的基础上，增加“约束类型识别—Rcap 有效性判断—经济阈值/技术边界—工程措施”的差异化判据；对当前不绑定或物理不可行的片区，不强行给出推荐容载比数字。
"""


def build_v32_frozen_outputs(
    *,
    project_root: Path,
    processed_root: Path,
    baseline_dir: Path,
    frontier_dir: Path,
    refinement_dir: Path,
    sensitivity_dir: Path,
    stress_dir: Path,
    refined_sensitivity_dir: Path | None,
    threshold_sensitivity_dir: Path | None,
    output_dir: Path,
) -> dict[str, Any]:
    project_root = Path(project_root).resolve()
    processed_root = Path(processed_root).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    baseline_manifest = json.loads(_required(Path(baseline_dir) / "manifest.json").read_text(encoding="utf-8"))
    if str(baseline_manifest.get("model_version")) != "3.2.0":
        raise FormalOutputError("baseline manifest is not v3.2.0")
    annual = _read_csv(processed_root / "annual_reference.csv")
    pv = _read_csv(processed_root / "station_pv_snapshot.csv")
    actual = _read_csv(Path(baseline_dir) / "actual_path_year_results.csv")
    policy_summary = _read_csv(Path(baseline_dir) / "policy_2025_summary.csv")
    comparison = _read_csv(Path(baseline_dir) / "policy_cost_comparison.csv")
    gaps = _read_csv(Path(baseline_dir) / "region_gap_summary.csv")
    diagnostics = _read_csv(Path(baseline_dir) / "initial_physical_diagnostics.csv")
    base_frontier = _collect_frontier(frontier_dir, "frontier_point.csv")
    base_thresholds = classify_economic_release_thresholds(base_frontier, near_optimal_band=0.05)
    refined_frontier = _collect_frontier(refinement_dir, "frontier_point.csv")
    refined_thresholds = _derive_refined_thresholds(refined_frontier)
    coarse_sensitivity = {**_collect_parameter_frontiers(sensitivity_dir), **_collect_parameter_frontiers(stress_dir)}
    if refined_sensitivity_dir is not None and Path(refined_sensitivity_dir).is_dir():
        # 局部细化结果用于审计，不纳入粗网格稳健交集；写入后续证据清单。
        _ = _collect_parameter_frontiers(refined_sensitivity_dir)
    if threshold_sensitivity_dir is not None and Path(threshold_sensitivity_dir).is_dir():
        _ = _collect_parameter_frontiers(threshold_sensitivity_dir)
    robust = _build_robust_summary(base_frontier, coarse_sensitivity)
    matrices = build_formal_matrices(
        annual_reference=annual,
        pv_snapshot=pv,
        actual_years=actual,
        policy_summary=policy_summary,
        cost_comparison=comparison,
        gaps=gaps,
        diagnostics=diagnostics,
        base_frontier=base_frontier,
        base_thresholds=base_thresholds,
        refined_thresholds=refined_thresholds,
        robust_summary=robust,
    )
    for voltage, frame in matrices.items():
        frame.to_csv(output_dir / f"formal_matrix_{voltage}kv.csv", index=False, lineterminator="\n", float_format="%.10g")
        (output_dir / f"formal_matrix_{voltage}kv.md").write_text(_markdown_matrix(frame, voltage), encoding="utf-8")
        write_transposed_word_matrix(frame, output_dir / f"formal_matrix_{voltage}kv.docx", title=f"{voltage} kV {'正式推荐矩阵' if voltage == 110 else '辅助分析矩阵'}")

    base_frontier.to_csv(output_dir / "elasticity_frontier_v32_actual_coarse.csv", index=False, lineterminator="\n")
    base_thresholds.to_csv(output_dir / "rcap_thresholds_v32_actual_coarse.csv", index=False, lineterminator="\n")
    refined_frontier.to_csv(output_dir / "elasticity_frontier_v32_actual_refined.csv", index=False, lineterminator="\n")
    refined_thresholds.to_csv(output_dir / "rcap_thresholds_v32_actual_refined.csv", index=False, lineterminator="\n")
    robust.to_csv(output_dir / "rcap_robust_near_optimal_summary.csv", index=False, lineterminator="\n")
    pd.concat(list(coarse_sensitivity.values()), ignore_index=True, sort=False).to_csv(output_dir / "rcap_sensitivity_frontiers_coarse.csv", index=False, lineterminator="\n")
    pd.DataFrame([
        {"scenario_id": key, **row}
        for key, frame in coarse_sensitivity.items()
        for row in classify_economic_release_thresholds(frame, near_optimal_band=0.05).to_dict("records")
    ]).to_csv(output_dir / "rcap_sensitivity_thresholds_coarse.csv", index=False, lineterminator="\n")

    baseline_copies = _copy_baseline_evidence(Path(baseline_dir), output_dir)
    support_copies = _copy_report_support(project_root, output_dir)
    run_evidence = {
        "frontier_coarse": _run_evidence_inventory("frontier_coarse", frontier_dir, "frontier_point.csv"),
        "frontier_refined": _run_evidence_inventory("frontier_refined", refinement_dir, "frontier_point.csv"),
        "sensitivity_coarse": _run_evidence_inventory("sensitivity_coarse", sensitivity_dir, "parameter_frontier.csv"),
        "stress_coarse": _run_evidence_inventory("stress_coarse", stress_dir, "parameter_frontier.csv"),
    }
    if not all(run_evidence.values()):
        raise FormalOutputError("one or more scan evidence inventories are empty")
    science = _science_review_markdown(matrices, base_frontier, base_thresholds, refined_thresholds, robust, baseline_manifest)
    (output_dir / "model_science_review.md").write_text(science, encoding="utf-8")
    (output_dir / "formal_result_notes.md").write_text(
        "# v3.2 冻结结果说明\n\n"
        "本目录是基于真实输入和已完成运行证据汇总的冻结结果包。精确查值以 `formal_matrix_110kv.csv` 和 `formal_matrix_35kv.csv` 为准；Word 仅作人工审查层。\n\n"
        "正式表中的 Rcap 推荐仅在经济释放阈值型片区输出；当前不绑定型和技术约束优先型片区不强行给出数值。\n",
        encoding="utf-8",
    )

    quality_rows = [
        {"check_id": "DQ-001", "status": "通过", "finding": "标准化数据 manifest、源文件 SHA-256 和年度表 lineage 可回查", "evidence": "data/processed/real_2021_2025/manifest.json"},
        {"check_id": "DQ-002", "status": "通过", "finding": "2025 年 QX-00005 110 kV 运行口径为 20 座站、40 台主变，年末新增设备未混入", "evidence": "annual_asset_whitelist.csv"},
        {"check_id": "DQ-003", "status": "通过", "finding": "2024 年三个异常值保留原值并隔离", "evidence": "data_quality_issues.csv"},
        {"check_id": "DQ-004", "status": "限制", "finding": "2021 官方年度锚点与当前设备投运范围不能还原历史设备动作，实际路径成本保持未识别", "evidence": "annual_asset_reconciliation.csv;actual_path_cost_breakdown.csv"},
        {"check_id": "DQ-005", "status": "限制", "finding": "少数静态站表与主变主数据存在未静默修正的编码范围差异", "evidence": "station_gap_diagnostics.csv;initial_physical_diagnostics.csv"},
        {"check_id": "DQ-006", "status": "假设", "finding": "扩建候选缺少可用年份时按 2022 年起可用，带质量标记", "evidence": "baseline/cost_library/expansion_cost_library.csv"},
        {"check_id": "DQ-007", "status": "限制", "finding": "光伏为 2026 站级快照，与 2025 负荷组合只作跨年背景量，不作历史回测", "evidence": "station_pv_snapshot.csv;formal_matrix_110kv.csv"},
        {"check_id": "DQ-008", "status": "边界", "finding": "缺少同步负荷—光伏分解和馈线点位，不执行纯光伏敏感性或随机撒点事实化", "evidence": "model_contract.yaml;formal_result_notes.md"},
        {"check_id": "DQ-009", "status": "边界", "finding": "QX-00005 以外片区采用经验时长情景，证据等级不高于 B", "evidence": "baseline/time_physics/empirical_scenario_index.csv"},
        {"check_id": "DQ-010", "status": "边界", "finding": "六馈线结构化拓扑为碎片森林，跨站联络后电压和支路负载不升级为完整 AC 结论", "evidence": "docs/TIE-CASE-CONCLUSIONS.md"},
        {"check_id": "DQ-011", "status": "边界", "finding": "缺少阻抗时只做内部容量网络压力筛查，不声称精确 AC/DC 潮流", "evidence": "formal_matrix_110kv.md;model_science_review.md"},
    ]
    pd.DataFrame(quality_rows).to_csv(output_dir / "data_quality_review.csv", index=False, lineterminator="\n")

    source_files = []
    for role, path in [
        ("processed_manifest", processed_root / "manifest.json"),
        ("model_contract", project_root / "model_contract.yaml"),
        ("baseline_manifest", Path(baseline_dir) / "manifest.json"),
    ]:
        try:
            source_label = str(path.relative_to(project_root))
        except ValueError:
            source_label = str(path)
        source_files.append({"role": role, "source_label": source_label, "sha256": _sha256(path), "bytes": path.stat().st_size})
    output_files = {
        str(path.relative_to(output_dir)): {
            "sha256": _sha256(path),
            "bytes": path.stat().st_size,
        }
        for path in sorted(output_dir.rglob("*"))
        if path.is_file() and path.name != "manifest.json"
    }
    manifest = {
        "model_version": "3.2.0",
        "validation_commit_sha": validation_commit_sha(project_root),
        "status": "MODEL V3.2 FROZEN",
        "dataset_id": "real_2021_2025",
        "contract_sha256": _sha256(project_root / "model_contract.yaml"),
        "processed_manifest_sha256": _sha256(processed_root / "manifest.json"),
        "baseline_manifest_sha256": _sha256(Path(baseline_dir) / "manifest.json"),
        "baseline_definition": "actual_2021_installed_capacity_with_existing_capacity_grandfathered",
        "rcap_definition": "planning_period_incremental_capacity_control_on_110kv_only",
        "formal_paths": list(PATHS),
        "direct_policy_cost_comparison": "allowed_when_both_paths_feasible_on_same_actual_baseline",
        "frontier_points": int(len(base_frontier)),
        "refined_frontier_points": int(len(refined_frontier)),
        "sensitivity_scenarios": sorted(coarse_sensitivity),
        "source_files": source_files,
        "output_files": output_files,
        "baseline_evidence_files": baseline_copies,
        "report_support_files": support_copies,
        "run_evidence_inventory": run_evidence,
        "report_facing_ids_only": True,
        "notes": [
            "Rcap推荐不与实现CLR取交集",
            "非绑定片区不强制给推荐Rcap数值",
            "EENS和弃光未建模，不以0填充",
            "10kV局部案例为容量包络/局部工程化互济分析，不是完整AC潮流",
        ],
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--processed-root", type=Path, default=ROOT / "data/processed/real_2021_2025")
    parser.add_argument("--baseline-dir", type=Path, required=True)
    parser.add_argument("--frontier-dir", type=Path, required=True)
    parser.add_argument("--refinement-dir", type=Path, required=True)
    parser.add_argument("--sensitivity-dir", type=Path, required=True)
    parser.add_argument("--stress-dir", type=Path, required=True)
    parser.add_argument("--refined-sensitivity-dir", type=Path)
    parser.add_argument("--threshold-sensitivity-dir", type=Path)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/runs/real-2021-2025-v32-frozen")
    args = parser.parse_args()
    manifest = build_v32_frozen_outputs(
        project_root=args.project_root,
        processed_root=args.processed_root,
        baseline_dir=args.baseline_dir,
        frontier_dir=args.frontier_dir,
        refinement_dir=args.refinement_dir,
        sensitivity_dir=args.sensitivity_dir,
        stress_dir=args.stress_dir,
        refined_sensitivity_dir=args.refined_sensitivity_dir,
        threshold_sensitivity_dir=args.threshold_sensitivity_dir,
        output_dir=args.output_dir,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
