"""本年总费用寻优、全年校核、逐年承接；不预设扩容或储能排序。"""
import argparse
import copy
import json
import fcntl
from contextlib import contextmanager
from pathlib import Path

import numpy as np

from ..annual_demand_driven_2035_20261017.solver import solve
from ..annual_demand_driven_2035_20261017.run import annual_row, asset_rows, write_warm
from . import model as m, prepare as p
from .repair import complete_storage


def get_stage(inp, power, y, case, old, oldn, built, last, folder, seconds, refine_seconds=30.):
    state = folder / 'adopted.json'
    if state.exists():
        result = json.loads(state.read_text())
        assert result['previous_assets_sha256'] == p.sha(folder / 'previous_assets.json')
        return np.array(result['units']), np.array(result['modules']), set(result['built']), result
    firm = .95 * (old.sum(1) - old.max(1))
    reverse = np.minimum(firm, .8 * .95 * old.sum(1))
    bp = np.array([min(.1, .215 * .76 / max(1, s['forward_duration_h'])) for s in inp['stations'].values()])
    bn = np.array([min(.1, .215 * .76 / max(1, s['reverse_duration_h'])) for s in inp['stations'].values()])
    warmn = np.maximum(oldn, np.ceil(np.maximum(0., np.maximum(
        (power.max(0) - firm) / bp, (-power.min(0) - reverse) / bn)) + 1e-8).astype(int))
    warm = folder / 'warm'
    write_warm(inp, warm, y, old, warmn, built)
    selected = {(int(h), f) for j in range(power.shape[1])
                for h in (np.argmax(power[:, j]), np.argmin(power[:, j])) for f in (-1, j)}
    previous = folder.parent / str(y-1) / 'adopted.json'
    if previous.exists():
        selected.update(tuple(v) for v in json.loads(previous.read_text())['selected_pairs'])
    progress = folder / 'separation_progress.json'
    if progress.exists():
        selected.update(tuple(v) for v in json.loads(progress.read_text())['selected_pairs'])
    history, bounds = [], []
    repair_log = []
    def save_feasible_warm(candidate,native,meta,source):
        completed = complete_storage(inp,power,candidate,meta,native)
        if completed is None:
            return False
        np.savez_compressed(warm/'full_solution.npz',solution=completed)
        uu,nn,bbs,_,_ = m.layout(inp,completed,meta)
        write_warm(inp,warm,y,uu,nn,bbs)
        repair_log.append(dict(source=source,cost_before=float(np.array(native.costs)@candidate),
                               cost_after=float(np.array(native.costs)@completed),verified=True))
        p.dump(folder/'可行热启动补足记录.json',repair_log)
        return True
    for iteration in range(1, 46):
        native, meta, one = m.build(inp, power, y, case, old, oldn, built, last, selected)
        if iteration==1:
            candidates = []
            for path in folder.glob('*_solution.npz'):
                candidate = np.load(path)['solution']
                if len(candidate)==len(native.costs):
                    completed = complete_storage(inp,power,candidate,meta,native)
                    if completed is not None:
                        candidates.append((float(np.array(native.costs)@completed),completed,path.name))
            if candidates:
                _,candidate,source = min(candidates,key=lambda v:v[0])
                save_feasible_warm(candidate,native,meta,'已有候选补足：'+source)
        z, solver = solve(native, folder, f'cost_{iteration:02}', seconds, .02,
                          dict(one, storage_usable_energy_fraction=1.), meta, warm)
        history.append(copy.deepcopy(solver))
        if not solver.get('feasible_incumbent'):
            z, solver = solve(native, folder, f'retry_{iteration:02}', max(45., seconds), .02,
                              dict(one, storage_usable_energy_fraction=1.), meta, warm)
            history.append(copy.deepcopy(solver))
        assert z is not None and solver.get('feasible_incumbent'), (y, case, solver)
        bounds.extend(r['dual_bound'] for r in history if r.get('dual_bound') is not None)
        np.savez_compressed(warm / 'full_solution.npz', solution=z)
        u, n, bs, normal, extra = m.layout(inp, z, meta)
        checked, bad = m.verify(inp, power, y, u, n, bs, normal, extra)
        print('COST_CHECK', inp['region_name'], case, y, iteration, 'bad', len(bad), flush=True)
        if bad:
            assert bad-selected
            selected |= bad
            p.dump(progress, dict(selected_pairs=sorted(selected)))
            if not save_feasible_warm(z,native,meta,f'cost_{iteration:02}'):
                write_warm(inp, warm, y, u, n, bs)
            continue
        if solver.get('mip_gap', 1.) > .05:
            zz, refined = solve(native, folder, f'refine_{iteration:02}', max(refine_seconds, seconds), .02,
                                 dict(one, storage_usable_energy_fraction=1.), meta, warm)
            history.append(copy.deepcopy(refined))
            if refined.get('dual_bound') is not None:
                bounds.append(refined['dual_bound'])
            if refined.get('feasible_incumbent') and refined['objective'] <= solver['objective'] + 1e-7:
                z, solver = zz, refined
                np.savez_compressed(warm / 'full_solution.npz', solution=z)
                u, n, bs, normal, extra = m.layout(inp, z, meta)
                checked, bad = m.verify(inp, power, y, u, n, bs, normal, extra)
                if bad:
                    assert bad-selected
                    selected |= bad
                    p.dump(progress, dict(selected_pairs=sorted(selected)))
                    if not save_feasible_warm(z,native,meta,f'refine_{iteration:02}'):
                        write_warm(inp, warm, y, u, n, bs)
                    continue
        row = annual_row(inp, y, u, n, bs, old, oldn, built, 0.)
        assert abs(row['added_lifecycle_npv_10k'] - float(np.array(native.costs) @ z)) < 1e-5
        solver = dict(solver, objective=row['added_lifecycle_npv_10k'], dual_bound=max(bounds),
                      mip_gap=max(0., (row['added_lifecycle_npv_10k']-max(bounds))/max(1., abs(row['added_lifecycle_npv_10k']))))
        result = dict(year=y, units=u.tolist(), modules=n.tolist(), built=sorted(bs), normal=normal, extra=extra,
                      solver=solver, economic_history=history, selected_pairs=sorted(selected), check=checked,
                      annual=row, previous_assets_sha256=p.sha(folder/'previous_assets.json'),
                      selection=dict(rule='按本年度新增主变、储能和联络全费用现值直接寻优', tolerance=0.))
        p.dump(state, result)
        np.savez_compressed(folder/'chosen_solution.npz', solution=z)
        return u, n, bs, result
    raise RuntimeError((case, y, '全年分离校核未闭合'))


@contextmanager
def case_lock(region,case):
    path = Path('/tmp')/f'xuzhou-annual-cost-interval-20261017-{region}-{case}.lock'
    with path.open('a') as handle:
        try:
            fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(f'{region}/{case}已有计算进程，拒绝并发写入') from exc
        yield


def run(region,case,seconds=12.,refine_seconds=30.):
    with case_lock(region,case):
        _run(region,case,seconds,refine_seconds)


def _run(region, case, seconds=12., refine_seconds=30.):
    inp, powers = p.load(region)
    root = p.RAW / region / case
    root.mkdir(exist_ok=True)
    old = np.array([s['initial_units']+[0.] for s in inp['stations'].values()])
    oldn = np.zeros(len(old), dtype=int)
    last = np.zeros((len(old), 2), dtype=int)
    built, projects, checks, transfers, history, replacements = set(), [], [], [], [], []
    calibrated = json.loads((p.RAW/region/'baseline/adopted.json').read_text())
    baseline, _ = m.verify(inp, powers[2021], 2021, old, oldn, built,
                           {int(k):v for k,v in calibrated['normal'].items()},
                           {int(k):v for k,v in calibrated['extra'].items()})
    p.dump(root/'baseline_check.json', baseline)
    annual = [annual_row(inp, 2021, old, oldn, built, old, oldn, built, 0.)]
    stations, cumulative = asset_rows(inp, 2021, old, oldn), 0.
    for y in inp['years']:
        folder = root/str(y)
        folder.mkdir(exist_ok=True)
        previous = dict(year=y, units=old.tolist(), modules=oldn.tolist(), built=sorted(built),
                        last_replacement_year=last.tolist(), input_sha256=p.sha(p.RAW/region/'inputs.json'))
        if (folder/'previous_assets.json').exists():
            assert json.loads((folder/'previous_assets.json').read_text()) == previous
        else:
            p.dump(folder/'previous_assets.json', previous)
        u, n, bs, result = get_stage(inp, powers[y], y, case, old, oldn, built, last, folder, seconds, refine_seconds)
        assert np.all(u >= old-1e-7) and np.all(n >= oldn) and bs >= built
        changed = u[:, :2] > old[:, :2]+1e-7
        assert not np.any(changed & m.locked_positions(last, y))
        for j, k in zip(*np.where(changed)):
            replacements.append(dict(year=y, station=list(inp['stations'])[j], slot=int(k+1),
                                     previous_year=int(last[j,k]), old_mva=float(old[j,k]), new_mva=float(u[j,k])))
        last[changed] = y
        row = annual_row(inp, y, u, n, bs, old, oldn, built, cumulative)
        cumulative = row['cumulative_lifecycle_npv_10k']
        annual.append(row)
        stations.extend(asset_rows(inp, y, u, n))
        projects.extend(dict(year=y, id=e) for e in sorted(bs-built))
        checks.extend(result['check']['records'])
        transfers.extend(result['check']['transfers'])
        history.append(dict(year=y, solver=result['solver']))
        old, oldn, built = u, n, bs
        for name, values in (('years.csv', annual), ('stations.csv', stations), ('projects.csv', projects),
                             ('replacements.csv', replacements)):
            p.write_csv(root/name, values)
        print('INTERVAL_YEAR', region, case, y, 'C', u.sum(), 'ESS_MW', n.sum()*.1, 'L', len(bs), flush=True)
    p.dump(root/'summary.json', dict(region=region, case=case, annual=annual, cost_npv_10k=cumulative,
        cost_scope='2022—2035当年新增工程至2041年费用现值，2021年为折现基年；既有资产不重复采购',
        planning_method='当年需求、上年资产、四年更换间隔下逐年总费用寻优；非全期联合最优',
        history=history, baseline_verified=baseline['verified'], input_sha256=p.sha(p.RAW/region/'inputs.json'),
        scope=inp['scope'], checked_hour_contingency_pairs=sum(r['checked_hours'] for r in checks), verified=True))
    p.dump(root/'independent_full_year.json', dict(verified=True, records=checks, transfers=transfers))
    print('INTERVAL_DONE', region, case, cumulative, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', choices=p.REGIONS, required=True)
    parser.add_argument('--case', choices=p.CASES, required=True)
    parser.add_argument('--seconds', type=float, default=12.)
    parser.add_argument('--refine-seconds', type=float, default=30.)
    args = parser.parse_args()
    run(args.region, args.case, args.seconds, args.refine_seconds)
