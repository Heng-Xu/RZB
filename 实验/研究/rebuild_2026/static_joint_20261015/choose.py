"""在经济参考费用5%以内，优先简化联络工程；不约束刚弹容量或储能排序。"""
import argparse
import copy
import json

import numpy as np

from . import model as m

TOLERANCE=.05


def selected(region,baseline,case):
    path=m.RAW/region/baseline/'工程优选.json'
    if case=='elastic_free' and path.exists():return m.ROOT/json.loads(path.read_text())['folder']
    return m.best(region,baseline,case)


def run(region,baseline,seconds=150.):
    inp,scenes,root=m.prepare(region,baseline);reference=m.best(region,baseline,'elastic_free')
    ref=json.loads((reference/'summary.json').read_text());limit=ref['cost_npv_10k']*(1+TOLERANCE)
    if ref['annual'][-1]['cumulative_lines']==0:
        m.old.dump(root/'工程优选.json',dict(folder=str(reference.relative_to(m.ROOT)),
            reference_cost=ref['cost_npv_10k'],chosen_cost=ref['cost_npv_10k'],premium=0.,line_simplification=0,
            basis='经济参考已无新增联络，直接保留'))
        return reference
    # 旧指定对照只作为候选布局，不继承其容量、储能或刚弹排序约束。
    candidate=m.old.best_folder(m.old.OUT/region/(baseline+'_reverse80'),'elastic_target')
    warm=reference
    if candidate:
        cr=json.loads((candidate/'summary.json').read_text())
        if cr['cost_npv_10k']<=limit+1e-7 and m.replacement_counts(inp,candidate).max()<=1:warm=candidate
    selected_pairs={tuple(r) for r in json.loads((reference/'selected_pairs.json').read_text())}
    selected_pairs.update(tuple(r) for r in json.loads((warm/'selected_pairs.json').read_text()))
    selected_pairs.update((y,h,-1) for y in inp['years'] for h in range(len(scenes[y])))
    out=root/'elastic_engineering';out.mkdir(exist_ok=True)
    if (out/'summary.json').exists():return out
    history=[]
    for iteration in range(1,7):
        native,meta=m.build(inp,scenes,'elastic_free',selected_pairs)
        economic=np.array(native.costs,dtype=float)
        native.constraint({j:float(c) for j,c in enumerate(economic) if c},upper=limit)
        native.costs=(economic/max(1.,limit)*1e-5).tolist()
        for (eid,y),v in meta['edgevars'].items():
            if y==inp['years'][-1]:native.costs[v]+=1.
        z,result=m.old.old.base.parameters.solve(native,out,f'iteration_{iteration:02}',seconds,.0001,
            dict(inp,storage_usable_energy_fraction=1.),meta,warm)
        if z is None or not result.get('feasible_incumbent'):
            m.old.dump(out/'failed_search.json',dict(solver=result,history=history));return None
        construction=copy.deepcopy(result);value=float(economic@z)
        checks,violations,details=m.old.old.base.check_all(inp,scenes,z,meta,m.OperatingLP(inp))
        result.update(objective=value,dual_bound=ref['solver']['dual_bound'],
            mip_gap=max(0.,(value-ref['solver']['dual_bound'])/max(1.,abs(value))),accepted=False,
            status='Feasible engineering selection within economic reference cost allowance',construction_search=construction)
        summary,stations,projects=m.old.old.base.network.extract(inp,None,'elastic_free',z,meta,result,history,checks)
        candidate_out=out/f'candidate_{iteration:02}';candidate_out.mkdir(exist_ok=True)
        m.old.write_csv(candidate_out/'stations.csv',stations);m.old.write_csv(candidate_out/'projects.csv',projects)
        history.append(dict(iteration=iteration,selected_pairs=len(selected_pairs),construction_solver=construction,checks=checks))
        print('ENGINEERING_CHECK',region,baseline,iteration,value,'violations',len(violations),flush=True)
        if violations:
            additions={(y,h,f) for _,y,h,f in sorted(violations,reverse=True)[:40]};assert additions-selected_pairs
            selected_pairs.update(additions);warm=candidate_out;continue
        assert value<=limit+1e-5
        m.save(inp,scenes,out,region,baseline,'elastic_free',z,meta,result,selected_pairs,history,
            dict(type='经济参考费用5%以内，优先减少末年累计联络工程，次选费用较低布局',
                 economic_reference=str(reference.relative_to(m.ROOT)),reference_cost=ref['cost_npv_10k'],
                 cost_allowance=TOLERANCE,cost_upper=limit,actual_premium=value/ref['cost_npv_10k']-1,
                 warm_source=str(warm.relative_to(m.ROOT)),no_cross_scheme_ordering_constraints=True))
        chosen=json.loads((out/'summary.json').read_text())
        # 保留参考方案和简化工程方案，以线路数、费用依次比较，不回写原始结果。
        options=[(r['annual'][-1]['cumulative_lines'],r['cost_npv_10k'],p,r) for p,r in [(reference,ref),(out,chosen)]]
        _,_,p,r=min(options,key=lambda x:(x[0],x[1]))
        m.old.dump(root/'工程优选.json',dict(folder=str(p.relative_to(m.ROOT)),reference_folder=str(reference.relative_to(m.ROOT)),
            reference_cost=ref['cost_npv_10k'],chosen_cost=r['cost_npv_10k'],premium=r['cost_npv_10k']/ref['cost_npv_10k']-1,
            line_simplification=ref['annual'][-1]['cumulative_lines']-r['annual'][-1]['cumulative_lines'],
            basis='共同静态约束，新购主变不重复更换；经济参考费用5%以内优先简化联络工程'))
        return p
    raise RuntimeError('工程优选的静态工况分离未完成')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--region',choices=list(m.REGIONS),required=True)
    p.add_argument('--baseline',choices=list(m.BASELINES),required=True);p.add_argument('--seconds',type=float,default=150.)
    a=p.parse_args();run(a.region,a.baseline,a.seconds)
