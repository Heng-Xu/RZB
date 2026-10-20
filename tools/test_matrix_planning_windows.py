"""窗口规则、真实平台和完整采样分档的回归检查。"""
import itertools
from decimal import Decimal

import pandas as pd
import pytest

from matrix_planning_windows import records,window,middle_node,adjoining_windows
from check_report_policy import check_window_matrix


def test_width_and_rounding_are_independent_of_transfer_column():
    assert window(2.024)=='1.97～2.07'
    assert window(2.03)=='1.99～2.09'
    assert window(2.025)==window(2.025)
    for value in [1.36,1.915,2.5,3.112]:
        a,b=map(Decimal,window(value).split('～'))
        assert b-a==Decimal('.10') and a<=Decimal(str(value))<=b


def synthetic():
    return pd.DataFrame([{'年最大净负荷平均增长率':g,'分布式电源装机渗透率':e,
        '初始转供率':r,'电缆长度占比':c,'负荷分散系数':round(1.05+.02*k,2),
        '储能支撑持续时间_h':4,'容载比':2.0}
        for g,e,r,c,k in itertools.product([.02,.04,.07,.08],[1,2,3],[.3,.5,.7,.9],[.1,.3,.5],range(11))])


def test_full_design_counts_boundary_once_and_preserves_real_plateau():
    d=synthetic();cells=records(d)
    assert len(cells)==288 and sum(r['有效样本数'] for r in cells)==len(d)
    assert {r['分散节点数'] for r in cells if r['分散档']==0}=={6}
    assert {r['分散节点数'] for r in cells if r['分散档']==1}=={5}
    assert {r['推荐窗口'] for r in cells}=={'1.95～2.05'}


def test_missing_cell_must_not_be_filled():
    d=synthetic()
    d=d[~((d['年最大净负荷平均增长率']==.08)&(d['分布式电源装机渗透率']==3)&
           (d['初始转供率']==.9)&(d['电缆长度占比']==.5))]
    with pytest.raises(AssertionError,match='无有效节点'):records(d)


def test_window_cannot_be_centered_in_a_gap_between_equipment_solutions():
    assert middle_node([1.4,1.7])==1.7
    assert window(middle_node([1.4,1.7]))=='1.65～1.75'


def test_policy_rejects_wrong_width_and_accepts_overlapping_windows():
    check_window_matrix('| A | B | 1.95～2.05 | 1.95～2.05 | 1.90～2.00 | 1.85～1.95 |','示例')
    with pytest.raises(AssertionError,match='窗口宽度'):
        check_window_matrix('| A | B | 1.90～2.11 | 1.90～2.10 | 1.85～2.05 | 1.80～2.00 |','问题示例')


def test_close_levels_share_boundaries_and_include_actual_nodes():
    values=[2.005,1.983,1.956,1.956]
    bands=adjoining_windows(values)
    assert bands==['1.99～2.05','1.97～1.99','1.91～1.97','1.91～1.97']
    for value,band in zip(values,bands):
        low,high=map(float,band.split('～'));assert low<=value<=high
    assert adjoining_windows([2.,1.8,1.9,1.8])==['1.95～2.05','1.75～1.85','1.85～1.95','1.75～1.85']


def test_solver_rechecks_tight_capacity_boundary_without_relaxing_audit():
    from extend_matrix_scenarios import solve
    row=solve(dict(eta=2.75,growth_rate=0,support_duration_h=2,cable_fraction=.3,
                   initial_transfer_fraction=.2,diversity=1.07,node_purpose='数值残差回归'))
    assert row['verified'] and row['physical_check']['max_violation_mw']<1e-5
