"""只读核查本地 v4 原结果；不调用写结果或求解函数。"""
from pathlib import Path
import csv, json, hashlib, math, sys
from collections import defaultdict

ROOT=Path(__file__).resolve().parents[3]
STUDY=ROOT/'实验/研究'
AUDIT=STUDY/'rebuild_2026/source_audit'
RESULT=AUDIT/'capacity_release_simulation/reserve_policy_v4'
sys.path.insert(0,str(STUDY))

def rows(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

def run():
    problems=[]; checks=0
    def check(ok,msg):
        nonlocal checks
        checks+=1
        if not ok: problems.append(msg)
    def near(a,b,tol=1e-5):
        return math.isclose(float(a),float(b),abs_tol=tol,rel_tol=1e-9)
    from rebuild_2026.official_annual import read_official_annual,DEFAULT_SOURCE
    from rebuild_2026.incremental_cost import replacement_cost_coefficients,storage_anchors
    from rebuild_2026.baseline_2021 import local_unit_catalog
    from rebuild_2026.baseline_historical_proxy import build
    from rebuild_2026.annual_forward_scenes import build_annual_forward_scenes
    from rebuild_2026.pizhou_station_scenarios import build_station_scenarios
    from rebuild_2026.city_scenarios import build_city_scenarios
    from rebuild_2026.new_line_section_audit import designed_new_line_section
    from rebuild_2026.tie_section_audit import transferable_section
    from rebuild_2026.joint_lifecycle_optimizer import tie_edges
    snapshot=json.loads((ROOT/'研究报告/00审查/证据/输入与原结果快照.json').read_text())
    for r in snapshot:
        p=ROOT/r['path']
        check(p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],'原输入或原结果变化：'+r['path'])
    official=rows(AUDIT/'official_annual.csv')
    generated=read_official_annual(DEFAULT_SOURCE)
    check(len(official)==len(generated)==15,'年度原表条数')
    for a,b in zip(official,generated):
        for key in ['capacity_mva','reported_downward_load_mw','reported_clr']:
            check(near(a[key],b[key]),f'年度原始单元格：{a["region_id"]}/{a["year"]}/{key}')
    station_baseline,layers=build()
    for a,b in zip(rows(RESULT/'baseline_layers.csv'),layers):
        for key in ['target_capacity_mva','proxy_capacity_mva','allocation_gap_mva']:
            check(near(a[key],b[key]),'基期分配：'+key)
    for a,b in zip(rows(RESULT/'baseline_stations.csv'),station_baseline):
        for key in ['simulation_unit_1_mva','simulation_unit_2_mva','simulation_capacity_mva_2021']:
            check(near(a[key],b[key]),'站级基期分配：'+key)
    _,forward=build_annual_forward_scenes()
    for a,b in zip(rows(AUDIT/'annual_forward_layer_scenes_2021_2025.csv'),forward):
        check(near(a['estimated_synchronous_forward_peak_mw'],b['estimated_synchronous_forward_peak_mw']),'年度正向场景复算')
    pz_stations,_=build_station_scenarios()
    for a,b in zip(rows(AUDIT/'pizhou_2025_station_scenarios_evidence.csv'),pz_stations):
        for key in ['forward_peak_mw','reverse_peak_mw','forward_h95_hours','reverse_h95_hours','forward_d95_max_run_hours','reverse_d95_max_run_hours']:
            check(near(a[key],b[key]),'邳州逐时复算：'+key)
    city_scenes,city_hourly,_=build_city_scenarios()
    for a,b in zip(rows(AUDIT/'city_2025_scenario_sensitivity.csv'),city_scenes):
        for key in ['forward_peak_mw','reverse_peak_mw','forward_d95_max_run_hours','reverse_d95_max_run_hours','observed_hours','imputed_hours']:
            check(near(a[key],b[key]),'市区逐时复算：'+key)
    coefficients={r['voltage_kv']:r['base_coefficient_10k_cny_per_purchased_mva'] for r in replacement_cost_coefficients()}
    one,ten=storage_anchors()
    def storage(n):
        q,m=divmod(n,10)
        return q*ten+(one+(m-1)*(ten-one)/9 if m else 0)
    def flows(capex,year,life,om):
        yield year,'首次投资',capex
        for t in range(year+life,2041,life): yield t,'更新投资',capex
        for t in range(year+1,2042): yield t,'运行维护',capex*om
    def effect(n,h): return n*min(.1,.215/h) if h else n*.1
    durations={(r['study_region_id'],int(r['voltage_kv']),r['model_station_id']):r for r in rows(AUDIT/'static_storage_need_screen_2025.csv') if r['capacity_case']=='hold_2021_simulation_capacity'}
    baselines={(r['study_region_id'],int(r['voltage_kv']),r['model_station_id']):r for r in rows(RESULT/'baseline_stations.csv')}
    catalogs=local_unit_catalog()
    edges,feeders=tie_edges(True,'designed_bus')
    edge_by_id={r['tie_id']:r for r in edges}
    section={'T01':transferable_section()['2025_feeder_stress_section_p_seed_mw'],'SIM-NEW-DZHEN-RIVER-BUS':designed_new_line_section()['2025_feeder_stress_section_load_seed_mw']}
    events=[]; breakdown=[]
    for case in rows(RESULT/'summary.csv'):
        region=case['study_region_id'];v=int(case['voltage_kv']);scheme=case['scheme'];stem=f'{scheme}_{region}_{v}'
        stations=rows(RESULT/(stem+'_stations.csv')); years=rows(RESULT/(stem+'_years.csv'))
        ties=rows(RESULT/(stem+'_ties.csv')) if (RESULT/(stem+'_ties.csv')).exists() else []
        check(len(stations)==len({(r['model_station_id'],r['year']) for r in stations}),'重复站年：'+stem)
        fraction=float(case['contingency_fraction_assumption']);gross=0;components=defaultdict(float)
        previous={key[2]:[float(b[f'simulation_unit_{i}_mva']) for i in [1,2]] for key,b in baselines.items() if key[:2]==(region,v)}
        previous_n=defaultdict(int)
        for r in sorted(stations,key=lambda r:(int(r['year']),r['model_station_id'])):
            name=r['model_station_id'];y=int(r['year']);skey=(region,v,name)
            units=[float(r[f'selected_unit_{i}_mva']) for i in [1,2]]
            old=[float(r[f'prior_unit_{i}_mva']) for i in [1,2]];n=int(r['storage_modules_in_service'])
            check(old==previous[name],stem+' 主变路径衔接 '+name)
            check(all(u in catalogs[region,v] for u in units),stem+' 本地离散规格 '+name)
            check(0<=n<=50 and n>=previous_n[name],stem+' 储能整数及单调性 '+name)
            check(near(r['selected_capacity_mva'],sum(units)),stem+' 单站容量加总')
            d=durations[skey]
            for direction in ['forward','reverse']:
                net=sum(float(t['transfer_mw'])*((t['donor_station_id']==name)-(t['receiver_station_id']==name)) for t in ties if int(t['year'])==y and t['scenario']==direction)
                e=effect(n,int(d[direction+'_d95_max_run_hours']))
                demand=float(r[direction+'_screen_mw']);factor=.95 if direction=='forward' else .76
                check(factor*sum(units)+e+net>=demand-1e-5,stem+' '+name+' '+str(y)+' '+direction+'容量约束')
                if direction=='forward': check(.95*min(units)+e+fraction*net>=fraction*demand-1e-5,stem+' 停运承载代理 '+name)
            gross+=sum(max(0,new-prior) for prior,new in zip(old,units))
            capex_t=sum(new*coefficients[v] for prior,new in zip(old,units) if new>prior)
            capex_s=storage(n)-storage(previous_n[name])
            check(near(capex_t,r['transformer_capex_10k_cny']),stem+' 新购全容量计价')
            check(near(capex_s,r['storage_capex_10k_cny']),stem+' 储能包价差分')
            for measure,capex,life,om in [('主变',capex_t,20,.01),('储能',capex_s,10,.03)]:
                npv=0
                if capex>0:
                    for t,component,amount in flows(capex,y,life,om):
                        pv=amount/1.06**(t-2021);npv+=pv;components[component]+=pv
                        events.append({'region':region,'voltage_kv':v,'scheme':scheme,'station':name,'commissioning_year':y,'year':t,'measure':measure,'component':component,'amount_10k_cny':amount,'npv_10k_cny':pv,'source':str((RESULT/(stem+'_stations.csv')).relative_to(ROOT)),'source_year':y})
                check(near(npv,r['transformer_lifecycle_npv_10k_cny' if measure=='主变' else 'storage_lifecycle_npv_10k_cny'],1e-4),stem+' 独立现金流 '+measure)
            previous[name]=units;previous_n[name]=n
        initial=sum(float(b['simulation_capacity_mva_2021']) for key,b in baselines.items() if key[:2]==(region,v))
        if scheme=='rigid':check(gross<=initial*float(case['rigid_budget_assumption'])+1e-5,stem+' 累计正增配预算')
        for yrow in years:
            y=int(yrow['year']);capacity=sum(float(r['selected_capacity_mva']) for r in stations if int(r['year'])==y)
            p=float(yrow['synchronous_forward_peak_mw'])
            check(near(capacity,yrow['selected_capacity_mva']),stem+' 年度总容量')
            check(near(capacity/p,yrow['actual_clr'],1e-7),stem+' 年度容载比')
            check(capacity/p<=float(case['clr_cap'])+1e-8,stem+' 容载比控制上限')
            line=float(yrow['new_line_capex_10k_cny'])
            if line>0:
                check(near(line,3*44.543),stem+' 新线投资')
                for t,component,amount in flows(line,y,20,.01):
                    pv=amount/1.06**(t-2021);components[component]+=pv
                    events.append({'region':region,'voltage_kv':v,'scheme':scheme,'station':'两站联络','commissioning_year':y,'year':t,'measure':'新线','component':component,'amount_10k_cny':amount,'npv_10k_cny':pv,'source':str((RESULT/(stem+'_years.csv')).relative_to(ROOT)),'source_year':y})
        for t in ties:
            edge=edge_by_id[t['tie_id']];donor=feeders[t['donor_feeder_id']];receiver=feeders[t['receiver_feeder_id']]
            q=float(t['transfer_mw']);bound=min(float(donor['current_equivalent_active_power_mw']),float(receiver['receiving_current_headroom_mw']),float(edge['path_cap_mw']))
            check(q<=bound+1e-5,stem+' 转供容量上界')
            donor_rows=[r for r in stations if r['model_station_id']==t['donor_station_id']]
            yr=int(t['year']);demand=float(next(r for r in donor_rows if int(r['year'])==yr)['forward_screen_mw'])
            demand_2025=float(next(r for r in donor_rows if int(r['year'])==2025)['forward_screen_mw'])
            check(near(q,section[t['tie_id']]*demand/demand_2025,2e-6),stem+' 转供区段种子年度缩放')
        total=sum(components.values());check(near(total,case['objective_npv_10k_cny'],1e-3),stem+' 总成本独立重建')
        breakdown.append({'region':region,'voltage_kv':v,'scheme':scheme,'initial_capex_npv':components['首次投资'],'renewal_capex_npv':components['更新投资'],'fixed_om_npv':components['运行维护'],'total_npv':total,'declared_npv':float(case['objective_npv_10k_cny']),'difference':total-float(case['objective_npv_10k_cny'])})
    matrix=rows(RESULT/'annual_matrix.csv')
    check(len(matrix)==12 and len({(r['study_region_id'],r['voltage_kv'],r['year']) for r in matrix})==12,'12行矩阵键')
    for r in matrix:
        for scheme in ['rigid','elastic']:
            check(near(float(r[scheme+'_capacity_mva'])/float(r['reference_peak_mw']),r[scheme+'_clr'],1e-7),'推荐矩阵比值')
    return {'status':'PASS' if not problems else 'FAIL','checks':checks,'problems':problems,'original_snapshot_count':len(snapshot),'path_count':6,'annual_cases':12,'scope':'源表复算、离散路径、正反向与停运代理、转供区段、投资及显式现金流','cost_breakdown':breakdown,'cashflow_events':events,'city_observed_hours':next(r['observed_hours'] for r in city_scenes if r['model_station_id']=='__DISTRICT__' and r['variant']=='observed')}

if __name__=='__main__':
    data=run()
    target=ROOT/'研究报告/00审查/证据/本阶段独立核查.json'
    target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in data.items() if k not in ['cashflow_events','cost_breakdown']},ensure_ascii=False))
    if data['problems']: raise SystemExit(1)
