"""Refine the Pizhou 35 kV CLR-cap cost frontier near the first benefit."""

import argparse
from pathlib import Path

from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .joint_lifecycle_optimizer import cost_factors, load_inputs, solve_layer


LAYER = ("QX-00005", 35)


def frontier() -> list[dict]:
    inputs = load_inputs()
    factors = cost_factors()
    caps = [round(2.0 + i * 0.01, 5) for i in range(41)]
    caps.extend((2.3183, 2.31833, 2.31834, 2.3184))
    rows = []
    for cap in sorted(set(caps)):
        stations, years, _, summary = solve_layer(LAYER, *inputs, factors, cap, False)
        rows.append({
            "study_region_id": LAYER[0], "voltage_kv": LAYER[1],
            "scan_cap": cap,
            "objective_npv_10k_cny": summary["objective_npv_10k_cny"],
            "max_actual_clr": summary["max_actual_clr"],
            "year_of_max_actual_clr": max(years, key=lambda r: r["actual_clr"])["year"],
            "capacity_path_mva": ";".join(f"{r['year']}:{r['selected_capacity_mva']}" for r in years),
            "storage_path_modules": ";".join(f"{r['year']}:{r['storage_modules_in_service']}" for r in years),
            "station_count": len({r["model_station_id"] for r in stations}),
            "status": "research_static_proxy_frontier_not_guide_certified",
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="邳州 35 kV 扫描上限—成本前沿加密")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    rows = frontier()
    write_csv(rows, args.output_dir / "cap_frontier_35kv.csv")
    changes = [row for i, row in enumerate(rows)
               if i == 0 or abs(row["objective_npv_10k_cny"] - rows[i-1]["objective_npv_10k_cny"]) > 1e-5]
    print(f"求解 {len(rows)} 档，识别 {len(changes)} 个成本台阶：")
    for row in changes:
        print(row["scan_cap"], row["objective_npv_10k_cny"], row["max_actual_clr"])


if __name__ == "__main__":
    main()
