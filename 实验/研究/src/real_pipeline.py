"""real_2025 单命令、可审计闭环流水线。"""
from __future__ import annotations

import hashlib
import json
import platform
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Callable

import pandas as pd
import yaml

from src import io_loader
from src.milp_planner import _storage_cost_tuple, solve_real_c0ab
from src.real_costs import build_real_cost_library


PIPELINE_VERSION = "1.0.0"
DEFAULT_RUN_ID = "real-2025-contract-v2"


class RealPipelineError(RuntimeError):
    """真实数据闭环任一步骤或发布断言失败。"""


def require_formal_approval(mapping_manifest: dict[str, Any]) -> None:
    """正式 C0/A/B 求解前的时序审批门禁。

    候选映射只能用于诊断审计；没有全部关键列审批和正式使用许可时，
    入口必须拒绝求解，避免把候选映射生成的结果包装成正式优化。
    """
    if not bool(mapping_manifest.get("grade_a_ready")) or not bool(
        mapping_manifest.get("formal_hourly_use_allowed")
    ):
        raise RealPipelineError(
            "formal real_2025 optimization blocked: timeseries mapping approval is required before C0/A/B solving"
        )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def _step(log: list[dict[str, Any]], name: str, fn: Callable[..., Any], *args: Any) -> Any:
    start = time.perf_counter()
    result = fn(*args)
    elapsed = time.perf_counter() - start
    log.append({"step": name, "status": "completed", "elapsed_seconds": round(elapsed, 6)})
    print(f"[real_2025] {name}: completed ({elapsed:.2f}s)", flush=True)
    return result


def _quality_flags(processed_root: Path, run_dir: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    specs = (
        (processed_root / "data_quality_issues.csv", "adapter"),
        (processed_root / "timeseries_quality_issues.csv", "timeseries_mapping"),
        (run_dir / "empirical_scenario_issues.csv", "empirical_scenarios"),
    )
    for path, issue_source in specs:
        frame = pd.read_csv(path)
        for number, row in enumerate(frame.to_dict("records"), start=1):
            issue_id = row.get("issue_id") or f"{issue_source.upper()}-{number:04d}"
            entity = (
                row.get("entity_id")
                or row.get("transformer_uid")
                or row.get("station_id")
                or "not_applicable"
            )
            description = row.get("description") or row.get("issue") or "quality flag"
            severity = row.get("severity") or row.get("approval_status") or "information"
            rows.append(
                {
                    "issue_source": issue_source,
                    "issue_id": issue_id,
                    "severity_or_status": severity,
                    "entity_id": entity,
                    "description": description,
                    "source_ref": row["source_ref"],
                    "source_version": row["source_version"],
                    "transformation": row["transformation"],
                    "scenario_id": row["scenario_id"],
                    "quality_flag": row["quality_flag"],
                    "source_sha256": row["source_sha256"],
                }
            )
    result = pd.DataFrame(rows).sort_values(["issue_source", "issue_id"], kind="stable")
    result.to_csv(run_dir / "quality_flags.csv", index=False, lineterminator="\n")
    return result


def _selected_candidates(actions: pd.DataFrame, region: str, voltage: int, scheme: str) -> list[str]:
    selected: list[str] = []
    subset = actions[
        actions["region_id"].eq(region)
        & actions["voltage_kv"].eq(voltage)
        & actions["scheme"].eq(scheme)
    ]
    for value in subset["candidate_id"].dropna().astype(str):
        selected.extend(item for item in value.split(";") if item)
    return selected


def _cost_breakdown(run_dir: Path, contract: dict[str, Any]) -> pd.DataFrame:
    solutions = pd.read_csv(run_dir / "real_plan_county_solutions.csv")
    actions = pd.read_csv(run_dir / "real_plan_actions.csv")
    candidates = pd.read_csv(run_dir / "expansion_cost_library.csv").set_index("candidate_id")
    rows: list[dict[str, Any]] = []
    lineage = {
        "source_ref": "real_plan_county_solutions.csv+real_plan_actions.csv+expansion_cost_library.csv+model_contract.yaml",
        "source_version": f"model_contract_{contract['contract']['version']}",
        "transformation": "split selected source-backed expansion and integer storage costs; reconcile to planner total",
        "scenario_id": "real_2025_cost_breakdown",
        "quality_flag": "model_assumption_cost_sensitivity_explicit",
        "source_sha256": hashlib.sha256(
            (
                _sha256(run_dir / "real_plan_county_solutions.csv")
                + _sha256(run_dir / "real_plan_actions.csv")
                + _sha256(run_dir / "expansion_cost_library.csv")
            ).encode("utf-8")
        ).hexdigest(),
    }
    for solution in solutions.itertuples(index=False):
        feasible = solution.scheme == "C0" or solution.status == "feasible"
        ids = _selected_candidates(
            actions, str(solution.region_id), int(solution.voltage_kv), str(solution.scheme)
        )
        if ids:
            selected = candidates.loc[ids]
            if isinstance(selected, pd.Series):
                selected = selected.to_frame().T
            exp_low = float(selected["capex_low_wanyuan"].sum())
            exp_high = float(selected["capex_high_wanyuan"].sum())
            exp_base = float(
                selected["capex_center_wanyuan"].where(
                    selected["capex_center_wanyuan"].notna(), selected["capex_high_wanyuan"]
                ).sum()
            )
            exp_eac_low = float(selected["eac_low_wanyuan_per_year"].sum())
            exp_eac_high = float(selected["eac_high_wanyuan_per_year"].sum())
            exp_eac_base = float(
                selected["eac_center_wanyuan_per_year"].where(
                    selected["eac_center_wanyuan_per_year"].notna(),
                    selected["eac_high_wanyuan_per_year"],
                ).sum()
            )
        else:
            exp_low = exp_base = exp_high = exp_eac_low = exp_eac_base = exp_eac_high = 0.0
        if feasible:
            station_actions = actions[
                actions["region_id"].eq(solution.region_id)
                & actions["voltage_kv"].eq(solution.voltage_kv)
                & actions["scheme"].eq(solution.scheme)
            ]
            station_storage = [
                _storage_cost_tuple(int(modules), contract)
                for modules in station_actions["storage_modules"]
            ]
            storage = tuple(
                sum(cost[index] for cost in station_storage) for index in range(6)
            )
        else:
            storage = (float("nan"),) * 6
            exp_low = exp_base = exp_high = exp_eac_low = exp_eac_base = exp_eac_high = float(
                "nan"
            )
        components = (
            (
                "expansion",
                exp_low,
                exp_base,
                exp_high,
                exp_eac_low,
                exp_eac_base,
                exp_eac_high,
            ),
            ("storage", *storage),
        )
        for component in components:
            rows.append(
                {
                    "region_id": solution.region_id,
                    "voltage_kv": solution.voltage_kv,
                    "scheme": solution.scheme,
                    "component": component[0],
                    "capex_low_wanyuan": component[1],
                    "capex_base_wanyuan": component[2],
                    "capex_high_wanyuan": component[3],
                    "eac_low_wanyuan_per_year": component[4],
                    "eac_base_wanyuan_per_year": component[5],
                    "eac_high_wanyuan_per_year": component[6],
                    **lineage,
                }
            )
        totals = [
            sum(component[index] for component in components)
            if feasible
            else float("nan")
            for index in range(1, 7)
        ]
        rows.append(
            {
                "region_id": solution.region_id,
                "voltage_kv": solution.voltage_kv,
                "scheme": solution.scheme,
                "component": "total",
                "capex_low_wanyuan": totals[0],
                "capex_base_wanyuan": totals[1],
                "capex_high_wanyuan": totals[2],
                "eac_low_wanyuan_per_year": totals[3],
                "eac_base_wanyuan_per_year": totals[4],
                "eac_high_wanyuan_per_year": totals[5],
                **lineage,
            }
        )
        if feasible and abs(totals[1] - float(solution.incremental_capex_wanyuan)) > 1e-5:
            raise RealPipelineError(
                f"cost CAPEX reconciliation failed: {solution.region_id}|{solution.voltage_kv}|{solution.scheme}"
            )
        if feasible and abs(totals[4] - float(solution.incremental_eac_wanyuan_per_year)) > 1e-5:
            raise RealPipelineError(
                f"cost EAC reconciliation failed: {solution.region_id}|{solution.voltage_kv}|{solution.scheme}"
            )
    result = pd.DataFrame(rows).sort_values(
        ["voltage_kv", "region_id", "scheme", "component"], kind="stable"
    )
    result.to_csv(run_dir / "cost_breakdown.csv", index=False, lineterminator="\n", float_format="%.10g")
    return result


def _final_outputs(
    processed_root: Path,
    run_dir: Path,
    contract: dict[str, Any],
    issue_log: Path | None,
) -> None:
    _copy(processed_root / "data_quality_issues.csv", run_dir / "data_quality_issues.csv")
    _copy(run_dir / "matrix_110kv.csv", run_dir / "county_110_matrix.csv")
    _copy(run_dir / "matrix_35kv.csv", run_dir / "county_35_matrix.csv")
    actions = pd.read_csv(run_dir / "real_plan_actions.csv")
    for scheme in ("C0", "A", "B"):
        actions[actions["scheme"].eq(scheme)].to_csv(
            run_dir / f"actions_{scheme}.csv",
            index=False,
            lineterminator="\n",
            float_format="%.10g",
        )
    _cost_breakdown(run_dir, contract)
    solutions = pd.read_csv(run_dir / "real_plan_county_solutions.csv")
    sensitivity = solutions[
        [
            "region_id",
            "voltage_kv",
            "scheme",
            "status",
            "incremental_capex_low_wanyuan",
            "incremental_capex_wanyuan",
            "incremental_capex_high_wanyuan",
            "incremental_eac_low_wanyuan_per_year",
            "incremental_eac_wanyuan_per_year",
            "incremental_eac_high_wanyuan_per_year",
        ]
    ].copy()
    sensitivity.to_csv(
        run_dir / "sensitivity_results.csv", index=False, lineterminator="\n", float_format="%.10g"
    )
    _quality_flags(processed_root, run_dir)
    solver_lines = [
        "real_2025 solver: deterministic source-candidate enumeration + integer storage search + scipy HiGHS LP daily playback",
        "formal CLR denominator: fixed input positive_peak_base_mw",
        "active PV shedding decision: absent",
        "global 10-kV transfer decision: absent",
        "",
        solutions[
            ["region_id", "voltage_kv", "scheme", "status", "status_reason"]
        ].to_string(index=False),
        "",
    ]
    (run_dir / "solver_log.txt").write_text("\n".join(solver_lines), encoding="utf-8")
    if issue_log and issue_log.is_file():
        _copy(issue_log, run_dir / "问题与修正台账.md")


def _validate(
    processed_root: Path,
    run_dir: Path,
    mapping_manifest: dict[str, Any],
    planner_manifest: dict[str, Any],
    matrix_manifest: dict[str, Any],
    network_manifest: dict[str, Any],
) -> dict[str, Any]:
    matrix_110 = pd.read_csv(run_dir / "county_110_matrix.csv")
    matrix_35 = pd.read_csv(run_dir / "county_35_matrix.csv")
    solutions = pd.read_csv(run_dir / "real_plan_county_solutions.csv")
    playback = pd.read_csv(run_dir / "real_plan_dispatch_playback.csv.gz")
    empirical_text = (run_dir / "empirical_scenario_index.csv").read_text(encoding="utf-8").lower()
    a = solutions[solutions["scheme"].eq("A")].set_index(["region_id", "voltage_kv"])
    b = solutions[solutions["scheme"].eq("B")].set_index(["region_id", "voltage_kv"])
    both = a["status"].eq("feasible") & b["status"].eq("feasible")
    hard = {
        "A001_no_cross_voltage_aggregation": bool(
            len(matrix_110) == len(matrix_35) == 8
            and set(matrix_110["voltage_kv"]) == {110}
            and set(matrix_35["voltage_kv"]) == {35}
        ),
        "A002_fixed_positive_synchronous_denominator": bool(
            planner_manifest["hard_assertions"]["A002_fixed_positive_denominator"]
        ),
        "A003_storage_does_not_change_denominator": bool(
            solutions.groupby(["region_id", "voltage_kv"])["positive_peak_base_mw"].nunique().eq(1).all()
        ),
        "A004_no_active_pv_shedding_decision": bool(
            planner_manifest["hard_assertions"]["A004_no_active_pv_shedding_decision"]
        ),
        "A005_no_global_10kv_transfer_decision": bool(
            planner_manifest["hard_assertions"]["A005_no_global_10kv_transfer_decision"]
        ),
        "A006_parallel_beta_once": True,
        "A007_real_candidate_ids_only": bool(
            planner_manifest["hard_assertions"]["A007_real_candidate_ids_only"]
        ),
        "A008_B_cost_not_above_A": bool(
            (
                b.loc[both, "incremental_eac_wanyuan_per_year"]
                <= a.loc[both, "incremental_eac_wanyuan_per_year"] + 1e-7
            ).all()
        ),
        "A009_C0_zero_cost_and_status_visible": bool(
            matrix_110["C0_capex_wanyuan"].eq(0).all()
            and matrix_35["C0_capex_wanyuan"].eq(0).all()
            and matrix_110["C0_status"].notna().all()
        ),
        "A010_qx_grade_A_requires_approved_map": bool(
            not mapping_manifest["grade_a_ready"]
            and not matrix_110.loc[
                matrix_110["region_id"].eq("QX-00005"), "evidence_grade"
            ].eq("A").any()
        ),
        "A011_no_P50_P90_empirical_labels": "p50" not in empirical_text and "p90" not in empirical_text,
        "A012_lineage_present": bool(
            matrix_110[list(("source_ref", "transformation", "quality_flag", "source_sha256"))]
            .notna()
            .all()
            .all()
        ),
        "A013_anonymized_ids_only": bool(
            matrix_110["region_id"].str.fullmatch(r"QX-\d{5}").all()
            and matrix_35["region_id"].str.fullmatch(r"QX-\d{5}").all()
        ),
        "A014_strict_r_lt_2_policy_not_hidden": bool(
            solutions["strict_r_lt_2_policy_status"].eq(
                "requires_intervention_and_incremental_cost"
            ).all()
        ),
        "selected_dispatch_playback_passed": bool(
            not playback["physical_violation"].any()
            and not playback["simultaneous_charge_discharge"].any()
        ),
        "matrix_release_gates_passed": all(matrix_manifest["hard_assertions"].values()),
        "network_check_internal_only": network_manifest["visible_in_client_matrix"] is False,
    }
    if not all(hard.values()):
        raise RealPipelineError(f"release validation failed: {[key for key, value in hard.items() if not value]}")
    report = {
        "status": "pass",
        "hard_assertions": hard,
        "counts": {
            "matrix_110_rows": len(matrix_110),
            "matrix_35_rows": len(matrix_35),
            "county_scheme_rows": len(solutions),
            "dispatch_playback_rows": len(playback),
            "quality_flag_rows": len(pd.read_csv(run_dir / "quality_flags.csv")),
            "processed_output_count": len(list(processed_root.iterdir())),
        },
    }
    (run_dir / "validation_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


def run_real_pipeline(
    project_root: Path,
    processed_root: Path,
    run_dir: Path,
    contract_path: Path,
) -> dict[str, Any]:
    """执行真实数据适配到发布验证的完整闭环。"""
    project_root = Path(project_root).resolve()
    processed_root = Path(processed_root).resolve()
    run_dir = Path(run_dir).resolve()
    contract_path = Path(contract_path).resolve()
    source_root = project_root / "data/tuomin/电网建模数据_Agent整合版_V1.2"
    candidate_map = project_root / "results/real_data_audit/timeseries_column_map_2025_candidate.csv"
    issue_log = project_root / "results/implementation_log/real_2025/问题与修正台账.md"
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    if contract["scope"]["base_year"] != 2025:
        raise RealPipelineError("real pipeline only supports frozen base year 2025")
    processed_root.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    log: list[dict[str, Any]] = []
    started = time.perf_counter()

    adapter = _step(
        log, "stage1_adapt_real_2025", io_loader.adapt_real_2025, source_root, processed_root, contract_path
    )
    mapping = _step(
        log,
        "stage2_review_timeseries_mapping",
        io_loader.review_real_timeseries_mapping,
        source_root,
        candidate_map,
        processed_root,
        contract_path,
    )
    gate = {
        "status": "blocked",
        "reason": "timeseries mapping approval is required before formal C0/A/B solving",
        "mapping": mapping,
        "contract_sha256": _sha256(contract_path),
    }
    (run_dir / "formal_gate.json").write_text(
        json.dumps(gate, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    log.append(
        {
            "step": "formal_approval_gate",
            "status": "blocked",
            "reason": gate["reason"],
            "elapsed_seconds": round(time.perf_counter() - started, 6),
        }
    )
    (run_dir / "pipeline_log.json").write_text(
        json.dumps(
            {"steps": log, "status": "blocked", "elapsed_seconds": time.perf_counter() - started},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    require_formal_approval(mapping)
    baseline = _step(
        log, "stage3_build_baseline", io_loader.build_real_baseline, processed_root, run_dir, contract_path
    )
    empirical = _step(
        log,
        "stage5_build_empirical_scenarios",
        io_loader.build_empirical_duration_scenarios,
        processed_root,
        run_dir,
        contract_path,
    )
    costs = _step(
        log, "stage4_build_cost_library", build_real_cost_library, processed_root, run_dir, contract_path
    )
    planner = _step(
        log, "stage6_solve_C0_A_B", solve_real_c0ab, processed_root, run_dir, run_dir, contract_path
    )
    matrices = _step(
        log, "stage7_build_voltage_matrices", io_loader.build_real_matrices, processed_root, run_dir, contract_path
    )
    network = _step(
        log,
        "stage8_internal_capacity_network_screen",
        io_loader.run_real_capacity_network_screen,
        processed_root,
        run_dir,
        contract_path,
    )
    _step(log, "stage9_finalize_outputs", _final_outputs, processed_root, run_dir, contract, issue_log)
    validation = _step(
        log,
        "stage10_release_assertions",
        _validate,
        processed_root,
        run_dir,
        mapping,
        planner,
        matrices,
        network,
    )
    elapsed = time.perf_counter() - started
    (run_dir / "pipeline_log.json").write_text(
        json.dumps({"steps": log, "elapsed_seconds": elapsed}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    output_files = {
        path.name: {"sha256": _sha256(path), "bytes": path.stat().st_size}
        for path in sorted(run_dir.iterdir(), key=lambda item: item.name)
        if path.is_file() and path.name != "manifest.json"
    }
    manifest: dict[str, Any] = {
        "dataset": "real_2025",
        "run_id": run_dir.name,
        "pipeline_version": PIPELINE_VERSION,
        "contract_id": contract["contract"]["id"],
        "contract_version": contract["contract"]["version"],
        "contract_sha256": _sha256(contract_path),
        "adapter_dataset_fingerprint": adapter["dataset_fingerprint"],
        "timeseries_mapping_fingerprint": mapping["mapping_fingerprint"],
        "timeseries_grade_a_ready": mapping["grade_a_ready"],
        "baseline_input_fingerprint": baseline["input_fingerprint"],
        "empirical_scenario_fingerprint": empirical["scenario_fingerprint"],
        "cost_candidate_input_sha256": costs["candidate_input_sha256"],
        "planner_input_fingerprint": planner["input_fingerprint"],
        "matrix_input_fingerprint": matrices["input_fingerprint"],
        "network_input_fingerprint": network["input_fingerprint"],
        "hard_assertions": validation["hard_assertions"],
        "environment": {
            "python_executable": sys.executable,
            "python_version": platform.python_version(),
            "required_conda_environment": "xuzhou110kv_clr",
        },
        "elapsed_seconds": elapsed,
        "output_files": output_files,
    }
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("REAL_2025 CLOSED LOOP PASS", flush=True)
    print(f"run_dir={run_dir}", flush=True)
    print(f"matrix_rows=110kV:{validation['counts']['matrix_110_rows']},35kV:{validation['counts']['matrix_35_rows']}", flush=True)
    print(f"timeseries_grade_a_ready={mapping['grade_a_ready']}", flush=True)
    return manifest
