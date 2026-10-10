"""同期场景与单站最大主变N-1；场景分离后对全年所有单故障复核。

转接仍是站群等效能力模型。每个场景的净转出t可负，sum(t)=0；
t<=min(本站正向负荷,既有MW+新增端数*线路MW)，新增部分共用项目预算。
故障后允许重新安排转接，正常与故障不是同时发生的两个场景。
"""
import argparse
import copy
import json
import math

import numpy as np

from ..annual_no_tie_investment_submodel import LinearModel
from ..pilot_20261009.run import NEW_RATINGS, CASES, PF, solve_model, dump, write_csv, sha
from ..station_transfer_equivalent import pair_equivalent_units
from ..two_district_ordered_guide_run import guide_range
from .prepare import OUT


def transfer_certificate(power, high, reverse, q0, added, budget):
    """等效完全互联站群的充要条件；逐行给出可行性余量与最低新增能力。

    t区间[l,u]，sum(t)=0，sum(max(t-q0,0))<=budget。
    r为q0投影到区间；从r向下调不增加费用，向上调每MW增加1MW新增需求。
    """
    p=np.atleast_2d(power)
    lo=p-high
    hi=np.minimum(np.minimum(p+reverse,np.maximum(p,0)),q0+added)
    r=np.minimum(hi,np.maximum(lo,q0))
    extra=np.maximum(lo-q0,0).sum(axis=1)+np.maximum(-r.sum(axis=1),0)
    margins=np.column_stack(((hi-lo).min(axis=1),-lo.sum(axis=1),hi.sum(axis=1),budget-extra))
    return margins,extra


def transfer_witness(power, high, reverse, q0, added, budget):
    p=np.asarray(power);lo=p-high
    hi=np.minimum(np.minimum(p+reverse,np.maximum(p,0)),q0+added)
    margins,_=transfer_certificate(p,high,reverse,q0,added,budget)
    assert margins.min()>=-1e-5
    t=np.minimum(hi,np.maximum(lo,q0))
    delta=t.sum()
    for j in range(len(t)):
        if delta>0:
            step=min(delta,max(0,t[j]-lo[j]));t[j]-=step;delta-=step
        else:
            step=min(-delta,max(0,hi[j]-t[j]));t[j]+=step;delta+=step
    assert abs(t.sum())<1e-5 and np.maximum(t-q0,0).sum()<=budget+1e-5
    return t


def build(inp, power, selected, case):
    ids=list(inp['stations']);years=inp['years'];g=inp['growth_rate']
    storage=not case.endswith('no_storage');elastic=case.startswith('elastic')
    m=LinearModel();x={};third={};modules={};ends={};projects={};new_projects={};flows={}
    countmax=sum(math.ceil(s['base_forward_mw']*(1+max(g,0))**4/inp['line_increment_mw']) for s in inp['stations'].values())
    ft,fb,fl=({int(k):v for k,v in inp['cost_factors'][name].items()} for name in ('transformer','storage','line'))
    caps={};peaks={y:inp['initial_peak_mw']*(1+g)**(y-2021) for y in years}
    q0=np.array([inp['initial_transfer_fraction']*inp['stations'][sid]['base_forward_mw'] for sid in ids])
    for y in years:
        projects[y]=m.variable(0,upper=countmax)
        new_projects[y]=m.variable(inp['line_capex_10k']*fl[y],upper=countmax,integer=0)
        terms={projects[y]:1,new_projects[y]:-1}
        if y>years[0]:terms[projects[y-1]]=-1
        m.constraint(terms,0,0)
        for sid,s in inp['stations'].items():
            if s['allow_third']:
                third[sid,y]=m.variable(0)
                new=m.variable(inp['third_50mva_capex_10k']*ft[y])
                terms={third[sid,y]:1,new:-1}
                if y>years[0]:terms[third[sid,y-1]]=-1
                m.constraint(terms,0,0)
            max_energy=max(s['base_forward_mw']*max(2.15,s['forward_duration_h']),s['base_reverse_mw']*max(2.15,s['reverse_duration_h']))*(1+g)**(y-2021)
            next_factor=fb[y+1] if y<years[-1] else 0
            modules[sid,y]=m.variable(inp['storage_module_capex_10k']*(fb[y]-next_factor),
                                     upper=math.ceil(max_energy/.215) if storage else 0)
            if y>years[0]:m.constraint({modules[sid,y]:1,modules[sid,y-1]:-1},lower=0)
            for slot,old in enumerate(s['initial_units']):
                ratings=sorted({old,*[r for r in NEW_RATINGS if r>=old]})
                for rating in ratings:
                    key=sid,slot,y,rating
                    x[key]=m.variable(0)
                    purchase=m.variable(rating*inp['transformer_price_10k_per_purchased_mva']*ft[y],integer=0)
                    terms={purchase:1,x[key]:-1}
                    lower=-int(rating==old) if y==years[0] else 0
                    if y>years[0]:terms[x[sid,slot,y-1,rating]]=1
                    m.constraint(terms,lower=lower)
                m.constraint({x[sid,slot,y,r]:1 for r in ratings},1,1)
                if y>years[0]:m.constraint({**{x[sid,slot,y,r]:r for r in ratings},**{x[sid,slot,y-1,r]:-r for r in ratings}},lower=0)
            m.constraint({v:(r if slot==0 else -r) for (ss,slot,yy,r),v in x.items() if ss==sid and yy==y},upper=0)
            cap={v:r for (ss,slot,yy,r),v in x.items() if ss==sid and yy==y}
            if s['allow_third']:cap[third[sid,y]]=50
            caps[sid,y]=cap
            ends[sid,y]=m.variable(0,upper=countmax)
            m.constraint({ends[sid,y]:1,projects[y]:-1},upper=0)
            if y>years[0]:
                terms={ends[sid,y]:1,ends[sid,y-1]:-1}
                m.constraint(terms,lower=0)
                m.constraint({**terms,new_projects[y]:-1},upper=0)
        m.constraint({**{ends[sid,y]:1 for sid in ids},projects[y]:-2},0,0)
        floor=2.001 if elastic else guide_range(inp['growth_rate'])[0]
        m.constraint({v:c for sid in ids for v,c in caps[sid,y].items()},lower=floor*peaks[y],
                     upper=2*peaks[y] if case.startswith('rigid') else inp['physical_capacity_upper_mva'])
        for h,failed in selected:
            p=power[h]*(1+g)**(y-2021)
            big_m=max(1,2*float(np.abs(p).sum())+2*inp['physical_capacity_upper_mva'])
            balance={};budget={projects[y]:-inp['line_increment_mw']}
            for j,sid in enumerate(ids):
                s=inp['stations'][sid]
                t=m.variable(0,upper=max(0,float(p[j])),integer=0);m.lower_bounds[t]=-big_m
                ex=m.variable(0,upper=big_m,integer=0)
                flows[y,h,failed,sid]=t
                balance[t]=1;budget[ex]=1
                m.constraint({t:1,ends[sid,y]:-inp['line_increment_mw']},upper=q0[j])
                m.constraint({t:1,ex:-1},upper=q0[j])
                coeffs=[caps[sid,y]]
                if j==failed:
                    coeffs=[]
                    for slot in range(3 if s['allow_third'] else 2):
                        cap={v:r for (ss,sl,yy,r),v in x.items() if ss==sid and yy==y and sl!=slot}
                        if s['allow_third'] and slot!=2:cap[third[sid,y]]=50
                        coeffs.append(cap)
                for slot,cap in enumerate(coeffs):
                    for sign,duration in ((1,s['forward_duration_h']),(-1,s['reverse_duration_h'])):
                        terms={v:PF*c for v,c in cap.items()}
                        terms.update({modules[sid,y]:.215/max(2.15,duration),t:sign})
                        rhs=sign*float(p[j])
                        if j==failed and slot==2:
                            terms[third[sid,y]]=-big_m;rhs-=big_m
                        m.constraint(terms,lower=rhs)
            m.constraint(balance,0,0);m.constraint(budget,upper=0)
    return m,dict(x=x,third=third,modules=modules,ends=ends,projects=projects,new_projects=new_projects,peaks=peaks,flows=flows)


def assets(inp,z,meta,y):
    ids=list(inp['stations'])
    units=np.array([[next(r for (ss,sl,yy,r),v in meta['x'].items() if ss==sid and sl==slot and yy==y and z[v]>.5) for slot in (0,1)]
                    +[50*round(z[meta['third'][sid,y]]) if (sid,y) in meta['third'] else 0] for sid in ids])
    n=np.array([round(z[meta['modules'][sid,y]]) for sid in ids])
    ends=np.array([round(z[meta['ends'][sid,y]]) for sid in ids])
    return units,n,ends,round(z[meta['projects'][y]])


def check_year(inp,power,units,n,ends,projects):
    ids=list(inp['stations']);cap=PF*units.sum(axis=1);survive=PF*(units.sum(axis=1)-units.max(axis=1))
    bp=np.array([.215/max(2.15,inp['stations'][sid]['forward_duration_h']) for sid in ids])*n
    bn=np.array([.215/max(2.15,inp['stations'][sid]['reverse_duration_h']) for sid in ids])*n
    q0=np.array([inp['initial_transfer_fraction']*inp['stations'][sid]['base_forward_mw'] for sid in ids])
    violations=[];worst=None;min_margin=np.inf
    for failed in range(-1,len(ids)):
        available=cap.copy()
        if failed>=0:available[failed]=survive[failed]
        margins,extra=transfer_certificate(power,available+bp,available+bn,q0,ends*inp['line_increment_mw'],projects*inp['line_increment_mw'])
        h,kind=np.unravel_index(np.argmin(margins),margins.shape)
        if margins[h,kind]<min_margin:
            min_margin=float(margins[h,kind]);worst=(int(h),failed,int(kind))
        # 每个故障、每类瓶颈最差时刻；避免只选一种约束，迭代才能覆盖全年。
        for kind in range(4):
            h=int(np.argmin(margins[:,kind]))
            if margins[h,kind]<-1e-5:violations.append((float(-margins[h,kind]),h,failed))
    return min_margin,worst,violations


def baseline_check(inp,power):
    units=np.array([s['initial_units']+[0] for s in inp['stations'].values()])
    margin,worst,violations=check_year(inp,power,units,np.zeros(len(units)),np.zeros(len(units)),0)
    return {'feasible':margin>=-1e-5,'worst_margin_mw':margin,'worst_hour_index':worst[0],
            'worst_failed_station_index':worst[1],'constraint_kind':worst[2],
            'meaning':'同一基期资产，无新增措施，8760小时正常及单主变N-1等效能力核查；负余量为约束违反程度，非失负荷预测。'}


def extract(inp,power,hours,case,z,meta,solver,history):
    ids=list(inp['stations']);station_rows=[];annual=[];pair_rows=[];checks=[];witness_rows=[]
    old_units=np.array([s['initial_units']+[0] for s in inp['stations'].values()])
    old_n=np.zeros(len(ids));old_ends=np.zeros(len(ids));old_projects=0
    total_cost=0
    for y in inp['years']:
        units,n,ends,projects=assets(inp,z,meta,y)
        p=power*(1+inp['growth_rate'])**(y-2021)
        margin,worst,violations=check_year(inp,p,units,n,ends,projects)
        assert margin>=-1e-5
        checks.append({'year':y,'checked_hour_contingency_pairs':len(p)*(len(ids)+1),'min_feasibility_margin_mw':margin,
                       'worst_hour':str(hours[worst[0]]),'worst_failed_station':ids[worst[1]] if worst[1]>=0 else 'normal','constraint_kind':worst[2]})
        replacements=np.where(units[:,:2]>old_units[:,:2]+1e-6,units[:,:2],0).sum(axis=1)
        new_third=(units[:,2]-old_units[:,2])/50
        tcost=replacements*inp['transformer_price_10k_per_purchased_mva']+new_third*inp['third_50mva_capex_10k']
        bcost=(n-old_n)*inp['storage_module_capex_10k'];lcost=(projects-old_projects)*inp['line_capex_10k']
        components={k:v*inp['cost_factors'][k][str(y)] for k,v in [('transformer',tcost.sum()),('storage',bcost.sum()),('line',lcost)]}
        npv=sum(components.values());total_cost+=npv
        increments={sid:int(ends[j]-old_ends[j]) for j,sid in enumerate(ids)}
        pairs=pair_equivalent_units(increments);assert len(pairs)==projects-old_projects
        pair_rows.extend({'year':y,'station_a':a,'station_b':b,'equivalent_capacity_mw':inp['line_increment_mw'],'status':'计数配对，非物理路线'} for a,b in pairs)
        for j,sid in enumerate(ids):
            station_rows.append({'case':case,'year':y,'station':sid,'unit_1_mva':units[j,0],'unit_2_mva':units[j,1],
                'unit_3_mva':units[j,2],'capacity_mva':units[j].sum(),'new_purchased_mva':replacements[j]+50*new_third[j],
                'new_third_count':int(new_third[j]),'storage_modules':int(n[j]),'storage_nameplate_mw':.1*n[j],
                'storage_mwh':.215*n[j],'new_storage_mwh':.215*(n[j]-old_n[j]),
                'fixed_existing_transfer_mw':inp['initial_transfer_fraction']*inp['stations'][sid]['base_forward_mw'],
                'new_line_ends':int(ends[j]),'transformer_capex_10k':tcost[j],'storage_capex_10k':bcost[j]})
        annual.append({'case':case,'year':y,'planning_year':y-2021,'peak_mw':meta['peaks'][y],
            'capacity_mva':units.sum(),'clr':units.sum()/meta['peaks'][y],
            'purchased_transformer_mva':replacements.sum()+50*new_third.sum(),'new_third_count':int(new_third.sum()),
            'new_lines':projects-old_projects,'cumulative_lines':projects,
            'storage_nameplate_mw':.1*n.sum(),'storage_mwh':.215*n.sum(),'new_storage_mwh':.215*(n-old_n).sum(),
            'transformer_capex_10k':tcost.sum(),'storage_capex_10k':bcost.sum(),'line_capex_10k':lcost,
            'construction_capex_10k':tcost.sum()+bcost.sum()+lcost,'added_lifecycle_npv_10k':npv,
            'cumulative_lifecycle_npv_10k':total_cost,**{k+'_npv_10k':v for k,v in components.items()}})
        # 保存区县峰值时刻全部故障的可行流量证据，无需保存上百万行全年调度。
        h=int(np.argmax(p.sum(axis=1)));q0=np.array([r['fixed_existing_transfer_mw'] for r in station_rows if r['year']==y])
        bp=np.array([.215/max(2.15,s['forward_duration_h']) for s in inp['stations'].values()])*n
        bn=np.array([.215/max(2.15,s['reverse_duration_h']) for s in inp['stations'].values()])*n
        for failed in range(-1,len(ids)):
            cap=PF*units.sum(axis=1)
            if failed>=0:cap[failed]-=PF*units[failed].max()
            t=transfer_witness(p[h],cap+bp,cap+bn,q0,ends*inp['line_increment_mw'],projects*inp['line_increment_mw'])
            for j,sid in enumerate(ids):
                witness_rows.append({'year':y,'hour':str(hours[h]),'failed_station':ids[failed] if failed>=0 else 'normal',
                     'station':sid,'original_mw':p[h,j],'net_transfer_out_mw':t[j],'post_transfer_mw':p[h,j]-t[j],
                     'forward_margin_mw':cap[j]+bp[j]-p[h,j]+t[j],'reverse_margin_mw':cap[j]+bn[j]+p[h,j]-t[j]})
        old_units,old_n,old_ends,old_projects=units,n,ends,projects
    assert abs(total_cost-solver['objective'])<.01
    if case.endswith('no_storage'):assert all(r['storage_mwh']==0 for r in annual)
    summary={'case':case,'region':inp['region'],'cost_npv_10k':total_cost,'annual':annual,'solver':solver,
             'scenario_iterations':history,'full_hour_checks':checks,'cost_recomputation_error_10k':abs(total_cost-solver['objective']),
             'scope':'全部8760小时及每站最大单台主变故障的静态等效能力可行；不含SOC时序及真实线路拓扑'}
    return summary,station_rows,pair_rows,witness_rows


def run(region,case,seconds=600,zero_growth=False):
    root=OUT/region;inp=json.loads((root/'inputs.json').read_text())
    if zero_growth:inp['growth_rate']=0
    data=np.load(root/'hourly.npz');power=data['power_base_mw'];hours=data['hours']
    assert list(data['station_ids'])==list(inp['stations'])
    directory=root/(case+('_zero_growth' if zero_growth else ''));directory.mkdir(exist_ok=True)
    dump(directory/'effective_inputs.json',inp)
    dump(root/'基期可行性.json',baseline_check(inp,power))
    selected={(int(np.argmax(power.sum(axis=1))),-1),(int(np.argmin(power.sum(axis=1))),-1)}
    for j in range(power.shape[1]):
        selected.add((int(np.argmax(power[:,j])),j));selected.add((int(np.argmin(power[:,j])),j))
    history=[]
    for iteration in range(1,31):
        model,meta=build(inp,power,sorted(selected),case)
        z,result=solve_model(model,directory,f'iteration_{iteration:02}',seconds,.01)
        history.append({'iteration':iteration,'selected_scenarios':len(selected),'solver':result})
        if not result['accepted']:
            dump(directory/'summary.json',{'case':case,'region':region,'solver':result,'scenario_iterations':history});return
        violations=[]
        for y in inp['years']:
            a=assets(inp,z,meta,y)
            margin,worst,v=check_year(inp,power*(1+inp['growth_rate'])**(y-2021),*a)
            violations.extend(v)
        history[-1]['violating_pairs']=len(set((h,f) for _,h,f in violations))
        history[-1]['max_full_hour_violation_mw']=max((v for v,_,_ in violations),default=0)
        print(region,case,iteration,'CHECK',history[-1]['violating_pairs'],history[-1]['max_full_hour_violation_mw'],flush=True)
        if not violations:
            summary,station,pairs,witness=extract(inp,power,hours,case,z,meta,result,history)
            summary.update(zero_growth=zero_growth,input_sha256=sha(directory/'effective_inputs.json'),hourly_sha256=sha(root/'hourly.npz'))
            dump(directory/'summary.json',summary);write_csv(directory/'years.csv',summary['annual'])
            write_csv(directory/'stations.csv',station);write_csv(directory/'line_pairs.csv',pairs)
            write_csv(directory/'peak_hour_contingency_dispatch.csv',witness)
            write_csv(directory/'selected_scenarios.csv',[{'hour_index':h,'hour':str(hours[h]),'failed_station':list(inp['stations'])[f] if f>=0 else 'normal'} for h,f in sorted(selected)])
            print('COMPLETE',region,case,'zero_growth',zero_growth,'cost',summary['cost_npv_10k'],flush=True);return
        added={(h,f) for _,h,f in sorted(violations,reverse=True)[:60]}-selected
        assert added,'场景仍违反但已在主模型中，须检查分离器一致性'
        selected.update(added)
    raise RuntimeError('场景分离未收敛，不输出已通过全年复核的结论')


if __name__=='__main__':
    raise SystemExit('该历史独立入口已归档；请使用 实验.研究.rebuild_2026.static_actual_20261010。公共函数仍保留供现行模型导入。')
    p=argparse.ArgumentParser();p.add_argument('region',choices=['city','pizhou']);p.add_argument('case',choices=(*CASES,'economic_storage','economic_no_storage'))
    p.add_argument('--seconds',type=int,default=600);p.add_argument('--zero-growth',action='store_true')
    a=p.parse_args();run(a.region,a.case,a.seconds,a.zero_growth)
