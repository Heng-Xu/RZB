"""同下限的单年机制筛查；不代替2021—2035逐年成果。"""
import argparse
import copy
import json
import math

import numpy as np

from . import audit as a
from ..two_district_ordered_guide_run import guide_range


def build(inp,scenes,case,selected):
    native,meta=a.base.build(inp,scenes,case,selected)
    for y in inp['years']:
        native.constraint(a.base.old.old.base.previous.capacity_terms(inp,meta,y),lower=inp['common_floor']*inp['annual_observed_peak_mw'][str(y)])
    edges={e['id']:e for e in inp['network']['edges']};ids=list(inp['stations'])
    for y,h,f,eid,d,v in meta['network_flows']:
        e=edges[eid]
        # 全停全转统计只作事故时可用总量；正常供区调整须由付费项目承担。
        if (f<0 and e['existing']) or (f>=0 and ids[f] not in (e['station_a'],e['station_b'])):
            native.upper_bounds[v]=0.
    return native,meta


def run(region,case,seconds=40):
    inp,scenes,_=a.base.prepare(region,'annual_2021')
    inp=copy.deepcopy(inp);inp['years']=[2025];inp['common_floor']=guide_range(inp['growth_rate'])[0]
    out=a.REVIEW/'单年机制筛查'/region/case;out.mkdir(parents=True,exist_ok=True)
    a.base.old.dump(out/'effective_inputs.json',inp)
    if (out/'summary.json').exists():return
    ids=list(inp['stations']);u=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]);zero=np.zeros(len(ids),int)
    lp_inp=copy.deepcopy(inp);lp_inp['audit_mode']='direct_fault';lp=a.RestrictedLP(lp_inp)
    selected=set();bad=[]
    for h,p in enumerate(scenes[2025]):
        ready=lp.prepared(p,2025,u,zero,set())
        for f in range(-1,len(ids)):
            result=lp.check(p,ready,f)
            if not result['verified']:bad.append((result['deficit_mw'],2025,h,f))
    for f in range(-1,len(ids)):
        found=[r for r in bad if r[3]==f]
        if found:
            _,y,h,ff=max(found);selected.add((y,h,ff))
    warm=out/'warm';warm.mkdir(exist_ok=True);rows=[]
    for j,(sid,s) in enumerate(inp['stations'].items()):
        survive=.95*(u[j].sum()-u[j].max());beta=.8*.95*u[j].sum()
        bp=min(.1,.215*.76/max(1,s['forward_duration_h']));bn=min(.1,.215*.76/max(1,s['reverse_duration_h']))
        n=math.ceil(max(0.,(scenes[2025][:,j].max()-survive)/bp,(-scenes[2025][:,j].min()-min(survive,beta))/bn)+1e-8)
        rows.append(dict(year=2025,station=sid,unit_1_mva=u[j,0],unit_2_mva=u[j,1],unit_3_mva=0.,storage_modules=n))
    a.base.old.write_csv(warm/'stations.csv',rows);(warm/'projects.csv').write_text('year,id\n',encoding='utf-8-sig')
    history=[]
    for iteration in range(1,7):
        native,meta=build(inp,scenes,case,selected)
        z,result=a.base.old.old.base.parameters.solve(native,out,f'probe_{iteration:02}',seconds,.01,
            dict(inp,storage_usable_energy_fraction=1.),meta,warm)
        assert z is not None and result['feasible_incumbent'],result
        checks,violations,detail=a.base.old.old.base.check_all(inp,{2025:scenes[2025]},z,meta,lp)
        summary,stations,projects=a.base.old.old.base.network.extract(inp,None,case,z,meta,result,history,checks)
        a.base.old.write_csv(warm/'stations.csv',stations);a.base.old.write_csv(warm/'projects.csv',projects)
        if not projects:(warm/'projects.csv').write_text('year,id\n',encoding='utf-8-sig')
        history.append(dict(iteration=iteration,selected_pairs=len(selected),checks=checks,solver=result))
        print('PROBE',region,case,iteration,'violations',len(violations),'annual',summary['annual'],flush=True)
        if violations:
            added={(y,h,f) for _,y,h,f in sorted(violations,reverse=True)[:30]};assert added-selected
            selected.update(added);continue
        summary.update(scope='2025单年静态机制筛查，2021设备保持且只决定本年度措施；不代替逐年规划',common_floor=inp['common_floor'],history=history)
        a.base.old.dump(out/'summary.json',summary);a.base.old.write_csv(out/'stations.csv',stations);a.base.old.write_csv(out/'projects.csv',projects)
        a.base.old.dump(out/'independent_lp.json',dict(verified=True,checks=checks,records=detail));a.base.old.dump(out/'selected_pairs.json',sorted(selected))
        np.savez_compressed(out/'chosen_solution.npz',solution=z)
        return
    raise RuntimeError('单年机制筛查未完成')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--region',required=True,choices=['city','pizhou']);p.add_argument('--case',required=True,choices=['rigid','elastic_free']);p.add_argument('--seconds',type=float,default=40)
    args=p.parse_args();run(args.region,args.case,args.seconds)
