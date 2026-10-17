"""按年滚动前推：固定上年资产，决定当年措施，逐年完整校核。"""
import argparse
import copy
import json
import math

import numpy as np

from . import run as m


def run(case,seconds=20):
    inp=json.loads((m.RAW/'inputs.json').read_text());archive=np.load(m.RAW/'scenarios.npz')
    assert inp['forecast_basis']['sha256']==m.sha(m.FORECAST),'预测源已变化，须重新准备独立输入'
    scenes={y:archive[str(y)] for y in inp['years']};ids=list(inp['stations'])
    out=m.RAW/(case+'_rolling');out.mkdir(exist_ok=True)
    old=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]);oldn=np.zeros(len(ids),int)
    built=set();replaced=np.zeros((len(ids),2),bool);rows=[];projects=[];selected_all=set();history=[]
    for y in inp['years']:
        one=copy.deepcopy(inp);one['years']=[y]
        for j,sid in enumerate(ids):one['stations'][sid]['initial_units']=old[j,:2].tolist()
        baseline_checks,bad,_=m.check(one,{y:scenes[y]},{y:old},{y:oldn},{y:built})
        floor=m.base.old.old.base.floor_value(inp,'rigid_storage') if case=='rigid' else 0.
        selected=set()
        for f in range(-1,len(ids)):
            found=[r for r in bad if r[3]==f]
            if found:
                _,yy,h,ff=max(found);selected.add((yy,h,ff))
        stage=out/str(y);stage.mkdir(exist_ok=True)
        u=old.copy();n=oldn.copy();newbuilt=set(built)
        year_history=[]
        if bad or old.sum()<floor*inp['annual_observed_peak_mw'][str(y)]-1e-7:
            # 显式可行起点：补足分档下限后，以储能直接弥补本站截面缺口。
            warmu=old.copy()
            while warmu.sum()<floor*inp['annual_observed_peak_mw'][str(y)]-1e-7:
                possible=[]
                for j,sid in enumerate(ids):
                    for slot in [1,0]:
                        if replaced[j,slot]:continue
                        for rating in inp['new_ratings']:
                            if rating<=warmu[j,slot] or (slot==0 and rating>warmu[j,1]):continue
                            if case=='rigid' and warmu.sum()+rating-warmu[j,slot]>max(old.sum(),2*inp['annual_observed_peak_mw'][str(y)])+1e-7:continue
                            possible.append((rating-warmu[j,slot],j,slot,rating))
                assert possible
                _,j,slot,rating=min(possible);warmu[j,slot]=rating
            warmrows=[]
            for j,(sid,s) in enumerate(inp['stations'].items()):
                bp=min(.1,.215*.76/max(1,s['forward_duration_h']));bn=min(.1,.215*.76/max(1,s['reverse_duration_h']))
                survive=.95*(warmu[j].sum()-warmu[j].max());rev=min(survive,.8*.95*warmu[j].sum())
                count=max(int(oldn[j]),math.ceil(max(0.,(scenes[y][:,j].max()-survive)/bp,(-scenes[y][:,j].min()-rev)/bn)+1e-8))
                warmrows.append(dict(year=y,station=sid,unit_1_mva=warmu[j,0],unit_2_mva=warmu[j,1],unit_3_mva=warmu[j,2],storage_modules=count))
            warm=stage/'warm';warm.mkdir(exist_ok=True);m.write_csv(warm/'stations.csv',warmrows)
            m.write_csv(warm/'projects.csv',[dict(year=y,id=eid) for eid in sorted(built)])
            if not built:(warm/'projects.csv').write_text('year,id\n',encoding='utf-8-sig')
            for iteration in range(1,7):
                native,meta=m.base.build(one,{y:scenes[y]},case,selected)
                for (sid,slot,yy,r),v in meta['x'].items():
                    j=ids.index(sid)
                    if replaced[j,slot]:native.lower_bounds[v]=native.upper_bounds[v]=float(abs(r-old[j,slot])<1e-8)
                for (sid,yy),v in meta['third'].items():
                    if old[ids.index(sid),2]>0:native.lower_bounds[v]=native.upper_bounds[v]=1.
                for (sid,yy),v in meta['modules'].items():
                    native.lower_bounds[v]=int(oldn[ids.index(sid)])
                    native.upper_bounds[v]=max(native.upper_bounds[v],native.lower_bounds[v])
                for (eid,yy),v in meta['edgevars'].items():
                    if eid in built:native.lower_bounds[v]=native.upper_bounds[v]=1.
                solution,result=m.base.old.old.base.parameters.solve(native,stage,f'year_{iteration:02}',seconds,.03,
                    dict(one,storage_usable_energy_fraction=1.),meta,warm)
                assert solution is not None and result['feasible_incumbent'],(case,y,result)
                u,n,_,_=m.base.old.old.base.assets.assets(one,solution,meta,y)
                newbuilt={eid for (eid,yy),v in meta['edgevars'].items() if solution[v]>.5}
                checks,violations,detail=m.check(one,{y:scenes[y]},{y:u},{y:n},{y:newbuilt})
                year_history.append(dict(iteration=iteration,solver=result,checks=checks))
                m.write_csv(warm/'stations.csv',[dict(year=y,station=sid,unit_1_mva=u[j,0],unit_2_mva=u[j,1],unit_3_mva=u[j,2],storage_modules=int(n[j])) for j,sid in enumerate(ids)])
                m.write_csv(warm/'projects.csv',[dict(year=y,id=eid) for eid in sorted(newbuilt)])
                if not newbuilt:(warm/'projects.csv').write_text('year,id\n',encoding='utf-8-sig')
                if not violations:break
                for f in range(-1,len(ids)):
                    found=sorted([r for r in violations if r[3]==f],reverse=True)[:2]
                    selected.update((yy,h,ff) for _,yy,h,ff in found)
            else:raise RuntimeError((case,y,'年度截面校核未通过'))
        assert np.all(u>=old) and np.all(n>=oldn) and newbuilt>=built
        changed=u[:,:2]>old[:,:2]+1e-8
        assert not np.any(changed&replaced);replaced|=changed
        rows.extend(dict(year=y,station=sid,unit_1_mva=u[j,0],unit_2_mva=u[j,1],unit_3_mva=u[j,2],storage_modules=int(n[j])) for j,sid in enumerate(ids))
        projects.extend(dict(year=y,id=eid) for eid in sorted(newbuilt-built))
        selected_all.update(selected);history.append(dict(year=y,method='固定上年资产的逐年费用寻优',history=year_history))
        old,oldn,built=u,n,newbuilt
        m.write_csv(out/'stations.csv',rows);m.write_csv(out/'projects.csv',projects)
        if not projects:(out/'projects.csv').write_text('year,id\n',encoding='utf-8-sig')
        print('ROLLING_YEAR',case,y,'capacity',u.sum(),'storage',n.sum()*.215,'lines',len(built),flush=True)
    m.dump(out/'selected_pairs.json',sorted(selected_all));m.dump(out/'rolling_history.json',history)
    certify(case,out)


def certify(case,folder):
    inp=json.loads((m.RAW/'inputs.json').read_text());archive=np.load(m.RAW/'scenarios.npz')
    scenes={y:archive[str(y)] for y in inp['years']};ids=list(inp['stations'])
    selected={tuple(r) for r in json.loads((folder/'selected_pairs.json').read_text())}
    native,meta=m.base.build(inp,scenes,case,selected)
    lookup={(int(r['year']),r['station']):r for r in m.base.old.old.base.previous.rows(folder/'stations.csv')}
    projects=m.base.old.old.base.previous.rows(folder/'projects.csv')
    def fix(v,value):native.lower_bounds[v]=native.upper_bounds[v]=value
    for (sid,slot,y,r),v in meta['x'].items():fix(v,float(abs(float(lookup[y,sid][f'unit_{slot+1}_mva'])-r)<1e-8))
    for (sid,y),v in meta['third'].items():fix(v,float(lookup[y,sid]['unit_3_mva'])/50.)
    for (sid,y),v in meta['modules'].items():fix(v,int(lookup[y,sid]['storage_modules']))
    for (eid,y),v in meta['edgevars'].items():fix(v,float(any(e['id']==eid and int(e['year'])<=y for e in projects)))
    z,result=m.base.old.old.base.parameters.solve(native,folder,'complete_model_fixed_layout',60.,.0001,
        dict(inp,storage_usable_energy_fraction=1.),meta,folder)
    assert z is not None and result['feasible_incumbent']
    units={};numbers={};built={}
    for y in inp['years']:
        units[y],numbers[y],_,_=m.base.old.old.base.assets.assets(inp,z,meta,y)
        built[y]={eid for (eid,yy),v in meta['edgevars'].items() if yy==y and z[v]>.5}
    checks,bad,detail=m.check(inp,scenes,units,numbers,built);assert not bad
    summary,station_rows,project_rows=m.base.old.old.base.network.extract(inp,None,case,z,meta,result,[],checks)
    bounds=[0.]
    for p in m.RAW.glob(case+'_*/iteration_*_solver.json'):
        value=json.loads(p.read_text()).get('dual_bound')
        if value is not None:bounds.append(value)
    result['fixed_layout_bound']=result['dual_bound'];result['dual_bound']=max(bounds)
    assert result['dual_bound']<=result['objective']+1e-5
    result['mip_gap']=max(0.,(result['objective']-result['dual_bound'])/max(1.,abs(result['objective'])))
    result.update(accepted=False,status='逐年方案通过完整模型固定设备复核；全局下界来自独立联合模型松弛')
    summary.update(region='city',case=case,baseline='annual_2021',solver=result,checks=checks,
        input_sha256=m.sha(m.RAW/'inputs.json'),forecast_sha256=m.sha(m.FORECAST),scope=inp['scope'],
        planning_method='逐年滚动：上一年已投运资产固定，计算当年新增；完整联合模型固定设备复核',
        optimality='逐年可行方案，非十年联合全局最优')
    m.dump(folder/'summary.json',summary);m.write_csv(folder/'years.csv',summary['annual'])
    m.write_csv(folder/'stations.csv',station_rows);m.write_csv(folder/'projects.csv',project_rows)
    if not project_rows:(folder/'projects.csv').write_text('year,id\n',encoding='utf-8-sig')
    np.savez_compressed(folder/'chosen_solution.npz',solution=z)
    m.dump(folder/'independent_lp.json',dict(verified=True,checks=checks,records=detail))
    print('ROLLING_DONE',case,summary['cost_npv_10k'],result['mip_gap'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--case',required=True,choices=list(m.LABEL));p.add_argument('--seconds',type=float,default=20.)
    a=p.parse_args();run(a.case,a.seconds)
