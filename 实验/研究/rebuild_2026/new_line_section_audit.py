"""仿真新馈线候选：墩振线 23—24 杆新分段，下游接河湾变新出线。"""

import csv
from collections import defaultdict, deque
from functools import lru_cache
from pathlib import Path


DATA = Path(__file__).resolve().parents[1] / "data/tuomin/10kv_case/data"
FEEDER = "PZXL-00099"
UPSTREAM_NAME = "dzhen线23杆"
DOWNSTREAM_NAME = "dzhen线24杆"


def rows(name: str) -> list[dict]:
    with (DATA / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@lru_cache(maxsize=1)
def designed_new_line_section() -> dict:
    names = {r["canonical_name"]: r["node_id"] for r in rows("node_master.csv")
             if r["feeder_id"] == FEEDER}
    upstream, endpoint = names[UPSTREAM_NAME], names[DOWNSTREAM_NAME]
    source = next(r["source_root_node_id"] for r in rows("feeder_master.csv")
                  if r["feeder_id"] == FEEDER)
    adjacency = defaultdict(set)
    for row in rows("base_debug_edges.csv"):
        a, b = row["from_node_id"], row["to_node_id"]
        if row["active_in_debug_base"] != "YES" or not a.startswith(FEEDER) or not b.startswith(FEEDER):
            continue
        adjacency[a].add(b)
        adjacency[b].add(a)
    if endpoint not in adjacency[upstream]:
        raise ValueError("墩振线 23—24 杆档距未在调试拓扑中闭合")

    def reachable(cut: bool) -> set[str]:
        seen = {endpoint}
        queue = deque([endpoint])
        while queue:
            node = queue.popleft()
            for nxt in adjacency[node]:
                if cut and {node, nxt} == {upstream, endpoint}:
                    continue
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        return seen

    if source not in reachable(False):
        raise ValueError("拟接入点与墩振线源端不连通")
    section = reachable(True)
    if source in section:
        raise ValueError("拟新建分段开关未隔离墩振线源端")
    loads = {r["node_id"]: float(r["p_seed_mw_at_feeder_stress"])
             for r in rows("node_load_seed_pf095.csv") if r["feeder_id"] == FEEDER}
    return {
        "candidate_id": "SIM-NEW-DZHEN-RIVER-BUS",
        "donor_feeder_id": FEEDER,
        "new_isolation_switch_span": "dzhen线23杆—dzhen线24杆",
        "upstream_node_id": upstream,
        "new_line_connection_node_id": endpoint,
        "receiver_station_id": "BDZ-00048",
        "receiver_connection": "河湾变新10kV出线间隔（仿真）",
        "isolated_section_nodes": len(section),
        "2025_feeder_stress_section_load_seed_mw": round(sum(loads.get(n, 0) for n in section), 8),
        "2025_feeder_total_load_seed_mw": round(sum(loads.values()), 8),
        "source_pdf": "data/tuomin/10kv_case/source/10kv.7z::10kv/邳州_10kV墩振线.pdf",
        "source_span_xlsx": "data/tuomin/10kv_case/source/10kv.7z::10kv/邳州_10kV墩振线明细.xlsx",
        "topology_source": "data/tuomin/10kv_case/data/base_debug_edges.csv",
        "status": "designed_candidate_new_switch_and_new_station_feeder_not_existing_asset",
    }
