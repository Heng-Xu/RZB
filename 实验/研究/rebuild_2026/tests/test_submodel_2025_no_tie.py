import pytest

from rebuild_2026.submodel_2025_no_tie import (
    build_2025_no_tie_submodel,
    solve_layer_candidates,
)


def test_integer_solver_obeys_layer_capacity_and_finds_small_exact_optimum():
    candidates = {
        "A": [
            {"model_station_id": "A", "capacity_mva": 2, "investment_10k_cny": 0},
            {"model_station_id": "A", "capacity_mva": 1, "investment_10k_cny": 3},
        ],
        "B": [
            {"model_station_id": "B", "capacity_mva": 2, "investment_10k_cny": 0},
            {"model_station_id": "B", "capacity_mva": 1, "investment_10k_cny": 4},
        ],
    }
    chosen, objective = solve_layer_candidates(candidates, 3)
    assert len(chosen) == 2
    assert sum(row["capacity_mva"] for row in chosen) == 3
    assert objective == pytest.approx(3)


def test_2025_restricted_submodel_reconciles_stations_and_beats_its_transformer_only_witness():
    stations, layers = build_2025_no_tie_submodel()
    assert len(stations) == 57
    assert len(layers) == 3
    assert len({(row["study_region_id"], row["voltage_kv"], row["model_station_id"]) for row in stations}) == 57
    assert all(0 <= row["storage_modules"] <= 10 for row in stations)
    for layer in layers:
        subset = [row for row in stations if (row["study_region_id"], row["voltage_kv"]) == (layer["study_region_id"], layer["voltage_kv"])]
        assert sum(row["capacity_mva"] for row in subset) == pytest.approx(layer["selected_capacity_mva"])
        assert sum(row["investment_10k_cny"] for row in subset) == pytest.approx(layer["selected_2025_investment_10k_cny"], abs=1e-3)
        assert layer["actual_clr"] <= 2
        assert layer["selected_2025_investment_10k_cny"] <= layer["transformer_only_2025_investment_10k_cny"] + 1e-5
        assert "no_lifecycle" in layer["cost_scope"]
    by_layer = {(row["study_region_id"], row["voltage_kv"]): row for row in layers}
    assert by_layer["QX-00005", 35]["selected_storage_modules"] == 10
    assert by_layer["QX-00005", 110]["selected_storage_modules"] == 0
    assert by_layer["QX-00007", 110]["selected_2025_investment_10k_cny"] == 0
