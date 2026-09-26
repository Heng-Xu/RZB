from rebuild_2026.baseline_2021 import read_csv
from rebuild_2026.hourly_source_profile import OUTPUT_DIR


def test_joint_pressure_cases_have_nested_costs_and_auditable_years():
    summary = read_csv(OUTPUT_DIR / "source_load_sensitivity_summary.csv")
    annual = read_csv(OUTPUT_DIR / "source_load_sensitivity_annual.csv")
    assert len(summary) == 45
    assert len(annual) == 45 * 2 * 4
    assert len({row["scenario_id"] for row in summary}) == 45
    for row in summary:
        assert float(row["relaxed_npv_10k_cny"]) <= float(row["rigid_npv_10k_cny"]) + 1e-5
        for scheme in ("cap_2", "relaxed"):
            years = [r for r in annual if r["scenario_id"] == row["scenario_id"] and r["scheme"] == scheme]
            assert {int(r["year"]) for r in years} == {2022, 2023, 2024, 2025}
            assert all(float(r["actual_clr"]) <= float(r["scan_cap"]) + 1e-8 for r in years)
            assert all(int(r["tie_transfer_event_count"]) == 0 for r in years)
    base = [r for r in summary if float(r["gross_demand_factor_2022_2025"]) == 1
            and float(r["pv_output_factor_2022_2025"]) == 1 and r["price_case"] == "base"]
    assert len(base) == 3
    assert all(abs(float(r["saving_10k_cny"])) <= 1e-5 for r in base)
