import pytest

from rebuild_2026.station_transfer_equivalent import (
    allocate_station_transfers, capacity_from_station_rate, pair_equivalent_units,
)


def test_equivalent_projects_allow_parallel_units_and_count_each_endpoint_once():
    pairs = pair_equivalent_units({"A": 3, "B": 2, "C": 1})
    assert len(pairs) == 3
    assert all(a != b for a, b in pairs)
    assert {s: sum(s in pair for pair in pairs) for s in ("A", "B", "C")} == {
        "A": 3, "B": 2, "C": 1}
    with pytest.raises(ValueError):
        pair_equivalent_units({"A": 3, "B": 1})


def test_post_solve_allocation_preserves_station_amounts_without_self_transfer():
    moves = allocate_station_transfers({"A": 8, "B": 3}, {"C": 7, "D": 4})
    assert {s: sum(r["mw"] for r in moves if r["donor"] == s) for s in ("A", "B")} == {
        "A": 8, "B": 3}
    assert {s: sum(r["mw"] for r in moves if r["receiver"] == s) for s in ("C", "D")} == {
        "C": 7, "D": 4}
    with pytest.raises(ValueError):
        allocate_station_transfers({"A": 5}, {"A": 5})


def test_seed_expansion_preserves_assets_across_block_offsets():
    from rebuild_2026.joint_shared_measure import expand_capacity_seed
    blocks = {
        "pizhou": {"offset": 0, "count": 3, "capacity_variables": {2022: 2},
                    "capacity_seed_terms": {2022: {0: 63}}},
        "city": {"offset": 3, "count": 3, "capacity_variables": {2022: 5},
                  "capacity_seed_terms": {2022: {3: 100}}}}
    result = expand_capacity_seed([1, 7, 1, 9], blocks, 6)
    assert result.tolist() == [1, 7, 63, 1, 9, 100]
    with pytest.raises(ValueError):
        expand_capacity_seed([1, 7, 1], blocks, 6)


@pytest.fixture(autouse=True)
def deterministic_solver(monkeypatch):
    monkeypatch.setenv("XUZHOU_MILP_BACKEND", "highspy")
    monkeypatch.setenv("XUZHOU_MILP_THREADS", "1")


def test_fixed_new_unit_increases_mw_equally_at_different_station_bases():
    small = capacity_from_station_rate(60, .3, 1, 7.49106117, .5)
    large = capacity_from_station_rate(90, .3, 1, 7.49106117, .5)
    assert small["credited_new_capacity_mw"] == pytest.approx(7.49106117)
    assert large["credited_new_capacity_mw"] == pytest.approx(7.49106117)
    assert small["capacity_fraction"] > large["capacity_fraction"]


def test_policy_ceiling_limits_credited_increment():
    result = capacity_from_station_rate(60, .3, 2, 7.49106117, .5)
    assert result["capacity_mw"] == pytest.approx(30)
    assert result["credited_new_capacity_mw"] == pytest.approx(12)


def test_optimizer_builds_to_fill_target_and_keeps_unit_capacity_fixed(monkeypatch):
    import rebuild_2026.regional_static_milp_v2 as regional
    a, b = ("QX-00005", 110, "A"), ("QX-00005", 110, "B")
    baseline = {
        s: {"simulation_unit_1_mva": 40, "simulation_unit_2_mva": 40,
            "simulation_capacity_mva_2021": 80,
            "estimated_forward_peak_mw_2021": load}
        for s, load in ((a, 60), (b, 20))}
    scenes = {
        (s, y): {"estimated_station_forward_peak_mw": load + (4 * (y - 2022) if s == a else 0),
                 "reverse_screen_mw": 10}
        for s, load in ((a, 60), (b, 20)) for y in (2022, 2023, 2024, 2025)}
    duration = {
        s: {"forward_d95_max_run_hours": 2, "reverse_d95_max_run_hours": 2}
        for s in baseline}
    peaks = {("QX-00005", 110, y): 80 + 4 * max(0, y - 2022)
             for y in range(2021, 2026)}
    monkeypatch.setattr(regional, "input_data", lambda *args: (
        baseline, scenes, duration, peaks, [40.0], 1))
    monkeypatch.setattr(regional, "station_metadata", lambda *args: {
        s[2]: {"area_class": "A", "available_third_slots": 0,
               "available_third_mva": 0, "spare_10kv_bays": 1}
        for s in baseline})
    result = regional.optimize(
        "rigid", allow_third_transformer=False, max_new_lines=1,
        existing_transfer_fraction=.1, target_transfer_fraction=.2,
        min_clr=0, require_transformer_n1=True,
        storage_max_mwh_per_station=None, transfer_mode="load_reallocation",
        transfer_capacity_model="station_rate_equivalent",
        minimize_transfer_tiebreak=True)
    summary, years, stations, transfers, lines, outages = result
    assert summary["installed_transfer_target_enforced"]
    assert not summary["existing_county_budget_enforced"]
    assert summary["max_transfer_fraction"] is None
    assert summary["candidate_pairs"] == 0
    assert summary["station_transfer_representation"] == "station_out_in_balance_no_pair_decisions"
    assert len(lines) == 1
    assert lines[0]["commissioning_year"] == 2022
    assert lines[0]["screen_capacity_mw_2025"] == pytest.approx(7.49106117)
    assert not outages
    assert all(int(y["new_lines_in_service"]) == 1 for y in years)
    for row in stations:
        assert row["effective_transfer_fraction"] >= .2 - 1e-7
        assert row["credited_new_transfer_capacity_mw"] == pytest.approx(7.49106117)
        assert row["normal_load_transferred_out_mw"] <= row["effective_transfer_capacity_mw"] + 1e-7
    for year in (2022, 2023, 2024, 2025):
        new_flow = sum(r["mw"] for r in transfers if r["year"] == year and r["kind"] == "rate_increment")
        assert new_flow <= 7.49106117 + 1e-7
        local = [r for r in stations if r["year"] == year]
        assert sum(r["post_transfer_forward_mw"] for r in local) == pytest.approx(
            sum(r["forward_mw"] for r in local))
