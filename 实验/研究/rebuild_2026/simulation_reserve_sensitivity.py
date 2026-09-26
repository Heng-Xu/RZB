"""历史容量起点下的预算、价格和停运恢复比例敏感性。"""

from pathlib import Path

from .baseline_historical_proxy import build as build_baseline
from .city_mapping_audit import write_csv
from .joint_lifecycle_optimizer import (
    DESIGNED_NEW_LINE_KM, PIZHOU_110, cost_factors, load_inputs, solve_layer,
)
from .simulation_reserve_policy import OUTPUT


def run(output_dir: Path = OUTPUT) -> list[dict]:
    stations, _ = build_baseline()
    baseline = {(r["study_region_id"], int(r["voltage_kv"]), r["model_station_id"]): r
                for r in stations}
    _, scene, durations, peaks, catalog, coefficients = load_inputs()
    cases = [
        ("pizhou_110_rigid_budget_3pct", PIZHOU_110, True, .03, .60, 1.0, 1.0),
        ("pizhou_110_rigid_budget_4pct", PIZHOU_110, True, .04, .60, 1.0, 1.0),
        ("pizhou_110_rigid_transformer_70pct", PIZHOU_110, True, .03, .60, .7, 1.0),
        ("pizhou_110_elastic_transformer_70pct", PIZHOU_110, False, None, .60, .7, 1.0),
        ("pizhou_110_rigid_storage_150pct", PIZHOU_110, True, .03, .60, 1.0, 1.5),
        ("pizhou_110_elastic_storage_150pct", PIZHOU_110, False, None, .60, 1.0, 1.5),
        ("city_110_rigid_recovery_40pct", ("QX-00007", 110), True, .01, .40, 1.0, 1.0),
        ("city_110_rigid_recovery_50pct", ("QX-00007", 110), True, .01, .50, 1.0, 1.0),
    ]
    rows = []
    for name, layer, rigid, budget, recovery, transformer_price, storage_price in cases:
        try:
            _, years, transfers, summary = solve_layer(
                layer, baseline, scene, durations, peaks, catalog, coefficients,
                cost_factors(), 2.0 if rigid else 3.2, rigid,
                include_new_line=layer == PIZHOU_110,
                new_line_variant="designed_bus", line_km=DESIGNED_NEW_LINE_KM,
                tie_allowed=layer == PIZHOU_110,
                transformer_cost_scale=transformer_price,
                storage_cost_scale=storage_price,
                policy_peak_basis="annual", max_storage_modules=50,
                allow_capacity_release=True,
                capacity_growth_budget_fraction=budget,
                prefer_reserve_at_equal_cost=True,
                contingency_service_fraction=recovery,
                require_existing_tie_operation=False,
                tie_year_basis="annual_station_scaled",
                canonicalize_tie_dispatch=True,
            )
            result = {"case_id": name, "status": "optimal",
                      "cost_npv_10k_cny": summary["objective_npv_10k_cny"],
                      "max_clr": summary["max_actual_clr"],
                      "capacity_2025_mva": years[-1]["selected_capacity_mva"],
                      "clr_2025": years[-1]["actual_clr"],
                      "storage_2025_modules": years[-1]["storage_modules_in_service"],
                      "new_line_built_2025": years[-1]["line_built"],
                      "transfer_2025_mw": round(sum(float(r["transfer_mw"]) for r in transfers
                                                    if r["year"] == 2025 and r["scenario"] == "forward"), 6),
                      "solver_detail": ""}
        except ValueError as exc:
            result = {"case_id": name, "status": "no_proven_optimum",
                      "cost_npv_10k_cny": "", "max_clr": "", "capacity_2025_mva": "",
                      "clr_2025": "", "storage_2025_modules": "", "new_line_built_2025": "",
                      "transfer_2025_mw": "", "solver_detail": str(exc)}
        rows.append({"study_region_id": layer[0], "voltage_kv": layer[1],
                     "scheme": "rigid" if rigid else "elastic",
                     "gross_budget_fraction": budget if budget is not None else "",
                     "contingency_fraction": recovery,
                     "transformer_price_scale": transformer_price,
                     "storage_price_scale": storage_price, **result})
    write_csv(rows, Path(output_dir) / "sensitivity.csv")
    return rows


if __name__ == "__main__":
    for row in run():
        print(row["case_id"], row["status"], row["cost_npv_10k_cny"])
