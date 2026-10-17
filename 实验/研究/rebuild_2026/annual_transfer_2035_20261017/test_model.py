"""约束边界与源荷绑定的实质性回归。"""
import copy

import numpy as np
import pytest

from . import model as m, prepare as p
from .reserve import prefer_ratings


def toy():
    station=lambda:dict(forward_duration_h=2,reverse_duration_h=2)
    return dict(stations={'A':station(),'B':station()},block_count={'A':4,'B':4},
        max_blocks_per_feeder_group=5,annual_observed_peak_mw={'2025':20.},
        existing_transfer_budget_by_year_mw={'2025':{'A':0.,'B':0.}},
        network=dict(feeders={f:dict(station=s,thermal_mw=100.,maximum_load_proxy_2025_mw=5.)
            for f,s in [('a','A'),('b','B')]},edges=[dict(id='paid',a='a',b='b',station_a='A',station_b='B',
                capacity_mw=20.,existing=False,bidirectional=False,source_section_fraction=1.)]))


def test_signed_block_moves_gross_load_and_pv_together():
    inp=toy();d=np.array([[1.,2.],[12.,1.]]);pv=np.array([[9.,0.],[0.,0.]])
    power=d-pv
    r,bad=m.verify(inp,power,2025,np.array([[10.,10.,0.],[10.,10.,0.]]),np.zeros(2),{'paid'},{0:1},{0:1})
    assert not bad
    records={v['failed']:v for v in r['records']}
    # 正常转走A四分之一区段，反向净负荷由-8变-6；A事故再转四分之一，12变6。
    assert records['正常']['minimum_margin_mw']==pytest.approx(9.2)
    assert records['A']['minimum_margin_mw']==pytest.approx(3.5)
    # B事故仍保留正常供区，不能额外动用健康A的追加切换。
    assert records['B']['minimum_margin_mw']==pytest.approx(5.5)


def test_duplicate_block_credit_is_rejected():
    with pytest.raises(AssertionError):
        m.verify(toy(),np.array([[12.,1.]]),2025,np.full((2,3),100.),np.zeros(2),{'paid'},{0:3},{0:2})


def test_unbuilt_paid_path_has_no_credit():
    with pytest.raises(AssertionError):
        m.verify(toy(),np.array([[12.,1.]]),2025,np.full((2,3),100.),np.zeros(2),set(),{0:1},{})


def test_forecast_nodes_and_floors_are_preserved():
    for region,end in [('city',4150.),('pizhou',2293.)]:
        series=p.forecasts(region);assert series[-1]['forecast_load_mw']==end
        assert series[-1]['pv_factor']==pytest.approx(1840/709)
        inp,powers=p.load(region)
        assert list(sorted(powers))==list(range(2021,2036))
        assert inp['initial_capacity_mva']==(3113.5 if region=='city' else 2027.)
        assert powers[2025].sum(axis=1).max()==pytest.approx(inp['annual_observed_peak_mw']['2025'])
        assert inp['annual_observed_peak_mw']['2035']==pytest.approx(inp['annual_observed_peak_mw']['2025']*series[-1]['load_factor'])
        old=np.array([s['initial_units']+[0.] for s in inp['stations'].values()])
        mm,meta,_=m.build(inp,powers[2022],2022,'rigid',old,np.zeros(len(old),int),set(),np.zeros((len(old),2),bool),set())
        total=p.base.old.old.base.previous.capacity_terms(inp,meta,2022)
        target=inp['common_floor_by_year']['2022']*inp['annual_observed_peak_mw']['2022']
        assert any({c:v for rr,c,v in mm.entries if rr==i}==total and lo==target for i,lo in enumerate(mm.constraint_lower))
        assert meta['network_flows']==[]
        assert all(not meta['arcs'][k]['existing'] for k in meta['normal_blocks'])
        assert all(mm.integrality[v] for v in meta['normal_blocks'].values())


def test_capacity_preference_uses_whole_rating_and_respects_budget():
    inp=dict(new_ratings=[31.5,50.,63.,80.],transformer_price_10k_per_purchased_mva=1.,
             cost_factors={'transformer':{'2025':1.}})
    before=np.array([[50.,80.,0.]])
    result,record=prefer_ratings(inp,before,np.array([[True,False]]),13.,2025)
    assert np.array_equal(result,[[63.,80.,0.]])
    assert record['incremental_npv_10k']==13. and record['secondary_n1_surviving_gain_mva']==13.
    low,_=prefer_ratings(inp,before,np.array([[True,False]]),12.99,2025)
    assert np.array_equal(low,before)


def test_retained_transformer_is_never_purchased_twice_for_reserve():
    inp=dict(new_ratings=[31.5,50.,63.,80.],transformer_price_10k_per_purchased_mva=1.,
             cost_factors={'transformer':{'2025':1.}})
    before=np.array([[63.,80.,0.]])
    result,record=prefer_ratings(inp,before,np.array([[False,False]]),1000.,2025)
    assert np.array_equal(result,before) and record['extra_capacity_mva']==0.
