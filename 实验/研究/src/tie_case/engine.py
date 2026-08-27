"""徐州 110 kV 项目——10 kV 联络独立案例分析引擎（规划级）。

数据基线：data/tuomin/10kv_case/（10kV_AgentReady_V5_2 解包）。
口径约束见 AGENTS.md §5.1 与包内 MODEL_CONFIG.yaml / final_preflight_qa.csv：
- 支路有效热限 = min(导线 Imax_base, SRC06 馈线最大允许电流)；
- 电压硬限 0.93—1.07 pu，优选 0.95—1.05 pu；Q 缺失按 PF 0.95 折算；
- 河东线规划 P 为 √3×10kV×I×0.95 代理值，引用必须带 proxy_i_pf095 标记；
- 六馈线年度极值不是同步断面，禁止相加冒充同步场景。
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


class TieCaseError(ValueError):
    """案例输入、拓扑或门禁不满足。"""


BASE_KV = 10.0
V_HARD = (0.93, 1.07)
V_SOFT = (0.95, 1.05)


@dataclass
class CaseData:
    case_root: Path
    config: dict[str, Any]
    edges: pd.DataFrame
    feeders: pd.DataFrame
    ties: pd.DataFrame
    load_seed: pd.DataFrame
    pv_seed: pd.DataFrame
    preflight_qa: pd.DataFrame
    confirmed_ties: dict[str, str] = field(default_factory=dict)

    @property
    def feeder_ids(self) -> list[str]:
        return list(self.config["scope"]["feeder_ids"])


def load_case(case_root: Path | str) -> CaseData:
    root = Path(case_root)
    if not root.is_dir():
        raise TieCaseError(f"case root not found: {root}")
    with (root / "MODEL_CONFIG.yaml").open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    def _read(name: str) -> pd.DataFrame:
        return pd.read_csv(root / "data" / name, encoding="utf-8-sig")

    ties = _read("tie_master.csv")
    confirmed = {
        str(row["tie_id"]): str(row["normal_state"])
        for _, row in ties.iterrows()
        if row.get("normal_state") in ("OPEN", "CLOSED")
    }
    declared = {str(k): str(v) for k, v in (config.get("switches", {}).get("confirmed_ties", {}) or {}).items()}
    if declared and declared != confirmed:
        raise TieCaseError(f"tie states disagree between MODEL_CONFIG and tie_master: {declared} vs {confirmed}")

    edges = _read("physical_edges.csv")
    required_edge_cols = {
        "edge_id", "feeder_id", "from_node_id", "to_node_id",
        "r_ohm", "x_ohm", "effective_rate_a_base", "normal_state",
    }
    missing = sorted(required_edge_cols - set(edges.columns))
    if missing:
        raise TieCaseError(f"physical_edges missing columns: {missing}")

    case = CaseData(
        case_root=root,
        config=config,
        edges=edges,
        feeders=_read("feeder_master.csv"),
        ties=ties,
        load_seed=_read("node_load_seed_pf095.csv"),
        pv_seed=_read("node_pv_seed.csv"),
        preflight_qa=_read("final_preflight_qa.csv"),
        confirmed_ties=confirmed,
    )
    run_preflight_gate(case)
    return case


def run_preflight_gate(case: CaseData) -> dict[str, str]:
    """把包自带 QA 门禁固化为运行时检查；任何 P0 FAIL 即拒绝计算。"""
    results: dict[str, str] = {}
    for _, row in case.preflight_qa.iterrows():
        qa_id = str(row["qa_id"])
        priority = str(row.get("priority", "P1"))
        status = str(row.get("status", ""))
        results[qa_id] = status
        if priority.startswith("P0") and status not in {
            "PASS", "PASS_WITH_ANOMALY_GUARD", "PASS_PLANNING",
            "PASS_PLANNING_SEED", "PARTIAL_BUT_SCENARIO_READY",
            "PASS_FIRST_CASE", "NO_LONGER_BLOCKS_PLANNING",
        }:
            raise TieCaseError(f"preflight gate {qa_id} blocks planning: {status}")
    return results


def feeder_boundary_p_mw(case: CaseData, feeder_id: str) -> tuple[float, bool]:
    """馈线边界正应力 P；河东线（源 P=0 异常，按电流折算）返回代理标记。"""
    row = case.feeders[case.feeders["feeder_id"].eq(feeder_id)]
    if row.empty:
        raise TieCaseError(f"unknown feeder {feeder_id}")
    record = row.iloc[0]
    source = str(record.get("model_boundary_p_source", ""))
    proxy = ("ANOMALY" in source) or ("DERIVED_FROM" in source)
    return float(record["model_boundary_p_mw"]), proxy


def build_feeder_tree(case: CaseData, feeder_id: str, extra_closed_edges: pd.DataFrame | None = None):
    """构造单馈线辐射树：{node: [(neighbor, edge_row)]}, roots, node→(P,Q)。"""
    edges = case.edges[case.edges["feeder_id"].eq(feeder_id)]
    parts = [edges]
    if extra_closed_edges is not None and not extra_closed_edges.empty:
        parts.append(extra_closed_edges)
    all_edges = pd.concat(parts, ignore_index=True, sort=False)
    closed = all_edges[
        all_edges["normal_state"].fillna("").eq("CLOSED")
        | all_edges.get("debug_state", pd.Series(dtype=str)).fillna("").eq("CLOSED")
    ]
    adjacency: dict[str, list[tuple[str, pd.Series]]] = {}
    for row in closed.itertuples(index=False):
        u, v = str(row.from_node_id), str(row.to_node_id)
        adjacency.setdefault(u, []).append((v, row._asdict()))
        adjacency.setdefault(v, []).append((u, row._asdict()))
    feeder = case.feeders[case.feeders["feeder_id"].eq(feeder_id)].iloc[0]
    root = str(feeder["source_root_node_id"])
    visited = {root}
    queue = [root]
    parent: dict[str, tuple[str, dict[str, Any]]] = {}
    children: dict[str, list[str]] = {}
    while queue:
        node = queue.pop()
        for neighbor, edge in adjacency.get(node, []):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            parent[neighbor] = (node, edge)
            children.setdefault(node, []).append(neighbor)
            queue.append(neighbor)
    return {"root": root, "visited": visited, "parent": parent, "children": children}


def _accumulate_and_backfeed(tree, injections: dict[str, tuple[float, float]], v_root: float = 1.0):
    """辐射网前推回代：返回 (node_voltages, branch_flows)。"""
    parent = tree["parent"]
    children = tree["children"]
    order = []
    stack = [tree["root"]]
    while stack:
        node = stack.pop()
        order.append(node)
        stack.extend(children.get(node, []))
    # 后序累加功率（叶→根）
    sub_p: dict[str, float] = {}
    sub_q: dict[str, float] = {}
    for node in reversed(order):
        p, q = injections.get(node, (0.0, 0.0))
        total_p, total_q = p, q
        for child in children.get(node, []):
            total_p += sub_p.get(child, 0.0) + (
                (sub_p[child] ** 2 + sub_q[child] ** 2) * parent[child][1]["r_ohm"]
                / max((BASE_KV) ** 2, 1e-9)
                if child in parent else 0.0
            )
            total_q += sub_q.get(child, 0.0) + (
                (sub_p.get(child, 0.0) ** 2 + sub_q.get(child, 0.0) ** 2) * parent[child][1]["x_ohm"]
                / max(BASE_KV ** 2, 1e-9)
            )
        sub_p[node], sub_q[node] = total_p, total_q
    # 回代求电压（根→叶）
    voltages = {tree["root"]: v_root}
    branch: dict[str, float] = {}
    for node in order:
        if node == tree["root"]:
            continue
        up, edge = parent[node]
        v_up = voltages.get(up, v_root)
        p = sub_p.get(node, 0.0)
        q = sub_q.get(node, 0.0)
        drop = (p * float(edge["r_ohm"]) + q * float(edge["x_ohm"])) / max(
            BASE_KV * v_up * BASE_KV, 1e-9
        )
        voltages[node] = v_up - drop
        current_a = math.hypot(p, q) / (math.sqrt(3.0) * BASE_KV * max(v_up, 1e-6)) * 1000.0
        branch[str(edge["edge_id"])] = current_a
    return voltages, branch


def scenario_s1_forward(
    case: CaseData,
    feeder_id: str,
    pv_factor: float = 0.0,
    load_factor: float = 1.0,
) -> dict[str, Any]:
    """S1 正向应力包络：馈线边界 P 按 kVA 权重撒点，PV factor 默认 0。

    负荷注入按 load_factor 缩放（S2 高 PV 反送场景在仿真内降载，而不是只在
    报告字段缩放）。结构化拓扑为碎片森林时（源数据缺杆段记录），只有源端
    可达分量参与潮流；未可达节点负荷如实计入 unserved，不得把边界功率冒充
    已校核负荷。umax 用于高 PV 反送过电压校核。
    """
    boundary_p, proxy = feeder_boundary_p_mw(case, feeder_id)
    seed = case.load_seed[case.load_seed["feeder_id"].eq(feeder_id)]
    if seed.empty:
        raise TieCaseError(f"no load seed for {feeder_id}")
    injections: dict[str, tuple[float, float]] = {}
    load_only: dict[str, float] = {}
    for row in seed.itertuples(index=False):
        p = float(row.p_seed_mw_at_feeder_stress) * load_factor
        node = str(row.node_id)
        injections[node] = (p, p * math.tan(math.acos(0.95)))
        load_only[node] = p
    if pv_factor > 0:
        for row in case.pv_seed[case.pv_seed["feeder_id"].eq(feeder_id)].itertuples(index=False):
            node = str(row.node_id)
            pg = float(row.pv_capacity_kva_seed) / 1000.0 * pv_factor
            base = injections.get(node, (0.0, 0.0))
            injections[node] = (base[0] - pg, base[1])
    tree = build_feeder_tree(case, feeder_id)
    reachable = tree["visited"]
    voltages, branch = _accumulate_and_backfeed(tree, injections)
    umin = min(voltages.values())
    umax = max(voltages.values())
    feeder_edges = case.edges[case.edges["feeder_id"].eq(feeder_id)]
    limits = {
        str(record["edge_id"]): float(record["effective_rate_a_base"])
        for _, record in feeder_edges.iterrows()
    }
    max_loading = max(
        (branch[eid] / limits[eid] * 100.0 for eid in branch if eid in limits and limits[eid] > 0),
        default=0.0,
    )
    # served/unserved 只度量负荷 seed 的源端可达部分（与 PV 抵扣无关）；
    # 潮流本身用净注入。
    served = sum(p for node, p in load_only.items() if node in reachable)
    scenario_load = boundary_p * load_factor
    unserved = max(scenario_load - served, 0.0)
    coverage = served / (boundary_p * load_factor) * 100.0 if scenario_load > 0 else 100.0
    return {
        "feeder_id": feeder_id,
        "boundary_p_mw": boundary_p,
        "proxy_i_pf095": proxy,
        "umin_pu": round(umin, 5),
        "umax_pu": round(umax, 5),
        "voltage_pass_hard": V_HARD[0] <= umin and umax <= V_HARD[1],
        "max_loading_pct": round(max_loading, 2),
        "served_load_mw": round(served, 4),
        "unserved_mw": round(unserved, 4),
        "load_coverage_pct": round(coverage, 2),
        "topology_fragmented": unserved > 1e-6,
    }


def tie_endpoint_reachability(case: CaseData) -> dict[str, dict[str, bool]]:
    """按 debug 基准拓扑校验各联络双侧端点是否源端可达（QF09 闭环判据）。"""
    edges = pd.read_csv(case.case_root / "data" / "base_debug_edges.csv", encoding="utf-8-sig")
    switches = pd.read_csv(case.case_root / "data" / "switch_master.csv", encoding="utf-8-sig")
    adjacency: dict[str, list[str]] = {}

    def add(u: str, v: str) -> None:
        adjacency.setdefault(u, []).append(v)
        adjacency.setdefault(v, []).append(u)

    active = edges[edges["active_in_debug_base"].astype(str).str.upper().eq("YES")]
    for row in active.itertuples(index=False):
        add(str(row.from_node_id), str(row.to_node_id))
    for row in switches[switches["debug_state"].astype(str).eq("CLOSED")].itertuples(index=False):
        add(str(row.from_node_id), str(row.to_node_id))

    feeders = pd.read_csv(case.case_root / "data" / "feeder_master.csv", encoding="utf-8-sig")
    reach: dict[str, set[str]] = {}
    for row in feeders.itertuples(index=False):
        root = str(row.source_root_node_id)
        seen = {root}
        queue = [root]
        while queue:
            node = queue.pop()
            for nxt in adjacency.get(node, []):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        reach[str(row.feeder_id)] = seen

    result: dict[str, dict[str, bool]] = {}
    for row in case.ties.itertuples(index=False):
        from_feeder = str(row.from_feeder_id)
        to_feeder = str(row.to_feeder_id)
        from_node = str(row.from_node_id)
        to_node = str(row.to_node_id)
        result[str(row.tie_id)] = {
            "from_side": bool(from_node and not from_node.startswith("NEED_CONFIRM") and from_node in reach.get(from_feeder, set())),
            "to_side": bool(to_node and not to_node.startswith("NEED_CONFIRM") and to_node in reach.get(to_feeder, set())),
        }
    return result


def tie_transfer_scan(case: CaseData, tie_id: str, direction: str, step_mw: float = 0.25) -> dict[str, Any]:
    """S3 转供扫描：逐步增大经联络线路的转供量，报告首个绑定约束。

    规划级容量包络：三重约束为送侧馈线可转负荷、受端站正常备用容量、
    路径最小有效热限，取最先绑定者。转供后潮流（电压降/支路负载分布）
    不在扫描内——受端馈线同时段自身负载余量未计入，涉及馈线拓扑碎片化
    时该余量亦不可核算；结果为容量包络口径，方式安排时需结合时段错峰。
    双侧端点必须源端可达（QF09 闭环判据），否则拒绝计算。
    """
    row = case.ties[case.ties["tie_id"].eq(tie_id)]
    if row.empty:
        raise TieCaseError(f"unknown tie {tie_id}")
    record = row.iloc[0]
    reach = tie_endpoint_reachability(case).get(tie_id, {"from_side": False, "to_side": False})
    if not (reach["from_side"] and reach["to_side"]):
        return {
            "tie_id": tie_id,
            "direction": direction,
            "transfer_mw": None,
            "served_load_mw": None,
            "unserved_mw": None,
            "binding_constraint": f"TOPOLOGY_NOT_CLOSED(from_side={reach['from_side']}, to_side={reach['to_side']}); 需图纸闭环后复算",
            "host_station_spare_mva": None,
            "path_thermal_min_mva": None,
            "sending_boundary_p_mw": None,
            "proxy_i_pf095": False,
            "parameter_gate_pass": False,
            "formal_or_debug": "DEBUG_BLOCKED",
        }
    from_feeder = str(record["from_feeder_id"])
    to_feeder = str(record["to_feeder_id"])
    to_station = str(record["to_station_id"])
    from_station = str(record["from_station_id"])
    # direction="from_to"：功率自 from_feeder 送向 to_feeder（受端为 to 侧）。
    if direction == "from_to":
        sending_feeder, host_station = from_feeder, to_station
    elif direction == "to_from":
        sending_feeder, host_station = to_feeder, from_station
    else:
        raise TieCaseError(f"unknown direction {direction!r}; use from_to or to_from")
    station_rows = pd.read_csv(case.case_root / "data" / "station_boundary_2025.csv", encoding="utf-8-sig")
    station = station_rows[station_rows["station_id"].eq(host_station)]
    if station.empty:
        raise TieCaseError(f"unknown host station {host_station}")
    spare_mva = float(station.iloc[0]["normal_spare_at_annual_max_mva"])

    path_limit_mva = math.inf
    tie_edges = case.edges[
        case.edges["feeder_id"].isin([from_feeder, to_feeder])
    ]
    if not tie_edges.empty:
        path_limit_mva = float(tie_edges["effective_rate_mva_10kv"].min())

    boundary_p, proxy = feeder_boundary_p_mw(case, sending_feeder)
    thermal_cap = min(spare_mva, path_limit_mva)
    steps = int(max(thermal_cap, 0.0) / step_mw)
    binding = None
    transferred = 0.0
    for step in range(1, steps + 1):
        candidate = round(step * step_mw, 4)
        if candidate > boundary_p:
            binding = f"sending_feeder_load_exhausted({boundary_p:.2f}MW)"
            break
        if candidate > spare_mva:
            binding = f"host_station_spare({spare_mva:.2f}MVA)"
            break
        if candidate >= path_limit_mva:
            binding = f"path_thermal_limit({path_limit_mva:.2f}MVA)"
            break
        transferred = candidate
    if binding is None and transferred < boundary_p:
        binding = f"path_thermal_limit({path_limit_mva:.2f}MVA)" if spare_mva >= boundary_p else f"host_station_spare({spare_mva:.2f}MVA)"
    return {
        "tie_id": tie_id,
        "direction": direction,
        "transfer_mw": round(transferred, 3),
        "served_load_mw": round(min(transferred, boundary_p), 3),
        "unserved_mw": round(max(boundary_p - transferred, 0.0), 3),
        "binding_constraint": binding or "sending_feeder_load_exhausted",
        "host_station_spare_mva": spare_mva,
        "path_thermal_min_mva": None if math.isinf(path_limit_mva) else round(path_limit_mva, 4),
        "sending_boundary_p_mw": boundary_p,
        "proxy_i_pf095": proxy,
        "parameter_gate_pass": True,
        "formal_or_debug": "PLANNING_ENVELOPE",
    }
