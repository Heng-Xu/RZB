"""Separate CLR-cap effects from the Pizhou 110 kV tie-option effect."""

import argparse
from pathlib import Path

from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .joint_lifecycle_optimizer import run_model


def diagnose() -> list[dict]:
    cases = (
        ("rigid_with_ties", True, True),
        ("rigid_without_ties", True, False),
        ("elastic_without_ties", False, False),
        ("elastic_with_ties_counterfactual", False, True),
    )
    rows = []
    for name, rigid, ties in cases:
        _, years, transfers, summaries = run_model(
            rigid=rigid, tie_allowed=ties,
            caps={("QX-00005", 35): 4.0, ("QX-00005", 110): 4.0,
                  ("QX-00007", 110): 3.0},
        )
        for summary in summaries:
            key = summary["study_region_id"], summary["voltage_kv"]
            matching = [year for year in years if (year["study_region_id"], year["voltage_kv"]) == key]
            rows.append({
                "diagnostic_case": name, "study_region_id": key[0], "voltage_kv": key[1],
                "clr_cap": summary["clr_cap"], "ties_allowed": ties and key == ("QX-00005", 110),
                "objective_npv_10k_cny": summary["objective_npv_10k_cny"],
                "max_actual_clr": summary["max_actual_clr"],
                "max_clr_minus_rigid_cap": round(summary["max_actual_clr"] - 2.0, 9),
                "tie_transfer_event_count": sum(
                    (move["study_region_id"], move["voltage_kv"]) == key for move in transfers),
                "actual_clr_by_year": ";".join(f"{year['year']}:{year['actual_clr']}" for year in matching),
                "status": "counterfactual_same_measure_scope_for_diagnosis_not_formal_elastic_scheme"
                if name == "elastic_with_ties_counterfactual" else "formal_or_scope_control",
            })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="容载比上限与 10 kV 联络措施影响分解")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    rows = diagnose()
    write_csv(rows, args.output_dir / "measure_scope_diagnostic.csv")
    print(f"输出 {len(rows)} 条同措施范围对照及反事实诊断结果")


if __name__ == "__main__":
    main()
