"""核对条件矩阵的覆盖、基准复现和推荐行是否对应真实求解路径。"""

import json
from collections import defaultdict

from .baseline_2021 import read_csv
from .hourly_source_profile import OUTPUT_DIR


def audit() -> dict:
    matrix = read_csv(OUTPUT_DIR / "planning_conditional_matrix.csv")
    recommendations = read_csv(OUTPUT_DIR / "planning_conditional_recommendation_matrix.csv")
    feasibility = read_csv(OUTPUT_DIR / "planning_conditional_feasibility.csv")
    scenarios = read_csv(OUTPUT_DIR / "planning_conditional_scenarios.csv")
    base_rigid = {(r["study_region_id"], r["voltage_kv"], r["year"]): r
                  for r in read_csv(OUTPUT_DIR / "planning_rigid_years.csv")}
    base_elastic = {(r["study_region_id"], r["voltage_kv"], r["year"]): r
                    for r in read_csv(OUTPUT_DIR / "planning_elastic_years.csv")}
    expected = {(s["scenario_id"], region, voltage, str(year))
                for s in scenarios for region, voltage in (("QX-00005", "35"),
                                                            ("QX-00005", "110"),
                                                            ("QX-00007", "110"))
                for year in (2022, 2023, 2024, 2025)}
    keys = [(r["scenario_id"], r["study_region_id"], r["voltage_kv"], r["year"])
            for r in recommendations]
    if set(keys) != expected or len(keys) != len(expected):
        raise ValueError("条件推荐矩阵缺失或重复情景、单元、年度")
    by_path = defaultdict(list)
    for row in matrix:
        by_path[(row["scenario_id"], row["study_region_id"], row["voltage_kv"], row["year"])].append(row)
        if float(row["simulated_clr"]) > (2.0 if row["scheme"] == "rigid" else 2.4) + 1e-7:
            raise ValueError("已求得的容量路径超过对应方案容载比上限")
        if row["scenario_id"] == "base":
            base = (base_rigid if row["scheme"] == "rigid" else base_elastic)[
                row["study_region_id"], row["voltage_kv"], row["year"]]
            if abs(float(row["simulated_clr"]) - float(base["actual_clr"])) > 1e-8 \
                    or abs(float(row["simulated_capacity_mva"]) - float(base["selected_capacity_mva"])) > 1e-8:
                raise ValueError("矩阵基准情景与已落盘方案不一致")
    for row in recommendations:
        key = row["scenario_id"], row["study_region_id"], row["voltage_kv"], row["year"]
        paths = by_path[key]
        choice = row["preferred_scheme"]
        selected = paths if choice == "cost_tie" else [p for p in paths if p["scheme"] == choice.replace("_only_feasible", "")]
        if not selected:
            raise ValueError(f"{key} 推荐值没有已求解的设备路径")
        lo, hi = min(float(p["simulated_clr"]) for p in selected), max(float(p["simulated_clr"]) for p in selected)
        if abs(lo - float(row["recommended_simulated_clr_min"])) > 1e-8 \
                or abs(hi - float(row["recommended_simulated_clr_max"])) > 1e-8:
            raise ValueError(f"{key} 推荐容载比与对应设备路径不符")
    result = {
        "scenario_count": len(scenarios), "research_unit_count": 3,
        "annual_recommendation_count": len(recommendations),
        "solved_annual_scheme_rows": len(matrix),
        "infeasible_scheme_paths": [
            {k: r[k] for k in ("scenario_id", "study_region_id", "voltage_kv", "scheme")}
            for r in feasibility if r["status"] != "feasible_optimum"],
        "base_path_reconciliation": "pass",
        "recommended_ratio_has_matching_feasible_equipment_path": "pass",
        "conditional_matrix_internal_status": "ready_for_project_review",
        "empirical_generalization_status": "not_claimed_two_regions_three_units",
        "final_report_status": "awaiting_project_matrix_review",
    }
    return result


def main() -> None:
    result = audit()
    path = OUTPUT_DIR / "planning_conditional_audit.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"条件矩阵核验通过：{result['annual_recommendation_count']} 条推荐行")


if __name__ == "__main__":
    main()
