"""独立复核联合输出、方案比较及重复计算的一致性。"""

import argparse
import hashlib
import json
from pathlib import Path

from .baseline_2021 import read_csv
from .joint_lifecycle_optimizer import cost_factors


YEARS = (2022, 2023, 2024, 2025)


def audit(directory, repeat_directory=None):
    directory = Path(directory)
    review = json.loads((directory / "review.json").read_text())
    annual = read_csv(directory / "annual_comparison.csv")
    assert len(annual) == 16
    by_key = {(r["district"], r["scheme"], int(r["year"])): r for r in annual}
    assert len(by_key) == 16
    computed_costs = {}
    total_npv = 0.0
    margin = float(review["ordering_margin"])
    factors = cost_factors()
    digests = {}
    for label in ("pizhou", "city"):
        summaries = {r["scheme"]: r for r in json.loads(
            (directory / label / "summary.json").read_text())}
        assert summaries["rigid"]["baseline_2021_capacity_mva"] == summaries[
            "elastic"]["baseline_2021_capacity_mva"]
        for field in (
            "baseline_2021_load_mw", "load_scenario", "transformer_scale", "line_scale",
            "storage_scale", "transformer_price_10k_per_purchased_mva",
            "third_50mva_project_price_10k", "storage_price_10k_per_mwh",
            "line_price_10k_per_planned_pair", "existing_transfer_fraction",
            "target_transfer_fraction", "max_transfer_fraction",
            "n1_load_requirement", "enforce_expansion_slot",
            "storage_upper_by_station_mwh",
            "transfer_mode", "installed_transfer_target_enforced", "n1_demand_basis",
            "transfer_capacity_model", "new_line_increment_mw", "new_line_capacity_year_rule",
            "station_fraction_ceiling", "existing_county_budget_enforced",
            "station_transfer_representation", "new_line_endpoint_representation",
            "new_increment_shared_use_rule",
        ):
            assert summaries["rigid"].get(field) == summaries["elastic"].get(field), (label, field)
        for scheme in ("rigid", "elastic"):
            summary = summaries[scheme]
            rows = read_csv(directory / label / f"{scheme}_years.csv")
            assert len(rows) == 4
            previous = float(summary["baseline_2021_capacity_mva"])
            cost = 0.0
            for row in rows:
                year = int(row["year"])
                aggregated = by_key[label, scheme, year]
                assert row == {k: v for k, v in aggregated.items() if k != "district"}
                capacity = float(row["capacity_mva"])
                assert capacity >= previous - 1e-6
                assert abs(float(row["clr"]) - capacity / float(row["net_peak_proxy_mw"])) < 1e-8
                if scheme == "rigid":
                    assert float(row["clr"]) <= 2 + 1e-6
                elif review["breakthrough_requirement"] == "all_years":
                    assert float(row["clr"]) >= 2 + margin - 1e-6
                cost += sum(float(row[component + "_capex_10k"]) * factors[component][year]
                            for component in ("transformer", "storage", "line"))
                previous = capacity
            assert abs(cost - float(summary["objective_npv_10k"])) < 1e-3
            computed_costs[label, scheme] = cost
            total_npv += cost
        assert (directory / label / "audit.json").exists()
        assert all(r["status"] == "PASS" for r in json.loads(
            (directory / label / "audit.json").read_text()))
    for year in YEARS:
        for scheme in ("rigid", "elastic"):
            assert float(by_key["city", scheme, year]["clr"]) + margin <= (
                float(by_key["pizhou", scheme, year]["clr"]) + 1e-6)
        for label in ("pizhou", "city"):
            assert float(by_key[label, "rigid", year]["clr"]) + margin <= (
                float(by_key[label, "elastic", year]["clr"]) + 1e-6)
    assert total_npv <= float(review["joint_minimum_primary_objective_10k"]) + float(
        review["cost_tiebreak_tolerance_10k"]) + 1e-3
    assert all(stage.get("status") == "optimal" for stage in review["solve_history"])
    for stage in review["solve_history"]:
        assert float(stage["mip_gap"]) <= float(stage.get("mip_relative_gap_target", 1e-9)) + 1e-9
    primary = review["solve_history"][0]
    if primary.get("objective_lower_bound") is not None:
        assert float(primary["objective_lower_bound"]) <= float(primary["objective"]) + 1e-4
        gap = max(0, (float(primary["objective"]) - float(primary["objective_lower_bound"])) /
                  max(1e-9, abs(float(primary["objective"]))))
        assert abs(gap - float(primary["mip_gap"])) < 1e-8
    assert all(r["status"].startswith("PASS") for r in json.loads(
        (directory / "source_audit.json").read_text()))
    if repeat_directory is not None:
        original_files = {str(p.relative_to(directory)) for p in directory.rglob("*.csv")}
        repeat_files = {str(p.relative_to(Path(repeat_directory)))
                        for p in Path(repeat_directory).rglob("*.csv")}
        assert original_files == repeat_files, "重复求解的CSV文件集合不一致"
    for path in sorted(directory.rglob("*.csv")):
        relative = path.relative_to(directory)
        digests[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
        if repeat_directory is not None:
            assert path.read_bytes() == (Path(repeat_directory) / relative).read_bytes(), str(relative)
    result = {
        "numerical_and_planning_checks": "PASS", "annual_records": 16,
        "primary_cost_solution_quality": review.get("primary_cost_solution_quality", "optimal_within_tight_tolerance"),
        "primary_cost_relative_gap": float(primary["mip_gap"]),
        "primary_cost_lower_bound_10k": primary.get("objective_lower_bound"),
        "same_prices_load_start_and_measure_limits": "PASS",
        "rigid_npv_10k": sum(computed_costs[label, "rigid"] for label in ("pizhou", "city")),
        "elastic_npv_10k": sum(computed_costs[label, "elastic"] for label in ("pizhou", "city")),
        "elastic_cost_below_rigid": {
            label: computed_costs[label, "elastic"] < computed_costs[label, "rigid"] - .01
            for label in ("pizhou", "city")},
        "repeat_csv_exact_match": True if repeat_directory is not None else None,
        "output_sha256": digests,
    }
    (directory / "independent_audit.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--repeat", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.directory, args.repeat), ensure_ascii=False))
