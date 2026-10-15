"""复用已确认的弹性经济模型，补齐两地区与原表容量起点。"""
import argparse
import copy
import json
import shutil

import numpy as np

from ..recommend_20261015 import model as parent

old=parent.old
ROOT=parent.ROOT
RAW=ROOT/'研究报告/试算/20261015_双区县经济方案'
PUBLIC=ROOT/'研究报告/01研究推荐/当前版/双区县经济方案_20261015'
REVIEW=ROOT/'研究报告/05_review/当前版/1015双区县经济方案'
SOURCE=ROOT/'研究报告/数据来源/当前版/双区县经济方案_20261015'
REGIONS={'pizhou':'邳州','city':'市区'}
BASELINES={'compressed':'共同仿真起点','annual_2021':'2021原表容量起点'}
CASES={'rigid':'刚性方案','elastic_free':'弹性经济优化方案'}
OperatingLP=parent.OperatingLP
build=parent.build


def prepare(region,baseline):
    source=old.OUT/region/(baseline+'_reverse80')/'inputs.json'
    assert source.exists(),source
    inp=copy.deepcopy(json.loads(source.read_text()))
    inp.update(normal_supply_area_fixed=False,planning_start_year=2022,fixed_baseline_year=2021,
        recommendation_basis='弹性经济参考；共同固定2021设备，2022—2025按相同运行规则寻优',
        normal_transfer_policy='年度通道比例固定，按送端正向净负荷缩放；正常不调用事故备用储能',
        economic_source_input_sha256=old.sha(source),selection_conditions={})
    assert inp['years']==[2022,2023,2024,2025]
    root=RAW/region/baseline;root.mkdir(parents=True,exist_ok=True)
    if (root/'inputs.json').exists():assert json.loads((root/'inputs.json').read_text())==inp
    else:old.dump(root/'inputs.json',inp)
    scenes=old.old.base.load_scenes(old.old.base.OUT/region,inp)
    return inp,scenes,root


def best(region,baseline,case):
    folders=[p.parent for p in (RAW/region/baseline).glob(case+'*/summary.json') if json.loads(p.read_text()).get('case')==case]
    return min(folders,key=lambda p:json.loads((p/'summary.json').read_text())['cost_npv_10k']) if folders else None


def inherit_pizhou():
    inp,scenes,root=prepare('pizhou','compressed')
    before=json.loads((parent.RAW/'邳州/inputs.json').read_text())
    for key in ['years','stations','network','existing_transfer_budget_by_year_mw','initial_capacity_mva','cost_factors']:
        assert inp[key]==before[key]
    for case in CASES:
        source=parent.best(case);out=root/(case+'_inherited');out.mkdir(exist_ok=True)
        if (out/'summary.json').exists():continue
        for name in ['stations.csv','projects.csv','chosen_solution.npz','selected_pairs.json','normal_fractions.json']:
            shutil.copyfile(source/name,out/name)
        result=json.loads((source/'summary.json').read_text())
        assert not result['selection_conditions']
        result.update(region='pizhou',baseline='compressed',input_sha256=old.sha(root/'inputs.json'),
            inherited_from=str(source.relative_to(ROOT)),inherited_summary_sha256=old.sha(source/'summary.json'),
            scope='2021固定共同起点，2022—2025经济规划；正常按年固定比例转供，储能事故备用，直接事故转接')
        old.dump(out/'summary.json',result);old.write_csv(out/'years.csv',result['annual'])


def run(region,baseline,case,seconds=240.,attempt='main'):
    inp,scenes,root=prepare(region,baseline);out=root/(case+'_'+attempt);out.mkdir(exist_ok=True)
    if (out/'summary.json').exists():return
    previous=best(region,baseline,case)
    source=previous or old.best_folder(old.OUT/region/(baseline+'_reverse80'),case)
    assert source
    selected={tuple(r) for r in json.loads((source/'selected_pairs.json').read_text())}
    selected.update((y,h,-1) for y in inp['years'] for h in range(len(scenes[y])))
    warm=source;history=[];bounds=[]
    for iteration in range(1,10):
        native,meta=build(inp,scenes,case,selected)
        z,result=old.old.base.parameters.solve(native,out,f'iteration_{iteration:02}',seconds,.005,
            dict(inp,storage_usable_energy_fraction=1.),meta,warm)
        if result.get('dual_bound') is not None:bounds.append(result['dual_bound'])
        if z is None or not result.get('feasible_incumbent'):
            old.dump(out/'failed_search.json',dict(solver=result,history=history));return
        checks,violations,detail=parent.check_all(inp,scenes,z,meta)
        summary,stations,projects=old.old.base.network.extract(inp,None,case,z,meta,result,history,checks)
        history.append(dict(iteration=iteration,selected_pairs=len(selected),solver=result,checks=checks))
        candidate=out/f'candidate_{iteration:02}';candidate.mkdir(exist_ok=True)
        old.write_csv(candidate/'stations.csv',stations);old.write_csv(candidate/'projects.csv',projects)
        print('TWO_DISTRICTS_CHECK',region,baseline,case,iteration,'violations',len(violations),'cost',summary['cost_npv_10k'],flush=True)
        if violations:
            additions={(y,h,f) for _,y,h,f in sorted(violations,reverse=True)[:50]};assert additions-selected
            selected.update(additions);warm=candidate;continue
        result['dual_bound']=max(bounds);result['mip_gap']=max(0.,(result['objective']-result['dual_bound'])/max(1.,abs(result['objective'])))
        summary.update(region=region,baseline=baseline,case=case,solver=result,checks=checks,history=history,
            selection_conditions={},reference_annual=[],input_sha256=old.sha(root/'inputs.json'),
            scope='2021固定共同起点，2022—2025经济规划；正常按年固定比例转供，储能事故备用，直接事故转接')
        old.dump(out/'summary.json',summary);old.write_csv(out/'years.csv',summary['annual'])
        old.write_csv(out/'stations.csv',stations);old.write_csv(out/'projects.csv',projects)
        fractions=[dict(year=y,edge=eid,direction=d,fraction=float(z[v])) for (y,eid,d),v in meta['normal_fractions'].items() if z[v]>1e-9]
        old.dump(out/'normal_fractions.json',fractions);old.dump(out/'selected_pairs.json',sorted(selected))
        np.savez_compressed(out/'chosen_solution.npz',solution=z);old.dump(out/'independent_lp.json',dict(verified=True,checks=checks,records=detail))
        print('TWO_DISTRICTS_DONE',region,baseline,case,summary['cost_npv_10k'],result['mip_gap'],
            [(a['year'],a['capacity_mva'],a['storage_mwh'],a['cumulative_lines']) for a in summary['annual']],flush=True)
        return
    raise RuntimeError('两地区全工况分离未完成')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--region',choices=list(REGIONS),required=True)
    p.add_argument('--baseline',choices=list(BASELINES),required=True);p.add_argument('--case',choices=list(CASES),required=True)
    p.add_argument('--seconds',type=float,default=240.);p.add_argument('--attempt',default='main');a=p.parse_args()
    run(a.region,a.baseline,a.case,a.seconds,a.attempt)
