"""将市区 29 站样本显式外推至区县原表边界；均属研究性估计。"""

from itertools import combinations_with_replacement

from .annual_no_tie_investment_submodel import LinearModel, YEARS
from .baseline_2021 import read_csv
from .hourly_source_profile import OUTPUT_DIR
from .station_grid_feasibility import AREA_RATINGS, station_metadata


CITY = ("QX-00007", 110)


def calibrate_city(baseline, scenes, peaks, catalog, baseline_cap_mva=None):
    official = {int(r["year"]): float(r["reported_downward_load_mw"])
                for r in read_csv(OUTPUT_DIR / "official_annual.csv")
                if (r["region_id"], int(r["voltage_kv"])) == CITY}
    if set((2021, *YEARS)) - set(official):
        raise ValueError("市区全域原表年度负荷缺失")
    original_peaks = {year: peaks[CITY + (year,)] for year in (2021, *YEARS)}
    local = sorted(k for k in baseline if k[:2] == CITY)
    metadata = station_metadata({k[2] for k in local})
    model = LinearModel()
    choice, options = {}, {}
    for station in local:
        source = baseline[station]
        old = tuple(float(source[f"simulation_unit_{i}_mva"]) for i in (1, 2))
        ceiling = float(source["source_capacity_mva_2025"] or 1e9)
        recommended = set(AREA_RATINGS[metadata[station[2]]["area_class"]])
        options[station] = [pair for pair in combinations_with_replacement(catalog, 2)
                            if all(pair[i] + 1e-8 >= old[i] and
                                   (pair[i] in recommended or pair[i] == old[i]) for i in (0, 1))
                            and sum(pair) <= ceiling + 1e-8]
        if not options[station]:
            raise ValueError(f"市区站 {station[2]} 无基准容量候选")
        for pair in options[station]:
            # 在给定区县基准年容量上限内取较高可行容量，再按设备容量分配。
            shape = float(source["source_capacity_mva_2025"] or sum(old))
            cost = -10000 * sum(pair) + (sum(pair) - shape) ** 2 / shape
            choice[station, pair] = model.variable(cost)
        model.constraint({choice[station, pair]: 1 for pair in options[station]}, lower=1, upper=1)
    # 2022 年全域负荷小于 2021 年；容量不可减少且刚性 R<=2 时，
    # 2021 起点须同时服从全期最低年度峰值，否则 2022 年数学上不可行。
    model.constraint({choice[station, pair]: sum(pair)
                      for station in local for pair in options[station]},
                     upper=min(2 * min(official.values()), baseline_cap_mva or float("inf")))
    solution, _ = model.solve(stage="city_district_2021_baseline")
    adjusted_baseline = dict(baseline)
    trace = []
    for station in local:
        pair = next(pair for pair in options[station] if solution[choice[station, pair]] > .5)
        original = baseline[station]
        updated = dict(original)
        updated["simulation_unit_1_mva"], updated["simulation_unit_2_mva"] = pair
        updated["simulation_capacity_mva_2021"] = sum(pair)
        updated["estimated_forward_peak_mw_2021"] = (
            float(original["estimated_forward_peak_mw_2021"]) *
            official[2021] / original_peaks[2021])
        updated["baseline_selection_rule"] = "city_29_station_sample_scaled_to_official_district_peak_with_research_cap"
        adjusted_baseline[station] = updated
        trace.append({"station": station[2], "source_2021_sample_capacity_mva":
                      original["simulation_capacity_mva_2021"],
                      "district_calibrated_2021_capacity_mva": sum(pair),
                      "district_calibrated_unit_1_mva": pair[0],
                      "district_calibrated_unit_2_mva": pair[1],
                      "source_2025_asset_capacity_mva": original["source_capacity_mva_2025"],
                      "area_class": metadata[station[2]]["area_class"],
                      "area_class_status": metadata[station[2]].get("area_class_status", "source_asset_row"),
                      "source_2021_sample_forward_mw": original["estimated_forward_peak_mw_2021"],
                      "district_calibrated_2021_forward_mw": updated["estimated_forward_peak_mw_2021"],
                      "forward_multiplier_2021": official[2021] / original_peaks[2021],
                      "status": "counterfactual_district_extrapolation_not_observed_station_asset"})
    adjusted_scenes, adjusted_peaks = dict(scenes), dict(peaks)
    for year in (2021, *YEARS):
        adjusted_peaks[CITY + (year,)] = official[year]
        if year == 2021:
            continue
        factor = official[year] / original_peaks[year]
        for station in local:
            updated = dict(scenes[station, year])
            for field in ("estimated_station_forward_peak_mw", "reverse_screen_mw"):
                updated[field] = float(updated[field]) * factor
            adjusted_scenes[station, year] = updated
    return adjusted_baseline, adjusted_scenes, adjusted_peaks, trace
