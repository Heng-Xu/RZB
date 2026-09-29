"""两电压独立的年度离散措施与全寿命成本 MILP；联络仅为源端静态仿真。"""

import argparse
import csv
import json
from collections import defaultdict
from itertools import combinations, combinations_with_replacement
from pathlib import Path

import numpy as np

from .annual_no_tie_investment_submodel import (
    BASELINE, CAP, FORWARD_LAYERS, STORAGE_SCREEN,
    TRANSFORMER_PATH, YEARS, LinearModel, storage_affine_cost_parts,
    storage_effective_power_per_module,
)
from .baseline_2021 import local_unit_catalog, read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .incremental_cost import (
    LINE_BASE_10K_PER_KM, lifecycle_cashflows, line_capex_10k_cny,
    npv_10k_cny, replacement_cost_coefficients, storage_replicated_package_capex_10k_cny,
)
from .pizhou_existing_ties import build_feeder_headroom, read_cross_station_ties
from .new_line_section_audit import designed_new_line_section
from .tie_section_audit import transferable_section


PIZHOU_110 = ("QX-00005", 110)
NEW_LINE_KM = 2.5  # 旧案例候选走廊的规划估计，非测绘里程。
NEW_LINE_FEEDERS = ("PZXL-00099", "PZXL-00154")
DESIGNED_NEW_LINE_ID = "SIM-NEW-DZHEN-RIVER-BUS"
DESIGNED_BUS_FEEDER_ID = "SIM-RIVER-NEW-FEEDER"
DESIGNED_NEW_LINE_KM = 3.0  # 无测绘路线，长度只作为待敏感性检验的仿真基准。
DESIGNED_NEW_LINE_LIMIT_MW = 9.05  # 9.53 MVA 同型导线×0.95 的线端上界。
EXISTING_OPERATIONAL_TIE = "T01"  # 旧案例 TIE-002；墩南线 -> 河炮线。
EXISTING_OPERATIONAL_DIRECTION = ("PZXL-00092", "PZXL-00161")
EXISTING_PATH_CAP_MW = 4.75  # 旧案例完整馈线最弱热限的保守容量包络。
RIGID_2025_FORWARD_OPERATION_MW = transferable_section()["2025_feeder_stress_section_p_seed_mw"]
TECHNICAL_SCOPE = "station_aggregate_and_feeder_source_end_static_proxy_not_DLT2041_certification"
MAX_PLANNING_STORAGE_MODULES = 50  # 新增长模型可扩至五组 10 柜包。
STORAGE_PACKAGE_SIZE = 10


def npv_factor(year: int, rate: float, life: int, om: float) -> float:
    return npv_10k_cny(lifecycle_cashflows(1.0, year, life, om), rate)


def cost_factors(rate: float = 0.06, transformer_life: int = 20,
                 line_life: int = 20, storage_life: int = 10,
                 network_om: float = 0.01, storage_om: float = 0.03) -> dict:
    if rate < 0 or any(v <= 0 for v in (transformer_life, line_life, storage_life)):
        raise ValueError("折现率和寿命参数无效")
    if network_om < 0 or storage_om < 0:
        raise ValueError("运维率不得为负")
    return {
        "transformer": {y: npv_factor(y, rate, transformer_life, network_om) for y in YEARS},
        "line": {y: npv_factor(y, rate, line_life, network_om) for y in YEARS},
        "storage": {y: npv_factor(y, rate, storage_life, storage_om) for y in YEARS},
        "discount_rate": rate, "transformer_life_years": transformer_life,
        "line_life_years": line_life, "storage_life_years": storage_life,
        "network_fixed_om_rate": network_om, "storage_fixed_om_rate": storage_om,
    }


def load_inputs(reverse_variant: str = "night_central") -> tuple[dict, dict, dict, dict, dict, dict]:
    baseline = {(r["study_region_id"], int(r["voltage_kv"]), r["model_station_id"]): r
                for r in read_csv(BASELINE)}
    scene = {((r["study_region_id"], int(r["voltage_kv"]), r["model_station_id"]), int(r["year"])): r
             for r in read_csv(TRANSFORMER_PATH)
             if r["reverse_variant"] == reverse_variant and int(r["year"]) in YEARS}
    durations = {(r["study_region_id"], int(r["voltage_kv"]), r["model_station_id"]): r
                 for r in read_csv(STORAGE_SCREEN)
                 if r["capacity_case"] == "hold_2021_simulation_capacity"}
    peaks = {(r["study_region_id"], int(r["voltage_kv"]), int(r["year"])):
             float(r["estimated_synchronous_forward_peak_mw"])
             for r in read_csv(FORWARD_LAYERS) if int(r["year"]) in (2021, *YEARS)}
    catalog = local_unit_catalog()
    coefficients = {r["voltage_kv"]: r["base_coefficient_10k_cny_per_purchased_mva"]
                    for r in replacement_cost_coefficients()}
    return baseline, scene, durations, peaks, catalog, coefficients


def tie_edges(include_new_line: bool = False,
              new_line_variant: str = "legacy",
              include_existing_tie: bool = True) -> tuple[list[dict], dict]:
    feeders = {r["feeder_id"]: r for r in build_feeder_headroom()}
    edges = []
    for tie in read_cross_station_ties() if include_existing_tie else []:
        if tie["tie_id"] != EXISTING_OPERATIONAL_TIE:
            continue  # 其余跨站联络端点或设备链未闭合，不进入基准可行集。
        edges.append({"tie_id": tie["tie_id"], "a": tie["from_feeder_id"],
                      "b": tie["to_feeder_id"], "new": False,
                      "path_cap_mw": EXISTING_PATH_CAP_MW})
    if include_new_line:
        if new_line_variant == "legacy":
            edges.append({"tie_id": "SIM-NEW-01", "a": NEW_LINE_FEEDERS[0],
                          "b": NEW_LINE_FEEDERS[1], "new": True,
                          "path_cap_mw": 4.0})  # 老候选仅有馈线配对，端点未闭合。
        elif new_line_variant == "designed_bus":
            feeders[DESIGNED_BUS_FEEDER_ID] = {
                "feeder_id": DESIGNED_BUS_FEEDER_ID,
                "station_id": "BDZ-00048",
                "current_equivalent_active_power_mw": 0.0,
                "receiving_current_headroom_mw": DESIGNED_NEW_LINE_LIMIT_MW,
            }
            edges.append({"tie_id": DESIGNED_NEW_LINE_ID, "a": "PZXL-00099",
                          "b": DESIGNED_BUS_FEEDER_ID, "new": True,
                          "path_cap_mw": DESIGNED_NEW_LINE_LIMIT_MW})
        else:
            raise ValueError("未知新线候选类型")
    if edges and {feeders[e[k]]["station_id"] for e in edges for k in ("a", "b")} != {"BDZ-00027", "BDZ-00048"}:
        raise ValueError("联络边界不在邳州确认的两座 110 kV 站内")
    return edges, feeders


def solve_layer(layer: tuple[str, int], baseline: dict, scene: dict, durations: dict,
                peaks: dict, catalog: dict, coefficients: dict, factors: dict,
                cap: float, rigid: bool, include_new_line: bool = False,
                line_km: float = NEW_LINE_KM, line_unit_cost: float = LINE_BASE_10K_PER_KM,
                line_extra_capex_10k_cny: float = 0.0,
                new_line_variant: str = "legacy",
                tie_allowed: bool | None = None, transformer_cost_scale: float = 1.0,
                storage_cost_scale: float = 1.0,
                replaced_unit_credit_fraction: float = 0.0,
                tie_transfer_limit_scale: float = 1.0,
                capacity_first: bool = False,
                preserve_baseline_forward_margin: bool = False,
                baseline_margin_fraction: float = 1.0,
                policy_peak_basis: str = "annual",
                max_storage_modules: int = 10,
                require_existing_tie_operation: bool = True,
                existing_tie_allowed: bool = True,
                new_line_section_coincidence: float = 1.0,
                tie_year_basis: str = "2025_only",
                canonicalize_tie_dispatch: bool = False,
                preserve_prior_year_forward_margin: bool = False,
                allow_capacity_release: bool = False,
                capacity_growth_budget_fraction: float | None = None,
                minimum_clr_by_year: dict[int, float] | None = None,
                prefer_reserve_at_equal_cost: bool = False,
                contingency_service_fraction: float | None = None,
                regional_transfer: dict | None = None,
                station_choice_cap_slack_mva: float | None = None) -> tuple[list[dict], list[dict], list[dict], dict]:
    if cap < CAP or (rigid and cap != CAP):
        raise ValueError("刚性上限必须为 2.0，弹性扫描不得低于 2.0")
    if transformer_cost_scale <= 0 or storage_cost_scale <= 0:
        raise ValueError("成本情景系数必须为正")
    if not 0 <= replaced_unit_credit_fraction <= 1:
        raise ValueError("被替换主变的回收抵扣比例须在 0—1 之间")
    if not 0 <= tie_transfer_limit_scale <= 1:
        raise ValueError("联络可转供比例须在 0—1 之间")
    if policy_peak_basis not in ("annual", "rolling_max"):
        raise ValueError("容载比控制分母只支持 annual 或 rolling_max")
    if not 0 <= baseline_margin_fraction <= 1:
        raise ValueError("基期正向裕度保留比例须在0—1之间")
    if not 1 <= max_storage_modules <= MAX_PLANNING_STORAGE_MODULES or max_storage_modules % 10:
        raise ValueError("单站储能模块上限须为 10、20、30、40 或 50")
    if line_extra_capex_10k_cny < 0:
        raise ValueError("新线附加工程费用不能为负")
    if not 0 < new_line_section_coincidence <= 1:
        raise ValueError("新线转供区段同时率须在 (0,1] 内")
    if tie_year_basis not in ("2025_only", "annual_station_scaled"):
        raise ValueError("10 kV 区段年度口径未知")
    if capacity_growth_budget_fraction is not None and capacity_growth_budget_fraction < 0:
        raise ValueError("容量增长预算不能为负")
    if station_choice_cap_slack_mva is not None and station_choice_cap_slack_mva < 0:
        raise ValueError("站级候选容量余量不能为负")
    minimum_clr_by_year = minimum_clr_by_year or {}
    if any(year not in YEARS or value < 0 or value > cap
           for year, value in minimum_clr_by_year.items()):
        raise ValueError("年度容载比下限必须位于规划期且不超过方案上限")
    if contingency_service_fraction is not None and not 0 < contingency_service_fraction <= 1:
        raise ValueError("主变停运后的恢复负荷比例须在 (0,1] 内")
    if regional_transfer is not None:
        initial_fraction = float(regional_transfer["initial_fraction"])
        maximum_fraction = float(regional_transfer["maximum_fraction"])
        line_capacity = float(regional_transfer["line_capacity_mw"])
        line_capacity_by_year = regional_transfer.get("line_capacity_mw_by_year") or {}
        if any(float(value) < 0 for value in line_capacity_by_year.values()):
            raise ValueError("逐年新线可转移功率不能为负")
        max_lines = int(regional_transfer["max_lines"])
        existing_capacity_mw = regional_transfer.get("existing_capacity_mw")
        existing_capacity_by_year = regional_transfer.get("existing_capacity_mw_by_year") or {}
        if any(float(value) < 0 for value in existing_capacity_by_year.values()):
            raise ValueError("逐年既有转供功率上限不能为负")
        if existing_capacity_mw is not None:
            existing_capacity_mw = float(existing_capacity_mw)
            if existing_capacity_mw < 0:
                raise ValueError("既有线路可转移功率上限不能为负")
        new_line_station_pair = regional_transfer.get("new_line_station_pair")
        existing_station_pair = regional_transfer.get("existing_station_pair")
        if existing_station_pair is not None and (len(existing_station_pair) != 2
                or existing_station_pair[0] == existing_station_pair[1]):
            raise ValueError("既有联络端点必须为两个不同站点")
        if new_line_station_pair is not None and (len(new_line_station_pair) != 2
                or new_line_station_pair[0] == new_line_station_pair[1]
                or max_lines > 1):
            raise ValueError("已指定站间新线仅支持一条、两个不同的候选端点")
        if not 0 <= initial_fraction <= maximum_fraction <= 1:
            raise ValueError("区域可转移比例须满足 0≤初始值≤上限≤1")
        if line_capacity <= 0 or max_lines < 0:
            raise ValueError("区域新增线路容量及数量无效")
    pairwise_regional_transfer = bool(regional_transfer and regional_transfer.get("pairwise"))
    if pairwise_regional_transfer and regional_transfer.get("existing_station_pair") is None:
        raise ValueError("站对联络模型须指定有原始记录的既有联络站对")
    stations = sorted(s for s in baseline if s[:2] == layer)
    if regional_transfer is not None and new_line_station_pair is not None:
        station_ids = {s[2] for s in stations}
        if not set(new_line_station_pair) <= station_ids:
            raise ValueError("候选新线端点不在本区域站点清单")
    if regional_transfer is not None and existing_station_pair is not None:
        station_ids = {s[2] for s in stations}
        if not set(existing_station_pair) <= station_ids:
            raise ValueError("既有联络端点不在本区域站点清单")
    model = LinearModel()
    fixed, slope = storage_affine_cost_parts()
    fixed *= storage_cost_scale
    slope *= storage_cost_scale
    x, t, n, b, choices = {}, {}, {}, {}, {}
    for s in stations:
        initial = tuple(float(baseline[s][f"simulation_unit_{i}_mva"]) for i in (1, 2))
        for y in YEARS:
            pairs = [p for p in combinations_with_replacement(catalog[layer], 2)
                     if allow_capacity_release or all(v >= old for old, v in zip(initial, p))]
            if station_choice_cap_slack_mva is not None and not allow_capacity_release:
                base_peak = float(baseline[s]["estimated_forward_peak_mw_2021"])
                base_margin = max(0.0, .95 * sum(initial) - base_peak)
                required_capacity = max(
                    max((float(scene[s, yy]["estimated_station_forward_peak_mw"])
                         + (baseline_margin_fraction * base_margin
                            if preserve_baseline_forward_margin else 0.0)) / .95
                        for yy in YEARS),
                    max(float(scene[s, yy]["reverse_screen_mw"]) / (.8 * .95)
                        for yy in YEARS),
                    sum(initial),
                )
                sufficient = [sum(p) for p in pairs if sum(p) + 1e-8 >= required_capacity]
                if sufficient:
                    cutoff = min(sufficient) + station_choice_cap_slack_mva
                    pairs = [p for p in pairs if sum(p) <= cutoff + 1e-8]
            if not pairs:
                raise ValueError(f"{s} 无主变候选")
            choices[s, y] = pairs
            for p in pairs:
                x[s, y, p] = model.variable(0)
            # 存量变量的目标系数差分，严格等于新增柜在投运年的全寿命成本。
            f = factors["storage"][y] - factors["storage"].get(y + 1, 0)
            n[s, y] = model.variable(slope * f, upper=max_storage_modules)
            b[s, y] = model.variable(fixed * f,
                                     upper=max_storage_modules // STORAGE_PACKAGE_SIZE)
            previous = [initial] if y == YEARS[0] else choices[s, y - 1]
            for before in previous:
                for after in pairs:
                    if allow_capacity_release or all(v >= old for old, v in zip(before, after)):
                        purchased = sum(v - replaced_unit_credit_fraction * old
                                        for old, v in zip(before, after) if v > old)
                        t[s, y, before, after] = model.variable(
                            purchased * coefficients[layer[1]] * transformer_cost_scale * factors["transformer"][y])

    for s in stations:
        initial = tuple(float(baseline[s][f"simulation_unit_{i}_mva"]) for i in (1, 2))
        for y in YEARS:
            pairs = choices[s, y]
            model.constraint({x[s, y, p]: 1 for p in pairs}, lower=1, upper=1)
            previous = [initial] if y == YEARS[0] else choices[s, y - 1]
            for before in previous:
                terms = {t[s, y, before, after]: 1 for after in pairs if (s, y, before, after) in t}
                if y == YEARS[0]:
                    model.constraint(terms, lower=1, upper=1)
                else:
                    terms[x[s, y - 1, before]] = -1
                    model.constraint(terms, lower=0, upper=0)
            for after in pairs:
                terms = {t[s, y, before, after]: 1 for before in previous if (s, y, before, after) in t}
                terms[x[s, y, after]] = -1
                model.constraint(terms, lower=0, upper=0)
            model.constraint({n[s, y]: 1, b[s, y]: -STORAGE_PACKAGE_SIZE}, upper=0)
            model.constraint({n[s, y]: 1, b[s, y]: -STORAGE_PACKAGE_SIZE}, lower=1 - STORAGE_PACKAGE_SIZE)
            if y > YEARS[0]:
                model.constraint({n[s, y]: 1, n[s, y - 1]: -1}, lower=0)
                model.constraint({b[s, y]: 1, b[s, y - 1]: -1}, lower=0)

    use_tie = rigid if tie_allowed is None else tie_allowed
    edges, feeders = (tie_edges(include_new_line, new_line_variant, existing_tie_allowed)
                      if use_tie and layer == PIZHOU_110 and regional_transfer is None else ([], {}))
    measure_scope = ("transformer_storage_and_regional_10kv_transfer" if regional_transfer is not None
                     else "transformer_storage_and_pizhou_ties" if edges else "transformer_storage_no_ties")
    transfer, direction, built, line_addition, section_active = {}, {}, {}, {}, {}
    if pairwise_regional_transfer:
        station_ids = sorted(s[2] for s in stations)
        for station_id in station_ids:
            feeders[station_id] = {"station_id": station_id}
        candidate_pairs = [tuple(pair) for pair in regional_transfer.get("new_line_candidate_pairs")
                           or combinations(station_ids, 2)]
        if any(len(pair) != 2 or pair[0] == pair[1] or not set(pair) <= set(station_ids)
               for pair in candidate_pairs):
            raise ValueError("新建联络候选站对不在区域站点清单")
        candidate_pairs = sorted({tuple(sorted(pair)) for pair in candidate_pairs})
        pair_built, pair_addition = {}, {}
        for y in YEARS:
            built[y] = model.variable(0, upper=max_lines, integer=1)
            line_addition[y] = model.variable(
                (line_capex_10k_cny(line_km, line_unit_cost) + line_extra_capex_10k_cny)
                * factors["line"][y], upper=max_lines, integer=1)
            count_built, count_added = {built[y]: -1}, {line_addition[y]: -1}
            for pair in candidate_pairs:
                pair_built[y, pair] = model.variable(0)
                pair_addition[y, pair] = model.variable(0)
                count_built[pair_built[y, pair]] = 1
                count_added[pair_addition[y, pair]] = 1
                previous = {pair_built[y, pair]: 1, pair_addition[y, pair]: -1}
                if y > YEARS[0]:
                    previous[pair_built[y - 1, pair]] = -1
                model.constraint(previous, lower=0, upper=0)
            model.constraint(count_built, lower=0, upper=0)
            model.constraint(count_added, lower=0, upper=0)
            for scenario in ("forward", "reverse"):
                field = ("estimated_station_forward_peak_mw" if scenario == "forward"
                         else "reverse_screen_mw")
                demand = {s[2]: max(0.0, float(scene[s, y][field])) for s in stations}
                donor_existing, donor_new = defaultdict(dict), defaultdict(dict)
                existing_pair = tuple(regional_transfer["existing_station_pair"])
                existing_limit = float(existing_capacity_by_year.get(y,
                                          existing_capacity_mw if existing_capacity_mw is not None else 0.0))
                existing_terms = {}
                for donor, receiver in (existing_pair, existing_pair[::-1]):
                    flow = model.variable(0, upper=min(demand[donor], existing_limit), integer=0)
                    transfer[y, scenario, "REGIONAL-existing", donor, receiver] = flow
                    donor_existing[donor][flow] = 1
                    existing_terms[flow] = 1
                model.constraint(existing_terms, upper=existing_limit)
                line_limit = float(line_capacity_by_year.get(y, line_capacity))
                for pair in candidate_pairs:
                    pair_terms = {pair_built[y, pair]: -line_limit}
                    for donor, receiver in (pair, pair[::-1]):
                        flow = model.variable(0, upper=min(demand[donor], line_limit), integer=0)
                        transfer[y, scenario, "REGIONAL-new", donor, receiver] = flow
                        donor_new[donor][flow] = 1
                        pair_terms[flow] = 1
                    model.constraint(pair_terms, upper=0)
                for station_id in station_ids:
                    model.constraint({**donor_existing[station_id], **donor_new[station_id]},
                                     upper=demand[station_id])
    elif regional_transfer is not None:
        for s in stations:
            feeders[s[2]] = {"station_id": s[2]}
        feeders["REGIONAL-EXISTING-HUB"] = {"station_id": "REGIONAL-HUB"}
        feeders["REGIONAL-NEW-HUB"] = {"station_id": "REGIONAL-HUB"}
        for y in YEARS:
            built[y] = model.variable(0, upper=max_lines, integer=1)
            line_addition[y] = model.variable(
                (line_capex_10k_cny(line_km, line_unit_cost) + line_extra_capex_10k_cny)
                * factors["line"][y], upper=max_lines, integer=1)
            cumulative = {built[y]: 1, line_addition[y]: -1}
            if y > YEARS[0]:
                cumulative[built[y - 1]] = -1
            model.constraint(cumulative, lower=0, upper=0)
            for scenario in ("forward", "reverse"):
                for kind, hub in (("existing", "REGIONAL-EXISTING-HUB"),
                                  ("new", "REGIONAL-NEW-HUB")):
                    balance = {}
                    new_out = {}
                    existing_out = {}
                    for s in stations:
                        station_id = s[2]
                        demand_field = ("estimated_station_forward_peak_mw" if scenario == "forward"
                                        else "reverse_screen_mw")
                        station_demand = max(0.0, float(scene[s, y][demand_field]))
                        fraction = (initial_fraction if kind == "existing" else
                                    maximum_fraction - initial_fraction)
                        pair = existing_station_pair if kind == "existing" else new_line_station_pair
                        eligible = pair is None or station_id in pair
                        outgoing = model.variable(0, upper=fraction * station_demand if eligible else 0, integer=0)
                        incoming = model.variable(0, upper=(sum(max(0.0, float(scene[z, y][demand_field]))
                                                               for z in stations) if eligible else 0), integer=0)
                        transfer[y, scenario, f"REGIONAL-{kind}", station_id, hub] = outgoing
                        transfer[y, scenario, f"REGIONAL-{kind}", hub, station_id] = incoming
                        balance[outgoing] = 1
                        balance[incoming] = -1
                        if kind == "new":
                            new_out[outgoing] = 1
                        else:
                            existing_out[outgoing] = 1
                    model.constraint(balance, lower=0, upper=0)
                    if kind == "new":
                        new_out[built[y]] = -float(line_capacity_by_year.get(y, line_capacity))
                        model.constraint(new_out, upper=0)
                    elif existing_capacity_mw is not None:
                        model.constraint(existing_out, upper=float(existing_capacity_by_year.get(y, existing_capacity_mw)))
    if edges:
        for y in YEARS:
            direction[y] = model.variable(0)
            if include_new_line:
                built[y] = model.variable(0)
                line_addition[y] = model.variable(
                    (line_capex_10k_cny(line_km, line_unit_cost) + line_extra_capex_10k_cny)
                    * factors["line"][y])
                terms = {built[y]: 1, line_addition[y]: -1}
                if y > YEARS[0]:
                    terms[built[y - 1]] = -1
                model.constraint(terms, lower=0, upper=0)
            for scenario in ("forward", "reverse"):
                donor_usage = defaultdict(dict)
                receiver_usage = defaultdict(dict)
                for edge in edges:
                    for a, b_feeder in ((edge["a"], edge["b"]), (edge["b"], edge["a"])):
                        if edge["tie_id"] == EXISTING_OPERATIONAL_TIE and (
                            (y != 2025 and tie_year_basis == "2025_only") or scenario != "forward"
                            or (a, b_feeder) != EXISTING_OPERATIONAL_DIRECTION
                        ):
                            continue  # 年度扩展仅作固定区段负荷比例仿真。
                        if edge["tie_id"] == DESIGNED_NEW_LINE_ID and (
                            (y != 2025 and tie_year_basis == "2025_only") or scenario != "forward"
                            or (a, b_feeder) != ("PZXL-00099", DESIGNED_BUS_FEEDER_ID)
                        ):
                            continue  # 拟建新线年度量也只是 2025 区段种子的比例代理。
                        donor, receiver = feeders[a], feeders[b_feeder]
                        donor_station, receiver_station = donor["station_id"], receiver["station_id"]
                        bound = min(float(donor["current_equivalent_active_power_mw"]),
                                    float(receiver["receiving_current_headroom_mw"]),
                                    edge["path_cap_mw"]) * tie_transfer_limit_scale
                        var = model.variable(0, upper=bound, integer=0)
                        transfer[y, scenario, edge["tie_id"], a, b_feeder] = var
                        if edge["tie_id"] in (EXISTING_OPERATIONAL_TIE, DESIGNED_NEW_LINE_ID):
                            section_mw = (RIGID_2025_FORWARD_OPERATION_MW
                                          if edge["tie_id"] == EXISTING_OPERATIONAL_TIE else
                                          designed_new_line_section()["2025_feeder_stress_section_load_seed_mw"]
                                          * new_line_section_coincidence)
                            if tie_year_basis == "annual_station_scaled" and y != 2025:
                                donor_key = (layer[0], layer[1], donor_station)
                                section_mw *= (float(scene[donor_key, y]["estimated_station_forward_peak_mw"])
                                               / float(scene[donor_key, 2025]["estimated_station_forward_peak_mw"]))
                            active = model.variable(0, upper=1, integer=1)
                            section_active[y, scenario, edge["tie_id"]] = active
                            model.constraint({var: 1, active: -section_mw},
                                             lower=0, upper=0)
                        donor_usage[a][var] = 1
                        receiver_usage[b_feeder][var] = 1
                        if donor_station == "BDZ-00027":
                            model.constraint({var: 1, direction[y]: -bound}, upper=0)
                        else:
                            model.constraint({var: 1, direction[y]: bound}, upper=bound)
                        if edge["new"]:
                            model.constraint({var: 1, built[y]: -bound}, upper=0)
                for feeder_id, terms in donor_usage.items():
                    model.constraint(terms, upper=float(feeders[feeder_id]["current_equivalent_active_power_mw"]))
                for feeder_id, terms in receiver_usage.items():
                    model.constraint(terms, upper=float(feeders[feeder_id]["receiving_current_headroom_mw"]))
                if rigid and require_existing_tie_operation and y == 2025 and scenario == "forward":
                    key = (y, scenario, EXISTING_OPERATIONAL_TIE,
                           *EXISTING_OPERATIONAL_DIRECTION)
                    if key not in transfer:
                        raise ValueError("刚性规划运行要求缺少已核实的墩南—河炮既有联络")
                    donor = feeders[EXISTING_OPERATIONAL_DIRECTION[0]]
                    receiver = feeders[EXISTING_OPERATIONAL_DIRECTION[1]]
                    physical_upper = min(float(donor["current_equivalent_active_power_mw"]),
                                         float(receiver["receiving_current_headroom_mw"]),
                                         EXISTING_PATH_CAP_MW) * tie_transfer_limit_scale
                    if physical_upper + 1e-8 >= RIGID_2025_FORWARD_OPERATION_MW:
                        model.constraint({section_active[y, scenario, EXISTING_OPERATIONAL_TIE]: 1},
                                         lower=1, upper=1)

    for y in YEARS:
        for s in stations:
            row = scene[s, y]
            d = durations[s]
            for scenario in ("forward", "reverse"):
                factor = 0.95 if scenario == "forward" else 0.8 * 0.95
                effect = storage_effective_power_per_module(int(d[f"{scenario}_d95_max_run_hours"]))
                demand = float(row["estimated_station_forward_peak_mw"] if scenario == "forward" else row["reverse_screen_mw"])
                terms = {x[s, y, p]: factor * sum(p) for p in choices[s, y]}
                terms[n[s, y]] = effect
                if edges or regional_transfer is not None:
                    for edge in edges:
                        for a, b_feeder in ((edge["a"], edge["b"]), (edge["b"], edge["a"])):
                            key = (y, scenario, edge["tie_id"], a, b_feeder)
                            if key not in transfer:
                                continue
                            var = transfer[key]
                            if feeders[a]["station_id"] == s[2]:
                                terms[var] = terms.get(var, 0) + 1
                            if feeders[b_feeder]["station_id"] == s[2]:
                                terms[var] = terms.get(var, 0) - 1
                    if pairwise_regional_transfer:
                        for (yy, ss, _kind, donor, receiver), var in transfer.items():
                            if yy != y or ss != scenario:
                                continue
                            if donor == s[2]:
                                terms[var] = terms.get(var, 0) + 1
                            if receiver == s[2]:
                                terms[var] = terms.get(var, 0) - 1
                    elif regional_transfer is not None:
                        for kind, hub in (("existing", "REGIONAL-EXISTING-HUB"),
                                          ("new", "REGIONAL-NEW-HUB")):
                            outgoing = transfer[y, scenario, f"REGIONAL-{kind}", s[2], hub]
                            incoming = transfer[y, scenario, f"REGIONAL-{kind}", hub, s[2]]
                            terms[outgoing] = terms.get(outgoing, 0) + 1
                            terms[incoming] = terms.get(incoming, 0) - 1
                required = demand
                if scenario == "forward" and preserve_baseline_forward_margin:
                    # 研究性规划约束：逐年保留共同起点的绝对正向备用能力。
                    # 这是增长驱动容量的候选口径，不是 DL/T 2041 的原式。
                    initial_capacity = float(baseline[s]["simulation_unit_1_mva"]) + float(
                        baseline[s]["simulation_unit_2_mva"])
                    initial_peak = float(baseline[s]["estimated_forward_peak_mw_2021"])
                    required += baseline_margin_fraction * max(0.0, .95 * initial_capacity - initial_peak)
                model.constraint(terms, lower=required)
                if scenario == "forward" and contingency_service_fraction is not None:
                    fraction = contingency_service_fraction
                    contingency = {x[s, y, p]: .95 * min(p) for p in choices[s, y]}
                    contingency[n[s, y]] = effect
                    if edges or regional_transfer is not None:
                        for edge in edges:
                            for a, b_feeder in ((edge["a"], edge["b"]), (edge["b"], edge["a"])):
                                key = (y, scenario, edge["tie_id"], a, b_feeder)
                                if key not in transfer:
                                    continue
                                var = transfer[key]
                                if feeders[a]["station_id"] == s[2]:
                                    contingency[var] = contingency.get(var, 0) + fraction
                                if feeders[b_feeder]["station_id"] == s[2]:
                                    contingency[var] = contingency.get(var, 0) - fraction
                    model.constraint(contingency, lower=fraction * demand)
            if preserve_prior_year_forward_margin:
                # 逐年增量式：净峰新增量须由当年新增主变能力、储能能力及净转供增量覆盖。
                # 与基期备用保持一样，是明确的研究规划假设，不冒充导则原式。
                effect = storage_effective_power_per_module(int(d["forward_d95_max_run_hours"]))
                delta_terms = {x[s, y, p]: .95 * sum(p) for p in choices[s, y]}
                delta_terms[n[s, y]] = effect
                prior = y - 1
                if prior in YEARS:
                    for p in choices[s, prior]:
                        delta_terms[x[s, prior, p]] = -.95 * sum(p)
                    delta_terms[n[s, prior]] = -effect
                if edges or regional_transfer is not None:
                    for yy, sign in ((y, 1), (prior, -1)):
                        if yy not in YEARS:
                            continue
                        for (transfer_year, scenario, edge_id, a, b_feeder), var in transfer.items():
                            if transfer_year != yy or scenario != "forward":
                                continue
                            if feeders[a]["station_id"] == s[2]:
                                delta_terms[var] = delta_terms.get(var, 0) + sign
                            if feeders[b_feeder]["station_id"] == s[2]:
                                delta_terms[var] = delta_terms.get(var, 0) - sign
                current_peak = float(scene[s, y]["estimated_station_forward_peak_mw"])
                previous_peak = (float(scene[s, prior]["estimated_station_forward_peak_mw"])
                                 if prior in YEARS else float(baseline[s]["estimated_forward_peak_mw_2021"]))
                previous_capacity = (0.0 if prior in YEARS else .95 * (
                    float(baseline[s]["simulation_unit_1_mva"])
                    + float(baseline[s]["simulation_unit_2_mva"])))
                model.constraint(delta_terms, lower=current_peak - previous_peak + previous_capacity)
        control_peak = (peaks[layer + (y,)] if policy_peak_basis == "annual" else
                        max(peaks[layer + (prior,)] for prior in (2021, *YEARS) if prior <= y))
        ratio_terms = {x[s, y, p]: sum(p) for s in stations for p in choices[s, y]}
        model.constraint(ratio_terms, upper=cap * control_peak,
                         lower=minimum_clr_by_year.get(y, 0.0) * peaks[layer + (y,)])

    if capacity_growth_budget_fraction is not None:
        # 各站增配量按正向增量累计；另一站减容不得抵扣新增容量预算。
        initial_total = sum(float(baseline[s]["simulation_unit_1_mva"]) +
                            float(baseline[s]["simulation_unit_2_mva"]) for s in stations)
        model.constraint({var: sum(max(0.0, new - old)
                                   for old, new in zip(before, after))
                          for (s, y, before, after), var in t.items()},
                         upper=initial_total * capacity_growth_budget_fraction)

    minimum_cumulative_capacity = None
    if capacity_first:
        original_costs = model.costs.copy()
        model.costs = [0.0] * len(original_costs)
        capacity_terms = {x[s, y, p]: sum(p) for s in stations for y in YEARS for p in choices[s, y]}
        for index, coefficient in capacity_terms.items():
            model.costs[index] = coefficient
        _, minimum_cumulative_capacity = model.solve()
        model.constraint(capacity_terms, upper=minimum_cumulative_capacity + 1e-5)
        model.costs = original_costs
    solution, optimum = model.solve(stage="minimum_cost")
    if prefer_reserve_at_equal_cost:
        # 费用相同时保留更多年度容量；不会为增容牺牲已求得的最低费用。
        original_costs = model.costs.copy()
        model.constraint({i: c for i, c in enumerate(original_costs) if c},
                         upper=optimum + 1e-5)
        model.costs = [0.0] * len(original_costs)
        reserve_terms = {x[s, y, p]: sum(p) / peaks[layer + (y,)]
                         for s in stations for y in YEARS for p in choices[s, y]}
        for index, coefficient in reserve_terms.items():
            model.costs[index] = -coefficient
        solution, minimum_negative_reserve = model.solve(stage="maximum_reserve_at_minimum_cost")
        model.constraint(reserve_terms, lower=-minimum_negative_reserve - 1e-6)
        model.costs = original_costs
        optimum = sum(c * solution[i] for i, c in enumerate(original_costs))
    if canonicalize_tie_dispatch and transfer:
        # 同成本路径可能有任意零费用转供；固定最优成本，再选最少转供量，
        # 避免把求解器的退化选择误报成必要的年度运行措施。
        original_costs = model.costs.copy()
        model.constraint({i: c for i, c in enumerate(original_costs) if c},
                         upper=optimum + 1e-6)
        model.costs = [0.0] * len(original_costs)
        for index in transfer.values():
            model.costs[index] = 1.0
        solution, _ = model.solve(stage="minimum_transfer_at_fixed_cost_and_reserve")
        model.costs = original_costs
        optimum = sum(c * solution[i] for i, c in enumerate(original_costs))
    station_rows, year_rows, tie_rows = [], [], []
    for s in stations:
        before = tuple(float(baseline[s][f"simulation_unit_{i}_mva"]) for i in (1, 2))
        old_modules = 0
        for y in YEARS:
            after = next(p for p in choices[s, y] if solution[x[s, y, p]] > 0.5)
            modules = int(round(solution[n[s, y]]))
            transformer_capex = sum((v - replaced_unit_credit_fraction * old)
                                    * coefficients[layer[1]] * transformer_cost_scale
                                    for old, v in zip(before, after) if v > old)
            storage_capex = storage_cost_scale * (
                storage_replicated_package_capex_10k_cny(modules)
                - storage_replicated_package_capex_10k_cny(old_modules))
            station_rows.append({
                "study_region_id": layer[0], "voltage_kv": layer[1], "year": y,
                "model_station_id": s[2], "scheme": "rigid" if rigid else "elastic",
                "measure_scope": measure_scope,
                "clr_cap": cap, "prior_unit_1_mva": before[0], "prior_unit_2_mva": before[1],
                "selected_unit_1_mva": after[0], "selected_unit_2_mva": after[1],
                "selected_capacity_mva": sum(after), "storage_modules_in_service": modules,
                "released_capacity_mva": max(0.0, sum(before) - sum(after)),
                "net_capacity_change_mva": sum(after) - sum(before),
                "new_storage_modules": modules - old_modules,
                "forward_screen_mw": float(scene[s, y]["estimated_station_forward_peak_mw"]),
                "reverse_screen_mw": float(scene[s, y]["reverse_screen_mw"]),
                "transformer_capex_10k_cny": round(transformer_capex, 8),
                "storage_capex_10k_cny": round(storage_capex, 8),
                "transformer_lifecycle_npv_10k_cny": round(transformer_capex * factors["transformer"][y], 8),
                "storage_lifecycle_npv_10k_cny": round(storage_capex * factors["storage"][y], 8),
                "technical_scope": TECHNICAL_SCOPE,
            })
            before, old_modules = after, modules
    for y in YEARS:
        selected = [r for r in station_rows if r["year"] == y]
        flows = []
        for (yy, scenario, edge_id, a, b_feeder), var in transfer.items():
            if yy != y or solution[var] <= 1e-7:
                continue
            flows.append({"study_region_id": layer[0], "voltage_kv": layer[1], "year": y,
                          "scenario": scenario, "tie_id": edge_id, "donor_feeder_id": a,
                          "receiver_feeder_id": b_feeder, "donor_station_id": feeders[a]["station_id"],
                          "receiver_station_id": feeders[b_feeder]["station_id"],
                          "transfer_mw": round(float(solution[var]), 8),
                          "operation_basis": ("pairwise_station_transfer_absolute_mw_scenario"
                                              if pairwise_regional_transfer else
                                              "regional_transfer_fraction_scenario" if regional_transfer is not None
                                              else (("original_pdf_switch28_whole_downstream_section_2025_load_seed"
                                                     if y == 2025 else "original_pdf_switch28_section_scaled_by_donor_station_forward_peak")
                                                    if edge_id == EXISTING_OPERATIONAL_TIE else
                                                    ("designed_switch23_24_section_2025_feeder_stress_seed"
                                                     if y == 2025 else "designed_switch23_24_section_scaled_by_donor_station_forward_peak"))),
                          "technical_scope": TECHNICAL_SCOPE})
        tie_rows.extend(flows)
        if pairwise_regional_transfer:
            for pair in candidate_pairs:
                if solution[pair_built[y, pair]] > 0.5:
                    tie_rows.append({"study_region_id": layer[0], "voltage_kv": layer[1],
                                     "year": y, "scenario": "infrastructure",
                                     "tie_id": "REGIONAL-new-build",
                                     "donor_feeder_id": pair[0], "receiver_feeder_id": pair[1],
                                     "donor_station_id": pair[0], "receiver_station_id": pair[1],
                                     "transfer_mw": 0.0,
                                     "operation_basis": "pairwise_new_line_in_service",
                                     "technical_scope": TECHNICAL_SCOPE})
        line_capex = (float(solution[line_addition[y]])
                      * (line_capex_10k_cny(line_km, line_unit_cost) + line_extra_capex_10k_cny)
                      if y in line_addition else 0.0)
        capacity = sum(r["selected_capacity_mva"] for r in selected)
        year_rows.append({"study_region_id": layer[0], "voltage_kv": layer[1], "year": y,
                          "scheme": "rigid" if rigid else "elastic", "clr_cap": cap,
                          "measure_scope": measure_scope,
                          "station_count": len(selected), "synchronous_forward_peak_mw": peaks[layer + (y,)],
                          "selected_capacity_mva": round(capacity, 8),
                          "actual_clr": round(capacity / peaks[layer + (y,)], 9),
                          "policy_peak_basis": policy_peak_basis,
                          "policy_control_peak_mw": round((peaks[layer + (y,)] if policy_peak_basis == "annual" else
                              max(peaks[layer + (prior,)] for prior in (2021, *YEARS) if prior <= y)), 6),
                          "policy_control_clr": round(capacity / (peaks[layer + (y,)] if policy_peak_basis == "annual" else
                              max(peaks[layer + (prior,)] for prior in (2021, *YEARS) if prior <= y)), 9),
                          "storage_modules_in_service": sum(r["storage_modules_in_service"] for r in selected),
                          "line_built": int(round(solution[built[y]])) if y in built else 0,
                          "new_line_capex_10k_cny": round(line_capex, 8),
                          "year_lifecycle_npv_10k_cny": round(
                              sum(r["transformer_lifecycle_npv_10k_cny"] + r["storage_lifecycle_npv_10k_cny"] for r in selected)
                              + line_capex * factors["line"][y], 8),
                          "technical_scope": TECHNICAL_SCOPE})
    reconstruction = sum(r["year_lifecycle_npv_10k_cny"] for r in year_rows)
    if not np.isclose(reconstruction, optimum, rtol=0, atol=1e-3):
        raise ValueError(f"{layer} 现金流复算失败：{reconstruction} != {optimum}")
    summary = {"study_region_id": layer[0], "voltage_kv": layer[1],
               "scheme": "rigid" if rigid else "elastic", "clr_cap": cap,
               "measure_scope": measure_scope,
               "objective_npv_10k_cny": round(optimum, 8),
               "solver_stages": json.dumps(model.solve_history, ensure_ascii=False),
               "max_actual_clr": max(r["actual_clr"] for r in year_rows),
               "new_line_built_2025": year_rows[-1]["line_built"],
               "solver_status": (
                   "time_limit_feasible_with_reported_gap_and_screened_candidates"
                   if any(stage.get("status") == "time_limit_feasible_incumbent"
                          for stage in model.solve_history)
                   else "within_requested_mip_gap_for_screened_station_choices"
                   if station_choice_cap_slack_mva is not None
                   else "within_requested_mip_gap_under_stated_static_proxy"
                   if any(stage.get("mip_gap", 0) > 1e-7 for stage in model.solve_history)
                   else "proven_optimal_under_stated_static_proxy"),
               "transformer_cost_scale": transformer_cost_scale,
               "storage_cost_scale": storage_cost_scale,
               "replaced_unit_credit_fraction": replaced_unit_credit_fraction,
               "tie_transfer_limit_scale": tie_transfer_limit_scale,
               "capacity_first": capacity_first,
               "preserve_baseline_forward_margin": preserve_baseline_forward_margin,
               "baseline_margin_fraction": baseline_margin_fraction,
               "policy_peak_basis": policy_peak_basis,
               "max_storage_modules_per_station": max_storage_modules,
               "require_existing_tie_operation": require_existing_tie_operation,
               "existing_tie_allowed": existing_tie_allowed,
               "new_line_section_coincidence": new_line_section_coincidence,
               "tie_year_basis": tie_year_basis,
               "canonicalize_tie_dispatch": canonicalize_tie_dispatch,
               "preserve_prior_year_forward_margin": preserve_prior_year_forward_margin,
               "allow_capacity_release": allow_capacity_release,
               "capacity_growth_budget_fraction": capacity_growth_budget_fraction,
               "minimum_clr_by_year": minimum_clr_by_year,
               "prefer_reserve_at_equal_cost": prefer_reserve_at_equal_cost,
               "contingency_service_fraction": contingency_service_fraction,
               "regional_transfer": regional_transfer,
               "minimum_cumulative_capacity_mva_years": minimum_cumulative_capacity,
               "technical_scope": TECHNICAL_SCOPE, **{k: v for k, v in factors.items() if not isinstance(v, dict)}}
    return station_rows, year_rows, tie_rows, summary


def run_model(reverse_variant: str = "night_central", caps: dict | None = None,
              factors: dict | None = None, rigid: bool = False,
              include_new_line: bool = False, line_km: float = NEW_LINE_KM,
              line_unit_cost: float = LINE_BASE_10K_PER_KM,
              tie_allowed: bool | None = None, transformer_cost_scale: float = 1.0,
              storage_cost_scale: float = 1.0,
              replaced_unit_credit_fraction: float = 0.0,
              tie_transfer_limit_scale: float = 1.0) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    baseline, scene, durations, peaks, catalog, coefficients = load_inputs(reverse_variant)
    factors = factors or cost_factors()
    caps = caps or {}
    all_stations, all_years, all_ties, all_summaries = [], [], [], []
    for layer in sorted({s[:2] for s in baseline}):
        cap = CAP if rigid else caps.get(layer, CAP)
        rows = solve_layer(layer, baseline, scene, durations, peaks, catalog, coefficients,
                           factors, cap, rigid, include_new_line=include_new_line,
                           line_km=line_km, line_unit_cost=line_unit_cost,
                           tie_allowed=tie_allowed, transformer_cost_scale=transformer_cost_scale,
                           storage_cost_scale=storage_cost_scale,
                           replaced_unit_credit_fraction=replaced_unit_credit_fraction,
                           tie_transfer_limit_scale=tie_transfer_limit_scale)
        for target, addition in zip((all_stations, all_years, all_ties, all_summaries), rows):
            target.extend(addition if isinstance(addition, list) else [addition])
    return all_stations, all_years, all_ties, all_summaries


def main() -> None:
    parser = argparse.ArgumentParser(description="年度全寿命成本离散优化；刚性局部联络为静态仿真")
    parser.add_argument("--scheme", choices=("rigid", "elastic"), required=True)
    parser.add_argument("--pizhou-cap", type=float, default=2.0)
    parser.add_argument("--city-cap", type=float, default=2.0)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    result = run_model(caps={("QX-00005", 35): args.pizhou_cap,
                             ("QX-00005", 110): args.pizhou_cap,
                             ("QX-00007", 110): args.city_cap}, rigid=args.scheme == "rigid")
    for name, rows in zip(("stations", "years", "ties", "layers"), result):
        if rows:
            write_csv(rows, args.output_dir / f"joint_lifecycle_{args.scheme}_{name}.csv")
        elif name == "ties":
            target = args.output_dir / f"joint_lifecycle_{args.scheme}_{name}.csv"
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("w", encoding="utf-8-sig", newline="") as handle:
                csv.writer(handle, lineterminator="\n").writerow((
                    "study_region_id", "voltage_kv", "year", "scenario", "tie_id",
                    "donor_feeder_id", "receiver_feeder_id", "donor_station_id",
                    "receiver_station_id", "transfer_mw", "operation_basis", "technical_scope",
                ))
    for row in result[-1]:
        print(row)


if __name__ == "__main__":
    main()
