"""对未由甲方报价锁定的全寿命参数做有限情景复算。"""

import argparse
from pathlib import Path

from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .joint_lifecycle_optimizer import cost_factors, run_model


CASES = (
    ("base", {}, "night_central"),
    ("discount_4pct", {"rate": 0.04}, "night_central"),
    ("discount_8pct", {"rate": 0.08}, "night_central"),
    ("network_om_0pct", {"network_om": 0}, "night_central"),
    ("network_om_2pct", {"network_om": 0.02}, "night_central"),
    ("storage_life_8yr", {"storage_life": 8}, "night_central"),
    ("storage_life_12yr", {"storage_life": 12}, "night_central"),
    ("early_pv_high", {}, "early_pv_high"),
)


def run_sensitivities() -> list[dict]:
    rows = []
    for case, overrides, reverse_variant in CASES:
        factors = cost_factors(**overrides)
        for scheme in ("rigid", "elastic"):
            _, years, ties, summaries = run_model(
                reverse_variant=reverse_variant, factors=factors, rigid=scheme == "rigid",
                caps={("QX-00005", 35): 2.4, ("QX-00005", 110): 2.0,
                      ("QX-00007", 110): 2.0},
            )
            for summary in summaries:
                matching = [r for r in years if (r["study_region_id"], r["voltage_kv"]) ==
                            (summary["study_region_id"], summary["voltage_kv"])]
                rows.append({
                    "case": case, "reverse_variant": reverse_variant,
                    "scheme": scheme, "study_region_id": summary["study_region_id"],
                    "voltage_kv": summary["voltage_kv"], "clr_cap": summary["clr_cap"],
                    "objective_npv_10k_cny": summary["objective_npv_10k_cny"],
                    "max_actual_clr": summary["max_actual_clr"],
                    "selected_capacity_2025_mva": matching[-1]["selected_capacity_mva"],
                    "storage_modules_2025": matching[-1]["storage_modules_in_service"],
                    "line_built_2025": matching[-1]["line_built"],
                    "tie_transfer_event_count": sum(
                        1 for t in ties if (t["study_region_id"], t["voltage_kv"]) ==
                        (summary["study_region_id"], summary["voltage_kv"])),
                    "solver_status": summary["solver_status"],
                    "cost_assumptions": ";".join(f"{k}={v}" for k, v in factors.items() if not isinstance(v, dict)),
                })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="全寿命参数及历史反送代理敏感性")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    rows = run_sensitivities()
    write_csv(rows, args.output_dir / "joint_lifecycle_sensitivity.csv")
    print(f"完成 {len(CASES)} 个假设情景、{len(rows)} 个片区×电压×方案结果。")


if __name__ == "__main__":
    main()
