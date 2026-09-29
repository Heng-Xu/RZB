"""在相同动作集与区县容载比排序条件下重解两项实际成本比值。"""

from pathlib import Path

from .city_mapping_audit import write_csv
from .regional_static_milp_v2 import optimize


OUTPUT = Path(__file__).resolve().parent / "outputs/ordered_guide_cost_sensitivity.csv"
CITY_BASELINE_CAP = 1.7 * 1449.77
COMMON = {"require_transformer_n1": True,
          "n1_load_requirement": "bc_min_service_static",
          "elastic_cap": 2.6,
          "elastic_allow_line_decisions": True}


def run(output=OUTPUT):
    rows = []
    for component, scale in (("baseline", 1.0), ("line", .8), ("line", 1.2),
                             ("storage", .8), ("storage", 1.2)):
        prices = {"line_scale": scale if component == "line" else 1.0,
                  "storage_scale": scale if component == "storage" else 1.0}
        pz = {"rigid": optimize("rigid", region=("QX-00005", 110), min_clr=1.8,
                                 **COMMON, **prices)}
        pz_floor = {y["year"]: y["clr"] + .001 for y in pz["rigid"][1]}
        pz["elastic"] = optimize("elastic", region=("QX-00005", 110), min_clr=1.8,
                                 annual_clr_floor=pz_floor, **COMMON, **prices)
        ceiling = {year: min(pz[s][1][i]["clr"] for s in ("rigid", "elastic")) - .001
                   for i, year in enumerate((2022, 2023, 2024, 2025))}
        city = {"rigid": optimize("rigid", region=("QX-00007", 110),
                                  city_baseline_cap_mva=CITY_BASELINE_CAP,
                                  min_clr=1.5, rigid_cap=1.8,
                                  annual_clr_ceiling=ceiling,
                                  **COMMON, **prices)}
        city_floor = {y["year"]: y["clr"] + .001 for y in city["rigid"][1]}
        city["elastic"] = optimize("elastic", region=("QX-00007", 110),
                                   city_baseline_cap_mva=CITY_BASELINE_CAP,
                                   min_clr=1.5, rigid_cap=1.8,
                                   annual_clr_ceiling=ceiling,
                                   annual_clr_floor=city_floor,
                                   **COMMON, **prices)
        for region, results in (("QX-00005", pz), ("QX-00007", city)):
            for scheme in ("rigid", "elastic"):
                summary, years, _, _, lines, _ = results[scheme]
                rows.append({"region_id": region, "scheme": scheme,
                             "changed_component": component, "price_scale": scale,
                             "transformer_to_line_price_ratio":
                             (summary["transformer_price_10k_per_purchased_mva"] / .95) /
                             (summary["line_price_10k_per_planned_pair"] * prices["line_scale"] / 7.491),
                             "transformer_to_storage_price_ratio":
                             (summary["transformer_price_10k_per_purchased_mva"] / .95) /
                             (summary["storage_price_10k_per_mwh"] * 2.15 * prices["storage_scale"]),
                             "lifecycle_npv_10k": summary["objective_npv_10k"],
                             "new_lines": len(lines),
                             "new_storage_cabinets": sum(y["new_storage_modules"] for y in years),
                             "purchased_transformer_mva": sum(y["new_transformer_purchase_mva"] for y in years),
                             **{f"clr_{y['year']}": y["clr"] for y in years},
                             "city_ordering_margin": .001,
                             "status": "reoptimized_identical_action_sets"})
        print(component, scale, "DONE", flush=True)
    write_csv(rows, output)
    return rows


if __name__ == "__main__":
    run()
