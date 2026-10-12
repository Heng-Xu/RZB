"""补齐地区与各站局部极值静态工况后，比较刚性及弹性方案。"""
import argparse
import copy
import json
import math
from collections import defaultdict

import numpy as np

from . import run as parameters
from .capacity_audit import snapshots,FlowLP,PROFILES

ROOT=parameters.ROOT
OUT=ROOT/'研究报告/试算/20261012_案例承载力复核_存量网络固定'
REVIEW=ROOT/'研究报告/05_review/当前版/1012案例承载力复核'
RESULT=ROOT/'研究报告/01研究推荐/当前版/案例承载力复核_20261012'
CASES=('rigid_storage','elastic_floor_2','elastic_no_floor')
dump=parameters.dump;write_csv=parameters.write_csv;sha=parameters.sha
previous=parameters.previous;network=parameters.network;assets=parameters.assets_model
PF=parameters.PF


def prepare():
    for region in ('city','pizhou'):
        root=OUT/region
        if (root/'inputs.json').exists():raise FileExistsError(root)
        root.mkdir(parents=True,exist_ok=True)
        source=parameters.OUT/region
        initial=json.loads((source/'inputs.json').read_text())
        # 转供收资对应2025实际设备；先在这个参考条件下标定存量通道。
        # 原共同压缩设备不参与标定，随后只用于规划方案及接收容量校核。
        seed=json.loads((previous.OUT/region/'inputs.json').read_text())
        peak_scenes=previous.load_scenes(previous.OUT/region,seed)
        seed['transfer_calibration_year']=2025
        seed['transfer_calibration_net_mw']={s:float(peak_scenes[2025][0,j]) for j,s in enumerate(seed['stations'])}
        seed['transfer_calibration_forward_mw']={s:max(v,0.) for s,v in seed['transfer_calibration_net_mw'].items()}
        seed['transfer_calibration_capacity_mva']={s:r['asset_capacity_mva'] or sum(r['initial_units']) for s,r in seed['stations'].items()}
        inp=parameters.calibrate(seed,initial['initial_transfer_fraction'])
        for key in ('line_cable_fraction','line_capex_10k','line_cost_coefficient','line_basis','parameter_changes'):
            inp[key]=initial[key]
        inp['transfer_reference_basis']='2025年站级统计容量及同期负荷标定既有通道；三座市区缺设备行站保留原模拟设备且无通道'
        inp['transfer_reference_audit']=copy.deepcopy(inp['initial_transfer_audit'])
        compressed=copy.deepcopy(inp)
        compressed['transfer_calibration_year']=2021
        compressed['transfer_calibration_net_mw']={s:v*inp['initial_peak_mw']/inp['annual_observed_peak_mw']['2025'] for s,v in inp['transfer_calibration_net_mw'].items()}
        compressed['transfer_calibration_forward_mw']={s:max(v,0.) for s,v in compressed['transfer_calibration_net_mw'].items()}
        compressed['transfer_calibration_capacity_mva']={s:sum(r['initial_units']) for s,r in inp['stations'].items()}
        inp['compressed_initial_transfer_audit']=parameters.initial_transfer_audit(compressed)
        base,records=snapshots(region,inp)
        inp['scope']='实际年度负荷；地区峰值及各站局部极值同期静态截面；正常与单台最大主变N-1'
        inp['static_scene_limit']='有限静态截面覆盖各站正向峰值与最低净负荷；保留原补值与年度缩放，储能使用原静态有效功率'
        inp['snapshot_source_sha256']=sha(PROFILES/f'{region}_stations.npz')
        inp['parameter_input_sha256']=sha(source/'inputs.json')
        inp['capacity_snapshot_count']=len(base)
        inp['station_snapshot_roles']=records
        inp['source_start_normalization']='各站同期矢量按地区2021净峰值统一缩放，年度再按原统计峰值缩放；各站峰值不叠加'
        scenes=[]
        for y in inp['years']:
            for h,p in enumerate(base*inp['annual_observed_peak_mw'][str(y)]/inp['initial_peak_mw']):
                for j,s in enumerate(inp['stations']):
                    scenes.append(dict(year=y,scenario=h,station=s,power_mw=float(p[j]),
                                       source_hour=records[h]['source_hour'],roles=records[h]['roles'],
                                       all_stations_observed=records[h]['all_stations_observed']))
        dump(root/'inputs.json',inp);write_csv(root/'静态工况.csv',scenes)
        np.savez_compressed(root/'static_base.npz',power_base_mw=base)
        print('PREPARED capacity',region,len(base),'snapshots',flush=True)


def load_scenes(root,inp):
    base=np.load(root/'static_base.npz')['power_base_mw']
    assert base.shape==(inp['capacity_snapshot_count'],len(inp['stations']))
    return {y:base*inp['annual_observed_peak_mw'][str(y)]/inp['initial_peak_mw'] for y in inp['years']}


def floor_value(inp,case):
    if case=='elastic_floor_2':return 2.
    if case=='rigid_storage':return previous.guide_range(inp['growth_rate'])[0]
    return 0.


def _build(inp,scenes,case,selected):
    # 只复用原设备投资约束；所有运行工况在下方显式添加。
    base_case='rigid_storage' if case=='rigid_storage' else 'elastic_storage'
    m,meta=network.build(inp,np.zeros((1,len(inp['stations']))),[],base_case)
    original=defaultdict(dict)
    for row,col,value in m.entries:original[row][col]=value
    ids=list(inp['stations']);caps={};flowmeta=[]
    for y in inp['years']:
        peak=inp['annual_observed_peak_mw'][str(y)];meta['peaks'][y]=peak
        total=previous.capacity_terms(inp,meta,y)
        matches=[row for row,terms in original.items() if terms==total];assert len(matches)==1
        m.constraint_lower[matches[0]]=floor_value(inp,case)*peak
        m.constraint_upper[matches[0]]=inp['physical_capacity_upper_mva']
        if case=='rigid_storage':
            prev=previous.capacity_terms(inp,meta,y-1) if y>inp['years'][0] else {}
            previous.retain_existing_upper(m,total,prev,inp['initial_capacity_mva'],2*peak,inp['physical_capacity_upper_mva'])
        for j,(sid,s) in enumerate(inp['stations'].items()):
            maxp=float(np.max(abs(scenes[y][:,j])))
            m.upper_bounds[meta['modules'][sid,y]]=math.ceil(maxp*max(s['forward_duration_h'],s['reverse_duration_h'],2.15)/(.215*.76))+1
            full={v:r for (ss,slot,yy,r),v in meta['x'].items() if ss==sid and yy==y}
            if (sid,y) in meta['third']:full[meta['third'][sid,y]]=50
            for f in range(-1,len(ids)):
                variants=[full]
                if f==j:
                    cap={v:r for (ss,slot,yy,r),v in meta['x'].items() if ss==sid and yy==y and slot!=1}
                    if (sid,y) in meta['third']:cap[meta['third'][sid,y]]=50
                    variants=[cap]
                    if s['allow_third'] and max(s['initial_units'])<50:
                        c3={v:r for (ss,slot,yy,r),v in meta['x'].items() if ss==sid and yy==y}
                        one=m.variable(0);m.lower_bounds[one]=1
                        c3[one]=50;c3[meta['third'][sid,y]]=-50;variants.append(c3)
                caps[sid,y,f]=variants
        edge_map={e['id']:e for e in inp['network']['edges']}
        for yy,h,f in sorted(selected):
            if yy!=y:continue
            start=len(flowmeta)
            network.add_network_scene(m,inp,scenes[y][h],y,f,caps,meta['modules'],meta['edgevars'],flowmeta)
            existing=defaultdict(dict)
            for _,_,eid,d,v in flowmeta[start:]:
                e=edge_map[eid]
                if e['existing']:
                    a=e['a'] if d==0 else e['b']
                    existing[inp['network']['feeders'][a]['station']][v]=1
            for sid,terms in existing.items():m.constraint(terms,upper=inp['existing_transfer_budget_mw'][sid])
            flowmeta[start:]=[(yy,h,ff,e,d,v) for yy,ff,e,d,v in flowmeta[start:]]
    meta['network_flows']=flowmeta
    return m,meta


def build(inp,scenes,case,selected):
    saved_limits=network.limits
    network.limits=parameters.limits
    try:return _build(inp,scenes,case,selected)
    finally:network.limits=saved_limits


def check_all(inp,scenes,z,meta,lp):
    checks=[];violations=[];detail=[]
    for y in inp['years']:
        units,n,_,_=assets.assets(inp,z,meta,y)
        built={eid for (eid,yy),v in meta['edgevars'].items() if yy==y and z[v]>.5}
        failures=[];calls=0;worst=0.
        for h,p in enumerate(scenes[y]):
            ready=lp.prepared(p,y,units,n,built)
            for f in range(-1,len(inp['stations'])):
                r=lp.check(p,ready,f)
                if not r.get('direct'):calls+=1
                row=dict(year=y,scenario=h,failed_station=lp.ids[f] if f>=0 else 'normal',**r)
                detail.append(row)
                if not r['verified']:
                    violations.append((r['deficit_mw'],y,h,f));failures.append(row);worst=max(worst,r['deficit_mw'])
        checks.append(dict(year=y,checked_pairs=len(scenes[y])*(len(inp['stations'])+1),
                           independent_lp_calls=calls,direct_checks=len(scenes[y])*(len(inp['stations'])+1)-calls,
                           violating_pairs=len(failures),max_deficit_mw=worst,verified=not failures))
    return checks,violations,detail


def run(region,case,seconds=120):
    root=OUT/region;out=root/case;out.mkdir(exist_ok=True)
    if (out/'summary.json').exists():raise FileExistsError(out)
    inp=json.loads((root/'inputs.json').read_text());scenes=load_scenes(root,inp)
    lp=FlowLP(inp);selected=set()
    for y in inp['years']:
        for h,r in enumerate(inp['station_snapshot_roles']):
            if '地区正向峰值' in r['roles'] or '地区最低净负荷' in r['roles']:
                selected.update((y,h,f) for f in range(-1,len(inp['stations'])))
    warm=parameters.OUT/region/('floor_2' if case=='elastic_floor_2' else 'no_floor')
    if case=='rigid_storage':warm=previous.OUT/region/'rigid_storage'
    history=[];bounds=[]
    for iteration in range(1,11):
        m,meta=build(inp,scenes,case,selected)
        z,result=parameters.solve(m,out,f'iteration_{iteration:02}',seconds,.01,
                                 dict(inp,storage_usable_energy_fraction=1.),meta,warm)
        if result.get('dual_bound') is not None:bounds.append(result['dual_bound'])
        if z is None or not result.get('feasible_incumbent'):
            dump(out/'failed_search.json',dict(solver=result,history=history));return
        checks,violations,detail=check_all(inp,scenes,z,meta,lp)
        history.append(dict(iteration=iteration,selected_pairs=len(selected),solver=result,checks=checks))
        summary,stations,projects=network.extract(inp,None,case,z,meta,result,history,checks)
        candidate=out/f'candidate_{iteration:02}';candidate.mkdir(exist_ok=True)
        write_csv(candidate/'stations.csv',stations);write_csv(candidate/'projects.csv',projects)
        dump(candidate/'summary.json',summary);warm=candidate
        print('CAPACITY_CHECK',region,case,iteration,'failed',len(violations),
              'worst',max((v[0] for v in violations),default=0.),flush=True)
        if violations:
            added={(y,h,f) for _,y,h,f in sorted(violations,reverse=True)[:40]}
            assert added-selected,'运行LP与优化约束应一致'
            selected.update(added);continue
        result['dual_bound']=max(bounds)
        result['mip_gap']=max(0.,(result['objective']-result['dual_bound'])/max(1.,abs(result['objective'])))
        result['bound_basis']='静态工况逐次加入后保留的最强有效下界'
        summary.update(region=region,case=case,solver=result,clr_floor=floor_value(inp,case),
                       scope=inp['scope'],input_sha256=sha(root/'inputs.json'),
                       static_network_checks=summary.pop('full_hour_network_checks'),
                       source_profile_sha256=inp['snapshot_source_sha256'])
        old=inp['initial_capacity_mva']
        for a in summary['annual']:
            a['net_capacity_increment_mva']=a['capacity_mva']-old
            a['passive_exceedance']=case=='rigid_storage' and a['capacity_mva']>2*a['peak_mw']+1e-5
            assert a['capacity_mva']>=old-1e-5 and a['clr']>=summary['clr_floor']-1e-6
            if case=='rigid_storage':assert a['capacity_mva']<=max(old,2*a['peak_mw'])+1e-5
            old=a['capacity_mva']
        np.savez_compressed(out/'chosen_solution.npz',solution=z)
        dump(out/'summary.json',summary);write_csv(out/'years.csv',summary['annual'])
        write_csv(out/'stations.csv',stations);write_csv(out/'projects.csv',projects)
        dump(out/'independent_lp.json',dict(verified=True,records=detail,checks=checks))
        dump(out/'selected_pairs.json',sorted(selected))
        print('COMPLETE_CAPACITY',region,case,summary['cost_npv_10k'],flush=True)
        return
    raise RuntimeError('局部工况分离未收敛；不得交付')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prepare',action='store_true');p.add_argument('--region',choices=('city','pizhou'))
    p.add_argument('--case',choices=CASES);p.add_argument('--seconds',type=int,default=120)
    a=p.parse_args()
    if a.prepare:prepare()
    if a.region and a.case:run(a.region,a.case,a.seconds)
