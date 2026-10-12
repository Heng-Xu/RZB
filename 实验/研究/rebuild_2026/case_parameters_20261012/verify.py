"""固定逐年设备，独立LP重求转供；核对配对模型和费用。"""
import argparse
import json
from collections import defaultdict

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

from .run import (OUT, REVIEW, SOURCE, CASES, PF, dump, sha, previous,
                  limits, initial_transfer_audit, transfer_evidence, cable_evidence)


def independent_lp(inp,scenes,stations,projects):
    ids=list(inp['stations']); index={s:j for j,s in enumerate(ids)}
    feeders=list(inp['network']['feeders']); fi={f:j for j,f in enumerate(feeders)}
    edges=inp['network']['edges']; arcs=[]
    for k,e in enumerate(edges):
        for d in range(2 if e['bidirectional'] else 1):
            a,b=(e['a'],e['b']) if d==0 else (e['b'],e['a'])
            sa=index[inp['network']['feeders'][a]['station']]
            sb=index[inp['network']['feeders'][b]['station']]
            arcs.append((k,e,d,a,b,sa,sb))
    # 每条边共享容量；逐馈线送/受余量；逐站原生负荷与存量预算；双向主变限额。
    nf=len(feeders); ne=len(edges); ns=len(ids)
    offset=[0,ne,ne+nf,ne+2*nf,ne+2*nf+ns,ne+2*nf+2*ns,ne+2*nf+3*ns]
    rr=[];cc=[];vv=[]
    for j,(k,e,d,a,b,sa,sb) in enumerate(arcs):
        entries=[(k,1),(offset[1]+fi[a],1),(offset[2]+fi[b],1),
                 (offset[3]+sa,1),(offset[5]+sa,-1),(offset[5]+sb,1),
                 (offset[6]+sa,1),(offset[6]+sb,-1)]
        if e['existing']:entries.append((offset[4]+sa,1))
        for row,value in entries:rr.append(row);cc.append(j);vv.append(value)
    matrix=coo_matrix((vv,(rr,cc)),shape=(offset[6]+ns,len(arcs))).tocsr()
    table={(int(r['year']),r['station']):r for r in stations}
    records=[]
    for y in inp['years']:
        units=np.array([[float(table[y,s][f'unit_{k}_mva']) for k in (1,2,3)] for s in ids])
        modules=np.array([int(table[y,s]['storage_modules']) for s in ids])
        usable=inp['storage_usable_energy_fraction']
        bp=np.array([min(.1,.215*usable/max(1,inp['stations'][s]['forward_duration_h'])) for s in ids])*modules
        bn=np.array([min(.1,.215*usable/max(1,inp['stations'][s]['reverse_duration_h'])) for s in ids])*modules
        built={r['id'] for r in projects if int(r['year'])<=y}
        capedge=np.array([e['capacity_mw'] if e['existing'] or e['id'] in built else 0 for e in edges])
        for h,p in enumerate(scenes[y]):
            donor,receive=limits(inp,p,y)
            bounds=[(0,min(capedge[k],donor[a]*e['source_section_fraction']) if e['existing'] else capedge[k])
                    for k,e,d,a,b,sa,sb in arcs]
            common=np.concatenate((capedge,[donor[f] for f in feeders],[receive[f] for f in feeders],
                                   np.maximum(p,0),[inp['existing_transfer_budget_mw'][s] for s in ids]))
            for failed in range(-1,ns):
                available=PF*units.sum(axis=1)
                if failed>=0:available[failed]-=PF*units[failed].max()
                rhs=np.concatenate((common,available+bp-p,available+bn+p))
                r=linprog(np.zeros(len(arcs)),A_ub=matrix,b_ub=rhs,bounds=bounds,method='highs')
                assert r.success, (y,h,failed,r.message)
                violation=max(0.,float((matrix@r.x-rhs).max()))
                assert violation<1e-6
                records.append(dict(year=y,scenario=h,failed_station=ids[failed] if failed>=0 else 'normal',
                                    verified=True,max_violation_mw=violation))
    return records


def read_csv(path):
    return previous.rows(path)


def verify():
    REVIEW.mkdir(parents=True,exist_ok=True)
    rr,stats=transfer_evidence(); cc,cable=cable_evidence()
    saved=json.loads((SOURCE/'来源及参数.json').read_text())
    for key in ('转供原表','邳州线路原表'):
        from .run import ROOT
        assert sha(ROOT/saved[key]['path'])==saved[key]['sha256']
    assert len(rr)==87 and len(cc)==403
    result=dict(verified=True,source_station_count=len(rr),source_line_count=len(cc),regions={})
    for region in ('city','pizhou'):
        root=OUT/region; inp=json.loads((root/'inputs.json').read_text())
        old=json.loads((previous.OUT/region/'inputs.json').read_text()); scenes=previous.load_scenes(root,inp)
        assert inp['stations']==old['stations'], '设备和储能持续时间须保持原案例'
        for key in ('annual_observed_peak_mw','initial_peak_mw','initial_capacity_mva','cost_factors',
                    'storage_usable_energy_fraction','storage_module_capex_10k','physical_capacity_upper_mva'):
            assert inp[key]==old[key],key
        assert sha(root/'静态工况.csv')==sha(previous.OUT/region/'静态工况.csv')
        old_edges={e['id']:e for e in old['network']['edges']}
        assert all(e==old_edges[e['id']] for e in inp['network']['edges'] if e['id'] in old_edges)
        old_feeders=old['network']['feeders']
        assert all(inp['network']['feeders'][f]==r for f,r in old_feeders.items())
        # 全部电压等级原表汇总应等于模型实际可实现的初始转供率。
        expected=next(r['转供率'] for r in stats if r['统计范围']=='全部电压等级' and
                      r['地区']==('徐州市区' if region=='city' else '邳州'))
        audit=initial_transfer_audit(inp)
        assert abs(audit['weighted_rate']-expected)<1e-7
        expected_net=scenes[2025][0]*inp['initial_peak_mw']/inp['annual_observed_peak_mw']['2025']
        assert np.allclose(list(inp['transfer_calibration_forward_mw'].values()),np.maximum(expected_net,0))
        raw=inp.get('transfer_calibration_net_mw',inp['transfer_calibration_forward_mw'])
        assert abs(sum(raw.values())-inp['initial_peak_mw'])<1e-6
        assert inp['line_cable_fraction']==(.8 if region=='city' else cable)
        assert abs(inp['line_capex_10k']-(3*(24*(1-inp['line_cable_fraction'])+180*inp['line_cable_fraction'])+6))<1e-9
        region_result=dict(initial_transfer_audit=audit,cases={})
        summaries={}
        for case in CASES:
            out=root/case; summary=json.loads((out/'summary.json').read_text()); summaries[case]=summary
            assert summary['input_sha256']==sha(root/'inputs.json')
            assert summary['solver']['feasible_incumbent']
            stations=read_csv(out/'stations.csv'); projects=read_csv(out/'projects.csv')
            station={(int(r['year']),r['station']):r for r in stations}
            assert len(station)==len(inp['years'])*len(inp['stations'])
            assert len({r['id'] for r in projects})==len(projects)
            edge_map={e['id']:e for e in inp['network']['edges']}
            assert all(not edge_map[r['id']]['existing'] for r in projects)
            total=0.; previous_units={s:np.array(inp['stations'][s]['initial_units']+[0.]) for s in inp['stations']}
            previous_modules={s:0 for s in inp['stations']}
            for annual in summary['annual']:
                y=annual['year']; purchased=0.; third=0; added_storage=0; capacity=0.; n_total=0
                for s,asset in inp['stations'].items():
                    row=station[y,s]; units=np.array([float(row[f'unit_{k}_mva']) for k in (1,2,3)])
                    n=int(row['storage_modules']); old_units=previous_units[s]
                    assert np.all(units>=old_units) and n>=previous_modules[s]
                    for k in (0,1):assert units[k] in {asset['initial_units'][k],*[r for r in inp['new_ratings'] if r>=asset['initial_units'][k]]}
                    assert units[0]<=units[1] and units[2] in ((0,50) if asset['allow_third'] else (0,))
                    bought=float(np.where(units[:2]>old_units[:2],units[:2],0).sum())
                    assert abs(bought+units[2]-old_units[2]-float(row['purchased_transformer_mva']))<1e-6
                    purchased+=bought; third+=(units[2]-old_units[2])/50
                    added_storage+=n-previous_modules[s]; capacity+=units.sum(); n_total+=n
                    bays=sum(r['new_bay_station']==s and int(r['year'])<=y for r in projects)
                    assert bays<=asset['metadata']['spare_10kv_bays']
                    previous_units[s]=units; previous_modules[s]=n
                assert abs(capacity-annual['capacity_mva'])<1e-6
                assert capacity>=summary['clr_floor']*inp['annual_observed_peak_mw'][str(y)]-1e-6
                assert abs(annual['clr']-capacity/inp['annual_observed_peak_mw'][str(y)])<1e-9
                assert abs(annual['storage_mwh']-.215*n_total)<1e-6
                raw=dict(transformer=purchased*inp['transformer_price_10k_per_purchased_mva']+third*inp['third_50mva_capex_10k'],
                         storage=added_storage*inp['storage_module_capex_10k'],
                         line=sum(int(r['year'])==y for r in projects)*inp['line_capex_10k'])
                cost=sum(raw[k]*inp['cost_factors'][k][str(y)] for k in raw)
                assert abs(cost-annual['added_lifecycle_npv_10k'])<1e-5
                total+=cost
            assert abs(total-summary['cost_npv_10k'])<1e-5
            lp=independent_lp(inp,scenes,stations,projects)
            dump(out/'independent_lp.json',dict(verified=True,checked_pairs=len(lp),records=lp))
            region_result['cases'][case]=dict(cost_recomputed_10k=total,independent_lp_pairs=len(lp),
                                             independent_lp_max_violation_mw=max(r['max_violation_mw'] for r in lp),
                                             input_sha256=summary['input_sha256'])
            print('VERIFIED',region,case,len(lp),'independent LPs',flush=True)
        assert summaries['no_floor']['cost_npv_10k']<=summaries['floor_2']['cost_npv_10k']+1e-5
        assert summaries['floor_2']['input_sha256']==summaries['no_floor']['input_sha256']
        result['regions'][region]=region_result
    dump(REVIEW/'独立核验.json',result)
    return result


if __name__=='__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    verify()
