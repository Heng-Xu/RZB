#!/usr/bin/env python3
"""运行 TIE-002 10 kV 分段—联络规划级案例并输出可追溯结果。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.feeder_10kv_section_tie import (
    build_summary,
    equal_section_transfer_demo,
    full_feeder_transfer,
    identify_sections_demo,
    load_case_inputs,
    normal_source_path,
    pv_reverse_envelope,
    switching_sequence_demo,
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
        default=Path("实验/研究/results/10kv_section_tie_case"),
    )
    args = parser.parse_args()

    case = load_case_inputs(args.data_dir, "TIE-002")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    summary = build_summary(case)
    section_id = identify_sections_demo(case)
    section_transfer = equal_section_transfer_demo(case)
    pv_reverse = pv_reverse_envelope(case)
    topology_trace = switching_sequence_demo(case)

    summary.to_csv(args.output_dir / "case_summary.csv", index=False, encoding="utf-8-sig")
    section_id.to_csv(args.output_dir / "section_identification_demo.csv", index=False, encoding="utf-8-sig")
    section_transfer.to_csv(args.output_dir / "section_transfer_demo.csv", index=False, encoding="utf-8-sig")
    pv_reverse.to_csv(args.output_dir / "pv_reverse_envelope.csv", index=False, encoding="utf-8-sig")
    topology_trace.to_csv(args.output_dir / "topology_state_trace.csv", index=False, encoding="utf-8-sig")
    # 兼容旧文件名，但内容已改为真实图连通状态计算结果。
    topology_trace.to_csv(args.output_dir / "switching_sequence.csv", index=False, encoding="utf-8-sig")

    manifest = {
        "case_id": "10KV_TIE002_SECTION_TIE_PLANNING_DEMO_V2",
        "tie_id": case.tie_id,
        "source_feeder_id": case.source_feeder_id,
        "receiving_feeder_id": case.receiving_feeder_id,
        "source_path_km": case.source_path_km,
        "receiving_path_km": case.receiving_path_km,
        "source_path_conductor_limit_mva": case.source_path_conductor_limit_mva,
        "receiving_path_conductor_limit_mva": case.receiving_path_conductor_limit_mva,
        "source_feeder_operating_limit_mva": case.source_feeder_operating_limit_mva,
        "receiving_feeder_operating_limit_mva": case.receiving_feeder_operating_limit_mva,
        "source_effective_limit_mva": case.source_effective_limit_mva,
        "receiving_effective_limit_mva": case.receiving_effective_limit_mva,
        "pf": case.pf,
        "client_reverse_ratio": case.client_reverse_ratio,
        "client_reverse_ratio_scope": "REVERSE_FLOW_ONLY_NOT_GENERIC_FORWARD_LOADING_LIMIT",
        "section_count_for_method_demo": case.section_count,
        "section_evidence": "EQUAL_SECTION_METHOD_DEMO_NOT_MEASURED_SECTION_LOADS",
        "topology_engine": "CONNECTED_COMPONENTS_FROM_SWITCH_STATES",
        "model_scope": "TOPOLOGY_CAPACITY_RECONFIGURATION_PLANNING_LEVEL",
        "not_claimed": [
            "FULL_AC_POWER_FLOW",
            "SHORT_CIRCUIT_CURRENT",
            "RELAY_SETTING_VALIDATION",
            "FIELD_SWITCHING_INSTRUCTION",
            "MEASURED_SECTION_LOADS",
            "SYNCHRONOUS_DUAL_FEEDER_ANNUAL_PEAK",
        ],
        "normal_source_path": normal_source_path(case),
        "full_feeder_transfer": full_feeder_transfer(case),
        "reverse_envelope_note": (
            "80% is applied only to reverse-flow envelope per client requirement; "
            "forward load transfer is checked against effective path capacity."
        ),
    }
    (args.output_dir / "run_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
