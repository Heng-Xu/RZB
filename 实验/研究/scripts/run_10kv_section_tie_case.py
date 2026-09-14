#!/usr/bin/env python3
"""运行 TIE-002 10 kV 分段-联络规划级案例并输出可追溯结果。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.feeder_10kv_section_tie import (
    build_summary,
    equal_section_transfer_demo,
    full_feeder_transfer,
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
    section_demo = equal_section_transfer_demo(case)
    pv_demo = pv_reverse_envelope(case)
    switching = switching_sequence_demo(case)

    summary.to_csv(args.output_dir / "case_summary.csv", index=False, encoding="utf-8-sig")
    section_demo.to_csv(args.output_dir / "section_transfer_demo.csv", index=False, encoding="utf-8-sig")
    pv_demo.to_csv(args.output_dir / "pv_reverse_envelope.csv", index=False, encoding="utf-8-sig")
    switching.to_csv(args.output_dir / "switching_sequence.csv", index=False, encoding="utf-8-sig")

    manifest = {
        "case_id": "10KV_TIE002_SECTION_TIE_PLANNING_DEMO",
        "tie_id": case.tie_id,
        "source_feeder_id": case.source_feeder_id,
        "receiving_feeder_id": case.receiving_feeder_id,
        "source_path_km": case.source_path_km,
        "receiving_path_km": case.receiving_path_km,
        "source_path_limit_mva": case.source_path_limit_mva,
        "receiving_path_limit_mva": case.receiving_path_limit_mva,
        "pf": case.pf,
        "client_control_ratio": case.control_ratio,
        "section_count_for_method_demo": case.section_count,
        "model_scope": "TOPOLOGY_CAPACITY_RECONFIGURATION_PLANNING_LEVEL",
        "not_claimed": [
            "FULL_AC_POWER_FLOW",
            "SHORT_CIRCUIT_CURRENT",
            "RELAY_SETTING_VALIDATION",
            "FIELD_SWITCHING_INSTRUCTION",
            "MEASURED_SECTION_LOADS",
        ],
        "normal_source_path": normal_source_path(case),
        "full_feeder_transfer": full_feeder_transfer(case),
    }
    (args.output_dir / "run_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
