#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成研究报告使用的核心指标与弹性容载比区间矩阵。"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.report_interval_matrix import build_report_interval_outputs  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/report_reconstruction"),
    )
    args = parser.parse_args()
    outputs = build_report_interval_outputs(ROOT, args.output_dir)
    for name, path in outputs.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
