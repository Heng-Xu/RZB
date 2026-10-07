"""以两类等容量站群进行通用参数外推，逐点整数优化并汇总区间。

五站模板为研究假定，不保留徐州具体站号与规模。推荐为第4年规划值。
"""
import csv,json,sys,itertools,math,time
from pathlib import Path
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import coo_matrix
from openpyxl import Workbook
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from 实验.研究.rebuild_2026.current_economic_assumptions import cost_factors,line_capex,LINE_TYPES
OUT=ROOT/'研究报告/01研究推荐/当前版';OUT.mkdir(parents=True,exist_ok=True)
BASE_T=16.57333333333333;BASE_B=21.0456262;INC=7.49106117
DETAILS=[]
def factor(life,om):
    return 1/1.06**4+sum(om/1.06**t for t in range(5,21))+sum(1/1.06**t for t in range(4+life,20,life))
CURRENT_FACTORS=cost_factors()
FT,FL,FB=(CURRENT_FACTORS[k][2025] for k in ('transformer','line','storage'))
def solve(eta,g,h,area,ls,bs,shape='偏集中',line_type='架空为主',upper=2.6,relative_gap=1e-8,lower=0.0):
    base=50 if area=='A' else 40
    p0=5*base;p=p0*(1+g)**4
    weights=np.array([.10,.15,.20,.25,.30]) if shape=='偏集中' else np.array([.16,.18,.20,.22,.24])
    pvweights=np.array([.08,.14,.18,.25,.35])
    peak_sum_factor=1.15 if shape=='偏集中' else 1.0
    load=p*weights*peak_sum_factor;reverse=np.maximum(0,.75*eta*p*pvweights-.3*load)
    rho=0.0;ceiling=.7 if area=='A' else .5
    options=[]
    for a,b in itertools.combinations_with_replacement([base,50,63] if base==40 else [50,63],2):
        for third in (0,50):
            purchased=sum(v for v in (a,b) if v>base)
            options.append((a+b+third,a+b+third-max(a,b,third),purchased,third,purchased*BASE_T+(1223 if third else 0)))
    costs=[];lo=[];hi=[];integ=[];entries=[];lb=[];ub=[]
    def var(c=0,u=np.inf,integer=0):
        k=len(costs);costs.append(c);lo.append(0);hi.append(u);integ.append(integer);return k
    def constraint(d,l=-np.inf,u=np.inf):
        r=len(lb);lb.append(l);ub.append(u);entries.extend((r,k,v) for k,v in d.items())
    x={};n={};qo={};qi={};ends={};ex={}
    line_price=line_capex(LINE_TYPES[line_type])
    project=var(line_price*ls*FL,30,1)
    for i in range(5):
        for j,o in enumerate(options):x[i,j]=var(o[4]*FT,1,1)
        n[i]=var(BASE_B*bs*FB,20000,1)
        qo[i]=var();qi[i]=var();ends[i]=var(0,30,1);ex[i]=var()
        constraint({x[i,j]:1 for j in range(len(options))},1,1)
        constraint({qo[i]:1},u=ceiling*load[i])
        constraint({qo[i]:1,ends[i]:-INC},u=rho*load[i])
        constraint({qo[i]:1,ex[i]:-1},u=rho*load[i])
        constraint({ends[i]:1,project:-1},u=0)
        for kind in ('forward','reverse'):
            d={x[i,j]:.95*o[1 if kind=='n1' else 0] for j,o in enumerate(options)}
            d[n[i]]=.215/max(2.15,h)
            if kind=='reverse':d[qo[i]]=-1;demand=reverse[i]
            else:d[qo[i]]=1;d[qi[i]]=-1;demand=load[i]
            constraint(d,l=demand)
    constraint({**{qo[i]:1 for i in range(5)},**{qi[i]:-1 for i in range(5)}},0,0)
    constraint({**{ends[i]:1 for i in range(5)},project:-2},0,0)
    constraint({**{ex[i]:1 for i in range(5)},project:-INC},u=0)
    pairs=list(itertools.combinations(range(5),2))
    built={pair:var(0,30,1) for pair in pairs}
    constraint({**{v:1 for v in built.values()},project:-1},0,0)
    for i in range(5):
        constraint({**{v:1 for pair,v in built.items() if i in pair},ends[i]:-1},0,0)
    old_normal={};new_normal={}
    for i,j in itertools.permutations(range(5),2):
        old_normal[i,j]=var();new_normal[i,j]=var()
    for i in range(5):
        outgoing={v:1 for flows in (old_normal,new_normal) for (a,b),v in flows.items() if a==i}
        incoming={v:1 for flows in (old_normal,new_normal) for (a,b),v in flows.items() if b==i}
        constraint({**outgoing,qo[i]:-1},0,0)
        constraint({**incoming,qi[i]:-1},0,0)
    contingency={};cont_ex={};new_cont={}

    for k in range(5):
        for j in range(5):
            if j!=k:
                contingency[k,j]=var();new_cont[k,j]=var()
                constraint({new_cont[k,j]:1,contingency[k,j]:-1},u=0)
                constraint({new_cont[k,j]:1,built[tuple(sorted((k,j)))]:-INC},u=0)
        # One transformer is out at station k; healthy receivers keep all units.
        d={x[k,j]:.95*o[1] for j,o in enumerate(options)}
        d.update({n[k]:.215/max(2.15,h),qo[k]:1,qi[k]:-1})
        d.update({contingency[k,j]:1 for j in range(5) if j!=k})
        constraint(d,l=load[k])
        for i in range(5):
            delta={contingency[k,j]:1 for j in range(5) if j!=k} if i==k else {contingency[k,i]:1}
            newdelta={new_cont[k,j]:-1 for j in range(5) if j!=k} if i==k else {new_cont[k,i]:-1}
            existing={v:1 for pair,v in old_normal.items() if i in pair}
            constraint({**existing,**delta,**newdelta},u=rho*load[i])
            # Normal transfer and contingency transfer share installed endpoint capacity.
            movement={qo[i]:1,qi[i]:1,**delta}
            constraint(movement,u=ceiling*load[i])
            constraint({**movement,ends[i]:-INC},u=rho*load[i])
            if i!=k:
                d={x[i,j]:.95*o[0] for j,o in enumerate(options)}
                d.update({n[i]:.215/max(2.15,h),qo[i]:1,qi[i]:-1,contingency[k,i]:-1})
                constraint(d,l=load[i])
            cont_ex[k,i]=var()
            constraint({**movement,cont_ex[k,i]:-1},u=rho*load[i])
        for pair,units in built.items():
            a,b=pair
            usage={new_normal[a,b]:1,new_normal[b,a]:1,units:-INC}
            if k in pair:usage[new_cont[k,b if k==a else a]]=1
            constraint(usage,u=0)
        # Count both source and receiver ends; each new project provides two ends.
        constraint({**{cont_ex[k,i]:1 for i in range(5)},project:-2*INC},u=0)
    floor=1.5 if g<=.02 else 1.6 if g<=.04 else 1.7 if g<=.07 else 1.8
    capacity={x[i,j]:o[0] for i in range(5) for j,o in enumerate(options)}
    if not 0 <= lower <= upper:
        raise ValueError('容载比搜索下限须在0至上限之间')
    constraint(capacity,l=max(lower,floor)*p,u=upper*p)
    rr,cc,vv=zip(*entries);a=coo_matrix((vv,(rr,cc)),shape=(len(lb),len(costs))).tocsc()
    result=milp(np.array(costs),integrality=np.array(integ),bounds=Bounds(lo,hi),constraints=LinearConstraint(a,lb,ub),options={'time_limit':60,'mip_rel_gap':relative_gap})
    if result.status!=0:raise ValueError((eta,g,h,area,ls,bs,shape,result.message))
    z=result.x;activity=a@z
    assert min(activity-np.array(lb))>=-1e-4 and min(np.array(ub)-activity)>=-1e-4
    assert max(abs(z[np.array(integ)==1]-np.round(z[np.array(integ)==1])))<1e-5
    s=sum(c*z[k] for k,c in capacity.items());qout=sum(z[qo[i]] for i in range(5));qin=sum(z[qi[i]] for i in range(5))
    assert abs(qout-qin)<1e-4
    DETAILS.append({'参数':[eta,g,h,area,ls,bs,shape,line_type], '线路基价万元':line_price,'目标负荷MW':p,'项目数':round(z[project]),'站级':[{'原单台MVA':base,'规格MVA':list(options[max(range(len(options)),key=lambda j:z[x[i,j]])][:4]),'负荷MW':float(load[i]),'反向MW':float(reverse[i]),'储能柜':round(z[n[i]]),'转出MW':float(z[qo[i]]),'转入MW':float(z[qi[i]]),'项目端数':round(z[ends[i]]),'新增使用MW':float(z[ex[i]])} for i in range(5)]})
    DETAILS[-1]['新增联络站对']=[{'起点':i,'终点':j,'项目数':round(z[v])} for (i,j),v in built.items() if z[v]>.5]
    DETAILS[-1]['正常转接路径']=[{'起点':i,'终点':j,'既有MW':float(z[old_normal[i,j]]),'新增MW':float(z[new_normal[i,j]])} for i,j in old_normal if z[old_normal[i,j]]+z[new_normal[i,j]]>1e-8]
    DETAILS[-1]['单台主变停运转供']=[{'停运站':k,'承接站':j,'总转供MW':float(z[v]),'新增线路转供MW':float(z[new_cont[k,j]])} for (k,j),v in contingency.items()]
    DETAILS[-1]['校核方式']='各站最大单台主变分别停运；健康站保留全部主变；正常与事故转供共用已建线路容量'
    return {'装机渗透率':eta,'电量渗透率估计':eta*1200/(8760*.5),'年负荷平均增长率':g,'95%峰值持续时间h':h,'供电区域':area,'初始转供率':rho,'负荷分布':shape,'线路类型':line_type,'电缆长度占比':LINE_TYPES[line_type],'线路价格倍数':ls,'储能价格倍数':bs,'主变线路成本比':(BASE_T/.95)/(line_price*ls/INC),'主变储能成本比_3h':(BASE_T/.95)/(BASE_B*bs/.215*3),'基期容载比':2.,'推荐容载比':s/p,'总容量MVA':s,'储能柜数':round(sum(z[n[i]] for i in range(5))),'联络项目数':round(z[project]),'转接负荷MW':qout,'全寿命费用万元':result.fun,'最优性间隙':result.mip_gap,'最小约束余量':min(float(np.min(activity-np.array(lb))),float(np.min(np.array(ub)-activity))),'状态':'通过'}

def solve_case(case):
    eta,g,h,area,(ls,bs),shape,line_type=case
    DETAILS.clear()
    row=solve(eta,g,h,area,ls,bs,shape,line_type)
    return row,DETAILS[-1]
def main():
    import argparse
    parser=argparse.ArgumentParser(description='计算七维完整参数组合；可指定独立输出目录。')
    parser.add_argument('--output',type=Path,default=OUT)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    rows=[];details=[];start=time.time()
    prices=list(itertools.product([.75,1,1.25],[.5,1,1.25]))
    cases=list(itertools.product([0,.3,.8,1,1.3,1.8,2,2.3,2.8,3],[0,.01,.02,.04,.07,.08,.1],[1,2,3,4,6],['A','BC'],prices,['偏集中','较均匀'],LINE_TYPES))
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=4) as executor:
        for k,(row,detail) in enumerate(executor.map(solve_case,cases,chunksize=20)):
            rows.append(row);details.append(detail)
            if k%1000==0:print(json.dumps({'完成':k+1,'总数':len(cases)},ensure_ascii=False),flush=True)
    (args.output/'外推逐点结果.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    (args.output/'外推站级方案.jsonl').write_text('\n'.join(json.dumps(d,ensure_ascii=False) for d in details)+'\n')
    with (args.output/'外推逐点结果.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    summary={'总组合':len(rows),'线路类型':LINE_TYPES,'价格组合':[list(x) for x in prices],'模型版本':'1008新增联络专项外推','既有联络剩余可用容量MW':0.0,'场景性质':'既有联络无剩余可用能力；新增转供需计建设费用','经济参数':CURRENT_FACTORS,'求解精度':1e-8,'最大最优性间隙':max(x['最优性间隙'] for x in rows),'全部约束核对':'通过','耗时秒':time.time()-start}
    (args.output/'外推核验.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':main()
