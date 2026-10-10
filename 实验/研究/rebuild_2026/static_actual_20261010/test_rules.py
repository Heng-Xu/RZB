"""核查被动超限析取边界和实际年度标定。"""
import json

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix

from ..annual_no_tie_investment_submodel import LinearModel
from .run import OUT, load_scenes, retain_existing_upper


def feasible(previous, current, threshold, variable_previous):
    m=LinearModel(); c=m.variable(0,upper=6000,integer=0)
    m.constraint({c:1},current,current)
    p={}
    if variable_previous:
        v=m.variable(0,upper=6000,integer=0);m.constraint({v:1},previous,previous);p={v:1}
    retain_existing_upper(m,{c:1},p,previous,threshold,6000)
    m.constraint({c:1},lower=previous)
    rr,cc,vv=zip(*m.entries)
    a=coo_matrix((vv,(rr,cc)),shape=(len(m.constraint_lower),len(m.costs))).tocsr()
    r=milp(np.array(m.costs),integrality=np.array(m.integrality),
           bounds=Bounds(m.lower_bounds,m.upper_bounds),
           constraints=LinearConstraint(a,m.constraint_lower,m.constraint_upper))
    return r.success


def test_passive_upper_exact_disjunction():
    for variable in (False,True):
        for previous,threshold in [(2900,2864.739954),(1564,1522.463606),(2900,3084.433498)]:
            for current in [previous-1,previous,previous+1,threshold,threshold+1]:
                expected=previous-1e-7<=current<=max(previous,threshold)+1e-7
                assert feasible(previous,current,threshold,variable)==expected


def test_official_static_scenes_and_fixed_baseline():
    for region,baseline in [('city',2900),('pizhou',1463.5)]:
        inp=json.loads((OUT/region/'inputs.json').read_text())
        scenes=load_scenes(OUT/region,inp)
        assert inp['initial_capacity_mva']==baseline
        assert inp['annual_observed_peak_mw']['2023'] != inp['initial_peak_mw']*(1+inp['growth_rate'])**2
        assert all(abs(p[0].sum()-inp['annual_observed_peak_mw'][str(y)])<1e-5 for y,p in scenes.items())
        if region=='city':
            assert not any(e['existing'] for e in inp['network']['edges'])
            assert all(e['basis'].startswith('规划假设') for e in inp['network']['edges'])
