from math import isclose

from rebuild_2026.baseline_2021 import local_unit_catalog, read_csv
from rebuild_2026.hourly_source_profile import OUTPUT_DIR
from rebuild_2026.transformer_only_screen_2025 import build_transformer_only_screen


def test_2025_transformer_only_screen_respects_both_station_screens_and_layer_cap():
    stations, layers = build_transformer_only_screen()
    assert len(stations) == 57
    catalogs = local_unit_catalog()
    for row in stations:
        key = row["study_region_id"], row["voltage_kv"]
        assert row["selected_unit_1_mva"] in catalogs[key]
        assert row["selected_unit_2_mva"] in catalogs[key]
        assert row["transformer_only_screen_capacity_mva"] >= row["baseline_capacity_mva_2021"]
        assert row["observed_station_forward_peak_mw_2025"] <= row["power_factor_assumption"] * row["transformer_only_screen_capacity_mva"] + 1e-9
        assert row["observed_station_reverse_peak_mw_2025"] <= row["power_factor_assumption"] * row["screening_beta_upper"] * row["transformer_only_screen_capacity_mva"] + 1e-9
        assert row["technical_status"] == "transformer_only_aggregate_screen_not_guide_feasibility"
    by_layer = {(row["study_region_id"], row["voltage_kv"]): row for row in layers}
    assert {key: row["transformer_only_screen_capacity_mva"] for key, row in by_layer.items()} == {
        ("QX-00005", 35): 232.0,
        ("QX-00005", 110): 1536.5,
        ("QX-00007", 110): 2469.0,
    }
    # 邳州使用甲方年度降压负荷；市区仍是29站同边界样本。
    official = {int(r["voltage_kv"]): float(r["reported_downward_load_mw"])
                for r in read_csv(OUTPUT_DIR / "official_annual.csv")
                if r["region_id"] == "QX-00005" and int(r["year"]) == 2025}
    for voltage in (35, 110):
        assert by_layer[("QX-00005", voltage)]["observed_synchronous_forward_peak_mw_2025"] == official[voltage]
    assert by_layer[("QX-00007", 110)]["observed_synchronous_forward_peak_mw_2025"] == 1307.315366
    for key, layer in by_layer.items():
        assert isclose(
            layer["transformer_only_screen_capacity_mva"],
            sum(row["transformer_only_screen_capacity_mva"] for row in stations if (row["study_region_id"], row["voltage_kv"]) == key),
        )
        assert layer["transformer_only_clr"] <= layer["clr_cap"]
        assert layer["ratio_screen_status"] == "within_cap"
