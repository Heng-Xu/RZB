import copy
import json

import numpy as np

from . import capacity_run as base
from .run import calibrate
from .test_model import toy_input
from .transfer_diagnostic import DiagnosticLP,constrained_input


def test_station_caps_use_matched_source_mw_without_rescaling_the_graph():
    for region,count in (('city',26),('pizhou',20)):
        original=json.loads((base.OUT/region/'inputs.json').read_text())
        p=constrained_input(original,'station_caps')
        assert p['network']==original['network']
        assert p['initial_transfer_fraction']==original['initial_transfer_fraction']
        assert sum(r['matched'] for r in p['station_transfer_evidence'])==count
        for r in p['station_transfer_evidence']:
            assert p['existing_transfer_budget_mw'][r['station']]==min(r['original_budget_mw'],r['transferable_mw'])
        if region=='city':
            r=next(r for r in p['station_transfer_evidence'] if r['station']=='BDZ-00055')
            assert r['source_region']=='铜山' and r['transferable_mw']==21.5


def test_minimum_transfer_reports_only_required_flow():
    inp=calibrate(toy_input(),.67);lp=DiagnosticLP(inp)
    units=np.array([[50.,50.,0.],[50.,50.,0.]]);n=np.zeros(2)
    p=np.array([55.,10.]);prepared=lp.prepared(p,2022,units,n,set())
    result=lp.dispatch(p,prepared,0)
    assert abs(result['total_mw']-7.5)<1e-7
    assert abs(result['existing_mw']-7.5)<1e-7
    assert abs(result['net_shift_mw']-7.5)<1e-7
    assert lp.dispatch(p,prepared,-1)['total_mw']==0.


def test_normal_fixed_does_not_remove_emergency_transfer():
    inp=calibrate(toy_input(),.67)
    units=np.array([[50.,50.,0.],[50.,50.,0.]]);n=np.zeros(2)
    p=np.array([100.,10.]);lp=DiagnosticLP(inp)
    assert lp.check(p,lp.prepared(p,2022,units,n,set()),-1)['verified']
    fixed=copy.deepcopy(inp);fixed['normal_supply_area_fixed']=True;lp=DiagnosticLP(fixed)
    assert not lp.check(p,lp.prepared(p,2022,units,n,set()),-1)['verified']
    p=np.array([55.,10.]);assert lp.check(p,lp.prepared(p,2022,units,n,set()),0)['verified']
