"""Task 3 测试:src/clr.py 双向容载比纯函数。

覆盖简报 Step 1 断言:
1. 手工序列 [10,-8,4]、cap=30 → p_fwd=10, p_rev=8, r=3.0, binding='forward'
2. 纯正向序列:binding=='forward' 且 r==r_fwd
3. 全负序列(纯返送):p_fwd=0 → r_fwd=inf
4. 手工序列(反向占优)验证正式 CLR 仍只使用正向峰值
5. 分区聚合回归测试:先逐时刻加总再取峰,不得用各站峰值相加(同时率内生)
6. compute_all 对合成数据输出 5 行,列结构正确

裁决记录(见 sdd/task-3-report.md):真实合成数据(data/synthetic)中五个分区
在全年 8760h 内均未出现 p_rev > p_fwd(乡镇高PV分区最大 prev/pfwd ≈ 0.68,
未达到 1.0),因此 compute_all 的真实数据用例只断言行数/列结构,不断言
某具体分区 binding=='reverse'——reverse 路径由本文件的手工构造序列覆盖。
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.clr import compute_all, compute_zone_clr
from src.io_loader import ScenarioData, load_scenario
from src.net_model import Station, Transformer, Zone

ROOT = Path(__file__).parents[1]


# ---------------------------------------------------------------------------
# compute_zone_clr:手工序列
# ---------------------------------------------------------------------------


def test_manual_sequence_forward_binding():
    s = pd.Series([10, -8, 4])
    r = compute_zone_clr(s, cap_mva=30)
    assert r.p_fwd == pytest.approx(10.0)
    assert r.p_rev == pytest.approx(8.0)
    assert r.r == pytest.approx(3.0)
    assert r.binding == "forward"


def test_pure_forward_sequence_r_equals_r_fwd():
    s = pd.Series([5, 3, 1])
    r = compute_zone_clr(s, cap_mva=10)
    assert r.p_rev == pytest.approx(0.0)
    assert r.binding == "forward"
    assert r.r == pytest.approx(r.r_fwd)


def test_all_negative_sequence_r_fwd_is_inf():
    s = pd.Series([-5, -3, -1])
    r = compute_zone_clr(s, cap_mva=10)
    assert r.p_fwd == pytest.approx(0.0)
    assert r.r_fwd == float("inf")
    assert r.binding == "reverse"


def test_reverse_dominant_sequence_keeps_reverse_as_diagnostic_only():
    s = pd.Series([4, -10, 2])
    r = compute_zone_clr(s, cap_mva=20)
    assert r.p_fwd == pytest.approx(4.0)
    assert r.p_rev == pytest.approx(10.0)
    assert r.binding == "reverse"
    assert r.r == pytest.approx(5.0)  # 正式 CLR = 20 / P_plus，不使用反向峰值


def test_contract_example_formal_clr_uses_positive_peak_only():
    r = compute_zone_clr(pd.Series([10.0, -20.0]), cap_mva=30.0)
    assert r.p_fwd == pytest.approx(10.0)
    assert r.p_rev == pytest.approx(20.0)
    assert r.r == pytest.approx(3.0)


def test_frozen_pre_intervention_denominator_ignores_storage_dispatch():
    base = compute_zone_clr(pd.Series([10.0, -20.0]), cap_mva=30.0)
    after_dispatch = compute_zone_clr(
        pd.Series([15.0, -5.0]),
        cap_mva=40.0,
        positive_peak_base=base.p_fwd,
    )
    assert after_dispatch.p_fwd == pytest.approx(15.0)  # 仍可单列措施后诊断峰值
    assert after_dispatch.r == pytest.approx(4.0)  # (30 + 10) / 冻结的 10 MW


def test_tie_breaks_forward():
    s = pd.Series([5, -5])
    r = compute_zone_clr(s, cap_mva=10)
    assert r.p_fwd == pytest.approx(5.0)
    assert r.p_rev == pytest.approx(5.0)
    assert r.binding == "forward"


# ---------------------------------------------------------------------------
# compute_all:分区聚合回归测试(先加总再取峰,不得用各站峰值相加)
# ---------------------------------------------------------------------------


def _make_two_station_zone(pnet_df: pd.DataFrame) -> ScenarioData:
    st_a = Station(
        station_id="A1", county="X", zone_id="Z1", area_type="urban",
        transformers=[Transformer("A1", "1", 50.0, "split")],
    )
    st_b = Station(
        station_id="A2", county="X", zone_id="Z1", area_type="urban",
        transformers=[Transformer("A2", "1", 50.0, "split")],
    )
    zone = Zone(zone_id="Z1", county="X", area_type="urban", stations=[st_a, st_b])
    return ScenarioData(
        zones={"Z1": zone},
        stations={"A1": st_a, "A2": st_b},
        ties=[],
        pnet=pnet_df,
        pv_capacity=pd.Series({"A1": 0.0, "A2": 0.0}),
        params={},
    )


def test_zone_aggregation_is_sum_then_peak_not_sum_of_peaks():
    # 两站峰值错峰:A1 在 t=0 达峰 10,A2 在 t=1 达峰 10,逐时刻和的峰值仅为 10
    # (而非两站峰值直接相加的 20)——验证同时率内生于聚合顺序。
    pnet_df = pd.DataFrame({"A1": [10, 0, 0], "A2": [0, 10, 0]})
    data = _make_two_station_zone(pnet_df)
    df = compute_all(data)
    assert df.loc["Z1", "p_fwd"] == pytest.approx(10.0)
    assert df.loc["Z1", "p_fwd"] < 10.0 + 10.0  # 明确排除"各站峰值相加"的错误实现
    assert df.loc["Z1", "cap_mva"] == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# compute_all:合成数据全量
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def scenario():
    return load_scenario(ROOT)


def test_compute_all_shape_and_columns(scenario):
    df = compute_all(scenario)
    assert df.shape[0] == 5
    assert set(df.index) == set(scenario.zones)
    assert list(df.columns) == [
        "county", "area_type", "cap_mva", "p_fwd", "p_rev", "r", "r_fwd", "binding",
    ]
    assert set(df["binding"]) <= {"forward", "reverse"}


def test_compute_all_cap_mva_matches_station_sum(scenario):
    df = compute_all(scenario)
    total_cap = sum(st.cap_mva for st in scenario.stations.values())
    assert df["cap_mva"].sum() == pytest.approx(total_cap)
