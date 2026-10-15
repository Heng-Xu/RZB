"""验证共同运行约束的物理作用，防止正常储能和故障转接误放开。"""
import copy
import numpy as np

from . import cases as c


def setup(policy):
    inp,scenes,_=c.prepare(policy)
    units=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]);n=np.full(len(units),10000)
    lp=c.OperatingLP(inp);p=scenes[2022][0]
    return inp,lp,lp.prepared(p,2022,units,n,set()),units


def test_normal_operation_does_not_claim_emergency_battery_power():
    inp,lp,prepared,units=setup('standby')
    _,bounds,full,largest,bp,bn=lp.bounds_for(prepared,-1)
    assert np.all(bp==0.) and np.allclose(full+bn,.8*.95*units.sum(axis=1))
    assert all(high==0. for low,high in bounds)
    _,_,_,_,fault_bp,fault_bn=lp.bounds_for(prepared,0)
    assert np.all(fault_bp>0.) and fault_bn[0]>0.


def test_local_contingency_blocks_healthy_to_healthy_reconfiguration():
    inp,lp,prepared,units=setup('local_standby')
    _,bounds,*_=lp.bounds_for(prepared,0)
    for arc,(_,upper) in zip(lp.arcs,bounds):
        if 0 not in (arc[5],arc[6]):assert upper==0.
    assert any(upper>0 for arc,(_,upper) in zip(lp.arcs,bounds) if 0 in (arc[5],arc[6]))


def test_transfer_margin_applies_to_each_station_in_each_year():
    ref,_,_=c.prepare('standby');margin,_,_=c.prepare('transfer80')
    for y in ref['existing_transfer_budget_by_year_mw']:
        for sid,v in ref['existing_transfer_budget_by_year_mw'][y].items():
            assert abs(margin['existing_transfer_budget_by_year_mw'][y][sid]-.8*v)<1e-10
