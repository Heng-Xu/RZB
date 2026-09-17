#!/usr/bin/env python3
"""运行 TIE-002 高光伏跨站反向功率转移规划案例。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pandas as pd

# 允许从仓库根目录直接执行本脚本，并保持与实验/研究下其他脚本一致的导入语义。
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.feeder_10kv_reverse_transfer import (
    build_case_summary,
    load_reverse_transfer_case,
    receiver_feeder_screen,
    scenario_sweep,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("实验/研究/data/tuomin/10kv_case/data"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("实验/研究/results/10kv_reverse_transfer_case"),
    )
    parser.add_argument("--reverse-ratio", type=float, default=0.80)
    args = parser.parse_args()

    case, feeders, injections, station_pv = load_reverse_transfer_case(
        args.data_dir,
        tie_id="TIE-002",
        client_reverse_ratio=args.reverse_ratio,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)

    sweep = scenario_sweep(case)
    summary = build_case_summary(case, sweep)

    screen_frames: list[pd.DataFrame] = []
    design_scenarios = [
        ("ZERO_LOAD_PV120", 0.0, 1.2),
        ("ZERO_LOAD_PV150", 0.0, 1.5),
        ("S2_LF030_PV150", 0.3, 1.5),
    ]
    for scenario_name, load_factor, pv_scale in design_scenarios:
        row = sweep.loc[
            (sweep["load_factor"].sub(load_factor).abs() < 1e-12)
            & (sweep["pv_scale"].sub(pv_scale).abs() < 1e-12)
        ].iloc[0]
        required = float(row["residual_after_existing_tie_mw"])
        screen = receiver_feeder_screen(
            case,
            feeders,
            injections,
            load_factor=load_factor,
            pv_scale=pv_scale,
            required_transfer_mw=required,
        )
        screen.insert(0, "design_scenario", scenario_name)
        screen_frames.append(screen)

    receiver_screen = pd.concat(screen_frames, ignore_index=True)

    summary.to_csv(args.output_dir / "case_summary.csv", index=False, encoding="utf-8-sig")
    sweep.to_csv(args.output_dir / "tie002_reverse_transfer_sweep.csv", index=False, encoding="utf-8-sig")
    receiver_screen.to_csv(
        args.output_dir / "new_tie_receiver_feeder_screen.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # 保留站级真实高光伏锚点用于边界交叉核对；不把不同时间记录相加为同步潮流。
    station_pv.to_csv(
        args.output_dir / "station_pv_anchor_crosscheck.csv",
        index=False,
        encoding="utf-8-sig",
    )

    manifest = {
        "case_id": "10KV_TIE002_HIGH_PV_CROSS_STATION_REVERSE_TRANSFER_V1",
        "model_core": "HIGH_PV_REVERSE_POWER_CROSS_STATION_BOUNDARY_RECONFIGURATION",
        "tie_id": case.tie_id,
        "donor_station": {
            "id": case.donor_station_id,
            "name": case.donor_station_name,
            "feeder_id": case.donor_feeder_id,
            "annual_min_net_load_2025_mw": case.donor_station_min_net_load_mw,
        },
        "receiver_station": {
            "id": case.receiver_station_id,
            "name": case.receiver_station_name,
            "feeder_id": case.receiver_feeder_id,
            "annual_min_net_load_2025_mw": case.receiver_station_min_net_load_mw,
            "n1_capacity_screen_mva": case.receiver_station_n1_screen_mva,
            "reverse_headroom_screen_mw": case.receiver_station_reverse_headroom_mw,
        },
        "existing_tie": {
            "normal_state": case.tie_normal_state,
            "donor_path_km": case.donor_path_km,
            "receiver_path_km": case.receiver_path_km,
            "donor_effective_limit_mva": case.donor_path_effective_limit_mva,
            "receiver_effective_limit_mva": case.receiver_path_effective_limit_mva,
            "client_reverse_ratio": case.client_reverse_ratio,
            "reverse_transfer_capacity_mw": case.existing_tie_reverse_capacity_mw,
        },
        "pv_anchor": {
            "donor_feeder_peak_output_mw": case.pv_peak_anchor_mw,
            "semantics": "REAL_OUTPUT_PEAK_ANCHOR_NOT_COMPLETE_INSTALLED_CAPACITY",
        },
        "optimization": {
            "level_1_existing_tie": (
                "maximize donor reverse-flow relief using existing TIE-002 while preserving "
                "radial/open-loop operation and respecting source path capacity, receiver "
                "reverse-flow control and receiver station screening headroom"
            ),
            "level_2_new_tie": (
                "if residual export remains, size the minimum additional effective reverse-transfer "
                "capacity and screen alternate receiver feeders; exact route/corridor is not selected "
                "without GIS/CAD distance evidence"
            ),
            "lexicographic_objectives": [
                "MAXIMIZE_DONOR_REVERSE_RELIEF",
                "MAXIMIZE_USE_OF_EXISTING_TIE_MINIMIZE_NEW_BUILD",
                "MINIMIZE_REQUIRED_NEW_TIE_EFFECTIVE_CAPACITY",
            ],
            "decision_variables": [
                "x_existing_mw",
                "x_new_mw",
                "receiver_feeder_candidate",
                "supply_boundary_state_existing_or_new",
            ],
        },
        "constraints": {
            "net_surplus": "x_existing + x_new <= max(PV - local_load, 0)",
            "donor_existing_path": "x_existing <= donor_path_effective_limit",
            "receiver_existing_reverse_control": (
                "x_existing <= client_reverse_ratio * receiver_path_effective_limit"
            ),
            "receiver_station_screen": (
                "x_existing + x_new <= receiver_station_reverse_headroom_screen"
            ),
            "radiality": (
                "existing/new tie transfer requires opening the original supply boundary before "
                "closing the cross-station tie; parallel 110-kV sources through 10-kV network are not allowed"
            ),
        },
        "scenario_semantics": {
            "load_factors": [0.0, 0.3, 0.5, 0.7],
            "pv_scales": [0.8, 0.9, 1.0, 1.2, 1.5],
            "load_factor_zero": "ZERO_LOCAL_LOAD_CONSERVATIVE_EXPORT_UPPER_BOUND",
            "load_factor_nonzero": "PLANNING_PROXY_FROM_FEEDER_ANNUAL_MAX_NOT_SYNCHRONOUS_MEASUREMENT",
            "station_minima": "INDEPENDENT_ANNUAL_STRESS_ANCHORS_NOT_SYNCHRONOUS_DUAL_STATION_FLOW",
        },
        "new_tie_route_boundary": (
            "current data can size required additional transfer capacity and screen receiver feeders; "
            "exact new-line endpoint/corridor/length requires GIS or field/CAD route evidence"
        ),
        "not_claimed": [
            "FAULT_DIAGNOSIS_AS_PRIMARY_OBJECTIVE",
            "FULL_AC_POWER_FLOW",
            "SHORT_CIRCUIT_CURRENT",
            "RELAY_SETTING_VALIDATION",
            "FIELD_SWITCHING_INSTRUCTION",
            "SYNCHRONOUS_DUAL_STATION_POWER_FLOW",
            "EXACT_NEW_LINE_ROUTE_OR_CONSTRUCTION_LENGTH",
        ],
    }
    (args.output_dir / "run_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
