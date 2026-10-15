"""正常及N-1共同参与的静态替代规划；新购主变在四年期内不重复更换。"""
import argparse
import copy
import json
from pathlib import Path

import numpy as np

from ..review_20261015 import cases as old

ROOT=old.ROOT
RAW=ROOT/'研究报告/试算/20261015_静态联合替代'
PUBLIC=ROOT/'研究报告/01研究推荐/当前版/静态联合替代_20261015'
REVIEW=ROOT/'研究报告/05_review/当前版/1015静态联合替代'
SOURCE=ROOT/'研究报告/数据来源/当前版/静态联合替代_20261015'
REGIONS={'pizhou':'邳州','city':'市区'}
BASELINES={'compressed':'共同仿真起点','annual_2021':'保留2021原表容量'}
CASES={'rigid':'刚性方案','elastic_free':'弹性经济优选方案'}
OperatingLP=old.StationLP


def prepare(region,baseline):
    src=old.OUT/region/(baseline+'_reverse80')/'inputs.json'
    inp=copy.deepcopy(json.loads(src.read_text()))
    inp.update(planning_start_year=2022,fixed_baseline_year=2021,normal_supply_area_fixed=False,
        normal_storage_policy='正常与N-1分别按有效功率和持续时间校核，共用同一套在役储能',
        normal_transfer_policy='代表工况分别优化负荷转供，受逐站预算、通道及接收侧约束',
        procurement_policy='每一主变位置在2022—2025最多更换一次；新购主变在期内继续在役',
        selection_conditions={},static_joint_source_sha256=old.sha(src))
    root=RAW/region/baseline;root.mkdir(parents=True,exist_ok=True)
    if (root/'inputs.json').exists():assert json.loads((root/'inputs.json').read_text())==inp
    else:old.dump(root/'inputs.json',inp)
    scenes=old.old.base.load_scenes(old.old.base.OUT/region,inp)
    return inp,scenes,root


def build(inp,scenes,case,selected):
    m,meta=old.build(inp,scenes,case,selected)
    # 对每一非初始规格，选中后在后续年维持。禁止31.5→50等四年内二次采购。
    for (sid,slot,y,r),v in meta['x'].items():
        if y==inp['years'][0] or abs(r-inp['stations'][sid]['initial_units'][slot])<1e-8:continue
        m.constraint({v:1.,meta['x'][sid,slot,y-1,r]:-1.},lower=0.)
    return m,meta


def best(region,baseline,case):
    paths=[p.parent for p in (RAW/region/baseline).glob(case+'*/summary.json')
           if json.loads(p.read_text()).get('case')==case]
    return min(paths,key=lambda p:json.loads((p/'summary.json').read_text())['cost_npv_10k']) if paths else None


def source_folder(region,baseline,case):
    return old.best_folder(old.OUT/region/(baseline+'_reverse80'),case)


def replacement_counts(inp,folder):
    before=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]);counts=np.zeros((len(before),2),dtype=int)
    for y in inp['years']:
        u,_,_=old.old.assets_from_csv(inp,folder,y)
        counts+=(u[:,:2]>before[:,:2]+1e-8);before=u
    return counts


def save(inp,scenes,out,region,baseline,case,z,meta,result,selected,history,method):
    checks,violations,details=old.old.base.check_all(inp,scenes,z,meta,OperatingLP(inp))
    if violations:return checks,violations
    summary,stations,projects=old.old.base.network.extract(inp,None,case,z,meta,result,history,checks)
    summary.pop('full_hour_network_checks',None)
    summary.update(region=region,baseline=baseline,case=case,solver=result,checks=checks,history=history,
        method=method,input_sha256=old.sha(out.parent/'inputs.json'),selection_conditions={},
        scope='2021固定基期；2022—2025静态正常/N-1共同替代；主变期内最多更换一次')
    old.dump(out/'summary.json',summary);old.write_csv(out/'years.csv',summary['annual'])
    old.write_csv(out/'stations.csv',stations);old.write_csv(out/'projects.csv',projects)
    old.dump(out/'selected_pairs.json',sorted(selected));np.savez_compressed(out/'chosen_solution.npz',solution=z)
    old.dump(out/'independent_lp.json',dict(verified=True,checks=checks,records=details))
    assert replacement_counts(inp,out).max()<=1
    print('JOINT_DONE',region,baseline,case,summary['cost_npv_10k'],result['mip_gap'],
          [(a['year'],a['capacity_mva'],a['storage_mwh'],a['cumulative_lines']) for a in summary['annual']],flush=True)
    return checks,[]


def certify(region,baseline,case):
    inp,scenes,root=prepare(region,baseline);src=source_folder(region,baseline,case)
    if replacement_counts(inp,src).max()>1:return None
    out=root/(case+'_certified');out.mkdir(exist_ok=True)
    if (out/'summary.json').exists():return out
    selected={tuple(v) for v in json.loads((src/'selected_pairs.json').read_text())}
    selected.update((y,h,-1) for y in inp['years'] for h in range(len(scenes[y])))
    native,meta=build(inp,scenes,case,selected)
    assets={(y,sid):row for y in inp['years'] for row in old.old.base.previous.rows(src/'stations.csv')
            if int(row['year'])==y for sid in [row['station']]}
    projects=old.old.base.previous.rows(src/'projects.csv')
    def fix(v,value):native.lower_bounds[v]=native.upper_bounds[v]=value
    for (sid,slot,y,r),v in meta['x'].items():fix(v,float(abs(float(assets[y,sid][f'unit_{slot+1}_mva'])-r)<1e-8))
    for (sid,y),v in meta['third'].items():fix(v,float(assets[y,sid]['unit_3_mva'])/50.)
    for (sid,y),v in meta['modules'].items():fix(v,int(assets[y,sid]['storage_modules']))
    for (eid,y),v in meta['edgevars'].items():fix(v,float(any(p['id']==eid and int(p['year'])<=y for p in projects)))
    z,result=old.old.base.parameters.solve(native,out,'fixed_layout',45.,.0001,dict(inp,storage_usable_energy_fraction=1.),meta,src)
    assert z is not None and result['feasible_incumbent']
    prior=json.loads((src/'summary.json').read_text());result['fixed_layout_bound']=result['dual_bound']
    result.update(dual_bound=prior['solver']['dual_bound'],accepted=False,
        status='Feasible source layout certified; global lower bound from relaxed static model',
        source_status=prior['solver']['status'],source_summary_sha256=old.sha(src/'summary.json'))
    assert result['dual_bound']<=result['objective']+1e-5
    result['mip_gap']=max(0.,(result['objective']-result['dual_bound'])/max(1.,abs(result['objective'])))
    checks,violations=save(inp,scenes,out,region,baseline,case,z,meta,result,selected,[],
        dict(type='旧布局在新共同采购约束下复核，保留松弛模型费用下界',source=str(src.relative_to(ROOT))))
    assert not violations
    return out


def run(region,baseline,case,seconds=180.,gap=.005,attempt='main'):
    inp,scenes,root=prepare(region,baseline);out=root/(case+'_'+attempt);out.mkdir(exist_ok=True)
    if (out/'summary.json').exists():return out
    src=best(region,baseline,case) or source_folder(region,baseline,case)
    selected={tuple(v) for v in json.loads((src/'selected_pairs.json').read_text())}
    selected.update((y,h,-1) for y in inp['years'] for h in range(len(scenes[y])))
    prior=json.loads((source_folder(region,baseline,case)/'summary.json').read_text())
    bounds=[prior['solver']['dual_bound']];warm=src;history=[]
    for iteration in range(1,9):
        native,meta=build(inp,scenes,case,selected)
        z,result=old.old.base.parameters.solve(native,out,f'iteration_{iteration:02}',seconds,gap,
            dict(inp,storage_usable_energy_fraction=1.),meta,warm)
        if result.get('dual_bound') is not None:bounds.append(result['dual_bound'])
        if z is None or not result.get('feasible_incumbent'):
            old.dump(out/'failed_search.json',dict(solver=result,history=history));return None
        checks,violations,details=old.old.base.check_all(inp,scenes,z,meta,OperatingLP(inp))
        summary,stations,projects=old.old.base.network.extract(inp,None,case,z,meta,result,history,checks)
        candidate=out/f'candidate_{iteration:02}';candidate.mkdir(exist_ok=True)
        old.write_csv(candidate/'stations.csv',stations);old.write_csv(candidate/'projects.csv',projects)
        history.append(dict(iteration=iteration,selected_pairs=len(selected),solver=result,checks=checks))
        print('JOINT_CHECK',region,baseline,case,iteration,'violations',len(violations),flush=True)
        if violations:
            additions={(y,h,f) for _,y,h,f in sorted(violations,reverse=True)[:40]};assert additions-selected
            selected.update(additions);warm=candidate;continue
        result['dual_bound']=max(bounds);assert result['dual_bound']<=result['objective']+1e-4
        result['mip_gap']=max(0.,(result['objective']-result['dual_bound'])/max(1.,abs(result['objective'])))
        save(inp,scenes,out,region,baseline,case,z,meta,result,selected,history,
             dict(type='共同静态约束下费用寻优；新购主变期内不重复更换'))
        return out
    raise RuntimeError('静态工况分离未完成')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--region',choices=list(REGIONS),required=True)
    p.add_argument('--baseline',choices=list(BASELINES),required=True);p.add_argument('--case',choices=list(CASES),required=True)
    p.add_argument('--seconds',type=float,default=180.);p.add_argument('--attempt',default='main');p.add_argument('--certify',action='store_true')
    a=p.parse_args();certify(a.region,a.baseline,a.case) if a.certify else run(a.region,a.baseline,a.case,a.seconds,attempt=a.attempt)
