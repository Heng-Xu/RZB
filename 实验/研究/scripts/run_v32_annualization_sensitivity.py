#!/usr/bin/env python3
"""运行 v3.2 EAC 年化参数的定向稳健性敏感性。

该层使用冻结契约已登记的年化参数范围，只对 QX-00001/QX-00005 做定向
Rcap 扫描；结果写入独立证据目录，不改写正式冻结主结果。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Sequence

import pandas as pd

from src.v32_annualization import ANNUALIZATION_FIELDS, build_annualization_scenarios
from src.v32_contract import load_v32_contract, validation_commit_sha
from src.v32_frontier_aggregate import build_coarse_recommendations
from src.v32_model import intersect_unique_rcap_point_sets, recommended_rcap_interval
from src.v32_sensitivity import run_v32_parameter_frontier
from src.v32_threshold import classify_economic_release_thresholds


REGIONS = ("QX-00001", "QX-00005")
# 2.0—3.0 粗网格 + 两个核心片区的局部细化点；全部落在 frozen contract
# 的 Rcap 扫描范围内，避免把粗网格分辨率误判为年化参数敏感性。
DEFAULT_RCAP_POINTS = tuple(
    sorted(
        {
            *[round(2.0 + 0.1 * index, 1) for index in range(11)],
            2.15,
            2.16,
            2.17,
            2.171,
            2.172,
            2.18,
            2.35,
            2.36,
            2.359,
            2.360,
            2.37,
        }
    )
)


class V32AnnualizationSensitivityError(ValueError):
    """年化敏感性运行或证据汇总不满足门禁。"""


def build_parser() -> argparse.ArgumentParser:
    contract_root = Path(__file__).resolve().parents[1]
    contract = load_v32_contract(contract_root)
    choices = ["all", *build_annualization_scenarios(contract)]
    parser = argparse.ArgumentParser(
        description="Run targeted EAC annualization sensitivity; output is secondary evidence, not the primary model."
    )
    parser.add_argument("--scenario", choices=choices, default="all")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("results/runs/real-2021-2025-v32-annualization-sensitivity"),
    )
    return parser


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _action_signature(row: pd.Series) -> str:
    def canonical(value: Any) -> str:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return ""
        try:
            number = float(value)
        except (TypeError, ValueError):
            return str(value)
        return f"{number:g}" if math.isfinite(number) else ""

    return "|".join(
        (
            str(row.get("action_types", "none")),
            canonical(row.get("candidate_ids", "")) if row.get("candidate_ids", "") else "",
            canonical(row.get("storage_modules", "")),
            canonical(row.get("capacity_action_delta_mva", "")),
        )
    )


def _aggregate_action_eac(actions: pd.DataFrame) -> pd.DataFrame:
    if actions.empty:
        return pd.DataFrame(
            columns=[
                "scenario_id",
                "rcap",
                "rcap_numeric",
                "region_id",
                "path_id",
                "storage_eac_wanyuan_per_year",
                "expansion_eac_wanyuan_per_year",
                "storage_cumulative_in_service_eac_wanyuan",
                "expansion_cumulative_in_service_eac_wanyuan",
            ]
        )
    frame = actions.copy()
    frame["year"] = pd.to_numeric(frame["year"], errors="raise").astype(int)
    frame["eac_wanyuan_per_year"] = pd.to_numeric(
        frame["eac_wanyuan_per_year"], errors="raise"
    )
    frame["in_service_years"] = 2025 - frame["year"] + 1
    frame["cumulative_in_service_eac_wanyuan"] = (
        frame["eac_wanyuan_per_year"] * frame["in_service_years"]
    )
    frame["measure_family"] = frame["action_type"].astype(str).map(
        lambda value: "storage" if value == "storage" else "expansion"
    )
    group_columns = ["scenario_id", "rcap", "rcap_numeric", "region_id", "path_id"]
    rows: list[dict[str, Any]] = []
    for keys, group in frame.groupby(group_columns, dropna=False, sort=True):
        key_map = dict(zip(group_columns, keys))
        rows.append(
            {
                **key_map,
                "storage_eac_wanyuan_per_year": float(
                    group.loc[group["measure_family"].eq("storage"), "eac_wanyuan_per_year"].sum()
                ),
                "expansion_eac_wanyuan_per_year": float(
                    group.loc[group["measure_family"].eq("expansion"), "eac_wanyuan_per_year"].sum()
                ),
                "storage_cumulative_in_service_eac_wanyuan": float(
                    group.loc[group["measure_family"].eq("storage"), "cumulative_in_service_eac_wanyuan"].sum()
                ),
                "expansion_cumulative_in_service_eac_wanyuan": float(
                    group.loc[group["measure_family"].eq("expansion"), "cumulative_in_service_eac_wanyuan"].sum()
                ),
            }
        )
    return pd.DataFrame(rows)


def _path_costs(
    frontier: pd.DataFrame,
    action_eac: pd.DataFrame,
    *,
    region_id: str,
    rcap: str,
) -> dict[str, Any]:
    row = frontier[
        frontier["region_id"].astype(str).eq(region_id)
        & frontier["rcap"].astype(str).eq(rcap)
    ]
    if row.empty:
        return {
            "storage_cumulative_in_service_eac_wanyuan": 0.0,
            "expansion_cumulative_in_service_eac_wanyuan": 0.0,
        }
    path_id = "PATH_OPT_CLR_UNBOUNDED" if rcap == "unbounded" else "PATH_OPT_CLR_LE_2"
    selected = action_eac[
        action_eac["region_id"].astype(str).eq(region_id)
        & action_eac["rcap"].astype(str).eq(rcap)
        & action_eac["path_id"].astype(str).eq(path_id)
    ]
    return {
        "storage_cumulative_in_service_eac_wanyuan": float(
            selected["storage_cumulative_in_service_eac_wanyuan"].sum()
        ),
        "expansion_cumulative_in_service_eac_wanyuan": float(
            selected["expansion_cumulative_in_service_eac_wanyuan"].sum()
        ),
    }


def _base_reference(project_root: Path) -> dict[str, dict[str, Any]]:
    frozen = Path(project_root) / "results/runs/real-2021-2025-v32-frozen"
    frontier = pd.read_csv(frozen / "elasticity_frontier_v32_actual_coarse.csv")
    refined = pd.read_csv(frozen / "rcap_thresholds_v32_actual_refined.csv")
    robust = pd.read_csv(frozen / "rcap_robust_near_optimal_summary.csv")
    reference: dict[str, dict[str, Any]] = {}
    for region_id in REGIONS:
        unbounded = frontier[
            frontier["region_id"].astype(str).eq(region_id)
            & frontier["rcap"].astype(str).eq("unbounded")
        ].iloc[0]
        threshold = refined[refined["region_id"].astype(str).eq(region_id)].iloc[0]
        robust_row = robust[robust["region_id"].astype(str).eq(region_id)].iloc[0]
        reference[region_id] = {
            "base_unbounded_feasible": bool(unbounded["feasible"]),
            "base_unbounded_measure": _action_signature(unbounded),
            "base_refined_threshold_lower_exclusive": _number(
                threshold["refined_threshold_lower_exclusive"]
            ),
            "base_refined_threshold_upper_inclusive": _number(
                threshold["refined_threshold_upper_inclusive"]
            ),
            "base_robust_lower": _number(robust_row["robust_rcap_lower"]),
        }
    return reference


def classify_annualization_result(
    row: dict[str, Any],
    base: dict[str, Any],
    *,
    threshold_tolerance: float = 0.05,
    robust_lower_tolerance: float = 0.05,
) -> str:
    """按阈值、稳健下限、可行性和措施类型分类年化参数影响。"""
    if bool(row.get("unbounded_feasible")) != bool(base["base_unbounded_feasible"]):
        return "SENSITIVE"
    if str(row.get("unbounded_measure")) != str(base["base_unbounded_measure"]):
        return "SENSITIVE"
    threshold_values = [
        (_number(row.get("threshold_lower")), base["base_refined_threshold_lower_exclusive"]),
        (_number(row.get("threshold_upper")), base["base_refined_threshold_upper_inclusive"]),
    ]
    if any(
        current is not None
        and reference is not None
        and abs(current - reference) > threshold_tolerance
        for current, reference in threshold_values
    ):
        return "SENSITIVE"
    current_lower = _number(row.get("near_optimal_lower"))
    base_lower = base["base_robust_lower"]
    if current_lower is not None and base_lower is not None and abs(current_lower - base_lower) > robust_lower_tolerance:
        return "SENSITIVE"
    if any(
        current is not None
        and reference is not None
        and abs(current - reference) > 1e-12
        for current, reference in threshold_values
    ) or (
        current_lower is not None
        and base_lower is not None
        and abs(current_lower - base_lower) > 1e-12
    ):
        return "WEAKLY_SENSITIVE"
    return "ROBUST"


def _summarize_scenario(
    frontier: pd.DataFrame,
    actions: pd.DataFrame,
    *,
    scenario_id: str,
    annualization: dict[str, Any],
    base_reference: dict[str, dict[str, Any]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    thresholds = classify_economic_release_thresholds(frontier, near_optimal_band=0.05)
    recommendations = build_coarse_recommendations(frontier, near_optimal_band=0.05)
    action_eac = _aggregate_action_eac(actions)
    threshold_map = thresholds.set_index("region_id").to_dict("index")
    recommendation_map = recommendations.set_index("region_id").to_dict("index")
    rows: list[dict[str, Any]] = []
    for region_id in REGIONS:
        unbounded = frontier[
            frontier["region_id"].astype(str).eq(region_id)
            & frontier["rcap"].astype(str).eq("unbounded")
        ].iloc[0]
        strict = frontier[
            frontier["region_id"].astype(str).eq(region_id)
            & frontier["rcap"].astype(str).eq("2.0")
        ]
        strict_row = strict.iloc[0] if not strict.empty else None
        threshold = threshold_map[region_id]
        recommendation = recommendation_map[region_id]
        unbounded_costs = _path_costs(frontier, action_eac, region_id=region_id, rcap="unbounded")
        strict_costs = _path_costs(frontier, action_eac, region_id=region_id, rcap="2.0")
        row: dict[str, Any] = {
            "scenario_id": scenario_id,
            "region_id": region_id,
            **annualization,
            "unbounded_feasible": bool(unbounded["feasible"]),
            "unbounded_status": str(unbounded["status"]),
            "unbounded_measure": _action_signature(unbounded),
            "unbounded_storage_modules": _number(unbounded.get("storage_modules")),
            "unbounded_capacity_action_delta_mva": _number(unbounded.get("capacity_action_delta_mva")),
            "strict_rcap_2_0_feasible": None if strict_row is None else bool(strict_row["feasible"]),
            "strict_rcap_2_0_status": None if strict_row is None else str(strict_row["status"]),
            "strict_rcap_2_0_measure": None if strict_row is None else _action_signature(strict_row),
            "strict_rcap_2_0_storage_modules": None if strict_row is None else _number(strict_row.get("storage_modules")),
            "threshold_status": threshold["threshold_status"],
            "threshold_lower": _number(threshold["coarse_release_threshold_lower"]),
            "threshold_upper": _number(threshold["coarse_release_threshold_upper"]),
            "near_optimal_lower": _number(recommendation["coarse_rcap_low"]),
            "near_optimal_measure_flip": bool(recommendation["measure_flip"]),
            **{f"unbounded_{key}": value for key, value in unbounded_costs.items()},
            **{f"strict_rcap_2_0_{key}": value for key, value in strict_costs.items()},
        }
        # 跨场景稳健下限在全部年化场景运行完成后计算；此处先保留待判定状态。
        row["classification"] = "PENDING_ROBUST_INTERSECTION"
        rows.append(row)
    summary = pd.DataFrame(rows)
    return summary, thresholds.assign(scenario_id=scenario_id), action_eac


def _annualization_robust_summary(
    project_root: Path,
    frontiers: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, dict[str, dict[str, float | None]]]:
    frozen = Path(project_root) / "results/runs/real-2021-2025-v32-frozen"
    base = pd.read_csv(frozen / "elasticity_frontier_v32_actual_coarse.csv")
    formal_robust = pd.read_csv(frozen / "rcap_robust_near_optimal_summary.csv")
    rows: list[dict[str, Any]] = []
    robust_map: dict[str, dict[str, float | None]] = {}
    for region_id in REGIONS:
        point_sets: list[set[float]] = []
        labels: list[str] = []
        formal_row = formal_robust[formal_robust["region_id"].astype(str).eq(region_id)].iloc[0]
        formal_points = {
            round(float(value), 10)
            for value in str(formal_row["robust_rcap_points"]).split(";")
            if value and value.lower() != "nan"
        }
        point_sets.append(formal_points)
        labels.append(
            f"formal_17_scenarios:{','.join(f'{point:g}' for point in sorted(formal_points))}"
        )
        for scenario_id, frontier in frontiers.items():
            result = recommended_rcap_interval(
                frontier,
                region_id=region_id,
                near_optimal_band=0.05,
            )
            points = {round(float(value), 10) for value in result["rcap_points"]}
            point_sets.append(points)
            labels.append(f"{scenario_id}:{','.join(f'{point:g}' for point in sorted(points))}")
        robust_points = intersect_unique_rcap_point_sets(point_sets) if all(point_sets) else []
        scan_high = float(pd.to_numeric(base["rcap_numeric"], errors="coerce").max())
        upper_identified = bool(robust_points and max(robust_points) < scan_high - 1e-9)
        robust_lower = min(robust_points) if robust_points else None
        robust_map[region_id] = {
            "robust_lower": robust_lower,
            "robust_upper": max(robust_points) if robust_points and upper_identified else None,
        }
        rows.append(
            {
                "region_id": region_id,
                "near_optimal_band": 0.05,
                "formal_sensitivity_scenario_count": 17,
                "annualization_scenario_count": len(frontiers),
                "robust_rcap_points": ";".join(f"{point:g}" for point in robust_points),
                "robust_rcap_lower": robust_lower,
                "robust_rcap_upper": max(robust_points) if robust_points and upper_identified else math.nan,
                "scan_upper": scan_high,
                "upper_identified_within_scan": upper_identified,
                "scenario_point_sets": " | ".join(labels),
                "interpretation": (
                    "年化参数场景与主基准的共同近优带向扫描上界延伸，未识别上界"
                    if robust_points
                    else "年化参数场景与主基准未形成共同近优 Rcap 点集"
                ),
            }
        )
    return pd.DataFrame(rows), robust_map


def _write_manifest(
    output_root: Path,
    files: Sequence[Path],
    *,
    contract: dict[str, Any],
    scenarios: dict[str, dict[str, Any]],
    generated_from_commit_sha: str,
) -> dict[str, Any]:
    manifest = {
        "schema_version": "v3.2.annualization-sensitivity.v1",
        "model_version": contract["contract"]["version"],
        "status": "secondary_annualization_sensitivity_not_primary_client_result",
        "primary_model_unchanged": True,
        "region_ids": list(REGIONS),
        "scenario_count": len(scenarios),
        "scenario_ids": list(scenarios),
        "annualization_base": {
            field: contract["costs"]["annualization"][field]
            for field in scenarios[next(iter(scenarios))]
        },
        "annualization_contract_ranges": contract["costs"]["annualization"]["sensitivity"],
        "rcap_points": list(DEFAULT_RCAP_POINTS),
        "near_optimal_band": 0.05,
        "generated_from_commit_sha": generated_from_commit_sha,
        "files": {
            str(path.relative_to(output_root)): {
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
            }
            for path in sorted(files)
        },
    }
    (output_root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def run_annualization_sensitivity(
    project_root: Path,
    *,
    output_root: Path,
    scenario: str = "all",
) -> dict[str, Any]:
    project_root = Path(project_root).resolve()
    output_root = Path(output_root).resolve()
    contract = load_v32_contract(project_root)
    scenarios = build_annualization_scenarios(contract)
    if scenario != "all":
        if scenario not in scenarios:
            raise V32AnnualizationSensitivityError(f"unknown annualization scenario: {scenario}")
        scenarios = {scenario: scenarios[scenario]}
    base_reference = _base_reference(project_root)
    output_root.mkdir(parents=True, exist_ok=True)
    summaries: list[pd.DataFrame] = []
    thresholds: list[pd.DataFrame] = []
    action_eacs: list[pd.DataFrame] = []
    frontiers: dict[str, pd.DataFrame] = {}
    artifact_files: list[Path] = []
    for name, annualization in scenarios.items():
        run_dir = output_root / name
        frontier = run_v32_parameter_frontier(
            project_root,
            project_root / "data/processed/real_2021_2025",
            run_dir,
            cos_phi=0.95,
            reverse_beta=0.80,
            rcap_points=DEFAULT_RCAP_POINTS,
            include_unbounded=True,
            annualization_overrides=annualization,
            scenario_name=name,
            region_ids=REGIONS,
        )
        actions = pd.read_csv(run_dir / "parameter_action_results.csv")
        summary, threshold, action_eac = _summarize_scenario(
            frontier,
            actions,
            scenario_id=name,
            annualization=annualization,
            base_reference=base_reference,
        )
        frontiers[name] = frontier
        summaries.append(summary)
        thresholds.append(threshold)
        action_eacs.append(action_eac)
        artifact_files.extend(
            [
                run_dir / "parameter_frontier.csv",
                run_dir / "parameter_action_results.csv",
                run_dir / "parameter_cost_breakdown.csv",
                run_dir / "scenario_manifest.json",
            ]
        )

    summary_frame = pd.concat(summaries, ignore_index=True, sort=False)
    threshold_frame = pd.concat(thresholds, ignore_index=True, sort=False)
    action_frame = pd.concat(action_eacs, ignore_index=True, sort=False)
    robust_frame, robust_map = _annualization_robust_summary(project_root, frontiers)
    for index, row in summary_frame.iterrows():
        region_id = str(row["region_id"])
        robust_lower = robust_map[region_id]["robust_lower"]
        summary_frame.at[index, "annualization_robust_lower"] = robust_lower
        classification_input = row.to_dict()
        classification_input["near_optimal_lower"] = robust_lower
        summary_frame.at[index, "classification"] = classify_annualization_result(
            classification_input,
            base_reference[region_id],
        )
    summary_path = output_root / "annualization_core_summary.csv"
    threshold_path = output_root / "annualization_thresholds.csv"
    action_path = output_root / "annualization_action_eac.csv"
    classification_path = output_root / "annualization_classification.csv"
    robust_path = output_root / "annualization_robust_summary.csv"
    summary_frame.to_csv(summary_path, index=False, lineterminator="\n", float_format="%.10g")
    threshold_frame.to_csv(threshold_path, index=False, lineterminator="\n", float_format="%.10g")
    action_frame.to_csv(action_path, index=False, lineterminator="\n", float_format="%.10g")
    robust_frame.to_csv(robust_path, index=False, lineterminator="\n", float_format="%.10g")
    classification_columns = [
        "scenario_id",
        "region_id",
        *ANNUALIZATION_FIELDS,
        "classification",
        "threshold_status",
        "threshold_lower",
        "threshold_upper",
        "near_optimal_lower",
        "near_optimal_measure_flip",
        "annualization_robust_lower",
    ]
    summary_frame[classification_columns].to_csv(
        classification_path,
        index=False,
        lineterminator="\n",
        float_format="%.10g",
    )
    artifact_files.extend([summary_path, threshold_path, action_path, classification_path, robust_path])
    manifest = _write_manifest(
        output_root,
        artifact_files,
        contract=contract,
        scenarios=scenarios,
        generated_from_commit_sha=validation_commit_sha(project_root),
    )
    return manifest


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    project_root = Path(__file__).resolve().parents[1]
    manifest = run_annualization_sensitivity(
        project_root,
        output_root=args.output_root,
        scenario=args.scenario,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
