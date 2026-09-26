"""从设备事件重建 2022—2041 年增量现金流，独立对账 MILP 目标值。"""

import argparse
from collections import defaultdict
from pathlib import Path

from .baseline_2021 import read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .incremental_cost import lifecycle_cashflows, discount_to_2021
from .joint_lifecycle_optimizer import cost_factors


def build_cashflows(source: Path = OUTPUT_DIR, factors: dict | None = None) -> tuple[list[dict], list[dict]]:
    factors = factors or cost_factors()
    recommended = {(r["study_region_id"], int(r["voltage_kv"])): float(r["least_cost_scan_cap"])
                   for r in read_csv(source / "joint_lifecycle_conditional_recommendations.csv")}
    station_cases = []
    for scheme, filename in (("rigid", "joint_lifecycle_rigid_stations.csv"),
                             ("elastic", "joint_lifecycle_elastic_scan_stations.csv")):
        for row in read_csv(source / filename):
            if scheme == "elastic" and float(row["clr_cap"]) != recommended[row["study_region_id"], int(row["voltage_kv"])]:
                continue
            station_cases.append(row)
    line_cases = [r for r in read_csv(source / "joint_lifecycle_rigid_years.csv")
                  if float(r["new_line_capex_10k_cny"]) > 0]
    events = []
    for row in station_cases:
        for measure, cost_key, life_key, om_key in (
            ("transformer", "transformer_capex_10k_cny", "transformer_life_years", "network_fixed_om_rate"),
            ("storage", "storage_capex_10k_cny", "storage_life_years", "storage_fixed_om_rate"),
        ):
            capex = float(row[cost_key])
            if capex <= 0:
                continue
            for flow in lifecycle_cashflows(capex, int(row["year"]), factors[life_key], factors[om_key]):
                events.append({"study_region_id": row["study_region_id"], "voltage_kv": int(row["voltage_kv"]),
                               "scheme": row["scheme"], "model_station_id": row["model_station_id"],
                               "commissioning_year": int(row["year"]), "cashflow_year": flow["year"],
                               "measure": measure, "component": flow["component"],
                               "amount_10k_cny": round(flow["amount_10k_cny"], 8),
                               "discounted_10k_cny": round(discount_to_2021(flow["amount_10k_cny"], flow["year"], factors["discount_rate"]), 8)})
    for row in line_cases:
        capex = float(row["new_line_capex_10k_cny"])
        for flow in lifecycle_cashflows(capex, int(row["year"]), factors["line_life_years"], factors["network_fixed_om_rate"]):
            events.append({"study_region_id": row["study_region_id"], "voltage_kv": int(row["voltage_kv"]),
                           "scheme": "rigid", "model_station_id": "BDZ-00027_to_BDZ-00048",
                           "commissioning_year": int(row["year"]), "cashflow_year": flow["year"],
                           "measure": "new_line", "component": flow["component"],
                           "amount_10k_cny": round(flow["amount_10k_cny"], 8),
                           "discounted_10k_cny": round(discount_to_2021(flow["amount_10k_cny"], flow["year"], factors["discount_rate"]), 8)})
    totals = defaultdict(lambda: [0.0, 0.0])
    for r in events:
        key = (r["study_region_id"], r["voltage_kv"], r["scheme"], r["cashflow_year"], r["measure"], r["component"])
        totals[key][0] += r["amount_10k_cny"]
        totals[key][1] += r["discounted_10k_cny"]
    annual = [{"study_region_id": key[0], "voltage_kv": key[1], "scheme": key[2],
               "cashflow_year": key[3], "measure": key[4], "component": key[5],
               "amount_10k_cny": round(value[0], 6), "discounted_10k_cny": round(value[1], 6)}
              for key, value in sorted(totals.items())]
    target = {(r["study_region_id"], int(r["voltage_kv"]), "rigid"): float(r["objective_npv_10k_cny"])
              for r in read_csv(source / "joint_lifecycle_rigid_layers.csv")}
    target.update({(r["study_region_id"], int(r["voltage_kv"]), "elastic"): float(r["minimum_lifecycle_npv_10k_cny"])
                   for r in read_csv(source / "joint_lifecycle_conditional_recommendations.csv")})
    for key, optimum in target.items():
        reconstructed = sum(r["discounted_10k_cny"] for r in events
                            if (r["study_region_id"], r["voltage_kv"], r["scheme"]) == key)
        if abs(reconstructed - optimum) > 1e-4:
            raise ValueError(f"{key} 现金流与最优目标不一致: {reconstructed} != {optimum}")
    return events, annual


def main() -> None:
    parser = argparse.ArgumentParser(description="重建 2022—2041 年措施投资、运维和更新现金流")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    events, annual = build_cashflows(args.output_dir)
    write_csv(events, args.output_dir / "joint_lifecycle_cashflow_events.csv")
    write_csv(annual, args.output_dir / "joint_lifecycle_cashflow_annual.csv")
    print(f"复算通过：{len(events)} 条措施现金流，{len(annual)} 条年度分类汇总。")


if __name__ == "__main__":
    main()
