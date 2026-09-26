from collections import Counter

from rebuild_2026.model_station_inputs import build_model_station_inputs


def test_two_region_station_inputs_preserve_capacity_provenance():
    rows = build_model_station_inputs()
    assert len(rows) == 57
    assert Counter((row["study_region_id"], row["voltage_kv"]) for row in rows) == {
        ("QX-00005", 110): 20,
        ("QX-00005", 35): 8,
        ("QX-00007", 110): 29,
    }
    virtual = [row for row in rows if row["capacity_basis"] == "simulation_capacity_to_select"]
    assert {row["model_station_id"] for row in virtual} == {"SIM-CITY-KL", "SIM-CITY-XSZ", "SIM-CITY-YQ"}
    assert all(row["source_capacity_mva_2025"] == "" and row["source_station_id"] == "" for row in virtual)
    external = {row["source_station_id"]: row for row in rows if row["capacity_basis"] == "source_equipment_other_region_user_confirmed_city"}
    assert {station: (row["source_asset_region_id"], row["source_capacity_mva_2025"]) for station, row in external.items()} == {
        "BDZ-00055": ("QX-00009", 81.5),
        "BDZ-00183": ("QX-00003", 100.0),
    }
    assert sum(float(row["source_capacity_mva_2025"]) for row in rows if row["study_region_id"] == "QX-00005" and row["voltage_kv"] == 110) == 2139.5
    assert sum(float(row["source_capacity_mva_2025"]) for row in rows if row["study_region_id"] == "QX-00005" and row["voltage_kv"] == 35) == 275
    assert sum(float(row["source_capacity_mva_2025"]) for row in rows if row["study_region_id"] == "QX-00007" and row["source_capacity_mva_2025"] != "") == 3263.5
