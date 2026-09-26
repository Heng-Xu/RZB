"""验证研究性上限能否覆盖无联络、仅投资现值子模型的设备变化。"""

import argparse
from pathlib import Path

from .annual_no_tie_investment_submodel import build_annual_no_tie_investment_submodel
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR


PIZHOU_CAPS = (2.0, 2.1, 2.2, 2.3, 2.4, 3.0, 4.0)


def run_scan(reverse_variant: str = "night_central", discount_rate: float = 0.06) -> list[dict]:
    output = []
    previous_cost = {}
    for pizhou_cap in PIZHOU_CAPS:
        city_cap = min(pizhou_cap, 3.0)
        _, years, layers = build_annual_no_tie_investment_submodel(
            reverse_variant=reverse_variant,
            discount_rate=discount_rate,
            capacity_load_caps={"QX-00005": pizhou_cap, "QX-00007": city_cap},
        )
        for layer in layers:
            key = layer["study_region_id"], layer["voltage_kv"]
            cost = layer["investment_npv_10k_cny"]
            if cost > previous_cost.get(key, float("inf")) + 1e-4:
                raise ValueError(f"上限放宽后目标成本上升：{key}")
            previous_cost[key] = cost
            selected = [row for row in years if (row["study_region_id"], row["voltage_kv"]) == key]
            output.append({
                "study_region_id": key[0],
                "voltage_kv": key[1],
                "reverse_variant": reverse_variant,
                "scan_cap": city_cap if key[0] == "QX-00007" else pizhou_cap,
                "investment_npv_10k_cny": cost,
                "maximum_actual_clr_2022_2025": max(row["actual_clr"] for row in selected),
                "storage_modules_2025": next(row["storage_modules_in_service"] for row in selected if row["year"] == 2025),
                "technical_scope": layer["technical_scope"],
                "cost_scope": layer["cost_scope"],
            })
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="扫描无联络投资现值子模型的容载比上限")
    parser.add_argument("--reverse-variant", choices=("night_central", "early_pv_high"), default="night_central")
    parser.add_argument("--discount-rate", type=float, default=0.06)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    rows = run_scan(args.reverse_variant, args.discount_rate)
    write_csv(rows, args.output_dir / f"annual_no_tie_cap_scan_{args.reverse_variant}.csv")
    print(f"已核对 {len(rows)} 条无联络投资现值扫描结果；非全寿命、非导则承载力或正式推荐。")


if __name__ == "__main__":
    main()
