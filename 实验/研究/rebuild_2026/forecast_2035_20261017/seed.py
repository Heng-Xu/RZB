"""较小的既有网络子问题，仅为完整逐年模型提供可行整数起点。"""
import argparse
import copy
import json
import math

import numpy as np

from . import run as m


def seed(case, seconds=90, compact=False):
    inp=json.loads((m.RAW/'inputs.json').read_text());z=np.load(m.RAW/'scenarios.npz')
    scenes={y:z[str(y)] for y in inp['years']};ids=list(inp['stations'])
    folder=m.RAW/(case+('_compact' if compact else '_seed'));folder.mkdir(exist_ok=True)
    small=copy.deepcopy(inp)
    chosen=[];groups={}
    for e in inp['network']['edges']:
        key=(tuple(sorted([e['station_a'],e['station_b']])),bool(e.get('new_bay_station')))
        if e['existing'] or (compact and groups.get(key,0)<2):
            chosen.append(e)
            if not e['existing']:groups[key]=groups.get(key,0)+1
    small['network']['edges']=chosen
    u=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]);n=np.zeros(len(u),int)
    states={};counts={};built={};rows=[]
    floor=m.base.old.old.base.floor_value(inp,'rigid_storage') if case=='rigid' else 0.
    for y in inp['years']:
        while u.sum()<floor*inp['annual_observed_peak_mw'][str(y)]-1e-7:
            candidates=[]
            for j,sid in enumerate(ids):
                for slot in [0,1]:
                    delta=80-u[j,slot]
                    if delta<1e-5 or (slot==0 and u[j,1]<80):continue
                    score=(max(scenes[y][:,j].max(),0.)/(.95*max(u[j,0],1.)))/delta
                    candidates.append((score,j,slot))
            _,j,slot=max(candidates);u[j,slot]=80.
        for j,(sid,s) in enumerate(inp['stations'].items()):
            bp=min(.1,.215*.76/max(1,s['forward_duration_h']));bn=min(.1,.215*.76/max(1,s['reverse_duration_h']))
            survive=.95*(u[j].sum()-u[j].max());rev=min(survive,.8*.95*u[j].sum())
            n[j]=max(n[j],math.ceil(max(0.,(scenes[y][:,j].max()-survive)/bp,(-scenes[y][:,j].min()-rev)/bn)+1e-8))
            rows.append(dict(year=y,station=sid,unit_1_mva=u[j,0],unit_2_mva=u[j,1],unit_3_mva=u[j,2],storage_modules=int(n[j])))
        states[y]=u.copy();counts[y]=n.copy();built[y]=set()
    m.write_csv(folder/'stations.csv',rows);(folder/'projects.csv').write_text('year,id\n',encoding='utf-8-sig')
    selected=set()
    # 起点设备的各故障最差缺口，由仅含可用边的等价LP计算。
    cached=m.RAW/'initial_selected.json'
    if cached.exists():selected={tuple(v) for v in json.loads(cached.read_text())}
    else:
        initial=np.array([s['initial_units']+[0.] for s in inp['stations'].values()])
        _,bad,_=m.check(small,scenes,{y:initial for y in inp['years']},{y:np.zeros(len(ids),int) for y in inp['years']},built)
        for y in inp['years']:
            for f in range(-1,len(ids)):
                found=[r for r in bad if r[1]==y and r[3]==f]
                if found:
                    _,yy,h,ff=max(found);selected.add((yy,h,ff))
        m.dump(cached,sorted(selected))
    for iteration in range(1,5):
        native,meta=m.base.build(small,scenes,case,selected)
        # 首轮子问题只用80MVA更换，压缩起点寻找时间，完整模型仍有全部规格。
        if not compact:
            for (sid,slot,y,r),v in meta['x'].items():
                if abs(r-inp['stations'][sid]['initial_units'][slot])>1e-8 and r!=80.:native.upper_bounds[v]=0.
        warm=m.RAW/(case+'_seed') if compact and iteration==1 else folder
        solution,result=m.base.old.old.base.parameters.solve(native,folder,f'seed_{iteration:02}',seconds,.05,
            dict(small,storage_usable_energy_fraction=1.),meta,warm)
        assert solution is not None and result['feasible_incumbent'],result
        summary,rows,projects=m.base.old.old.base.network.extract(small,None,case,solution,meta,result,[],[])
        m.write_csv(folder/'stations.csv',rows);m.write_csv(folder/'projects.csv',projects)
        # 原求解器读取空项目CSV也可正常运行，保留显式表头。
        if not projects:(folder/'projects.csv').write_text('year,id\n',encoding='utf-8-sig')
        for y in inp['years']:
            states[y],counts[y],_,_=m.base.old.old.base.assets.assets(inp,solution,meta,y)
            built[y]={eid for (eid,yy),v in meta['edgevars'].items() if yy==y and solution[v]>.5}
        checks,bad,detail=m.check(inp,scenes,states,counts,built)
        print('SEED_CHECK',case,iteration,summary['cost_npv_10k'],'violations',len(bad),flush=True)
        if not bad:
            m.dump(folder/'summary.json',summary);m.dump(folder/'selected_pairs.json',sorted(selected))
            m.dump(folder/'subproblem_checks.json',dict(checks=checks,records=detail))
            return
        for y in inp['years']:
            for f in range(-1,len(ids)):
                found=sorted([r for r in bad if r[1]==y and r[3]==f],reverse=True)[:2]
                selected.update((yy,h,ff) for _,yy,h,ff in found)
    raise RuntimeError('子问题未完成截面校核')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--case',required=True,choices=list(m.LABEL));p.add_argument('--seconds',type=float,default=90.)
    p.add_argument('--compact',action='store_true')
    a=p.parse_args();seed(a.case,a.seconds,a.compact)
