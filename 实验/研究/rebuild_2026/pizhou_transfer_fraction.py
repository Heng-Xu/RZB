"""依据六馈线原始样本计算邳州等效站间可转供比例。"""

from itertools import product

from scipy.optimize import linprog

from .pizhou_existing_ties import build_feeder_headroom, read_cross_station_ties


def pizhou_sample_fraction() -> dict:
    """静态源端比例；外推至区县属于研究假设，非全县实测。"""
    feeders = {r["feeder_id"]: r for r in build_feeder_headroom()}
    ties = read_cross_station_ties()
    best = (0.0, (), ())
    for directions in product((-1, 0, 1), repeat=len(ties)):
        edges = []
        for tie, direction in zip(ties, directions):
            if direction:
                endpoints = (tie["from_feeder_id"], tie["to_feeder_id"])
                edges.append(endpoints if direction == 1 else endpoints[::-1])
        if not edges:
            continue
        matrix, limits = [], []
        for feeder_id, feeder in feeders.items():
            matrix.append([float(a == feeder_id) for a, _ in edges])
            limits.append(float(feeder["current_equivalent_active_power_mw"]))
            matrix.append([float(b == feeder_id) for _, b in edges])
            limits.append(float(feeder["receiving_current_headroom_mw"]))
        result = linprog([-1.0] * len(edges), A_ub=matrix, b_ub=limits,
                         bounds=(0, None), method="highs")
        if result.success and -result.fun > best[0]:
            best = (-float(result.fun), directions, edges)
    denominator = sum(float(r["current_equivalent_active_power_mw"]) for r in feeders.values())
    return {"sample_feeder_count": len(feeders), "cross_station_tie_count": len(ties),
            "sample_current_equivalent_power_mw": denominator,
            "sample_transfer_screen_mw": best[0],
            "initial_fraction": best[0] / denominator,
            "status": "six_feeder_source_end_proxy_extrapolated_as_regional_scenario_not_verified_transfer"}
