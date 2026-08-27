"""Task 6 tests: 方案A/B MILP(milp_planner.solve_scheme)。

模块级缓存 solve('A')/solve('B') 各求解一次(避免 pytest 重复求解)。
断言逐字来自 task-6-brief.md Step 1。
"""
from __future__ import annotations

from pathlib import Path

import pytest

from src.io_loader import load_scenario
from src.links_sigma import build_linkset
from src.milp_planner import solve_scheme
from src.typical_days import reduce_days

ROOT = Path(__file__).resolve().parents[1]

_data = load_scenario(ROOT, track="synthetic")
_links = build_linkset(_data)
_k = int(_data.params["milp"]["typical_days"])
_tdays = reduce_days(_data.pnet.sum(axis=1), _k)

_cache: dict[str, object] = {}


def solve(scheme: str):
    if scheme not in _cache:
        _cache[scheme] = solve_scheme(_data, _links, _tdays, scheme)
    return _cache[scheme]


def test_scheme_b_cheaper_or_equal():
    sa, sb = solve("A"), solve("B")
    assert sa.status == sb.status == "ok"
    assert sb.total_cost <= sa.total_cost + 1e-6  # B 是 A 的松弛


def test_redline_binds_somewhere():
    sa = solve("A")
    assert (sa.r_after <= 2.0 + 1e-6).all()  # A 全分区守线
    sb = solve("B")
    assert (sb.r_after > 2.0).any()  # 合成数据保证:至少1个高PV分区弹过2.0


def test_alpha_only_when_needed():
    sb = solve("B")
    assert (sb.alpha.values >= -1e-9).all() and (sb.alpha.values <= 0.30 + 1e-9).all()


def test_redline_cost_positive_and_shadow():
    """完成判据:红线代价严格 >0;方案A影子价格非 None 且 >0。"""
    sa, sb = solve("A"), solve("B")
    assert sb.total_cost < sa.total_cost  # 严格:合成数据制造出红线代价
    assert sa.shadow_r is not None and sa.shadow_r > 0


def test_no_peak_inflation():
    """方案A 不得靠"人为抬高峰值"来压容载比(跨任务修复:堵住抬峰演示路径)。

    红线线性化(milp_planner O6 单时刻钉法)只钉住分区基态绑定方向峰值时刻,
    优化器理论上可通过储能午间放电抬高该时刻反送峰(或晚峰充电抬正向峰)把
    R=cap/peak 人为压低。合成数据修复后基线 R 已 <=1.95、红线在基态成立,不再
    需要抬峰;本测试固化该性质:方案A 各分区措施后聚合峰值 max(P⁺',P⁻') 不得
    超过基线峰值×1.02(仅容忍数值噪声)。

    基线峰值与方案A的 r_after 取自同一批代表日(_rep_arrays(_data, _tdays)),
    口径一致:措施后峰值 = cap_after / r_after(milp_planner 内部同式)。
    """
    import numpy as np

    from src.milp_planner import _rep_arrays

    sa = solve("A")
    stations, _days, pnet, _pv, _load, _seasons, _weights = _rep_arrays(_data, _tdays)
    for zid in sorted(_data.zones):
        zst = [s.station_id for s in _data.zones[zid].stations]
        idx = [stations.index(s) for s in zst]
        base_peak = float(np.max(np.abs(pnet[idx].sum(axis=0))))
        cap_after = (sum(_data.stations[s].cap_mva for s in zst)
                     + float(sa.expand_mva[zst].sum()))
        post_peak = cap_after / float(sa.r_after[zid])
        assert post_peak <= base_peak * 1.02 + 1e-6, (
            f"{zid} 方案A措施后峰值 {post_peak:.2f}MW > 基线峰值 "
            f"{base_peak:.2f}MW ×1.02(优化器在人为抬峰压 R)"
        )
