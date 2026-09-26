"""把上限变化与是否允许联络拆开，检验同措施边界的成本单调性。"""

import argparse
from pathlib import Path

from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .joint_lifecycle_optimizer import PIZHOU_110, cost_factors, load_inputs, solve_layer


CAPS = (2.0, 2.1, 2.4, 4.0)


def reconcile() -> tuple[list[dict], list[dict]]:
    baseline, scene, durations, peaks, catalog, coefficients = load_inputs()
    factors = cost_factors()
    layer_rows, year_rows = [], []
    for ties in (False, True):
        for cap in CAPS:
            stations, years, transfers, layer = solve_layer(
                PIZHOU_110, baseline, scene, durations, peaks, catalog,
                coefficients, factors, cap, rigid=False, tie_allowed=ties,
            )
            layer_rows.append({
                "study_region_id": PIZHOU_110[0], "voltage_kv": PIZHOU_110[1],
                "clr_cap": cap, "ties_allowed": ties,
                "measure_scope": layer["measure_scope"],
                "objective_npv_10k_cny": layer["objective_npv_10k_cny"],
                "max_actual_clr": layer["max_actual_clr"],
                "transfer_event_count": len(transfers),
                "max_year_forward_transfer_mw": round(max(
                    (sum(t["transfer_mw"] for t in transfers
                         if t["year"] == y and t["scenario"] == "forward")
                     for y in (2022, 2023, 2024, 2025)), default=0), 6),
            })
            for row in years:
                year_rows.append({
                    "study_region_id": PIZHOU_110[0], "voltage_kv": PIZHOU_110[1],
                    "year": row["year"], "clr_cap": cap, "ties_allowed": ties,
                    "measure_scope": layer["measure_scope"],
                    "actual_clr": row["actual_clr"],
                    "selected_capacity_mva": row["selected_capacity_mva"],
                    "year_commissioned_event_lifecycle_npv_10k_cny": row["year_lifecycle_npv_10k_cny"],
                    "forward_transfer_mw": round(sum(
                        t["transfer_mw"] for t in transfers
                        if t["year"] == row["year"] and t["scenario"] == "forward"), 6),
                    "reverse_transfer_mw": round(sum(
                        t["transfer_mw"] for t in transfers
                        if t["year"] == row["year"] and t["scenario"] == "reverse"), 6),
                    "new_line_built": row["line_built"],
                })
    for ties in (False, True):
        costs = [r["objective_npv_10k_cny"] for r in layer_rows if r["ties_allowed"] == ties]
        if any(later > earlier + 1e-5 for earlier, later in zip(costs, costs[1:])):
            raise ValueError(f"同措施边界 ties={ties} 下放宽上限却增加成本")
    return layer_rows, year_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="核对联络因素与容载比上限因素")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    layers, years = reconcile()
    write_csv(layers, args.output_dir / "joint_lifecycle_scope_reconciliation.csv")
    write_csv(years, args.output_dir / "joint_lifecycle_scope_reconciliation_years.csv")
    for row in layers:
        print(row)


if __name__ == "__main__":
    main()
