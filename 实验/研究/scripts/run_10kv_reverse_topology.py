#!/usr/bin/env python3
"""输出TIE-002高光伏跨站转移的规划级供电边界拓扑状态。"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.feeder_10kv_reverse_topology import boundary_reconfiguration_trace


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("实验/研究/results/10kv_reverse_transfer_case"),
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    trace = boundary_reconfiguration_trace()
    trace.to_csv(
        args.output_dir / "boundary_reconfiguration_topology.csv",
        index=False,
        encoding="utf-8-sig",
    )
    print(trace.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
