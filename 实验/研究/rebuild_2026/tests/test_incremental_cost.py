from collections import Counter

import pytest

from rebuild_2026.incremental_cost import (
    cost_parameter_inventory,
    discount_to_2021,
    lifecycle_cashflows,
    line_capex_10k_cny,
    npv_10k_cny,
    replacement_cost_coefficients,
    storage_anchors,
    storage_capex_10k_cny,
    storage_replicated_package_capex_10k_cny,
    summarize_transformer_capex,
    transformer_upgrade_events,
)
from rebuild_2026.transformer_only_path_2021_2025 import build_transformer_only_path


def test_storage_case_prices_are_read_from_primary_case_register():
    single, ten = storage_anchors()
    assert single == 27.2
    assert ten == pytest.approx(210.456262)
    assert storage_capex_10k_cny(0) == 0
    assert storage_capex_10k_cny(1) == single
    assert storage_capex_10k_cny(10) == ten
    assert storage_capex_10k_cny(5) == pytest.approx(single + (ten - single) * 4 / 9)
    with pytest.raises(ValueError, match="0—10"):
        storage_capex_10k_cny(11)


def test_large_storage_screen_repeats_ten_cabinet_packages_as_an_assumption():
    ten = storage_capex_10k_cny(10)
    assert storage_replicated_package_capex_10k_cny(0) == 0
    assert storage_replicated_package_capex_10k_cny(10) == ten
    assert storage_replicated_package_capex_10k_cny(11) == pytest.approx(ten + 27.2)
    assert storage_replicated_package_capex_10k_cny(20) == pytest.approx(2 * ten)
    with pytest.raises(ValueError, match="非负整数"):
        storage_replicated_package_capex_10k_cny(-1)


def test_line_and_discounting_use_incremental_2021_end_basis():
    assert line_capex_10k_cny(2) == pytest.approx(89.086)
    assert discount_to_2021(106, 2022, 0.06) == pytest.approx(100)
    assert discount_to_2021(100, 2025, 0.0) == 100
    assert npv_10k_cny([
        {"year": 2022, "amount_10k_cny": 106},
        {"year": 2023, "amount_10k_cny": 112.36},
    ], 0.06) == pytest.approx(200)
    with pytest.raises(ValueError, match="2022—2041"):
        discount_to_2021(100, 2021, 0.06)


def test_lifecycle_cashflows_make_om_and_renewal_explicit():
    rows = lifecycle_cashflows(100, 2022, 10, 0.03)
    assert [(row["year"], row["amount_10k_cny"]) for row in rows if row["component"] == "renewal_capex"] == [
        (2032, 100),
    ]
    assert len([row for row in rows if row["component"] == "fixed_om"]) == 19
    assert next(row["amount_10k_cny"] for row in rows if row["component"] == "fixed_om") == 3
    assert sum(row["amount_10k_cny"] for row in rows) == 257
    assert len([row for row in lifecycle_cashflows(100, 2022, 30, 0) if row["component"] == "renewal_capex"]) == 0


def test_replacement_coefficients_use_matched_cases_and_purchased_capacity():
    by_voltage = {row["voltage_kv"]: row for row in replacement_cost_coefficients()}
    assert by_voltage[110]["source_case_rows"] == "21;36"
    assert by_voltage[110]["purchased_transformer_mva_sum"] == 150
    assert by_voltage[110]["base_coefficient_10k_cny_per_purchased_mva"] == pytest.approx(2486 / 150)
    assert by_voltage[110]["low_case_coefficient_10k_cny_per_purchased_mva"] == 13.35
    assert by_voltage[110]["high_case_coefficient_10k_cny_per_purchased_mva"] == 23.02
    assert by_voltage[35]["source_case_rows"] == "43;45;48;54"
    assert by_voltage[35]["purchased_transformer_mva_sum"] == 100
    assert by_voltage[35]["base_coefficient_10k_cny_per_purchased_mva"] == 15.48
    assert by_voltage[35]["low_case_coefficient_10k_cny_per_purchased_mva"] == 13.725
    assert by_voltage[35]["high_case_coefficient_10k_cny_per_purchased_mva"] == 18.2


def test_transformer_events_are_per_unit_priced_and_exclude_baseline():
    stations, layers = build_transformer_only_path()
    events = transformer_upgrade_events(stations)
    assert events
    assert min(event["year"] for event in events) == 2022
    assert all(event["purchased_unit_mva"] > event["old_unit_mva"] for event in events)
    assert all(event["investment_10k_cny"] > 0 for event in events)
    assert all(event["price_status"] == "simulation_scaled_local_replacement_cases" for event in events)
    variants = Counter(event["reverse_variant"] for event in events)
    assert variants["night_central"] == variants["early_pv_high"]
    assert all(event["operation"] == "simulated_replacement_uprating" for event in events)
    increments = Counter()
    for event in events:
        key = event["study_region_id"], event["voltage_kv"], event["year"], event["reverse_variant"]
        increments[key] += event["net_capacity_increment_mva"]
    for row in layers:
        key = row["study_region_id"], row["voltage_kv"], row["year"], row["reverse_variant"]
        assert increments[key] == pytest.approx(row["year_capacity_increment_mva"])
    assert all(
        event["investment_10k_cny"] == pytest.approx(
            event["purchased_unit_mva"] * (15.48 if event["voltage_kv"] == 35 else 2486 / 150)
        ) for event in events
    )
    summaries = summarize_transformer_capex(events, layers)
    assert len(summaries) == 3 * 4 * 2
    assert sum(row["base_capex_10k_cny"] for row in summaries if row["reverse_variant"] == "night_central") == pytest.approx(
        sum(event["investment_10k_cny"] for event in events if event["reverse_variant"] == "night_central")
    )


def test_cost_inventory_keeps_quotes_separate_from_scenario_assumptions():
    by_key = {row["parameter"]: row for row in cost_parameter_inventory()}
    assert by_key["existing_tie_incremental_capex"]["value"] == 0
    assert by_key["storage_one_module_cost"]["status"] == "tender_ceiling_not_award"
    assert by_key["storage_above_10_package_rule"]["status"] == "simulation_only_unverified_large_site"
    assert by_key["discount_rate"]["value"] == 0.06
    assert by_key["discount_rate"]["status"] == "research_base_case_with_4_8pct_sensitivity"
    assert by_key["planned_new_tie_route_length"]["value"] == 2.52
    assert by_key["transformer_replacement_35kv_per_purchased_mva"]["value"] == 15.48
    assert by_key["transformer_replacement_110kv_per_purchased_mva"]["value"] == pytest.approx(2486 / 150)
    assert by_key["project_case_sheet1_row_14"]["value"] == 1206
    assert by_key["project_case_sheet1_row_43"]["value"] == 322
