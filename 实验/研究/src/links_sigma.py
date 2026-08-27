"""计算层:10kV 联络参数聚合(结构联络度 d_struct / 可切分度 sigma)
+ 网络转移能力 A_NTC(分区级最大流,正/反两向)。

纯函数,不做 IO——ScenarioData 由调用方(io_loader.load_scenario)传入。
"""
from __future__ import annotations

from dataclasses import dataclass

import networkx as nx
import pandas as pd

from src.io_loader import ScenarioData
from src.net_model import TiePair

# 对端裕度代理系数(占位):d_struct 分子里"对端站可接纳容量"用 对端cap_mva * 该系数
# 近似替代逐时刻真实裕度(d_struct 是不含 t 的静态结构指标,无法读时序 pnet)。
# M2 若有更精细的对端可用容量估计模型,应替换此常数并重新标定全部结果。
PEER_MARGIN_PROXY = 0.5

# sigma 聚合截断上限:同站多条 usable 联络的 sigma_load 直接相加是保守近似
# (未考虑多条联络实际服务的负荷是否重叠/互斥)。M1 聚合近似,M2 应按各联络
# 负荷实际去向做分段真值分摊,替换此截断。
SIGMA_CAP = 0.6

_SENTINEL_SRC = "__A_NTC_SOURCE__"
_SENTINEL_SNK = "__A_NTC_SINK__"


@dataclass
class LinkSet:
    """Task 4 对外接口:联络参数聚合结果。"""

    ties: list[TiePair]     # 仅 usable(switch_mode != 'forbidden' 且非 sensitive)
    d_struct: pd.Series     # station_id → 结构联络度(Σmin(通道容量, 对端裕度代理)/本站cap_mva)
    sigma: pd.Series        # station_id → Σ可切分负荷比例(截断于 SIGMA_CAP)


def build_linkset(data: ScenarioData) -> LinkSet:
    """聚合全部 usable 联络的结构联络度与可切分度(双端站各计一次)。"""
    usable_ties = [t for t in data.ties if t.usable]
    station_ids = sorted(data.stations)

    d_struct = pd.Series(0.0, index=station_ids, name="d_struct")
    sigma = pd.Series(0.0, index=station_ids, name="sigma")

    for tie in usable_ties:
        a, b = tie.station_a, tie.station_b
        chan_cap = tie.n_channels * tie.ampacity_mw
        cap_a = data.stations[a].cap_mva
        cap_b = data.stations[b].cap_mva

        if cap_a > 0:
            d_struct.loc[a] += min(chan_cap, cap_b * PEER_MARGIN_PROXY) / cap_a
        if cap_b > 0:
            d_struct.loc[b] += min(chan_cap, cap_a * PEER_MARGIN_PROXY) / cap_b

        sigma.loc[a] += tie.sigma_load
        sigma.loc[b] += tie.sigma_load

    sigma = sigma.clip(upper=SIGMA_CAP)
    sigma.index.name = "station_id"
    d_struct.index.name = "station_id"

    return LinkSet(ties=usable_ties, d_struct=d_struct, sigma=sigma)


def _src_node(station_id: str) -> str:
    """站 X 的"源侧"图节点(承接 s->X_src 的供给边)。"""
    return f"{station_id}::src"


def _dst_node(station_id: str) -> str:
    """站 X 的"汇侧"图节点(承接 X_dst->t 的裕度边)。"""
    return f"{station_id}::dst"


def a_ntc(data: ScenarioData, links: LinkSet, t_idx: int, direction: str) -> pd.Series:
    """分区级网络转移能力上限(MW),按最大流估计。

    每站 X 拆两个图节点 X_src(源侧)/X_dst(汇侧),保证任何 s->t 路径必经
    一条联络边——节点拆分消除了"同站自我吸收"退化路径:
      - 源点 -> 该分区各站的 X_src,容量 = 该站 t_idx 时刻"可转出的全部正/反向功率"
        fwd: max(pnet[站,t], 0)   rev: max(-pnet[站,t], 0)
      - 每条 usable 联络 (X, Y) -> 两条有向边 X_src->Y_dst 与 Y_src->X_dst,
        容量均为 n_channels * ampacity_mw(X_src 与 X_dst 之间无直连边,同站
        供给不能绕过联络直接抵达自身裕度)
      - 受端站(区内站,或经联络触达的区外站)的 X_dst -> 汇点,容量 = 该站
        t_idx 时刻裕度
        fwd: max(cap_mva - pnet[站,t], 0)   rev: max(pnet[站,t], 0)(还能吃多少反向送入)

    **M1 简化声明**:源侧容量取该站全部正/反向功率,而非"超出自身容量的净
    缺口"(更精确的 max(pnet - k*cap, 0) 版本对 M1 过于复杂),因此本函数度量的
    是"通道 + 受端裕度"共同决定的转移能力**上限**,不代表实际会发生的转移量。
    节点拆分保证流量必经联络;双向满额为宽松上界(同一联络的两个方向各按
    n_channels*ampacity_mw 全额计容,未扣减对向占用),M2 收紧。

    跨分区联络:两端分属不同分区的联络边,双侧分区的流网络各自计入一次
    (受端站即使在区外,也可作为该侧网络的汇点候选)。
    """
    if direction not in ("fwd", "rev"):
        raise ValueError(f"direction must be 'fwd' or 'rev', got {direction!r}")

    pnet_t = data.pnet.iloc[t_idx]
    result: dict[str, float] = {}

    for zone_id in sorted(data.zones):
        zone_station_ids = {st.station_id for st in data.zones[zone_id].stations}
        graph = nx.DiGraph()

        for sid in zone_station_ids:
            p = float(pnet_t[sid])
            supply = max(p, 0.0) if direction == "fwd" else max(-p, 0.0)
            if supply > 0:
                graph.add_edge(_SENTINEL_SRC, _src_node(sid), capacity=supply)

        zone_ties = [
            tie
            for tie in links.ties
            if tie.station_a in zone_station_ids or tie.station_b in zone_station_ids
        ]
        for tie in zone_ties:
            a, b = tie.station_a, tie.station_b
            chan_cap = tie.n_channels * tie.ampacity_mw
            graph.add_edge(_src_node(a), _dst_node(b), capacity=chan_cap)
            graph.add_edge(_src_node(b), _dst_node(a), capacity=chan_cap)

        candidate_sinks = set(zone_station_ids)
        for tie in zone_ties:
            candidate_sinks.add(tie.station_a)
            candidate_sinks.add(tie.station_b)

        for sid in candidate_sinks:
            p = float(pnet_t[sid])
            cap_mva = data.stations[sid].cap_mva
            margin = max(cap_mva - p, 0.0) if direction == "fwd" else max(p, 0.0)
            if margin > 0:
                graph.add_edge(_dst_node(sid), _SENTINEL_SNK, capacity=margin)

        if _SENTINEL_SRC in graph and _SENTINEL_SNK in graph:
            flow_value, _ = nx.maximum_flow(graph, _SENTINEL_SRC, _SENTINEL_SNK)
        else:
            flow_value = 0.0
        result[zone_id] = flow_value

    s = pd.Series(result, name=f"a_ntc_{direction}")
    s.index.name = "zone_id"
    return s.reindex(sorted(data.zones))
