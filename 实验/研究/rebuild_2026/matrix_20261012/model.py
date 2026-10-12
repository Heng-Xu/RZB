"""10%～90%等步长转供局部补充；设备层函数沿用收资锚点模型。

从案例校准模型独立复制，仅修正既有环网首尾边的馈线组映射，
并增加联合情景取值域；设备、费用及静态安全约束保持原实现。

光伏按原站母线等值注入；两组联络馈线只表达可切换用户负荷。
馈线组是聚合通道，不是两条实际10 kV馈线。未建模光伏接入支路、
电压及保护校核。费用边界与当前报告一致，正式模型文件不改。
"""
import hashlib
import json
import math
import time
from collections import defaultdict

import highspy
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

from ..annual_no_tie_investment_submodel import LinearModel
from ..current_economic_assumptions import cost_factors, line_capex

FIELDS = ['eta', 'growth_rate', 'cable_fraction', 'initial_transfer_fraction',
          'support_duration_h', 'diversity']

AREA_SCENARIOS = {
    '一般城镇及较弱网络参考': dict(cable_nodes=[.1, .3, .5], transfer_nodes=[.1, .2, .3, .4, .5],
        basis='30%～50%沿用DL/T 5729—2023第7.1.2条B/C类参考；10%/20%为较弱既有网络研究拓展，电缆分组为研究设定'),
    '邳州较高转供参考': dict(cable_nodes=[.1, .3], transfer_nodes=[.6, .7],
        basis='邳州地区整体转供率约67%、电缆长度占比约10.76%提供数据背景；取60%/70%比较'),
    '核心及高可靠参考': dict(cable_nodes=[.3, .5, .8, .9],
        transfer_nodes=[.5, .6, .7, .8, .9],
        basis='50%～70%沿用2023版A+/A类参考；高段结合市区转供率约91%、电缆化率约80%的最新收资拓展'),
    '低电缆高转供研究拓展': dict(cable_nodes=[.1],transfer_nodes=[.8,.9],
        basis='架空占比较高时，可通过既有联络和接收余量形成高转供；作为受控研究情景，按具体网络约束求解'),
}


def matching_scenarios(parameters):
    def near(value, nodes): return any(abs(float(value)-x)<1e-9 for x in nodes)
    return [name for name, item in AREA_SCENARIOS.items()
            if near(parameters['cable_fraction'], item['cable_nodes'])
            and near(parameters['initial_transfer_fraction'], item['transfer_nodes'])]


def check_joint_domain(parameters):
    names=matching_scenarios(parameters)
    if not names:
        raise ValueError('该组合不在本次联合情景域；未作工程不可行判定')
    return names


def initial_transfer_audit(base, edges, thermal, budget, pf=.95):
    """初始网络的逐站单送端可转负荷能力，负荷加权汇总。

    每次仅一个送端转出原生负荷；受端使用固定馈线余量和正常主变余量。
    5站环的同一送端各边受端站互异，可直接求各馈线组的星形最大流。
    独立LP复核另见验证脚本。不是全部站同时转供，也不授予免费全区流。
    """
    limits=[]
    for s in range(5):
        by_group=defaultdict(float)
        for e in edges:
            if not e['existing']:continue
            if e['a']//2==s:a,b=e['a'],e['b']
            elif e['b']//2==s:a,b=e['b'],e['a']
            else:continue
            by_group[a]+=min(e['capacity'],max(thermal[b]-base[b//2]/2,0),
                             max(pf*100-base[b//2],0))
        limits.append(min(budget[s],sum(min(base[s]/2,c) for c in by_group.values())))
    return dict(station_transfer_mw=limits,station_rates=(np.array(limits)/base).tolist(),
                weighted_rate=float(sum(limits)/sum(base)))


def calibrate_initial_network(base, pairs, target, pf):
    """将输入转供率映射为可实现的初始网络指标，而非名义通道倍率。

    构造维度：同一环形网络既有通道规模与馈线接收余量共同变化。
    该形态为研究场景假设，六参数之外不再另外采样；费用仍仅计新增工程。
    """
    def network(scale):
        # 沿0→1→2→3→4→0布置环网，每站两个馈线组分别接相邻站。
        # 排序后的首尾边(0,4)应接0站组1与4站组0；避免两条边挤在同一组。
        es=[dict(id=f'E{n}',a=2*i+(1 if (i,j)==(0,4) else 0),
                 b=2*j+(0 if (i,j)==(0,4) else 1),existing=True,
                 capacity=scale*max(base[i],base[j])/2) for n,(i,j) in enumerate(pairs)]
        thermal=np.repeat(base*(1+scale)/2,2)
        audit=initial_transfer_audit(base,es,thermal,scale*base,pf)
        return es,thermal,audit
    lo,hi=0.,4.
    assert 0<=target<=network(hi)[2]['weighted_rate']+1e-9
    for _ in range(55):
        mid=(lo+hi)/2
        if network(mid)[2]['weighted_rate']<target:lo=mid
        else:hi=mid
    edges,thermal,audit=network((lo+hi)/2)
    assert abs(audit['weighted_rate']-target)<1e-9
    return edges,thermal,(lo+hi)/2,audit


def make_input(parameters):
    p = dict(eta=1., growth_rate=.04, cable_fraction=.2,
             initial_transfer_fraction=.4, support_duration_h=4., diversity=1.1,
             storage_price=1., thermal_factor=1.5, pf=.95, third=True,
             storage=True, existing=True, candidates=True, shape='base',
             line_length_km=3., clr_floor=0., receiver_budget=True,
             network_synthesis='realized_transfer',new_receiving_feeders=True,spare_bays=2)
    p.update(parameters)
    names=check_joint_domain(p)
    assert p['support_duration_h'] > 0 and p['diversity'] >= 1
    weights = np.array([.10, .15, .20, .25, .30] if p['shape'] == 'base'
                       else [.18, .19, .20, .21, .22])
    base = 250 * weights
    peak = 250 * (1 + p['growth_rate']) ** 4
    load = peak * weights
    gross = [load.copy()]
    if p['diversity'] > 1:
        for j in range(5):
            extra = (p['diversity'] - 1) * load[j]
            x = load - extra * load / (peak - load[j])
            x[j] = p['diversity'] * load[j]
            assert abs(x.sum() - peak) < 1e-8 and x.min() >= 0
            gross.append(x)
    gross.append(.30 * load)
    gross = np.array(gross)
    generation = np.zeros_like(gross)
    generation[-1] = .75 * p['eta'] * peak * np.array([.08, .14, .18, .25, .35])
    pairs = sorted({tuple(sorted((i, (i + 1) % 5))) for i in range(5)})
    edges = []
    for n, (i, j) in enumerate(pairs):
        edges.append(dict(id=f'E{n}', a=2*i, b=2*j+1, existing=True,
                          capacity=p['initial_transfer_fraction'] * max(base[i], base[j]) / 2
                          if p['existing'] else 0.))
        for f in range(2):
            edges.append(dict(id=f'N{n}-{f}', a=2*i+f, b=2*j+1-f,
                              existing=False, capacity=7.49106117 if p['candidates'] else 0.))
        if p['new_receiving_feeders']:
            for a,b in [(i,j),(j,i)]:
                for f in range(2):
                    edges.append(dict(id=f'F{n}-{a}-{f}',a=2*a+f,b=2*b,
                                      existing=False,dedicated=True,new_bay_station=b,
                                      capacity=7.49106117 if p['candidates'] else 0.))
    cf = cost_factors()
    # 固定为原模板参考条件 kd=1.10、rho=0.40 的能力系数1.50。
    # 与六项主参数分离；其变化另作网络假设敏感性。
    thermal = np.repeat(base * p['thermal_factor'] / 2, 2)
    existing_budget=p['initial_transfer_fraction']*base
    if p['network_synthesis']=='realized_transfer':
        existing,thermal,scale,initial_audit=calibrate_initial_network(
            base,pairs,p['initial_transfer_fraction'],p['pf'])
        for edge in existing:
            chosen=next(e for e in edges if e['id']==edge['id'])
            chosen.update(a=edge['a'],b=edge['b'],
                          capacity=edge['capacity'] if p['existing'] else 0.)
        existing_budget=scale*base
    else:
        scale=None
        initial_audit=initial_transfer_audit(base,edges,thermal,existing_budget,p['pf'])
    line_cost = line_capex(p['cable_fraction'])
    if p['line_length_km'] != 3:
        line_cost = p['line_length_km'] * (24 * (1-p['cable_fraction'])
                                         + 180 * p['cable_fraction']) + 6
    # 与两区县案例actual_limits一致：接收余量以该馈线组的年度峰值
    # 代理计算，各条联络共享；转出负荷不额外授予接收额度。
    receiver_headroom=np.maximum(thermal-np.repeat(gross.max(axis=0)/2,2),0.)
    return dict(p=p, base=base, peak=peak, gross=gross, generation=generation,
                net=gross-generation, edges=edges, thermal=thermal,
                receiver_headroom=receiver_headroom,
                existing_budget=existing_budget,initial_transfer_audit=initial_audit,
                joint_area_scenarios=names,
                initial_network_scale=scale,
                factors={k: cf[k][2025] for k in ['transformer', 'storage', 'line']},
                line_cost=line_cost, storage_unit_cost=21.0456262,
                transformer_cost_per_purchased_mva=16.57333333333333,
                third_cost=1223., usable_energy=.215*.76,
                storage_effective=min(.1, .215*.76/p['support_duration_h']))


def build(inp):
    p=inp['p']; m=LinearModel(); units={}; third={}; modules={}; built={}
    factors=inp['factors']
    for s in range(5):
        for sl in range(2):
            for rating in [50,63,80]:
                cost=0 if rating==50 else rating*inp['transformer_cost_per_purchased_mva']*factors['transformer']
                units[s,sl,rating]=m.variable(cost)
            m.constraint({units[s,sl,r]:1 for r in [50,63,80]},1,1)
        m.constraint({**{units[s,0,r]:r for r in [50,63,80]},
                      **{units[s,1,r]:-r for r in [50,63,80]}},upper=0)
        third[s]=m.variable(inp['third_cost']*factors['transformer'],upper=int(p['third']))
        max_power=float(np.max(np.abs(inp['net'][:,s])))+float(inp['gross'].sum(axis=1).max())
        modules[s]=m.variable(inp['storage_unit_cost']*p['storage_price']*factors['storage'],
                              upper=math.ceil(max_power/inp['storage_effective'])+1 if p['storage'] else 0)
    for e in inp['edges']:
        if not e['existing']:
            built[e['id']]=m.variable(inp['line_cost']*factors['line'],upper=int(e['capacity']>0))
    for s in range(5):
        m.constraint({built[e['id']]:1 for e in inp['edges'] if e.get('new_bay_station')==s},
                     upper=p['spare_bays'])
    if p['clr_floor']:
        terms={v:r for (s,sl,r),v in units.items()}
        terms.update({v:50 for v in third.values()})
        m.constraint(terms,lower=p['clr_floor']*inp['peak'])
    flowmeta=[]
    for h,D in enumerate(inp['gross']):
        for failed in range(-1,5):
            outgoing=defaultdict(dict); incoming=defaultdict(dict); netgroup=defaultdict(dict); existing=defaultdict(dict)
            new_incoming=defaultdict(dict)
            for e in inp['edges']:
                ev=[]
                for direction in range(1 if e.get('dedicated') else 2):
                    a,b=(e['a'],e['b']) if direction==0 else (e['b'],e['a'])
                    v=m.variable(0,upper=e['capacity'],integer=0); ev.append(v)
                    outgoing[a][v]=1; netgroup[a][v]=1
                    if e.get('dedicated'):new_incoming[b//2][v]=-1
                    else:incoming[b][v]=1;netgroup[b][v]=-1
                    if e['existing']:existing[a//2][v]=1
                    flowmeta.append((h,failed,e['id'],direction,v))
                terms={v:1 for v in ev}
                if not e['existing']:terms[built[e['id']]]=-e['capacity']
                m.constraint(terms,upper=e['capacity'] if e['existing'] else 0)
            for f in range(10):
                native=D[f//2]/2
                m.constraint(outgoing[f],upper=native)
                if p['receiver_budget']:
                    m.constraint(incoming[f],upper=inp['receiver_headroom'][f])
                # 馈线组供电负荷=原有用户负荷-转出+转入，逐工况受热限约束。
                m.constraint(netgroup[f],lower=native-inp['thermal'][f],upper=native)
            for s in range(5):
                m.constraint(existing[s],upper=inp['existing_budget'][s])
                cap={v:r for (ss,sl,r),v in units.items() if ss==s and not (failed==s and sl==1)}
                cap[third[s]]=50
                station_netout={**netgroup[2*s],**netgroup[2*s+1],**new_incoming[s]}
                # 每条边连接不同站，两个馈线组的变量集合不重叠。
                for sign in [1,-1]:
                    terms={v:p['pf']*r for v,r in cap.items()}
                    terms[modules[s]]=inp['storage_effective']
                    for v,c in station_netout.items():terms[v]=sign*c
                    m.constraint(terms,lower=sign*float(inp['net'][h,s]))
    return m, dict(units=units,third=third,modules=modules,built=built,flows=flowmeta)


def check_dispatch(inp, ratings, modules, chosen, flows):
    """直接由设备、原生负荷、电源和开关流量重算，不读取优化约束矩阵。"""
    grouped=defaultdict(list)
    for h,f,e,d,value in flows:grouped[h,f].append((e,d,value))
    edge_map={e['id']:e for e in inp['edges']};worst=0.;critical=None
    max_transfer=0.;max_day_transfer=0.;max_storage=0.
    for h,D in enumerate(inp['gross']):
        for failed in range(-1,5):
            out=np.zeros(10);inc=np.zeros(10);dedicated_inc=np.zeros(5);ex=np.zeros(5);tot=defaultdict(float)
            residuals=[]
            for name,d,value in grouped[h,failed]:
                e=edge_map[name];a,b=(e['a'],e['b']) if d==0 else (e['b'],e['a'])
                out[a]+=value;tot[name]+=value
                if e.get('dedicated'):dedicated_inc[b//2]+=value
                else:inc[b]+=value
                if e['existing']:ex[a//2]+=value
                residuals.append(-value)
            for name,e in edge_map.items():
                allowed=e['capacity'] if e['existing'] or name in chosen else 0.
                residuals.append(tot[name]-allowed)
            native=np.repeat(D/2,2);served=native-out+inc
            residuals.extend(out-native);residuals.extend(served-inp['thermal']);residuals.extend(-served)
            if inp['p']['receiver_budget']:
                residuals.extend(inc-inp['receiver_headroom'])
            residuals.extend(ex-inp['existing_budget'])
            station_load=served.reshape(5,2).sum(axis=1)+dedicated_inc
            station_net=station_load-inp['generation'][h]
            available=inp['p']['pf']*ratings.sum(axis=1)
            if failed>=0:available[failed]-=inp['p']['pf']*ratings[failed].max()
            support=modules*inp['storage_effective']
            residuals.extend(np.abs(station_net)-available-support)
            conservation=abs(station_net.sum()-inp['net'][h].sum())
            residuals.append(conservation)
            violation=max(0.,float(max(residuals)))
            if violation>worst:worst=violation;critical=[int(h),int(failed)]
            max_transfer=max(max_transfer,float(out.sum()))
            if h==len(inp['gross'])-1:max_day_transfer=max(max_day_transfer,float(out.sum()))
            max_storage=max(max_storage,float(np.maximum(abs(station_net)-available,0).sum()))
    bays=[sum(edge_map[name].get('new_bay_station')==s for name in chosen) for s in range(5)]
    worst=max(worst,float(max(bays)-inp['p']['spare_bays']))
    return dict(violating_pairs=0 if worst<1e-5 else 1,max_violation_mw=worst,
                checked_pairs=len(inp['gross'])*6,worst=critical,
                new_receiving_bays=bays,
                max_transfer_mw=max_transfer,max_day_transfer_mw=max_day_transfer,
                max_required_storage_effective_mw=max_storage)


def independent_lp_check(parameters, ratings, modules, chosen):
    """固定设备，用独立LP再求各工况的转供可行性，校核双向发送端与守恒。"""
    inp=make_input(parameters);ratings=np.array(ratings);modules=np.array(modules)
    arcs=[(e,d) for e in inp['edges'] for d in range(1 if e.get('dedicated') else 2)]; n=len(arcs);worst=None;count=0
    bay_counts=[sum(e.get('new_bay_station')==s and e['id'] in chosen for e in inp['edges']) for s in range(5)]
    if max(bay_counts)>inp['p']['spare_bays']:
        return dict(verified=False,checked_pairs=0,worst='receiving bay count')
    for h,D in enumerate(inp['gross']):
        for failed in range(-1,5):
            out=np.zeros((10,n));inc=np.zeros((10,n));net=np.zeros((10,n));ex=np.zeros((5,n));new_in=np.zeros((5,n));edge_rows={e['id']:np.zeros(n) for e in inp['edges']}
            bounds=[]
            for k,(e,d) in enumerate(arcs):
                a,b=(e['a'],e['b']) if d==0 else (e['b'],e['a'])
                out[a,k]=1;net[a,k]=1;edge_rows[e['id']][k]=1
                if e.get('dedicated'):new_in[b//2,k]=-1
                else:inc[b,k]=1;net[b,k]=-1
                if e['existing']:ex[a//2,k]=1
                bounds.append((0,e['capacity'] if e['existing'] or e['id'] in chosen else 0))
            native=np.repeat(D/2,2);sn=net.reshape(5,2,n).sum(axis=1)+new_in
            available=inp['p']['pf']*ratings.sum(axis=1)
            if failed>=0:available[failed]-=inp['p']['pf']*ratings[failed].max()
            support=modules*inp['storage_effective'];rows=[out,-net,net,ex,sn,-sn]
            rhs=[native,inp['thermal']-native,native,
                 inp['existing_budget'],
                 inp['net'][h]+available+support,available+support-inp['net'][h]]
            if inp['p']['receiver_budget']:
                rows.append(inc);rhs.append(inp['receiver_headroom'])
            for e in inp['edges']:
                rows.append(edge_rows[e['id']][None,:]);rhs.append(np.array([e['capacity']]))
            r=linprog(np.zeros(n),A_ub=np.vstack(rows),b_ub=np.concatenate(rhs),bounds=bounds,method='highs')
            count+=1
            if not r.success:worst=dict(scenario=h,failed=failed,status=int(r.status),message=r.message);break
        if worst:break
    return dict(verified=worst is None,checked_pairs=count,worst=worst)


def solve(parameters):
    start=time.monotonic();inp=make_input(parameters);m,meta=build(inp)
    rr,cc,vv=zip(*m.entries);a=coo_matrix((vv,(rr,cc)),shape=(len(m.constraint_lower),len(m.costs))).tocsr()
    lp=highspy.HighsLp();lp.num_col_,lp.num_row_=a.shape[1],a.shape[0]
    lp.col_cost_,lp.col_lower_,lp.col_upper_=m.costs,m.lower_bounds,m.upper_bounds
    lp.row_lower_,lp.row_upper_=m.constraint_lower,m.constraint_upper
    lp.integrality_=[highspy.HighsVarType.kInteger if x else highspy.HighsVarType.kContinuous for x in m.integrality]
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise;lp.a_matrix_.start_,lp.a_matrix_.index_,lp.a_matrix_.value_=a.indptr,a.indices,a.data
    h=highspy.Highs()
    for k,v in [('threads',1),('random_seed',0),('mip_rel_gap',parameters.get('gap',.001)),
                ('time_limit',parameters.get('seconds',30.)),('log_to_console',False)]:h.setOptionValue(k,v)
    h.passModel(lp);h.run();info=h.getInfo();solution=h.getSolution()
    row=dict(inp['p'],status=h.modelStatusToString(h.getModelStatus()),verified=False,
             elapsed=time.monotonic()-start,peak_mw=inp['peak'],
             cost_lower=float(info.mip_dual_bound) if math.isfinite(info.mip_dual_bound) else None,
             relative_gap=float(info.mip_gap) if math.isfinite(info.mip_gap) else None,
             storage_effective_per_module_mw=inp['storage_effective'],
             template='五站负荷切换审查模板',variables=len(m.costs),constraints=len(m.constraint_lower))
    row.update(initial_transfer_audit=inp['initial_transfer_audit'],
               joint_area_scenarios=inp['joint_area_scenarios'],joint_domain_passed=True,
               initial_network_scale=inp['initial_network_scale'],
               receiver_headroom_mw=inp['receiver_headroom'].tolist(),
               thermal_mw=inp['thermal'].tolist())
    if not solution.value_valid or info.primal_solution_status!=2:return row
    z=np.array(solution.col_value);az=a@z;integer=np.array(m.integrality,dtype=bool)
    violation=max(0.,float(np.max(np.array(m.constraint_lower)-az)),float(np.max(az-np.array(m.constraint_upper))),
                  float(np.max(np.array(m.lower_bounds)-z)),float(np.max(z-np.array(m.upper_bounds))),
                  float(np.max(abs(z[integer]-np.round(z[integer])))))
    assert violation<1e-5,(parameters,violation)
    ratings=np.array([[next(r for r in [50,63,80] if z[meta['units'][s,sl,r]]>.5) for sl in range(2)]
                      +[50*round(z[meta['third'][s]])] for s in range(5)])
    modules=np.array([round(z[meta['modules'][s]]) for s in range(5)])
    chosen={e for e,v in meta['built'].items() if z[v]>.5}
    flows=[(hh,f,e,d,float(z[v])) for hh,f,e,d,v in meta['flows'] if z[v]>1e-7]
    check=check_dispatch(inp,ratings,modules,chosen,flows)
    assert check['violating_pairs']==0,(parameters,check)
    tc=float(np.where(ratings[:,:2]>50,ratings[:,:2],0).sum()*inp['transformer_cost_per_purchased_mva']
             +ratings[:,2].sum()/50*inp['third_cost'])
    raw=dict(transformer=tc,storage=float(modules.sum()*inp['storage_unit_cost']*inp['p']['storage_price']),
             line=len(chosen)*inp['line_cost'])
    costs={k:v*inp['factors'][k] for k,v in raw.items()}
    assert abs(sum(costs.values())-info.objective_function_value)<1e-4
    row.update(verified=True,capacity_mva=float(ratings.sum()),clr=float(ratings.sum()/inp['peak']),
               cost=float(info.objective_function_value),cost_components=costs,units=ratings.tolist(),
               modules=modules.tolist(),storage_mw=float(modules.sum()*.1),
               storage_mwh=float(modules.sum()*.215),storage_effective_mw=float(modules.sum()*inp['storage_effective']),
               line_count=len(chosen),built=sorted(chosen),matrix_violation=violation,
               new_receiving_feeder_count=sum(e.get('dedicated',False) and e['id'] in chosen for e in inp['edges']),
               physical_check=check,flow_sha256=hashlib.sha256(json.dumps(flows).encode()).hexdigest())
    if parameters.get('keep_flows'):row['flows']=flows
    return row
