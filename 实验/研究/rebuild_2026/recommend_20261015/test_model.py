"""固定年度转供比例、未建通道及规划选择条件的机制检查。"""
import numpy as np

from . import model as m


def test_fixed_schedule_scales_with_source_and_does_not_use_unbuilt_line():
    inp,scenes,_=m.prepare();lp=m.OperatingLP(inp);units=np.full((len(inp['stations']),3),80.);units[:,2]=0.
    n=np.zeros(len(units));p=np.full(len(units),20.)
    existing=next(arc for arc in lp.arcs if arc[1]['existing'])
    key=(existing[1]['id'],existing[2]);fractions={key:.001}
    a=lp.dispatch_fixed(p,lp.prepared(p,2022,units,n,set()),-1,fractions)
    b=lp.dispatch_fixed(p/2,lp.prepared(p/2,2022,units,n,set()),-1,fractions)
    assert a['verified'] and b['verified'] and abs(a['total_mw']-2*b['total_mw'])<1e-10
    new=next(arc for arc in lp.arcs if not arc[1]['existing'])
    r=lp.dispatch_fixed(p,lp.prepared(p,2022,units,n,set()),-1,{(new[1]['id'],new[2]):.001})
    assert not r['verified']


def test_selected_case_keeps_objective_and_all_common_security_rows():
    inp,scenes,_=m.prepare();selected={(y,0,-1) for y in inp['years']}
    a,am=m.build(inp,scenes,'elastic_free',selected)
    ref={y:dict(capacity_mva=1700.,storage_mwh=30.1,cumulative_lines=15) for y in inp['years']}
    b,bm=m.build(inp,scenes,'elastic_selected',selected,ref)
    assert a.costs==b.costs and a.integrality==b.integrality
    assert b.entries[:len(a.entries)]==a.entries
    assert b.constraint_lower[:len(a.constraint_lower)]==a.constraint_lower
    assert b.constraint_upper[:len(a.constraint_upper)]==a.constraint_upper
    assert len(b.constraint_lower)-len(a.constraint_lower)==12
