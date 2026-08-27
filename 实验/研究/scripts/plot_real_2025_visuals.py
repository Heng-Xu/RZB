#!/usr/bin/env python3
"""Render the auditable real_2025 visualization review package."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.real_visuals import RUN_ID, render_real_2025_visuals


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate real_2025 matrix review visuals")
    parser.add_argument("--run-dir", type=Path, default=ROOT / "results" / "runs" / RUN_ID)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "real_2025_visuals")
    args = parser.parse_args()
    manifest = render_real_2025_visuals(args.run_dir, args.output_dir)
    print("REAL_2025 VISUAL PACKAGE PASS")
    print(f"output_dir={args.output_dir}")
    print(f"rows={manifest['row_count']}; voltage_levels={manifest['voltage_levels']}")
    print(f"output_files={len(manifest['output_files'])}")
    print(json.dumps(manifest["chart_contracts"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
