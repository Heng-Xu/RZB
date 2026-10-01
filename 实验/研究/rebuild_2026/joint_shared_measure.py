"""两区县刚性、弹性四条路径同步寻优，排序为显式规划条件。"""

import argparse
import hashlib
import json
import numpy as np
from pathlib import Path

from .annual_no_tie_investment_submodel import LinearModel, YEARS
from .baseline_2021 import read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .planning_load_profile import weighted_annual_growth
from .regional_static_milp_v2 import optimization_problem
from .regional_static_milp_v2_audit import audit
from .shared_measure_deterministic import CASES, DISTRICTS, settings
from .two_district_ordered_guide_run import guide_range
from .two_district_source_audit import audit as source_audit
from .city_district_calibration import calibrate_city
from .joint_lifecycle_optimizer import load_inputs
from .regional_static_milp_v2 import BASELINE


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "outputs/joint_shared_measure"
MARGIN = .001
TOLERANCE_10K = .001


def build_joint(case="transfer_10pct", breakthrough="all_years", transfer_mode="load_reallocation"):
    observed = {}
    for row in read_csv(OUTPUT_DIR / "official_annual.csv"):
        region = row["region_id"], int(row["voltage_kv"])
        if region in DISTRICTS.values():
            observed.setdefault(region, {})[int(row["year"])] = float(
                row["reported_downward_load_mw"])
    joint = LinearModel()
    problems, blocks = {}, {}
    city_start = None
    for label, region in DISTRICTS.items():
        minimum, upper = guide_range(weighted_annual_growth(observed[region])[0])
        for scheme in ("rigid", "elastic"):
            kwargs = dict(
                region=region, rigid_cap=2.0, elastic_cap=2.6, min_clr=minimum,
                require_transformer_n1=True, n1_load_requirement="bc_min_service_static",
                elastic_allow_line_decisions=True, enforce_expansion_slot=True,
                max_transfer_fraction=CASES[case], storage_max_mwh_per_station=None,
                prefer_larger_clr=True, minimize_transfer_tiebreak=True,
                transfer_mode=transfer_mode)
            if label == "city":
                city_start = upper * observed[region][2021]
                kwargs["city_baseline_cap_mva"] = city_start
            generator = optimization_problem(scheme, **kwargs)
            model, metadata = next(generator)
            offset, row_offset = len(joint.costs), len(joint.constraint_lower)
            for name in ("costs", "lower_bounds", "upper_bounds", "integrality",
                         "constraint_lower", "constraint_upper"):
                getattr(joint, name).extend(getattr(model, name))
            joint.entries.extend((r + row_offset, c + offset, value)
                                 for r, c, value in model.entries)
            key = label, scheme
            problems[key] = generator
            blocks[key] = {
                "offset": offset, "count": len(model.costs),
                "clr_terms": {year: {i + offset: value for i, value in terms.items()}
                              for year, terms in metadata["clr_terms"].items()},
                "transfer_variables": [i + offset for i in metadata["transfer_variables"]]}
            blocks[key]["line_variables"] = [i + offset for i in metadata["line_variables"]]
            blocks[key]["line_dispatch_substitutable"] = metadata["line_dispatch_substitutable"]
    for year in YEARS:
        for scheme in ("rigid", "elastic"):
            terms = dict(blocks["city", scheme]["clr_terms"][year])
            terms.update({i: -v for i, v in blocks["pizhou", scheme]["clr_terms"][year].items()})
            joint.constraint(terms, upper=-MARGIN)
        for label in DISTRICTS:
            terms = dict(blocks[label, "elastic"]["clr_terms"][year])
            terms.update({i: -v for i, v in blocks[label, "rigid"]["clr_terms"][year].items()})
            joint.constraint(terms, lower=MARGIN)
    # "any" 要求至少一个区县的一个年份突破；"both"要求各区县至少一年；
    # "all_years"要求两区县各年均突破。此处为用户规划目标，不改原始负荷。
    groups = ([list(DISTRICTS)] if breakthrough == "any" else [[label] for label in DISTRICTS])
    for group in groups:
        indicators = []
        for label in group:
            for year in YEARS:
                terms = dict(blocks[label, "elastic"]["clr_terms"][year])
                if breakthrough == "all_years":
                    joint.constraint(terms, lower=2 + MARGIN)
                else:
                    indicator = joint.variable(0)
                    indicators.append(indicator)
                    terms[indicator] = -2.6
                    joint.constraint(terms, lower=2 + MARGIN - 2.6)
        if indicators:
            joint.constraint({i: 1 for i in indicators}, lower=1)
    return joint, problems, blocks, city_start


def finish(generator, override):
    try:
        generator.send(override)
    except StopIteration as result:
        return result.value
    raise RuntimeError("模型结果未结束")


def solve(case="transfer_10pct", breakthrough="all_years", output=None, resume=False,
          stage_seconds=480, transfer_mode="load_reallocation"):
    settings()
    import os
    os.environ["XUZHOU_MILP_TIME_LIMIT_SECONDS"] = str(stage_seconds)
    suffix = "_load_reallocation" if transfer_mode == "load_reallocation" else ""
    directory = Path(output) if output else OUTPUT / f"{case}_{breakthrough}{suffix}"
    directory.mkdir(parents=True, exist_ok=True)
    joint, problems, blocks, city_start = build_joint(case, breakthrough, transfer_mode)
    presolved_unused_lines = 0
    if transfer_mode == "load_reallocation":
        # 没有强制建设目标，且既有代理网络可等价承接任意新线转接：
        # 正投资新线严格劣于既有通道，零建设是可证明的费用最优选择。
        for block in blocks.values():
            if block["line_dispatch_substitutable"]:
                for i in block["line_variables"]:
                    joint.lower_bounds[i] = joint.upper_bounds[i] = 0
                    joint.integrality[i] = 0
                    presolved_unused_lines += 1
    primary_costs = list(joint.costs)
    if resume:
        from scipy.sparse import coo_matrix
        checkpoint = np.load(directory / "minimum_cost_checkpoint.npz")
        saved = json.loads((directory / "minimum_cost_checkpoint.json").read_text())
        if (saved["case"], saved["breakthrough"]) != (case, breakthrough):
            raise ValueError("断点的情景与本次要求不一致")
        if saved.get("transfer_mode", "legacy_outage_proxy") != transfer_mode:
            raise ValueError("断点的转供用途与本次要求不一致")
        primary_solution, minimum = checkpoint["solution"], float(checkpoint["minimum"])
        if len(primary_solution) != len(joint.costs):
            raise ValueError("断点变量数量与当前模型不一致")
        rr, cc, vv = zip(*joint.entries)
        matrix = coo_matrix((vv, (rr, cc)), shape=(
            len(joint.constraint_lower), len(joint.costs))).tocsr()
        activity = matrix @ primary_solution
        if not (np.all(activity >= np.array(joint.constraint_lower) - 1e-4) and
                np.all(activity <= np.array(joint.constraint_upper) + 1e-4) and
                np.all(primary_solution >= np.array(joint.lower_bounds) - 1e-5) and
                np.all(primary_solution <= np.array(joint.upper_bounds) + 1e-5) and
                abs(np.dot(primary_costs, primary_solution) - minimum) < 1e-3):
            raise ValueError("断点不满足当前约束或费用")
        joint.last_solution = primary_solution.copy()
        joint.solve_history = saved["history"]
    else:
        primary_solution, minimum = joint.solve(stage="joint_four_paths_minimum_cost")
    np.savez_compressed(directory / "minimum_cost_checkpoint.npz",
                        solution=primary_solution, minimum=minimum)
    (directory / "minimum_cost_checkpoint.json").write_text(json.dumps(
        {"case": case, "breakthrough": breakthrough, "transfer_mode": transfer_mode,
         "history": joint.solve_history},
        ensure_ascii=False, indent=2) + "\n")
    fixed_dispatch_equivalent_lines = 0
    for block in blocks.values():
        if block["line_dispatch_substitutable"]:
            for i in block["line_variables"]:
                joint.lower_bounds[i] = joint.upper_bounds[i] = round(float(primary_solution[i]))
                joint.integrality[i] = 0
                fixed_dispatch_equivalent_lines += 1
    joint.constraint({i: v for i, v in enumerate(primary_costs) if v},
                     upper=minimum + TOLERANCE_10K)
    capacity_objective = {i: -v for key, block in blocks.items() if key[1] == "elastic"
                          for terms in block["clr_terms"].values() for i, v in terms.items()}
    joint.costs = [capacity_objective.get(i, 0.0) for i in range(len(joint.costs))]
    capacity_solution, reserve = joint.solve(stage="joint_maximum_elastic_clr_at_minimum_cost")
    joint.constraint(capacity_objective, upper=reserve + 1e-8)
    # 设备与投运布局已由前两阶段选定；最后仅优化该布局的连续转供量。
    # 固定整数变量后成为LP，不重复搜索与前两阶段同价同R的其它设备布局。
    for i, integer in enumerate(joint.integrality):
        if integer:
            joint.lower_bounds[i] = joint.upper_bounds[i] = round(float(capacity_solution[i]))
            joint.integrality[i] = 0
    joint.costs = [0.0] * len(joint.costs)
    for block in blocks.values():
        for i in block["transfer_variables"]:
            joint.costs[i] = 1.0
    solution, transfer = joint.solve(stage="joint_minimum_transfer_at_selected_layout")
    selected_primary = sum(v * float(solution[i]) for i, v in enumerate(primary_costs))
    portfolios = {}
    annual_rows = []
    for label in DISTRICTS:
        local = directory / label
        local.mkdir(parents=True, exist_ok=True)
        summaries = []
        for scheme in ("rigid", "elastic"):
            block = blocks[label, scheme]
            offset = block["offset"]
            part = solution[offset:offset + block["count"]]
            result = finish(problems[label, scheme], (part, minimum, selected_primary, joint.solve_history))
            summary, years, stations, transfers, lines, outages = result
            summaries.append(summary)
            for suffix, rows in (("years", years), ("stations", stations), ("transfers", transfers),
                                 ("new_lines", lines), ("outage_flows", outages)):
                path = local / f"{scheme}_{suffix}.csv"
                if rows:
                    write_csv(rows, path)
                elif path.exists():
                    path.unlink()
            annual_rows.extend({"district": label, **r} for r in years)
        (local / "summary.json").write_text(json.dumps(summaries, ensure_ascii=False, indent=2) + "\n")
        if label == "city":
            source_baseline = {(r["study_region_id"], int(r["voltage_kv"]), r["model_station_id"]): r
                               for r in read_csv(BASELINE)}
            _, scenes, _, peaks, catalogs, _ = load_inputs()
            _, _, _, trace = calibrate_city(source_baseline, scenes, peaks, catalogs[DISTRICTS[label]],
                                           city_start)
            write_csv(trace, local / "city_2021_district_calibration.csv")
        portfolios[label] = {r["scheme"]: r for r in summaries}
        print(audit(local), flush=True)
    write_csv(annual_rows, directory / "annual_comparison.csv")
    source_audit(tuple(str((directory / label).resolve()) for label in DISTRICTS),
                 directory / "source_audit.json")
    by_key = {(r["district"], r["scheme"], r["year"]): r for r in annual_rows}
    cost_order = {label: portfolios[label]["elastic"]["objective_npv_10k"] <
                  portfolios[label]["rigid"]["objective_npv_10k"] - .01 for label in DISTRICTS}
    result = {
        "case": case, "breakthrough_requirement": breakthrough,
        "transfer_mode": transfer_mode,
        "transfer_purpose": "normal_district_internal_load_reallocation"
        if transfer_mode == "load_reallocation" else "legacy_normal_and_fault_proxy",
        "max_transfer_fraction": CASES[case],
        "same_measure_set": True, "same_start_per_district": True,
        "optimization_scope": "simultaneous_four_path_minimum_total_lifecycle_cost",
        "ordering_constraints_imposed": True, "ordering_margin": MARGIN,
        "cost_order_imposed": False, "cost_order": cost_order,
        "city_below_pizhou_all_years": all(
            by_key["city", scheme, year]["clr"] + MARGIN <=
            by_key["pizhou", scheme, year]["clr"] + 1e-7
            for scheme in ("rigid", "elastic") for year in YEARS),
        "elastic_above_rigid_all_years": all(
            by_key[label, "rigid", year]["clr"] + MARGIN <=
            by_key[label, "elastic", year]["clr"] + 1e-7
            for label in DISTRICTS for year in YEARS),
        "elastic_break_2_years": {label: [
            year for year in YEARS if by_key[label, "elastic", year]["clr"] > 2 + 1e-7]
                                for label in DISTRICTS},
        "cost_npv_10k": {label: {scheme: s["objective_npv_10k"] for scheme, s in summaries.items()}
                         for label, summaries in portfolios.items()},
        "joint_minimum_primary_objective_10k": minimum,
        "selected_joint_primary_objective_10k": selected_primary,
        "cost_tiebreak_tolerance_10k": TOLERANCE_10K,
        "sum_elastic_annual_clr": -reserve,
        "transfer_objective_mw_sum": transfer,
        "transfer_tiebreak_scope": "minimum_continuous_transfer_for_selected_optimal_layout",
        "fixed_dispatch_equivalent_line_variables": fixed_dispatch_equivalent_lines,
        "presolved_unused_line_variables": presolved_unused_lines,
        "line_fixing_basis": "transfer_use_bound_below_existing_pair_donor_and_county_bounds",
        "solve_history": joint.solve_history,
        "solver_configuration": {
            "backend": "highspy", "threads": 1, "random_seed": 0,
            "mip_rel_gap": 1e-9, "mip_abs_gap": 1e-7, "time_limit_per_stage_seconds": stage_seconds},
    }
    breakthrough_pass = (
        all(len(values) == len(YEARS) for values in result["elastic_break_2_years"].values())
        if breakthrough == "all_years" else
        all(result["elastic_break_2_years"].values()) if breakthrough == "both" else
        any(result["elastic_break_2_years"].values()))
    result["all_requested_relations"] = all(cost_order.values()) and result[
        "city_below_pizhou_all_years"] and result["elastic_above_rigid_all_years"] and breakthrough_pass
    (directory / "review.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    evidence = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(ROOT.glob("*.py"))}
    evidence.update({str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                     for path in sorted(OUTPUT_DIR.glob("*.csv"))})
    (directory / "input_and_model_hashes.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "solve_history"}, ensure_ascii=False), flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=CASES, default="transfer_10pct")
    parser.add_argument("--breakthrough", choices=("any", "both", "all_years"), default="all_years")
    parser.add_argument("--output")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--stage-seconds", type=int, default=480)
    parser.add_argument("--transfer-mode", choices=("load_reallocation", "legacy_outage_proxy"),
                        default="load_reallocation")
    args = parser.parse_args()
    solve(args.case, args.breakthrough, args.output, args.resume, args.stage_seconds, args.transfer_mode)
