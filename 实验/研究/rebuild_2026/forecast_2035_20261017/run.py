"""最小范围的市区2026—2035年前推；原结果与报告不回写。"""
import argparse
import copy
import csv
import json
import math
from pathlib import Path

import numpy as np

from ..static_joint_20261015 import model as base
from ..case_parameters_20261012.capacity_audit import PROFILES
from ..current_economic_assumptions import (
    DISCOUNT_RATE, TRANSFORMER_LIFE, LINE_LIFE, STORAGE_LIFE,
    TRANSFORMER_OM, LINE_OM, STORAGE_OM,
)

ROOT = base.ROOT
RAW = ROOT/'研究报告/试算/20261017_市区前推2035'
PUBLIC = ROOT/'研究报告/01研究推荐/当前版/市区前推2035_20261017'
SOURCE = ROOT/'研究报告/数据来源/当前版/市区前推2035_20261017'
REVIEW = ROOT/'研究报告/05_review/当前版/1017市区前推2035'
FORECAST = ROOT/'实验/研究/data/tuomin/补充数据/负荷和光伏装机预测.md'
PROXY = ROOT/'实验/研究/rebuild_2026/source_audit/annual_reverse_station_proxy_2021_2025.csv'
ORIGINAL = base.RAW/'city/annual_2021'
LABEL = {'rigid': '刚性', 'elastic_free': '弹性经济参考'}
dump, write_csv, sha = base.old.dump, base.old.write_csv, base.old.sha


def table_values(section):
    """直接读取用户预测表，避免手工复制数值后漏同步。"""
    content = FORECAST.read_text().split(section, 1)[1].split('\n## ', 1)[0]
    return [line for line in content.splitlines() if line.startswith('|')]


def forecasts():
    pv = {}
    for line in table_values('## 1.'):
        fields = [v.strip() for v in line.strip('|').split('|')]
        if fields[0].isdigit(): pv[int(fields[0])] = float(fields[1])
    rows = table_values('## 2.')
    headers = [s.strip() for s in rows[0].strip('|').split('|')]
    cells = [s.strip() for s in next(r for r in rows if r.startswith('| 市区 ')).strip('|').split('|')]
    load = {int(h[:4]): float(v) for h, v in zip(headers, cells) if h[:4].isdigit()}
    originals = dict(load=copy.deepcopy(load), pv=copy.deepcopy(pv))
    def interpolate(values):
        nodes = sorted(values)
        for y in range(2025, 2036):
            if y not in values:
                a = max(k for k in nodes if k < y); b = min(k for k in nodes if k > y)
                values[y] = values[a] + (values[b]-values[a])*(y-a)/(b-a)
    interpolate(load); interpolate(pv)
    annual = [dict(year=y, city_load_mw=load[y], citywide_pv_index=pv[y],
        load_factor=load[y]/load[2025], pv_factor=pv[y]/pv[2025],
        load_yoy=load[y]/load[y-1]-1 if y>2025 else None,
        pv_yoy=pv[y]/pv[y-1]-1 if y>2025 else None,
        load_interpolated=y not in originals['load'], pv_interpolated=y not in originals['pv']) for y in range(2025,2036)]
    return annual


def factor(year, life, om):
    """沿用2021现值基年、2041评价截止与次年起运维，无残值。"""
    values = [(year, 1.)]
    renewal = year+life
    while renewal < 2041:
        values.append((renewal, 1.)); renewal += life
    values.extend((y, om) for y in range(year+1, 2042))
    return sum(value/(1+DISCOUNT_RATE)**(y-2021) for y,value in values)


def prepare():
    for p in [RAW, PUBLIC, SOURCE, REVIEW]: p.mkdir(parents=True, exist_ok=True)
    inp = copy.deepcopy(json.loads((ORIGINAL/'inputs.json').read_text()))
    ids = list(inp['stations']); annual = forecasts()
    profile = np.load(PROFILES/'city_stations.npz')
    order = [list(profile['station_ids']).index(s) for s in ids]
    raw_net = profile['power_mw'][:, order]
    scale = inp['annual_observed_peak_mw']['2025']/raw_net.sum(axis=1).max()
    net = raw_net*scale
    proxies = {r['model_station_id']: r for r in base.old.old.base.previous.rows(PROXY)
               if r['study_region_id']=='QX-00007' and r['voltage_kv']=='110'
               and r['year']=='2025' and r['variant']=='night_central'}
    assert set(proxies)==set(ids)
    central = np.array([float(proxies[s]['gross_load_proxy_mw_2025']) for s in ids])*scale
    daylight = np.isin(np.arange(8760)%24, np.arange(8,18))
    # 沿用归档夜间中位数代理日间用电负荷，按各同期净负荷残差估计光伏。
    # 夜间原有的少量反向净功率保持在非光伏分量，避免推定为夜间光伏发电。
    generation = np.where(daylight[:,None], np.maximum(central[None,:]-net, 0.), 0.)
    demand = net+generation
    assert np.max(abs(demand-generation-net))<1e-10
    whole = {a['year']: demand*a['load_factor']-generation*a['pv_factor'] for a in annual}
    original_hours = {r['source_hour'] for r in inp['station_snapshot_roles']}
    scenes = {}; roles = {}; forecast_rows=[]
    evidence = {r['station']:r for r in inp['station_transfer_evidence']}
    inp['years'] = list(range(2026,2036))
    inp['fixed_baseline_year'] = 2025; inp['planning_start_year'] = 2026
    inp['growth_rate'] = (annual[-1]['city_load_mw']/annual[0]['city_load_mw'])**.1-1
    inp['procurement_policy'] = '2025配置固定；2026—2035每个主变位置最多更换一次，新购配置持续保留'
    inp['annual_observed_peak_mw'] = dict(inp['annual_observed_peak_mw'])
    # 规划年度峰值继续用110kV年度统计基数乘负荷增长比例；不改为8760曲线峰值。
    for a in annual:
        y=a['year']; p=whole[y]
        inp['annual_observed_peak_mw'][str(y)] = inp['annual_observed_peak_mw']['2025']*a['load_factor']
        if y==2025: continue
        chosen = set(original_hours)
        chosen.update([int(np.argmax(p.sum(axis=1))),int(np.argmin(p.sum(axis=1)))])
        chosen.update(map(int,np.argmax(p,axis=0))); chosen.update(map(int,np.argmin(p,axis=0)))
        hours = sorted(chosen); scenes[y]=p[hours]
        roles[y] = [dict(source_hour=h, regional_peak=h==int(np.argmax(p.sum(axis=1))),
                         regional_min=h==int(np.argmin(p.sum(axis=1))),
                         all_stations_observed=bool(profile['observed'][h,order].all())) for h in hours]
        inp['existing_transfer_budget_by_year_mw'][str(y)] = {
            sid:min(evidence[sid]['transferable_mw'], (inp['station_transfer_rates'][sid] or 0.)*max(0.,float(p[:,j].max())))
            for j,sid in enumerate(ids)}
        forecast_rows.append(dict(**a, planning_peak_110kv_mw=inp['annual_observed_peak_mw'][str(y)],
            synchronous_profile_forward_peak_mw=float(p.sum(axis=1).max()),
            synchronous_profile_reverse_peak_mw=float(max(0.,-p.sum(axis=1).min())), snapshots=len(hours)))
    for kind,life,om in [('transformer',TRANSFORMER_LIFE,TRANSFORMER_OM),('line',LINE_LIFE,LINE_OM),('storage',STORAGE_LIFE,STORAGE_OM)]:
        inp['cost_factors'][kind] = {str(y): factor(y,life,om) for y in inp['years']}
    inp['forecast_basis'] = dict(source=str(FORECAST.relative_to(ROOT)),sha256=sha(FORECAST),
        load='最新市区总负荷相对2025年比例作用于原110kV负荷分量，缺年按相邻节点等增量插值',
        pv='徐州市光伏装机相对2025年比例作用于市区光伏代理，缺年等增量插值；单位在比例中消去',
        decomposition='日间08—18时，用归档night_central负荷代理与同期净负荷之较大值作为负荷分量，差额为光伏代理；夜间原净功率作为非光伏分量。2025原净负荷逐点还原。',
        static_scope='各年保留原45个同期截面，并补充外推后地区及各站正向峰值与最低净负荷截面；非SOC调度',
        historical='2021起点3113.5 MVA及2022—2025已确认配置保持，2026起直接接续',
        economics='延用40/40/25年寿命、4.2%/2.2%/3%维护、6%折现、2021现值基年和2041评价截止，延长可投运年份')
    inp['scope']='市区实际容量起点接续2026—2035，正常/N-1静态联合替代，源荷分别按相对增量外推'
    inp['forecast_snapshot_roles']={str(y):v for y,v in roles.items()}
    dump(RAW/'inputs.json',inp); dump(RAW/'forecast_annual.json',annual)
    np.savez_compressed(RAW/'scenarios.npz',**{str(y):p for y,p in scenes.items()})
    np.savez_compressed(RAW/'base_components.npz',net_2025_mw=net,demand_proxy_mw=demand,generation_proxy_mw=generation,station_ids=np.array(ids))
    write_csv(SOURCE/'逐年预测及增长率.csv',annual); write_csv(SOURCE/'模型负荷及工况.csv',forecast_rows)
    dump(SOURCE/'来源与假设.json',dict(inputs_sha256=sha(RAW/'inputs.json'),assumptions=inp['forecast_basis'],
        sources=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in [FORECAST,ORIGINAL/'inputs.json',PROFILES/'city_stations.npz',PROXY]],
        decomposition_baseline_error_mw=float(np.max(abs(demand-generation-net)))))
    return inp,scenes


def check(inp,scenes,units,n,built):
    details=[]; violations=[]; checks=[]
    for y in inp['years']:
        active=copy.deepcopy(inp)
        active['network']['edges']=[e for e in inp['network']['edges'] if e['existing'] or e['id'] in built[y]]
        used={e[k] for e in active['network']['edges'] for k in ('a','b')}
        active['network']['feeders']={f:r for f,r in active['network']['feeders'].items() if f in used}
        lp=base.OperatingLP(active)
        bad=[]
        for h,p in enumerate(scenes[y]):
            ready=lp.prepared(p,y,units[y],n[y],built[y])
            for f in range(-1,len(inp['stations'])):
                r=lp.check(p,ready,f)
                row=dict(year=y,scenario=h,failed=f,**r);details.append(row)
                if not r['verified']:
                    violations.append((r['deficit_mw'],y,h,f));bad.append(row)
        checks.append(dict(year=y,checked_pairs=len(scenes[y])*(len(inp['stations'])+1),
                           violating_pairs=len(bad),verified=not bad))
    return checks,violations,details


def run(case,seconds=60.,attempt='main'):
    if not (RAW/'inputs.json').exists():prepare()
    inp=json.loads((RAW/'inputs.json').read_text())
    assert inp['forecast_basis']['sha256']==sha(FORECAST),'预测源已变化，须另建试算版本并重新准备输入'
    archived=np.load(RAW/'scenarios.npz');scenes={y:archived[str(y)] for y in inp['years']}
    out=RAW/(case+'_'+attempt);out.mkdir(exist_ok=True)
    if (out/'summary.json').exists():return
    units0=np.array([s['initial_units']+[0.] for s in inp['stations'].values()])
    # 两个2025方案均无新增，逐站核对后从同一资产直接延伸。
    for source_case in ['rigid_certified','elastic_free_certified']:
        u,n,built=base.old.old.assets_from_csv(inp,ORIGINAL/source_case,2025)
        assert np.array_equal(u,units0) and n.sum()==0 and not built
    units={y:units0.copy() for y in inp['years']};counts={y:np.zeros(len(units0),int) for y in inp['years']};built={y:set() for y in inp['years']}
    cached=RAW/'initial_selected.json'
    if cached.exists():selected={tuple(r) for r in json.loads(cached.read_text())}
    else:
        _,bad,_=check(inp,scenes,units,counts,built)
        selected=set()
    # 每个故障、每年先纳入缺口最大的一个同期截面，随后全截面独立分离。
        for y in inp['years']:
            for f in range(-1,len(units0)):
                candidates=[r for r in bad if r[1]==y and r[3]==f]
                if candidates:
                    _,yy,h,ff=max(candidates);selected.add((yy,h,ff))
        dump(cached,sorted(selected))
    warm=out/'warm';warm.mkdir(exist_ok=True)
    # 逐站足额储能仅作整数可行起点，不作为采用方案。
    warm_rows=[]
    for y in inp['years']:
        for j,(sid,s) in enumerate(inp['stations'].items()):
            bp=min(.1,.215*.76/max(1,s['forward_duration_h']));bn=min(.1,.215*.76/max(1,s['reverse_duration_h']))
            surviving=.95*(sum(s['initial_units'])-max(s['initial_units']))
            normal_reverse=.8*.95*sum(s['initial_units'])
            number=math.ceil(max(0.,(scenes[y][:,j].max()-surviving)/bp,
                (-scenes[y][:,j].min()-min(normal_reverse,surviving))/bn)+1e-8)
            if warm_rows:
                prior=[r['storage_modules'] for r in warm_rows if r['station']==sid]
                if prior:number=max(number,prior[-1])
            warm_rows.append(dict(year=y,station=sid,unit_1_mva=s['initial_units'][0],unit_2_mva=s['initial_units'][1],unit_3_mva=0.,storage_modules=number))
    write_csv(warm/'stations.csv',warm_rows);(warm/'projects.csv').write_text('year,id\n',encoding='utf-8-sig')
    # 先在不新建联络的子问题取得较好的设备布局，随后释放全部原候选。
    seed=RAW/(case+'_seed')
    if (seed/'stations.csv').exists():
        warm=seed
        if (seed/'selected_pairs.json').exists():
            selected.update(tuple(r) for r in json.loads((seed/'selected_pairs.json').read_text()))
    history=[];bounds=[]
    for iteration in range(1,9):
        m,meta=base.build(inp,scenes,case,selected)
        print('BUILD',case,iteration,'pairs',len(selected),'vars',len(m.costs),flush=True)
        z,result=base.old.old.base.parameters.solve(m,out,f'iteration_{iteration:02}',seconds,.02,
            dict(inp,storage_usable_energy_fraction=1.),meta,warm)
        if result.get('dual_bound') is not None:bounds.append(result['dual_bound'])
        assert z is not None and result.get('feasible_incumbent'),result
        us={};ns={};bs={}
        for y in inp['years']:
            us[y],ns[y],_,_=base.old.old.base.assets.assets(inp,z,meta,y)
            bs[y]={eid for (eid,yy),v in meta['edgevars'].items() if yy==y and z[v]>.5}
        checks,violations,details=check(inp,scenes,us,ns,bs)
        summary,stations,projects=base.old.old.base.network.extract(inp,None,case,z,meta,result,history,checks)
        candidate=out/f'candidate_{iteration:02}';candidate.mkdir(exist_ok=True)
        write_csv(candidate/'stations.csv',stations);write_csv(candidate/'projects.csv',projects)
        history.append(dict(iteration=iteration,selected_pairs=len(selected),solver=result,checks=checks))
        print('CHECK',case,iteration,'violations',len(violations),'cost',summary['cost_npv_10k'],flush=True)
        if violations:
            additions=set()
            for y in inp['years']:
                for f in range(-1,len(units0)):
                    found=sorted([r for r in violations if r[1]==y and r[3]==f],reverse=True)[:2]
                    additions.update((yy,h,ff) for _,yy,h,ff in found)
            assert additions-selected;selected.update(additions);warm=candidate;continue
        result['dual_bound']=max(bounds)
        result['mip_gap']=max(0.,(result['objective']-result['dual_bound'])/max(1.,abs(result['objective'])))
        summary.update(region='city',case=case,baseline='annual_2021',history=history,checks=checks,solver=result,
            scope=inp['scope'],input_sha256=sha(RAW/'inputs.json'),forecast_sha256=sha(FORECAST),
            cost_scope='2026—2035新增措施至2041的费用现值，2021为折现基年，既有资产不计重复采购',
            optimality='限时费用寻优可行方案；下界与间隙保留')
        dump(out/'summary.json',summary);write_csv(out/'years.csv',summary['annual'])
        write_csv(out/'stations.csv',stations);write_csv(out/'projects.csv',projects)
        dump(out/'selected_pairs.json',sorted(selected));np.savez_compressed(out/'chosen_solution.npz',solution=z)
        dump(out/'independent_lp.json',dict(verified=True,checks=checks,records=details))
        print('DONE',case,summary['cost_npv_10k'],result['mip_gap'],
            [(r['year'],r['capacity_mva'],r['storage_mwh'],r['cumulative_lines']) for r in summary['annual']],flush=True)
        return
    raise RuntimeError('全静态截面分离未完成')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--case',choices=list(LABEL));p.add_argument('--seconds',type=float,default=60.)
    p.add_argument('--attempt',default='main');a=p.parse_args()
    run(a.case,a.seconds,a.attempt) if a.case else prepare()
