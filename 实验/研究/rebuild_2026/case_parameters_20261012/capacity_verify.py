"""复建约束矩阵、复算逐站费用并重新校核静态工况。"""
import json
from collections import defaultdict

import numpy as np
from scipy.sparse import coo_matrix

from .capacity_run import (OUT,REVIEW,CASES,previous,parameters,load_scenes,build,check_all,dump,sha)
from .capacity_audit import FlowLP,PROFILES


def verify():
    REVIEW.mkdir(parents=True,exist_ok=True)
    result=dict(verified=True,regions={},checked_pairs=0)
    for region in ('city','pizhou'):
        root=OUT/region;inp=json.loads((root/'inputs.json').read_text());scenes=load_scenes(root,inp)
        original=json.loads((previous.OUT/region/'inputs.json').read_text())
        assert inp['stations']==original['stations']
        for key in ('initial_capacity_mva','initial_peak_mw','annual_observed_peak_mw','cost_factors',
                    'storage_usable_energy_fraction','storage_module_capex_10k','physical_capacity_upper_mva'):
            assert inp[key]==original[key],key
        assert inp['transfer_calibration_year']==2025
        assert sha(PROFILES/f'{region}_stations.npz')==inp['snapshot_source_sha256']
        audit=parameters.initial_transfer_audit(inp)
        assert abs(audit['weighted_rate']-inp['initial_transfer_fraction'])<1e-7
        edges={e['id']:e for e in inp['network']['edges']}
        assert all(edges[e['id']]==e for e in original['network']['edges'])
        assert all(inp['network']['feeders'][f]==r for f,r in original['network']['feeders'].items())
        assert all(inp['transfer_calibration_capacity_mva'][s]==(r['asset_capacity_mva'] or sum(r['initial_units']))
                   for s,r in original['stations'].items())
        lp=FlowLP(inp);region_result={};costs={}
        for case in CASES:
            out=root/case;s=json.loads((out/'summary.json').read_text());costs[case]=s['cost_npv_10k']
            assert s['input_sha256']==sha(root/'inputs.json')
            selected={tuple(v) for v in json.loads((out/'selected_pairs.json').read_text())}
            m,meta=build(inp,scenes,case,selected)
            z=np.load(out/'chosen_solution.npz')['solution']
            rr,cc,vv=zip(*m.entries)
            matrix=coo_matrix((vv,(rr,cc)),shape=(len(m.constraint_lower),len(m.costs))).tocsr()
            assert len(z)==len(m.costs)
            az=matrix@z;integer=np.array(m.integrality,dtype=bool)
            violation=max(0.,float(np.max(np.array(m.constraint_lower)-az)),float(np.max(az-np.array(m.constraint_upper))),
                          float(np.max(np.array(m.lower_bounds)-z)),float(np.max(z-np.array(m.upper_bounds))),
                          float(np.max(abs(z[integer]-np.round(z[integer])))))
            assert violation<1e-5,(region,case,violation)
            assert abs(np.dot(m.costs,z)-s['cost_npv_10k'])<1e-5
            checks,failures,detail=check_all(inp,scenes,z,meta,lp)
            assert not failures,(region,case,failures[:3])
            stations={(int(r['year']),r['station']):r for r in previous.rows(out/'stations.csv')}
            assert len(stations)==len(inp['stations'])*len(inp['years'])
            projects=previous.rows(out/'projects.csv')
            assert len({r['id'] for r in projects})==len(projects)
            assert all(not edges[r['id']]['existing'] for r in projects)
            total_cost=0.;prev_units={sid:np.array(a['initial_units']+[0.]) for sid,a in inp['stations'].items()}
            prev_modules={sid:0 for sid in inp['stations']};oldcap=inp['initial_capacity_mva']
            for annual in s['annual']:
                y=annual['year'];purchased=0.;third=0.;added_modules=0.;capacity=0.;all_modules=0
                for sid,a in inp['stations'].items():
                    r=stations[y,sid];u=np.array([float(r[f'unit_{k}_mva']) for k in (1,2,3)])
                    n=int(r['storage_modules']);old=prev_units[sid]
                    assert np.all(u>=old) and n>=prev_modules[sid] and u[0]<=u[1]
                    assert u[2] in ((0.,50.) if a['allow_third'] else (0.,))
                    for slot in (0,1):assert u[slot] in {a['initial_units'][slot],*[v for v in inp['new_ratings'] if v>=a['initial_units'][slot]]}
                    bought=float(np.where(u[:2]>old[:2],u[:2],0).sum());purchased+=bought
                    third+=(u[2]-old[2])/50;added_modules+=n-prev_modules[sid];all_modules+=n;capacity+=u.sum()
                    assert abs(float(r['purchased_transformer_mva'])-bought-u[2]+old[2])<1e-6
                    assert sum(r['new_bay_station']==sid and int(r['year'])<=y for r in projects)<=a['metadata']['spare_10kv_bays']
                    prev_units[sid]=u;prev_modules[sid]=n
                assert abs(capacity-annual['capacity_mva'])<1e-6
                assert capacity>=s['clr_floor']*annual['peak_mw']-1e-6
                assert abs(annual['clr']-capacity/annual['peak_mw'])<1e-9
                assert abs(annual['net_capacity_increment_mva']-(capacity-oldcap))<1e-6
                if case=='rigid_storage':assert capacity<=max(oldcap,2*annual['peak_mw'])+1e-6
                oldcap=capacity
                raw=dict(transformer=purchased*inp['transformer_price_10k_per_purchased_mva']+third*inp['third_50mva_capex_10k'],
                         storage=added_modules*inp['storage_module_capex_10k'],
                         line=sum(int(r['year'])==y for r in projects)*inp['line_capex_10k'])
                for key,cost in raw.items():
                    cost*=inp['cost_factors'][key][str(y)]
                    assert abs(cost-annual[key+'_npv_10k'])<1e-5
                    total_cost+=cost
                assert abs(annual['storage_mwh']-.215*all_modules)<1e-6
            assert abs(total_cost-s['cost_npv_10k'])<1e-5
            count=sum(c['checked_pairs'] for c in checks);result['checked_pairs']+=count
            region_result[case]=dict(verified=True,checked_pairs=count,matrix_violation=violation,
                cost_recomputed_10k=total_cost,input_sha256=s['input_sha256'],solution_sha256=sha(out/'chosen_solution.npz'),
                checks=checks,solver_lower_bound_10k=s['solver']['dual_bound'],solver_gap=s['solver']['mip_gap'])
            print('VERIFIED_CAPACITY',region,case,count,'pairs',flush=True)
        assert costs['elastic_no_floor']<=min(costs['rigid_storage'],costs['elastic_floor_2'])+1e-5
        result['regions'][region]=region_result
    dump(REVIEW/'矩阵费用及独立承载力核验.json',result)
    return result


if __name__=='__main__':verify()
