"""同一工程运行约束下重算刚弹方案；不加两方案容量差目标。"""
import argparse
import copy
import itertools
import json
import math
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path

import numpy as np

from ..review_20261015 import cases as prior

ROOT=prior.ROOT
RAW=ROOT/'研究报告/试算/20261015_运行约束及五参数深化'
PUBLIC=ROOT/'研究报告/01研究推荐/当前版/运行约束及五参数深化_20261015'
REVIEW=ROOT/'研究报告/05_review/当前版/1015运行约束及五参数深化'
SOURCE=ROOT/'研究报告/数据来源/当前版/运行约束及五参数深化_20261015'
POLICIES={
    'normal_fixed':dict(normal_fixed=True,reserve_only=False,local_fault=False,transfer_factor=1.),
    'standby':dict(normal_fixed=True,reserve_only=True,local_fault=False,transfer_factor=1.),
    'local_standby':dict(normal_fixed=True,reserve_only=True,local_fault=True,transfer_factor=1.),
    'transfer80':dict(normal_fixed=True,reserve_only=True,local_fault=False,transfer_factor=.8),
    'transfer60':dict(normal_fixed=True,reserve_only=True,local_fault=False,transfer_factor=.6),
    'station_floor':dict(normal_fixed=True,reserve_only=True,local_fault=False,transfer_factor=1.,station_floor=True),
}


def prepare(policy):
    source=prior.OUT/'pizhou/compressed_reverse80/inputs.json'
    inp=json.loads(source.read_text());inp=copy.deepcopy(inp);options=POLICIES[policy]
    inp.update(followup_policy=policy,followup_options=options,normal_supply_area_fixed=options['normal_fixed'],
        followup_source_sha256=prior.sha(source))
    factor=options['transfer_factor']
    for budgets in inp['existing_transfer_budget_by_year_mw'].values():
        for sid in budgets:budgets[sid]*=factor
    inp['existing_transfer_budget_mw']={sid:max(r[sid] for r in inp['existing_transfer_budget_by_year_mw'].values()) for sid in inp['stations']}
    if options.get('station_floor'):
        reference=best('standby','rigid');assert reference is not None
        inp['station_floor_reference']=str(reference.relative_to(ROOT))
        inp['station_floor_reference_sha256']=prior.sha(reference/'stations.csv')
        inp['station_floor_by_year']={str(y):dict(zip(inp['stations'],prior.old.assets_from_csv(inp,reference,y)[0].sum(axis=1).tolist())) for y in inp['years']}
    folder=RAW/'邳州'/policy;folder.mkdir(parents=True,exist_ok=True)
    if (folder/'inputs.json').exists():assert json.loads((folder/'inputs.json').read_text())==inp
    else:prior.dump(folder/'inputs.json',inp)
    scenes=prior.old.base.load_scenes(prior.old.base.OUT/'pizhou',inp)
    return inp,scenes,folder


class OperatingLP(prior.StationLP):
    def bounds_for(self,prepared,failed):
        common,bounds,full,largest,bp,bn=super().bounds_for(prepared,failed)
        options=self.inp['followup_options']
        if failed<0 and options['reserve_only']:
            beta=self.inp['normal_reverse_limit_fraction']
            bp=np.zeros_like(bp);bn=-(1-beta)*full
        if failed>=0 and options['local_fault']:
            bounds=[bound if failed in (a[5],a[6]) else (0.,0.) for a,bound in zip(self.arcs,bounds)]
        return common,bounds,full,largest,bp,bn


def build(inp,scenes,case,selected):
    m,meta=prior.build(inp,scenes,case,selected)
    options=inp['followup_options'];ids=list(inp['stations'])
    if options['local_fault']:
        edges={e['id']:e for e in inp['network']['edges']}
        for y,h,f,eid,d,v in meta['network_flows']:
            e=edges[eid];ends={inp['network']['feeders'][e[k]]['station'] for k in ('a','b')}
            if f>=0 and ids[f] not in ends:m.upper_bounds[v]=0.
    if options['reserve_only']:
        for y in inp['years']:
            for j,sid in enumerate(ids):
                terms={v:prior.old.PF*r for (s,slot,yy,r),v in meta['x'].items() if s==sid and yy==y}
                if (sid,y) in meta['third']:terms[meta['third'][sid,y]]=prior.old.PF*50.
                # 正常方式不依赖储能，站间供区固定；正反向原生负荷极值均检查。
                m.constraint(terms,lower=max(0.,float(scenes[y][:,j].max())))
                m.constraint({v:inp['normal_reverse_limit_fraction']*r for v,r in terms.items()},
                    lower=max(0.,float(-scenes[y][:,j].min())))
    if options.get('station_floor'):
        for y in inp['years']:
            for sid in ids:
                terms={v:r for (s,slot,yy,r),v in meta['x'].items() if s==sid and yy==y}
                if (sid,y) in meta['third']:terms[meta['third'][sid,y]]=50.
                m.constraint(terms,lower=inp['station_floor_by_year'][str(y)][sid])
    return m,meta


def best(policy,case):
    folders=[p.parent for p in (RAW/'邳州'/policy).glob(case+'*/summary.json')]
    return min(folders,key=lambda p:json.loads((p/'summary.json').read_text())['cost_npv_10k']) if folders else None


def warm_start(inp,scenes,source,out):
    """共同工程条件的可行设备起点；原方案目录保持只读。"""
    ids=list(inp['stations']);lp=OperatingLP(inp);records=[];projects=prior.old.base.previous.rows(source/'projects.csv')
    previous=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]);previous_n=np.zeros(len(ids),dtype=int)
    for y in inp['years']:
        units,n,built=prior.old.assets_from_csv(inp,source,y);units=np.maximum(units,previous);n=np.maximum(n,previous_n)
        if inp['followup_options']['reserve_only']:
            for j,(sid,s) in enumerate(inp['stations'].items()):
                need=max(0.,scenes[y][:,j].max()/prior.old.PF,-scenes[y][:,j].min()/(.8*prior.old.PF))
                if units[j].sum()+1e-8>=need:continue
                choices=[]
                for a,b,c in itertools.product(*[sorted({units[j,k],*[r for r in inp['new_ratings'] if r>=units[j,k]]}) for k in (0,1)],
                                               ([units[j,2],50.] if s['allow_third'] else [0.])):
                    if a>b or a+b+c<need-1e-8:continue
                    cost=(a if a>units[j,0] else 0)+(b if b>units[j,1] else 0)+100*int(c>units[j,2])
                    choices.append((cost,a,b,c))
                assert choices,(sid,need)
                units[j]=min(choices)[1:]
        for p in scenes[y]:
            ready=lp.prepared(p,y,units,n,built)
            for f in range(-1,len(ids)):
                r=lp.check(p,ready,f)
                if not r['verified']:
                    assert f>=0 or not inp['followup_options']['reserve_only']
                    for sid,deficit in r['station_deficits'].items():
                        j=ids.index(sid);s=inp['stations'][sid]
                        coefficient=min(.1,.215*.76/max(1,s['forward_duration_h']),.215*.76/max(1,s['reverse_duration_h']))
                        n[j]+=math.ceil((deficit+1e-7)/coefficient)
                    ready=lp.prepared(p,y,units,n,built)
        for j,sid in enumerate(ids):records.append(dict(year=y,station=sid,unit_1_mva=units[j,0],unit_2_mva=units[j,1],
            unit_3_mva=units[j,2],storage_modules=int(n[j]),storage_mwh=float(n[j]*.215)))
        previous=units;previous_n=n.copy()
    out.mkdir(parents=True,exist_ok=True);prior.write_csv(out/'stations.csv',records);prior.write_csv(out/'projects.csv',projects)
    return out


def run(policy,case,seconds=100.,attempt='main'):
    inp,scenes,folder=prepare(policy);out=folder/(case+'_'+attempt);out.mkdir(exist_ok=True)
    if (out/'summary.json').exists():return json.loads((out/'summary.json').read_text())
    source=prior.best_folder(prior.OUT/'pizhou/compressed_reverse80','rigid' if case=='rigid' else 'elastic_free')
    if inp['followup_options'].get('station_floor'):source=ROOT/inp['station_floor_reference']
    earlier=[p.parent for p in folder.glob(case+'*/summary.json')]
    if earlier:source=min(earlier,key=lambda p:json.loads((p/'summary.json').read_text())['cost_npv_10k'])
    selected={tuple(r) for r in json.loads((source/'selected_pairs.json').read_text())}
    selected.update((y,h,-1) for y in inp['years'] for h in range(len(scenes[y])))
    lp=OperatingLP(inp);warm=warm_start(inp,scenes,source,out/'warm_start');history=[];bounds=[]
    for iteration in range(1,9):
        m,meta=build(inp,scenes,case,selected)
        z,result=prior.old.base.parameters.solve(m,out,f'iteration_{iteration:02}',seconds,.01,
            dict(inp,storage_usable_energy_fraction=1.),meta,warm)
        if result.get('dual_bound') is not None:bounds.append(result['dual_bound'])
        if z is None or not result.get('feasible_incumbent'):
            prior.dump(out/'failed_search.json',dict(solver=result,history=history));return None
        checks,violations,detail=prior.old.base.check_all(inp,scenes,z,meta,lp)
        summary,station_rows,project_rows=prior.old.base.network.extract(inp,None,case,z,meta,result,history,checks)
        candidate=out/f'candidate_{iteration:02}';candidate.mkdir(exist_ok=True)
        prior.write_csv(candidate/'stations.csv',station_rows);prior.write_csv(candidate/'projects.csv',project_rows)
        history.append(dict(iteration=iteration,selected_pairs=len(selected),solver=result,checks=checks))
        print('FOLLOWUP_CHECK',policy,case,iteration,'failures',len(violations),'cost',summary['cost_npv_10k'],flush=True)
        if violations:
            added={(y,h,f) for _,y,h,f in sorted(violations,reverse=True)[:40]};assert added-selected
            selected.update(added);warm=warm_start(inp,scenes,candidate,candidate/'warm_start');continue
        result['dual_bound']=max(bounds);result['mip_gap']=max(0.,(result['objective']-result['dual_bound'])/result['objective'])
        summary.update(case=case,policy=policy,region='pizhou',solver=result,checks=checks,history=history,
            input_sha256=prior.sha(folder/'inputs.json'),scope='逐站容量不退减的主变替代对照；以刚性建设方案为逐站容量基础' if inp['followup_options'].get('station_floor') else '共同运行条件下的费用寻优；未加刚弹容量差或储能线路排序约束')
        prior.dump(out/'summary.json',summary);prior.write_csv(out/'years.csv',summary['annual'])
        prior.write_csv(out/'stations.csv',station_rows);prior.write_csv(out/'projects.csv',project_rows)
        prior.dump(out/'selected_pairs.json',sorted(selected));np.savez_compressed(out/'chosen_solution.npz',solution=z)
        prior.dump(out/'independent_lp.json',dict(verified=True,checks=checks,records=detail))
        print('FOLLOWUP_DONE',policy,case,summary['cost_npv_10k'],[(a['year'],a['capacity_mva'],a['storage_mwh'],a['cumulative_lines']) for a in summary['annual']],flush=True)
        return summary
    raise RuntimeError('运行约束分离尚未完成')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--policy',choices=list(POLICIES),default='standby')
    p.add_argument('--case',choices=['rigid','elastic_free']);p.add_argument('--seconds',type=float,default=100.)
    p.add_argument('--attempt',default='main');a=p.parse_args()
    if a.case:run(a.policy,a.case,a.seconds,a.attempt)
    else:
        with ProcessPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(run,a.policy,case,a.seconds,a.attempt) for case in ('rigid','elastic_free')]
            for f in as_completed(futures):f.result()
