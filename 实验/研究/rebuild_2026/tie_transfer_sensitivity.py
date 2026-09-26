"""Bound the value of source-end 10 kV tie capacity before topology verification."""

import argparse
from pathlib import Path

from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .joint_lifecycle_optimizer import run_model


SCALES = (0.0, 0.25, 0.5, 0.75, 1.0)


def run_sensitivity() -> list[dict]:
    rows = []
    for scale in SCALES:
        stations, years, transfers, summaries = run_model(
            rigid=True, tie_allowed=True, tie_transfer_limit_scale=scale)
        summary = next(r for r in summaries if (r["study_region_id"], r["voltage_kv"]) == ("QX-00005", 110))
        layer_years = [r for r in years if (r["study_region_id"], r["voltage_kv"]) == ("QX-00005", 110)]
        layer_transfers = [r for r in transfers if (r["study_region_id"], r["voltage_kv"]) == ("QX-00005", 110)]
        rows.append({
            "study_region_id": "QX-00005", "voltage_kv": 110,
            "source_end_transfer_limit_fraction": scale,
            "objective_npv_10k_cny": summary["objective_npv_10k_cny"],
            "max_actual_clr": summary["max_actual_clr"],
            "tie_transfer_event_count": len(layer_transfers),
            "max_single_transfer_mw": max((r["transfer_mw"] for r in layer_transfers), default=0),
            "capacity_2022_mva": layer_years[0]["selected_capacity_mva"],
            "capacity_2025_mva": layer_years[-1]["selected_capacity_mva"],
            "status": "source_end_headroom_fraction_proxy_not_verified_downstream_transferability",
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="邳州两站 10 kV 联络可转供比例敏感性")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    rows = run_sensitivity()
    write_csv(rows, args.output_dir / "tie_transfer_sensitivity_110kv.csv")
    print(f"输出 {len(rows)} 条联络可转供比例诊断")


if __name__ == "__main__":
    main()
