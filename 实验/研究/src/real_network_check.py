"""110 kV 内部容量网络故障压力筛查。

线路台账没有阻抗，且节点到研究站的正式映射未完全闭合。本模块因此只做
电流限额换算、并行走廊余量、拓扑割边和主变剩余容量检查，不执行或声称
潮流计算。结果只供技术底稿使用，不修改两套县区矩阵。
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np
import pandas as pd
import yaml


SCREEN_VERSION = "1.0.0"
METHOD = "capacity_network_contingency_screen_no_impedance"
LINEAGE_FIELDS = (
    "source_ref",
    "source_version",
    "transformation",
    "scenario_id",
    "quality_flag",
    "source_sha256",
)


class RealNetworkCheckError(ValueError):
    """内部容量网络筛查输入或门禁错误。"""


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
        raise RealNetworkCheckError(f"required internal-check input missing: {path}")
    frame = pd.read_csv(path)
    missing = required - set(frame.columns)
    if missing:
        raise RealNetworkCheckError(f"{filename}: missing columns {sorted(missing)}")
    return frame


def _lineage(source_version: str, source_hash: str, quality: str) -> dict[str, str]:
    return {
        "source_ref": "network_lines_110kv.csv+transformer_master.csv+real_plan_actions.csv+real_plan_dispatch_playback.csv.gz",
        "source_version": source_version,
        "transformation": "internal current-capacity, topology-cut and transformer remaining-capacity contingency screen",
        "scenario_id": "real_2025_internal_capacity_network_screen",
        "quality_flag": quality,
        "source_sha256": source_hash,
    }


def _node_mapping(
    lines: pd.DataFrame,
    master: pd.DataFrame,
    source_version: str,
    source_hash: str,
) -> pd.DataFrame:
    same_region = {
        region: set(group["station_id"].astype(str))
        for region, group in master[master["voltage_kv"].eq(110)].groupby("region_id")
    }
    all_110 = set(master[master["voltage_kv"].eq(110)]["station_id"].astype(str))
    rows: list[dict[str, Any]] = []
    for region, group in lines.groupby("region_id", sort=True):
        nodes = sorted(set(group["from_node"].astype(str)) | set(group["to_node"].astype(str)))
        for node in nodes:
            if node in same_region.get(str(region), set()):
                status = "exact_same_region_110kv_station"
                matched_station = node
            elif node in all_110:
                status = "exact_id_but_region_conflict_requires_review"
                matched_station = node
            else:
                status = "unresolved_nonstudy_or_boundary_candidate"
                matched_station = None
            rows.append(
                {
                    "region_id": str(region),
                    "voltage_kv": 110,
                    "network_node_id": node,
                    "mapping_status": status,
                    "matched_station_id": matched_station,
                    "formal_boundary_node": False,
                    "source_ref": "network_lines_110kv.csv:endpoints+transformer_master.csv",
                    "source_version": source_version,
                    "transformation": "exact anonymized ID comparison only; unresolved nodes are not auto-promoted to boundaries",
                    "scenario_id": "real_2025_internal_network_node_mapping",
                    "quality_flag": "exact_match" if status.startswith("exact_same") else "mapping_review_required",
                    "source_sha256": source_hash,
                }
            )
    return pd.DataFrame(rows)


def _line_screen(
    lines: pd.DataFrame,
    cos_phi: float,
    source_version: str,
    source_hash: str,
) -> pd.DataFrame:
    frame = lines.copy()
    frame["active_power_limit_mw"] = (
        math.sqrt(3.0)
        * frame["voltage_kv"].astype(float)
        * frame["current_limit_a"].astype(float)
        / 1000.0
        * cos_phi
    )
    frame["estimated_peak_flow_mw"] = (
        frame["active_power_limit_mw"] * frame["max_loading_pct"].astype(float) / 100.0
    )
    frame["corridor_key"] = frame.apply(
        lambda row: "|".join(sorted([str(row["from_node"]), str(row["to_node"])])), axis=1
    )
    rows: list[dict[str, Any]] = []
    for region, region_lines in frame.groupby("region_id", sort=True):
        graph = nx.MultiGraph()
        for line in region_lines.itertuples(index=False):
            graph.add_edge(str(line.from_node), str(line.to_node), key=str(line.line_id))
        corridor_capacity = region_lines.groupby("corridor_key")["active_power_limit_mw"].sum()
        corridor_stress = region_lines.groupby("corridor_key")["estimated_peak_flow_mw"].sum()
        for line in region_lines.itertuples(index=False):
            trial = graph.copy()
            trial.remove_edge(str(line.from_node), str(line.to_node), key=str(line.line_id))
            connectivity_cut = not nx.has_path(trial, str(line.from_node), str(line.to_node))
            residual_corridor = float(corridor_capacity[line.corridor_key] - line.active_power_limit_mw)
            corridor_ratio = (
                float(corridor_stress[line.corridor_key] / residual_corridor * 100.0)
                if residual_corridor > 0
                else float("nan")
            )
            incident = region_lines[
                region_lines["from_node"].isin([line.from_node, line.to_node])
                | region_lines["to_node"].isin([line.from_node, line.to_node])
            ]
            incident_residual = float(
                incident.loc[incident["line_id"].ne(line.line_id), "active_power_limit_mw"].sum()
            )
            incident_stress = float(incident["estimated_peak_flow_mw"].sum())
            incident_ratio = (
                incident_stress / incident_residual * 100.0
                if incident_residual > 0
                else float("inf")
            )
            if connectivity_cut:
                status = "critical_connectivity_cut"
            elif pd.notna(corridor_ratio) and corridor_ratio > 100.0:
                status = "parallel_corridor_capacity_pressure"
            elif incident_ratio > 100.0:
                status = "endpoint_incident_capacity_pressure"
            else:
                status = "no_obvious_capacity_pressure"
            rows.append(
                {
                    "region_id": str(region),
                    "voltage_kv": 110,
                    "line_id": str(line.line_id),
                    "from_node": str(line.from_node),
                    "to_node": str(line.to_node),
                    "current_limit_a": float(line.current_limit_a),
                    "active_power_limit_mw": float(line.active_power_limit_mw),
                    "source_max_loading_pct": float(line.max_loading_pct),
                    "estimated_peak_flow_mw": float(line.estimated_peak_flow_mw),
                    "residual_parallel_corridor_mw": residual_corridor,
                    "parallel_corridor_loading_pct_after_outage": corridor_ratio,
                    "endpoint_incident_loading_pct_after_outage": incident_ratio,
                    "connectivity_cut_after_outage": connectivity_cut,
                    "pressure_status": status,
                    "method": METHOD,
                    "scheme_propagation_status": "not_propagated_without_approved_network_node_and_synchronous_flow_mapping",
                    **_lineage(source_version, source_hash, "internal_topology_capacity_screen"),
                }
            )
    return pd.DataFrame(rows)


def _operating_units(
    master: pd.DataFrame,
    station_master: pd.DataFrame,
    region_id: str,
) -> pd.DataFrame:
    result = master[master["region_id"].eq(region_id) & master["voltage_kv"].eq(110)].copy()
    scope = station_master[
        station_master["region_id"].eq(region_id)
        & station_master["voltage_kv"].eq(110)
        & station_master["asset_scope_id"].eq("operating_2025")
    ]
    if not scope.empty:
        result = result[result["station_id"].isin(set(scope["station_id"]))]
    return result


def _transformer_screen(
    master: pd.DataFrame,
    station_master: pd.DataFrame,
    station_baseline: pd.DataFrame,
    actions: pd.DataFrame,
    solutions: pd.DataFrame,
    playback: pd.DataFrame,
    candidate_costs: pd.DataFrame,
    cos_phi: float,
    source_version: str,
    source_hash: str,
) -> pd.DataFrame:
    baseline_lookup = station_baseline[station_baseline["voltage_kv"].eq(110)].set_index(
        ["region_id", "station_id"]
    )
    candidate_capacity = candidate_costs.set_index("candidate_id")["new_capacity_mva"]
    solution_lookup = solutions[solutions["voltage_kv"].eq(110)].set_index(
        ["region_id", "scheme"]
    )
    playback_stress = (
        playback[playback["voltage_kv"].eq(110)]
        .groupby(["region_id", "scheme", "station_id"], as_index=False)
        .agg(
            forward_stress_mw=("net_load_after_mw", lambda values: max(float(values.max()), 0.0)),
            reverse_stress_mw=("net_load_after_mw", lambda values: max(float(-values.min()), 0.0)),
        )
    )
    stress_lookup = playback_stress.set_index(["region_id", "scheme", "station_id"])
    rows: list[dict[str, Any]] = []
    for region_id in sorted(solutions[solutions["voltage_kv"].eq(110)]["region_id"].unique()):
        units_region = _operating_units(master, station_master, str(region_id))
        for scheme in ("C0", "A", "B"):
            county_solution = solution_lookup.loc[(region_id, scheme)]
            scheme_runnable = scheme == "C0" or county_solution["status"] == "feasible"
            scheme_actions = actions[
                actions["region_id"].eq(region_id)
                & actions["voltage_kv"].eq(110)
                & actions["scheme"].eq(scheme)
            ].set_index("station_id")
            for station_id, units in units_region.groupby("station_id", sort=True):
                total = float(units["capacity_mva"].sum())
                existing_largest = float(units["capacity_mva"].max())
                if station_id in scheme_actions.index:
                    action = scheme_actions.loc[station_id]
                    if isinstance(action, pd.DataFrame):
                        action = action.iloc[0]
                    delta = float(action["expansion_delta_mva"])
                    ids = [
                        item
                        for item in str(action.get("candidate_id", "")).split(";")
                        if item and item.lower() != "nan"
                    ]
                    added_largest = max(
                        [float(candidate_capacity.get(item, 0.0)) for item in ids], default=0.0
                    )
                else:
                    delta = 0.0
                    added_largest = 0.0
                total_after = total + delta
                largest_after = max(existing_largest, added_largest)
                remaining = max(total_after - largest_after, 0.0)
                forward_limit = remaining * cos_phi
                reverse_limit = min(0.8 * total_after, remaining) * cos_phi
                if not scheme_runnable:
                    forward_stress = reverse_stress = float("nan")
                    screen_status = "not_run_scheme_infeasible"
                elif scheme == "C0":
                    key = (region_id, station_id)
                    if key not in baseline_lookup.index:
                        forward_stress = reverse_stress = float("nan")
                        screen_status = "missing_station_stress"
                    else:
                        base = baseline_lookup.loc[key]
                        if pd.isna(base["forward_peak_static_mw"]) or pd.isna(
                            base["reverse_peak_static_mw"]
                        ):
                            forward_stress = reverse_stress = float("nan")
                            screen_status = "missing_station_stress"
                        else:
                            forward_stress = max(float(base["forward_peak_static_mw"]), 0.0)
                            reverse_stress = max(float(base["reverse_peak_static_mw"]), 0.0)
                            screen_status = "screened"
                else:
                    key = (region_id, scheme, station_id)
                    if key not in stress_lookup.index:
                        forward_stress = reverse_stress = float("nan")
                        screen_status = "missing_station_stress"
                    else:
                        stress = stress_lookup.loc[key]
                        forward_stress = float(stress["forward_stress_mw"])
                        reverse_stress = float(stress["reverse_stress_mw"])
                        screen_status = "screened"
                for direction, stress, limit in (
                    ("forward", forward_stress, forward_limit),
                    ("reverse", reverse_stress, reverse_limit),
                ):
                    if pd.isna(stress):
                        loading = float("nan")
                    elif limit > 0:
                        loading = stress / limit * 100.0
                    elif stress > 0:
                        loading = float("inf")
                    else:
                        loading = 0.0
                    rows.append(
                        {
                            "region_id": str(region_id),
                            "voltage_kv": 110,
                            "scheme": scheme,
                            "station_id": str(station_id),
                            "direction": direction,
                            "capacity_before_mva": total,
                            "expansion_delta_mva": delta,
                            "largest_unit_after_mva": largest_after,
                            "remaining_capacity_mva": remaining,
                            "stress_mw": stress,
                            "contingency_limit_mw": limit,
                            "loading_pct": loading,
                            "pressure_over_100pct": bool(pd.notna(loading) and loading > 100.0),
                            "screen_status": screen_status,
                            "method": METHOD,
                            **_lineage(source_version, source_hash, "internal_transformer_capacity_screen"),
                        }
                    )
    return pd.DataFrame(rows)


def _summary(
    line_screen: pd.DataFrame,
    node_mapping: pd.DataFrame,
    transformer_screen: pd.DataFrame,
    solutions: pd.DataFrame,
    source_version: str,
    source_hash: str,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for region_id in sorted(solutions[solutions["voltage_kv"].eq(110)]["region_id"].unique()):
        line_region = line_screen[line_screen["region_id"].eq(region_id)]
        node_region = node_mapping[node_mapping["region_id"].eq(region_id)]
        critical_lines = int(line_region["pressure_status"].ne("no_obvious_capacity_pressure").sum())
        unresolved_nodes = int(
            node_region["mapping_status"].ne("exact_same_region_110kv_station").sum()
        )
        for scheme in ("C0", "A", "B"):
            county_solution = solutions[
                solutions["region_id"].eq(region_id)
                & solutions["voltage_kv"].eq(110)
                & solutions["scheme"].eq(scheme)
            ].iloc[0]
            transformer = transformer_screen[
                transformer_screen["region_id"].eq(region_id)
                & transformer_screen["scheme"].eq(scheme)
            ]
            screened = transformer[transformer["screen_status"].eq("screened")]
            maximum = float(screened["loading_pct"].max()) if not screened.empty else float("nan")
            violations = int(screened["pressure_over_100pct"].sum())
            if scheme != "C0" and county_solution["status"] != "feasible":
                status = "scheme_infeasible_transformer_screen_not_run"
            elif unresolved_nodes:
                status = "warning_unresolved_network_node_mapping"
            elif critical_lines or violations:
                status = "capacity_pressure_detected"
            else:
                status = "no_obvious_capacity_pressure"
            rows.append(
                {
                    "region_id": str(region_id),
                    "voltage_kv": 110,
                    "scheme": scheme,
                    "internal_check_status": status,
                    "critical_line_outage_count": critical_lines,
                    "unresolved_network_node_count": unresolved_nodes,
                    "transformer_pressure_row_count": violations,
                    "maximum_transformer_loading_pct": maximum,
                    "visible_in_client_matrix": False,
                    "method": METHOD,
                    **_lineage(source_version, source_hash, "internal_summary_not_client_matrix"),
                }
            )
    return pd.DataFrame(rows)


def _write(path: Path, frame: pd.DataFrame, sort_by: list[str]) -> None:
    missing = set(LINEAGE_FIELDS) - set(frame.columns)
    if missing:
        raise RealNetworkCheckError(f"{path.name}: missing lineage fields {sorted(missing)}")
    frame.sort_values(sort_by, kind="stable").reset_index(drop=True).to_csv(
        path, index=False, lineterminator="\n", float_format="%.10g"
    )


def run_real_capacity_network_screen(
    processed_root: Path,
    run_dir: Path,
    contract_path: Path,
) -> dict[str, Any]:
    """执行线路与主变的内部容量故障压力筛查。"""
    processed_root = Path(processed_root).resolve()
    run_dir = Path(run_dir).resolve()
    contract_path = Path(contract_path).resolve()
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    cos_phi = float(contract["technical_parameters"]["cos_phi"]["baseline"])
    input_paths = [
        processed_root / "network_lines_110kv.csv",
        processed_root / "station_master.csv",
        processed_root / "transformer_master.csv",
        run_dir / "station_baseline.csv",
        run_dir / "real_plan_actions.csv",
        run_dir / "real_plan_county_solutions.csv",
        run_dir / "real_plan_dispatch_playback.csv.gz",
        run_dir / "expansion_cost_library.csv",
        contract_path,
    ]
    lines = _read(
        processed_root,
        "network_lines_110kv.csv",
        {"region_id", "voltage_kv", "line_id", "from_node", "to_node", "current_limit_a", "max_loading_pct"},
    )
    station_master = _read(
        processed_root,
        "station_master.csv",
        {"region_id", "voltage_kv", "station_id", "asset_scope_id"},
    )
    master = _read(
        processed_root,
        "transformer_master.csv",
        {"region_id", "voltage_kv", "station_id", "capacity_mva"},
    )
    station_baseline = _read(
        run_dir,
        "station_baseline.csv",
        {"region_id", "voltage_kv", "station_id", "forward_peak_static_mw", "reverse_peak_static_mw"},
    )
    actions = _read(
        run_dir,
        "real_plan_actions.csv",
        {"region_id", "voltage_kv", "scheme", "station_id", "candidate_id", "expansion_delta_mva"},
    )
    solutions = _read(
        run_dir,
        "real_plan_county_solutions.csv",
        {"region_id", "voltage_kv", "scheme", "status"},
    )
    playback = _read(
        run_dir,
        "real_plan_dispatch_playback.csv.gz",
        {"region_id", "voltage_kv", "scheme", "station_id", "net_load_after_mw"},
    )
    candidate_costs = _read(
        run_dir,
        "expansion_cost_library.csv",
        {"candidate_id", "new_capacity_mva"},
    )
    source_hash = _combined_hash(input_paths)
    source_version = "+".join(sorted(set(lines["source_version"].dropna().astype(str))))
    node_mapping = _node_mapping(lines, master, source_version, source_hash)
    line_result = _line_screen(lines, cos_phi, source_version, source_hash)
    transformer_result = _transformer_screen(
        master,
        station_master,
        station_baseline,
        actions,
        solutions,
        playback,
        candidate_costs,
        cos_phi,
        source_version,
        source_hash,
    )
    summary = _summary(
        line_result,
        node_mapping,
        transformer_result,
        solutions,
        source_version,
        source_hash,
    )
    if len(line_result) != len(lines):
        raise RealNetworkCheckError("every source line must have one outage screen row")
    if len(summary) != 24:
        raise RealNetworkCheckError("internal summary must have 8 regions x 3 schemes")

    frames = {
        "internal_network_node_mapping.csv": (
            node_mapping,
            ["region_id", "network_node_id"],
        ),
        "internal_line_capacity_contingency.csv": (
            line_result,
            ["region_id", "line_id"],
        ),
        "internal_transformer_contingency.csv": (
            transformer_result,
            ["region_id", "scheme", "station_id", "direction"],
        ),
        "internal_capacity_network_summary.csv": (
            summary,
            ["region_id", "scheme"],
        ),
    }
    for filename, (frame, keys) in frames.items():
        _write(run_dir / filename, frame, keys)
    manifest: dict[str, Any] = {
        "screen_version": SCREEN_VERSION,
        "method_claim": METHOD,
        "visible_in_client_matrix": False,
        "contract_sha256": _sha256(contract_path),
        "input_fingerprint": source_hash,
        "node_mapping_gate": "unresolved_nodes_not_assumed_as_boundaries",
        "output_files": {
            filename: {"sha256": _sha256(run_dir / filename), "rows": int(len(frame))}
            for filename, (frame, _keys) in sorted(frames.items())
        },
    }
    (run_dir / "internal_capacity_network_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest
