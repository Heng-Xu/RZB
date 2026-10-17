"""在已核验的费用参考5%以内优先简化联络，仅作单年方向筛查。"""
import copy
import json

import numpy as np

from . import audit as a, probe


def run():
    reference=a.REVIEW/'单年机制筛查/pizhou/elastic_free'
    ref=json.loads((reference/'summary.json').read_text());inp=json.loads((reference/'effective_inputs.json').read_text())
    _,scenes,_=a.base.prepare('pizhou','annual_2021');selected={tuple(v) for v in json.loads((reference/'selected_pairs.json').read_text())}
    folder=a.REVIEW/'单年机制筛查/pizhou/elastic_engineering';folder.mkdir(exist_ok=True)
    if (folder/'summary.json').exists():return
    warm=reference;history=[];limit=ref['cost_npv_10k']*1.05
    lp_inp=copy.deepcopy(inp);lp_inp['audit_mode']='direct_fault';lp=a.RestrictedLP(lp_inp)
    for iteration in range(1,6):
        native,meta=probe.build(inp,scenes,'elastic_free',selected);cost=np.array(native.costs)
        native.constraint({j:float(c) for j,c in enumerate(cost) if c},upper=limit)
        native.costs=(cost/max(1.,limit)*1e-5).tolist()
        for (eid,y),v in meta['edgevars'].items():native.costs[v]+=1.
        z,result=a.base.old.old.base.parameters.solve(native,folder,f'engineering_{iteration:02}',60.,.00001,
            dict(inp,storage_usable_energy_fraction=1.),meta,warm)
        assert z is not None and result['feasible_incumbent']
        construction=copy.deepcopy(result);value=float(cost@z)
        result.update(objective=value,dual_bound=ref['solver']['dual_bound'],mip_gap=max(0.,(value-ref['solver']['dual_bound'])/value),
            accepted=False,status='经济参考5%费用容差内优先简化联络的单年可行方案',construction_search=construction)
        checks,bad,detail=a.base.old.old.base.check_all(inp,{2025:scenes[2025]},z,meta,lp)
        summary,stations,projects=a.base.old.old.base.network.extract(inp,None,'elastic_free',z,meta,result,history,checks)
        candidate=folder/f'candidate_{iteration:02}';candidate.mkdir(exist_ok=True)
        a.base.old.write_csv(candidate/'stations.csv',stations);a.base.old.write_csv(candidate/'projects.csv',projects)
        if not projects:(candidate/'projects.csv').write_text('year,id\n',encoding='utf-8-sig')
        history.append(dict(iteration=iteration,construction_search=construction,checks=checks))
        print('ENGINEERING_PROBE',iteration,'violations',len(bad),'cost',value,'annual',summary['annual'],flush=True)
        if bad:
            selected.update((y,h,f) for _,y,h,f in sorted(bad,reverse=True)[:30]);warm=candidate;continue
        assert value<=limit+1e-5
        summary.update(scope=ref['scope'],common_floor=inp['common_floor'],history=history,
            selection=dict(reference_cost=ref['cost_npv_10k'],cost_tolerance=.05,actual_premium=value/ref['cost_npv_10k']-1,
                rule='费用容差内优先最少联络；未施加容量或储能跨方案排序要求'))
        a.base.old.dump(folder/'summary.json',summary);a.base.old.dump(folder/'effective_inputs.json',inp)
        a.base.old.write_csv(folder/'stations.csv',stations);a.base.old.write_csv(folder/'projects.csv',projects)
        a.base.old.dump(folder/'independent_lp.json',dict(verified=True,checks=checks,records=detail))
        a.base.old.dump(folder/'selected_pairs.json',sorted(selected));np.savez_compressed(folder/'chosen_solution.npz',solution=z)
        return
    raise RuntimeError('工程优选单年校核未完成')


if __name__=='__main__':run()
