"""转供规则不得把新增投资、正常方式和事故方式混为一体。"""
import copy
import json

import numpy as np

from . import audit, probe


def setup(region='city'):
    inp,scenes,_=audit.base.prepare(region,'annual_2021')
    u=np.array([s['initial_units']+[0.] for s in inp['stations'].values()])
    n=np.zeros(len(u));built={next(e['id'] for e in inp['network']['edges'] if not e['existing'])}
    return inp,scenes,u,n,built


def test_free_normal_transfer_is_blocked_but_built_project_is_retained():
    inp,scenes,u,n,built=setup();inp=copy.deepcopy(inp);inp['audit_mode']='fault_only'
    lp=audit.RestrictedLP(inp);ready=lp.prepared(scenes[2025][0],2025,u,n,built)
    _,bounds,*_=lp.bounds_for(ready,-1)
    assert all(hi==0 for arc,(_,hi) in zip(lp.arcs,bounds) if arc[1]['existing'])
    assert any(hi>0 for arc,(_,hi) in zip(lp.arcs,bounds) if arc[1]['id'] in built)


def test_fault_only_policy_still_allows_existing_emergency_paths():
    inp,scenes,u,n,built=setup();inp=copy.deepcopy(inp);inp['audit_mode']='fault_only'
    lp=audit.RestrictedLP(inp);ready=lp.prepared(scenes[2025][0],2025,u,n,built)
    _,bounds,*_=lp.bounds_for(ready,0)
    assert any(hi>0 for arc,(_,hi) in zip(lp.arcs,bounds) if arc[1]['existing'])


def test_direct_fault_policy_closes_healthy_to_healthy_reconfiguration():
    inp,scenes,u,n,built=setup();inp=copy.deepcopy(inp);inp['audit_mode']='direct_fault'
    lp=audit.RestrictedLP(inp);ready=lp.prepared(scenes[2025][0],2025,u,n,built)
    _,bounds,*_=lp.bounds_for(ready,0)
    assert all(hi==0 for arc,(_,hi) in zip(lp.arcs,bounds) if 0 not in (arc[5],arc[6]))


def test_both_schemes_have_the_same_explicit_floor_and_run_restrictions():
    inp,scenes,*_=setup();inp=copy.deepcopy(inp);inp['years']=[2025];inp['common_floor']=1.6
    selected={(2025,0,-1),(2025,0,0)}
    for case in ['rigid','elastic_free']:
        native,meta=probe.build(inp,scenes,case,selected)
        assert native.constraint_lower[-1]==1.6*inp['annual_observed_peak_mw']['2025']
        edges={e['id']:e for e in inp['network']['edges']};ids=list(inp['stations'])
        for y,h,f,eid,d,v in meta['network_flows']:
            e=edges[eid]
            if (f<0 and e['existing']) or (f>=0 and ids[f] not in (e['station_a'],e['station_b'])):
                assert native.upper_bounds[v]==0.


def test_selected_line_simplification_preserves_cost_allowance_and_full_feasibility():
    folder=audit.REVIEW/'单年机制筛查/pizhou'
    ref=json.loads((folder/'elastic_free/summary.json').read_text())
    chosen=json.loads((folder/'elastic_engineering/summary.json').read_text())
    proof=json.loads((folder/'elastic_engineering/independent_lp.json').read_text())
    assert chosen['common_floor']==ref['common_floor']
    assert chosen['cost_npv_10k']<=ref['cost_npv_10k']*1.05+1e-6
    assert chosen['annual'][0]['cumulative_lines']<ref['annual'][0]['cumulative_lines']
    assert proof['verified'] and all(r['verified'] for r in proof['records'])
    assert not chosen['solver']['accepted']
    assert chosen['selection']['cost_tolerance']==.05
