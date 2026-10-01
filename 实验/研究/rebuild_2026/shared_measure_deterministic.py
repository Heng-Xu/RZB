"""相同三措施、固定输入、限制转供的确定性成本优化。"""

import argparse
import hashlib
import json
import os
from pathlib import Path

from .baseline_2021 import read_csv
from .city_mapping_audit import write_csv
from .regional_static_milp_v2 import input_data, run
from .regional_static_milp_v2_audit import audit
from .two_district_ordered_guide_run import guide_range
from .planning_load_profile import weighted_annual_growth
from .hourly_source_profile import OUTPUT_DIR


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "outputs/shared_measure_deterministic"
DISTRICTS = {"pizhou": ("QX-00005", 110), "city": ("QX-00007", 110)}
CASES = {"reference": None, "transfer_20pct": .2, "transfer_10pct": .1}
YEARS = (2022, 2023, 2024, 2025)


def settings():
    for key, value in {
        "XUZHOU_MILP_BACKEND": "highspy", "XUZHOU_MILP_THREADS": "1",
        "XUZHOU_MILP_SEED": "0", "XUZHOU_MILP_REL_GAP": "1e-9",
        "XUZHOU_MILP_TIME_LIMIT_SECONDS": "180",
        "XUZHOU_SOLVER_TRACE": "1",
    }.items():
        os.environ[key] = value


def run_case(name):
    settings()
    observed = {}
    for row in read_csv(OUTPUT_DIR / "official_annual.csv"):
        region = row["region_id"], int(row["voltage_kv"])
        if region in DISTRICTS.values():
            observed.setdefault(region, {})[int(row["year"])] = float(
                row["reported_downward_load_mw"])
    folder = OUTPUT / name
    for label, region in DISTRICTS.items():
        growth, _ = weighted_annual_growth(observed[region])
        minimum, upper = guide_range(growth)
        common = dict(
            region=region, rigid_cap=2.0, elastic_cap=2.6, min_clr=minimum,
            require_transformer_n1=True, n1_load_requirement="bc_min_service_static",
            elastic_allow_line_decisions=True, enforce_expansion_slot=True,
            max_transfer_fraction=CASES[name], storage_max_mwh_per_station=None,
            prefer_larger_clr=True, minimize_transfer_tiebreak=True)
        if label == "city":
            common["city_baseline_cap_mva"] = upper * observed[region][2021]
        run(folder / label, **common)
        print(audit(folder / label), flush=True)
    return review_case(name)


def review_case(name):
    folder = OUTPUT / name
    portfolios = {}
    table = []
    for label in DISTRICTS:
        summaries = {row["scheme"]: row for row in json.loads(
            (folder / label / "summary.json").read_text())}
        rows = {scheme: {int(row["year"]): row for row in read_csv(
            folder / label / f"{scheme}_years.csv")} for scheme in summaries}
        portfolios[label] = {"summaries": summaries, "years": rows}
        for scheme in rows:
            for year, row in rows[scheme].items():
                table.append({"district": label, **row})
    cost_order = {label: portfolios[label]["summaries"]["elastic"]["objective_npv_10k"] <
                  portfolios[label]["summaries"]["rigid"]["objective_npv_10k"] - .01
                  for label in DISTRICTS}
    district_order = all(float(portfolios["city"]["years"][scheme][year]["clr"]) <
                         float(portfolios["pizhou"]["years"][scheme][year]["clr"]) - 1e-7
                         for scheme in ("rigid", "elastic") for year in YEARS)
    elastic_above_rigid = all(float(portfolios[label]["years"]["elastic"][year]["clr"]) >=
                             float(portfolios[label]["years"]["rigid"][year]["clr"]) - 1e-7
                             for label in DISTRICTS for year in YEARS)
    break_2 = {label: [year for year in YEARS if
                      float(portfolios[label]["years"]["elastic"][year]["clr"]) > 2 + 1e-7]
               for label in DISTRICTS}
    result = {
        "case": name, "max_transfer_fraction": CASES[name],
        "same_measure_set": True, "same_start_per_district": True,
        "cost_order": cost_order, "city_below_pizhou_all_years": district_order,
        "elastic_at_least_rigid_all_years": elastic_above_rigid,
        "elastic_break_2_years": break_2,
        "all_requested_relations": all(cost_order.values()) and district_order and
                                   elastic_above_rigid and all(break_2.values()),
        "cost_npv_10k": {label: {scheme: summaries["objective_npv_10k"]
                                for scheme, summaries in portfolios[label]["summaries"].items()}
                         for label in DISTRICTS},
        "ordering_constraints_imposed": False,
        "transfer_limit_basis": "research_operational_scenario_same_in_both_schemes",
        "storage_upper_basis": "station_full_peak_task_times_duration_rounded_to_modules",
    }
    write_csv(table, folder / "annual_comparison.csv")
    (folder / "review.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=CASES, default="transfer_10pct")
    args = parser.parse_args()
    result = run_case(args.case)
    evidence = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                for name in ("shared_measure_deterministic.py", "regional_static_milp_v2.py",
                             "regional_static_milp_v2_audit.py",
                             "annual_no_tie_investment_submodel.py")}
    (OUTPUT / args.case / "model_hashes.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
