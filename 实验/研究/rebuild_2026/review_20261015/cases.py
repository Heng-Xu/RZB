"""逐站转供、未压缩地区基期及指定容量对照的逐年规划试算。"""
import argparse
import copy
import json
import math
import shutil
from pathlib import Path

import highspy
import numpy as np
from scipy.sparse import coo_matrix

from ..annual_no_tie_investment_submodel import LinearModel
from ..case_parameters_20261012 import transfer_diagnostic as old

ROOT = old.ROOT
OUT = ROOT / '研究报告/试算/20261015_会后建模复核/案例'
SOURCE = ROOT / '研究报告/数据来源/当前版/会后建模复核_20261015'
PUBLIC = ROOT / '研究报告/01研究推荐/当前版/会后建模复核_20261015'
REVIEW = ROOT / '研究报告/05_review/当前版/1015会后建模复核'
dump, write_csv, sha = old.dump, old.write_csv, old.sha


def fit_initial_capacity(inp, target):
    """固定原表地区总容量，按2025站级容量比例标定双主变组合。

    2021逐台档案不齐，输出明确标记为标定组合，不能称为历史逐台实测。
    此模型只拟合起点，不使用后续规划的经济结果选择起点。
    """
    m = LinearModel(); choices = {}; refs = {}
    weights = {sid: s['asset_capacity_mva'] or sum(s['initial_units'])
               for sid, s in inp['stations'].items()}
    denom = sum(weights.values())
    total = {}
    for sid, s in inp['stations'].items():
        refs[sid] = weights[sid] * target / denom
        station = {}
        for slot, before in enumerate(s['initial_units']):
            ratings = sorted({before, 20., 31.5, 40., 50., 63., 80.})
            one = {}
            for rating in ratings:
                v = m.variable(0); choices[sid, slot, rating] = v
                one[v] = 1.; station[v] = rating; total[v] = rating
            m.constraint(one, 1., 1.)
        m.constraint({v: r * (1 if slot == 0 else -1)
                      for (ss, slot, r), v in choices.items() if ss == sid}, upper=0.)
        pos = m.variable(1., upper=np.inf, integer=0); neg = m.variable(1., upper=np.inf, integer=0)
        m.constraint({**station, pos: -1., neg: 1.}, refs[sid], refs[sid])
    m.constraint(total, target, target)
    rr, cc, vv = zip(*m.entries)
    a = coo_matrix((vv, (rr, cc)), shape=(len(m.constraint_lower), len(m.costs))).tocsr()
    lp = highspy.HighsLp(); lp.num_col_, lp.num_row_ = a.shape[1], a.shape[0]
    lp.col_cost_, lp.col_lower_, lp.col_upper_ = m.costs, m.lower_bounds, m.upper_bounds
    lp.row_lower_, lp.row_upper_ = m.constraint_lower, m.constraint_upper
    lp.integrality_ = [highspy.HighsVarType.kInteger if v else highspy.HighsVarType.kContinuous
                       for v in m.integrality]
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = a.indptr, a.indices, a.data
    h = highspy.Highs()
    for k, v in [('threads', 1), ('random_seed', 0), ('mip_rel_gap', .0001),
                 ('time_limit', 60.), ('log_to_console', False)]: h.setOptionValue(k, v)
    h.passModel(lp); h.run()
    assert h.getModelStatus() == highspy.HighsModelStatus.kOptimal, h.modelStatusToString(h.getModelStatus())
    z = h.getSolution().col_value; records = []
    for sid, s in inp['stations'].items():
        units = [next(r for (ss, sl, r), v in choices.items()
                      if ss == sid and sl == slot and z[v] > .5) for slot in (0, 1)]
        records.append(dict(station=sid, reference_2025_mva=weights[sid],
                            proportional_reference_mva=refs[sid], fitted_units=units,
                            fitted_capacity_mva=sum(units),
                            evidence='2021地区总容量为原表；逐站双主变组合为按2025容量比例标定'))
        s['initial_units'] = units
    assert abs(sum(sum(s['initial_units']) for s in inp['stations'].values()) - target) < 1e-7
    return records


def prepare(region, baseline, reverse_limit=.8):
    suffix = '_reverse80' if abs(reverse_limit - .8) < 1e-10 else ''
    root = OUT / region / (baseline + suffix)
    if (root / 'inputs.json').exists():
        inp = json.loads((root / 'inputs.json').read_text())
        scenes = old.base.load_scenes(old.base.OUT / region, inp)
        return inp, scenes, root
    source = old.OUT / '约束对照' / region / 'station_caps' / 'inputs.json'
    inp = json.loads(source.read_text()); inp = copy.deepcopy(inp)
    scenes = old.base.load_scenes(old.base.OUT / region, inp)
    evidence = old.station_evidence(inp); byid = {r['station']: r for r in evidence}
    budgets = {}
    for y in inp['years']:
        budgets[str(y)] = {}
        for j, sid in enumerate(inp['stations']):
            r = byid[sid]; rate = r['source_fraction'] or 0.
            budgets[str(y)][sid] = min(r['transferable_mw'], rate * max(0., float(scenes[y][:, j].max())))
    inp['existing_transfer_budget_by_year_mw'] = budgets
    inp['existing_transfer_budget_mw'] = {sid: max(b[sid] for b in budgets.values()) for sid in inp['stations']}
    inp['station_transfer_rates'] = {sid: byid[sid]['source_fraction'] for sid in inp['stations']}
    inp['transfer_constraint_policy'] = 'station_rate_with_absolute_J_cap'
    inp['transfer_constraint_definition'] = 'rho_i=J_i/(J_i+K_i); Q_iy=min(J_i,rho_i*站i当年最大正向净负荷); 另受通道、馈线共享余量和接收主变约束'
    inp['normal_supply_area_fixed'] = False
    inp['normal_reverse_limit_fraction'] = reverse_limit
    inp['reverse_limit_basis'] = '2025年4月修订稿6.5.3正常反向80%；DL/T 2041—2025第6.4条，N-1故障站按剩余主变不过载，健康站仍按正常反向限值'
    fitted = []
    if baseline == 'annual_2021':
        target = inp['annual_observed_capacity_mva']['2021']
        fitted = fit_initial_capacity(inp, target)
        inp['initial_capacity_mva'] = target
        inp['baseline_treatment'] = '保留2021原表地区容量；逐站组合按2025容量比例标定，非2021逐台历史复原'
    else:
        inp['baseline_treatment'] = '保留报告原共同压缩设备组合，单独改逐站转供'
    inp['initial_clr'] = inp['initial_capacity_mva'] / inp['initial_peak_mw']
    inp['physical_capacity_upper_mva'] = sum(sum(max(v, 80.) for v in s['initial_units'])
        + 50. * int(s['allow_third']) for s in inp['stations'].values())
    inp['review_source_input_sha256'] = sha(source)
    inp['review_baseline'] = baseline
    root.mkdir(parents=True, exist_ok=True)
    if (root / 'inputs.json').exists():
        assert json.loads((root / 'inputs.json').read_text()) == inp
    else:
        dump(root / 'inputs.json', inp)
        write_csv(root / 'station_transfer_evidence.csv', evidence)
        if fitted: dump(root / 'initial_capacity_fit.json', fitted)
    return inp, scenes, root


class StationLP(old.DiagnosticLP):
    def prepared(self, p, y, units, n, built):
        common, bounds, full, largest, bp, bn = super().prepared(p, y, units, n, built)
        common = common.copy()
        common[-len(self.ids):] = [self.inp['existing_transfer_budget_by_year_mw'][str(y)][s] for s in self.ids]
        return common, bounds, full, largest, bp, bn

    def bounds_for(self, prepared, failed):
        common, bounds, full, largest, bp, bn = super().bounds_for(prepared, failed)
        beta = self.inp.get('normal_reverse_limit_fraction', 1.)
        reverse_allowance = bn - (1. - beta) * full
        if failed >= 0: reverse_allowance[failed] = bn[failed]
        return common, bounds, full, largest, bp, reverse_allowance


def build(inp, scenes, case, selected, target=None):
    economic_case = 'rigid_storage' if case == 'rigid' else 'elastic_no_floor'
    m, meta = old.build(inp, scenes, economic_case, selected)
    groups = {}
    station_flows = {}
    edge_map = {e['id']: e for e in inp['network']['edges']}
    for y, h, f, eid, direction, v in meta['network_flows']:
        e = edge_map[eid]
        a, b = (e['a'], e['b']) if direction == 0 else (e['b'], e['a'])
        sa = inp['network']['feeders'][a]['station']; sb = inp['network']['feeders'][b]['station']
        station_flows.setdefault((y, h, f, sa), {})[v] = -1.
        station_flows.setdefault((y, h, f, sb), {})[v] = 1.
        if e['existing']:
            a = e['a'] if direction == 0 else e['b']
            sid = inp['network']['feeders'][a]['station']
            groups.setdefault((y, h, f, sid), {})[v] = 1.
    for (y, h, f, sid), terms in groups.items():
        m.constraint(terms, upper=inp['existing_transfer_budget_by_year_mw'][str(y)][sid])
    beta = inp.get('normal_reverse_limit_fraction', 1.)
    if beta < 1.:
        ids = list(inp['stations'])
        for y, h, f in sorted(selected):
            for j, sid in enumerate(ids):
                if j == f: continue
                s = inp['stations'][sid]
                terms = {v: beta * old.PF * r for (ss, slot, yy, r), v in meta['x'].items() if ss == sid and yy == y}
                if (sid, y) in meta['third']: terms[meta['third'][sid, y]] = beta * old.PF * 50.
                terms[meta['modules'][sid, y]] = min(.1, .215 * .76 / max(1, s['reverse_duration_h']))
                terms.update(station_flows.get((y, h, f, sid), {}))
                m.constraint(terms, lower=-float(scenes[y][h, j]))
    if target:
        # 用户指定的方案比较要求，单独登记；不当作自由寻优的自然结论。
        for y in inp['years']:
            r = target[y]
            m.constraint(old.base.previous.capacity_terms(inp, meta, y), lower=r['capacity_mva'] + .5)
            m.constraint({v: 1. for (sid, yy), v in meta['modules'].items() if yy == y},
                         upper=round(r['storage_mwh'] / .215))
            m.constraint({v: 1. for (eid, yy), v in meta['edgevars'].items() if yy == y},
                         upper=max(0, r['cumulative_lines'] - int(y == inp['years'][-1] and r['cumulative_lines'] > 0)))
    return m, meta


def make_warm(inp, scenes, folder, target):
    """在当前输入上给已有候选补足静态缺口，只用作求解起点。"""
    lp = StationLP(inp); ids = list(inp['stations']); records = []; projects = []
    for y in inp['years']:
        if folder and (folder / 'stations.csv').exists():
            oldunits, oldn, built = old.assets_from_csv(inp, folder, y)
            units = np.maximum(oldunits, np.array([s['initial_units'] + [0.] for s in inp['stations'].values()]))
            units[:, :2].sort(axis=1); n = oldn.copy()
        else:
            units = np.array([s['initial_units'] + [0.] for s in inp['stations'].values()]); n = np.zeros(len(ids), dtype=int); built = set()
        for p in scenes[y]:
            ready = lp.prepared(p, y, units, n, built)
            for f in range(-1, len(ids)):
                r = lp.check(p, ready, f)
                if not r['verified']:
                    for sid, deficit in r['station_deficits'].items():
                        j = ids.index(sid); s = inp['stations'][sid]
                        coef = min(.1, .215 * .76 / max(1, s['forward_duration_h']),
                                   .215 * .76 / max(1, s['reverse_duration_h']))
                        n[j] += math.ceil((deficit + 1e-6) / coef)
                    ready = lp.prepared(p, y, units, n, built)
        if records:
            for j, sid in enumerate(ids): n[j] = max(n[j], int(records[-len(ids) + j]['storage_modules']))
        for j, sid in enumerate(ids):
            records.append(dict(year=y, station=sid, unit_1_mva=units[j, 0], unit_2_mva=units[j, 1],
                unit_3_mva=units[j, 2], storage_modules=int(n[j]), storage_mwh=float(n[j] * .215)))
    target.mkdir(parents=True, exist_ok=True)
    write_csv(target / 'stations.csv', records)
    if folder and (folder / 'projects.csv').exists(): (target / 'projects.csv').write_bytes((folder / 'projects.csv').read_bytes())
    else: (target / 'projects.csv').write_text('year,id\n', encoding='utf-8-sig')
    return target


def best_folder(root, case):
    folders = [p.parent for p in root.glob(case + '*/summary.json')
               if json.loads(p.read_text()).get('case') == case]
    def quality(folder):
        r = json.loads((folder / 'summary.json').read_text())
        return round(r['cost_npv_10k'], 6), r['solver'].get('mip_gap', 1.)
    return min(folders, key=quality) if folders else None


def certify_legacy(region, baseline, case):
    """更宽反向限值下的设备若通过当前全工况校核，其费用下界仍有效。"""
    inp, scenes, root = prepare(region, baseline, .8)
    legacy = best_folder(OUT / region / baseline, case)
    if legacy is None: return None
    source_inp = json.loads((legacy.parent / 'inputs.json').read_text())
    for key in ('stations', 'network', 'existing_transfer_budget_by_year_mw'):
        assert source_inp[key] == inp[key], key
    summary = json.loads((legacy / 'summary.json').read_text()); lp = StationLP(inp)
    checks = []; detail = []
    for y in inp['years']:
        units, n, built = old.assets_from_csv(inp, legacy, y); failures = []
        for h, p in enumerate(scenes[y]):
            ready = lp.prepared(p, y, units, n, built)
            for f in range(-1, len(inp['stations'])):
                r = lp.check(p, ready, f)
                detail.append(dict(year=y, scenario=h, failed_station=lp.ids[f] if f >= 0 else 'normal', **r))
                if not r['verified']: failures.append(r)
        checks.append(dict(year=y, checked_pairs=len(scenes[y]) * (len(inp['stations']) + 1),
            violating_pairs=len(failures), max_deficit_mw=max((r['deficit_mw'] for r in failures), default=0.), verified=not failures))
    if not all(r['verified'] for r in checks): return None
    out = root / (case + '_certified80'); out.mkdir(exist_ok=True)
    for name in ('stations.csv', 'projects.csv', 'selected_pairs.json', 'chosen_solution.npz'):
        shutil.copyfile(legacy / name, out / name)
    summary.update(input_sha256=sha(root / 'inputs.json'), checks=checks, certified_from=str(legacy.relative_to(ROOT)),
        source_input_sha256=sha(legacy.parent / 'inputs.json'),
        certificate='固定原设备通过当前反向80%及逐站转供全部LP校核；原较宽约束的费用下界作为当前问题有效下界')
    summary['solver']['source_status'] = summary['solver']['status']
    summary['solver']['status'] = 'Independent LP verified with valid relaxation bound'
    summary['solver']['source_matrix_check'] = summary['solver'].pop('matrix_check', None)
    dump(out / 'summary.json', summary); write_csv(out / 'years.csv', summary['annual'])
    dump(out / 'independent_lp.json', dict(verified=True, checks=checks, records=detail))
    return out


def run(region, baseline, case, seconds=180., gap=.005, attempt=None, reverse_limit=.8):
    inp, scenes, root = prepare(region, baseline, reverse_limit)
    out = root / (case + ('_' + attempt if attempt else '')); out.mkdir(exist_ok=True)
    if (out / 'summary.json').exists(): return json.loads((out / 'summary.json').read_text())
    target = None
    if case == 'elastic_target':
        rigid_folder = best_folder(root, 'rigid')
        target = {r['year']: r for r in json.loads((rigid_folder / 'summary.json').read_text())['annual']}
    lp = StationLP(inp); selected = set()
    for y in inp['years']:
        for h, r in enumerate(inp['station_snapshot_roles']):
            if '地区正向峰值' in r['roles'] or '地区最低净负荷' in r['roles']:
                selected.update((y, h, f) for f in range(-1, len(inp['stations'])))
    label = 'rigid_storage_refine_02' if case == 'rigid' else 'elastic_no_floor_refine_02'
    source = old.OUT / '约束对照' / region / 'station_caps' / label
    if not source.exists():
        source = old.OUT / '约束对照' / region / 'station_caps' / ('rigid_storage_refine_01' if case == 'rigid' else 'elastic_no_floor_refine_01')
    if (source / 'selected_pairs.json').exists():
        selected.update(tuple(r) for r in json.loads((source / 'selected_pairs.json').read_text()))
    if case == 'elastic_target': source = best_folder(root, 'elastic_free')
    if attempt and best_folder(root, case): source = best_folder(root, case)
    if (source / 'selected_pairs.json').exists():
        selected.update(tuple(r) for r in json.loads((source / 'selected_pairs.json').read_text()))
    warm = make_warm(inp, scenes, source, out / 'warm_start')
    history = []; bounds = []
    for iteration in range(1, 9):
        m, meta = build(inp, scenes, case, selected, target)
        z, result = old.base.parameters.solve(m, out, f'iteration_{iteration:02}', seconds, gap,
            dict(inp, storage_usable_energy_fraction=1.), meta, warm)
        if result.get('dual_bound') is not None: bounds.append(result['dual_bound'])
        if z is None or not result.get('feasible_incumbent'):
            dump(out / 'failed_search.json', dict(solver=result, history=history)); return None
        checks, violations, detail = old.base.check_all(inp, scenes, z, meta, lp)
        history.append(dict(iteration=iteration, selected_pairs=len(selected), solver=result, checks=checks))
        summary, stations, projects = old.base.network.extract(inp, None, case, z, meta, result, history, checks)
        candidate = out / f'candidate_{iteration:02}'; candidate.mkdir(exist_ok=True)
        write_csv(candidate / 'stations.csv', stations); write_csv(candidate / 'projects.csv', projects)
        dump(candidate / 'summary.json', summary)
        print('CASE_CHECK', region, baseline, case, iteration, 'failures', len(violations), flush=True)
        if violations:
            added = {(y, h, f) for _, y, h, f in sorted(violations, reverse=True)[:40]}
            assert added - selected; selected.update(added)
            warm = make_warm(inp, scenes, candidate, candidate / 'repaired_warm'); continue
        result['dual_bound'] = max(bounds)
        result['mip_gap'] = max(0., (result['objective'] - result['dual_bound']) / max(1., abs(result['objective'])))
        summary.update(region=region, baseline=baseline, case=case, solver=result,
            scope='地区及各站极值同期静态截面，正常及最大单台主变N-1；储能按规定时长折算；年度空间形态沿用样本',
            scenario_constraint='指定对照：弹性容量逐年大于刚性至少0.5 MVA，储能及联络累计不多于刚性，末年在刚性联络非零时至少少1条' if target else '费用自由寻优；刚性保留2.0扩容控制，弹性取消该容量上限',
            input_sha256=sha(root / 'inputs.json'), checks=checks)
        if target:
            summary['target_reference'] = str(rigid_folder.relative_to(ROOT))
            summary['target_annual'] = list(target.values())
        summary.pop('full_hour_network_checks', None)
        previous = inp['initial_capacity_mva']
        for a in summary['annual']:
            a['net_capacity_increment_mva'] = a['capacity_mva'] - previous; previous = a['capacity_mva']
        dump(out / 'summary.json', summary); write_csv(out / 'years.csv', summary['annual'])
        write_csv(out / 'stations.csv', stations); write_csv(out / 'projects.csv', projects)
        dump(out / 'selected_pairs.json', sorted(selected)); np.savez_compressed(out / 'chosen_solution.npz', solution=z)
        dump(out / 'independent_lp.json', dict(verified=True, checks=checks, records=detail))
        print('CASE_DONE', region, baseline, case, summary['cost_npv_10k'], flush=True)
        return summary
    raise RuntimeError('承载力切面迭代尚未完成')


def main():
    p = argparse.ArgumentParser(); p.add_argument('--region', choices=['city', 'pizhou'], required=True)
    p.add_argument('--baseline', choices=['compressed', 'annual_2021'], required=True)
    p.add_argument('--case', choices=['rigid', 'elastic_free', 'elastic_target'], required=True)
    p.add_argument('--seconds', type=float, default=180.); p.add_argument('--gap', type=float, default=.005)
    p.add_argument('--attempt')
    p.add_argument('--reverse-limit', type=float, choices=[.8, 1.], default=.8)
    a = p.parse_args(); run(a.region, a.baseline, a.case, a.seconds, a.gap, a.attempt, a.reverse_limit)


if __name__ == '__main__': main()
