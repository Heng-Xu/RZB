"""从原始逐段线路拓扑计算墩南线 28 开关下游可转供负荷块。"""

import csv
from collections import defaultdict, deque
from functools import lru_cache
from pathlib import Path


DATA = Path(__file__).resolve().parents[1] / "data/tuomin/10kv_case/data"
FEEDER = "PZXL-00092"
SOURCE = "PZXL-00092-N0016"
TIE_END = "PZXL-00092-N0146"
SWITCH_UPSTREAM = "dnan线28杆"
SWITCH_DOWNSTREAM = "dnan线29杆"


def _rows(name: str) -> list[dict]:
    with (DATA / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@lru_cache(maxsize=1)
def transferable_section() -> dict:
    """负荷按原节点种子分配；结果是 2025 馈线应力时刻的仿真值。"""
    nodes = {r["canonical_name"]: r["node_id"] for r in _rows("node_master.csv")
             if r["feeder_id"] == FEEDER}
    upstream, downstream = nodes[SWITCH_UPSTREAM], nodes[SWITCH_DOWNSTREAM]
    adjacency = defaultdict(set)
    for row in _rows("physical_edges.csv"):
        if row["feeder_id"] != FEEDER:
            continue
        a, b = row["from_node_id"], row["to_node_id"]
        adjacency[a].add(b)
        adjacency[b].add(a)
    if downstream not in adjacency[upstream]:
        raise ValueError("原始墩南线逐段数据中缺少 28—29 杆连接")

    def reachable(cut: bool) -> set[str]:
        seen = {TIE_END}
        queue = deque([TIE_END])
        while queue:
            a = queue.popleft()
            for b in adjacency[a]:
                if cut and {a, b} == {upstream, downstream}:
                    continue
                if b not in seen:
                    seen.add(b)
                    queue.append(b)
        return seen

    if SOURCE not in reachable(False):
        raise ValueError("墩南线源端与联络点在原始拓扑中不连通")
    section = reachable(True)
    if SOURCE in section or downstream not in section or upstream in section:
        raise ValueError("28 开关切除后未形成预期的下游供电区段")
    loads = {r["node_id"]: float(r["p_seed_mw_at_feeder_stress"])
             for r in _rows("node_load_seed_pf095.csv") if r["feeder_id"] == FEEDER}
    return {
        "feeder_id": FEEDER,
        "section_switch": "dnan线28开关",
        "switch_upstream_node_id": upstream,
        "switch_downstream_node_id": downstream,
        "tie_endpoint_node_id": TIE_END,
        "section_node_count": len(section),
        "2025_feeder_stress_section_p_seed_mw": round(sum(loads.get(n, 0) for n in section), 8),
        "2025_feeder_stress_total_p_seed_mw": round(sum(loads.values()), 8),
        "source_pdf": "data/tuomin/10kv_case/source/10kv.7z::10kv/邳州_10kVdnan线.pdf",
        "source_span_xlsx": "data/tuomin/10kv_case/source/10kv.7z::10kv/邳州_10kVdnan线明细.xlsx",
        "load_seed_source": "data/tuomin/10kv_case/data/node_load_seed_pf095.csv",
        "evidence_level": "topology_and_allocated_feeder_stress_load_not_synchronous_measured_transfer",
    }
