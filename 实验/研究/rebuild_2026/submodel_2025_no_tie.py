"""2025 年无联络静态子模型：验证离散主变＋至多 10 柜储能的成本寻优内核。"""

import argparse
from itertools import combinations_with_replacement
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix

from .baseline_2021 import local_unit_catalog, read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR
from .incremental_cost import replacement_cost_coefficients, storage_capex_10k_cny
from .static_storage_screen_2025 import module_count_for_peak


STORAGE_SCREEN = OUTPUT_DIR / "static_storage_need_screen_2025.csv"
TRANSFORMER_PATH = OUTPUT_DIR / "transformer_only_path_station_2021_2025.csv"
FORWARD_LAYERS = OUTPUT_DIR / "annual_forward_layer_scenes_2021_2025.csv"
TRANSFORMER_CAPEX = OUTPUT_DIR / "transformer_only_capex_layer_2022_2025.csv"
MAX_ANCHORED_STORAGE_MODULES = 10
RIGID_CLR_CAP = 2.0


def solve_layer_candidates(candidates_by_station: dict[str, list[dict]], capacity_ceiling_mva: float) -> tuple[list[dict], float]:
    """每站恰选一项、总容量不超上限，精确比较候选投资。"""
    station_ids = sorted(candidates_by_station)
    candidates = [candidate for station_id in station_ids for candidate in candidates_by_station[station_id]]
    matrix = lil_matrix((len(station_ids) + 1, len(candidates)), dtype=float)
    column = 0
    for row, station_id in enumerate(station_ids):
        for _ in candidates_by_station[station_id]:
            matrix[row, column] = 1
            matrix[-1, column] = candidates[column]["capacity_mva"]
            column += 1
    lower = np.array([1.0] * len(station_ids) + [0.0])
    upper = np.array([1.0] * len(station_ids) + [capacity_ceiling_mva])
    result = milp(
        c=np.array([item["investment_10k_cny"] for item in candidates]),
        integrality=np.ones(len(candidates)),
        bounds=Bounds(0, 1),
        constraints=LinearConstraint(matrix.tocsr(), lower, upper),
        options={"mip_rel_gap": 1e-8},
    )
    if result.status != 0 or result.x is None:
        raise ValueError(f"静态子模型未取得已证明最优解：{result.message}")
    chosen = [candidate for candidate, value in zip(candidates, result.x) if value > 0.5]
    return chosen, float(result.fun)


def build_2025_no_tie_submodel(
    storage_source: Path = STORAGE_SCREEN,
    transformer_source: Path = TRANSFORMER_PATH,
    forward_source: Path = FORWARD_LAYERS,
    capex_source: Path = TRANSFORMER_CAPEX,
) -> tuple[list[dict], list[dict]]:
    storage = [row for row in read_csv(storage_source) if row["capacity_case"] == "hold_2024_transformer_path_capacity"]
    prior = {
        (row["study_region_id"], int(row["voltage_kv"]), row["model_station_id"]): row
        for row in read_csv(transformer_source)
        if int(row["year"]) == 2024 and row["reverse_variant"] == "night_central"
    }
    layers = {
        (row["study_region_id"], int(row["voltage_kv"])): row
        for row in read_csv(forward_source)
        if int(row["year"]) == 2025
    }
    transformer_only = {
        (row["study_region_id"], int(row["voltage_kv"])): row
        for row in read_csv(capex_source)
        if int(row["year"]) == 2025 and row["reverse_variant"] == "night_central"
    }
    catalog = local_unit_catalog()
    coefficients = {row["voltage_kv"]: row["base_coefficient_10k_cny_per_purchased_mva"] for row in replacement_cost_coefficients()}
    by_layer = {}
    for row in storage:
        layer = row["study_region_id"], int(row["voltage_kv"])
        station_id = row["model_station_id"]
        prior_row = prior[layer + (station_id,)]
        old_pair = (float(prior_row["selected_unit_1_mva"]), float(prior_row["selected_unit_2_mva"]))
        candidates = []
        for pair in combinations_with_replacement(catalog[layer], 2):
            if any(new < old for old, new in zip(old_pair, pair)):
                continue
            capacity = sum(pair)
            forward_shortfall = max(0.0, float(row["forward_peak_mw"]) - 0.95 * capacity)
            reverse_shortfall = max(0.0, float(row["reverse_peak_mw"]) - 0.8 * 0.95 * capacity)
            forward_modules = module_count_for_peak(forward_shortfall, int(row["forward_d95_max_run_hours"]))[2]
            reverse_modules = module_count_for_peak(reverse_shortfall, int(row["reverse_d95_max_run_hours"]))[2]
            modules = max(forward_modules, reverse_modules)
            if modules > MAX_ANCHORED_STORAGE_MODULES:
                continue
            transformer_cost = sum(new * coefficients[layer[1]] for old, new in zip(old_pair, pair) if new > old)
            storage_cost = storage_capex_10k_cny(modules)
            candidates.append({
                "study_region_id": layer[0],
                "voltage_kv": layer[1],
                "year": 2025,
                "model_station_id": station_id,
                "prior_unit_1_mva": old_pair[0],
                "prior_unit_2_mva": old_pair[1],
                "selected_unit_1_mva": pair[0],
                "selected_unit_2_mva": pair[1],
                "capacity_mva": capacity,
                "storage_modules": modules,
                "forward_shortfall_before_storage_mw": round(forward_shortfall, 6),
                "reverse_shortfall_before_storage_mw": round(reverse_shortfall, 6),
                "transformer_investment_10k_cny": round(transformer_cost, 6),
                "storage_investment_10k_cny": round(storage_cost, 6),
                "investment_10k_cny": round(transformer_cost + storage_cost, 6),
                "technical_scope": "2025_station_aggregate_peak_and_D95_proxy_not_guide_certification",
                "cost_scope": "2025_investment_only_no_lifecycle_or_ties_or_new_line",
            })
        if not candidates:
            raise ValueError(f"{layer} {station_id} 没有 0—10 柜范围内的静态候选")
        by_layer.setdefault(layer, {})[station_id] = candidates

    station_results = []
    layer_results = []
    for layer, candidates_by_station in sorted(by_layer.items()):
        peak = float(layers[layer]["estimated_synchronous_forward_peak_mw"])
        chosen, objective = solve_layer_candidates(candidates_by_station, RIGID_CLR_CAP * peak)
        capacity = sum(row["capacity_mva"] for row in chosen)
        if not np.isclose(sum(row["investment_10k_cny"] for row in chosen), objective, rtol=0, atol=1e-3):
            raise ValueError(f"{layer} 求解器目标与逐站投资不一致")
        station_results.extend(chosen)
        layer_results.append({
            "study_region_id": layer[0],
            "voltage_kv": layer[1],
            "year": 2025,
            "station_count": len(chosen),
            "synchronous_forward_peak_mw": peak,
            "selected_capacity_mva": capacity,
            "actual_clr": round(capacity / peak, 9),
            "clr_cap": RIGID_CLR_CAP,
            "selected_storage_modules": sum(row["storage_modules"] for row in chosen),
            "selected_transformer_investment_10k_cny": round(sum(row["transformer_investment_10k_cny"] for row in chosen), 6),
            "selected_storage_investment_10k_cny": round(sum(row["storage_investment_10k_cny"] for row in chosen), 6),
            "selected_2025_investment_10k_cny": round(objective, 6),
            "transformer_only_2025_investment_10k_cny": float(transformer_only[layer]["base_capex_10k_cny"]),
            "solver_status": "proven_optimal_within_restricted_2025_submodel",
            "technical_scope": "2025_station_aggregate_peak_and_D95_proxy_not_guide_certification",
            "cost_scope": "2025_investment_only_no_lifecycle_or_ties_or_new_line",
        })
    return station_results, layer_results


def main() -> None:
    parser = argparse.ArgumentParser(description="验证 2025 年无联络主变+储能静态投资子模型")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    stations, layers = build_2025_no_tie_submodel()
    write_csv(stations, args.output_dir / "submodel_2025_no_tie_stations.csv")
    write_csv(layers, args.output_dir / "submodel_2025_no_tie_layers.csv")
    print(f"已求解 {len(stations)} 站、{len(layers)} 层的受限 2025 年投资子模型；不构成全寿命刚性最优结果。")


if __name__ == "__main__":
    main()
