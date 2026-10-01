import pytest

from rebuild_2026.annual_no_tie_investment_submodel import LinearModel
from rebuild_2026.load_reallocation import add_post_transfer_n1


@pytest.fixture(autouse=True)
def deterministic_solver(monkeypatch):
    monkeypatch.setenv("XUZHOU_MILP_BACKEND", "highspy")
    monkeypatch.setenv("XUZHOU_MILP_THREADS", "1")


@pytest.mark.parametrize("load,shift,service", [
    (60, 10, 100 / 3), (38, 4, 22), (14, 5, 0), (30, -15, 30), (40, 4, 24),
])
def test_bc_service_uses_reallocated_load_on_both_sides_of_36mw(load, shift, service):
    model = LinearModel()
    moved = model.variable(0, upper=abs(shift), integer=0)
    model.lower_bounds[moved] = abs(shift)
    supply = model.variable(1, upper=100, integer=0)
    add_post_transfer_n1(model, [({supply: 1}, 0)], load,
                         {moved: 1 if shift > 0 else -1}, False, 100)
    solution, _ = model.solve()
    assert solution[supply] == pytest.approx(service, abs=1e-7)


def test_load_reallocation_relies_on_receiver_capacity_and_preserves_total_load():
    model = LinearModel()
    transfer = model.variable(1, upper=20, integer=0)
    storage = model.variable(10, upper=100, integer=0)
    donor_supply = model.variable(0, upper=50, integer=0)
    receiver_supply = model.variable(0, upper=35, integer=0)
    model.lower_bounds[donor_supply] = 50
    model.lower_bounds[receiver_supply] = 35
    add_post_transfer_n1(model, [({donor_supply: 1, storage: 1}, 0)], 60,
                         {transfer: 1}, True, 80)
    add_post_transfer_n1(model, [({receiver_supply: 1}, 0)], 20,
                         {transfer: -1}, True, 80)
    solution, _ = model.solve()
    assert solution[transfer] == pytest.approx(10)
    assert solution[storage] == pytest.approx(0)
    assert 60 - solution[transfer] + 20 + solution[transfer] == pytest.approx(80)
    # 禁止正常转接后，原设备布局需要储能补足供电任务。
    model.upper_bounds[transfer] = 0
    solution, _ = model.solve()
    assert solution[storage] == pytest.approx(10)


def test_receiver_cannot_accept_more_load_than_its_capacity():
    model = LinearModel()
    transfer = model.variable(1, upper=20, integer=0)
    storage = model.variable(10, upper=100, integer=0)
    donor_supply = model.variable(0, upper=50, integer=0)
    receiver_supply = model.variable(0, upper=23, integer=0)
    model.lower_bounds[donor_supply] = 50
    model.lower_bounds[receiver_supply] = 23
    add_post_transfer_n1(model, [({donor_supply: 1, storage: 1}, 0)], 60,
                         {transfer: 1}, True, 80)
    add_post_transfer_n1(model, [({receiver_supply: 1}, 0)], 20,
                         {transfer: -1}, True, 80)
    solution, _ = model.solve()
    assert solution[transfer] == pytest.approx(3)
    assert solution[storage] == pytest.approx(7)


def test_regional_optimizer_returns_normal_transfer_and_prices_storage_after_reallocation(monkeypatch):
    import rebuild_2026.regional_static_milp_v2 as regional
    a, b = ("QX-00005", 110, "A"), ("QX-00005", 110, "B")
    baseline = {s: {"simulation_unit_1_mva": 40, "simulation_unit_2_mva": 40,
                    "simulation_capacity_mva_2021": 80, "estimated_forward_peak_mw_2021": load}
                for s, load in ((a, 60), (b, 20))}
    scenes = {(s, y): {"estimated_station_forward_peak_mw": load, "reverse_screen_mw": 10}
              for s, load in ((a, 60), (b, 20)) for y in (2022, 2023, 2024, 2025)}
    duration = {s: {"forward_d95_max_run_hours": 2, "reverse_d95_max_run_hours": 2}
                for s in baseline}
    peaks = {("QX-00005", 110, y): 80 for y in range(2021, 2026)}
    monkeypatch.setattr(regional, "input_data", lambda *args: (
        baseline, scenes, duration, peaks, [40.0], 1))
    monkeypatch.setattr(regional, "station_metadata", lambda *args: {
        s[2]: {"area_class": "A", "available_third_slots": 0, "available_third_mva": 0,
               "spare_10kv_bays": 1} for s in baseline})
    result = regional.optimize(
        "rigid", use_new_lines=False, allow_third_transformer=False,
        existing_transfer_fraction=.2, max_transfer_fraction=.1,
        min_clr=0, require_transformer_n1=True, storage_max_mwh_per_station=None,
        transfer_mode="load_reallocation", minimize_transfer_tiebreak=True)
    summary, _, stations, transfers, lines, outages = result
    assert summary["n1_demand_basis"].startswith("post_normal_transfer")
    assert not lines and not outages
    assert len(transfers) == 4
    for row in stations:
        if row["station"] == "A":
            assert row["normal_load_transferred_out_mw"] == pytest.approx(6)
            assert row["post_transfer_forward_mw"] == pytest.approx(54)
            assert row["storage_power_mw"] == pytest.approx(16)
            assert row["post_transfer_reverse_upper_mw"] == pytest.approx(16)
        else:
            assert row["post_transfer_forward_mw"] == pytest.approx(26)
            assert row["storage_power_mw"] == pytest.approx(0)
