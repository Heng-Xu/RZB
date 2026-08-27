"""生成项目负责人已批准的 v3 时序映射审批副本。"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


APPROVAL_DATE = "2026-08-14"
APPROVAL_BASIS = "project_owner_approved_candidate_mapping_for_2025_operating_scope"
EXCLUSION_BASIS = "project_owner_excluded_year_end_only_from_2025_operating_scope"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--processed-root", type=Path, required=True)
    parser.add_argument("--output-file", type=Path, required=True)
    args = parser.parse_args()

    source = pd.read_csv(args.processed_root / "timeseries_mapping_approval.csv")
    if len(source) != 58 or set(source["series_column_1_based"]) != set(range(1, 59)):
        raise ValueError("the v3 approval source must contain exactly 58 reviewed columns")
    source["approval_status"] = source["series_column_1_based"].le(56).map(
        {True: "approved", False: "rejected"}
    )
    source["approval_date"] = APPROVAL_DATE
    source["approval_basis"] = source["series_column_1_based"].le(56).map(
        {True: APPROVAL_BASIS, False: EXCLUSION_BASIS}
    )
    source["approval_authority"] = "project_owner"
    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    source.to_csv(args.output_file, index=False, lineterminator="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
