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
OUT=ROOT/'研究报告/01研究推荐/2026-10-01甲方修订';OUT.mkdir(parents=True,exist_ok=True)
BASE_T=16.57333333333333;BASE_B=21.0456262;INC=7.49106117
DETAILS=[]
def factor(life,om):
    return 1/1.06**4+sum(om/1.06**t for t in range(5,21))+sum(1/1.06**t for t in range(4+life,20,life))
FT,FB=factor(20,.01),factor(10,.03)
def solve(eta,g,h,area,ls,bs,shape='偏集中'):
    base=50 if area=='A' else 40
    p0=5*base;p=p0*(1+g)**4
    weights=np.array([.10,.15,.20,.25,.30]) if shape=='偏集中' else np.array([.16,.18,.20,.22,.24])
    pvweights=np.array([.08,.14,.18,.25,.35])
    peak_sum_factor=1.15 if shape=='偏集中' else 1.0
    load=p*weights*peak_sum_factor;reverse=np.maximum(0,.75*eta*p*pvweights-.3*load)
    rho=.5 if area=='A' else .28287889;ceiling=.7 if area=='A' else .5
    target=.5 if area=='A' else .3
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
    project=var(106.8*ls*FT,30,1)
    for i in range(5):
        for j,o in enumerate(options):x[i,j]=var(o[4]*FT,1,1)
        n[i]=var(BASE_B*bs*FB,20000,1)
        qo[i]=var();qi[i]=var();ends[i]=var(0,30,1);ex[i]=var()
        constraint({x[i,j]:1 for j in range(len(options))},1,1)
        constraint({qo[i]:1},u=ceiling*load[i])
        constraint({qo[i]:1,ends[i]:-INC},u=rho*load[i])
        constraint({qo[i]:1,ex[i]:-1},u=rho*load[i])
        constraint({ends[i]:1,project:-1},u=0)
        constraint({ends[i]:1},l=max(0,math.ceil((target-rho)*load[i]/INC-1e-12)))
        for kind in ('forward','n1','reverse'):
            d={x[i,j]:.95*o[1 if kind=='n1' else 0] for j,o in enumerate(options)}
            d[n[i]]=.215/max(2.15,h)
            if kind=='reverse':d[qo[i]]=-1;demand=reverse[i]
            else:d[qo[i]]=1;d[qi[i]]=-1;demand=load[i]
            constraint(d,l=demand)
    constraint({**{qo[i]:1 for i in range(5)},**{qi[i]:-1 for i in range(5)}},0,0)
    constraint({**{ends[i]:1 for i in range(5)},project:-2},0,0)
    constraint({**{ex[i]:1 for i in range(5)},project:-INC},u=0)
    floor=1.5 if g<=.02 else 1.6 if g<=.04 else 1.7 if g<=.07 else 1.8
    capacity={x[i,j]:o[0] for i in range(5) for j,o in enumerate(options)}
    constraint(capacity,l=max(2.001,floor)*p,u=2.6*p)
    rr,cc,vv=zip(*entries);a=coo_matrix((vv,(rr,cc)),shape=(len(lb),len(costs))).tocsc()
    result=milp(np.array(costs),integrality=np.array(integ),bounds=Bounds(lo,hi),constraints=LinearConstraint(a,lb,ub),options={'time_limit':20,'mip_rel_gap':.005})
    if result.status!=0:raise ValueError((eta,g,h,area,ls,bs,shape,result.message))
    z=result.x;activity=a@z
    assert min(activity-np.array(lb))>=-1e-4 and min(np.array(ub)-activity)>=-1e-4
    assert max(abs(z[np.array(integ)==1]-np.round(z[np.array(integ)==1])))<1e-5
    s=sum(c*z[k] for k,c in capacity.items());qout=sum(z[qo[i]] for i in range(5));qin=sum(z[qi[i]] for i in range(5))
    assert abs(qout-qin)<1e-4
    DETAILS.append({'参数':[eta,g,h,area,ls,bs,shape], '目标负荷MW':p,'项目数':round(z[project]),'站级':[{'原单台MVA':base,'规格MVA':list(options[max(range(len(options)),key=lambda j:z[x[i,j]])][:4]),'负荷MW':float(load[i]),'反向MW':float(reverse[i]),'储能柜':round(z[n[i]]),'转出MW':float(z[qo[i]]),'转入MW':float(z[qi[i]]),'项目端数':round(z[ends[i]]),'新增使用MW':float(z[ex[i]])} for i in range(5)]})
    return {'装机渗透率':eta,'电量渗透率估计':eta*1200/(8760*.5),'年负荷平均增长率':g,'95%峰值持续时间h':h,'供电区域':area,'初始转供率':rho,'负荷分布':shape,'线路价格倍数':ls,'储能价格倍数':bs,'主变线路成本比':1.22364/ls,'主变储能成本比_3h':.05941/bs,'基期容载比':2.,'推荐容载比':s/p,'总容量MVA':s,'储能柜数':round(sum(z[n[i]] for i in range(5))),'联络项目数':round(z[project]),'转接负荷MW':qout,'全寿命费用万元':result.fun,'最优性间隙':result.mip_gap,'最小约束余量':min(float(np.min(activity-np.array(lb))),float(np.min(np.array(ub)-activity))),'状态':'通过'}
def main():
    rows=[];start=time.time()
    # 每档装机、增长与时间取内点和边界；两种负荷形态、五组交叉价格。
    prices=[(.75,.5),(1,1),(1.25,1.25),(.75,1.25),(1.25,.5)]
    cases=list(itertools.product([0,.3,.8,1,1.3,1.8,2,2.3,2.8,3],[0,.01,.02,.04,.07,.08,.10],[1,2,3,4,6],['A','BC'],prices,['偏集中','较均匀']))
    for k,(eta,g,h,area,(ls,bs),shape) in enumerate(cases):
        rows.append(solve(eta,g,h,area,ls,bs,shape))
        if k%300==0:print(json.dumps({'完成':k+1,'总数':len(cases),'秒':round(time.time()-start,1)},ensure_ascii=False),flush=True)
    (OUT/'外推逐点结果.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    (OUT/'外推站级方案.jsonl').write_text('\n'.join(json.dumps(d,ensure_ascii=False) for d in DETAILS))
    with (OUT/'外推逐点结果.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    matrix=[]
    for elo,ehi in [(0,1),(1,2),(2,3)]:
        for glo,ghi in [(0,.02),(.02,.07),(.07,.10)]:
            for hlo,hhi in [(1,3),(3,6)]:
                selected=[r for r in rows if elo<=r['装机渗透率']<=ehi and (glo<r['年负荷平均增长率']<=ghi or glo==0 and r['年负荷平均增长率']==0) and hlo<=r['95%峰值持续时间h']<=hhi]
                assert selected
                values=[r['推荐容载比'] for r in selected]
                # 向外取0.05步长，保留至少0.05的工程推荐宽度。
                lower=max(1.5,math.floor(min(values)/.05)*.05);upper=min(2.6,math.ceil(max(values)/.05)*.05)
                matrix.append({'分布式电源装机渗透率':f'{elo:.1f}～{ehi:.1f}','年负荷平均增长率':(('＞' if glo>0 else '')+f'{glo*100:g}%～{ghi*100:g}%'),'95%峰值持续时间':f'{hlo}～{hhi} h','主变与线路成本比':'0.97～1.64','主变与储能成本比_3h':'0.047～0.119','推荐容载比区间':f'{lower:.2f}～{upper:.2f}','计算点数':len(selected)})
    (OUT/'通用推荐矩阵.json').write_text(json.dumps(matrix,ensure_ascii=False,indent=2))
    wb=Workbook();wb.remove(wb.active)
    for name,items in [('通用推荐区间',matrix),('外推计算点',rows)]:
        ws=wb.create_sheet(name);ws.append(list(items[0]));[ws.append(list(r.values())) for r in items];ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions
        for column in ws.columns:ws.column_dimensions[column[0].column_letter].width=22
    wb.save(OUT/'通用容载比推荐矩阵.xlsx')
    audit={'外推点数':len(rows),'全部约束核对':'通过','最大最优性间隙':max(r['最优性间隙'] for r in rows),'推荐行数':len(matrix),'计算性质':'标准术语下的条件整数规划外推；五站两类模板为研究假定；规划第4年结果','矩阵解释':'参数分档内已计算点的容载比包络向外取整至0.05；属条件推荐区间','价格组合':'五组交叉价格，非完整笛卡尔价格范围验证','评价规则':'统一2021基准至2041评价期；第4年投运；不含建设时序寻优','年用户负荷率假定':.5,'光伏年利用小时假定':1200,'日间出力系数假定':.75,'日间用户负荷系数假定':.3}
    (OUT/'外推核验.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2));print(json.dumps(audit,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
