from rebuild_2026.rooftop_area_audit import (
    capacity_scenario_mw,
    pizhou_village_match,
    read_roof_records,
    scope_areas,
)


def test_roof_area_excludes_rural_subtotal_and_retains_distinct_urban_area() -> None:
    records = read_roof_records()
    assert len(records) == 2724
    assert len({row["area_id"] for row in records}) == len(records)
    areas = scope_areas(records)
    assert round(areas["QX-00005"], 3) == 89391862.785
    assert round(areas["urban_core_proxy"], 3) == 40823592.042
    assert capacity_scenario_mw(areas["QX-00005"], 0.20) == areas["QX-00005"] * 0.20 * 0.10 / 1000


def test_pizhou_village_keys_join_without_assuming_station_allocation() -> None:
    match = pizhou_village_match(read_roof_records())
    assert match["roof_area_ids"] == 498
    assert match["matched_area_ids"] == 496
