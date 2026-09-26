from math import isclose

from rebuild_2026.reverse_screen_2025 import build_reverse_screen


def test_reverse_screen_is_upper_bound_risk_check_not_guide_hosting_result():
    stations, layers = build_reverse_screen()
    assert len(stations) == 57
    by_layer = {(row["study_region_id"], row["voltage_kv"]): row for row in layers}
    assert {key: row["exceeds_even_at_beta_0_8_count"] for key, row in by_layer.items()} == {
        ("QX-00005", 35): 5,
        ("QX-00005", 110): 4,
        ("QX-00007", 110): 0,
    }
    assert {key: row["reverse_station_count"] for key, row in by_layer.items()} == {
        ("QX-00005", 35): 8,
        ("QX-00005", 110): 17,
        ("QX-00007", 110): 9,
    }
    for row in stations:
        assert isclose(
            row["screening_reverse_limit_mw"],
            row["beta_assumed_upper_screen"] * row["power_factor_assumption"] * row["candidate_capacity_mva"],
            abs_tol=1e-6,
        )
        assert row["guide_sd_status"].startswith("not_computed_")
        if row["screen_status"] == "exceeds_even_at_beta_0_8":
            assert row["screening_shortfall_mw"] > 0
        else:
            assert row["screening_shortfall_mw"] == 0
