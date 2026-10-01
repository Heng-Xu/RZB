"""2022—2025 年无联络的逐年主变/储能投资现值整数规划子模型。"""

import argparse
import os
import time
from collections import defaultdict
from itertools import combinations_with_replacement
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix

from .baseline_2021 import local_unit_catalog, read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .incremental_cost import replacement_cost_coefficients, storage_anchors, storage_capex_10k_cny


BASELINE = OUTPUT_DIR / "baseline_2021_station_candidates.csv"
TRANSFORMER_PATH = OUTPUT_DIR / "transformer_only_path_station_2021_2025.csv"
FORWARD_LAYERS = OUTPUT_DIR / "annual_forward_layer_scenes_2021_2025.csv"
STORAGE_SCREEN = OUTPUT_DIR / "static_storage_need_screen_2025.csv"
SCAN_CEILINGS = OUTPUT_DIR / "source_load_scan_ceiling_research.csv"
YEARS = (2022, 2023, 2024, 2025)
CAP = 2.0
MAX_MODULES = 10


def storage_affine_cost_parts() -> tuple[float, float]:
    """1—10 柜价格等于首次安装固定额 + 每柜边际额。"""
    one, ten = storage_anchors()
    slope = (ten - one) / 9
    return one - slope, slope


def storage_effective_power_per_module(run_hours: int) -> float:
    """在 D95 矩形代理中，单柜同时受 0.1 MW 与 0.215 MWh 限制。"""
    return min(0.1, 0.215 / run_hours) if run_hours > 0 else 0.1


class LinearModel:
    def __init__(self) -> None:
        self.costs = []
        self.lower_bounds = []
        self.upper_bounds = []
        self.integrality = []
        self.entries = []
        self.constraint_lower = []
        self.constraint_upper = []
        self.last_solution = None
        self.solve_history = []

    def variable(self, cost: float, upper: float = 1, integer: int = 1) -> int:
        index = len(self.costs)
        self.costs.append(cost)
        self.lower_bounds.append(0)
        self.upper_bounds.append(upper)
        self.integrality.append(integer)
        return index

    def constraint(self, terms: dict[int, float], lower: float = -np.inf, upper: float = np.inf) -> None:
        row = len(self.constraint_lower)
        self.constraint_lower.append(lower)
        self.constraint_upper.append(upper)
        self.entries.extend((row, column, value) for column, value in terms.items() if value)

    def solve(self, stage: str = "cost") -> tuple[np.ndarray, float]:
        row, column, data = zip(*self.entries)
        matrix = coo_matrix((data, (row, column)), shape=(len(self.constraint_lower), len(self.costs))).tocsr()
        started = time.monotonic()
        backend = os.environ.get("XUZHOU_MILP_BACKEND", "scipy")
        if os.environ.get("XUZHOU_SOLVER_TRACE") == "1":
            print(f"MILP start: {stage}, {backend}, {len(self.costs)} variables", flush=True)
        if backend == "highspy":
            return self._solve_highspy(matrix, stage, started)
        if backend != "scipy":
            raise ValueError(f"未知 MILP 后端: {backend}")
        mip_gap_target = float(os.environ.get("XUZHOU_MILP_REL_GAP", "1e-7"))
        result = milp(
            c=np.array(self.costs),
            integrality=np.array(self.integrality),
            bounds=Bounds(self.lower_bounds, self.upper_bounds),
            constraints=LinearConstraint(matrix, self.constraint_lower, self.constraint_upper),
            options={"mip_rel_gap": mip_gap_target,
                     "time_limit": float(os.environ.get("XUZHOU_MILP_TIME_LIMIT_SECONDS", "120"))},
        )
        accepted_time_limit_gap = float(os.environ.get("XUZHOU_MILP_ACCEPT_FEASIBLE_GAP", "0"))
        accepted_incumbent = (result.status == 1 and result.x is not None
                              and getattr(result, "mip_gap", None) is not None
                              and float(result.mip_gap) <= accepted_time_limit_gap)
        if (result.status != 0 and not accepted_incumbent) or result.x is None:
            gap = getattr(result, "mip_gap", None)
            raise ValueError(f"逐年无联络子模型未取得目标精度的最优解：{result.message}; mip_gap={gap}")
        self.last_solution = result.x.copy()
        self.solve_history.append({"stage": stage, "backend": backend,
                                   "status": "time_limit_feasible_incumbent" if accepted_incumbent else "mip_gap_met",
                                   "elapsed_seconds": time.monotonic() - started,
                                   "objective": float(result.fun),
                                   "mip_gap": float(result.mip_gap)})
        return result.x, float(result.fun)

    def _solve_highspy(self, matrix, stage, started):
        """相同矩阵与容差；给次级目标传入上一阶段可行解。"""
        import highspy
        solver = highspy.Highs()
        log_dir = os.environ.get("XUZHOU_MILP_LOG_DIR")
        solver.setOptionValue("output_flag", bool(log_dir))
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            solver.setOptionValue("log_to_console", False)
            log_path = Path(log_dir) / f"{stage}.log"
            log_path.write_text("", encoding="utf-8")
            solver.setOptionValue("log_file", str(log_path))
        solver.setOptionValue("threads", int(os.environ.get("XUZHOU_MILP_THREADS", "1")))
        solver.setOptionValue("random_seed", int(os.environ.get("XUZHOU_MILP_SEED", "0")))
        solver.setOptionValue("mip_rel_gap", float(os.environ.get("XUZHOU_MILP_REL_GAP", "1e-7")))
        solver.setOptionValue("mip_abs_gap", float(os.environ.get("XUZHOU_MILP_ABS_GAP", "1e-7")))
        solver.setOptionValue("time_limit", float(os.environ.get("XUZHOU_MILP_TIME_LIMIT_SECONDS", "120")))
        lp = highspy.HighsLp()
        lp.num_col_, lp.num_row_ = matrix.shape[1], matrix.shape[0]
        lp.col_cost_, lp.col_lower_, lp.col_upper_ = self.costs, self.lower_bounds, self.upper_bounds
        lp.row_lower_, lp.row_upper_ = self.constraint_lower, self.constraint_upper
        lp.integrality_ = [highspy.HighsVarType.kInteger if i else highspy.HighsVarType.kContinuous
                           for i in self.integrality]
        lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
        lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = matrix.indptr, matrix.indices, matrix.data
        solver.passModel(lp)
        if self.last_solution is not None:
            solver.setSolution(len(self.costs), np.arange(len(self.costs), dtype=np.int32), self.last_solution)
        solver.run()
        status = solver.getModelStatus()
        if status != highspy.HighsModelStatus.kOptimal:
            if log_dir:
                np.savez_compressed(Path(log_dir) / f"{stage}_unproven_candidate.npz",
                                    solution=np.array(solver.getSolution().col_value))
            raise ValueError(f"MILP {stage} 未取得已证明最优解：{solver.modelStatusToString(status)}")
        solution = np.array(solver.getSolution().col_value)
        info = solver.getInfo()
        self.last_solution = solution.copy()
        gap = float(info.mip_gap) if any(self.integrality) else 0.0
        self.solve_history.append({"stage": stage, "backend": "highspy", "solver_version": solver.version(),
                                   "status": "optimal",
                                   "threads": int(os.environ.get("XUZHOU_MILP_THREADS", "1")),
                                   "random_seed": int(os.environ.get("XUZHOU_MILP_SEED", "0")),
                                   "elapsed_seconds": time.monotonic() - started,
                                   "objective": info.objective_function_value, "mip_gap": gap,
                                   "objective_lower_bound": float(info.mip_dual_bound)
                                   if any(self.integrality) else float(info.objective_function_value),
                                   "mip_relative_gap_target": float(os.environ.get("XUZHOU_MILP_REL_GAP", "1e-7"))})
        if os.environ.get("XUZHOU_SOLVER_TRACE") == "1":
            print(f"MILP optimal: {stage}, objective={info.objective_function_value:.9f}, gap={gap}", flush=True)
        return solution, float(info.objective_function_value)


def solve_annual_layer(
    layer: tuple[str, int],
    baseline: dict,
    scene: dict,
    durations: dict,
    peak_by_year: dict[int, float],
    unit_sizes: list[float],
    unit_cost: float,
    discount_rate: float,
    capacity_load_cap: float = CAP,
) -> tuple[list[dict], dict]:
    if discount_rate < 0:
        raise ValueError("折现率不得为负")
    if capacity_load_cap < CAP:
        raise ValueError("该子模型只比较刚性 2.0 及以上的扫描档")
    stations = sorted(station for station in baseline if station[:2] == layer)
    fixed, slope = storage_affine_cost_parts()
    weight = {year: (1 + discount_rate) ** -(year - 2021) for year in YEARS}
    model = LinearModel()
    choices = {}
    chosen_var = {}
    modules_var = {}
    installed_var = {}
    transition_var = {}

    for station in stations:
        prior_pair = tuple(float(baseline[station][f"simulation_unit_{slot}_mva"]) for slot in (1, 2))
        durations_row = durations[station]
        forward_effect = storage_effective_power_per_module(int(durations_row["forward_d95_max_run_hours"]))
        reverse_effect = storage_effective_power_per_module(int(durations_row["reverse_d95_max_run_hours"]))
        for year in YEARS:
            row = scene[station, year]
            forward = float(row["estimated_station_forward_peak_mw"])
            reverse = float(row["reverse_screen_mw"])
            feasible_pairs = [
                pair for pair in combinations_with_replacement(unit_sizes, 2)
                if all(new >= old for old, new in zip(prior_pair, pair))
                and 0.95 * sum(pair) + forward_effect * MAX_MODULES + 1e-8 >= forward
                and 0.8 * 0.95 * sum(pair) + reverse_effect * MAX_MODULES + 1e-8 >= reverse
            ]
            choices[station, year] = feasible_pairs
            for pair in feasible_pairs:
                chosen_var[station, year, pair] = model.variable(0)
            marginal_weight = weight[year] - weight.get(year + 1, 0)
            modules_var[station, year] = model.variable(slope * marginal_weight, upper=MAX_MODULES)
            installed_var[station, year] = model.variable(fixed * marginal_weight)

        for year in YEARS:
            previous_pairs = [prior_pair] if year == 2022 else choices[station, year - 1]
            for before in previous_pairs:
                for after in choices[station, year]:
                    if not all(new >= old for old, new in zip(before, after)):
                        continue
                    purchased = sum(new for old, new in zip(before, after) if new > old)
                    transition_var[station, year, before, after] = model.variable(purchased * unit_cost * weight[year])

    for station in stations:
        for year in YEARS:
            pairs = choices[station, year]
            x = {chosen_var[station, year, pair]: 1 for pair in pairs}
            model.constraint(x, lower=1, upper=1)
            before_pairs = [tuple(float(baseline[station][f"simulation_unit_{slot}_mva"]) for slot in (1, 2))] if year == 2022 else choices[station, year - 1]
            for before in before_pairs:
                outflow = {
                    transition_var[station, year, before, after]: 1
                    for after in pairs if (station, year, before, after) in transition_var
                }
                if year > 2022:
                    outflow[chosen_var[station, year - 1, before]] = -1
                    model.constraint(outflow, lower=0, upper=0)
                else:
                    model.constraint(outflow, lower=1, upper=1)
            for after in pairs:
                inflow = {
                    transition_var[station, year, before, after]: 1
                    for before in before_pairs if (station, year, before, after) in transition_var
                }
                inflow[chosen_var[station, year, after]] = -1
                model.constraint(inflow, lower=0, upper=0)

            n = modules_var[station, year]
            b = installed_var[station, year]
            model.constraint({n: 1, b: -MAX_MODULES}, upper=0)
            model.constraint({n: 1, b: -1}, lower=0)
            if year > 2022:
                model.constraint({n: 1, modules_var[station, year - 1]: -1}, lower=0)
                model.constraint({b: 1, installed_var[station, year - 1]: -1}, lower=0)
            row = scene[station, year]
            duration = durations[station]
            forward_effect = storage_effective_power_per_module(int(duration["forward_d95_max_run_hours"]))
            reverse_effect = storage_effective_power_per_module(int(duration["reverse_d95_max_run_hours"]))
            forward_terms = {chosen_var[station, year, pair]: 0.95 * sum(pair) for pair in pairs}
            forward_terms[n] = forward_effect
            model.constraint(forward_terms, lower=float(row["estimated_station_forward_peak_mw"]))
            reverse_terms = {chosen_var[station, year, pair]: 0.8 * 0.95 * sum(pair) for pair in pairs}
            reverse_terms[n] = reverse_effect
            model.constraint(reverse_terms, lower=float(row["reverse_screen_mw"]))

    for year in YEARS:
        capacity_terms = {
            chosen_var[station, year, pair]: sum(pair)
            for station in stations for pair in choices[station, year]
        }
        model.constraint(capacity_terms, upper=capacity_load_cap * peak_by_year[year])

    solution, objective = model.solve()
    output = []
    for station in stations:
        old_pair = tuple(float(baseline[station][f"simulation_unit_{slot}_mva"]) for slot in (1, 2))
        old_modules = 0
        for year in YEARS:
            pair = next(pair for pair in choices[station, year] if solution[chosen_var[station, year, pair]] > 0.5)
            modules = int(round(solution[modules_var[station, year]]))
            transformer_capex = sum(new * unit_cost for old, new in zip(old_pair, pair) if new > old)
            storage_capex = storage_capex_10k_cny(modules) - storage_capex_10k_cny(old_modules)
            output.append({
                "study_region_id": layer[0],
                "voltage_kv": layer[1],
                "year": year,
                "model_station_id": station[2],
                "reverse_variant": scene[station, year]["reverse_variant"],
                "prior_unit_1_mva": old_pair[0],
                "prior_unit_2_mva": old_pair[1],
                "selected_unit_1_mva": pair[0],
                "selected_unit_2_mva": pair[1],
                "selected_capacity_mva": sum(pair),
                "storage_modules_in_service": modules,
                "new_storage_modules": modules - old_modules,
                "forward_screen_mw": float(scene[station, year]["estimated_station_forward_peak_mw"]),
                "reverse_screen_mw": float(scene[station, year]["reverse_screen_mw"]),
                "forward_duration_template_hours": int(durations[station]["forward_d95_max_run_hours"]),
                "reverse_duration_template_hours": int(durations[station]["reverse_d95_max_run_hours"]),
                "transformer_capex_10k_cny": round(transformer_capex, 6),
                "storage_capex_10k_cny": round(storage_capex, 6),
                "investment_10k_cny": round(transformer_capex + storage_capex, 6),
                "discounted_investment_10k_cny": round((transformer_capex + storage_capex) * weight[year], 6),
                "technical_scope": "station_aggregate_screens_2025_D95_template_not_guide_certification",
                "cost_scope": "2022_2025_investment_npv_only_not_full_lifecycle",
            })
            old_pair, old_modules = pair, modules
    reconstructed = sum(float(row["discounted_investment_10k_cny"]) for row in output)
    if not np.isclose(reconstructed, objective, rtol=0, atol=1e-3):
        raise ValueError(f"{layer} 目标值与逐年折现投资不一致：{objective} vs {reconstructed}")
    return output, {
        "study_region_id": layer[0],
        "voltage_kv": layer[1],
        "reverse_variant": next(iter(scene.values()))["reverse_variant"],
        "station_count": len(stations),
        "discount_rate": discount_rate,
        "clr_cap": capacity_load_cap,
        "discount_rate_status": "illustrative_from_local_storage_cost_note_not_approved",
        "investment_npv_10k_cny": round(objective, 6),
        "solver_status": "proven_optimal_within_no_tie_investment_submodel",
        "technical_scope": "station_aggregate_screens_2025_D95_template_not_guide_certification",
        "cost_scope": "2022_2025_investment_npv_only_not_full_lifecycle",
    }


def build_annual_no_tie_investment_submodel(
    reverse_variant: str = "night_central",
    discount_rate: float = 0.06,
    capacity_load_caps: dict[str, float] | None = None,
) -> tuple[list[dict], list[dict], list[dict]]:
    capacity_load_caps = capacity_load_caps or {}
    baseline = {
        (row["study_region_id"], int(row["voltage_kv"]), row["model_station_id"]): row
        for row in read_csv(BASELINE)
    }
    scene = {
        ((row["study_region_id"], int(row["voltage_kv"]), row["model_station_id"]), int(row["year"])): row
        for row in read_csv(TRANSFORMER_PATH)
        if row["reverse_variant"] == reverse_variant and int(row["year"]) in YEARS
    }
    durations = {
        (row["study_region_id"], int(row["voltage_kv"]), row["model_station_id"]): row
        for row in read_csv(STORAGE_SCREEN)
        if row["capacity_case"] == "hold_2021_simulation_capacity"
    }
    peaks = {
        (row["study_region_id"], int(row["voltage_kv"]), int(row["year"])): float(row["estimated_synchronous_forward_peak_mw"])
        for row in read_csv(FORWARD_LAYERS)
        if int(row["year"]) in YEARS
    }
    catalog = local_unit_catalog()
    unit_costs = {row["voltage_kv"]: row["base_coefficient_10k_cny_per_purchased_mva"] for row in replacement_cost_coefficients()}
    stations = []
    layer_summaries = []
    year_summaries = []
    for layer in sorted({station[:2] for station in baseline}):
        layer_cap = capacity_load_caps.get(layer[0], CAP)
        rows, summary = solve_annual_layer(
            layer, baseline, scene, durations,
            {year: peaks[layer + (year,)] for year in YEARS},
            catalog[layer], unit_costs[layer[1]], discount_rate, layer_cap,
        )
        stations.extend(rows)
        layer_summaries.append(summary)
        for year in YEARS:
            selected = [row for row in rows if row["year"] == year]
            capacity = sum(row["selected_capacity_mva"] for row in selected)
            peak = peaks[layer + (year,)]
            year_summaries.append({
                "study_region_id": layer[0],
                "voltage_kv": layer[1],
                "year": year,
                "reverse_variant": reverse_variant,
                "station_count": len(selected),
                "synchronous_forward_peak_mw": peak,
                "selected_capacity_mva": capacity,
                "actual_clr": round(capacity / peak, 9),
                "clr_cap": layer_cap,
                "storage_modules_in_service": sum(row["storage_modules_in_service"] for row in selected),
                "year_investment_10k_cny": round(sum(row["investment_10k_cny"] for row in selected), 6),
                "year_discounted_investment_10k_cny": round(sum(row["discounted_investment_10k_cny"] for row in selected), 6),
                "technical_scope": summary["technical_scope"],
                "cost_scope": summary["cost_scope"],
            })
    return stations, year_summaries, layer_summaries


def main() -> None:
    parser = argparse.ArgumentParser(description="求解逐年无联络主变+储能的投资现值子模型")
    parser.add_argument("--reverse-variant", choices=("night_central", "early_pv_high"), default="night_central")
    parser.add_argument("--discount-rate", type=float, default=0.06)
    parser.add_argument("--research-ceilings", action="store_true", help="按已固化的邳州 4.0/市区 3.0 研究扫描上限求解")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    caps = {
        row["region_id"]: float(row["capacity_load_scan_ceiling"])
        for row in read_csv(SCAN_CEILINGS)
    } if args.research_ceilings else None
    stations, years, layers = build_annual_no_tie_investment_submodel(args.reverse_variant, args.discount_rate, caps)
    suffix = f"{args.reverse_variant}_research_ceiling" if args.research_ceilings else args.reverse_variant
    write_csv(stations, args.output_dir / f"annual_no_tie_investment_stations_{suffix}.csv")
    write_csv(years, args.output_dir / f"annual_no_tie_investment_years_{suffix}.csv")
    write_csv(layers, args.output_dir / f"annual_no_tie_investment_layers_{suffix}.csv")
    print(f"已求解 {len(stations)} 条站—年、{len(years)} 条层—年；仅投资现值子模型，不是全寿命刚性解。")


if __name__ == "__main__":
    main()
