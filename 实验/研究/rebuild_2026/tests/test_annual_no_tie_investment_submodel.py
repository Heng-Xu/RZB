from rebuild_2026.annual_no_tie_investment_submodel import build_annual_no_tie_investment_submodel


def test_research_ceiling_changes_only_supported_submodel_result() -> None:
    stations, years, layers = build_annual_no_tie_investment_submodel(
        capacity_load_caps={"QX-00005": 4.0, "QX-00007": 3.0}
    )
    assert len(stations) == 228
    assert len(years) == 12
    assert len(layers) == 3
    for row in years:
        assert row["actual_clr"] <= row["clr_cap"] + 1e-8
    by_layer = {(row["study_region_id"], row["voltage_kv"]): row for row in layers}
    assert by_layer["QX-00005", 35]["investment_npv_10k_cny"] == 2025.025475
    assert by_layer["QX-00005", 35]["clr_cap"] == 4.0
    assert by_layer["QX-00007", 110]["clr_cap"] == 3.0
