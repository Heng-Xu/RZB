"""弹性：先减少新增配套费用，再比较达到该水平的主变方案费用。"""
import argparse
import copy
import json

import numpy as np

from . import model as m, prepare as p
from .run import annual_row, asset_rows, write_warm

AUXILIARY_TOLERANCE = .20

def objective_vectors(inp,native,meta,y,oldn,built):
    price=np.array(native.costs);support=np.zeros(len(price))
    for v in meta['modules'].values():support[v]=price[v]
    # 原模型把联络采购费用记在new_projects辅助变量上，edgevars自身费用为零。
    # 此处按已建路径逐项计价，避免优选目标漏计联络投资。
    for v in meta['edgevars'].values():support[v]=inp['line_capex_10k']*inp['cost_factors']['line'][str(y)]
    support[meta['one']]=-(oldn.sum()*inp['storage_module_capex_10k']*inp['cost_factors']['storage'][str(y)]
        +len(built)*inp['line_capex_10k']*inp['cost_factors']['line'][str(y)])
    return price,support


def get_stage(inp,power,y,case,old,oldn,built,replaced,folder,seconds):
    state=folder/'adopted.json'
    if state.exists():
        r=json.loads(state.read_text());assert r['previous_assets_sha256']==p.sha(folder/'previous_assets.json')
        return np.array(r['units']),np.array(r['modules']),set(r['built']),r
    survive=.95*(old.sum(1)-old.max(1));reverse=np.minimum(survive,.8*.95*old.sum(1))
    bp=np.array([min(.1,.215*.76/max(1,s['forward_duration_h'])) for s in inp['stations'].values()])
    bn=np.array([min(.1,.215*.76/max(1,s['reverse_duration_h'])) for s in inp['stations'].values()])
    warmn=np.maximum(oldn,np.ceil(np.maximum(0.,np.maximum((power.max(0)-survive)/bp,(-power.min(0)-reverse)/bn))+1e-8).astype(int))
    warm=folder/'warm';write_warm(inp,warm,y,old,warmn,built)
    selected={(int(h),f) for j in range(power.shape[1]) for h in (np.argmax(power[:,j]),np.argmin(power[:,j])) for f in (-1,j)}
    prior=folder.parent/str(y-1)/'adopted.json'
    if prior.exists():selected.update(tuple(v) for v in json.loads(prior.read_text())['selected_pairs'])
    progress=folder/'separation_progress.json'
    if progress.exists():selected.update(tuple(v) for v in json.loads(progress.read_text())['selected_pairs'])
    history=[]
    for phase in ('support','engineering','cost'):
        for iteration in range(1,46):
            native,meta,one=m.build(inp,power,y,case,old,oldn,built,replaced,selected)
            price,support=objective_vectors(inp,native,meta,y,oldn,built)
            if phase=='support':native.costs=support.tolist()
            else:
                native.constraint({v:float(c) for v,c in enumerate(support) if c},upper=support_limit*(1+AUXILIARY_TOLERANCE)+1e-6)
                if phase=='engineering':
                    native.costs=(support/max(1.,support_limit)*1e-5).tolist()
                    for v in meta['edgevars'].values():native.costs[v]+=1.
                else:native.constraint({v:1. for v in meta['edgevars'].values()},upper=line_limit)
            z,solver=p.base.old.old.base.parameters.solve(native,folder,f'{phase}_{iteration:02}',seconds,.001,
                dict(one,storage_usable_energy_fraction=1.),meta,warm)
            if z is None or not solver.get('feasible_incumbent'):
                if phase!='support':
                    # 一级候选已通过全年检查，且变量次序与二级一致。
                    z=fallback_z.copy();solver=dict(fallback_solver,fallback='工程/费用搜索限时，保留前阶段已核验候选')
                else:raise RuntimeError((y,phase,solver))
            u,n,bs,normal,extra=m.layout(inp,z,meta)
            checked,bad=m.verify(inp,power,y,u,n,bs,normal,extra)
            history.append(dict(phase=phase,iteration=iteration,solver=copy.deepcopy(solver),verified=not bad))
            print('CAPACITY_SEARCH',inp['region_name'],y,phase,iteration,'bad',len(bad),'C',u.sum(),'E',n.sum()*.215,'L',len(bs),flush=True)
            if bad:
                assert bad-selected;selected|=bad;p.dump(progress,dict(selected_pairs=sorted(selected)))
                write_warm(inp,warm,y,u,n,bs);continue
            write_warm(inp,warm,y,u,n,bs)
            if phase=='support':
                support_limit=max(0.,float(support@z))
                p.dump(folder/'support_reference.json',dict(solver=solver,support_limit_npv_10k=support_limit,
                    units=u.tolist(),modules=n.tolist(),built=sorted(bs),normal=normal,extra=extra,check=checked))
                np.savez_compressed(folder/'support_solution.npz',solution=z)
            if phase=='engineering':line_limit=len(bs)
            fallback_z=z.copy();fallback_solver=copy.deepcopy(solver)
            break
        else:raise RuntimeError((y,phase,'全年校核未闭合'))
    row=annual_row(inp,y,u,n,bs,old,oldn,built,0.)
    assert abs(float(price@z)-row['added_lifecycle_npv_10k'])<.02
    assert abs(float(support@z)-row['storage_npv_10k']-row['line_npv_10k'])<.02
    assert float(support@z)<=support_limit*(1+AUXILIARY_TOLERANCE)+1e-4 and len(bs)<=line_limit
    solver=dict(solver,conditional_search=copy.deepcopy(solver),objective=row['added_lifecycle_npv_10k'],
        dual_bound=0.,mip_gap=1. if row['added_lifecycle_npv_10k']>1e-6 else 0.,accepted=False,
        status='配套费用优先、再比较总费用的逐年工程可行方案；不宣称总费用全局最优')
    result=dict(year=y,units=u.tolist(),modules=n.tolist(),built=sorted(bs),normal=normal,extra=extra,
        solver=solver,selected_pairs=sorted(selected),check=checked,annual=row,history=history,
        previous_assets_sha256=p.sha(folder/'previous_assets.json'),support_limit_npv_10k=support_limit,line_limit=line_limit,
        support_tolerance=AUXILIARY_TOLERANCE,
        selection=dict(rule=f'先最小化本年新增储能与联络费用，在该候选配套费用{AUXILIARY_TOLERANCE:.0%}范围内优先减少联络，再比较新增工程总费用；主变增容投资不受5%总费用包络限制',
            primary_source='本方案本年独立搜索，未使用刚性方案结果设置排序约束'))
    p.dump(state,result);np.savez_compressed(folder/'chosen_solution.npz',solution=z)
    return u,n,bs,result


def run(region,seconds=8.):
    inp,powers=p.load(region);case='elastic_capacity';root=p.RAW/region/case;root.mkdir(exist_ok=True)
    ids=list(inp['stations']);old=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]);oldn=np.zeros(len(ids),int)
    built=set();replaced=np.zeros((len(ids),2),bool);cumulative=0.;stations=asset_rows(inp,2021,old,oldn);projects=[];checks=[];transfers=[]
    baseline,_=m.verify(inp,powers[2021],2021,old,oldn,set(),{},{});p.dump(root/'baseline_check.json',baseline)
    original=json.loads((p.parent.RAW/region/'rigid'/'summary.json').read_text());annual=[original['annual'][0]]
    for y in inp['years']:
        folder=root/str(y);folder.mkdir(exist_ok=True)
        previous=dict(year=y,units=old.tolist(),modules=oldn.tolist(),built=sorted(built),replaced=replaced.tolist(),input_sha256=p.sha(p.RAW/region/'inputs.json'))
        if (folder/'previous_assets.json').exists():assert json.loads((folder/'previous_assets.json').read_text())==previous
        else:p.dump(folder/'previous_assets.json',previous)
        u,n,bs,r=get_stage(inp,powers[y],y,case,old,oldn,built,replaced,folder,seconds)
        assert np.all(u>=old) and np.all(n>=oldn) and bs>=built
        changed=u[:,:2]>old[:,:2]+1e-7;assert not np.any(changed&replaced);replaced|=changed
        row=annual_row(inp,y,u,n,bs,old,oldn,built,cumulative);cumulative=row['cumulative_lifecycle_npv_10k']
        annual.append(row);stations.extend(asset_rows(inp,y,u,n));projects.extend(dict(year=y,id=e) for e in sorted(bs-built))
        checks.extend(r['check']['records']);transfers.extend(r['check']['transfers']);old,oldn,built=u,n,bs
        p.write_csv(root/'years.csv',annual);p.write_csv(root/'stations.csv',stations);p.write_csv(root/'projects.csv',projects)
        print('CAPACITY_YEAR',region,y,'C',u.sum(),'E',n.sum()*.215,'L',len(bs),flush=True)
    p.dump(root/'summary.json',dict(region=region,case=case,annual=annual,cost_npv_10k=cumulative,verified=True,
        cost_scope=original['cost_scope'],planning_method='远景选型、年度继承，配套费用优先的逐年工程候选；非全期联合最优',
        baseline_verified=baseline['verified'],input_sha256=p.sha(p.RAW/region/'inputs.json'),scope=inp['scope'],
        checked_hour_contingency_pairs=sum(r['checked_hours'] for r in checks)))
    p.dump(root/'independent_full_year.json',dict(verified=True,records=checks,transfers=transfers))
    print('CAPACITY_DONE',region,cumulative,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--region',choices=p.REGIONS,required=True)
    parser.add_argument('--seconds',type=float,default=8.);a=parser.parse_args();run(a.region,a.seconds)
