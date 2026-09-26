"""把甲方 2021 区域实有容量分配到仿真站，不伪称逐站历史台账。"""

from collections import defaultdict
from itertools import combinations_with_replacement
from pathlib import Path

from .baseline_2021 import local_unit_catalog, read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR


def build() -> tuple[list[dict], list[dict]]:
    original = read_csv(OUTPUT_DIR / "planning_2021_common_baseline_stations.csv")
    source = {(r["study_region_id"], int(r["voltage_kv"]), r["model_station_id"]): r
              for r in read_csv(OUTPUT_DIR / "model_station_inputs_2025.csv")}
    official = {(r["region_id"], int(r["voltage_kv"]), int(r["year"])): r
                for r in read_csv(OUTPUT_DIR / "official_annual.csv")}
    catalogs = local_unit_catalog()
    grouped = defaultdict(list)
    for row in original:
        grouped[row["study_region_id"], int(row["voltage_kv"])].append(row)
    stations, layers = [], []
    for layer, rows in sorted(grouped.items()):
        weights = {}
        for row in rows:
            key = (*layer, row["model_station_id"])
            reported = source[key]["source_capacity_mva_2025"]
            weights[key] = (float(reported) if reported else
                            float(row["simulation_capacity_mva_2021"]))
        if layer[0] == "QX-00005":
            target = float(official[(*layer, 2021)]["capacity_mva"])
        else:
            target = (sum(weights.values()) *
                      float(official[(*layer, 2021)]["capacity_mva"]) /
                      float(official[(*layer, 2025)]["capacity_mva"]))
        weight_total = sum(weights.values())
        options = {}
        ideals = {}
        for row in rows:
            key = (*layer, row["model_station_id"])
            ideal = target * weights[key] / weight_total
            ideals[key] = ideal
            minimum = float(row["estimated_forward_peak_mw_2021"]) / 0.95
            pairs = [p for p in combinations_with_replacement(catalogs[layer], 2)
                     if sum(p) + 1e-8 >= minimum]
            if not pairs:
                raise ValueError(f"{key}: 本地规格无法覆盖基期站峰")
            options[key] = pairs
        selected = {key: min(pairs, key=lambda p: (abs(sum(p) - ideals[key]), sum(p)))
                    for key, pairs in options.items()}
        current_total = sum(map(sum, selected.values()))
        # 分配只需逼近区域台账总量；单站规格离散时保留不足 1 MVA 的差额。
        for _ in range(1000):
            best = None
            for key, pairs in options.items():
                old = selected[key]
                for pair in pairs:
                    if pair == old:
                        continue
                    new_total = current_total + sum(pair) - sum(old)
                    gain = 1000 * (abs(current_total - target) - abs(new_total - target))
                    gain += abs(sum(old) - ideals[key]) - abs(sum(pair) - ideals[key])
                    if best is None or gain > best[0]:
                        best = (gain, key, pair, new_total)
            if best is None or best[0] <= 1e-9:
                break
            _, key, pair, current_total = best
            selected[key] = pair
        total = 0.0
        for row in rows:
            key = (*layer, row["model_station_id"])
            pair = selected[key]
            result = dict(row)
            result.update({"simulation_unit_1_mva": pair[0],
                           "simulation_unit_2_mva": pair[1],
                           "simulation_capacity_mva_2021": sum(pair),
                           "capacity_kind": "reported_2021_region_total_allocated_to_stations_by_2025_shares"})
            stations.append(result)
            total += sum(pair)
        peak = sum(float(r["estimated_forward_peak_mw_2021"]) for r in rows)
        layers.append({"study_region_id": layer[0], "voltage_kv": layer[1],
                       "year": 2021, "target_capacity_mva": round(target, 6),
                       "proxy_capacity_mva": total,
                       "allocation_gap_mva": round(total - target, 6),
                       "estimated_station_peak_sum_mw": round(peak, 6),
                       "reported_or_sample_scaled_2021_peak_mw":
                           float(official[(*layer, 2021)]["reported_downward_load_mw"])
                           if layer[0] == "QX-00005" else "29_station_sample_proxy",
                       "capacity_kind": "regional_reported_total_or_city_sample_scaled_proxy"})
    return stations, layers


if __name__ == "__main__":
    station_rows, layer_rows = build()
    output = OUTPUT_DIR / "capacity_release_simulation/historical_baseline_v4"
    write_csv(station_rows, Path(output) / "station_proxy.csv")
    write_csv(layer_rows, Path(output) / "layer_check.csv")
    for row in layer_rows:
        print(row)
