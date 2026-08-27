"""提交并校验 v3 跨年时序映射审批副本。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from src.annual_asset_scope import approve_real_timeseries_mapping


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a project-owner approval copy for the v3 2022-2026 transformer mapping."
    )
    parser.add_argument("--processed-root", type=Path, required=True)
    parser.add_argument("--approval-file", type=Path, required=True)
    parser.add_argument("--output-file", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = approve_real_timeseries_mapping(
        args.processed_root,
        args.approval_file,
        output_path=args.output_file,
    )
    summary = {
        "processed_root": str(args.processed_root.resolve()),
        "approval_file": str(args.approval_file.resolve()),
        "output_file": str((args.output_file or args.processed_root / "timeseries_mapping_approval.csv").resolve()),
        "approval_status_counts": {
            str(key): int(value)
            for key, value in result["approval"]["approval_status"].value_counts().sort_index().items()
        },
        "formal_use_allowed": bool(result["formal_use_allowed"]),
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
