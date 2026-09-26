from collections import defaultdict

from rebuild_2026.transformer_only_path_2021_2025 import build_transformer_only_path


def test_transformer_only_path_is_monotone_and_screened_year_by_year():
    stations, layers = build_transformer_only_path()
    assert len(stations) == 57 * 5 * 2
    assert len(layers) == 3 * 5 * 2
    grouped = defaultdict(list)
    for row in stations:
        key = row["study_region_id"], row["voltage_kv"], row["model_station_id"], row["reverse_variant"]
        grouped[key].append(row)
        capacity = row["selected_capacity_mva"]
        assert row["estimated_station_forward_peak_mw"] <= 0.95 * capacity + 1e-6
        assert row["reverse_screen_mw"] <= 0.8 * 0.95 * capacity + 1e-6
    assert len(grouped) == 57 * 2
    for rows in grouped.values():
        rows.sort(key=lambda row: row["year"])
        assert [row["year"] for row in rows] == [2021, 2022, 2023, 2024, 2025]
        assert all(right["selected_capacity_mva"] >= left["selected_capacity_mva"] for left, right in zip(rows, rows[1:]))
        assert all(
            all(new >= old for old, new in zip(
                sorted((left["selected_unit_1_mva"], left["selected_unit_2_mva"])),
                sorted((right["selected_unit_1_mva"], right["selected_unit_2_mva"])),
            ))
            for left, right in zip(rows, rows[1:])
        )
    by_key = {(row["study_region_id"], row["voltage_kv"], row["year"], row["reverse_variant"]): row for row in layers}
    assert all(row["ratio_status"] == "within_cap" for row in layers)
    assert {(row["study_region_id"], row["voltage_kv"]): row["transformer_only_capacity_mva"] for row in layers if row["year"] == 2025 and row["reverse_variant"] == "night_central"} == {
        ("QX-00005", 35): 234.0,
        ("QX-00005", 110): 1536.5,
        ("QX-00007", 110): 2475.0,
    }
    assert by_key[("QX-00005", 35, 2023, "night_central")]["transformer_only_clr"] > 1.9
    for row in layers:
        comparison = by_key[row["study_region_id"], row["voltage_kv"], row["year"], "early_pv_high"]
        if row["reverse_variant"] == "night_central":
            assert comparison["transformer_only_capacity_mva"] == row["transformer_only_capacity_mva"]
