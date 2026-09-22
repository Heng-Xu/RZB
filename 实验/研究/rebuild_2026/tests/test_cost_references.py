from rebuild_2026.cost_references import read_cost_references


def test_original_investments_keep_project_scope_and_replacement_denominator():
    rows = read_cost_references()
    by_row = {row["source_row"]: row for row in rows}
    assert len(rows) == 4
    assert by_row[14]["project_capacity_increment_mva"] == 50
    assert by_row[14]["static_total_10k_cny"] == 1206
    assert by_row[16]["static_total_10k_cny"] == 1240
    assert by_row[43]["project_capacity_increment_mva"] == 10
    assert by_row[43]["static_total_10k_cny"] == 322
    assert by_row[45]["static_total_10k_cny"] == 313
    assert all(row["pricing_role"] == "project_case_reference_not_generic_unit_price" for row in rows)
