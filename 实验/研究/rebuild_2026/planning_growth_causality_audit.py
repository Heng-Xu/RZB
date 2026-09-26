"""核对年度负荷增长是否真实触发容量决策；旧矩阵只作诊断。"""

from pathlib import Path

from .baseline_2021 import read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR


def build_growth_audit(output_dir: Path = OUTPUT_DIR) -> list[dict]:
    output_dir = Path(output_dir)
    starts = {(r["study_region_id"], r["voltage_kv"]): r
              for r in read_csv(output_dir / "planning_2021_common_baseline_layers.csv")}
    years = {(r["study_region_id"], r["voltage_kv"], int(r["year"])): r
             for r in read_csv(output_dir / "planning_rigid_years.csv")}
    years.update({(r["study_region_id"], r["voltage_kv"], int(r["year"])): r
                  for r in read_csv(output_dir / "planning_rigid_no_tie_years.csv")})
    official = {(r["region_id"], r["voltage_kv"], int(r["year"])): r
                for r in read_csv(output_dir / "official_annual.csv")}
    rows = []
    for layer, start in sorted(starts.items()):
        p0 = float(start["net_forward_peak_mw"])
        c0 = float(start["capacity_mva"])
        previous_peak, previous_capacity = p0, c0
        for year in range(2022, 2026):
            row = years[layer + (year,)]
            peak = float(row["synchronous_forward_peak_mw"])
            capacity = float(row["selected_capacity_mva"])
            observed = official.get(layer + (year,))
            rows.append({
                "study_region_id": layer[0], "voltage_kv": layer[1], "year": year,
                "2021_simulated_capacity_mva": c0,
                "2021_net_peak_mw": p0,
                "annual_net_peak_mw": peak,
                "net_peak_change_from_previous_mw": round(peak - previous_peak, 6),
                "net_peak_growth_from_2021_pct": round(100 * (peak / p0 - 1), 3),
                "rigid_no_tie_selected_capacity_mva": capacity,
                "capacity_change_from_previous_mva": round(capacity - previous_capacity, 6),
                "selected_clr": round(capacity / peak, 9),
                "R2_capacity_ceiling_mva": round(2 * peak, 6),
                "unused_R2_capacity_budget_mva": round(2 * peak - capacity, 6),
                "aggregate_095_forward_service_floor_mva": round(peak / .95, 6),
                "observed_district_capacity_mva_different_baseline": (
                    observed["capacity_mva"] if observed else ""),
                "observed_capacity_scope": (
                    "same_district_voltage_but_not_simulated_station_sample"
                    if layer == ("QX-00007", "110") else "district_observed_not_simulated_baseline"),
                "diagnosis": "R2_is_capacity_ceiling_not_growth_driven_capacity_floor",
            })
            previous_peak, previous_capacity = peak, capacity
    return rows


def main() -> None:
    rows = build_growth_audit()
    write_csv(rows, OUTPUT_DIR / "planning_growth_causality_audit.csv")
    print(f"已核对 {len(rows)} 条年度增长与容量决策关系")


if __name__ == "__main__":
    main()
