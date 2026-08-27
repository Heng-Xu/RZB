"""Task 4 测试:src/links_sigma.py 联络参数聚合 + A_NTC(最大流)。

覆盖简报 Step 1 断言:
1. 手工 3 站微网:站1 供给足量(非绑定)、站2 裕度15、站3 裕度10,通道各12
   → maxflow=22(被通道+受端裕度封顶:min(12,15)+min(12,10)=12+10=22)。
   站1 自身裕度设为 0,避免"源=汇同站"的自我吸收退化路径掩盖联络封顶。
2. forbidden 联络不入图(即使容量很大也不参与,结果不变)。
3. d_struct/sigma 聚合值与 ties.csv 手算一致(真实合成数据,S01/S04)。
4. sigma 截断上限 SIGMA_CAP 生效(构造同站两条联络之和 > 0.6)。
5. 合成数据上 a_ntc('rev') 在反向峰时刻 >= 1 个分区 > 0(判据,若为0记为发现而非强行调整)。
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.io_loader import ScenarioData, load_scenario
from src.links_sigma import PEER_MARGIN_PROXY, SIGMA_CAP, a_ntc, build_linkset
from src.net_model import Station, TiePair, Transformer, Zone

ROOT = Path(__file__).parents[1]


# ---------------------------------------------------------------------------
# 手工 3 站微网(Step 1)
# ---------------------------------------------------------------------------


def _make_microgrid(extra_ties: list[TiePair] | None = None) -> ScenarioData:
    """3 站单分区:S1 供给非绑定(裕度0),S2 裕度15,S3 裕度10,通道各12。"""
    st1 = Station("S1", "X", "Z1", "urban", [Transformer("S1", "1", 30.0, "split")])
    st2 = Station("S2", "X", "Z1", "urban", [Transformer("S2", "1", 15.0, "split")])
    st3 = Station("S3", "X", "Z1", "urban", [Transformer("S3", "1", 10.0, "split")])
    zone = Zone("Z1", "X", "urban", [st1, st2, st3])

    ties = [
        TiePair("T1", "S1", "S2", 1, "LGJ-150", 12.0, 0.1, 0.1, "loop", False),
        TiePair("T2", "S1", "S3", 1, "LGJ-150", 12.0, 0.1, 0.1, "loop", False),
    ]
    if extra_ties:
        ties = ties + extra_ties

    # t=0:S1 供给=30(>=22,非绑定,恰好等于 S1 自身 cap → 裕度0,不会自我吸收)
    # S2/S3 自身无正向需求(供给=0),仅作受端(裕度=各自 cap)
    pnet = pd.DataFrame({"S1": [30.0], "S2": [0.0], "S3": [0.0]})

    return ScenarioData(
        zones={"Z1": zone},
        stations={"S1": st1, "S2": st2, "S3": st3},
        ties=ties,
        pnet=pnet,
        pv_capacity=pd.Series({"S1": 0.0, "S2": 0.0, "S3": 0.0}),
        params={},
    )


def test_manual_microgrid_maxflow_capped_by_channels():
    data = _make_microgrid()
    links = build_linkset(data)
    result = a_ntc(data, links, t_idx=0, direction="fwd")
    assert result.loc["Z1"] == pytest.approx(22.0)


def test_no_self_absorption_fwd():
    """孤立健康站(pnet>0 且 margin>0,无任何联络)不应贡献 a_ntc('fwd')。

    节点拆分修复前:该站会同时挂 s->X 与 X->t 边,自身即构成 s->X->t
    的两跳直通路径,不经任何联络边即可产生流量(自吸收缺陷)。
    修复后:X_src 与 X_dst 之间无边,该路径不存在,分区流量应为 0。
    """
    st_iso = Station("ISO", "X", "Z1", "urban", [Transformer("ISO", "1", 100.0, "split")])
    zone = Zone("Z1", "X", "urban", [st_iso])
    data = ScenarioData(
        zones={"Z1": zone},
        stations={"ISO": st_iso},
        ties=[],  # 无任何联络
        pnet=pd.DataFrame({"ISO": [40.0]}),  # supply=40>0, margin=100-40=60>0
        pv_capacity=pd.Series({"ISO": 0.0}),
        params={},
    )
    links = build_linkset(data)
    assert links.ties == []

    result = a_ntc(data, links, t_idx=0, direction="fwd")
    assert result.loc["Z1"] == pytest.approx(0.0)


def test_forbidden_tie_excluded_from_flow_and_linkset():
    forbidden = TiePair("T3", "S2", "S3", 1, "LGJ-240", 100.0, 0.5, 0.5, "forbidden", False)
    data = _make_microgrid(extra_ties=[forbidden])
    links = build_linkset(data)

    assert all(t.tie_id != "T3" for t in links.ties)
    assert len(links.ties) == 2

    result = a_ntc(data, links, t_idx=0, direction="fwd")
    assert result.loc["Z1"] == pytest.approx(22.0)  # 未被 forbidden 边的大容量抬高


def test_sensitive_tie_excluded_from_linkset():
    sensitive = TiePair("T4", "S2", "S3", 1, "LGJ-240", 100.0, 0.5, 0.5, "loop", True)
    data = _make_microgrid(extra_ties=[sensitive])
    links = build_linkset(data)
    assert all(t.tie_id != "T4" for t in links.ties)


# ---------------------------------------------------------------------------
# sigma 截断上限(SIGMA_CAP)
# ---------------------------------------------------------------------------


def test_sigma_cap_clips_overlapping_ties():
    st_a = Station("A", "X", "Z1", "urban", [Transformer("A", "1", 50.0, "split")])
    st_b = Station("B", "X", "Z1", "urban", [Transformer("B", "1", 50.0, "split")])
    zone = Zone("Z1", "X", "urban", [st_a, st_b])
    ties = [
        TiePair("T1", "A", "B", 1, "LGJ-150", 10.0, 0.4, 0.1, "loop", False),
        TiePair("T2", "A", "B", 1, "LGJ-150", 10.0, 0.5, 0.1, "loop", False),
    ]
    data = ScenarioData(
        zones={"Z1": zone},
        stations={"A": st_a, "B": st_b},
        ties=ties,
        pnet=pd.DataFrame({"A": [0.0], "B": [0.0]}),
        pv_capacity=pd.Series({"A": 0.0, "B": 0.0}),
        params={},
    )
    links = build_linkset(data)
    # 0.4 + 0.5 = 0.9 > SIGMA_CAP,应截断
    assert links.sigma.loc["A"] == pytest.approx(SIGMA_CAP)
    assert links.sigma.loc["B"] == pytest.approx(SIGMA_CAP)


# ---------------------------------------------------------------------------
# 真实合成数据:d_struct / sigma 手算对照
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def scenario():
    return load_scenario(ROOT)


@pytest.fixture(scope="module")
def linkset(scenario):
    return build_linkset(scenario)


def test_linkset_usable_tie_count(linkset):
    # 9条 ties:T09 forbidden、T01/T08 sensitive → usable 共 6 条(见简报裁决)
    assert len(linkset.ties) == 6


def test_sigma_hand_check_S04(linkset):
    # S04 usable 联络:T04(S04-S06, sigma_load=0.2967)+ T06(S03-S04, sigma_load=0.1484)
    # T09(S04-S05)forbidden 已排除
    expected = 0.2967 + 0.1484
    assert linkset.sigma.loc["S04"] == pytest.approx(expected, rel=1e-6)


def test_d_struct_hand_check_S01(scenario, linkset):
    # S01 usable 联络:T03(S01-S02, n=1, ampacity=10.154)+ T05(S01-S03, n=2, ampacity=11.982)
    # cap_S01=cap_S02=cap_S03=100 → PEER_MARGIN_PROXY*cap = 50,均不封顶(通道容量更小)
    cap_s01 = scenario.stations["S01"].cap_mva
    t03 = 1 * 10.154
    t05 = 2 * 11.982
    expected = (min(t03, 100 * PEER_MARGIN_PROXY) + min(t05, 100 * PEER_MARGIN_PROXY)) / cap_s01
    assert linkset.d_struct.loc["S01"] == pytest.approx(expected, rel=1e-6)


def test_build_linkset_index_covers_all_stations(scenario, linkset):
    assert set(linkset.d_struct.index) == set(scenario.stations)
    assert set(linkset.sigma.index) == set(scenario.stations)


# ---------------------------------------------------------------------------
# a_ntc('rev') 反向峰判据
# ---------------------------------------------------------------------------


def test_a_ntc_rev_direction_validation(scenario, linkset):
    with pytest.raises(ValueError):
        a_ntc(scenario, linkset, t_idx=0, direction="sideways")


def test_a_ntc_rev_positive_at_reverse_peak(scenario, linkset):
    # 反向峰时刻:系统级 Σmax(-pnet,0) 最大的小时(确定性选取,非按分区单独挑)
    total_rev = (-scenario.pnet).clip(lower=0.0).sum(axis=1)
    t_idx = int(total_rev.to_numpy().argmax())

    result = a_ntc(scenario, linkset, t_idx=t_idx, direction="rev")
    assert (result > 0).sum() >= 1
