"""从区县原表构造四年加权增长率的规划负荷敏感性场景。"""

from .baseline_2021 import read_csv
from .hourly_source_profile import OUTPUT_DIR


PIZHOU = ("QX-00005", 110)
YEARS = (2022, 2023, 2024, 2025)


def weighted_annual_growth(annual_load: dict[int, float]) -> tuple[float, list[dict]]:
    rates = []
    for weight, year in enumerate(YEARS, start=1):
        rate = annual_load[year] / annual_load[year - 1] - 1
        rates.append({"year": year, "weight": weight, "observed_growth_rate": rate,
                      "previous_load_mw": annual_load[year - 1],
                      "current_load_mw": annual_load[year]})
    return sum(r["weight"] * r["observed_growth_rate"] for r in rates) / 10, rates


def apply_pizhou_weighted_growth(baseline: dict, scenes: dict, peaks: dict):
    annual_load = {int(r["year"]): float(r["reported_downward_load_mw"])
                   for r in read_csv(OUTPUT_DIR / "official_annual.csv")
                   if r["region_id"] == PIZHOU[0] and int(r["voltage_kv"]) == 110}
    growth, source_rows = weighted_annual_growth(annual_load)
    adjusted_scenes = dict(scenes)
    adjusted_peaks = dict(peaks)
    profile = []
    for year in YEARS:
        factor = (1 + growth) ** (year - 2021)
        adjusted_peaks[PIZHOU + (year,)] = annual_load[2021] * factor
        profile.append({"year": year, "original_annual_load_mw": annual_load[year],
                        "weighted_growth_planning_load_mw": adjusted_peaks[PIZHOU + (year,)],
                        "growth_rate": growth,
                        "formula": "P_2021*(1+sum(weight_y*(P_y/P_(y-1)-1))/10)^(y-2021)",
                        "source_cells": "近5年容载比.xlsx::Sheet1!D19,G19,J19,M19,P19×10",
                        "status": "four_year_weighted_growth_forecast_sensitivity_not_observed_load"})
        for station in (s for s in baseline if s[:2] == PIZHOU):
            row = dict(scenes[station, year])
            row["estimated_station_forward_peak_mw"] = (
                float(baseline[station]["estimated_forward_peak_mw_2021"]) * factor)
            adjusted_scenes[station, year] = row
    return adjusted_scenes, adjusted_peaks, profile, source_rows
