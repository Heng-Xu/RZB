"""站级转供率 × 转接前负荷基数的等效能力接口。

既有转供率为研究情景输入；新增独立联络单元参考局部可切换区段。
不要求全区县馈线拓扑；本模块参照表仍是参数变化表，不代替年度优化结果。
"""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

from .new_line_section_audit import DATA, designed_new_line_section


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE = Path(__file__).resolve().parent / (
    "outputs/joint_shared_measure/station_rate_all_years_load_reallocation_full_service_city_A")
DEFAULT_DEST = ROOT / "docs/2026-10-01局部联络仿真依据"


def station_rate_ceiling(area_class):
    if area_class not in ("A+", "A", "B", "C"):
        raise ValueError(f"未定义供电类别的转供率上限：{area_class}")
    return .7 if area_class in ("A+", "A") else .5


def pair_equivalent_units(degrees):
    """仅把站级关联数配成一次计费的双端单元，不推测实际路由。"""
    remaining = {k: int(v) for k, v in degrees.items()}
    if any(v < 0 or v != degrees[k] for k, v in remaining.items()):
        raise ValueError("新增关联单元数必须为非负整数")
    total = sum(remaining.values())
    if total % 2 or (remaining and max(remaining.values()) > total // 2):
        raise ValueError("单元端点数量无法组成无自联络的双端项目")
    pairs = []
    while sum(remaining.values()):
        active = sorted((k for k, v in remaining.items() if v),
                        key=lambda k: (-remaining[k], k))
        a, b = active[:2]
        remaining[a] -= 1
        remaining[b] -= 1
        pairs.append(tuple(sorted((a, b))))
    return pairs


def allocate_station_transfers(outgoing, incoming, tolerance=1e-6):
    """按固定站号顺序给出守恒的站间分配表；分配不进入寻优。"""
    sent, received = dict(outgoing), dict(incoming)
    if any(v < -tolerance for v in (*sent.values(), *received.values())):
        raise ValueError("转出与承接量不得为负")
    if abs(sum(sent.values()) - sum(received.values())) > tolerance:
        raise ValueError("区县转出与承接总量不守恒")
    for sid in set(sent) | set(received):
        common = min(sent.get(sid, 0), received.get(sid, 0))
        if common > tolerance:
            raise ValueError("最小转接解不应同时从同站转出和承接")
        sent[sid] = max(0, sent.get(sid, 0) - common)
        received[sid] = max(0, received.get(sid, 0) - common)
    moves = []
    for a in sorted(sent):
        for b in sorted(received):
            if a == b:
                continue
            amount = min(sent[a], received[b])
            if amount > 1e-8:
                moves.append({"donor": a, "receiver": b, "mw": amount})
                sent[a] -= amount
                received[b] -= amount
    if sum(sent.values()) > tolerance or sum(received.values()) > tolerance:
        raise ValueError("站级分配表未覆盖转出与承接量")
    return moves


def capacity_from_station_rate(base_load_mw, initial_fraction, line_count,
                               increment_mw, fraction_ceiling=1.0):
    """基数在设备和转接决策前固定；新增线路只改变能力比例。"""
    values = (base_load_mw, initial_fraction, increment_mw, fraction_ceiling)
    if not all(math.isfinite(float(v)) for v in values):
        raise ValueError("转供参数必须为有限值")
    if base_load_mw <= 0 or increment_mw <= 0:
        raise ValueError("站级负荷基数和新增单元增量须为正")
    if not 0 <= initial_fraction <= fraction_ceiling <= 1:
        raise ValueError("既有率、规划率上限须满足0 <= 既有率 <= 上限 <= 1")
    if not isinstance(line_count, int) or line_count < 0:
        raise ValueError("在役新增单元数须为非负整数")
    raw_fraction = initial_fraction + line_count * increment_mw / base_load_mw
    effective_fraction = min(fraction_ceiling, raw_fraction)
    return {
        "base_load_mw": float(base_load_mw),
        "initial_fraction": float(initial_fraction),
        "line_count": line_count,
        "new_line_increment_mw": float(increment_mw),
        "fraction_ceiling": float(fraction_ceiling),
        "initial_capacity_mw": initial_fraction * base_load_mw,
        "raw_capacity_fraction": raw_fraction,
        "capacity_fraction": effective_fraction,
        "capacity_mw": effective_fraction * base_load_mw,
        "credited_new_capacity_mw": (
            effective_fraction - initial_fraction) * base_load_mw,
    }


def new_line_increment_reference():
    section = designed_new_line_section()
    increment = section["2025_feeder_stress_section_load_seed_mw"]
    source_hashes = {
        name: hashlib.sha256((DATA / name).read_bytes()).hexdigest()
        for name in ("node_master.csv", "feeder_master.csv", "base_debug_edges.csv",
                     "node_load_seed_pf095.csv")
    }
    return {
        "model": "station_rate_equivalent_capacity",
        "scope": "normal_station_load_reallocation_planning_simulation",
        "capacity_formula": "Q_cap = rho_effective * B_station",
        "base_definition": "station_supply_area_pre_transfer_planning_load",
        "current_base_proxy": "estimated_station_forward_peak_mw",
        "base_proxy_status": (
            "annual_station_positive_net_flow_peak_proxy_not_measured_gross_area_load"),
        "new_line_increment_mw": increment,
        "new_line_increment_basis": (
            "one_new_dedicated_receiving_feeder_serving_one_isolated_local_load_section"),
        "new_line_increment_status": (
            "local_case_calibrated_independent_unit_assumption_not_standard_line_rating"),
        "fraction_increment_formula": "delta_rho = new_line_increment_mw / B_station",
        "fraction_update_formula": (
            "rho_effective = min(rho_ceiling, rho_initial + n * delta_rho)"),
        "rate_ceiling_status": "research_policy_selected_from_guide_recommended_range",
        "preserve_initial_fraction_configuration": True,
        "year_rule": (
            "unit_increment_fixed; station_base_follows_declared_annual_load_scenario"),
        "sharing_rule": (
            "add_increment_once_per_independent_unit; no_duplicate_shared_load_or_path"),
        "topology_scope": (
            "county_level_equivalent_allocation_not_observed_all_station_pair_ties"),
        "normal_flow_rule": (
            "total_station_outgoing <= capacity_mw; receiver_post_load_capacity_checked"),
        "planning_target_rule": (
            "if_target_enabled_capacity_mw >= target_fraction * same_station_base"),
        "source_section": section,
        "source_csv_sha256": source_hashes,
        "optimization_status": "station_equivalent_constraints_integrated_in_annual_solver",
    }


def build_reference(source_dir=DEFAULT_SOURCE):
    reference = new_line_increment_reference()
    increment = reference["new_line_increment_mw"]
    rows = []
    source_hashes = {}
    for district in ("pizhou", "city"):
        summary_path = Path(source_dir) / district / "summary.json"
        station_path = Path(source_dir) / district / "rigid_stations.csv"
        summaries = json.loads(summary_path.read_text(encoding="utf-8"))
        summary = next(r for r in summaries if r["scheme"] == "rigid")
        initial = float(summary["existing_transfer_fraction"])
        target = float(summary["target_transfer_fraction"])
        source_hashes[district] = {
            "station_file": str(station_path),
            "station_sha256": hashlib.sha256(station_path.read_bytes()).hexdigest(),
            "summary_sha256": hashlib.sha256(summary_path.read_bytes()).hexdigest(),
            "area_class_override": summary.get("area_class_override"),
            "n1_load_requirement": summary.get("n1_load_requirement"),
        }
        with station_path.open(encoding="utf-8-sig", newline="") as handle:
            stations = list(csv.DictReader(handle))
        for row in stations:
            base = float(row["forward_mw"])
            area = row["area_class"]
            ceiling = station_rate_ceiling(area)
            result = capacity_from_station_rate(base, initial, 1, increment, ceiling)
            rows.append({
                "district": district, "station": row["station"],
                "year": int(row["year"]), "area_class": area,
                "source_area_class": row.get("source_area_class", area),
                "area_class_status": row.get("area_class_status", "source_asset_row"),
                "station_load_base_mw": base,
                "base_status": reference["base_proxy_status"],
                "initial_fraction_scenario": initial,
                "initial_capacity_scenario_mw": result["initial_capacity_mw"],
                "target_fraction_scenario": target,
                "target_capacity_mw": target * base,
                "capacity_gap_to_target_mw": max(0.0, (target - initial) * base),
                "one_independent_new_line_increment_mw": increment,
                "one_line_raw_fraction_increment": increment / base,
                "one_line_fraction_increment_percentage_points": 100 * increment / base,
                "fraction_ceiling_scenario": ceiling,
                "one_line_effective_fraction": result["capacity_fraction"],
                "one_line_effective_capacity_mw": result["capacity_mw"],
                "one_line_credited_increment_mw": result["credited_new_capacity_mw"],
                "single_station_unit_need_to_target": max(
                    0, math.ceil((target - initial) * base / increment - 1e-12)),
                "unit_need_status": (
                    "single_station_check_not_additive_count_of_county_line_projects"),
            })
    reference["current_initial_and_target_rate_status"] = (
        "preserved_previous_model_scenarios_not_verified_existing_station_capability")
    reference["station_reference_source"] = source_hashes
    reference["station_year_count"] = len(rows)
    reference["reference_table_status"] = (
        "before_build_and_one_unit_what_if_not_new_optimized_annual_results")
    return reference, rows


def main():
    parser = argparse.ArgumentParser(description="生成站级等效转供能力参数和参照表")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_DEST)
    args = parser.parse_args()
    reference, rows = build_reference(args.source)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "站级等效转供参数.json").write_text(
        json.dumps(reference, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (args.output / "逐站逐年转供基数与单线增量参照.csv").open(
            "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({
        "station_year_count": len(rows),
        "fixed_new_line_increment_mw": reference["new_line_increment_mw"],
        "status": reference["optimization_status"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
