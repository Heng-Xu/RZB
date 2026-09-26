"""Audit whether solved paths can support a transferable CLR recommendation matrix."""

import argparse
import json
from collections import defaultdict
from pathlib import Path

from .baseline_2021 import read_csv
from .hourly_source_profile import OUTPUT_DIR


FEATURES = (
    "source_to_gross_load_ratio_2025_regional_proxy",
    "forward_h95_hours_2025_template",
    "reverse_h95_hours_2025_template",
    "storage_to_transformer_unit_capex_ratio",
    "elastic_cost_to_rigid_cost",
)


def audit(source: Path = OUTPUT_DIR) -> dict:
    rows = []
    for voltage in (35, 110):
        rows.extend(read_csv(source / f"joint_lifecycle_conditional_matrix_{voltage}kv.csv"))
    groups = defaultdict(list)
    for row in rows:
        groups[row["study_region_id"], int(row["voltage_kv"])].append(row)
    variation = []
    for (region, voltage), group in sorted(groups.items()):
        variation.append({
            "study_region_id": region,
            "voltage_kv": voltage,
            "year_count": len(group),
            "feature_unique_values": {key: len({row[key] for row in group}) for key in FEATURES},
            "elastic_actual_clr_unique_values": len({row["elastic_actual_clr"] for row in group}),
        })
    return {
        "row_count": len(rows),
        "independent_region_voltage_groups": len(groups),
        "within_group_variation": variation,
        "requested_predictors_not_present": [
            "annual_or_layer_specific_source_load_ratio",
            "synchronous_annual_reverse_net_extreme_for_2022_to_2024",
            "exogenous_transformer_tie_storage_cost_ratio_scenario_variation",
            "annual_observed_h95_for_2022_to_2024",
        ],
        "outcome_leakage": (
            "elastic_cost_to_rigid_cost is computed after both paths are optimized; "
            "it cannot serve as an input predictor of the recommended CLR"
        ),
        "assessment": "conditional_case_table_only_not_transferable_recommendation_matrix",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="审查条件矩阵的独立样本与指标可识别性")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    result = audit(args.output_dir)
    target = args.output_dir / "matrix_readiness_audit.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{result['row_count']} 行、{result['independent_region_voltage_groups']} 组；"
          f"结论：{result['assessment']}")


if __name__ == "__main__":
    main()
