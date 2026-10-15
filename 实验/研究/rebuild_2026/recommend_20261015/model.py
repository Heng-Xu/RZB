"""年度固定比例供区调整、直接事故转接及明示的规划选择条件。"""
import argparse
import copy
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

from ..review_20261015 import cases as old
from ..review_20261015_followup import cases as followup

ROOT=old.ROOT
RAW=ROOT/'研究报告/试算/20261015_增容替代推荐'
PUBLIC=ROOT/'研究报告/01研究推荐/当前版/增容替代推荐_20261015'
REVIEW=ROOT/'研究报告/05_review/当前版/1015增容替代推荐'
SOURCE=ROOT/'研究报告/数据来源/当前版/增容替代推荐_20261015'
PREFERENCE=dict(min_capacity_ratio=1.05,max_storage_ratio=.5,final_line_reduction=2)


def prepare():
    source=old.OUT/'pizhou/compressed_reverse80/inputs.json';inp=json.loads(source.read_text())
    inp.update(normal_supply_area_fixed=False,recommendation_basis='增容替代偏好，年度正常转供比例固定，事故仅直接转接',
        normal_transfer_policy='各年各通道按送端正向净负荷固定比例分配；比例为规划代理，不是逐段实际开关及全年SOC模型',
        recommendation_source_sha256=old.sha(source),selection_preference=PREFERENCE)
    folder=RAW/'邳州';folder.mkdir(parents=True,exist_ok=True)
    if (folder/'inputs.json').exists():assert json.loads((folder/'inputs.json').read_text())==inp
    else:old.dump(folder/'inputs.json',inp)
    scenes=old.old.base.load_scenes(old.old.base.OUT/'pizhou',inp)
    return inp,scenes,folder


class OperatingLP(old.StationLP):
    def bounds_for(self,prepared,failed):
        common,bounds,full,largest,bp,bn=super().bounds_for(prepared,failed)
        if failed<0:
            bp=np.zeros_like(bp);bn=-(1-self.inp['normal_reverse_limit_fraction'])*full
        else:
            bounds=[bound if failed in (arc[5],arc[6]) else (0.,0.) for arc,bound in zip(self.arcs,bounds)]
        return common,bounds,full,largest,bp,bn

    def dispatch_fixed(self,p,prepared,f,normal_fractions=None):
        if f>=0:return self.dispatch(p,prepared,f)
        common,bounds,full,largest,bp,bn=self.bounds_for(prepared,-1)
        flow=np.array([(normal_fractions or {}).get((arc[1]['id'],arc[2]),0.)*max(0.,p[arc[5]]) for arc in self.arcs])
        rhs=np.r_[common,full+bp-p,full+bn+p]
        violation=max(0.,float(np.max(self.matrix@flow-rhs)),float(-flow.min()),
            max(float(v-upper) for v,(_,upper) in zip(flow,bounds)))
        return dict(verified=violation<1e-5,max_violation_mw=violation,flow=[[j,float(v)] for j,v in enumerate(flow) if v>1e-8],
            total_mw=float(flow.sum()),existing_mw=float(sum(v for arc,v in zip(self.arcs,flow) if arc[1]['existing'])))


def build(inp,scenes,case,selected,reference=None):
    m,meta=old.build(inp,scenes,'rigid' if case=='rigid' else 'elastic_free',selected)
    ids=list(inp['stations']);index={s:j for j,s in enumerate(ids)};edges={e['id']:e for e in inp['network']['edges']}
    station_flows={};normal_vars={};normal_station={}
    for y,h,f,eid,d,v in meta['network_flows']:
        e=edges[eid];a,b=(e['a'],e['b']) if d==0 else (e['b'],e['a'])
        sa=inp['network']['feeders'][a]['station'];sb=inp['network']['feeders'][b]['station']
        if f>=0 and ids[f] not in (sa,sb):m.upper_bounds[v]=0.
        station_flows.setdefault((y,h,f,sa),{})[v]=1.;station_flows.setdefault((y,h,f,sb),{})[v]=-1.
        if f<0:
            key=(y,eid,d)
            if key not in normal_vars:
                normal_vars[key]=m.variable(0.,upper=1.,integer=0)
                normal_station.setdefault((y,sa),{})[normal_vars[key]]=1.
            scale=max(0.,float(scenes[y][h,index[sa]]))
            m.constraint({v:1.,normal_vars[key]:-scale},0.,0.)
    for terms in normal_station.values():m.constraint(terms,upper=1.)
    # 正常方式不依赖事故备用储能，供区仍允许按年选择固定比例调整。
    for y,h,f in sorted(selected):
        if f>=0:continue
        for j,sid in enumerate(ids):
            full={v:old.old.PF*r for (s,slot,yy,r),v in meta['x'].items() if s==sid and yy==y}
            if (sid,y) in meta['third']:full[meta['third'][sid,y]]=old.old.PF*50.
            net=station_flows.get((y,h,-1,sid),{})
            m.constraint({**full,**net},lower=float(scenes[y][h,j]))
            m.constraint({**{v:.8*r for v,r in full.items()},**{v:-r for v,r in net.items()}},lower=-float(scenes[y][h,j]))
    if reference:
        for y in inp['years']:
            r=reference[y]
            m.constraint(old.old.base.previous.capacity_terms(inp,meta,y),lower=PREFERENCE['min_capacity_ratio']*r['capacity_mva'])
            m.constraint({v:1. for (sid,yy),v in meta['modules'].items() if yy==y},upper=math.floor(r['storage_mwh']/.215*PREFERENCE['max_storage_ratio']+1e-8))
            limit=r['cumulative_lines']-(PREFERENCE['final_line_reduction'] if y==inp['years'][-1] else 0)
            m.constraint({v:1. for (eid,yy),v in meta['edgevars'].items() if yy==y},upper=max(0,limit))
    meta['normal_fractions']=normal_vars
    return m,meta


def best(case):
    folders=[p.parent for p in (RAW/'邳州').glob(case+'*/summary.json') if json.loads(p.read_text()).get('case')==case]
    return min(folders,key=lambda p:json.loads((p/'summary.json').read_text())['cost_npv_10k']) if folders else None


def check_all(inp,scenes,z,meta):
    lp=OperatingLP(inp);checks=[];violations=[];detail=[]
    fractions={y:{(eid,d):float(z[v]) for (yy,eid,d),v in meta['normal_fractions'].items() if yy==y} for y in inp['years']}
    for y in inp['years']:
        units,n,_,_=old.old.base.assets.assets(inp,z,meta,y)
        built={eid for (eid,yy),v in meta['edgevars'].items() if yy==y and z[v]>.5};failures=[]
        for h,p in enumerate(scenes[y]):
            ready=lp.prepared(p,y,units,n,built)
            for f in range(-1,len(inp['stations'])):
                r=lp.dispatch_fixed(p,ready,f,fractions[y]) if f<0 else lp.check(p,ready,f)
                item=dict(year=y,scenario=h,failed=f,**r);detail.append(item)
                if not r['verified']:
                    violations.append((r.get('deficit_mw',r.get('max_violation_mw',0.)),y,h,f));failures.append(item)
        checks.append(dict(year=y,checked_pairs=len(scenes[y])*(len(inp['stations'])+1),violating_pairs=len(failures),verified=not failures))
    return checks,violations,detail


def run(case,seconds=180.,attempt='main'):
    inp,scenes,folder=prepare();out=folder/(case+'_'+attempt);out.mkdir(exist_ok=True)
    if (out/'summary.json').exists():return
    reference=None
    if case=='elastic_selected':
        rigid=best('rigid');assert rigid
        reference={r['year']:r for r in json.loads((rigid/'summary.json').read_text())['annual']}
    previous=best(case)
    source=previous or followup.best('local_standby','rigid' if case=='rigid' else 'elastic_free')
    if case=='elastic_selected' and not previous:source=followup.best('station_floor','elastic_free')
    selected={tuple(r) for r in json.loads((source/'selected_pairs.json').read_text())}
    selected.update((y,h,-1) for y in inp['years'] for h in range(len(scenes[y])))
    warm=source;history=[];bounds=[]
    for iteration in range(1,9):
        m,meta=build(inp,scenes,case,selected,reference)
        z,result=old.old.base.parameters.solve(m,out,f'iteration_{iteration:02}',seconds,.005,dict(inp,storage_usable_energy_fraction=1.),meta,warm)
        if result.get('dual_bound') is not None:bounds.append(result['dual_bound'])
        if z is None or not result.get('feasible_incumbent'):
            old.dump(out/'failed_search.json',dict(solver=result,history=history));return
        checks,violations,detail=check_all(inp,scenes,z,meta)
        summary,stations,projects=old.old.base.network.extract(inp,None,case,z,meta,result,history,checks)
        history.append(dict(iteration=iteration,selected_pairs=len(selected),solver=result,checks=checks))
        candidate=out/f'candidate_{iteration:02}';candidate.mkdir(exist_ok=True)
        old.write_csv(candidate/'stations.csv',stations);old.write_csv(candidate/'projects.csv',projects)
        print('RECOMMEND_CHECK',case,iteration,'violations',len(violations),'cost',summary['cost_npv_10k'],flush=True)
        if violations:
            additions={(y,h,f) for _,y,h,f in sorted(violations,reverse=True)[:40]};assert additions-selected
            selected.update(additions);warm=candidate;continue
        result['dual_bound']=max(bounds);result['mip_gap']=max(0.,(result['objective']-result['dual_bound'])/result['objective'])
        summary.update(case=case,region='pizhou',solver=result,checks=checks,history=history,
            selection_conditions=PREFERENCE if reference else {},reference_annual=list(reference.values()) if reference else [],
            input_sha256=old.sha(folder/'inputs.json'),scope='年度正常转供比例固定、正常储能备用、直接N-1转接；规划偏好另列')
        old.dump(out/'summary.json',summary);old.write_csv(out/'years.csv',summary['annual'])
        old.write_csv(out/'stations.csv',stations);old.write_csv(out/'projects.csv',projects)
        fractions=[dict(year=y,edge=eid,direction=d,fraction=float(z[v])) for (y,eid,d),v in meta['normal_fractions'].items() if z[v]>1e-9]
        old.dump(out/'normal_fractions.json',fractions);old.dump(out/'selected_pairs.json',sorted(selected))
        np.savez_compressed(out/'chosen_solution.npz',solution=z);old.dump(out/'independent_lp.json',dict(verified=True,checks=checks,records=detail))
        print('RECOMMEND_DONE',case,summary['cost_npv_10k'],result['mip_gap'],[(a['year'],a['capacity_mva'],a['storage_mwh'],a['cumulative_lines']) for a in summary['annual']],flush=True)
        return
    raise RuntimeError('全工况分离未完成')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--case',choices=['rigid','elastic_free','elastic_selected'],required=True)
    p.add_argument('--seconds',type=float,default=180.);p.add_argument('--attempt',default='main');a=p.parse_args()
    run(a.case,a.seconds,a.attempt)
