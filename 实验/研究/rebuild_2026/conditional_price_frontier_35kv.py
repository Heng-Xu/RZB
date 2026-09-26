"""Locate the first cost release under explicitly hypothetical measure prices."""

import argparse
from pathlib import Path

from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .joint_lifecycle_optimizer import cost_factors, load_inputs, solve_layer


CASES = (
    ("base", 1.0, 1.0),
    ("transformer_half", 0.5, 1.0),
    ("storage_double", 1.0, 2.0),
)


def frontier() -> list[dict]:
    inputs = load_inputs()
    factors = cost_factors()
    rows = []
    for name, transformer_scale, storage_scale in CASES:
        cache = {}

        def evaluate(cap):
            if cap not in cache:
                stations, years, transfers, summary = solve_layer(
                    ("QX-00005", 35), *inputs, factors, cap, False,
                    transformer_cost_scale=transformer_scale,
                    storage_cost_scale=storage_scale,
                )
                cache[cap] = stations, years, transfers, summary
            return cache[cap]

        rigid_cost = evaluate(2.0)[3]["objective_npv_10k_cny"]
        high_cost = evaluate(2.4)[3]["objective_npv_10k_cny"]
        release = None
        if high_cost < rigid_cost - 1e-4:
            low, high = 2.0, 2.4
            for _ in range(17):  # cap resolution < 0.00001
                middle = (low + high) / 2
                if evaluate(middle)[3]["objective_npv_10k_cny"] < rigid_cost - 1e-4:
                    high = middle
                else:
                    low = middle
            release = high
        for label, cap in (("rigid_cap", 2.0), ("first_cost_release", release), ("relaxed_cap", 2.4)):
            if cap is None:
                continue
            stations, years, transfers, summary = evaluate(cap)
            rows.append({
                "case": name,
                "transformer_cost_scale": transformer_scale,
                "storage_cost_scale": storage_scale,
                "point": label,
                "scan_cap": round(cap, 8),
                "objective_npv_10k_cny": summary["objective_npv_10k_cny"],
                "saving_vs_cap_2_10k_cny": round(rigid_cost - summary["objective_npv_10k_cny"], 6),
                "max_actual_clr": summary["max_actual_clr"],
                "yearly_actual_clr": ";".join(f"{r['year']}:{r['actual_clr']:.9f}" for r in years),
                "yearly_capacity_mva": ";".join(f"{r['year']}:{r['selected_capacity_mva']}" for r in years),
                "yearly_storage_modules": ";".join(f"{r['year']}:{r['storage_modules_in_service']}" for r in years),
                "tie_events": len(transfers),
                "status": "hypothetical_price_static_proxy_not_market_recommendation",
            })
    return rows


def price_thresholds() -> list[dict]:
    """Find the single-factor switch; values are conditional model coefficients."""
    inputs, factors = load_inputs(), cost_factors()

    def saving(transformer_scale: float, storage_scale: float) -> float:
        common = {"transformer_cost_scale": transformer_scale,
                  "storage_cost_scale": storage_scale}
        rigid = solve_layer(("QX-00005", 35), *inputs, factors, 2.0, False, **common)[3]
        relaxed = solve_layer(("QX-00005", 35), *inputs, factors, 2.4, False, **common)[3]
        return rigid["objective_npv_10k_cny"] - relaxed["objective_npv_10k_cny"]

    result = []
    for axis, low, high in (("transformer", 0.5, 1.0), ("storage", 1.0, 2.0)):
        for _ in range(17):
            middle = (low + high) / 2
            delta = saving(middle, 1.0) if axis == "transformer" else saving(1.0, middle)
            if axis == "transformer":
                if delta > 1e-4:
                    low = middle
                else:
                    high = middle
            elif delta > 1e-4:
                high = middle
            else:
                low = middle
        result.append({
            "price_axis": axis,
            "first_positive_saving_scale_approx": round(low if axis == "transformer" else high, 8),
            "bracket_lower_scale": round(low, 8),
            "bracket_upper_scale": round(high, 8),
            "bracket_width": high - low,
            "saving_tolerance_10k_cny": 1e-4,
            "status": "single_factor_hypothetical_price_threshold_static_proxy",
        })
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    rows = frontier()
    write_csv(rows, args.output_dir / "conditional_price_frontier_35kv.csv")
    write_csv(price_thresholds(), args.output_dir / "conditional_price_thresholds_35kv.csv")
    for row in rows:
        if row["point"] == "first_cost_release":
            print(row["case"], row["scan_cap"], row["saving_vs_cap_2_10k_cny"], row["max_actual_clr"])


if __name__ == "__main__":
    main()
