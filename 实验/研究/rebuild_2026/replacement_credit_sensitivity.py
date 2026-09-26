"""Test dependence on unpriced recovery value of displaced transformers."""

import argparse
from pathlib import Path

from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .joint_lifecycle_optimizer import cost_factors, load_inputs, solve_layer


LAYER = ("QX-00005", 35)
CREDIT_FRACTIONS = (0.0, 0.25, 0.5, 0.75, 1.0)


def run_sensitivity() -> list[dict]:
    inputs = load_inputs()
    factors = cost_factors()
    rows = []
    for credit in CREDIT_FRACTIONS:
        for cap in (2.0, 2.4, 4.0):
            stations, years, _, summary = solve_layer(
                LAYER, *inputs, factors, cap, False,
                replaced_unit_credit_fraction=credit)
            rows.append({
                "study_region_id": LAYER[0], "voltage_kv": LAYER[1],
                "hypothetical_displaced_unit_credit_fraction": credit,
                "credit_scope": "hypothetical_fraction_of_old_transformer_rated_MVA_unit_cost_at_replacement",
                "scan_cap": cap,
                "objective_npv_10k_cny": summary["objective_npv_10k_cny"],
                "max_actual_clr": summary["max_actual_clr"],
                "selected_capacity_2025_mva": years[-1]["selected_capacity_mva"],
                "transformer_capex_10k_cny": round(sum(r["transformer_capex_10k_cny"] for r in stations), 6),
                "status": "sensitivity_only_no_verified_recovery_price_or_reuse_path",
            })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="被替换主变回收抵扣假设敏感性")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    rows = run_sensitivity()
    write_csv(rows, args.output_dir / "replacement_credit_sensitivity_35kv.csv")
    print(f"输出 {len(rows)} 条主变回收抵扣反事实情景")


if __name__ == "__main__":
    main()
