"""2026-09-28 区域 10 kV 转移能力修正试算；不覆盖冻结 v4。"""

import json
from itertools import product
from pathlib import Path

from scipy.optimize import linprog

from .baseline_historical_proxy import build
from .baseline_2021 import read_csv
from .city_mapping_audit import write_csv
from .cost_references import read_cost_references
from .hourly_source_profile import OUTPUT_DIR
from .incremental_cost import (
    LINE_BASE_10K_PER_KM, line_capex_10k_cny,
    replacement_cost_coefficients, storage_replicated_package_capex_10k_cny,
)
from .joint_lifecycle_optimizer import cost_factors, load_inputs, solve_layer
from .pizhou_existing_ties import build_feeder_headroom, read_cross_station_ties
from .planning_load_profile import apply_pizhou_weighted_growth


OUTPUT = OUTPUT_DIR / "capacity_release_simulation/regional_revision_2026_09_28"
PIZHOU = ("QX-00005", 110)
CITY = ("QX-00007", 110)
LINE_KM = 3.0
LINE_CAPACITY_MW = 9.05


def pizhou_sample_fraction() -> dict:
    """六条样本馈线的静态源端能力比例；不作全区实测能力认证。"""
    feeders = {r["feeder_id"]: r for r in build_feeder_headroom()}
    ties = read_cross_station_ties()
    best = (0.0, (), ())
    for directions in product((-1, 0, 1), repeat=len(ties)):
        edges = []
        for tie, direction in zip(ties, directions):
            if direction:
                endpoints = (tie["from_feeder_id"], tie["to_feeder_id"])
                edges.append(endpoints if direction == 1 else endpoints[::-1])
        if not edges:
            continue
        matrix, limits = [], []
        for feeder_id, feeder in feeders.items():
            matrix.append([float(a == feeder_id) for a, _ in edges])
            limits.append(float(feeder["current_equivalent_active_power_mw"]))
            matrix.append([float(b == feeder_id) for _, b in edges])
            limits.append(float(feeder["receiving_current_headroom_mw"]))
        result = linprog([-1.0] * len(edges), A_ub=matrix, b_ub=limits,
                         bounds=(0, None), method="highs")
        if result.success and -result.fun > best[0]:
            best = (-float(result.fun), directions, edges)
    denominator = sum(float(r["current_equivalent_active_power_mw"]) for r in feeders.values())
    return {"sample_feeder_count": len(feeders), "cross_station_tie_count": len(ties),
            "sample_current_equivalent_power_mw": denominator,
            "sample_transfer_screen_mw": best[0],
            "initial_fraction": best[0] / denominator,
            "status": "six_feeder_source_end_proxy_extrapolated_as_regional_scenario_not_verified_transfer"}


def base_cost_ratios(line_unit_cost: float = LINE_BASE_10K_PER_KM,
                     line_extra_capex: float = 0.0,
                     line_capacity_mw: float = LINE_CAPACITY_MW,
                     line_km: float = LINE_KM) -> dict:
    project = next(r for r in read_cost_references() if r["source_row"] == 21)
    expansion_mw = (float(project["purchased_transformer_mva"]) -
                    float(project["replaced_old_transformer_mva"])) * 0.95
    project_net_increment_per_mw = float(project["static_total_10k_cny"]) / expansion_mw
    model_coefficient = next(r["base_coefficient_10k_cny_per_purchased_mva"]
                             for r in replacement_cost_coefficients() if r["voltage_kv"] == 110)
    transformer_per_mw = model_coefficient / .95
    line_per_mw = (line_capex_10k_cny(line_km, line_unit_cost)
                   + line_extra_capex) / line_capacity_mw
    storage_per_mw = storage_replicated_package_capex_10k_cny(10) / (10 * min(.1, .215 / 3))
    factors = cost_factors()
    transformer_npv = transformer_per_mw * factors["transformer"][2025]
    line_npv = line_per_mw * factors["line"][2025]
    storage_npv = storage_per_mw * factors["storage"][2025]
    return {"reference_transformer_project_row": 21,
            "reference_peak_duration_hours": 3,
            "transformer_model_10k_per_purchased_mva": model_coefficient,
            "reference_row_21_10k_per_net_added_mw": project_net_increment_per_mw,
            "transformer_expansion_10k_per_effective_mw": transformer_per_mw,
            "new_line_10k_per_effective_mw": line_per_mw,
            "storage_10k_per_effective_mw": storage_per_mw,
            "transformer_to_line_base_ratio": transformer_per_mw / line_per_mw,
            "expansion_to_storage_base_ratio": transformer_per_mw / storage_per_mw,
            "transformer_to_line_lifecycle_ratio": transformer_npv / line_npv,
            "expansion_to_storage_lifecycle_ratio": transformer_npv / storage_npv,
            "reference_in_service_year": 2025,
            "scope": "transformer_model_price_per_purchased_mva_divided_by_pf;_replacement_net_MW_differs;_line_extra_as_parameter;_civil_bay_protection_unpriced"}


def run(output_dir: Path = OUTPUT, cases: tuple[str, ...] = ("pizhou_base", "pizhou_no_existing", "city_base"),
        baseline_mode: str = "historical_proxy",
        allow_capacity_release: bool = True,
        preserve_baseline_forward_margin: bool = False,
        baseline_margin_fraction: float = 1.0,
        line_unit_cost: float = LINE_BASE_10K_PER_KM,
        line_extra_capex: float = 0.0,
        line_capacity_mw: float = LINE_CAPACITY_MW,
        line_km: float = LINE_KM,
        max_lines: int = 12,
        new_line_station_pair: tuple[str, str] | None = None,
        existing_transfer_capacity_mw: float | None = None,
        existing_transfer_capacity_mw_by_year: dict[int, float] | None = None,
        line_capacity_mw_by_year: dict[int, float] | None = None,
        existing_station_pair: tuple[str, str] | None = None,
        maximum_transfer_fraction: float | None = None,
        prefer_reserve_at_equal_cost: bool = True,
        canonicalize_tie_dispatch: bool = True,
        elastic_clr_cap: float = 2.4,
        minimum_clr_by_year: dict[int, float] | None = None,
        elastic_target_2025_clr: float | None = None,
        station_choice_cap_slack_mva: float | None = None,
        pairwise_transfer: bool = False,
        new_line_candidate_pairs: list[tuple[str, str]] | None = None,
        pizhou_existing_fraction: float | None = None,
        load_scenario: str = "observed_annual",
        elastic_no_10kv: bool = False) -> list[dict]:
    output_dir = Path(output_dir)
    sample = pizhou_sample_fraction()
    cost_ratios = base_cost_ratios(line_unit_cost, line_extra_capex,
                                   line_capacity_mw, line_km)
    if baseline_mode == "historical_proxy":
        station_baseline, _ = build()
    elif baseline_mode == "planning_2021":
        station_baseline = read_csv(OUTPUT_DIR / "planning_2021_common_baseline_stations.csv")
    elif baseline_mode == "near2_2021":
        station_baseline = read_csv(OUTPUT_DIR / "baseline_2021_station_candidates.csv")
    else:
        raise ValueError("未知的2021年仿真起点口径")
    baseline = {(r["study_region_id"], int(r["voltage_kv"]), r["model_station_id"]): r
                for r in station_baseline}
    _, scenes, durations, peaks, catalog, coefficients = load_inputs()
    if load_scenario == "weighted_4y_growth":
        scenes, peaks, profile, growth_sources = apply_pizhou_weighted_growth(
            baseline, scenes, peaks)
        write_csv(profile, output_dir / "weighted_growth_load_profile.csv")
        write_csv(growth_sources, output_dir / "weighted_growth_source_rates.csv")
    elif load_scenario != "observed_annual":
        raise ValueError("未知负荷情景")
    pz_initial_fraction = (sample["initial_fraction"] if pizhou_existing_fraction is None
                           else pizhou_existing_fraction)
    definitions = {
        "pizhou_base": (PIZHOU, sample["initial_fraction"], .55),
        "pizhou_no_existing": (PIZHOU, 0.0, .55),
        "city_base": (CITY, .50, .70),
        "pizhou_rigid": (PIZHOU, pz_initial_fraction, 1.0),
        "pizhou_elastic": (PIZHOU, pz_initial_fraction, 1.0),
        "pizhou_elastic_target": (PIZHOU, pz_initial_fraction, 1.0),
    }
    summaries, annual = [], []
    for case in cases:
        layer, initial, maximum = definitions[case]
        if maximum_transfer_fraction is not None:
            maximum = maximum_transfer_fraction
        case_max_lines = max_lines if layer == PIZHOU else 0
        case_new_line_pair = new_line_station_pair if layer == PIZHOU else None
        is_elastic = case in ("pizhou_elastic", "pizhou_elastic_target")
        no_tie_elastic = is_elastic and elastic_no_10kv
        if no_tie_elastic:
            initial = maximum = 0.0
        case_minimum_clr = dict(minimum_clr_by_year or {})
        if case == "pizhou_elastic_target" and elastic_target_2025_clr is not None:
            case_minimum_clr[2025] = elastic_target_2025_clr
        case_transfer = None if no_tie_elastic else {
            "initial_fraction": initial,
            "maximum_fraction": maximum,
            "line_capacity_mw": line_capacity_mw,
            "line_capacity_mw_by_year": line_capacity_mw_by_year,
            "max_lines": case_max_lines,
            "new_line_station_pair": case_new_line_pair,
            "existing_capacity_mw": existing_transfer_capacity_mw,
            "existing_capacity_mw_by_year": existing_transfer_capacity_mw_by_year,
            "existing_station_pair": existing_station_pair if layer == PIZHOU else None,
            "pairwise": pairwise_transfer if layer == PIZHOU else False,
            "new_line_candidate_pairs": new_line_candidate_pairs,
        }
        print(f"START {case}", flush=True)
        stations, years, transfers, summary = solve_layer(
            layer, baseline, scenes, durations, peaks, catalog, coefficients,
            cost_factors(), elastic_clr_cap if is_elastic else 2.0,
            not is_elastic, line_km=line_km,
            line_unit_cost=line_unit_cost,
            line_extra_capex_10k_cny=line_extra_capex,
            policy_peak_basis="annual", max_storage_modules=50,
            require_existing_tie_operation=not no_tie_elastic,
            allow_capacity_release=allow_capacity_release,
            preserve_baseline_forward_margin=preserve_baseline_forward_margin,
            baseline_margin_fraction=baseline_margin_fraction,
            prefer_reserve_at_equal_cost=prefer_reserve_at_equal_cost,
            canonicalize_tie_dispatch=canonicalize_tie_dispatch, contingency_service_fraction=None,
            minimum_clr_by_year=case_minimum_clr,
            station_choice_cap_slack_mva=station_choice_cap_slack_mva,
            tie_allowed=False if no_tie_elastic else None,
            existing_tie_allowed=not no_tie_elastic,
            regional_transfer=case_transfer,
        )
        write_csv(stations, output_dir / f"{case}_stations.csv")
        write_csv(years, output_dir / f"{case}_years.csv")
        if transfers:
            write_csv(transfers, output_dir / f"{case}_transfers.csv")
        summary.update({"case_id": case, "initial_transfer_fraction": initial,
                        "maximum_transfer_fraction": maximum,
                        "baseline_mode": baseline_mode,
                        "initial_fraction_source": ("not_applicable_elastic_no_10kv" if no_tie_elastic else
                                                    "unused_in_pairwise_absolute_MW_model" if pairwise_transfer
                                                    else sample["status"] if layer == PIZHOU
                                                    else "meeting_assumption_city_50pct"),
                        "cost_scope": "2022_to_2041_incremental_lifecycle_npv_base_2021",
                        "existing_capacity_release_cost": 0,
                        "minimum_clr_by_year": str(case_minimum_clr),
                        "station_choice_cap_slack_mva": station_choice_cap_slack_mva})
        if no_tie_elastic and (transfers or any(y["line_built"] for y in years)):
            raise AssertionError("弹性方案不得包含既有或新建 10 kV 联络")
        summaries.append(summary)
        previous_lines = 0
        for year in years:
            yr = year["year"]
            local = [r for r in stations if r["year"] == yr]
            shifts = {}
            for scenario in ("forward", "reverse"):
                for kind in ("existing", "new"):
                    shifts[scenario, kind] = sum(
                        float(t["transfer_mw"]) for t in transfers
                        if t["year"] == yr and t["scenario"] == scenario
                        and t["tie_id"] == f"REGIONAL-{kind}"
                        and (pairwise_transfer or t["receiver_station_id"] == "REGIONAL-HUB"))
            annual.append({"case_id": case, "study_region_id": layer[0],
                           "voltage_kv": layer[1], "year": yr,
                           "station_count": year["station_count"],
                           "net_peak_mw": year["synchronous_forward_peak_mw"],
                           "selected_capacity_mva": year["selected_capacity_mva"],
                           "clr": year["actual_clr"],
                           "transformer_investment_10k_cny": round(sum(float(r["transformer_capex_10k_cny"]) for r in local), 6),
                           "capacity_release_mva": round(sum(float(r["released_capacity_mva"]) for r in local), 6),
                           "new_storage_modules": sum(int(r["new_storage_modules"]) for r in local),
                           "storage_modules_in_service": year["storage_modules_in_service"],
                           "existing_transfer_forward_mw": round(shifts["forward", "existing"], 6),
                           "existing_transfer_reverse_mw": round(shifts["reverse", "existing"], 6),
                           "new_line_transfer_forward_mw": round(shifts["forward", "new"], 6),
                           "new_line_transfer_reverse_mw": round(shifts["reverse", "new"], 6),
                           "new_lines_in_service": year["line_built"],
                           "new_lines_commissioned": year["line_built"] - previous_lines,
                           "line_investment_10k_cny": year["new_line_capex_10k_cny"],
                           "year_lifecycle_npv_10k_cny": year["year_lifecycle_npv_10k_cny"],
                           "path_lifecycle_npv_10k_cny": summary["objective_npv_10k_cny"],
                           "source_status": ("pizhou_weighted_4y_growth_forecast_not_observed_annual"
                                             if load_scenario == "weighted_4y_growth" else
                                             "pizhou_20_station_near_county_2025_peak_with_estimated_scenarios"
                                             if layer == PIZHOU else "city_29_station_sample")})
            previous_lines = year["line_built"]
        write_csv(summaries, output_dir / "summary.csv")
        write_csv(annual, output_dir / "annual_measures.csv")
        print(f"DONE {case} {summary['objective_npv_10k_cny']}", flush=True)
    (output_dir / "assumptions.json").write_text(
        json.dumps({"pizhou_sample_transfer": sample, "base_cost_ratios": cost_ratios,
                    "guide_reference": "2025_revised_draft_9.2.1.2_not_7.1.2",
                    "new_line_km_each": line_km, "new_line_capacity_mw_each": line_capacity_mw,
                    "line_cost_10k_per_km": line_unit_cost,
                    "line_extra_capex_10k_cny_each": line_extra_capex,
                    "max_lines": max_lines,
                    "new_line_station_pair": new_line_station_pair,
                    "existing_transfer_capacity_mw": existing_transfer_capacity_mw,
                    "existing_transfer_capacity_mw_by_year": existing_transfer_capacity_mw_by_year,
                    "line_capacity_mw_by_year": line_capacity_mw_by_year,
                    "existing_station_pair": existing_station_pair,
                    "storage_and_line_scenarios": "planning_estimates_not_site_engineering_quotes",
                    "baseline_mode": baseline_mode,
                    "allow_capacity_release_after_2021": allow_capacity_release,
                    "preserve_baseline_forward_margin": preserve_baseline_forward_margin,
                    "baseline_margin_fraction": baseline_margin_fraction,
                    "prefer_reserve_at_equal_cost": prefer_reserve_at_equal_cost,
                    "canonicalize_tie_dispatch": canonicalize_tie_dispatch,
                    "elastic_clr_cap": elastic_clr_cap,
                    "minimum_clr_by_year": minimum_clr_by_year,
                    "elastic_target_2025_clr": elastic_target_2025_clr,
                    "station_choice_cap_slack_mva": station_choice_cap_slack_mva,
                    "pairwise_transfer": pairwise_transfer,
                    "new_line_candidate_pairs": new_line_candidate_pairs,
                    "pizhou_existing_fraction": pizhou_existing_fraction,
                    "load_scenario": load_scenario,
                    "elastic_no_10kv": elastic_no_10kv},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summaries


if __name__ == "__main__":
    run()
