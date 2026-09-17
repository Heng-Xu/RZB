#!/usr/bin/env python3
"""检查10 kV高光伏跨站转移模型的数据契约与已知边界。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("实验/研究/data/tuomin/10kv_case/data"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("实验/研究/results/10kv_reverse_transfer_case/data_contract_check.json"),
    )
    args = parser.parse_args()

    data = args.data_dir
    ties = pd.read_csv(data / "tie_master.csv", encoding="utf-8-sig")
    paths = pd.read_csv(data / "key_tie_path_parameter_impact.csv", encoding="utf-8-sig")
    inj = pd.read_csv(data / "injection_summary.csv", encoding="utf-8-sig")
    feeders = pd.read_csv(data / "feeder_master.csv", encoding="utf-8-sig")
    stations = pd.read_csv(data / "station_boundary_2025.csv", encoding="utf-8-sig")
    switches = pd.read_csv(data / "switch_master.csv", encoding="utf-8-sig")
    nodes = pd.read_csv(data / "node_master.csv", encoding="utf-8-sig", nrows=1)

    issues: list[str] = []
    warnings: list[str] = []

    tie = ties.loc[ties["tie_id"] == "TIE-002"]
    if len(tie) != 1:
        issues.append("TIE-002 must have exactly one master record")
        tie_row = None
    else:
        tie_row = tie.iloc[0]
        if str(tie_row["normal_state"]).upper() != "OPEN":
            issues.append("TIE-002 normal state must be OPEN")
        if str(tie_row["confidence"]).upper() != "HIGH":
            issues.append("TIE-002 confidence must be HIGH")
        if str(tie_row["endpoint_resolution"]) != "EXACT_CANONICAL/EXACT_CANONICAL":
            issues.append("TIE-002 both endpoints must be exact canonical nodes")
        if str(tie_row["requires_revalidation"]).upper() not in {"NO", "FALSE"}:
            issues.append("TIE-002 must not require topology revalidation")

    tie_paths = paths.loc[paths["tie_id"] == "TIE-002"]
    if len(tie_paths) != 2:
        issues.append("TIE-002 must have exactly two source-to-tie path records")
    else:
        if not (tie_paths["path_status"] == "READY").all():
            issues.append("TIE-002 both paths must be READY")
        if not (tie_paths["parameter_grade"] == "B+").all():
            warnings.append("TIE-002 path parameter grade is not uniformly B+")

    dnan = inj.loc[inj["feeder_id"] == "PZXL-00092"]
    hpao = inj.loc[inj["feeder_id"] == "PZXL-00161"]
    if len(dnan) != 1 or len(hpao) != 1:
        issues.append("dnan/hpao injection summary row missing or duplicated")
    else:
        dnan_row = dnan.iloc[0]
        hpao_row = hpao.iloc[0]
        if str(dnan_row["pv_status"]) != "OUTPUT_ANCHOR_ONLY":
            issues.append("dnan PV must remain OUTPUT_ANCHOR_ONLY; do not reinterpret as installed capacity")
        if "7.34" not in str(dnan_row["pv_total_or_anchor"]):
            issues.append("dnan 7.34 MW real PV output anchor missing")
        if str(hpao_row["pv_status"]) != "CONFIRMED_ZERO":
            issues.append("hpao PV status must remain CONFIRMED_ZERO in current dataset")

    station_dj = stations.loc[stations["station_id"] == "BDZ-00027"]
    station_hw = stations.loc[stations["station_id"] == "BDZ-00048"]
    if len(station_dj) != 1 or len(station_hw) != 1:
        issues.append("station boundary records for DJ/HW missing or duplicated")
    else:
        if float(station_dj.iloc[0]["2025_annual_min_load_mw"]) >= 0:
            issues.append("DJ 2025 annual minimum should show reverse power")
        if float(station_hw.iloc[0]["2025_annual_min_load_mw"]) >= 0:
            issues.append("HW 2025 annual minimum should show reverse power")

    blocking_text = switches["blocking_final"].astype(str).str.upper()
    donor_switches = switches.loc[
        (switches["feeder_id"] == "PZXL-00092")
        & (switches["device_type"] == "分段开关")
        & blocking_text.isin({"NO", "FALSE", "0"})
    ]
    verified_selective_section_switch_count = int(len(donor_switches))
    selective_section_transfer_ready = verified_selective_section_switch_count > 0
    if not selective_section_transfer_ready:
        warnings.append(
            "dnan has no final-unblocked verified sectional switch in current switch master; "
            "formal current case must stay at whole-feeder boundary transfer or treat a new/verified switch as an engineering action"
        )

    node_columns = {str(c).lower() for c in nodes.columns}
    has_gis = any(c in node_columns for c in {"lat", "latitude", "lon", "long", "longitude", "x", "y"})
    if not has_gis:
        warnings.append(
            "node master has no GIS coordinates; exact new-tie route length/corridor optimization is not data-ready"
        )

    feeder_map_ok = (
        set(feeders.loc[feeders["station_id"] == "BDZ-00027", "feeder_id"])
        >= {"PZXL-00092", "PZXL-00097", "PZXL-00099"}
        and set(feeders.loc[feeders["station_id"] == "BDZ-00048", "feeder_id"])
        >= {"PZXL-00154", "PZXL-00161", "PZXL-00173"}
    )
    if not feeder_map_ok:
        issues.append("six-feeder station mapping is incomplete")

    result = {
        "passed": not issues,
        "issues": issues,
        "warnings": warnings,
        "tie002_topology_ready": len(tie_paths) == 2 and not issues,
        "whole_feeder_boundary_transfer_ready": len(tie_paths) == 2 and not issues,
        "selective_section_transfer_ready": selective_section_transfer_ready,
        "verified_dnan_sectional_switch_count": verified_selective_section_switch_count,
        "exact_new_tie_route_ready": has_gis,
        "current_model_scope": (
            "EXISTING_TIE_WHOLE_FEEDER_BOUNDARY_RECONFIGURATION_PLUS_NEW_TIE_CAPACITY_AND_RECEIVER_FEEDER_SCREEN"
        ),
        "data_semantics": {
            "dnan_pv_7_34_mw": "REAL_OUTPUT_PEAK_ANCHOR_NOT_COMPLETE_INSTALLED_CAPACITY",
            "station_minima": "INDEPENDENT_ANNUAL_STRESS_ANCHORS_NOT_SYNCHRONOUS_PAIR",
            "node_loads": "PLANNING_SEEDS_NOT_SYNCHRONOUS_MEASUREMENTS",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
