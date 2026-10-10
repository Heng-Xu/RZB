"""固定已选资产，独立检查24h充放电及峰值2h单台N-1恢复。

这是计划性预充条件下的典型日筛查；不代替全年SOC与随机故障储备。
允许10%—90%SOC，双向效率均95%，每天末SOC恢复到初始SOC。
若LP发生同时充放电，该条不判为通过，避免靠损耗消纳反送的伪可行。
"""
import argparse
import json
import numpy as np
import highspy
from scipy.sparse import coo_matrix

from ..annual_no_tie_investment_submodel import LinearModel
from ..pilot_20261009.run import PF,dump,write_csv
from .run import case_root,network_arcs


def check_day(inp,power,units,n,built,y,peak_index,failed):
    day=peak_index//24;start=24*day;N=len(units);pday=power[start:start+24]
    duration=int(next(iter(inp['stations'].values()))['forward_duration_h'])
    window_start=min(max(peak_index%24-duration//2,0),24-duration)
    outage=set(range(window_start,window_start+duration)) if failed>=0 else set()
    m=LinearModel();soc={};charge={};discharge={};slacks=[]
    for j in range(N):
        energy=.215*n[j];rating=.1*n[j]
        for h in range(25):
            soc[j,h]=m.variable(0,upper=.9*energy,integer=0);m.lower_bounds[soc[j,h]]=.1*energy
        m.constraint({soc[j,0]:1,soc[j,24]:-1},0,0)
        for h in range(24):
            charge[j,h]=m.variable(1e-7,upper=rating,integer=0)
            discharge[j,h]=m.variable(1e-7,upper=rating,integer=0)
            m.constraint({soc[j,h+1]:1,soc[j,h]:-1,charge[j,h]:-.95,discharge[j,h]:1/.95},0,0)
    for h,p in enumerate(pday):
        nodes,arcs=network_arcs(inp,p,y,built)
        balance=[{} for _ in range(nodes)]
        for a,b,cap in arcs:
            v=m.variable(0,upper=cap,integer=0);balance[a][v]=1;balance[b][v]=-1
        for j in range(nodes):
            if j>=N:m.constraint(balance[j],0,0);continue
            cap=PF*units[j].sum()
            if j==failed and h in outage:cap-=PF*units[j].max()
            # net out + discharge - charge reduces forward transformer loading.
            balance[j][discharge[j,h]]=1;balance[j][charge[j,h]]=-1
            sp=m.variable(1,upper=np.inf,integer=0);sn=m.variable(1,upper=np.inf,integer=0);slacks.extend([sp,sn])
            m.constraint({**balance[j],sp:1},lower=float(p[j]-cap))
            m.constraint({**balance[j],sn:-1},upper=float(p[j]+cap))
    rr,cc,vv=zip(*m.entries);a=coo_matrix((vv,(rr,cc)),shape=(len(m.constraint_lower),len(m.costs))).tocsr()
    lp=highspy.HighsLp();lp.num_col_,lp.num_row_=a.shape[1],a.shape[0]
    lp.col_cost_,lp.col_lower_,lp.col_upper_=m.costs,m.lower_bounds,m.upper_bounds
    lp.row_lower_,lp.row_upper_=m.constraint_lower,m.constraint_upper
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_,lp.a_matrix_.index_,lp.a_matrix_.value_=a.indptr,a.indices,a.data
    solver=highspy.Highs();solver.setOptionValue('threads',1);solver.setOptionValue('output_flag',False);solver.passModel(lp);solver.run()
    assert solver.getModelStatus()==highspy.HighsModelStatus.kOptimal
    z=np.asarray(solver.getSolution().col_value)
    overlap=max(min(z[charge[j,h]],z[discharge[j,h]]) for j in range(N) for h in range(24))
    if overlap>1e-5:
        # 仅有同时充放电的LP解才补互斥整数模式，避免用充放电损耗虚增吸纳。
        for j in range(N):
            if n[j]==0:continue
            for h in range(24):
                mode=m.variable(0);rating=.1*n[j]
                m.constraint({charge[j,h]:1,mode:-rating},upper=0)
                m.constraint({discharge[j,h]:1,mode:rating},upper=rating)
        rr,cc,vv=zip(*m.entries);a=coo_matrix((vv,(rr,cc)),shape=(len(m.constraint_lower),len(m.costs))).tocsr()
        lp.num_col_,lp.num_row_=a.shape[1],a.shape[0]
        lp.col_cost_,lp.col_lower_,lp.col_upper_=m.costs,m.lower_bounds,m.upper_bounds
        lp.row_lower_,lp.row_upper_=m.constraint_lower,m.constraint_upper
        lp.integrality_=[highspy.HighsVarType.kInteger if v else highspy.HighsVarType.kContinuous for v in m.integrality]
        lp.a_matrix_.start_,lp.a_matrix_.index_,lp.a_matrix_.value_=a.indptr,a.indices,a.data
        solver.clearModel();solver.passModel(lp);solver.run()
        assert solver.getModelStatus()==highspy.HighsModelStatus.kOptimal
        z=np.asarray(solver.getSolution().col_value)
        overlap=max(min(z[charge[j,h]],z[discharge[j,h]]) for j in range(N) for h in range(24))
    unmet=float(z[slacks].sum());maxslack=float(z[slacks].max())
    return {'year':y,'day_index':day,'peak_hour_index':peak_index,'failed_station':list(inp['stations'])[failed] if failed>=0 else 'normal',
            'fault_duration_h':len(outage),'unserved_or_unabsorbed_energy_proxy_mwh':unmet,
            'maximum_power_slack_mw':maxslack,'maximum_simultaneous_charge_discharge_mw':float(overlap),
            'passes_screen':bool(unmet<1e-5 and overlap<1e-5)}


def run(case,usable=1.):
    root=case_root(4,True,usable);inp=json.loads((root/'inputs.json').read_text());directory=root/case
    summary=json.loads((directory/'summary.json').read_text())
    if 'annual' not in summary:return
    import csv
    stations=list(csv.DictReader((directory/'stations.csv').open(encoding='utf-8-sig')))
    projects=list(csv.DictReader((directory/'projects.csv').open(encoding='utf-8-sig')))
    base=np.load(root/'hourly.npz')['power_base_mw'];ids=list(inp['stations']);results=[]
    for y in inp['years']:
        rows={r['station']:r for r in stations if int(r['year'])==y}
        units=np.array([[float(rows[s][f'unit_{j}_mva']) for j in (1,2,3)] for s in ids])
        n=np.array([int(rows[s]['storage_modules']) for s in ids]);p=base*(1+inp['growth_rate'])**(y-2021)
        built={r['id'] for r in projects if int(r['year'])<=y}
        cases={(int(np.argmax(p.sum(axis=1))),-1),(int(np.argmin(p.sum(axis=1))),-1)}
        for j in range(len(ids)):
            cases.add((int(np.argmax(p[:,j])),j));cases.add((int(np.argmin(p[:,j])),j))
        for h,f in sorted(cases):results.append(check_day(inp,p,units,n,built,y,h,f))
        print('SOC',case,y,'checks',len(cases),'failures',sum(not r['passes_screen'] for r in results if r['year']==y),flush=True)
    write_csv(directory/'SOC典型日复核.csv',results)
    dump(directory/'SOC复核摘要.json',{'case':case,'checks':len(results),'passed':sum(r['passes_screen'] for r in results),
                                    'failed':sum(not r['passes_screen'] for r in results),
                                    'worst_power_slack_mw':max(r['maximum_power_slack_mw'] for r in results),
                                    'scope':'24h循环SOC，10%—90%，充放电效率各95%；区县正反峰正常日与各站正反峰时段2h故障；允许预知故障、日内预充；非全年连续SOC'})


if __name__=='__main__':
    raise SystemExit('该历史独立入口已归档；请使用 实验.研究.rebuild_2026.static_actual_20261010。公共函数仍保留供现行模型导入。')
    p=argparse.ArgumentParser();p.add_argument('case');p.add_argument('--usable',type=float,default=1.);a=p.parse_args();run(a.case,a.usable)
