"""2021 共同起点的区县 110 kV 静态年度规划；全部主变规格进入成本寻优。

这是研究性静态容量筛查，不替代潮流、N-1 或站址与 10 kV 路由校核。
"""

import argparse
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path

from .annual_no_tie_investment_submodel import LinearModel, YEARS
from .baseline_2021 import read_csv
from .city_mapping_audit import write_csv
from .city_district_calibration import calibrate_city
from .cost_references import read_cost_references
from .hourly_source_profile import OUTPUT_DIR
from .incremental_cost import replacement_cost_coefficients, storage_anchors
from .joint_lifecycle_optimizer import cost_factors, load_inputs
from .planning_load_profile import apply_pizhou_weighted_growth
from .pizhou_transfer_fraction import pizhou_sample_fraction
from .station_grid_feasibility import AREA_RATINGS, grid_candidate_rows, station_metadata


REGION = ("QX-00005", 110)
BASELINE = OUTPUT_DIR / "baseline_2021_station_candidates.csv"
OUTPUT = OUTPUT_DIR / "capacity_release_simulation/regional_static_milp_v2"
STORAGE_MWH_PER_MW = 2.15  # 浏阳 1 MW / 最低 2.15 MWh 中标案例的成套功率能量比。
STORAGE_MODULE_MWH = 0.215  # 研究案例单柜 0.1 MW / 0.215 MWh。
STORAGE_MAX_MWH_PER_STATION = 10.75  # 研究性站级配置上界；相当于五套案例包。
LINE_CAPEX_10K = 3 * (0.9 * 24 + 0.1 * 120) + 2 * 3  # 规划 3 km + 两台开关。
LINE_MW_2025 = 7.491
THIRD_UNIT_MVA = 50.0


def input_data(load_scenario: str, region=REGION, city_baseline_cap_mva=None):
    baseline = {(r["study_region_id"], int(r["voltage_kv"]), r["model_station_id"]): r
                for r in read_csv(BASELINE) if (r["study_region_id"], int(r["voltage_kv"])) == region}
    _, scenes, duration, peaks, catalog, _ = load_inputs()
    if load_scenario == "weighted_4y_growth":
        if region != REGION:
            raise ValueError("四年加权增长情景目前只有邳州原表依据")
        scenes, peaks, _, _ = apply_pizhou_weighted_growth(baseline, scenes, peaks)
    elif load_scenario != "observed_annual":
        raise ValueError("未知负荷情景")
    if region[0] == "QX-00007" and region[1] == 110:
        baseline, scenes, peaks, _ = calibrate_city(
            baseline, scenes, peaks, catalog[region], city_baseline_cap_mva)
    coefficient = next(r["base_coefficient_10k_cny_per_purchased_mva"]
                       for r in replacement_cost_coefficients() if r["voltage_kv"] == 110)
    return baseline, scenes, duration, peaks, catalog[region], coefficient


def optimize(scheme: str, load_scenario: str = "observed_annual", elastic_cap: float = 2.4,
             rigid_cap: float = 2.0,
             transformer_scale: float = 1.0, line_scale: float = 1.0,
             storage_scale: float = 1.0, use_new_lines: bool = True,
             max_new_lines: int = 30, station_pairs=None, min_clr: float = 1.8,
             baseline_margin_fraction: float = 0.0,
             reverse_capacity_fraction: float = 1.0,
             outage_recovery_fraction: float = 0.0,
             require_transformer_n1: bool = False,
             n1_load_requirement: str = "full",
             allow_third_transformer: bool = True,
             new_unit_cap_mva: float = 63.0,
             new_unit_rating_policy: str = "by_source_class",
             use_shared_grid_candidates: bool = False,
             require_both_spare_bays: bool = False,
             enforce_expansion_slot: bool = False,
             existing_transfer_fraction: float | None = None,
             target_transfer_fraction: float = 0.30,
             annual_growth_rate: float | None = None,
             source_load_ratio: float | None = None,
             region=REGION,
             city_baseline_cap_mva: float | None = None,
             elastic_use_existing_outage_transfer: bool = False,
             elastic_allow_line_decisions: bool = False,
             annual_clr_floor: dict[int, float] | None = None,
             annual_clr_ceiling: dict[int, float] | None = None):
    if scheme not in ("rigid", "elastic"):
        raise ValueError("scheme 应为 rigid 或 elastic")
    if any(v <= 0 for v in (transformer_scale, line_scale, storage_scale)):
        raise ValueError("成本比例系数须为正")
    if elastic_cap < rigid_cap or not 0 < rigid_cap <= 2 or not 0 <= min_clr <= rigid_cap:
        raise ValueError("容载比扫描边界无效")
    if not 0 <= baseline_margin_fraction <= 1 or not 0 < reverse_capacity_fraction <= 1:
        raise ValueError("裕度或反向筛查比例无效")
    if not 0 <= outage_recovery_fraction <= 1:
        raise ValueError("停运转供比例应在 0～1")
    if n1_load_requirement not in ("full", "bc_min_service_static"):
        raise ValueError("未知 N-1 静态供电量口径")
    if scheme == "elastic" and outage_recovery_fraction and not elastic_allow_line_decisions:
        raise ValueError("弹性方案未建模站间联络，不得声称满足整站停运转供比例")
    if annual_growth_rate is not None and not -.2 <= annual_growth_rate <= .3:
        raise ValueError("年增长率外推范围应在 -20%～30%")
    if source_load_ratio is not None and not 0 <= source_load_ratio <= 4:
        raise ValueError("研究性源荷比外推范围应在 0～4")
    if new_unit_cap_mva not in (63.0, 100.0):
        raise ValueError("新购单台容量上界须为导则推荐 63 MVA 或宽松研究 100 MVA")
    if new_unit_rating_policy not in ("by_source_class", "BC_common", "all_upto_cap"):
        raise ValueError("未知导则单台容量候选规则")
    if existing_transfer_fraction is None:
        existing_transfer_fraction = (float(pizhou_sample_fraction()["initial_fraction"])
                                      if region == REGION else 0.50)
    if region != REGION and target_transfer_fraction == 0.30:
        target_transfer_fraction = 0.50
    if not 0 <= existing_transfer_fraction <= 1 or not 0 <= target_transfer_fraction <= 1:
        raise ValueError("转供比例须位于 0～1")
    baseline, scenes, durations, peaks, catalog, transformer_price = input_data(
        load_scenario, region, city_baseline_cap_mva)
    if annual_growth_rate is not None:
        scenes, peaks = dict(scenes), dict(peaks)
        for year in YEARS:
            factor = (1 + annual_growth_rate) ** (year - 2021)
            peaks[region + (year,)] = peaks[region + (2021,)] * factor
            for station in baseline:
                row = dict(scenes[station, year])
                row["estimated_station_forward_peak_mw"] = (
                    float(baseline[station]["estimated_forward_peak_mw_2021"]) * factor)
                scenes[station, year] = row
    if source_load_ratio is not None:
        # 2025 区县源荷比是研究估计；线性放大各站反向压力仅为条件外推。
        # 不把该映射声称为 DL/T 5729—2023 公式或完整光伏时序仿真。
        scenes = dict(scenes)
        multiplier = source_load_ratio / 1.630652935
        for station in baseline:
            for year in YEARS:
                row = dict(scenes[station, year])
                row["reverse_screen_mw"] = float(row["reverse_screen_mw"]) * multiplier
                scenes[station, year] = row
    stations = sorted(baseline)
    ids = [key[2] for key in stations]
    physical = station_metadata(set(ids))
    grid_rows = grid_candidate_rows(set(ids)) if use_shared_grid_candidates else []
    grid_info = {(row["station_a"], row["station_b"]): row for row in grid_rows}
    tie_decisions = scheme == "rigid" or (scheme == "elastic" and elastic_allow_line_decisions)
    if tie_decisions and use_new_lines:
        if station_pairs is None and use_shared_grid_candidates:
            station_pairs = [pair for pair, row in grid_info.items()
                             if not require_both_spare_bays or row["both_have_spare_bay"]]
        pairs = sorted(tuple(sorted(pair)) for pair in
                       (combinations(ids, 2) if station_pairs is None else station_pairs))
        if len(set(pairs)) != len(pairs) or any(a not in ids or b not in ids or a == b for a, b in pairs):
            raise ValueError("新线站对须唯一且位于当前区县")
    else:
        pairs = []
    cap = rigid_cap if scheme == "rigid" else elastic_cap
    factors = cost_factors()
    third_project_costs = [float(row["static_total_10k_cny"]) for row in read_cost_references()
                           if row["voltage_kv"] == 110
                           and row["measure_type"] == "third_transformer_expansion"
                           and row["purchased_transformer_mva"] == THIRD_UNIT_MVA]
    if len(third_project_costs) != 2:
        raise ValueError("第三台主变必须有两条徐州工程成本依据")
    third_unit_project_capex = sum(third_project_costs) / len(third_project_costs)
    storage_price = storage_anchors()[1] / 2.15  # 万元/MWh；线性规模外推假设。
    model = LinearModel()
    x, replace, energy, third, third_added = {}, {}, {}, {}, {}
    built, added, flow, existing_flow, outage_flow = {}, {}, {}, {}, {}
    for station in stations:
        initial = tuple(float(baseline[station][f"simulation_unit_{slot}_mva"]) for slot in (1, 2))
        for year in YEARS:
            if (allow_third_transformer and
                    (not enforce_expansion_slot or
                     (physical[station[2]]["available_third_slots"] >= 1 and
                      physical[station[2]]["available_third_mva"] >= THIRD_UNIT_MVA))):
                third[station, year] = model.variable(0)
                third_added[station, year] = model.variable(
                    third_unit_project_capex * transformer_scale * factors["transformer"][year])
                third_progress = {third[station, year]: 1, third_added[station, year]: -1}
                if year != YEARS[0]:
                    third_progress[third[station, year - 1]] = -1
                model.constraint(third_progress, lower=0, upper=0)
            energy[station, year] = model.variable(
                STORAGE_MODULE_MWH * storage_price * storage_scale *
                (factors["storage"][year] - factors["storage"].get(year + 1, 0)),
                upper=round(STORAGE_MAX_MWH_PER_STATION / STORAGE_MODULE_MWH))
            if year != YEARS[0]:
                model.constraint({energy[station, year]: 1, energy[station, year - 1]: -1}, lower=0)
            for slot in (0, 1):
                recommended_new = (
                    set(AREA_RATINGS[physical[station[2]]["area_class"]])
                    if new_unit_rating_policy == "by_source_class" else
                    {40.0, 50.0} if new_unit_rating_policy == "BC_common" else
                    {rating for rating in catalog if rating <= new_unit_cap_mva})
                allowed = [rating for rating in catalog
                           if rating + 1e-8 >= initial[slot]
                           and (rating in recommended_new or rating == initial[slot])]
                model.constraint({(x.setdefault((station, slot, year, rating),
                                               model.variable(0))): 1 for rating in allowed}, lower=1, upper=1)
                for rating in allowed:
                    key = station, slot, year, rating
                    replace[key] = model.variable(
                        rating * transformer_price * transformer_scale * factors["transformer"][year],
                        integer=0)
                    terms = {replace[key]: 1, x[key]: -1}
                    if year == YEARS[0]:
                        model.constraint(terms, lower=-float(rating == initial[slot]))
                    elif (station, slot, year - 1, rating) in x:
                        terms[x[station, slot, year - 1, rating]] = 1
                        model.constraint(terms, lower=0)
                    else:
                        model.constraint(terms, lower=0)
                if year != YEARS[0]:
                    monotone = {x[station, slot, year, rating]: rating for rating in allowed}
                    monotone.update({x[station, slot, year - 1, rating]: -rating for rating in allowed})
                    model.constraint(monotone, lower=0)
            order = {x[station, 0, year, rating]: rating for rating in catalog
                     if (station, 0, year, rating) in x}
            order.update({x[station, 1, year, rating]: -rating for rating in catalog
                          if (station, 1, year, rating) in x})
            model.constraint(order, upper=0)

    annual_peak = {year: peaks[region + (year,)] for year in YEARS}
    if tie_decisions:
        existing_limit_2025 = existing_transfer_fraction * annual_peak[2025]
        for year in YEARS:
            ratio = annual_peak[year] / annual_peak[2025]
            for station in stations:
                a = station[2]
                donor_load = float(scenes[station, year]["estimated_station_forward_peak_mw"])
                for b in ids:
                    if a != b:
                        existing_flow[year, a, b] = model.variable(
                            0, upper=existing_transfer_fraction * donor_load, integer=0)
                model.constraint({existing_flow[year, a, b]: 1 for b in ids if a != b},
                                 upper=existing_transfer_fraction * donor_load)
            model.constraint({var: 1 for (yy, _, _), var in existing_flow.items() if yy == year},
                             upper=existing_transfer_fraction * annual_peak[year])
            for pair in pairs:
                built[year, pair] = model.variable(0)
                added[year, pair] = model.variable(
                    LINE_CAPEX_10K * line_scale * factors["line"][year])
                progress = {built[year, pair]: 1, added[year, pair]: -1}
                if year != YEARS[0]:
                    progress[built[year - 1, pair]] = -1
                model.constraint(progress, lower=0, upper=0)
                direction_terms = {built[year, pair]: -LINE_MW_2025 * ratio}
                for a, b in (pair, pair[::-1]):
                    flow[year, pair, a, b] = model.variable(0, upper=LINE_MW_2025 * ratio,
                                                            integer=0)
                    direction_terms[flow[year, pair, a, b]] = 1
                model.constraint(direction_terms, upper=0)
            model.constraint({built[year, pair]: 1 for pair in pairs}, upper=max_new_lines)
            for station in stations:
                station_id = station[2]
                model.constraint({built[year, pair]: LINE_MW_2025 * ratio for pair in pairs
                                  if station_id in pair},
                                 lower=max(0, target_transfer_fraction - existing_transfer_fraction) *
                                 float(scenes[station, year]["estimated_station_forward_peak_mw"]))
                outbound = {v: 1 for (yy, _, a, _), v in flow.items() if yy == year and a == station_id}
                outbound.update({v: 1 for (yy, a, _), v in existing_flow.items()
                                 if yy == year and a == station_id})
                if outbound:
                    model.constraint(outbound, upper=float(scenes[station, year]["estimated_station_forward_peak_mw"]))
    else:
        existing_limit_2025 = 0.0

    if (tie_decisions or (scheme == "elastic" and elastic_use_existing_outage_transfer)) and (
            outage_recovery_fraction or require_transformer_n1):
        # 单座站全停时，经其它站的正常负荷与可用裕度做一跳恢复筛查。
        # 与正常场景的负荷迁移变量分开，且不把它冒称完整 N-1 校核。
        for year in YEARS:
            annual_scale = annual_peak[year] / annual_peak[2025]
            for failed in stations:
                failed_id = failed[2]
                recover = {}
                existing_recover = {}
                failed_load = float(scenes[failed, year]["estimated_station_forward_peak_mw"])
                for recipient in stations:
                    if recipient == failed:
                        continue
                    receiver_id = recipient[2]
                    pair = tuple(sorted((failed_id, receiver_id)))
                    channels = []
                    channels.append(("existing_county_proxy",
                                     existing_transfer_fraction * failed_load, None))
                    if pair in pairs:
                        channels.append(("new", LINE_MW_2025 * annual_scale, built[year, pair]))
                    receiver_supply = {x[recipient, slot, year, rating]: .95 * rating
                                       for slot in (0, 1) for rating in catalog
                                       if (recipient, slot, year, rating) in x}
                    if (recipient, year) in third:
                        receiver_supply[third[recipient, year]] = .95 * THIRD_UNIT_MVA
                    hours = int(durations[recipient]["forward_d95_max_run_hours"])
                    receiver_supply[energy[recipient, year]] = (
                        STORAGE_MODULE_MWH / max(STORAGE_MWH_PER_MW, hours))
                    for kind, line_limit, construction in channels:
                        variable = model.variable(1e-7, upper=line_limit, integer=0)
                        outage_flow[year, failed_id, receiver_id, kind] = variable
                        recover[variable] = 1
                        if kind == "existing_county_proxy":
                            existing_recover[variable] = 1
                        if construction is not None:
                            model.constraint({variable: 1, construction: -line_limit}, upper=0)
                        receiver_supply[variable] = -1
                    if channels:
                        recipient_margin = baseline_margin_fraction * max(
                            0, .95 * sum(float(baseline[recipient][f"simulation_unit_{slot}_mva"])
                                         for slot in (1, 2))
                            - float(baseline[recipient]["estimated_forward_peak_mw_2021"]))
                        model.constraint(receiver_supply,
                                         lower=float(scenes[recipient, year]["estimated_station_forward_peak_mw"])
                                         + recipient_margin)
                model.constraint(existing_recover,
                                 upper=existing_transfer_fraction * failed_load)
                required_recovery = (outage_recovery_fraction *
                                     float(scenes[failed, year]["estimated_station_forward_peak_mw"]))
                if outage_recovery_fraction:
                    model.constraint(recover, lower=required_recovery)
                model.constraint(recover,
                                 upper=float(scenes[failed, year]["estimated_station_forward_peak_mw"]))
                if require_transformer_n1:
                    hours = int(durations[failed]["forward_d95_max_run_hours"])
                    full_demand = float(scenes[failed, year]["estimated_station_forward_peak_mw"])
                    demand = (full_demand if n1_load_requirement == "full" or
                              physical[failed_id]["area_class"] == "A" else
                              max(0, min(full_demand - 12, full_demand * 2 / 3)))
                    for failed_slot in (0, 1, 2) if (failed, year) in third else (0, 1):
                        available = {x[failed, slot, year, rating]: .95 * rating
                                     for slot in (0, 1) if slot != failed_slot
                                     for rating in catalog if (failed, slot, year, rating) in x}
                        available[energy[failed, year]] = (
                            STORAGE_MODULE_MWH / max(STORAGE_MWH_PER_MW, hours))
                        available.update(recover)
                        if (failed, year) in third:
                            if failed_slot == 2:
                                # 第三台尚未投运时，这个停运情景不激活。
                                available[third[failed, year]] = -200.0
                                model.constraint(available, lower=demand - 200.0)
                                continue
                            available[third[failed, year]] = .95 * THIRD_UNIT_MVA
                        model.constraint(available, lower=demand)

    if scheme == "elastic" and require_transformer_n1 and not (
            elastic_use_existing_outage_transfer or elastic_allow_line_decisions):
        for year in YEARS:
            for station in stations:
                hours = int(durations[station]["forward_d95_max_run_hours"])
                full_demand = float(scenes[station, year]["estimated_station_forward_peak_mw"])
                demand = (full_demand if n1_load_requirement == "full" or
                          physical[station[2]]["area_class"] == "A" else
                          max(0, min(full_demand - 12, full_demand * 2 / 3)))
                for failed_slot in (0, 1, 2) if (station, year) in third else (0, 1):
                    available = {x[station, slot, year, rating]: .95 * rating
                                 for slot in (0, 1) if slot != failed_slot
                                 for rating in catalog if (station, slot, year, rating) in x}
                    available[energy[station, year]] = (
                        STORAGE_MODULE_MWH / max(STORAGE_MWH_PER_MW, hours))
                    if (station, year) in third:
                        if failed_slot == 2:
                            available[third[station, year]] = -200.0
                            model.constraint(available, lower=demand - 200.0)
                            continue
                        available[third[station, year]] = .95 * THIRD_UNIT_MVA
                    model.constraint(available, lower=demand)

    for year in YEARS:
        ratio_terms = {}
        for station in stations:
            station_id = station[2]
            for slot in (0, 1):
                for rating in catalog:
                    key = station, slot, year, rating
                    if key in x:
                        ratio_terms[x[key]] = rating
            if (station, year) in third:
                ratio_terms[third[station, year]] = THIRD_UNIT_MVA
            forward = {idx: .95 * value for idx, value in ratio_terms.items()
                       if idx in {x[key] for key in x if key[0] == station and key[2] == year}
                       or idx == third.get((station, year))}
            reverse = {idx: reverse_capacity_fraction * coefficient
                       for idx, coefficient in forward.items()}
            for scenario, terms, demand in (
                ("forward", forward, float(scenes[station, year]["estimated_station_forward_peak_mw"])),
                ("reverse", reverse, float(scenes[station, year]["reverse_screen_mw"])),
            ):
                hours = int(durations[station][f"{scenario}_d95_max_run_hours"])
                terms[energy[station, year]] = (
                    STORAGE_MODULE_MWH / max(STORAGE_MWH_PER_MW, hours))
                if scenario == "forward" and tie_decisions:
                    for (yy, _, a, b), variable in flow.items():
                        if yy == year:
                            if a == station_id:
                                terms[variable] = terms.get(variable, 0) + 1
                            if b == station_id:
                                terms[variable] = terms.get(variable, 0) - 1
                    for (yy, a, b), variable in existing_flow.items():
                        if yy == year:
                            if a == station_id:
                                terms[variable] = terms.get(variable, 0) + 1
                            if b == station_id:
                                terms[variable] = terms.get(variable, 0) - 1
                if scenario == "forward":
                    initial_capacity = sum(float(baseline[station][f"simulation_unit_{slot}_mva"])
                                           for slot in (1, 2))
                    initial_peak = float(baseline[station]["estimated_forward_peak_mw_2021"])
                    demand += baseline_margin_fraction * max(0, .95 * initial_capacity - initial_peak)
                model.constraint(terms, lower=demand)
        model.constraint(ratio_terms, lower=max(min_clr, (annual_clr_floor or {}).get(year, 0)) * annual_peak[year],
                         upper=min(cap, (annual_clr_ceiling or {}).get(year, cap)) * annual_peak[year])
    solution, _ = model.solve(stage=f"{scheme}_{load_scenario}")
    stations_out, years_out, transfers_out, lines_out, outage_out = [], [], [], [], []
    prior_capacity = {station: tuple(float(baseline[station][f"simulation_unit_{slot}_mva"])
                                     for slot in (1, 2)) for station in stations}
    prior_energy = defaultdict(float)
    prior_third = defaultdict(float)
    prior_lines = set()
    for year in YEARS:
        line_set = {pair for pair in pairs if solution[built[year, pair]] > .5}
        for station in stations:
            chosen = tuple(next(rating for rating in catalog
                                if (station, slot, year, rating) in x and
                                solution[x[station, slot, year, rating]] > .5)
                           for slot in (0, 1))
            modules = int(round(float(solution[energy[station, year]])))
            total_energy = STORAGE_MODULE_MWH * modules
            new_energy = max(0, total_energy - prior_energy[station])
            third_unit = THIRD_UNIT_MVA if (station, year) in third and solution[third[station, year]] > .5 else 0.0
            new_third = third_unit - prior_third[station]
            replaced = sum(new for old, new in zip(prior_capacity[station], chosen) if new > old + 1e-6)
            purchased = replaced + new_third
            stations_out.append({"year": year, "station": station[2],
                                 "area_class": physical[station[2]]["area_class"],
                                 "source_available_third_slots": physical[station[2]]["available_third_slots"],
                                 "source_spare_10kv_bays": physical[station[2]]["spare_10kv_bays"],
                                 "new_third_without_reserved_slot": int(
                                     new_third > .5 and physical[station[2]]["available_third_slots"] == 0),
                                 "prior_unit_1_mva": prior_capacity[station][0],
                                 "prior_unit_2_mva": prior_capacity[station][1],
                                 "unit_1_mva": chosen[0], "unit_2_mva": chosen[1],
                                 "unit_3_mva": third_unit,
                                 "third_transformer_commissioned": int(new_third > .5),
                                 "capacity_mva": sum(chosen) + third_unit,
                                 "purchased_unit_mva": purchased,
                                 "transformer_capex_10k": (replaced * transformer_price +
                                                           int(new_third > .5) * third_unit_project_capex) * transformer_scale,
                                 "storage_power_mw": total_energy / STORAGE_MWH_PER_MW,
                                 "storage_energy_mwh": total_energy,
                                 "storage_modules": modules,
                                 "new_storage_power_mw": new_energy / STORAGE_MWH_PER_MW,
                                 "new_storage_energy_mwh": new_energy,
                                 "new_storage_modules": int(round(new_energy / STORAGE_MODULE_MWH)),
                                 "storage_capex_10k": new_energy * storage_price * storage_scale,
                                 "forward_mw": scenes[station, year]["estimated_station_forward_peak_mw"],
                                 "reverse_mw": scenes[station, year]["reverse_screen_mw"],
                                 "forward_duration_h": durations[station]["forward_d95_max_run_hours"],
                                 "reverse_duration_h": durations[station]["reverse_d95_max_run_hours"]})
            prior_capacity[station] = chosen
            prior_third[station] = third_unit
            prior_energy[station] = total_energy
        for (yy, pair, a, b), var in flow.items():
            if yy == year and solution[var] > 1e-6:
                transfers_out.append({"year": year, "kind": "new", "donor": a,
                                      "receiver": b, "mw": float(solution[var]),
                                      "pair": "|".join(pair)})
        for (yy, a, b), var in existing_flow.items():
            if yy == year and solution[var] > 1e-6:
                transfers_out.append({"year": year, "kind": "existing", "donor": a,
                                      "receiver": b, "mw": float(solution[var]),
                                      "pair": "|".join(sorted((a, b)))})
        for (yy, failed_id, receiver_id, kind), var in outage_flow.items():
            if yy == year and solution[var] > 1e-6:
                outage_out.append({"year": year, "failed_station": failed_id,
                                   "receiver_station": receiver_id, "kind": kind,
                                   "recoverable_mw": float(solution[var]),
                                   "scope": "one_hop_station_outage_capacity_proxy"})
        for pair in sorted(line_set - prior_lines):
            grid_row = grid_info.get(pair, {}) if use_shared_grid_candidates else {}
            lines_out.append({"commissioning_year": year, "station_a": pair[0],
                              "station_b": pair[1], "planned_length_km": 3.0,
                              "length_status": "uniform_cost_scenario_not_measured_distance",
                              "shared_grid_evidence": grid_row.get("shared_grid", ""),
                              "both_have_spare_bay": grid_row.get("both_have_spare_bay", ""),
                              "screen_capacity_mw_2025": LINE_MW_2025,
                              "construction_capex_10k": LINE_CAPEX_10K * line_scale,
                              "route_status": "equivalent_station_transfer_channel_no_actual_route"})
        local = [row for row in stations_out if row["year"] == year]
        years_out.append({"year": year, "scheme": scheme, "load_scenario": load_scenario,
                          "net_peak_proxy_mw": annual_peak[year],
                          "capacity_mva": sum(row["capacity_mva"] for row in local),
                          "clr": sum(row["capacity_mva"] for row in local) / annual_peak[year],
                          "new_transformer_purchase_mva": sum(row["purchased_unit_mva"] for row in local),
                          "new_third_transformers": sum(row["third_transformer_commissioned"] for row in local),
                          "new_third_without_reserved_slot": sum(
                              row["new_third_without_reserved_slot"] for row in local),
                          "new_storage_power_mw": sum(row["new_storage_power_mw"] for row in local),
                          "new_storage_energy_mwh": sum(row["new_storage_energy_mwh"] for row in local),
                          "new_storage_modules": sum(row["new_storage_modules"] for row in local),
                          "installed_storage_power_mw": sum(row["storage_power_mw"] for row in local),
                          "installed_storage_energy_mwh": sum(row["storage_energy_mwh"] for row in local),
                          "installed_storage_modules": sum(row["storage_modules"] for row in local),
                          "existing_transfer_mw": sum(row["mw"] for row in transfers_out
                                                      if row["year"] == year and row["kind"] == "existing"),
                          "new_line_transfer_mw": sum(row["mw"] for row in transfers_out
                                                      if row["year"] == year and row["kind"] == "new"),
                          "new_lines_in_service": len(line_set),
                          "new_lines_commissioned": len(line_set - prior_lines),
                          "transformer_capex_10k": sum(row["transformer_capex_10k"] for row in local),
                          "storage_capex_10k": sum(row["storage_capex_10k"] for row in local),
                          "line_capex_10k": len(line_set - prior_lines) * LINE_CAPEX_10K * line_scale})
        prior_lines = line_set
    actual_npv = sum((r["transformer_capex_10k"] * factors["transformer"][r["year"]]
                      + r["storage_capex_10k"] * factors["storage"][r["year"]]
                      + r["line_capex_10k"] * factors["line"][r["year"]]) for r in years_out)
    summary = {"scheme": scheme, "load_scenario": load_scenario,
               "region_id": region[0], "voltage_kv": region[1], "cap": cap,
               "city_baseline_cap_mva": city_baseline_cap_mva,
               "baseline_2021_capacity_mva": sum(float(r["simulation_capacity_mva_2021"])
                                                   for r in baseline.values()),
               "baseline_2021_load_mw": peaks[region + (2021,)],
               "baseline_2021_clr": (sum(float(r["simulation_capacity_mva_2021"])
                                         for r in baseline.values()) / peaks[region + (2021,)]),
               "station_count": len(stations),
               "min_clr": min_clr, "objective_npv_10k": actual_npv,
               "annual_clr_floor": annual_clr_floor or {},
               "annual_clr_ceiling": annual_clr_ceiling or {},
               "mip_gap": model.solve_history[-1]["mip_gap"],
               "solver_status": model.solve_history[-1]["status"],
               "candidate_pairs": len(pairs), "catalog": catalog,
               "transformer_price_10k_per_purchased_mva": transformer_price,
               "third_50mva_project_price_10k": third_unit_project_capex,
               "allow_third_transformer": allow_third_transformer,
               "new_unit_cap_mva": new_unit_cap_mva,
               "new_unit_rating_policy": new_unit_rating_policy,
               "use_shared_grid_candidates": use_shared_grid_candidates,
               "require_both_spare_bays": require_both_spare_bays,
               "enforce_expansion_slot": enforce_expansion_slot,
               "unreserved_third_site_cost_status": "not_included_no_source_capex",
               "transformer_scale": transformer_scale,
               "line_scale": line_scale,
               "storage_scale": storage_scale,
               "storage_price_10k_per_mwh": storage_price,
               "storage_module_mwh": STORAGE_MODULE_MWH,
               "line_price_10k_per_planned_pair": LINE_CAPEX_10K,
               "existing_transfer_limit_2025_mw": existing_limit_2025,
               "existing_transfer_fraction": existing_transfer_fraction,
               "target_transfer_fraction": target_transfer_fraction,
               "existing_transfer_scope": "sample_ratio_extrapolated_to_county_all_station_pairs"
               if region == REGION else "meeting_assumed_city_50pct_all_station_pairs",
               "baseline_margin_fraction": baseline_margin_fraction,
               "reverse_capacity_fraction": reverse_capacity_fraction,
               "outage_recovery_fraction": outage_recovery_fraction,
               "require_transformer_n1_static_proxy": require_transformer_n1,
               "n1_load_requirement": n1_load_requirement,
               "elastic_use_existing_outage_transfer": elastic_use_existing_outage_transfer,
               "elastic_allow_line_decisions": elastic_allow_line_decisions,
               "annual_growth_rate_scenario": annual_growth_rate,
               "source_load_ratio_scenario": source_load_ratio,
               "source_load_reverse_proxy_mapping": (
                   "station_reverse_mw_times_scenario_ratio_over_2025_estimated_1.630652935"
                   if source_load_ratio is not None else "no_override"),
               "source_scope": ("2021_counterfactual_baseline;_official_district_downward_load_proxy;"
                                "_29_station_sample_extrapolated_to_district"
                                if region[0] == "QX-00007" else
                                "2021_counterfactual_baseline;_official_district_downward_load_proxy;"
                                "_pizhou_sample_tie_ratio_extrapolated_to_county")}
    return summary, years_out, stations_out, transfers_out, lines_out, outage_out


def run(output_dir: Path = OUTPUT, load_scenario: str = "observed_annual",
        schemes=("rigid", "elastic"), scheme_kwargs=None, **kwargs):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if kwargs.get("region", REGION) == ("QX-00007", 110):
        source_baseline = {(r["study_region_id"], int(r["voltage_kv"]), r["model_station_id"]): r
                           for r in read_csv(BASELINE)}
        _, source_scenes, _, source_peaks, catalogs, _ = load_inputs()
        _, _, _, city_trace = calibrate_city(source_baseline, source_scenes,
                                              source_peaks, catalogs[("QX-00007", 110)],
                                              kwargs.get("city_baseline_cap_mva"))
        write_csv(city_trace, output_dir / "city_2021_district_calibration.csv")
    summaries = []
    for scheme in schemes:
        print(f"START {scheme} {load_scenario}", flush=True)
        local_kwargs = {**kwargs, **(scheme_kwargs or {}).get(scheme, {})}
        summary, years, stations, transfers, lines, outage = optimize(scheme, load_scenario,
                                                                       **local_kwargs)
        write_csv(years, output_dir / f"{scheme}_years.csv")
        write_csv(stations, output_dir / f"{scheme}_stations.csv")
        if transfers:
            write_csv(transfers, output_dir / f"{scheme}_transfers.csv")
        if lines:
            write_csv(lines, output_dir / f"{scheme}_new_lines.csv")
        if outage:
            write_csv(outage, output_dir / f"{scheme}_outage_flows.csv")
        summaries.append(summary)
        print(f"DONE {scheme}: {summary['objective_npv_10k']:.3f} 万元", flush=True)
    (output_dir / "summary.json").write_text(json.dumps(summaries, ensure_ascii=False, indent=2) + "\n",
                                               encoding="utf-8")
    return summaries


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scheme", choices=("rigid", "elastic", "both"), default="both")
    parser.add_argument("--load-scenario", choices=("observed_annual", "weighted_4y_growth"),
                        default="observed_annual")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    parser.add_argument("--require-transformer-n1", action="store_true")
    parser.add_argument("--n1-load-requirement", choices=("full", "bc_min_service_static"),
                        default="full")
    parser.add_argument("--outage-recovery-fraction", type=float, default=0.0)
    parser.add_argument("--elastic-cap", type=float, default=2.4)
    parser.add_argument("--new-unit-cap-mva", type=float, default=63.0)
    parser.add_argument("--new-unit-rating-policy",
                        choices=("by_source_class", "BC_common", "all_upto_cap"),
                        default="by_source_class")
    parser.add_argument("--use-shared-grid-candidates", action="store_true")
    parser.add_argument("--require-both-spare-bays", action="store_true")
    parser.add_argument("--enforce-expansion-slots", action="store_true")
    parser.add_argument("--max-new-lines", type=int, default=30)
    args = parser.parse_args()
    run(args.output_dir, args.load_scenario,
        schemes=("rigid", "elastic") if args.scheme == "both" else (args.scheme,),
        require_transformer_n1=args.require_transformer_n1,
        n1_load_requirement=args.n1_load_requirement,
        outage_recovery_fraction=args.outage_recovery_fraction,
        elastic_cap=args.elastic_cap,
        new_unit_cap_mva=args.new_unit_cap_mva,
        new_unit_rating_policy=args.new_unit_rating_policy,
        use_shared_grid_candidates=args.use_shared_grid_candidates,
        require_both_spare_bays=args.require_both_spare_bays,
        enforce_expansion_slot=args.enforce_expansion_slots,
        max_new_lines=args.max_new_lines)
