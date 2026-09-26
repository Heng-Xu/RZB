"""独立复核历史容量起点下的刚弹年度路径与停运承载代理。"""

import json
from collections import defaultdict
from pathlib import Path

from .annual_no_tie_investment_submodel import storage_effective_power_per_module
from .baseline_2021 import read_csv
from .hourly_source_profile import OUTPUT_DIR
from .simulation_reserve_policy import OUTPUT


def audit(output_dir: Path = OUTPUT) -> dict:
    output_dir = Path(output_dir)
    baselines = read_csv(output_dir / "baseline_stations.csv")
    initial = defaultdict(float)
    for row in baselines:
        initial[row["study_region_id"], int(row["voltage_kv"])] += float(row["simulation_capacity_mva_2021"])
    official = {(r["region_id"], int(r["voltage_kv"]), int(r["year"])):
                float(r["reported_downward_load_mw"])
                for r in read_csv(OUTPUT_DIR / "official_annual.csv")}
    durations = {(r["study_region_id"], int(r["voltage_kv"]), r["model_station_id"]): r
                 for r in read_csv(OUTPUT_DIR / "static_storage_need_screen_2025.csv")
                 if r["capacity_case"] == "hold_2021_simulation_capacity"}
    problems = []
    summaries = read_csv(output_dir / "summary.csv")
    for case in summaries:
        layer = case["study_region_id"], int(case["voltage_kv"])
        stem = f"{case['scheme']}_{layer[0]}_{layer[1]}"
        stations = read_csv(output_dir / f"{stem}_stations.csv")
        years = read_csv(output_dir / f"{stem}_years.csv")
        tie_file = output_dir / f"{stem}_ties.csv"
        ties = read_csv(tie_file) if tie_file.exists() else []
        fraction = float(case["contingency_fraction_assumption"])
        gross = 0.0
        for row in stations:
            s = layer + (row["model_station_id"],)
            year = int(row["year"])
            units = [float(row[f"selected_unit_{i}_mva"]) for i in (1, 2)]
            gross += sum(max(0.0, float(row[f"selected_unit_{i}_mva"]) -
                             float(row[f"prior_unit_{i}_mva"])) for i in (1, 2))
            storage = (int(row["storage_modules_in_service"]) *
                       storage_effective_power_per_module(int(durations[s]["forward_d95_max_run_hours"])))
            net_out = sum(float(t["transfer_mw"]) *
                          ((t["donor_station_id"] == s[2]) - (t["receiver_station_id"] == s[2]))
                          for t in ties if int(t["year"]) == year and t["scenario"] == "forward")
            demand = float(row["forward_screen_mw"])
            if .95 * sum(units) + storage + net_out < demand - 1e-5:
                problems.append(f"{stem} {s[2]} {year}: 正常供电不足")
            if .95 * min(units) + storage + fraction * net_out < fraction * demand - 1e-5:
                problems.append(f"{stem} {s[2]} {year}: 停运承载不足")
        if case["scheme"] == "rigid":
            if gross > initial[layer] * float(case["rigid_budget_assumption"]) + 1e-5:
                problems.append(f"{stem}: 累计增配量超限")
        for year in years:
            yy = int(year["year"])
            peak = float(year["synchronous_forward_peak_mw"])
            if layer[0] == "QX-00005" and abs(peak - official[layer + (yy,)]) > 1e-5:
                problems.append(f"{stem} {yy}: 分母不等于甲方原表")
            ratio = float(year["selected_capacity_mva"]) / peak
            if abs(ratio - float(year["actual_clr"])) > 1e-6:
                problems.append(f"{stem} {yy}: 容载比不一致")
            if case["scheme"] == "rigid" and ratio > 2.0 + 1e-8:
                problems.append(f"{stem} {yy}: 刚性比值超过 2")
        if abs(sum(float(y["year_lifecycle_npv_10k_cny"]) for y in years) -
               float(case["objective_npv_10k_cny"])) > 1e-3:
            problems.append(f"{stem}: 全寿命费用不一致")
    matrix = read_csv(output_dir / "annual_matrix.csv")
    if len(matrix) != 12:
        problems.append("逐年矩阵不是 12 行")
    result = {"status": "PASS" if not problems else "FAIL",
              "audited_path_count": len(summaries), "matrix_row_count": len(matrix),
              "problems": problems}
    (output_dir / "audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                                           encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(audit(), ensure_ascii=False))
