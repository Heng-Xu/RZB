"""检验新增输入与物理量一致，价格扰动保持原技术约束。"""
import numpy as np
import pytest
from . import model


def parameters(**extra):
    return dict(eta=2., energy_penetration=.4, growth_rate=.04, cable_fraction=.1,
                initial_transfer_fraction=.4, h95_h=4, diversity=1.1,
                line_price=1., storage_price=1., **extra)


@pytest.mark.parametrize('eta,energy,h',[(0,0,1),(.5,.10,2),(1,.25,8),(2,.4,4),(3,.65,6)])
def test_annual_energy_and_absolute_peak_duration(eta,energy,h):
    cert=model.profile(eta,energy,h)
    load,generation,blocks=model._curve(eta,cert['amplitude'],h)
    assert len(load)==len(generation)==8760
    assert abs(generation.sum()/load.sum()-energy)<1e-10
    net=load-generation;mask=abs(net)>=.95*abs(net).max()
    edges=np.diff(np.r_[False,mask,False].astype(int))
    assert max(np.flatnonzero(edges==-1)-np.flatnonzero(edges==1))==h
    assert load.max()==1 and generation.max()<=eta+1e-10
    assert abs(max(-net.min(),0)-cert['reverse_peak_per_unit'])<1e-10


def test_inconsistent_source_energy_is_rejected():
    with pytest.raises(ValueError):model.profile(0,.1,4)
    with pytest.raises(ValueError):model.profile(.5,.4,4)


def test_prices_preserve_all_technical_constraints():
    a=model.make_input(parameters())
    p=parameters();p.update(line_price=1.3,storage_price=.7)
    b=model.make_input(p)
    ma,_=model.locked.build(a);mb,_=model.locked.build(b)
    for name in ['entries','constraint_lower','constraint_upper','lower_bounds','upper_bounds','integrality']:
        assert getattr(ma,name)==getattr(mb,name),name
    assert a['line_cost']*1.3==b['line_cost']
    assert not np.array_equal(ma.costs,mb.costs)


def test_actual_solve_and_independent_dispatch():
    p=parameters();p.update(gap=1e-7,seconds=10)
    r=model.solve(p)
    assert r['verified']
    assert model.independent_lp_check(p,r['units'],r['modules'],r['built'])['verified']
    assert r['profile_certificate']['h95_h']==r['support_duration_h']
