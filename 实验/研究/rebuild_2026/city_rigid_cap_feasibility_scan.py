"""市区增长分档起点与排序条件下，检验刚性容载比控制值。"""

from pathlib import Path

from .city_mapping_audit import write_csv
from .regional_static_milp_v2 import optimize


OUTPUT = Path(__file__).resolve().parent / "outputs/ordered_guide_city_rigid_cap_scan.csv"
COMMON = {"require_transformer_n1": True,
          "n1_load_requirement": "bc_min_service_static",
          "elastic_allow_line_decisions": True,
          "elastic_cap": 2.6}


def run(output=OUTPUT):
    pz = {"rigid": optimize("rigid", region=("QX-00005", 110), min_clr=1.8, **COMMON)}
    elastic_floor = {y["year"]: y["clr"] + .001 for y in pz["rigid"][1]}
    pz["elastic"] = optimize("elastic", region=("QX-00005", 110), min_clr=1.8,
                              annual_clr_floor=elastic_floor, **COMMON)
    ceiling = {year: min(pz[s][1][i]["clr"] for s in ("rigid", "elastic")) - .001
               for i, year in enumerate((2022, 2023, 2024, 2025))}
    rows = []
    for cap in (1.7, 1.75, 1.79, 1.8, 1.81, 2.0):
        try:
            summary, years, _, _, lines, _ = optimize(
                "rigid", region=("QX-00007", 110),
                city_baseline_cap_mva=1.7 * 1449.77,
                min_clr=1.5, rigid_cap=cap,
                annual_clr_ceiling=ceiling, **COMMON)
            status = "feasible"
            cost = summary["objective_npv_10k"]
            ratios = {f"clr_{y['year']}": y["clr"] for y in years}
            lines_count = len(lines)
        except ValueError as exc:
            if "infeasible" not in str(exc).lower():
                raise
            status, cost, ratios, lines_count = "infeasible", "", {}, ""
        rows.append({"tested_rigid_cap": cap, "status": status,
                     "lifecycle_npv_10k": cost, "new_lines": lines_count,
                     **{f"clr_{year}": ratios.get(f"clr_{year}", "")
                        for year in (2022, 2023, 2024, 2025)},
                     "basis": "DLT5729_2023_table_6_3_4_city_slow_growth;_N1_static_proxy;_city_below_pizhou"})
        print(cap, status, flush=True)
    write_csv(rows, output)
    return rows


if __name__ == "__main__":
    run()
