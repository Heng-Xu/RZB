"""回归关键机制：逐站上限、比较约束及小主变+第三台的N-1。"""
import copy
import json

import highspy
import numpy as np
from scipy.sparse import coo_matrix

from . import cases, matrix


def test_station_rate_is_year_specific_and_capped_by_source_J():
    inp, scenes, root = cases.prepare('pizhou', 'compressed')
    byid = {r['station']: r for r in cases.old.station_evidence(inp)}
    lp = cases.StationLP(inp)
    units = np.array([s['initial_units'] + [0.] for s in inp['stations'].values()])
    for y in inp['years']:
        ready = lp.prepared(scenes[y][0], y, units, np.zeros(len(units)), set())
        for j, sid in enumerate(inp['stations']):
            r = byid[sid]
            expected = min(r['transferable_mw'], (r['source_fraction'] or 0.) * max(0., scenes[y][:, j].max()))
            assert abs(ready[0][-len(units) + j] - expected) < 1e-8


def test_target_does_not_change_economic_objective_or_remove_safety_rows():
    inp, scenes, root = cases.prepare('pizhou', 'compressed')
    selected = {(y, 0, -1) for y in inp['years']}
    target = {y: dict(capacity_mva=1704., storage_mwh=48.805, cumulative_lines=15) for y in inp['years']}
    free, fm = cases.build(inp, scenes, 'elastic_free', selected)
    chosen, cm = cases.build(inp, scenes, 'elastic_target', selected, target)
    assert fm == cm
    for key in ('costs', 'lower_bounds', 'upper_bounds', 'integrality'):
        assert getattr(free, key) == getattr(chosen, key)
    assert chosen.entries[:len(free.entries)] == free.entries
    assert chosen.constraint_lower[:len(free.constraint_lower)] == free.constraint_lower
    assert chosen.constraint_upper[:len(free.constraint_upper)] == free.constraint_upper
    assert len(chosen.constraint_upper) - len(free.constraint_upper) == 12
    assert chosen.constraint_lower[len(free.constraint_lower)] == 1704.5
    assert chosen.constraint_upper[-1] == 14


def test_normal_reverse_80_percent_is_not_applied_twice_after_failure():
    inp,scenes,root=cases.prepare('pizhou','compressed')
    lp=cases.StationLP(inp);units=np.full((len(inp['stations']),3),50.);units[:,2]=0.
    prepared=lp.prepared(scenes[2022][0],2022,units,np.zeros(len(units)),set())
    common,bounds,full,largest,bp,bn=lp.bounds_for(prepared,0)
    assert abs(full[0]-largest[0]+bn[0]-47.5)<1e-8
    assert abs(full[1]+bn[1]-76.)<1e-8


def fixed_tiny_case(last_demand):
    inp = matrix.old.make_input(dict(eta=0., growth_rate=0., cable_fraction=.1,
        initial_transfer_fraction=.1, support_duration_h=2., diversity=1.))
    inp['edges'] = []
    inp['gross'] = np.array([[5., 5., 5., 5., last_demand]])
    inp['generation'] = np.zeros((1, 5)); inp['net'] = inp['gross'].copy()
    inp['thermal'] = np.full(10, 100.); inp['receiver_headroom'] = np.full(10, 100.)
    m, meta = matrix.build(inp, 'greenfield')
    for (s, sl, r), v in meta['units'].items():
        m.lower_bounds[v] = m.upper_bounds[v] = float(r == 31.5)
    for s, v in meta['third'].items(): m.lower_bounds[v] = m.upper_bounds[v] = float(s == 4)
    for v in meta['modules'].values(): m.upper_bounds[v] = 0.
    rr, cc, vv = zip(*m.entries)
    a = coo_matrix((vv, (rr, cc)), shape=(len(m.constraint_lower), len(m.costs))).tocsr()
    lp = highspy.HighsLp(); lp.num_col_, lp.num_row_ = a.shape[1], a.shape[0]
    lp.col_cost_, lp.col_lower_, lp.col_upper_ = m.costs, m.lower_bounds, m.upper_bounds
    lp.row_lower_, lp.row_upper_ = m.constraint_lower, m.constraint_upper
    lp.integrality_ = [highspy.HighsVarType.kInteger if v else highspy.HighsVarType.kContinuous for v in m.integrality]
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = a.indptr, a.indices, a.data
    h = highspy.Highs(); h.setOptionValue('log_to_console', False); h.setOptionValue('threads', 1)
    h.passModel(lp); h.run()
    return h.getModelStatus()


def test_n1_removes_50_mva_third_unit_when_it_is_the_largest():
    assert fixed_tiny_case(65.) == highspy.HighsModelStatus.kInfeasible
    assert fixed_tiny_case(59.85) == highspy.HighsModelStatus.kOptimal


def test_greenfield_charges_all_transformers_and_has_no_500_mva_stock_floor():
    inp = matrix.old.make_input(dict(eta=.5, growth_rate=.04, cable_fraction=.1,
        initial_transfer_fraction=.4, support_duration_h=2., diversity=1.1))
    m, meta = matrix.build(inp, 'greenfield')
    assert min(r for s, sl, r in meta['units']) == 31.5
    assert all(m.costs[v] > 0. for v in meta['units'].values())
    original, original_meta = matrix.build(inp, 'stock')
    assert min(r for s, sl, r in original_meta['units']) == 50.
    assert all(original.costs[v] == 0. for (s, sl, r), v in original_meta['units'].items() if r == 50.)
