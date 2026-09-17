"""TIE-002 高光伏跨站转移的规划级供电边界拓扑校核。

这里只验证“开原供电边界、再合站间联络”是否保持单电源开环供电，不输出
现场倒闸操作票。后续若墩南线分段开关完成现场闭环，可将 DONOR_BOUNDARY
从馈线出口边界替换为实际分段开关，算法本身无需改变。
"""

from __future__ import annotations

from typing import Iterable

import pandas as pd


NODES = ("DJ_SOURCE", "DNAN_AREA", "HPAO_AREA", "HW_SOURCE")
EDGES = {
    "DONOR_BOUNDARY": ("DJ_SOURCE", "DNAN_AREA"),
    "TIE_002": ("DNAN_AREA", "HPAO_AREA"),
    "RECEIVER_BOUNDARY": ("HPAO_AREA", "HW_SOURCE"),
}


def connected_components(
    nodes: Iterable[str],
    edges: dict[str, tuple[str, str]],
    closed_state: dict[str, bool],
) -> list[set[str]]:
    node_set = set(nodes)
    adjacency = {node: set() for node in node_set}
    for edge_id, (u, v) in edges.items():
        if not closed_state.get(edge_id, False):
            continue
        if u not in node_set or v not in node_set:
            raise ValueError(f"edge {edge_id} references unknown node")
        adjacency[u].add(v)
        adjacency[v].add(u)

    components: list[set[str]] = []
    unseen = set(node_set)
    while unseen:
        start = unseen.pop()
        comp = {start}
        stack = [start]
        while stack:
            current = stack.pop()
            for nxt in adjacency[current]:
                if nxt in unseen:
                    unseen.remove(nxt)
                    comp.add(nxt)
                    stack.append(nxt)
        components.append(comp)
    return components


def _supply_label(node: str, states: dict[str, bool]) -> str:
    comps = connected_components(NODES, EDGES, states)
    comp = next(c for c in comps if node in c)
    has_dj = "DJ_SOURCE" in comp
    has_hw = "HW_SOURCE" in comp
    if has_dj and has_hw:
        return "PARALLEL_SOURCES_INVALID"
    if has_dj:
        return "DJ_SOURCE"
    if has_hw:
        return "HW_SOURCE"
    return "DEENERGIZED"


def _no_parallel_sources(states: dict[str, bool]) -> bool:
    comps = connected_components(NODES, EDGES, states)
    return all(not ({"DJ_SOURCE", "HW_SOURCE"} <= comp) for comp in comps)


def boundary_reconfiguration_trace() -> pd.DataFrame:
    """给出规划状态序列，并显式验证不能直接合联络形成双电源并列。"""
    rows: list[dict[str, object]] = []

    scenarios = [
        (
            0,
            "NORMAL",
            {"DONOR_BOUNDARY": True, "TIE_002": False, "RECEIVER_BOUNDARY": True},
            "现状：墩南由墩集变供电，河炮由河湾变供电，站间联络分闸",
            True,
        ),
        (
            1,
            "OPEN_DONOR_BOUNDARY",
            {"DONOR_BOUNDARY": False, "TIE_002": False, "RECEIVER_BOUNDARY": True},
            "规划边界切换中间态：先退出墩南原供电边界，避免两站经10kV并列",
            True,
        ),
        (
            2,
            "CLOSE_TIE_AFTER_BOUNDARY_OPEN",
            {"DONOR_BOUNDARY": False, "TIE_002": True, "RECEIVER_BOUNDARY": True},
            "重构态：TIE-002投入，墩南供电边界转移至河湾变侧",
            True,
        ),
        (
            99,
            "FORBIDDEN_DIRECT_TIE_CLOSE",
            {"DONOR_BOUNDARY": True, "TIE_002": True, "RECEIVER_BOUNDARY": True},
            "禁止态：若原供电边界未退出即合联络，会形成两110kV电源经10kV并列",
            False,
        ),
    ]

    for step, state_name, states, note, expected_allowed in scenarios:
        no_parallel = _no_parallel_sources(states)
        actual_allowed = no_parallel
        rows.append(
            {
                "step": step,
                "state": state_name,
                "donor_boundary_closed": states["DONOR_BOUNDARY"],
                "tie002_closed": states["TIE_002"],
                "receiver_boundary_closed": states["RECEIVER_BOUNDARY"],
                "dnan_supply": _supply_label("DNAN_AREA", states),
                "hpao_supply": _supply_label("HPAO_AREA", states),
                "radial_no_parallel_sources": no_parallel,
                "planning_state_allowed": actual_allowed,
                "expected_allowed": expected_allowed,
                "check_matches_expected": actual_allowed == expected_allowed,
                "note": note,
            }
        )

    return pd.DataFrame(rows)
