from math import sqrt

import pytest

from rebuild_2026.pizhou_existing_ties import (
    active_mw_at_current,
    build_existing_tie_screen,
    build_feeder_headroom,
    check_simultaneous_transfers,
    read_cross_station_ties,
)


def test_six_feeder_headroom_uses_current_and_flags_conflicting_power():
    feeders = build_feeder_headroom()
    assert len(feeders) == 6
    by_id = {row["feeder_id"]: row for row in feeders}
    assert by_id["PZXL-00154"]["reported_max_active_power_mw"] == 0
    assert by_id["PZXL-00154"]["source_power_status"] == "zero_active_power_conflicts_with_current"
    assert by_id["PZXL-00154"]["current_equivalent_active_power_mw"] == pytest.approx(
        sqrt(3) * 10 * 544.57 * 0.95 / 1000, abs=1e-6
    )
    assert by_id["PZXL-00154"]["receiving_current_headroom_mw"] == pytest.approx(
        active_mw_at_current(600 - 544.57), abs=1e-6
    )
    assert all(row["receiving_current_headroom_mw"] >= 0 for row in feeders)


def test_three_cross_station_ties_are_screened_both_directions():
    ties = read_cross_station_ties()
    assert {row["tie_id"] for row in ties} == {"T01", "T02", "T03"}
    assert {(row["from_feeder_id"], row["to_feeder_id"]) for row in ties} == {
        ("PZXL-00092", "PZXL-00161"),
        ("PZXL-00099", "PZXL-00154"),
        ("PZXL-00097", "PZXL-00161"),
    }
    screen = build_existing_tie_screen(build_feeder_headroom(), ties)
    assert len(screen) == 6
    assert all(row["incremental_tie_investment_10k_cny"] == 0 for row in screen)
    assert all(row["forward_import_screen_mw"] <= row["receiver_feeder_headroom_mw"] for row in screen)
    assert all(row["forward_import_screen_mw"] <= row["donor_annual_current_power_upper_proxy_mw"] for row in screen)
    assert all(row["forward_import_screen_mw"] <= row["receiver_station_forward_headroom_mw"] for row in screen)
    assert all(row["reverse_import_screen_mw"] <= row["receiver_station_reverse_headroom_mw"] for row in screen)
    receiving_161 = [row for row in screen if row["receiver_feeder_id"] == "PZXL-00161"]
    assert len(receiving_161) == 2
    assert len({row["receiver_feeder_headroom_mw"] for row in receiving_161}) == 1


def test_simultaneous_transfer_checks_shared_feeder_and_district_conservation():
    feeders = build_feeder_headroom()
    ties = read_cross_station_ties()
    net = {"BDZ-00027": 54.77, "BDZ-00048": 70.93}
    capacity = {"BDZ-00027": 70.0, "BDZ-00048": 81.5}
    valid = check_simultaneous_transfers([
        {"tie_id": "T01", "donor_feeder_id": "PZXL-00092", "receiver_feeder_id": "PZXL-00161", "net_load_shift_to_receiver_mw": 2.0},
        {"tie_id": "T03", "donor_feeder_id": "PZXL-00097", "receiver_feeder_id": "PZXL-00161", "net_load_shift_to_receiver_mw": 1.0},
    ], ties, feeders, net, capacity)
    assert valid["feasible_under_static_screen"]
    assert valid["receiver_feeder_usage_mw"]["PZXL-00161"] == 3.0
    assert valid["district_net_load_after_mw"] == pytest.approx(valid["district_net_load_before_mw"])
    assert valid["post_station_net_load_mw"]["BDZ-00027"] == pytest.approx(51.77)
    assert valid["post_station_net_load_mw"]["BDZ-00048"] == pytest.approx(73.93)

    over_shared_line = check_simultaneous_transfers([
        {"tie_id": "T01", "donor_feeder_id": "PZXL-00092", "receiver_feeder_id": "PZXL-00161", "net_load_shift_to_receiver_mw": 5.0},
        {"tie_id": "T03", "donor_feeder_id": "PZXL-00097", "receiver_feeder_id": "PZXL-00161", "net_load_shift_to_receiver_mw": 3.0},
    ], ties, feeders, net, {"BDZ-00027": 100.0, "BDZ-00048": 100.0})
    assert not over_shared_line["feasible_under_static_screen"]
    assert "PZXL-00161:shared_receiving_headroom" in over_shared_line["violations"]

    over_shared_donor = check_simultaneous_transfers([
        {"tie_id": "T01", "donor_feeder_id": "PZXL-00161", "receiver_feeder_id": "PZXL-00092", "net_load_shift_to_receiver_mw": 1.5},
        {"tie_id": "T03", "donor_feeder_id": "PZXL-00161", "receiver_feeder_id": "PZXL-00097", "net_load_shift_to_receiver_mw": 1.5},
    ], ties, feeders, net, {"BDZ-00027": 100.0, "BDZ-00048": 100.0})
    assert "PZXL-00161:shared_donor_annual_current_upper_proxy" in over_shared_donor["violations"]

    reverse = check_simultaneous_transfers([
        {"tie_id": "T01", "donor_feeder_id": "PZXL-00092", "receiver_feeder_id": "PZXL-00161", "net_load_shift_to_receiver_mw": -1.0},
    ], ties, feeders, {"BDZ-00027": -35.27, "BDZ-00048": -3.48}, capacity)
    assert reverse["feasible_under_static_screen"]
    assert reverse["post_station_net_load_mw"] == {"BDZ-00027": pytest.approx(-34.27), "BDZ-00048": pytest.approx(-4.48)}
