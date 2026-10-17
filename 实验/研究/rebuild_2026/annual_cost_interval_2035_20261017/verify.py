"""核对原始证据、采购差量、四年窗口、整数解与全年固定预案。"""
import json

import numpy as np
from openpyxl import load_workbook
from scipy.sparse import coo_matrix

from ..annual_demand_driven_2035_20261017.verify import independent_cost
from ..case_parameters_20261012.run import TRANSFER_FILE
from . import model as m, prepare as p


def run():
    from .sources import run as audit_asset_sources
    audit_asset_sources()
    wb = load_workbook(TRANSFER_FILE, read_only=True, data_only=True)
    original = list(wb.worksheets[0].values)
    wb.close()
    sources, schemes, costs, evidence, replacement_rows = [], [], [], [], []
    total, max_matrix, max_cost = 0, 0., 0.
    for region in p.REGIONS:
        inp, powers = p.load(region)
        ids = list(inp['stations'])
        assert len(powers) == 15 and all(v.shape == (8760, len(ids)) for v in powers.values())
        assert inp['forecast_basis']['sha256'] == p.sha(p.ROOT/inp['forecast_basis']['source'])
        for record in inp['station_transfer_evidence']:
            sid = record['station']
            if record['matched']:
                raw = original[record['source_row']-1]
                assert raw[2] == record['name']
                assert abs(raw[9]-record['transferable_mw']) < 1e-9
            else:
                assert record['transferable_mw'] == 0.
            assert all(inp['existing_transfer_budget_by_year_mw'][str(y)][sid] == record['transferable_mw'] for y in powers)
            evidence.append(dict(地区=p.REGIONS[region],变电站=sid,站名=record['name'],
                                 原表行号=record['source_row'],既有能力_MW=record['transferable_mw'],原表对应=record['matched']))
        for case in p.CASES:
            root = p.RAW/region/case
            summary = json.loads((root/'summary.json').read_text())
            assert summary['input_sha256'] == p.sha(p.RAW/region/'inputs.json')
            assert [a['year'] for a in summary['annual']] == list(range(2021, 2036))
            old = np.array([s['initial_units']+[0.] for s in inp['stations'].values()])
            oldn, built = np.zeros(len(old), int), set()
            last = np.zeros((len(old), 2), int)
            cumulative, records, transfers = 0., [], []
            assert old.sum() == inp['initial_capacity_mva'] == summary['annual'][0]['capacity_mva']
            for y in inp['years']:
                stage = root/str(y)
                r = json.loads((stage/'adopted.json').read_text())
                previous = json.loads((stage/'previous_assets.json').read_text())
                assert previous == dict(year=y, units=old.tolist(), modules=oldn.tolist(), built=sorted(built),
                                        last_replacement_year=last.tolist(),input_sha256=p.sha(p.RAW/region/'inputs.json'))
                assert r['previous_assets_sha256'] == p.sha(stage/'previous_assets.json')
                native, meta, _ = m.build(inp, powers[y], y, case, old, oldn, built, last,
                                          {tuple(v) for v in r['selected_pairs']})
                z = np.load(stage/'chosen_solution.npz')['solution']
                assert len(z) == len(native.costs)
                rr, cc, vv = zip(*native.entries)
                lhs = coo_matrix((vv, (rr, cc)), shape=(len(native.constraint_lower), len(z))).tocsr()@z
                ints = np.asarray(native.integrality, bool)
                err = max(0., float(np.max(np.array(native.constraint_lower)-lhs)),
                          float(np.max(lhs-np.array(native.constraint_upper))),
                          float(np.max(np.array(native.lower_bounds)-z)), float(np.max(z-np.array(native.upper_bounds))),
                          float(np.max(abs(z[ints]-np.round(z[ints])))))
                assert err < 1e-5, (region, case, y, err)
                max_matrix = max(max_matrix, err)
                u, n, bs, normal, extra = m.layout(inp, z, meta)
                np.testing.assert_array_equal(u, r['units'])
                np.testing.assert_array_equal(n, r['modules'])
                assert bs == set(r['built']) and normal == {int(k):v for k,v in r['normal'].items()}
                assert extra == {int(k):v for k,v in r['extra'].items()}
                checked, bad = m.verify(inp, powers[y], y, u, n, bs, normal, extra)
                assert not bad
                assert np.all(u >= old) and np.all(n >= oldn) and bs >= built
                changed = u[:, :2] > old[:, :2]+1e-7
                for j, k in zip(*np.where(changed)):
                    # 不调用锁定函数，直接以历次投运年份复算间隔。
                    assert last[j,k] == 0 or y-last[j,k] >= 4
                    replacement_rows.append(dict(地区=p.REGIONS[region],方案=case,变电站=ids[j],
                        主变位置=int(k+1),更换年份=y,上次更换年份=int(last[j,k]),
                        更换间隔_年=None if last[j,k]==0 else int(y-last[j,k]),
                        原容量_MVA=float(old[j,k]),新购容量_MVA=float(u[j,k])))
                last[changed] = y
                purchased, capex, npvs = independent_cost(inp, y, old, oldn, built, u, n, bs)
                cumulative += sum(npvs)
                expected = dict(capacity_mva=float(u.sum()),clr=float(u.sum()/inp['annual_observed_peak_mw'][str(y)]),
                    purchased_transformer_mva=purchased,net_capacity_increment_mva=float(u.sum()-old.sum()),
                    replaced_capacity_mva=float(purchased-u.sum()+old.sum()),storage_nameplate_mw=float(n.sum()*.1),
                    storage_mwh=float(n.sum()*.215),new_storage_mwh=float((n-oldn).sum()*.215),
                    new_lines=len(bs-built),cumulative_lines=len(bs),construction_capex_10k=sum(capex),
                    added_lifecycle_npv_10k=sum(npvs),cumulative_lifecycle_npv_10k=cumulative)
                expected.update(zip(('transformer_capex_10k','storage_capex_10k','line_capex_10k'),capex))
                expected.update(zip(('transformer_npv_10k','storage_npv_10k','line_npv_10k'),npvs))
                a = summary['annual'][y-2021]
                for key, value in expected.items():
                    assert abs(value-a[key]) < 1e-5, (region,case,y,key,value,a[key])
                err = abs(float(np.array(native.costs)@z)-sum(npvs))
                max_cost = max(max_cost, err)
                assert err < 1e-5 and abs(r['solver']['objective']-sum(npvs)) < 1e-5
                assert r['solver']['dual_bound'] <= sum(npvs)+1e-5
                assert a['clr'] >= a['common_floor']-1e-8
                if case == 'rigid':
                    assert u.sum() <= max(old.sum(), 2*a['peak_mw'])+1e-6
                costs.append(dict(地区=p.REGIONS[region],方案=case,年份=y,费用现值_万元=sum(npvs),
                    条件下界_万元=r['solver']['dual_bound'],间隙比例=r['solver']['mip_gap'],
                    主变费用_万元=npvs[0],储能费用_万元=npvs[1],联络费用_万元=npvs[2]))
                for item in checked['records']:
                    item['verified'] = item['max_deficit_mw'] < 1e-5
                records.extend(checked['records'])
                transfers.extend(checked['transfers'])
                total += checked['checked_hour_contingency_pairs']
                old, oldn, built = u, n, bs
            assert abs(cumulative-summary['cost_npv_10k']) < 1e-5
            p.dump(root/'independent_lp.json',dict(verified=True,records=records,transfers=transfers,
                method='全部整数约束重建，固定供区矩阵对8760小时复核，采购与维护折现费用独立复算，四年间隔按投运年份逐次核对'))
            files = ['summary.json','years.csv','stations.csv','projects.csv','replacements.csv',
                     'baseline_check.json','independent_lp.json']
            files.extend(f'{y}/{name}' for y in inp['years'] for name in ('adopted.json','previous_assets.json','chosen_solution.npz'))
            sources.append(dict(folder=str(root.relative_to(p.ROOT)),files={name:p.sha(root/name) for name in files}))
            schemes.append(dict(region=region,case=case,verified=True,cost_npv_10k=cumulative,
                                baseline_verified=summary['baseline_verified']))
            print('VERIFIED_INTERVAL',region,case,cumulative,flush=True)
    p.write_csv(p.REVIEW/'年度费用独立复算.csv',costs)
    p.write_csv(p.REVIEW/'主变更换间隔独立核对.csv',replacement_rows)
    p.write_csv(p.SOURCE/'既有转供逐站原表核对.csv',evidence)
    p.dump(p.SOURCE/'转供证据来源.json',dict(path=str(TRANSFER_FILE.relative_to(p.ROOT)),sha256=p.sha(TRANSFER_FILE),
        matched_stations=sum(r['原表对应'] for r in evidence),
        historical_caveat='原表为2025年收资，早期投运与逐线拓扑资料不完整；未匹配站既有能力按零'))
    proof = dict(verified=True,artifact_kind='annual_cost_interval_planning',schemes=schemes,solution_sources=sources,
        full_hour_pairs=total,primary_hour_pairs=total,max_matrix_error=max_matrix,max_cost_error_10k=max_cost,
        replacement_interval_years=4,planning_years=[2022,2035],display_years=[2021,2035],
        limitation='2021邳州固定设备事故缺口单列；2025收资用于早期回算、EQ拓扑为代理；储能静态时长，无连续SOC；年度条件下界不构成全期最优下界')
    p.dump(p.REVIEW/'逐年方案独立核验.json',proof)
    return proof


if __name__ == '__main__':
    run()
