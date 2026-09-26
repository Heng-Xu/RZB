"""独立复算可减容预算前沿的年度比值、增配预算和费用。"""

import json
from collections import defaultdict
from pathlib import Path

from .baseline_2021 import read_csv
from .hourly_source_profile import OUTPUT_DIR


def audit(output_dir: Path = OUTPUT_DIR / "capacity_release_simulation/final_policy_frontier_v3") -> dict:
    output_dir = Path(output_dir)
    summaries = read_csv(output_dir / "summary.csv")
    baseline = read_csv(OUTPUT_DIR / "planning_2021_common_baseline_layers.csv")
    official = {(r["region_id"], int(r["voltage_kv"]), int(r["year"])):
                float(r["reported_downward_load_mw"])
                for r in read_csv(OUTPUT_DIR / "official_annual.csv")}
    initial = {(r["study_region_id"], int(r["voltage_kv"])): float(r["capacity_mva"])
               for r in baseline}
    problems = []
    fronts = defaultdict(list)
    for case in summaries:
        layer = case["study_region_id"], int(case["voltage_kv"])
        scenario = case["planning_scenario"]
        stem = f"{scenario}_{layer[0]}_{layer[1]}"
        stations = read_csv(output_dir / f"{stem}_stations.csv")
        years = read_csv(output_dir / f"{stem}_years.csv")
        if len(years) != 4 or len(stations) != 4 * int(years[0]["station_count"]):
            problems.append(f"{stem}: 年度或站级记录不完整")
        gross = 0.0
        for row in stations:
            before = sum(float(row[f"prior_unit_{i}_mva"]) for i in (1, 2))
            after = sum(float(row[f"selected_unit_{i}_mva"]) for i in (1, 2))
            gross += sum(max(0.0, float(row[f"selected_unit_{i}_mva"]) -
                             float(row[f"prior_unit_{i}_mva"])) for i in (1, 2))
            if abs(float(row["selected_capacity_mva"]) - after) > 1e-6:
                problems.append(f"{stem}: {row['model_station_id']} 容量不一致")
            if abs(float(row["released_capacity_mva"]) - max(0.0, before - after)) > 1e-6:
                problems.append(f"{stem}: {row['model_station_id']} 减容量不一致")
        if case["capacity_growth_budget_fraction"]:
            budget = float(case["capacity_growth_budget_fraction"]) * initial[layer]
            if gross > budget + 1e-5:
                problems.append(f"{stem}: 累计增配量 {gross} 超预算 {budget}")
            fronts[layer].append((float(case["capacity_growth_budget_fraction"]),
                                  float(case["objective_npv_10k_cny"])))
        for year in years:
            if layer[0] == "QX-00005" and abs(
                float(year["synchronous_forward_peak_mw"]) -
                official[layer + (int(year["year"]),)]
            ) > 1e-5:
                problems.append(f"{stem}: {year['year']} 邳州年度分母与甲方原表不一致")
            ratio = float(year["selected_capacity_mva"]) / float(year["synchronous_forward_peak_mw"])
            if abs(ratio - float(year["actual_clr"])) > 1e-6:
                problems.append(f"{stem}: {year['year']} 实际容载比不一致")
            if scenario.startswith("rigid") and ratio > 2.0 + 1e-8:
                problems.append(f"{stem}: {year['year']} 刚性实际容载比超过 2.0")
        cost = sum(float(r["year_lifecycle_npv_10k_cny"]) for r in years)
        if abs(cost - float(case["objective_npv_10k_cny"])) > 1e-3:
            problems.append(f"{stem}: 成本现值不一致")
    for layer, values in fronts.items():
        for left, right in zip(sorted(values), sorted(values)[1:]):
            if right[1] > left[1] + 1e-3:
                problems.append(f"{layer}: 放宽增配预算后成本上升")
    result = {"status": "PASS" if not problems else "FAIL",
              "feasible_path_count": len(summaries),
              "infeasible_path_count": len(read_csv(output_dir / "infeasible.csv"))
              if (output_dir / "infeasible.csv").exists() else 0,
              "problems": problems}
    (output_dir / "audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                                           encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(audit(), ensure_ascii=False))
