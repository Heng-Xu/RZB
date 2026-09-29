"""在两种站点结构模板上外推负荷增长和源荷水平，形成条件推荐矩阵。

本脚本不把模板站点和等效线路当作任意区县的真实网架。
"""

import csv
import json
from pathlib import Path

from .regional_static_milp_v2 import optimize


OUTPUT = Path(__file__).resolve().parent / "outputs/generic_parameter_matrix_v2"
ARCHETYPES = {
    "PZ-20-站结构模板": {"region": ("QX-00005", 110), "min_clr": 1.8},
    "CITY-29-站结构模板": {"region": ("QX-00007", 110),
                          "min_clr": 1.5, "city_baseline_cap_mva": 1.7 * 1449.77},
}
SOURCE_LOAD_RATIOS = (0.3, 1.0, 1.8)
ANNUAL_GROWTH_RATES = (0.0, 0.04, 0.08)
COMMON = {"require_transformer_n1": True,
          "n1_load_requirement": "bc_min_service_static",
          "elastic_cap": 2.6,
          "rigid_cap": 2.0,
          "elastic_allow_line_decisions": True}


def run(output=OUTPUT):
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for archetype, settings in ARCHETYPES.items():
        for growth in ANNUAL_GROWTH_RATES:
            for source_load in SOURCE_LOAD_RATIOS:
                common = {**settings, **COMMON,
                          "annual_growth_rate": growth,
                          "source_load_ratio": source_load}
                prefix = {"archetype": archetype,
                          "annual_load_growth_rate_assumed": growth,
                          "source_load_ratio_assumed": source_load}
                try:
                    rigid, rigid_years, *_ = optimize("rigid", **common)
                    elastic_floor = {x["year"]: x["clr"] + .001 for x in rigid_years}
                    elastic, elastic_years, *_ = optimize(
                        "elastic", annual_clr_floor=elastic_floor, **common)
                except ValueError as error:
                    rows.append({**prefix, "status": "infeasible_or_unproved",
                                 "reason": str(error)[:240]})
                    print(archetype, growth, source_load, "NO_RESULT", flush=True)
                    continue
                rigid_r = {r["year"]: r["clr"] for r in rigid_years}
                elastic_r = {r["year"]: r["clr"] for r in elastic_years}
                assert all(elastic_r[y] >= rigid_r[y] + .001 - 1e-7
                           for y in rigid_r)
                saving = rigid["objective_npv_10k"] - elastic["objective_npv_10k"]
                row = {**prefix, "status": "solved",
                       "rigid_npv_10k": rigid["objective_npv_10k"],
                       "elastic_npv_10k": elastic["objective_npv_10k"],
                       "elastic_saving_10k": saving,
                       "economically_preferred": "elastic" if saving > 1e-6 else "rigid",
                       "rigid_new_lines": sum(x["new_lines_commissioned"] for x in rigid_years),
                       "elastic_new_lines": sum(x["new_lines_commissioned"] for x in elastic_years),
                       "rigid_new_storage_mwh": sum(x["new_storage_energy_mwh"] for x in rigid_years),
                       "elastic_new_storage_mwh": sum(x["new_storage_energy_mwh"] for x in elastic_years),
                       "rigid_purchased_transformer_mva": sum(
                           x["new_transformer_purchase_mva"] for x in rigid_years),
                       "elastic_purchased_transformer_mva": sum(
                           x["new_transformer_purchase_mva"] for x in elastic_years),
                       **{f"rigid_clr_{y}": rigid_r[y] for y in rigid_r},
                       **{f"elastic_clr_{y}": elastic_r[y] for y in elastic_r},
                       "interpretation": "conditional_parameter_extrapolation_on_fixed_station_archetype"}
                rows.append(row)
                print(archetype, growth, source_load, "DONE", flush=True)
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with (output / "conditional_recommendation_matrix.csv").open(
            "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    metadata = {
        "method": "same static MILP as two district cases; both schemes share actions",
        "status": "conditional research extrapolation, not a standard table or grid approval",
        "archetypes": list(ARCHETYPES),
        "source_load_ratio_range": list(SOURCE_LOAD_RATIOS),
        "annual_growth_rate_range": list(ANNUAL_GROWTH_RATES),
        "baseline_source_load_ratio": 1.630652935,
        "rigid_cap": 2.0,
        "elastic_cap": 2.6,
        "elastic_clr_margin_over_rigid": .001,
        "solved": sum(x["status"] == "solved" for x in rows),
        "unsolved": sum(x["status"] != "solved" for x in rows),
        "limitation": "station structure and line pair abstraction remain fixed; source load ratio only rescales reverse peak proxy; PV and energy penetration are not equivalent",
    }
    (output / "assumptions.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
                                              encoding="utf-8")
    return rows


if __name__ == "__main__":
    run()
