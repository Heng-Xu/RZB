"""导则负荷增长分档 + 同动作集成本对照 + 市区低于邳州的研究条件。"""

import json
from pathlib import Path

from .baseline_2021 import read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .planning_load_profile import weighted_annual_growth
from .regional_static_milp_v2 import optimize, run
from .regional_static_milp_v2_audit import audit
from .two_district_source_audit import audit as source_audit


OUTPUT = Path(__file__).resolve().parent / "outputs"
PIZHOU = OUTPUT / "ordered_guide_pizhou_n1"
CITY = OUTPUT / "ordered_guide_city_n1"
MARGIN = .001


def guide_range(weighted_growth):
    if weighted_growth <= .02:
        return 1.5, 1.7
    if weighted_growth <= .04:
        return 1.6, 1.8
    if weighted_growth <= .07:
        return 1.7, 1.9
    return 1.8, 2.0


def main():
    observed = {}
    for row in read_csv(OUTPUT_DIR / "official_annual.csv"):
        key = row["region_id"], int(row["voltage_kv"])
        if key in (("QX-00005", 110), ("QX-00007", 110)):
            observed.setdefault(key, {})[int(row["year"])] = float(row["reported_downward_load_mw"])
    guide = {}
    guide_rows = []
    for region, annual in observed.items():
        growth, source = weighted_annual_growth(annual)
        lo, hi = guide_range(growth)
        guide[region] = lo, hi
        guide_rows.append({"region_id": region[0], "voltage_kv": region[1],
                           "weighted_four_year_growth": growth,
                           "guide_table": "DL/T 5729-2023 Table 6.3.4",
                           "guide_lower": lo, "guide_upper": hi,
                           "load_source_cells": "Sheet1!D19,G19,J19,M19,P19"
                           if region[0] == "QX-00005" else "Sheet1!D9,G9,J9,M9,P9",
                           "annual_growth_rates": "|".join(str(x["observed_growth_rate"]) for x in source),
                           "interpretation": "four_year_weighted_research_classification_not_historical_forecast"})
    write_csv(guide_rows, OUTPUT / "two_district_guide_growth_classification.csv")
    common = {"require_transformer_n1": True,
              "n1_load_requirement": "bc_min_service_static",
              "elastic_cap": 2.6,
              "elastic_allow_line_decisions": True}
    _, pz_rigid_years, *_ = optimize("rigid", region=("QX-00005", 110),
                                     min_clr=guide[("QX-00005", 110)][0], **common)
    pz_elastic_floor = {r["year"]: r["clr"] + MARGIN for r in pz_rigid_years}
    run(PIZHOU, region=("QX-00005", 110), min_clr=guide[("QX-00005", 110)][0],
        scheme_kwargs={"elastic": {"annual_clr_floor": pz_elastic_floor}}, **common)
    print(audit(PIZHOU), flush=True)
    pz_years = {scheme: {int(r["year"]): float(r["clr"])
                         for r in read_csv(PIZHOU / f"{scheme}_years.csv")}
                for scheme in ("rigid", "elastic")}
    city_ceiling = {year: min(pz_years["rigid"][year], pz_years["elastic"][year]) - MARGIN
                    for year in (2022, 2023, 2024, 2025)}
    city_baseline_cap = guide[("QX-00007", 110)][1] * observed[("QX-00007", 110)][2021]
    _, city_rigid_years, *_ = optimize(
        "rigid", region=("QX-00007", 110), city_baseline_cap_mva=city_baseline_cap,
        min_clr=guide[("QX-00007", 110)][0], rigid_cap=1.8,
        annual_clr_ceiling=city_ceiling, **common)
    city_elastic_floor = {r["year"]: r["clr"] + MARGIN for r in city_rigid_years}
    run(CITY, region=("QX-00007", 110), city_baseline_cap_mva=city_baseline_cap,
        min_clr=guide[("QX-00007", 110)][0], rigid_cap=1.8,
        annual_clr_ceiling=city_ceiling,
        scheme_kwargs={"elastic": {"annual_clr_floor": city_elastic_floor}}, **common)
    print(audit(CITY), flush=True)
    source_audit((PIZHOU.name, CITY.name), OUTPUT / "ordered_guide_source_audit.json")
    pz_s = {x["scheme"]: x for x in json.loads((PIZHOU / "summary.json").read_text(encoding="utf-8"))}
    city_s = {x["scheme"]: x for x in json.loads((CITY / "summary.json").read_text(encoding="utf-8"))}
    result = {"guide_classification": guide_rows,
              "city_ordering_margin": MARGIN,
              "city_annual_clr_ceiling": city_ceiling,
              "elastic_over_rigid_annual_clr_margin": MARGIN,
              "city_rigid_cap": 1.8,
              "city_rigid_cap_basis": "guide_slow_growth_upper_1.7_infeasible_under_static_N1;_1.8_feasible_research_control",
              "decision_sets_identical": True,
              "n1_background_and_new_lines_available_in_both_schemes": True,
              "cost_order_scope": "each_district_and_total",
              "total_npv_10k": {scheme: pz_s[scheme]["objective_npv_10k"] +
                                city_s[scheme]["objective_npv_10k"]
                                for scheme in ("rigid", "elastic")},
              "city_per_scheme_cost_status": "strictly_lower_elastic_in_this_run_not_a_model_theorem"}
    (OUTPUT / "ordered_guide_summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(result["total_npv_10k"], flush=True)


if __name__ == "__main__":
    main()
