"""按首尾开口区间归档；有限采样范围单独登记，不改变容载比定义。"""
import argparse
import copy
import hashlib
import itertools
import json
import math
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import highspy
import numpy as np
from scipy.sparse import coo_matrix

from ..static_actual_20261010 import run as actual
from ..current_economic_assumptions import cost_factors
from ..synchronous_20261009 import model as assets

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / '研究报告/试算/20261010_五参数推广'
CONFIG = ROOT / '研究报告/试算/20261010_推广矩阵优化方案/参数设计.json'
PARAMS = ['eta', 'growth_rate', 'line_cost_coefficient', 'initial_transfer_fraction', 'support_duration_h']


def bins(row):
    cuts = [[1, 2], [.02, .04, .07], [1.65, 6.85], [.3, .5], [2, 4]]
    return tuple(sum(row[key] > x for x in cut) for key, cut in zip(PARAMS, cuts))


def make_input(parameters):
    p = dict(eta=1., growth_rate=.04, line_cost_coefficient=4.25,
             initial_transfer_fraction=.4, support_duration_h=4., topology='ring',
             diversity=1.1, storage_price=1., transformer_price=1., usable=.76,
             length_km=3., thermal_factor=1., pf=.95, third=True, allow80=True,
             discount_factor=1., asset_life_factor=1., maintenance_factor=1., shape='base', lower=2.001)
    p.update(parameters)
    g=p['growth_rate']; scale=(1+g)**4; peak=250*scale
    weights=np.array([.1,.15,.2,.25,.3] if p['shape']=='base' else [.18,.19,.20,.21,.22])
    base=250*weights; load=peak*weights; kd=p['diversity']
    # 区域同期峰值不变；各站非同时峰值用独立静态场景表达。
    scenes=[load.copy()]
    if kd>1:
        for i in range(5):
            local=load.copy(); extra=(kd-1)*load[i]
            local-=extra*load/(peak-load[i]);local[i]=kd*load[i]
            assert abs(local.sum()-peak)<1e-8 and min(local)>=0
            scenes.append(local)
    scenes.append(.30*load-.75*p['eta']*peak*np.array([.08,.14,.18,.25,.35]))
    inp=dict(years=[2025],growth_rate=g,initial_peak_mw=250.,initial_capacity_mva=500.,
             annual_observed_peak_mw={'2025':peak},physical_capacity_upper_mva=5*(160 if p['allow80'] else 126)+250*int(p['third']),
             initial_transfer_fraction=p['initial_transfer_fraction'],line_increment_mw=7.49106117,
             transformer_price_10k_per_purchased_mva=16.57333333333333*p['transformer_price'],
             third_50mva_capex_10k=1223*p['transformer_price'],storage_module_capex_10k=21.0456262*p['storage_price'],
             storage_usable_energy_fraction=p['usable'],line_capex_10k=p['length_km']*24*p['line_cost_coefficient']+6,
             cost_factors=cost_factors(),stations={})
    if any(p[k]!=1 for k in ('discount_factor','asset_life_factor','maintenance_factor')):
        from ..joint_lifecycle_optimizer import npv_factor
        for name,life,om in [('transformer',40,.042),('line',40,.022),('storage',25,.03)]:
            inp['cost_factors'][name][2025]=npv_factor(2025,.06*p['discount_factor'],round(life*p['asset_life_factor']),om*p['maintenance_factor'])
    feeders={};edges=[];rho=p['initial_transfer_fraction']
    for i in range(5):
        sid=f'T{i+1}'
        inp['stations'][sid]=dict(initial_units=[50.,50.],allow_third=p['third'],base_forward_mw=float(base[i]*kd),
             base_reverse_mw=max(0.,float(-scenes[-1][i]/scale)),forward_duration_h=p['support_duration_h'],
             reverse_duration_h=p['support_duration_h'],metadata={'spare_10kv_bays':2})
        for j in range(2):
            # 同一馈线的全部联络共用可转负荷和接收余量，既有热限不随规划负荷增长。
            feeders[f'{sid}F{j}']=dict(station=sid,maximum_load_proxy_2025_mw=float(base[i]*kd*scale/2),
                 thermal_mw=float((base[i]*kd/2+rho*base[i]/2)*p['thermal_factor']))
    ring={tuple(sorted((i,(i+1)%5))) for i in range(5)}
    for n,(i,j) in enumerate(sorted(ring)):
        edges.append(dict(id=f'E{n}',a=f'T{i+1}F0',b=f'T{j+1}F1',station_a=f'T{i+1}',station_b=f'T{j+1}',
            existing=True,bidirectional=True,capacity_mw=rho*max(base[i],base[j])/2,
            source_section_fraction=1.,new_bay_station=''))
    pairs=sorted(ring) if p['topology']=='ring' else list(itertools.combinations(range(5),2))
    for n,(i,j) in enumerate(pairs):
        for f in range(2):
            edges.append(dict(id=f'N{n}-{f}',a=f'T{i+1}F{f}',b=f'T{j+1}F{1-f}',station_a=f'T{i+1}',station_b=f'T{j+1}',
                existing=False,bidirectional=True,capacity_mw=7.49106117,source_section_fraction=1.,new_bay_station=''))
    inp['network']={'feeders':feeders,'edges':edges}
    return inp,{2025:np.array(scenes)},p,base


def solve(parameters):
    started=time.monotonic();inp,scenes,p,base=make_input(parameters)
    actual.network.limits=actual.actual_limits
    actual.network.PF=p['pf']
    # 当前静态模型将资产和网络分开创建，既有模型文件不改。
    m,meta=actual.build(inp,scenes,'elastic_storage')
    cap=actual.capacity_terms(inp,meta,2025)
    for r in range(len(m.constraint_lower)):
        terms={c:v for rr,c,v in m.entries if rr==r}
        if terms==cap:m.constraint_lower[r]=p['lower']*inp['annual_observed_peak_mw']['2025']
    if not p['allow80']:
        for key,v in meta['x'].items():
            if key[-1]==80:m.upper_bounds[v]=0
    # 存量转供预算固定为基期MW，不因年负荷增长免费增加。
    edge_map={e['id']:e for e in inp['network']['edges']}
    groups={}
    for y,h,f,e,d,v in meta['network_flows']:
        edge=edge_map[e]
        if edge['existing']:
            sid=edge['station_a'] if d==0 else edge['station_b']
            groups.setdefault((h,f,sid),{})[v]=1
    for (h,f,sid),terms in groups.items():m.constraint(terms,upper=p['initial_transfer_fraction']*base[int(sid[1:])-1])
    rr,cc,vv=zip(*m.entries);a=coo_matrix((vv,(rr,cc)),shape=(len(m.constraint_lower),len(m.costs))).tocsr()
    lp=highspy.HighsLp();lp.num_col_,lp.num_row_=a.shape[1],a.shape[0]
    lp.col_cost_,lp.col_lower_,lp.col_upper_=m.costs,m.lower_bounds,m.upper_bounds
    lp.row_lower_,lp.row_upper_=m.constraint_lower,m.constraint_upper
    lp.integrality_=[highspy.HighsVarType.kInteger if x else highspy.HighsVarType.kContinuous for x in m.integrality]
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise;lp.a_matrix_.start_,lp.a_matrix_.index_,lp.a_matrix_.value_=a.indptr,a.indices,a.data
    h=highspy.Highs()
    for k,v in [('threads',1),('random_seed',0),('mip_rel_gap',.005),('time_limit',parameters.get('seconds',20.)),('log_to_console',False)]:h.setOptionValue(k,v)
    h.passModel(lp);h.run();info=h.getInfo();solution=h.getSolution()
    row={**p,'status':h.modelStatusToString(h.getModelStatus()),'elapsed':time.monotonic()-started,
         'sample_set':parameters.get('sample_set','main'),'verified':False,'peak_mw':inp['annual_observed_peak_mw']['2025'],
         'cost_lower':float(info.mip_dual_bound) if math.isfinite(info.mip_dual_bound) else None,
         'relative_gap':float(info.mip_gap) if math.isfinite(info.mip_gap) else None,
         'bin':bins(p),'variables':len(m.costs),'constraints':len(m.constraint_lower)}
    if not solution.value_valid or info.primal_solution_status!=2:return row
    z=np.array(solution.col_value);az=a@z;integer=np.array(m.integrality,dtype=bool)
    violation=max(0.,float(np.max(np.array(m.constraint_lower)-az)),float(np.max(az-np.array(m.constraint_upper))),
                  float(np.max(np.array(m.lower_bounds)-z)),float(np.max(z-np.array(m.upper_bounds))),
                  float(np.max(abs(z[integer]-np.round(z[integer])))))
    assert violation<1e-5,(p,violation)
    units,n,_,_=assets.assets(inp,z,meta,2025)
    built={e for (e,y),v in meta['edgevars'].items() if z[v]>.5}
    check,violations=actual.network.check_year(inp,scenes[2025],2025,units,n,built)
    assert not violations,(p,check)
    purchased=np.where(units[:,:2]>50+1e-5,units[:,:2],0).sum()
    tc=purchased*inp['transformer_price_10k_per_purchased_mva']+units[:,2].sum()/50*inp['third_50mva_capex_10k']
    bc=n.sum()*inp['storage_module_capex_10k'];lc=len(built)*inp['line_capex_10k']
    costs={name:float(value*inp['cost_factors'][name][2025]) for name,value in [('transformer',tc),('storage',bc),('line',lc)]}
    assert abs(sum(costs.values())-info.objective_function_value)<1e-4
    flows=[dict(scenario=int(hh),failed=int(f),edge=e,direction=d,mw=float(z[v])) for y,hh,f,e,d,v in meta['network_flows'] if z[v]>1e-6]
    normal=[x for x in flows if x['scenario']==0 and x['failed']==-1]
    row.update(verified=True,capacity_mva=float(units.sum()),clr=float(units.sum()/row['peak_mw']),
        cost=float(info.objective_function_value),cost_components=costs,storage_modules=int(n.sum()),
        storage_mw=float(n.sum()*.1),storage_mwh=float(n.sum()*.215),line_count=len(built),
        nominal_transfer_mw=float(p['initial_transfer_fraction']*sum(base)),normal_transfer_mw=sum(x['mw'] for x in normal),
        units=units.tolist(),modules=n.tolist(),built=sorted(built),flows=flows,
        matrix_violation=violation,independent_network_check=check)
    return row


def task_cases(kind):
    c=json.loads(CONFIG.read_text());grid=c['小样本' if kind=='pilot' else '主网格']
    if kind in ('pilot','main'):
        return [{**dict(zip(PARAMS,values)),'topology':top,'sample_set':kind}
                for top in (['ring','dense'] if kind=='pilot' else ['ring']) for values in itertools.product(*(grid[k] for k in PARAMS))]
    result=[]
    # 每一辅助参数均在固定其余参数的条件下改变；首尾档、阈值及两地锚点另存。
    extras={'eta':[.32,1.63,4.], 'growth_rate':[-.02,.01336129306847722,.06923192559398061,.15],
            'line_cost_coefficient':[.75,9.], 'initial_transfer_fraction':[0.,.28287889057972354,.8],
            'support_duration_h':[1.,8.], 'storage_price':[.5,.75,1.,1.25],
            'transformer_price':[.75,1.,1.25], 'diversity':[1.,1.1,1.15], 'usable':[.65,.76,.85],
            'length_km':[1.,3.,5.], 'thermal_factor':[.8,1.,1.2], 'pf':[.9,.95,.98],
            'third':[False,True], 'allow80':[False,True], 'topology':['ring','dense'],
            'discount_factor':[.8,1.,1.2], 'asset_life_factor':[.8,1.,1.2],
            'maintenance_factor':[.8,1.,1.2], 'shape':['base','even'], 'lower':[1.6,2.001]}
    for eta,H in itertools.product([.5,2.5],[2.,4.,6.]):
        base={'eta':eta,'support_duration_h':H,'sample_set':'sensitivity'}
        for key,values in extras.items():
            for value in values:result.append({**base,key:value,'varied':key})
    for k,thresholds in [('growth_rate',[.02,.04,.07]),('eta',[1.,2.]),('initial_transfer_fraction',[.3,.5]),('line_cost_coefficient',[1.65,6.85]),('support_duration_h',[2.,4.])]:
        for x in thresholds:
            for delta in [-1e-4,0.,1e-4]:result.append({k:x+delta,'sample_set':'boundary','varied':k})
    return result


def execute_task(p):
    r=solve(p);r['varied']=p.get('varied');return r


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--kind',choices=['pilot','main','sensitivity'],default='pilot')
    ap.add_argument('--workers',type=int,default=8);ap.add_argument('--seconds',type=float,default=20);args=ap.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);cases=task_cases(args.kind)
    path=OUT/(args.kind+'.jsonl');done={}
    if path.exists():
        for line in path.read_text().splitlines():
            r=json.loads(line);done[r['task_id']]=r
    pending=[]
    for i,p in enumerate(cases):
        if i not in done:pending.append({**p,'task_id':i,'seconds':args.seconds})
    print('TASKS',args.kind,'total',len(cases),'pending',len(pending),flush=True)
    with path.open('a') as f,ProcessPoolExecutor(max_workers=args.workers) as pool:
        for p,r in zip(pending,pool.map(execute_task,pending,chunksize=1)):
            r['task_id']=p['task_id'];f.write(json.dumps(r,ensure_ascii=False)+'\n');f.flush()
            if (p['task_id']+1)%20==0:print('PROGRESS',args.kind,p['task_id']+1,len(cases),r['status'],flush=True)
    records=[json.loads(x) for x in path.read_text().splitlines()]
    assert len(records)==len(cases)
    summary={'set':args.kind,'count':len(records),'verified':sum(r['verified'] for r in records),
             'status_counts':{s:sum(r['status']==s for r in records) for s in {r['status'] for r in records}},
             'config_sha256':hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
             'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (OUT/(args.kind+'_summary.json')).write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(summary,flush=True)


if __name__=='__main__':main()
