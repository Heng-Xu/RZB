"""从《近5年容载比》原工作簿逐格复核本轮区县分母与 2021 基准。"""

import json
from pathlib import Path

from openpyxl import load_workbook

from .baseline_2021 import read_csv
from .regional_static_milp_v2 import BASELINE


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/tuomin/电网建模数据_Agent整合版_V1.2/近5年容载比.xlsx"
OUTPUT = Path(__file__).resolve().parent / "outputs"


def audit(directory_names=None, output_file=None):
    sheet = load_workbook(SOURCE, read_only=True, data_only=True).worksheets[0]
    directory_names = directory_names or ("two_districts_pizhou_n1",
                                          "two_districts_city_district_extrapolated_n1")
    cases = (("QX-00005", 19, directory_names[0]),
             ("QX-00007", 9, directory_names[1]))
    results = []
    for region_id, row, dirname in cases:
        directory = OUTPUT / dirname
        summaries = json.loads((directory / "summary.json").read_text(encoding="utf-8"))
        source_capacity = 10 * float(sheet[f"C{row}"].value)
        source_load = 10 * float(sheet[f"D{row}"].value)
        if region_id == "QX-00005":
            baseline = [x for x in read_csv(BASELINE)
                        if x["study_region_id"] == region_id and int(x["voltage_kv"]) == 110]
            planned_start = sum(float(x["simulation_capacity_mva_2021"]) for x in baseline)
        else:
            baseline = read_csv(directory / "city_2021_district_calibration.csv")
            planned_start = sum(float(x["district_calibrated_2021_capacity_mva"])
                                for x in baseline)
        for summary in summaries:
            assert abs(float(summary["baseline_2021_capacity_mva"]) - planned_start) < 1e-6
            assert abs(float(summary["baseline_2021_load_mw"]) - source_load) < 1e-6
            assert abs(float(summary["baseline_2021_clr"]) - planned_start / source_load) < 1e-9
            years = read_csv(directory / f"{summary['scheme']}_years.csv")
            assert len(years) == 4
            for result, letter in zip(years, ("G", "J", "M", "P")):
                source_peak = 10 * float(sheet[f"{letter}{row}"].value)
                assert abs(float(result["net_peak_proxy_mw"]) - source_peak) < 1e-6
                assert abs(float(result["clr"]) -
                           float(result["capacity_mva"]) / source_peak) < 1e-9
        results.append({"region_id": region_id, "workbook": str(SOURCE),
                        "sheet": sheet.title, "source_row": row,
                        "2021_source_capacity_cell": f"C{row}",
                        "2021_source_capacity_mva": source_capacity,
                        "2021_source_load_cell": f"D{row}",
                        "2021_source_load_mw": source_load,
                        "2022_2025_load_cells": ",".join(f"{c}{row}" for c in "GJMP"),
                        "planned_2021_capacity_mva": planned_start,
                        "counterfactual_release_mva": source_capacity - planned_start,
                        "status": "PASS_original_workbook_cells_vs_both_scheme_outputs"})
    (Path(output_file) if output_file else OUTPUT / "two_district_source_audit.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return results


if __name__ == "__main__":
    print(audit())
