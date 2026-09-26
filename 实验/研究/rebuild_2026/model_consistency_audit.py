"""独立读取重构输出，核对站集、场景、设备路径与成本的内部一致性。"""

import argparse
from collections import Counter, defaultdict
from math import isclose
from pathlib import Path

from .baseline_2021 import read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR


EXPECTED_LAYERS = {("QX-00005", 35): 8, ("QX-00005", 110): 20, ("QX-00007", 110): 29}
YEARS = range(2021, 2026)
VARIANTS = ("night_central", "early_pv_high")
CASES = (
    "hold_2021_simulation_capacity",
    "hold_2024_transformer_path_capacity",
    "transformer_only_2025_capacity",
)


def station_key(row: dict) -> tuple[str, int, str]:
    return row["study_region_id"], int(row["voltage_kv"]), row["model_station_id"]


def close(a: float, b: float, tol: float = 1e-4) -> bool:
    return isclose(float(a), float(b), rel_tol=0, abs_tol=tol)


def build_checks(output_dir: Path = OUTPUT_DIR, overrides: dict[str, Path] | None = None) -> list[dict]:
    overrides = overrides or {}

    def rows(name: str) -> list[dict]:
        return read_csv(overrides.get(name, output_dir / name))

    checks = []

    def check(check_id: str, scope: str, passed: bool, observed, expected, note: str = "") -> None:
        checks.append({
            "check_id": check_id,
            "scope": scope,
            "status": "pass" if passed else "fail",
            "observed": str(observed),
            "expected": str(expected),
            "note": note,
        })

    inputs = rows("model_station_inputs_2025.csv")
    expected_stations = {station_key(row) for row in inputs}
    layer_counts = Counter(key[:2] for key in expected_stations)
    check("study_scope", "2025_inputs", layer_counts == EXPECTED_LAYERS and len(inputs) == len(expected_stations), layer_counts, EXPECTED_LAYERS)

    baseline_rows = rows("baseline_2021_station_candidates.csv")
    baseline = {station_key(row): row for row in baseline_rows}
    check("baseline_station_set", "2021", len(baseline) == len(baseline_rows) and set(baseline) == expected_stations, len(baseline), len(expected_stations))
    for layer, expected_count in EXPECTED_LAYERS.items():
        selected = [row for key, row in baseline.items() if key[:2] == layer]
        valid = all(
            close(float(row["simulation_unit_1_mva"]) + float(row["simulation_unit_2_mva"]), float(row["simulation_capacity_mva_2021"]))
            and float(row["estimated_forward_peak_mw_2021"]) <= 0.95 * float(row["simulation_capacity_mva_2021"]) + 1e-5
            for row in selected
        )
        check("baseline_station_capacity", f"{layer}", len(selected) == expected_count and valid, len(selected), expected_count,
              "双主变和、2021 正向峰值初筛；不是完整技术可行性")

    baseline_layers = {(row["study_region_id"], int(row["voltage_kv"])): row for row in rows("baseline_2021_layer_check.csv")}
    for layer in EXPECTED_LAYERS:
        row = baseline_layers[layer]
        capacity = sum(float(item["simulation_capacity_mva_2021"]) for key, item in baseline.items() if key[:2] == layer)
        peak = float(row["estimated_district_peak_mw_2021"])
        valid = close(capacity, float(row["simulation_capacity_mva_2021"])) and close(capacity / peak, float(row["baseline_clr"]), 1e-6) and capacity / peak <= 2 + 1e-9
        check("baseline_layer_ratio", f"{layer}", valid, round(capacity / peak, 9), row["baseline_clr"], "同片区同电压容量/同步正向峰值")

    forward_stations = defaultdict(list)
    for row in rows("annual_forward_station_scenes_2021_2025.csv"):
        forward_stations[row["study_region_id"], int(row["voltage_kv"]), int(row["year"])].append(row)
    forward_layers = {
        (row["study_region_id"], int(row["voltage_kv"]), int(row["year"])): row
        for row in rows("annual_forward_layer_scenes_2021_2025.csv")
    }
    check("forward_layer_rows", "2021_2025", len(forward_layers) == 15, len(forward_layers), 15)
    for layer in EXPECTED_LAYERS:
        for year in YEARS:
            key = layer + (year,)
            station_rows = forward_stations[key]
            same_stations = (
                len(station_rows) == EXPECTED_LAYERS[layer]
                and {station_key(row) for row in station_rows} == {station for station in expected_stations if station[:2] == layer}
            )
            total = sum(float(row["estimated_station_net_load_mw"]) for row in station_rows)
            reported = float(forward_layers[key]["estimated_synchronous_forward_peak_mw"])
            check("synchronous_forward_sum", f"{key}", same_stations and close(total, reported), round(total, 6), reported,
                  "同一模板时刻逐站净负荷求和，不是各站独立峰值相加")

    reverse_rows = rows("annual_reverse_station_proxy_2021_2025.csv")
    reverse = {(station_key(row), int(row["year"]), row["variant"]): row for row in reverse_rows}
    check("reverse_proxy_rows", "2021_2025", len(reverse) == len(reverse_rows) == 1140, len(reverse), 1140)
    for layer in EXPECTED_LAYERS:
        layer_stations = {station for station in expected_stations if station[:2] == layer}
        for year in YEARS:
            for variant in ("night_low", "night_central", "night_high", "early_pv_high"):
                keys = {station for station, row_year, row_variant in reverse if station[:2] == layer and row_year == year and row_variant == variant}
                check("reverse_proxy_station_set", f"{layer + (year, variant)}", keys == layer_stations,
                      len(keys), len(layer_stations), "历史反向值是代理，不是当年实测")

    path_rows = rows("transformer_only_path_station_2021_2025.csv")
    path = {(station_key(row), int(row["year"]), row["reverse_variant"]): row for row in path_rows}
    path_layers = {
        (row["study_region_id"], int(row["voltage_kv"]), int(row["year"]), row["reverse_variant"]): row
        for row in rows("transformer_only_path_layer_2021_2025.csv")
    }
    check("transformer_path_rows", "2021_2025", len(path) == len(path_rows) == 570 and len(path_layers) == 30,
          (len(path), len(path_layers)), (570, 30))
    for layer in EXPECTED_LAYERS:
        layer_stations = {station for station in expected_stations if station[:2] == layer}
        for year in YEARS:
            for variant in VARIANTS:
                key = layer + (year, variant)
                selected = {station: path[station, year, variant] for station in layer_stations}
                pair_valid = True
                screen_valid = True
                for station, row in selected.items():
                    before = (float(row["prior_unit_1_mva"]), float(row["prior_unit_2_mva"]))
                    after = (float(row["selected_unit_1_mva"]), float(row["selected_unit_2_mva"]))
                    prior = (
                        (float(baseline[station]["simulation_unit_1_mva"]), float(baseline[station]["simulation_unit_2_mva"]))
                        if year == 2021 else
                        (float(path[station, year - 1, variant]["selected_unit_1_mva"]), float(path[station, year - 1, variant]["selected_unit_2_mva"]))
                    )
                    capacity = float(row["selected_capacity_mva"])
                    pair_valid &= before == prior and all(new >= old for old, new in zip(before, after)) and close(sum(after), capacity)
                    screen_valid &= (
                        float(row["estimated_station_forward_peak_mw"]) <= 0.95 * capacity + 1e-5
                        and float(row["reverse_screen_mw"]) <= 0.8 * 0.95 * capacity + 1e-5
                    )
                    proxy_reverse = float(reverse[station, year, variant]["reverse_at_template_proxy_mw"])
                    screen_valid &= (
                        close(float(row["reverse_screen_mw"]), proxy_reverse, 1e-5)
                        if year < 2025 else float(row["reverse_screen_mw"]) + 1e-5 >= proxy_reverse
                    )
                capacity = sum(float(row["selected_capacity_mva"]) for row in selected.values())
                layer_row = path_layers[key]
                peak = float(forward_layers[layer + (year,)]["estimated_synchronous_forward_peak_mw"])
                layer_valid = (
                    close(capacity, float(layer_row["transformer_only_capacity_mva"]))
                    and close(peak, float(layer_row["estimated_synchronous_forward_peak_mw"]))
                    and close(capacity / peak, float(layer_row["transformer_only_clr"]), 1e-6)
                    and capacity / peak <= 2 + 1e-9
                )
                check("transformer_path_screen", f"{key}", pair_valid and screen_valid and layer_valid,
                      (pair_valid, screen_valid, round(capacity / peak, 6)), "逐台不降档、站级峰值屏查、片区R≤2",
                      "站级反向 β=0.8 聚合式仅是风险屏查，不是导则认证")

    events = defaultdict(list)
    for row in rows("transformer_only_incremental_events_2022_2025.csv"):
        events[row["study_region_id"], int(row["voltage_kv"]), int(row["year"]), row["reverse_variant"]].append(row)
    capex = {
        (row["study_region_id"], int(row["voltage_kv"]), int(row["year"]), row["reverse_variant"]): row
        for row in rows("transformer_only_capex_layer_2022_2025.csv")
    }
    for layer in EXPECTED_LAYERS:
        for year in range(2022, 2026):
            for variant in VARIANTS:
                key = layer + (year, variant)
                selected = events[key]
                report = capex[key]
                investment = sum(float(row["investment_10k_cny"]) for row in selected)
                purchased = sum(float(row["purchased_unit_mva"]) for row in selected)
                valid = (
                    len(selected) == int(report["upgraded_transformer_count"])
                    and close(investment, float(report["base_capex_10k_cny"]), 1e-3)
                    and close(purchased, float(report["purchased_transformer_mva"]))
                    and all(close(float(row["investment_10k_cny"]), float(row["purchased_unit_mva"]) * float(row["cost_coefficient_10k_cny_per_purchased_mva"]), 1e-5) for row in selected)
                )
                check("transformer_cost_reconciliation", f"{key}", valid, round(investment, 6), report["base_capex_10k_cny"],
                      "仅本地替换工程折算的购置投资，不是全寿命成本")

    storage_rows = rows("static_storage_need_screen_2025.csv")
    storage = {(station_key(row), row["capacity_case"]): row for row in storage_rows}
    check("storage_screen_rows", "2025", len(storage) == len(storage_rows) == 171, len(storage), 171)
    for case in CASES:
        selected = {station: storage[station, case] for station in expected_stations}
        valid = True
        for station, row in selected.items():
            source_capacity = (
                float(baseline[station]["simulation_capacity_mva_2021"])
                if case == CASES[0] else
                float(path[station, 2024 if case == CASES[1] else 2025, "night_central"]["selected_capacity_mva"])
            )
            valid &= (
                close(float(row["station_capacity_mva"]), source_capacity)
                and int(row["forward_h95_hours"]) >= int(row["forward_d95_max_run_hours"])
                and int(row["reverse_h95_hours"]) >= int(row["reverse_d95_max_run_hours"])
                and int(row["required_modules_scenario_proxy"]) == max(
                    int(row["forward_modules_by_power"]), int(row["forward_modules_by_nominal_energy"]),
                    int(row["reverse_modules_by_power"]), int(row["reverse_modules_by_nominal_energy"])
                )
            )
        check("storage_proxy_consistency", case, valid, len(selected), 57,
              "H95 总小时与 D95 连续时段分列；柜数是静态代理，不是 SOC/站址证明")

    marginal = {(row["study_region_id"], int(row["voltage_kv"])): row for row in rows("marginal_measure_comparison_2025.csv")}
    for layer in EXPECTED_LAYERS:
        selected = [storage[station, CASES[1]] for station in expected_stations if station[:2] == layer]
        reported = marginal[layer]
        storage_cost = sum(float(row["replicated_package_capex_10k_cny"]) for row in selected)
        transformer_cost = float(capex[layer + (2025, "night_central")]["base_capex_10k_cny"])
        valid = (
            close(storage_cost, float(reported["storage_only_simulated_capex_10k_cny"]), 1e-3)
            and close(transformer_cost, float(reported["transformer_only_simulated_capex_10k_cny"]), 1e-3)
            and close(storage_cost - transformer_cost, float(reported["storage_minus_transformer_capex_10k_cny"]), 1e-3)
        )
        check("marginal_cost_reconciliation", f"{layer}", valid, round(storage_cost - transformer_cost, 6),
              reported["storage_minus_transformer_capex_10k_cny"], "仅同起点 2025 年单措施投资对照，非最优成本")

    submodel_stations = rows("submodel_2025_no_tie_stations.csv")
    submodel_layers = {(row["study_region_id"], int(row["voltage_kv"])): row for row in rows("submodel_2025_no_tie_layers.csv")}
    check("submodel_2025_station_set", "2025_no_tie", len(submodel_stations) == 57 and
          {station_key(row) for row in submodel_stations} == expected_stations and len(submodel_layers) == 3,
          (len(submodel_stations), len(submodel_layers)), (57, 3), "受限 2025 年投资子模型，不是正式刚性解")
    for layer in EXPECTED_LAYERS:
        selected = [row for row in submodel_stations if station_key(row)[:2] == layer]
        report = submodel_layers[layer]
        capacity = sum(float(row["capacity_mva"]) for row in selected)
        cost = sum(float(row["investment_10k_cny"]) for row in selected)
        peak = float(report["synchronous_forward_peak_mw"])
        valid = (
            close(capacity, float(report["selected_capacity_mva"]))
            and close(cost, float(report["selected_2025_investment_10k_cny"]), 1e-3)
            and close(capacity / peak, float(report["actual_clr"]), 1e-6)
            and capacity / peak <= 2 + 1e-9
            and cost <= float(report["transformer_only_2025_investment_10k_cny"]) + 1e-3
            and all(0 <= int(row["storage_modules"]) <= 10 for row in selected)
        )
        check("submodel_2025_layer_reconciliation", f"{layer}", valid, (round(capacity / peak, 6), round(cost, 3)),
              ("R≤2", "不高于仅主变候选投资"), "仅可验证受限静态子模型，未纳入既有联络或全寿命成本")
    return checks


def main() -> None:
    parser = argparse.ArgumentParser(description="核对重构模型输入、场景、主变路径及成本的内部一致性")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    checks = build_checks(args.output_dir)
    write_csv(checks, args.output_dir / "model_consistency_checks.csv")
    failed = [row for row in checks if row["status"] == "fail"]
    print(f"一致性核查：{len(checks) - len(failed)}/{len(checks)} 通过；结果只证明内部对账，不证明导则技术可行。")
    for row in failed:
        print(f"失败：{row['check_id']} {row['scope']}，实测 {row['observed']}，应为 {row['expected']}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
