"""转供率完整序列复核：存量改造与主变全部选配的费用优化分别计算。"""
import argparse
import copy
import hashlib
import itertools
import json
import math
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import highspy
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

from ..annual_no_tie_investment_submodel import LinearModel
from ..matrix_20261012 import model as old

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / '研究报告/试算/20261015_会后建模复核/推广'
CATALOG = (31.5, 50., 63., 80.)
REFERENCE = None


def reverse_rows(inp, m, meta):
    beta = inp['p'].get('normal_reverse_limit_fraction', .8)
    edges = {e['id']: e for e in inp['edges']}; flows = defaultdict(dict)
    for h, f, eid, direction, v in meta['flows']:
        e = edges[eid]; a, b = (e['a'], e['b']) if direction == 0 else (e['b'], e['a'])
        flows[h, f, a // 2][v] = -1.; flows[h, f, b // 2][v] = 1.
    for h in range(len(inp['gross'])):
        for failed in range(-1, 5):
            for s in range(5):
                if failed == s: continue
                terms = {v: beta * inp['p']['pf'] * r for (ss, sl, r), v in meta['units'].items() if ss == s}
                terms[meta['third'][s]] = beta * inp['p']['pf'] * 50.
                terms[meta['modules'][s]] = inp['storage_effective']
                terms.update(flows[h, failed, s])
                m.constraint(terms, lower=-float(inp['net'][h, s]))
    return m, meta


def build(inp, mode):
    if mode == 'stock':
        m, meta = old.build(inp)
        return reverse_rows(inp, m, meta)
    p = inp['p']; m = LinearModel(); units = {}; third = {}; modules = {}; built = {}
    factors = inp['factors']
    catalog = CATALOG if mode == 'greenfield' else (50., 63., 80.)
    for s in range(5):
        for sl in range(2):
            for rating in catalog:
                cost = rating * inp['transformer_cost_per_purchased_mva'] * factors['transformer']
                units[s, sl, rating] = m.variable(cost)
            m.constraint({units[s, sl, r]: 1. for r in catalog}, 1., 1.)
        m.constraint({v: r * (1 if sl == 0 else -1)
                      for (ss, sl, r), v in units.items() if ss == s}, upper=0.)
        third[s] = m.variable(inp['third_cost'] * factors['transformer'], upper=int(p['third']))
        max_power = float(np.max(abs(inp['net'][:, s]))) + float(inp['gross'].sum(axis=1).max())
        modules[s] = m.variable(inp['storage_unit_cost'] * p['storage_price'] * factors['storage'],
            upper=math.ceil(max_power / inp['storage_effective']) + 1 if p['storage'] else 0)
    for e in inp['edges']:
        if not e['existing']:
            built[e['id']] = m.variable(inp['line_cost'] * factors['line'], upper=int(e['capacity'] > 0))
    for s in range(5):
        m.constraint({built[e['id']]: 1. for e in inp['edges'] if e.get('new_bay_station') == s}, upper=p['spare_bays'])
    flowmeta = []
    for h, D in enumerate(inp['gross']):
        for failed in range(-1, 5):
            outgoing = defaultdict(dict); incoming = defaultdict(dict); netgroup = defaultdict(dict)
            existing = defaultdict(dict); new_incoming = defaultdict(dict)
            for e in inp['edges']:
                ev = []
                for direction in range(1 if e.get('dedicated') else 2):
                    a, b = (e['a'], e['b']) if direction == 0 else (e['b'], e['a'])
                    v = m.variable(0., upper=e['capacity'], integer=0); ev.append(v)
                    outgoing[a][v] = 1.; netgroup[a][v] = 1.
                    if e.get('dedicated'): new_incoming[b // 2][v] = -1.
                    else: incoming[b][v] = 1.; netgroup[b][v] = -1.
                    if e['existing']: existing[a // 2][v] = 1.
                    flowmeta.append((h, failed, e['id'], direction, v))
                terms = {v: 1. for v in ev}
                if not e['existing']: terms[built[e['id']]] = -e['capacity']
                m.constraint(terms, upper=e['capacity'] if e['existing'] else 0.)
            for f in range(10):
                native = D[f // 2] / 2.
                m.constraint(outgoing[f], upper=native)
                if p['receiver_budget']: m.constraint(incoming[f], upper=inp['receiver_headroom'][f])
                m.constraint(netgroup[f], lower=native - inp['thermal'][f], upper=native)
            for s in range(5):
                m.constraint(existing[s], upper=inp['existing_budget'][s])
                cap = {v: r for (ss, sl, r), v in units.items() if ss == s and not (failed == s and sl == 1)}
                cap[third[s]] = 50.
                variants = [cap]
                if failed == s:
                    # 允许小规格主变时，新增50MVA也可能成为最大一台。
                    variants.append({v: r for (ss, sl, r), v in units.items() if ss == s})
                station_netout = {**netgroup[2*s], **netgroup[2*s+1], **new_incoming[s]}
                for variant in variants:
                    for sign in (1., -1.):
                        terms = {v: p['pf'] * r for v, r in variant.items()}
                        terms[modules[s]] = inp['storage_effective']
                        for v, c in station_netout.items(): terms[v] = sign * c
                        m.constraint(terms, lower=sign * float(inp['net'][h, s]))
    return reverse_rows(inp, m, dict(units=units, third=third, modules=modules, built=built, flows=flowmeta))


def check_reverse(inp, ratings, modules, flows):
    grouped = defaultdict(list); edges = {e['id']: e for e in inp['edges']}
    for h, f, e, d, value in flows: grouped[h, f].append((e, d, value))
    worst = 0.; beta = inp['p'].get('normal_reverse_limit_fraction', .8)
    for h, p in enumerate(inp['net']):
        for f in range(-1, 5):
            served = p.copy()
            for eid, d, value in grouped[h, f]:
                e = edges[eid]; a, b = (e['a'], e['b']) if d == 0 else (e['b'], e['a'])
                served[a // 2] -= value; served[b // 2] += value
            available = beta * inp['p']['pf'] * ratings.sum(axis=1)
            if f >= 0: available[f] = inp['p']['pf'] * (ratings[f].sum() - ratings[f].max())
            worst = max(worst, float(np.max(-served - available - modules * inp['storage_effective'])))
    return max(0., worst)


def independent_lp_check(parameters, ratings, modules, chosen):
    """从设备和边重新组装LP，含正常80%和故障站N-1不过载。"""
    inp = old.make_input(parameters); ratings = np.array(ratings); modules = np.array(modules)
    arcs = [(e, d) for e in inp['edges'] for d in range(1 if e.get('dedicated') else 2)]; n = len(arcs)
    bay_counts = [sum(e.get('new_bay_station') == s and e['id'] in chosen for e in inp['edges']) for s in range(5)]
    if max(bay_counts) > inp['p']['spare_bays']: return dict(verified=False, worst='receiving bays')
    count = 0; worst = None; violation = 0.
    for h, D in enumerate(inp['gross']):
        for failed in range(-1, 5):
            out = np.zeros((10, n)); inc = np.zeros((10, n)); net = np.zeros((10, n))
            ex = np.zeros((5, n)); new_in = np.zeros((5, n))
            erows = {e['id']: np.zeros(n) for e in inp['edges']}; bounds = []
            for k, (e, d) in enumerate(arcs):
                a, b = (e['a'], e['b']) if d == 0 else (e['b'], e['a'])
                out[a, k] = 1.; net[a, k] = 1.; erows[e['id']][k] = 1.
                if e.get('dedicated'): new_in[b // 2, k] = -1.
                else: inc[b, k] = 1.; net[b, k] = -1.
                if e['existing']: ex[a // 2, k] = 1.
                bounds.append((0., e['capacity'] if e['existing'] or e['id'] in chosen else 0.))
            native = np.repeat(D / 2., 2); sn = net.reshape(5, 2, n).sum(axis=1) + new_in
            full = inp['p']['pf'] * ratings.sum(axis=1); available = full.copy()
            reverse = inp['p'].get('normal_reverse_limit_fraction', .8) * full
            if failed >= 0:
                available[failed] -= inp['p']['pf'] * ratings[failed].max()
                reverse[failed] = available[failed]
            support = modules * inp['storage_effective']
            rows = [out, -net, net, ex, sn, -sn]
            rhs = [native, inp['thermal'] - native, native, inp['existing_budget'],
                   inp['net'][h] + reverse + support, available + support - inp['net'][h]]
            if inp['p']['receiver_budget']: rows.append(inc); rhs.append(inp['receiver_headroom'])
            for e in inp['edges']:
                rows.append(erows[e['id']][None, :]); rhs.append(np.array([e['capacity']]))
            r = linprog(np.zeros(n), A_ub=np.vstack(rows), b_ub=np.concatenate(rhs), bounds=bounds, method='highs')
            count += 1
            if not r.success: worst = dict(scenario=h, failed=failed, status=int(r.status), message=r.message); break
            violation = max(violation, float(np.max(np.vstack(rows) @ r.x - np.concatenate(rhs))))
        if worst: break
    return dict(verified=worst is None, checked_pairs=count, worst=worst, max_violation_mw=max(0., violation))


def solve(parameters, mode='greenfield', warm=None):
    started = time.monotonic(); inp = old.make_input(parameters); m, meta = build(inp, mode)
    rr, cc, vv = zip(*m.entries)
    a = coo_matrix((vv, (rr, cc)), shape=(len(m.constraint_lower), len(m.costs))).tocsr()
    lp = highspy.HighsLp(); lp.num_col_, lp.num_row_ = a.shape[1], a.shape[0]
    lp.col_cost_, lp.col_lower_, lp.col_upper_ = m.costs, m.lower_bounds, m.upper_bounds
    lp.row_lower_, lp.row_upper_ = m.constraint_lower, m.constraint_upper
    lp.integrality_ = [highspy.HighsVarType.kInteger if v else highspy.HighsVarType.kContinuous for v in m.integrality]
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = a.indptr, a.indices, a.data
    h = highspy.Highs()
    for k, v in [('threads', 1), ('random_seed', 0), ('mip_rel_gap', parameters.get('gap', .001)),
                 ('time_limit', parameters.get('seconds', 20.)), ('log_to_console', False)]: h.setOptionValue(k, v)
    h.passModel(lp)
    if warm:
        values = {}
        for (s, sl, r), v in meta['units'].items(): values[v] = float(abs(warm['units'][s][sl] - r) < 1e-8)
        for s, v in meta['third'].items(): values[v] = warm['units'][s][2] / 50.
        for s, v in meta['modules'].items(): values[v] = warm['modules'][s]
        for eid, v in meta['built'].items(): values[v] = float(eid in warm['built'])
        h.setSolution(len(values), np.array(list(values), dtype=np.int32), np.array(list(values.values())))
    h.run(); info = h.getInfo(); raw = h.getSolution()
    row = dict(parameters, mode=mode, verified=False, elapsed_seconds=time.monotonic() - started,
        status=h.modelStatusToString(h.getModelStatus()), cost_lower=float(info.mip_dual_bound) if math.isfinite(info.mip_dual_bound) else None,
        relative_gap=float(info.mip_gap) if math.isfinite(info.mip_gap) else None,
        capacity_catalog_mva=list(CATALOG) if mode == 'greenfield' else [50., 63., 80.],
        stock_capacity_floor_mva=0. if mode == 'greenfield' else 500.,
        physical_minimum_capacity_mva=315. if mode == 'greenfield' else 500.,
        network_reference='相同的5站、基准负荷250MW、每站100MVA参考设备标定既有转供网络，规划正常和N-1逐工况重校核')
    if not raw.value_valid or info.primal_solution_status != 2: return row
    z = np.array(raw.col_value); az = a @ z; integers = np.array(m.integrality, dtype=bool)
    violation = max(0., float(np.max(np.array(m.constraint_lower) - az)), float(np.max(az - np.array(m.constraint_upper))),
        float(np.max(np.array(m.lower_bounds) - z)), float(np.max(z - np.array(m.upper_bounds))),
        float(np.max(abs(z[integers] - np.round(z[integers])))))
    assert violation < 1e-5, violation
    catalog = CATALOG if mode == 'greenfield' else (50., 63., 80.)
    ratings = np.array([[next(r for r in catalog if z[meta['units'][s, sl, r]] > .5) for sl in (0, 1)]
                        + [50. * round(z[meta['third'][s]])] for s in range(5)])
    modules = np.array([round(z[meta['modules'][s]]) for s in range(5)])
    chosen = {e for e, v in meta['built'].items() if z[v] > .5}
    flows = [(hh, f, e, d, float(z[v])) for hh, f, e, d, v in meta['flows'] if z[v] > 1e-7]
    check = old.check_dispatch(inp, ratings, modules, chosen, flows)
    assert check['violating_pairs'] == 0, check
    reverse_violation = check_reverse(inp, ratings, modules, flows)
    assert reverse_violation < 1e-5, reverse_violation
    check['normal_reverse_limit_fraction'] = inp['p'].get('normal_reverse_limit_fraction', .8)
    check['reverse_limit_violation_mw'] = reverse_violation
    bought = np.where(ratings[:, :2] > 50., ratings[:, :2], 0.).sum() if mode == 'stock' else ratings[:, :2].sum()
    raw_costs = dict(transformer=float(bought * inp['transformer_cost_per_purchased_mva'] + ratings[:, 2].sum() / 50. * inp['third_cost']),
        storage=float(modules.sum() * inp['storage_unit_cost'] * inp['p']['storage_price']), line=float(len(chosen) * inp['line_cost']))
    costs = {k: v * inp['factors'][k] for k, v in raw_costs.items()}
    assert abs(sum(costs.values()) - info.objective_function_value) < 1e-4
    row.update(verified=True, capacity_mva=float(ratings.sum()), clr=float(ratings.sum() / inp['peak']),
        cost=float(info.objective_function_value), cost_components=costs, units=ratings.tolist(), modules=modules.tolist(),
        storage_mw=float(modules.sum() * .1), storage_mwh=float(modules.sum() * .215), line_count=len(chosen), built=sorted(chosen),
        physical_check=check, matrix_violation=violation, initial_transfer_audit=inp['initial_transfer_audit'])
    if parameters.get('independent_lp', False):
        proof = independent_lp_check(parameters, ratings, modules, chosen)
        assert proof['verified'], proof
        row['independent_lp'] = proof
    return row


def task(item):
    mode, p = item
    global REFERENCE
    if REFERENCE is None:
        REFERENCE = defaultdict(list)
        for name in ('transfer_grid.jsonl', 'transfer_grid_reverse80.jsonl', 'pilot_reverse80.jsonl',
                     'transfer_grid_procurement.jsonl', 'pilot_procurement.jsonl'):
            path = OUT / name
            if not path.exists(): continue
            for line in path.read_text().splitlines():
                try: r = json.loads(line)
                except json.JSONDecodeError: continue
                key = (r['mode'], r['eta'], r['growth_rate'], r['cable_fraction'], r['initial_transfer_fraction'])
                REFERENCE[key].append(r)
    key = (mode, p['eta'], p['growth_rate'], p['cable_fraction'], p['initial_transfer_fraction'])
    # 较短支撑时长、较低分散系数和较宽反向限值均为当前问题的松弛。
    # 固定旧设备经当前独立LP验证且费用上下界收敛后，可复用证书；其余仍寻优。
    weaker = [r for r in REFERENCE[key] if r['support_duration_h'] <= p['support_duration_h'] + 1e-9
              and r['diversity'] <= p['diversity'] + 1e-9
              and r.get('normal_reverse_limit_fraction', 1.) >= p.get('normal_reverse_limit_fraction', .8) - 1e-9]
    warm = None; best_proof = None; began = time.monotonic()
    allowed=set(CATALOG) if mode=='greenfield' else {50.,63.,80.}
    for r in sorted(weaker, key=lambda r: r.get('cost', np.inf)):
        if r['status'] == 'Infeasible':
            row = dict(p, mode=mode, verified=False, status='Infeasible', cost_lower=None, relative_gap=None,
                       elapsed_seconds=time.monotonic() - began,
                       reuse_basis='松弛问题已证不可行，当前约束更严', source_parameters={k:r[k] for k in old.FIELDS})
            return row
        if not r.get('verified'): continue
        if any(float(v) not in allowed for unit in r['units'] for v in unit[:2]):continue
        if warm and r['cost'] >= warm['cost'] - 1e-7: continue
        proof = independent_lp_check(p, r['units'], r['modules'], set(r['built']))
        if proof['verified']:
            warm = r; best_proof = proof
    bounds = [r['cost_lower'] for r in weaker if r.get('cost_lower') is not None and math.isfinite(r['cost_lower'])]
    if warm and bounds:
        lower = max(bounds); gap = max(0., (warm['cost'] - lower) / max(1., abs(warm['cost'])))
        assert lower <= warm['cost'] + 1e-4, ('松弛费用下界超过可行费用', p, lower, warm['cost'])
        if gap <= p.get('gap', .001) + 1e-10:
            row = copy.deepcopy(warm); row.update(p, mode=mode, cost_lower=lower, relative_gap=gap,
                elapsed_seconds=time.monotonic() - began, status='Certified by feasible layout and relaxation bound',
                independent_lp=best_proof, reuse_basis='旧设备在当前约束独立LP可行，松弛问题费用下界仍有效',
                source_row_sha256=hashlib.sha256(json.dumps(warm, sort_keys=True).encode()).hexdigest())
            row['legacy_physical_check'] = row.pop('physical_check', None)
            row['physical_check'] = dict(checked_pairs=best_proof['checked_pairs'],
                max_violation_mw=best_proof['max_violation_mw'], normal_reverse_limit_fraction=p['normal_reverse_limit_fraction'])
            row['source_parameters'] = {k: warm[k] for k in old.FIELDS}
            REFERENCE[key].append(row)
            return row
    if warm is None:
        candidates=[r for r in weaker if r.get('verified')]
        if candidates:
            seed=copy.deepcopy(min(candidates,key=lambda r:r['cost']))
            seed['units']=[[next(r for r in sorted(allowed) if r>=v-1e-7) for v in unit[:2]]+[unit[2]] for unit in seed['units']]
            warm=seed
    row = solve(p, mode, warm)
    REFERENCE[key].append(row)
    return row


def run_grid(workers=4, pilot=False):
    OUT.mkdir(parents=True, exist_ok=True)
    values = [(1.5, .04, .1, h) for h in (2., 4.)] if pilot else itertools.product([.5, 1.5, 2.5], [0., .04, .055, .08], [.1, .3, .5], [2., 4., 6.], [1., 1.1, 1.15])
    if pilot: values = [(e, g, q, h, 1.1) for e, g, q, h in values]
    tasks = [(mode, dict(eta=e, growth_rate=g, cable_fraction=q, support_duration_h=hours,
        initial_transfer_fraction=r / 10., diversity=diversity, seconds=25., gap=.001, independent_lp=pilot,
        normal_reverse_limit_fraction=.8,procurement_catalog_revision='31.5_50_63_80'))
        for e, g, q, hours, diversity in values for r in range(1, 10)
        for mode in (('stock', 'stock_allcost', 'greenfield') if pilot else ('stock', 'greenfield'))]
    path = OUT / ('pilot_procurement.jsonl' if pilot else 'transfer_grid_procurement.jsonl')
    done = set()
    if path.exists():
        for line in path.read_text().splitlines():
            r = json.loads(line); done.add((r['mode'], *(r[k] for k in old.FIELDS)))
    tasks = [item for item in tasks if (item[0], *(item[1][k] for k in old.FIELDS)) not in done]
    with path.open('a', encoding='utf-8') as f, ProcessPoolExecutor(max_workers=workers) as pool:
        pending = {pool.submit(task, item): item for item in tasks}
        for i, future in enumerate(as_completed(pending), 1):
            row = future.result(); f.write(json.dumps(row, ensure_ascii=False) + '\n'); f.flush()
            if pilot or i % 30 == 0:
                print('MATRIX', i, '/', len(tasks), row['mode'], row['initial_transfer_fraction'],
                      row.get('capacity_mva'), row.get('relative_gap'), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--workers', type=int, default=4); p.add_argument('--pilot', action='store_true')
    a = p.parse_args(); run_grid(a.workers, a.pilot)
