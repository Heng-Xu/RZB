"""Exogenous measure-price scenarios for the Pizhou 35 kV CLR decision."""

import argparse
from pathlib import Path

from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .incremental_cost import replacement_cost_coefficients, storage_capex_10k_cny
from .joint_lifecycle_optimizer import cost_factors, load_inputs, solve_layer


LAYER = ("QX-00005", 35)
CASES = (
    ("base", 1.0, 1.0),
    ("transformer_half", 0.5, 1.0),
    ("transformer_double", 2.0, 1.0),
    ("storage_half", 1.0, 0.5),
    ("storage_double", 1.0, 2.0),
)
CAPS = (2.0, 2.4, 4.0)


def run_sweep() -> tuple[list[dict], list[dict]]:
    inputs = load_inputs()
    factors = cost_factors()
    base_transformer_unit = next(
        float(row["base_coefficient_10k_cny_per_purchased_mva"])
        for row in replacement_cost_coefficients() if row["voltage_kv"] == LAYER[1]
    )
    base_storage_per_mw = storage_capex_10k_cny(10)
    summaries, annual = [], []
    for case, transformer_scale, storage_scale in CASES:
        for cap in CAPS:
            stations, years, _, summary = solve_layer(
                LAYER, *inputs, factors, cap, False,
                transformer_cost_scale=transformer_scale,
                storage_cost_scale=storage_scale,
            )
            ratio = (base_storage_per_mw * storage_scale /
                     (base_transformer_unit * transformer_scale / 0.95))
            common = {
                "case": case, "study_region_id": LAYER[0], "voltage_kv": LAYER[1],
                "scan_cap": cap, "transformer_cost_scale": transformer_scale,
                "storage_cost_scale": storage_scale,
                "storage_to_transformer_unit_capex_ratio": round(ratio, 6),
                "ratio_scope": "10_cabinet_1MW_storage_vs_1MW_active_transformer_purchased_capex_only",
                "scenario_scope": "research_price_sensitivity_not_market_quote",
            }
            summaries.append({**common, "objective_npv_10k_cny": summary["objective_npv_10k_cny"],
                              "max_actual_clr": summary["max_actual_clr"],
                              "station_count": len({row["model_station_id"] for row in stations})})
            annual.extend({**common, "year": row["year"], "actual_clr": row["actual_clr"],
                           "selected_capacity_mva": row["selected_capacity_mva"],
                           "storage_modules_in_service": row["storage_modules_in_service"]}
                          for row in years)
    return summaries, annual


def main() -> None:
    parser = argparse.ArgumentParser(description="邳州 35 kV 措施价格比情景扫描")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    summaries, annual = run_sweep()
    write_csv(summaries, args.output_dir / "cost_ratio_sweep_35kv_summary.csv")
    write_csv(annual, args.output_dir / "cost_ratio_sweep_35kv_annual.csv")
    print(f"{len(CASES)} 个价格情景、{len(summaries)} 次求解、{len(annual)} 条年度路径")


if __name__ == "__main__":
    main()
