"""市区40%初始转供率：四组独立成本寻优及区县同期峰段复算。

python -m 实验.研究.rebuild_2026.pilot_20261009.run --prepare
python -m 实验.研究.rebuild_2026.pilot_20261009.run --case rigid_storage

技术边界沿用案例的正常负荷转接后本站主变N-1静态全负荷校核，
不新增事故转供变量。联络是站级等效建设单元，不代表已核实的线路路由。
"""
import argparse
import csv
import hashlib
import itertools
import json
import math
import time
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import highspy
import numpy as np
from openpyxl import load_workbook
from scipy.sparse import coo_matrix

from ..annual_no_tie_investment_submodel import LinearModel
from ..baseline_2021 import read_csv
from ..current_economic_assumptions import cost_factors, line_capex
from ..hourly_source_profile import CITY_SOURCE, OUTPUT_DIR
from ..incremental_cost import replacement_cost_coefficients, storage_anchors
from ..cost_references import read_cost_references
from ..joint_lifecycle_optimizer import load_inputs
from ..station_grid_feasibility import station_metadata
from ..station_transfer_equivalent import new_line_increment_reference, pair_equivalent_units

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / '研究报告/试算/20261009_市区40'
CITY = ('QX-00007', 110)
YEARS = (2022, 2023, 2024, 2025)
NEW_RATINGS = (31.5, 50., 63., 80.)
CASES = ('rigid_storage', 'rigid_no_storage', 'elastic_storage', 'elastic_no_storage')
PF = .95


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def write_csv(path, rows):
    if not rows:
        Path(path).write_text('', encoding='utf-8-sig')
        return
    with Path(path).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def peak_events(hours, values, threshold_fraction=.95):
    """Missing hours break a run; durations count hourly intervals."""
    peak = max(values)
    if peak <= 0:
        return []
    events, run = [], []
    for h, v in zip(hours, values):
        if v >= threshold_fraction*peak:
            if run and h-run[-1] != timedelta(hours=1):
                events.append(run)
                run = []
            run.append(h)
        elif run:
            events.append(run)
            run = []
    if run:
        events.append(run)
    return [{'start': r[0].isoformat(sep=' '),
             'end_exclusive': (r[-1]+timedelta(hours=1)).isoformat(sep=' '),
             'hours': len(r)} for r in events]


def aggregate_profile(out):
    mapping = read_csv(out/'city_2025_mapping_audit.csv')
    selected = [r for r in mapping if r['in_study_cohort']=='True']
    assert len(selected)==29 and len({r['model_station_id'] for r in selected})==29
    assert all(int(r['voltage_kv'])==110 and not r['duplicate_of'] for r in selected)
    assert all(r['city_source_sha256']==sha(CITY_SOURCE) for r in selected)
    hours = [datetime(2025,1,1)+timedelta(hours=i) for i in range(8760)]
    series = {}
    with ZipFile(CITY_SOURCE) as archive:
        for r in selected:
            w = load_workbook(BytesIO(archive.read(r['archive_member'])), read_only=True, data_only=True)
            s = w.active
            s.reset_dimensions()
            v = {}
            for cells in s.iter_rows(values_only=True):
                raw = str(cells[0] or '')
                if raw.startswith('2025-') and cells[1] is not None:
                    h = datetime.fromisoformat(raw)
                    if h in v:
                        raise ValueError('原始序列有重复时刻')
                    v[h] = float(cells[1])
            w.close()
            series[r['model_station_id']] = v
    common = set.intersection(*(set(v) for v in series.values()))
    observed = {h:sum(v[h] for v in series.values()) for h in sorted(common)}
    variants = {k:{h:0. for h in hours} for k in ('low','mean','high')}
    for v in series.values():
        for h in hours:
            if h in v:
                candidates = [v[h]]
            else:
                candidates = []
                for direction in (-1,1):
                    for weeks in range(1,7):
                        neighbor = h+timedelta(days=7*weeks*direction)
                        if neighbor in v:
                            candidates.append(v[neighbor])
                            break
                if not candidates:
                    raise ValueError('无同周类型补值参照')
            for key,value in [('low',min(candidates)),('mean',sum(candidates)/len(candidates)),('high',max(candidates))]:
                variants[key][h] += value
    reference = read_csv(out/'city_2025_aggregate_hourly.csv')
    max_error = max(abs(float(r['weekly_mean_mw'])-variants['mean'][datetime.fromisoformat(r['hour'])]) for r in reference)
    assert max_error < 1e-5
    official = {int(r['year']):r for r in read_csv(OUTPUT_DIR/'official_annual.csv')
                if r['region_id']==CITY[0] and r['voltage_kv']=='110'}
    actual_peak = float(official[2025]['reported_downward_load_mw'])
    capacity = float(official[2025]['capacity_mva'])
    scale = actual_peak/max(variants['mean'].values())
    stats = {}
    for variant,v in [('observed',observed),*variants.items()]:
        ts = sorted(v)
        events = peak_events(ts,[v[h] for h in ts])
        longest = max(events,key=lambda r:r['hours'])
        peak_time = max(ts,key=lambda h:v[h])
        stats[variant] = {'sample_peak_mw':v[peak_time], 'peak_time':peak_time.isoformat(sep=' '),
                          'longest_hours':longest['hours'], 'longest_event':longest,
                          'cumulative_hours':sum(e['hours'] for e in events),
                          'event_count':len(events), 'events':events,
                          'longest_event_imputed_hours':sum(datetime.fromisoformat(longest['start'])+timedelta(hours=i) not in common for i in range(longest['hours']))}
    hourly = [{'hour':h.isoformat(sep=' '),'observed':int(h in common),
               'sample_observed_mw':observed.get(h,''), 'sample_mean_mw':variants['mean'][h],
               'district_estimated_mw':variants['mean'][h]*scale,
               'district_estimated_loading_fraction':variants['mean'][h]*scale/(PF*capacity)} for h in hours]
    stats.update({'station_count':29,'common_observed_hours':len(common),'imputed_hours':8760-len(common),
                  'original_zip_sha256':sha(CITY_SOURCE),'mapping_sha256':sha(out/'city_2025_mapping_audit.csv'),
                  'archived_hourly_reference_max_error_mw':max_error,
                  'district_peak_calibration_factor':scale,'official_2025_peak_mw':actual_peak,
                  'official_2025_capacity_mva':capacity,
                  'scope':'29站同期样本；区县估计曲线按官方年度峰值作统一比例标定，非全域实测曲线',
                  'imputation':'原始观测同一周内时刻，前后六周各取最近可用值求平均；不使用递归补值'})
    write_csv(out/'区县同期逐时曲线.csv',hourly)
    dump(out/'区县峰段统计.json',stats)
    return stats


def solve_model(model, out, stage, seconds=600, gap=.01):
    out.mkdir(parents=True,exist_ok=True)
    rr,cc,vv = zip(*model.entries)
    a = coo_matrix((vv,(rr,cc)),shape=(len(model.constraint_lower),len(model.costs))).tocsr()
    h = highspy.Highs()
    for key,value in [('threads',1),('random_seed',0),('mip_rel_gap',gap),('time_limit',seconds),
                      ('output_flag',True),('log_to_console',False),('log_file',str(out/(stage+'.log')))]:
        h.setOptionValue(key,value)
    lp = highspy.HighsLp()
    lp.num_col_,lp.num_row_ = a.shape[1],a.shape[0]
    lp.col_cost_,lp.col_lower_,lp.col_upper_ = model.costs,model.lower_bounds,model.upper_bounds
    lp.row_lower_,lp.row_upper_ = model.constraint_lower,model.constraint_upper
    lp.integrality_ = [highspy.HighsVarType.kInteger if i else highspy.HighsVarType.kContinuous for i in model.integrality]
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_,lp.a_matrix_.index_,lp.a_matrix_.value_ = a.indptr,a.indices,a.data
    h.passModel(lp)
    print('SOLVE',stage,len(model.costs),'variables',flush=True)
    start = time.monotonic()
    h.run()
    status = h.getModelStatus()
    info = h.getInfo()
    raw = h.getSolution()
    result = {'stage':stage,'status':h.modelStatusToString(status),'solver':h.version(),
              'elapsed_seconds':time.monotonic()-start,'variables':len(model.costs),
              'constraints':len(model.constraint_lower),'relative_gap_target':gap,
              'objective':float(info.objective_function_value) if raw.value_valid else None,
              'dual_bound':float(info.mip_dual_bound) if math.isfinite(info.mip_dual_bound) else None,
              'mip_gap':float(info.mip_gap) if math.isfinite(info.mip_gap) else None}
    z = np.array(raw.col_value) if raw.value_valid else None
    result['accepted'] = status==highspy.HighsModelStatus.kOptimal
    result['proven_infeasible'] = status==highspy.HighsModelStatus.kInfeasible
    if z is not None:
        activity = a@z
        integrality = np.array(model.integrality,dtype=bool)
        result['matrix_check'] = {
            'lower_violation':float(max(0,np.max(np.array(model.constraint_lower)-activity))),
            'upper_violation':float(max(0,np.max(activity-np.array(model.constraint_upper)))),
            'bound_violation':float(max(0,np.max(np.array(model.lower_bounds)-z),np.max(z-np.array(model.upper_bounds)))),
            'integer_violation':float(np.max(abs(z[integrality]-np.round(z[integrality])))) if any(integrality) else 0.}
        result['feasible_incumbent'] = max(result['matrix_check'].values())<1e-5
        np.savez_compressed(out/(stage+'_solution.npz'),solution=z)
        if result['accepted']:
            assert result['feasible_incumbent']
    dump(out/(stage+'_solver.json'),result)
    print('RESULT',stage,result['status'],result['objective'],result['mip_gap'],flush=True)
    return z,result


def reconstruct_baseline(stations, target, out):
    """最近总容量优先，再贴近现有资产的站间容量比例；不使用后续方案费用。"""
    model = LinearModel()
    x,choices = {},{}
    old_sizes = (20.,31.5,40.,50.,63.,80.)
    for sid,s in stations.items():
        old = tuple(s['old_units'])
        ceiling = s['asset_capacity_mva'] or sum(old)
        choices[sid] = [p for p in itertools.combinations_with_replacement(old_sizes,2)
                        if sum(p)<=ceiling+1e-8 and all(v>=o for v,o in zip(p,old))]
        if not choices[sid]:
            raise ValueError(f'基期重构无设备候选：{sid}')
        for pair in choices[sid]:
            x[sid,pair] = model.variable(0)
        model.constraint({x[sid,p]:1 for p in choices[sid]},1,1)
    cap = {var:sum(pair) for (sid,pair),var in x.items()}
    d = model.variable(1,upper=np.inf,integer=0)
    model.constraint({**cap,d:-1},upper=target)
    model.constraint({**cap,d:1},lower=target)
    z,r = solve_model(model,out,'baseline_nearest_capacity',120,1e-9)
    assert r['accepted']
    deviation = z[d]
    model.constraint({d:1},upper=deviation+1e-7)
    model.costs = [0.]*len(model.costs)
    denominator = sum(s['asset_capacity_mva'] or sum(s['old_units']) for s in stations.values())
    for sid,s in stations.items():
        desired = target*(s['asset_capacity_mva'] or sum(s['old_units']))/denominator
        e = model.variable(1,upper=np.inf,integer=0)
        terms = {x[sid,p]:sum(p) for p in choices[sid]}
        model.constraint({**terms,e:-1},upper=desired)
        model.constraint({**terms,e:1},lower=desired)
    z,r = solve_model(model,out,'baseline_asset_distribution',120,1e-9)
    assert r['accepted']
    for sid in stations:
        stations[sid]['initial_units'] = list(next(p for p in choices[sid] if z[x[sid,p]]>.5))
    return sum(sum(s['initial_units']) for s in stations.values())


def prepare(out):
    out.mkdir(parents=True,exist_ok=True)
    stats = aggregate_profile(out)
    b,sc,d,p,c,prices = load_inputs()
    keys = sorted(k for k in b if k[:2]==CITY)
    physical = station_metadata({k[2] for k in keys})
    annual = {int(r['year']):float(r['reported_downward_load_mw']) for r in read_csv(OUTPUT_DIR/'official_annual.csv')
              if r['region_id']==CITY[0] and r['voltage_kv']=='110'}
    g = (annual[2025]/annual[2021])**.25-1
    scale2025 = annual[2025]/p[CITY+(2025,)]
    stations = {}
    for k in keys:
        old = b[k]
        sid = k[2]
        template = sc[k,2025]
        peak2025 = float(template['estimated_station_forward_peak_mw'])*scale2025
        reverse2025 = float(template['reverse_screen_mw'])*scale2025
        metadata = physical[sid]
        stations[sid] = {'station':sid,'old_units':[float(old[f'simulation_unit_{i}_mva']) for i in (1,2)],
                         'asset_capacity_mva':float(old['source_capacity_mva_2025'] or 0),
                         'base_forward_mw':peak2025*annual[2021]/annual[2025],
                         'base_reverse_mw':reverse2025*annual[2021]/annual[2025],
                         'forward_duration_h':stats['mean']['longest_hours'],
                         'reverse_duration_h':int(d[k]['reverse_d95_max_run_hours']),
                         'allow_third':metadata['available_third_slots']>=1 and metadata['available_third_mva']>=50,
                         'metadata':metadata}
    initial_capacity = reconstruct_baseline(stations,2*annual[2021],out/'solver_logs')
    factors = cost_factors()
    transformer_price = next(r['base_coefficient_10k_cny_per_purchased_mva'] for r in replacement_cost_coefficients() if r['voltage_kv']==110)
    third_prices = [float(r['static_total_10k_cny']) for r in read_cost_references()
                    if r['voltage_kv']==110 and r['measure_type']=='third_transformer_expansion' and r['purchased_transformer_mva']==50]
    assert len(third_prices)==2
    physical_max = sum(sum(max(v,80) for v in s['initial_units'])+50*int(s['allow_third']) for s in stations.values())
    source_paths = [CITY_SOURCE,OUTPUT_DIR/'baseline_2021_station_candidates.csv',OUTPUT_DIR/'official_annual.csv',
                    OUTPUT_DIR/'transformer_only_path_station_2021_2025.csv',OUTPUT_DIR/'static_storage_need_screen_2025.csv',
                    out/'city_2025_mapping_audit.csv',Path(__file__)]
    inputs = {'scope':'市区29站等效模型，基期真实区县峰值；规划年标签2022—2025为四年增长仿真，不冒称历史复现',
              'annual_observed_peak_mw':annual,'growth_rate':g,'initial_peak_mw':annual[2021],
              'initial_capacity_mva':initial_capacity,'initial_clr':initial_capacity/annual[2021],
              'initial_transfer_fraction':.4,'transfer_ceiling':1.,
              'transfer_ceiling_basis':'仅限制正常转出不超过本站原负荷；不统一指定市区A类，不把导则推荐比例当热容量',
              'physical_capacity_upper_mva':physical_max,'stations':stations,'new_ratings':NEW_RATINGS,
              'cost_factors':factors,'transformer_price_10k_per_purchased_mva':transformer_price,
              'third_50mva_capex_10k':sum(third_prices)/len(third_prices),
              'storage_module_mwh':.215,'storage_module_mw':.1,'storage_module_capex_10k':storage_anchors()[1]/10,
              'line_capex_10k':line_capex(.9),'line_cable_fraction':.9,
              'line_cost_coefficient':1+.9*(180/24-1),
              'line_increment_mw':new_line_increment_reference()['new_line_increment_mw'],
              'source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in source_paths},
              'n1_basis':'正常转接后逐站每台主变N-1满足本站全部负荷；无额外事故转供',
              'storage_basis':'给定正反向持续时间的功率能量静态折算；未计算SOC、效率衰减及充电调度',
              'line_basis':'市区线路构成暂沿用原90%电缆参考造价；项目为等效能力，不是实际路由'}
    dump(out/'pilot_inputs.json',inputs)
    dump(out/'accepted_scope.json',{'cases':CASES,'elastic_floor':2.001,'rigid_ceiling':2.,
                                  'elastic_ceiling':'equipment capacity only','cross_region_order':False,
                                  'cost_order_required':False,'prefer_larger_clr':False,
                                  'notes':'首轮仅市区40%，不改正式结果、不重算全矩阵；本文件替代上一版讨论中的两类推荐与纯联络组'})
    print(json.dumps({'prepared':True,'district_duration_h':stats['mean']['longest_hours'],
                      'initial_capacity_mva':initial_capacity,'initial_clr':inputs['initial_clr'],
                      'growth_rate':g,'physical_max_mva':physical_max},ensure_ascii=False),flush=True)


def build(inputs, case, diagnostic=False):
    storage = not case.endswith('no_storage')
    elastic = case.startswith('elastic')
    stations = inputs['stations']
    model = LinearModel()
    x,purchase,third,third_added,modules = {},{},{},{},{}
    outgoing,incoming,ends,excess,projects,project_add,slack = {},{},{},{},{},{},{}
    original_cost = {}
    rho = inputs['initial_transfer_fraction']
    inc = inputs['line_increment_mw']
    max_projects = sum(math.ceil(s['base_forward_mw']*(1+inputs['growth_rate'])**4/inc) for s in stations.values())
    ft,fb,fl = ({int(y):v for y,v in inputs['cost_factors'][k].items()} for k in ('transformer','storage','line'))
    peaks = {y:inputs['initial_peak_mw']*(1+inputs['growth_rate'])**(y-2021) for y in YEARS}
    loads,reverse = {},{}
    for sid,s in stations.items():
        for y in YEARS:
            scale=(1+inputs['growth_rate'])**(y-2021)
            loads[sid,y]=s['base_forward_mw']*scale
            reverse[sid,y]=s['base_reverse_mw']*scale
            if s['allow_third']:
                third[sid,y]=model.variable(0)
                third_added[sid,y]=model.variable(inputs['third_50mva_capex_10k']*ft[y])
                terms={third[sid,y]:1,third_added[sid,y]:-1}
                if y>YEARS[0]:terms[third[sid,y-1]]=-1
                model.constraint(terms,0,0)
            max_energy=max(loads[sid,y]*max(2.15,s['forward_duration_h']),
                           reverse[sid,y]*max(2.15,s['reverse_duration_h']))
            modules[sid,y]=model.variable(inputs['storage_module_capex_10k']*(fb[y]-fb.get(y+1,0)),
                                          upper=math.ceil(max_energy/.215) if storage else 0)
            if y>YEARS[0]:model.constraint({modules[sid,y]:1,modules[sid,y-1]:-1},lower=0)
            for slot,old in enumerate(s['initial_units']):
                ratings=sorted({old,*[r for r in NEW_RATINGS if r>=old]})
                for rating in ratings:
                    k=sid,slot,y,rating
                    x[k]=model.variable(0)
                    purchase[k]=model.variable(rating*inputs['transformer_price_10k_per_purchased_mva']*ft[y],upper=1,integer=0)
                    terms={purchase[k]:1,x[k]:-1}
                    if y==YEARS[0]:lower=-int(rating==old)
                    else:terms[x[sid,slot,y-1,rating]]=1;lower=0
                    model.constraint(terms,lower=lower)
                model.constraint({x[sid,slot,y,r]:1 for r in ratings},1,1)
                if y>YEARS[0]:
                    terms={x[sid,slot,y,r]:r for r in ratings}
                    terms.update({x[sid,slot,y-1,r]:-r for r in ratings})
                    model.constraint(terms,lower=0)
            terms={v:(r if slot==0 else -r) for (st,slot,yy,r),v in x.items() if st==sid and yy==y}
            model.constraint(terms,upper=0)
    for y in YEARS:
        projects[y]=model.variable(0,upper=max_projects)
        project_add[y]=model.variable(inputs['line_capex_10k']*fl[y],upper=max_projects,integer=0)
        terms={projects[y]:1,project_add[y]:-1}
        if y>YEARS[0]:terms[projects[y-1]]=-1
        model.constraint(terms,0,0)
        balance,endpoint,budget={},{projects[y]:-2},{projects[y]:-inc}
        for sid,s in stations.items():
            base=loads[sid,y]
            q0=rho*s['base_forward_mw']
            outgoing[sid,y]=model.variable(0,upper=base,integer=0)
            incoming[sid,y]=model.variable(0,upper=sum(loads[t,y] for t in stations),integer=0)
            ends[sid,y]=model.variable(0,upper=max_projects)
            excess[sid,y]=model.variable(0,upper=base,integer=0)
            qo,qi,unit,ex=outgoing[sid,y],incoming[sid,y],ends[sid,y],excess[sid,y]
            # 对同一站禁止同时转出和转入，以保持单目标下输出确定的物理含义。
            direction=model.variable(0)
            model.constraint({qo:1,direction:-base},upper=0)
            total_load=sum(loads[t,y] for t in stations)
            model.constraint({qi:1,direction:total_load},upper=total_load)
            model.constraint({qo:1,unit:-inc},upper=q0)
            model.constraint({qo:1,ex:-1},upper=q0)
            model.constraint({unit:1,projects[y]:-1},upper=0)
            if y>YEARS[0]:
                terms={unit:1,ends[sid,y-1]:-1}
                model.constraint(terms,lower=0)
                model.constraint({**terms,project_add[y]:-1},upper=0)
            balance[qo]=1;balance[qi]=-1;endpoint[unit]=1;budget[ex]=1
        model.constraint(balance,0,0)
        model.constraint(endpoint,0,0)
        model.constraint(budget,upper=0)
        capacity={}
        for sid,s in stations.items():
            cap={v:r for (st,slot,yy,r),v in x.items() if st==sid and yy==y}
            if (sid,y) in third:cap[third[sid,y]]=50.
            capacity.update(cap)
            forward_power=.215/max(2.15,s['forward_duration_h'])
            reverse_power=.215/max(2.15,s['reverse_duration_h'])
            qout,qin=outgoing[sid,y],incoming[sid,y]
            forward={v:PF*c for v,c in cap.items()}
            forward.update({modules[sid,y]:forward_power,qout:1,qin:-1})
            model.constraint(forward,lower=loads[sid,y])
            back={v:PF*c for v,c in cap.items()}
            back.update({modules[sid,y]:reverse_power,qout:-1})
            model.constraint(back,lower=reverse[sid,y])
            if diagnostic:slack[sid,y]=model.variable(0,upper=sum(loads[t,y] for t in stations),integer=0)
            # 与原案例相同：正常转接后负荷由每次N-1剩余主变和储能满足。
            for failed in (0,1,2) if s['allow_third'] else (0,1):
                terms={v:PF*r for (st,slot,yy,r),v in x.items() if st==sid and yy==y and slot!=failed}
                if failed!=2 and s['allow_third']:terms[third[sid,y]]=PF*50
                terms.update({modules[sid,y]:forward_power,qout:1,qin:-1})
                lower=loads[sid,y]
                if failed==2:
                    big_m=sum(loads[t,y] for t in stations)
                    terms[third[sid,y]]=-big_m
                    lower-=big_m
                if diagnostic:terms[slack[sid,y]]=1
                model.constraint(terms,lower=lower)
        floor=2.001 if elastic else 1.5
        model.constraint(capacity,lower=floor*peaks[y],
                         upper=inputs['physical_capacity_upper_mva'] if elastic else 2*peaks[y])
    original_cost=list(model.costs)
    if diagnostic:
        model.costs=[0.]*len(model.costs)
        for v in slack.values():model.costs[v]=1
    meta={'x':x,'third':third,'modules':modules,'out':outgoing,'in':incoming,'ends':ends,
          'projects':projects,'project_add':project_add,'loads':loads,'reverse':reverse,
          'peaks':peaks,'slack':slack,'original_cost':original_cost,'max_projects':max_projects}
    return model,meta


def extract(inputs,case,z,meta,solver):
    strows,years,line_rows=[],[],[]
    factors=inputs['cost_factors']
    previous_units={sid:s['initial_units'] for sid,s in inputs['stations'].items()}
    previous_third={sid:0 for sid in previous_units}
    previous_modules={sid:0 for sid in previous_units}
    previous_ends={sid:0 for sid in previous_units}
    inc=inputs['line_increment_mw']
    for y in YEARS:
        increments={sid:round(z[meta['ends'][sid,y]])-previous_ends[sid] for sid in previous_ends}
        pairs=pair_equivalent_units(increments)
        assert len(pairs)==round(z[meta['project_add'][y]])
        for a,b in pairs:line_rows.append({'year':y,'station_a':a,'station_b':b,'capacity_mw':inc,
                                          'capex_10k':inputs['line_capex_10k'],'status':'等效双端计费配对，非实际路由'})
        for sid,s in inputs['stations'].items():
            units=[next(r for (st,sl,yy,r),v in meta['x'].items() if st==sid and sl==slot and yy==y and z[v]>.5) for slot in (0,1)]
            third=50*round(z[meta['third'][sid,y]]) if (sid,y) in meta['third'] else 0
            n=round(z[meta['modules'][sid,y]])
            end=round(z[meta['ends'][sid,y]])
            cap=sum(units)+third
            available_n1=PF*(cap-max(*units,third))+.215*n/max(2.15,s['forward_duration_h'])
            qo,qi=float(z[meta['out'][sid,y]]),float(z[meta['in'][sid,y]])
            load=meta['loads'][sid,y]
            q0=inputs['initial_transfer_fraction']*s['base_forward_mw']
            replaced=sum(new for old,new in zip(previous_units[sid],units) if new>old+1e-6)
            new_third=third-previous_third[sid]
            tcapex=replaced*inputs['transformer_price_10k_per_purchased_mva']+(inputs['third_50mva_capex_10k'] if new_third else 0)
            bcapex=(n-previous_modules[sid])*inputs['storage_module_capex_10k']
            row={'case':case,'year':y,'station':sid,'unit_1_mva':units[0],'unit_2_mva':units[1],'unit_3_mva':third,
                 'capacity_mva':cap,'purchased_mva':replaced+new_third,'new_third_count':int(new_third>0),
                 'forward_mw':load,'reverse_mw':meta['reverse'][sid,y],'outgoing_mw':qo,'incoming_mw':qi,
                 'post_transfer_mw':load-qo+qi,'n1_available_mw':available_n1,'n1_margin_mw':available_n1-load+qo-qi,
                 'normal_margin_mw':PF*cap+.215*n/max(2.15,s['forward_duration_h'])-load+qo-qi,
                 'reverse_margin_mw':PF*cap+.215*n/max(2.15,s['reverse_duration_h'])-meta['reverse'][sid,y]-qo,
                 'storage_modules':n,'storage_nameplate_mw':.1*n,'storage_mwh':.215*n,
                 'storage_forward_effective_mw':.215*n/max(2.15,s['forward_duration_h']),
                 'storage_reverse_effective_mw':.215*n/max(2.15,s['reverse_duration_h']),
                 'forward_duration_h':s['forward_duration_h'],'reverse_duration_h':s['reverse_duration_h'],
                 'initial_transfer_capacity_mw':q0,'new_line_ends':end,
                 'transfer_capacity_mw':min(load,q0+end*inc),
                 'transfer_capacity_fraction':min(load,q0+end*inc)/load,
                 'transformer_capex_10k':tcapex,'storage_capex_10k':bcapex}
            strows.append(row)
            previous_units[sid]=units;previous_third[sid]=third;previous_modules[sid]=n;previous_ends[sid]=end
        local=[r for r in strows if r['year']==y]
        totalcap=sum(r['capacity_mva'] for r in local)
        linecapex=round(z[meta['project_add'][y]])*inputs['line_capex_10k']
        years.append({'case':case,'year':y,'planning_year':y-2021,'peak_mw':meta['peaks'][y],
                      'capacity_mva':totalcap,'clr':totalcap/meta['peaks'][y],
                      'storage_nameplate_mw':sum(r['storage_nameplate_mw'] for r in local),
                      'storage_forward_effective_mw':sum(r['storage_forward_effective_mw'] for r in local),
                      'storage_mwh':sum(r['storage_mwh'] for r in local),
                      'transfer_mw':sum(r['outgoing_mw'] for r in local),
                      'new_lines':round(z[meta['project_add'][y]]),'lines_in_service':round(z[meta['projects'][y]]),
                      'new_transformer_purchase_mva':sum(r['purchased_mva'] for r in local),
                      'new_third_count':sum(r['new_third_count'] for r in local),
                      'transformer_capex_10k':sum(r['transformer_capex_10k'] for r in local),
                      'storage_capex_10k':sum(r['storage_capex_10k'] for r in local),'line_capex_10k':linecapex})
    npv={k:sum(r[k+'_capex_10k']*factors[k][str(r['year'])] for r in years) for k in ('transformer','storage','line')}
    checks={'min_n1_margin_mw':min(r['n1_margin_mw'] for r in strows),
            'min_normal_margin_mw':min(r['normal_margin_mw'] for r in strows),
            'min_reverse_margin_mw':min(r['reverse_margin_mw'] for r in strows),
            'max_balance_error_mw':max(abs(sum(r['outgoing_mw']-r['incoming_mw'] for r in strows if r['year']==y)) for y in YEARS),
            'npv_recomputed_10k':sum(npv.values()),'npv_objective_error_10k':abs(sum(npv.values())-solver['objective']),
            'max_transfer_budget_violation_mw':max(0.,max(r['outgoing_mw']-r['transfer_capacity_mw'] for r in strows)),
            'max_shared_new_capacity_violation_mw':max(0.,max(sum(max(0,r['outgoing_mw']-r['initial_transfer_capacity_mw']) for r in strows if r['year']==y)-round(z[meta['projects'][y]])*inc for y in YEARS))}
    assert min(checks[k] for k in ('min_n1_margin_mw','min_normal_margin_mw','min_reverse_margin_mw'))>=-1e-5
    assert checks['max_balance_error_mw']<1e-5 and checks['npv_objective_error_10k']<.01
    assert checks['max_transfer_budget_violation_mw']<1e-5 and checks['max_shared_new_capacity_violation_mw']<1e-5
    for r in years:
        assert r['clr']>=2.001-1e-7 if case.startswith('elastic') else 1.5-1e-7<=r['clr']<=2+1e-7
    if case.endswith('no_storage'):assert all(r['storage_modules']==0 for r in strows)
    summary={'case':case,'solver':solver,'cost_npv_10k':sum(npv.values()),'cost_components_npv_10k':npv,
             'final_year':years[-1],'validation':checks,'input_sha256':sha(OUT/'pilot_inputs.json')}
    return strows,years,line_rows,summary


def run_case(out,case,seconds):
    inputs=json.loads((out/'pilot_inputs.json').read_text())
    model,meta=build(inputs,case)
    directory=out/case
    directory.mkdir(exist_ok=True)
    z,result=solve_model(model,directory,case,seconds,.01)
    if result['accepted']:
        stations,years,lines,summary=extract(inputs,case,z,meta,result)
        write_csv(directory/'stations.csv',stations);write_csv(directory/'years.csv',years);write_csv(directory/'lines.csv',lines)
        dump(directory/'summary.json',summary)
    else:
        dump(directory/'summary.json',{'case':case,'solver':result,'input_sha256':sha(out/'pilot_inputs.json')})
    if result['proven_infeasible'] and case.endswith('no_storage'):
        model,meta=build(inputs,case,diagnostic=True)
        z,diag=solve_model(model,directory,case+'_n1_shortfall_diagnostic',seconds,.01)
        if diag['accepted']:
            rows=[{'year':y,'station':sid,'n1_shortfall_mw':float(z[v])} for (sid,y),v in meta['slack'].items() if z[v]>1e-7]
            write_csv(directory/'n1_shortfall_diagnostic.csv',rows)
        dump(directory/'diagnostic.json',{'solver':diag,'meaning':'仅放松站级N-1约束后，站级缺口之和最小；不是可推荐供电方案，非区县同期失负荷'})


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--prepare',action='store_true')
    p.add_argument('--case',choices=CASES)
    p.add_argument('--seconds',type=int,default=600)
    args=p.parse_args()
    if args.prepare:prepare(OUT)
    if args.case:run_case(OUT,args.case,args.seconds)


if __name__=='__main__':
    raise SystemExit('该历史独立入口已归档；请使用 实验.研究.rebuild_2026.static_actual_20261010。公共函数仍保留供现行模型导入。')
    main()
