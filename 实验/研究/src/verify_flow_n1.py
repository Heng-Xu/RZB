"""校核层:合成网架 DC 潮流 N-1 枚举。

[合成网架,M2 换真实台账]:M1 收资未到位,按 task-7-brief 裁决从 ScenarioData
派生星型+分区互联 110kV 网架;M2 应换真实线路台账,枚举/潮流逻辑不必大改。

run_n1 简化声明(允许越限行如实输出,判据=跑通+结构正确):solution 落盘只有
ess_mw(额定功率非逐时)、alpha(|ap+an|未分方向)、curtail_mwh(全年汇总),
净负荷仅在两断面近似重构——储能仅在全年P+/P-峰值满出力削峰、其余无储能;
tie 按两端净负荷高低推断转移方向,量≈alpha×回路容量;弃光占比<0.04%全年
PV电量故忽略(M2 应补逐时 p_cur)。
"""
from __future__ import annotations

from typing import Any

import networkx as nx
import numpy as np
import pandas as pd

from src.io_loader import ScenarioData
from src.milp_planner import SPRING_MONTHS

GRID220 = "__GRID220__"          # 220kV 边界平衡节点(DC 潮流参考角=0)
X_PU = 0.1                       # 合成网架线路电抗标幺值(裁决,全网统一)
THERMAL_FACTOR = 1.2             # 热稳限额 = 1.2 × 两端站容量较小者
INTER_ZONE_PAIRS = [("Z1", "Z2"), ("Z2", "Z3"), ("Z4", "Z5"), ("Z1", "Z4")]


def _mother_station(zone) -> str:
    """区内容量最大站;并列同容量时取 station_id 最小者(确定性裁决)。"""
    return min(zone.stations, key=lambda s: (-s.cap_mva, s.station_id)).station_id


def build_synthetic_grid(data: ScenarioData) -> nx.Graph:
    """构造 M1 合成 110kV 网架(星型+分区互联+220kV 边界)。

    分区内各站星型接至"母站"(单回,x=X_PU,限额=THERMAL_FACTOR×两端容量
    较小者);分区间按相邻关系各连2回——networkx.Graph 不支持平行边,故以
    "n_channels=2 的单一等效边"表示(等效x=单回x/2,限额=2×单回限额),
    run_n1 按 n_channels 逐回退化模拟 N-1(而非整条边删除);220kV 边界=
    每分区母站各接一条边到 GRID220。"""
    g = nx.Graph()
    g.add_node(GRID220)
    mothers: dict[str, str] = {}
    for zid in sorted(data.zones):
        zone = data.zones[zid]
        mother = _mother_station(zone)
        mothers[zid] = mother
        for st in zone.stations:
            g.add_node(st.station_id)
            if st.station_id == mother:
                continue
            rating = THERMAL_FACTOR * min(st.cap_mva, data.stations[mother].cap_mva)
            g.add_edge(st.station_id, mother, x=X_PU, rating_mw=rating, n_channels=1,
                       element_id=f"L_{zid}_{st.station_id}_{mother}", kind="intra")
    for za, zb in INTER_ZONE_PAIRS:
        ma, mb = mothers[za], mothers[zb]
        single = THERMAL_FACTOR * min(data.stations[ma].cap_mva, data.stations[mb].cap_mva)
        g.add_edge(ma, mb, x=X_PU / 2, rating_mw=2 * single, n_channels=2,
                   element_id=f"L_{za}_{zb}_{ma}_{mb}", kind="inter")
    for zid, mother in mothers.items():
        rating = THERMAL_FACTOR * data.stations[mother].cap_mva
        g.add_edge(mother, GRID220, x=X_PU, rating_mw=rating, n_channels=1,
                   element_id=f"L_{zid}_boundary_{mother}", kind="boundary")
    return g


def _transformer_elements(data: ScenarioData) -> list[tuple[str, str, float]]:
    """每台主变一个 N-1 元件:(element_id, station_id, 该站最大单台容量);
    简化(裁决):剩余容量都按"减去该站最大单台"计算,同站各单元 loading_pct 相同。"""
    rows = []
    for sid in sorted(data.stations):
        st = data.stations[sid]
        if not st.transformers:
            continue
        max_unit = max(t.capacity_mva for t in st.transformers)
        for t in st.transformers:
            rows.append((f"X_{sid}_{t.unit_id}", sid, max_unit))
    return rows


def _normalize_solution(solution: Any) -> dict:
    """dict(读自 json)或 SolutionBundle 均可,统一转为内部所需字段。"""
    def get(key, default=None):
        return (solution.get(key, default) if isinstance(solution, dict)
                else getattr(solution, key, default))

    def series(key):
        v = get(key, {})
        return v if isinstance(v, pd.Series) else pd.Series({k: float(x) for k, x in v.items()})

    alpha = get("alpha", {})
    alpha_df = alpha if isinstance(alpha, pd.DataFrame) else pd.DataFrame(alpha)
    return {"ess_mw": series("ess_mw"), "expand_mva": series("expand_mva"), "alpha": alpha_df}


def _pnet_prime_at(data: ScenarioData, sol: dict, hour_idx: int,
                    fwd_idx: int, rev_idx: int) -> pd.Series:
    """措施后净负荷(单一时刻近似,见模块 docstring 简化声明)。"""
    stations = sorted(data.stations)
    prime = data.pnet.iloc[hour_idx][stations].astype(float).copy()
    # 放电(P+峰,sign=-1)/充电(P-峰,sign=+1)削峰;其余时刻 sign=0(无储能)
    sign = -1 if hour_idx == fwd_idx else (1 if hour_idx == rev_idx else 0)
    if sign:
        for s in stations:
            prime[s] += sign * float(sol["ess_mw"].get(s, 0.0))
    month = int(data.pnet.index[hour_idx].month)
    season = "spring" if month in SPRING_MONTHS else "winter"
    alpha = sol["alpha"]
    for tie in data.ties:
        if not tie.usable or tie.tie_id not in alpha.index or season not in alpha.columns:
            continue
        ratio = float(alpha.loc[tie.tie_id, season])
        if ratio <= 0:
            continue
        shift = ratio * tie.n_channels * tie.ampacity_mw
        a, b = tie.station_a, tie.station_b
        if prime[a] >= prime[b]:
            prime[a] -= shift
            prime[b] += shift
        else:
            prime[b] -= shift
            prime[a] += shift
    return prime


def _dc_flow(graph: nx.Graph, injections: dict[str, float]) -> dict[tuple, float]:
    """简化直流法:各连通分量选参考节点(优先GRID220),化简B·θ=P求解(去参考行列),线路潮流=Δθ/x。"""
    flows: dict[tuple, float] = {}
    for comp in nx.connected_components(graph):
        nodes = sorted(comp)
        ref = GRID220 if GRID220 in nodes else nodes[0]
        others = [n for n in nodes if n != ref]
        if not others:
            continue
        idx = {n: i for i, n in enumerate(others)}
        n = len(others)
        b_mat = np.zeros((n, n))
        p_vec = np.array([injections.get(node, 0.0) for node in others])
        sub = graph.subgraph(comp)
        for u, v, attrs in sub.edges(data=True):
            b = 1.0 / attrs["x"]
            if u in idx:
                b_mat[idx[u], idx[u]] += b
            if v in idx:
                b_mat[idx[v], idx[v]] += b
            if u in idx and v in idx:
                b_mat[idx[u], idx[v]] -= b
                b_mat[idx[v], idx[u]] -= b
        theta_others = np.linalg.solve(b_mat, p_vec)
        theta = {ref: 0.0, **{node: theta_others[idx[node]] for node in others}}
        for u, v, attrs in sub.edges(data=True):
            flows[(u, v)] = (theta[u] - theta[v]) / attrs["x"]
    return flows


def run_n1(data: ScenarioData, solution: Any, snapshots: list[int] | None = None) -> pd.DataFrame:
    """合成网架 DC 潮流 N-1 枚举。枚举对象=每回线路(多回按n_channels逐回
    退化,非整条边删除)+每台主变(简化为站净注入/失去最大单台后剩余容量,
    不做潮流重分布)。snapshots 默认=[全年P+峰, 全年P-峰]小时序号(0..8759)。
    返回 DataFrame(element_id, snapshot, loading_pct);>100 为越限,M1 判据
    仅要求跑通+结构正确,允许越限行如实输出。"""
    sol = _normalize_solution(solution)
    total = data.pnet.sum(axis=1)
    fwd_idx, rev_idx = int(total.values.argmax()), int(total.values.argmin())
    if snapshots is None:
        snapshots = [fwd_idx, rev_idx]
    graph = build_synthetic_grid(data)
    xfmr_rows = _transformer_elements(data)
    records: list[dict] = []
    for t in snapshots:
        prime = _pnet_prime_at(data, sol, t, fwd_idx, rev_idx)
        injections = {s: -float(prime[s]) for s in prime.index}
        for u, v, attrs in list(graph.edges(data=True)):
            n_ch = attrs["n_channels"]
            base_id = attrs["element_id"]
            for c in range(n_ch):
                trial = graph.copy()
                if n_ch == 1:
                    trial.remove_edge(u, v)
                    eid = base_id
                else:
                    remain = n_ch - 1
                    trial[u][v]["rating_mw"] = attrs["rating_mw"] * remain / n_ch
                    trial[u][v]["x"] = attrs["x"] * n_ch / remain
                    eid = f"{base_id}_c{c + 1}"
                flows = _dc_flow(trial, injections)
                worst = 0.0
                for (uu, vv), flow_mw in flows.items():
                    rating = trial[uu][vv]["rating_mw"]
                    if rating > 0:
                        worst = max(worst, abs(flow_mw) / rating * 100.0)
                records.append({"element_id": eid, "snapshot": t, "loading_pct": worst})
        for eid, sid, max_unit in xfmr_rows:
            st = data.stations[sid]
            remaining = st.cap_mva - max_unit + float(sol["expand_mva"].get(sid, 0.0))
            load = abs(float(prime[sid]))
            pct = load / remaining * 100.0 if remaining > 0 else float("inf")
            records.append({"element_id": eid, "snapshot": t, "loading_pct": pct})
    return pd.DataFrame.from_records(records, columns=["element_id", "snapshot", "loading_pct"])
