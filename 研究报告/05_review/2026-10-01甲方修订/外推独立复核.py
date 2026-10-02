from pathlib import Path
import json,math
R=Path(__file__).resolve().parents[2];D=R/'01研究推荐/2026-10-01甲方修订';OUT=Path(__file__).parent
rows=json.loads((D/'外推逐点结果.json').read_text());details=[json.loads(l) for l in (D/'外推站级方案.jsonl').read_text().splitlines()]
assert len(rows)==len(details)==7000
minimum=1e9;worstcost=0
def factor(life,q):
 return 1/1.06**4+sum(q/1.06**(y-2021) for y in range(2026,2042))+sum(1/1.06**(y-2021) for y in range(2025+life,2041,life))
for r,d in zip(rows,details):
 eta,g,h,area,ls,bs,shape=d['参数'];a=d['站级'];p=d['目标负荷MW'];M=d['项目数'];rho=.5 if area=='A' else .28287889;limit=.7 if area=='A' else .5;target=.5 if area=='A' else .3
 assert abs(sum(t['转出MW'] for t in a)-sum(t['转入MW'] for t in a))<1e-4
 assert sum(t['项目端数'] for t in a)==2*M
 assert max(t['项目端数'] for t in a)<=M
 assert sum(t['新增使用MW'] for t in a)<=M*7.49106117+1e-4
 cost=0;capacity=0
 for t in a:
  S,N,purchased,third=t['规格MVA'];n=t['储能柜'];qo=t['转出MW'];qi=t['转入MW'];l=t['负荷MW'];rev=t['反向MW'];B=n*.215/max(2.15,h)
  assert n>=0 and abs(n-round(n))<1e-5 and third in (0,50)
  assert S>=2*t['原单台MVA']+third-1e-5
  margins=[.95*S+B-(l-qo+qi),.95*N+B-(l-qo+qi),.95*S+B-(rev+qo)]
  assert min(margins)>=-1e-4
  minimum=min(minimum,min(margins))
  assert qo<=min(limit*l,rho*l+t['项目端数']*7.49106117)+1e-4
  assert qo<=rho*l+t['新增使用MW']+1e-4
  assert rho*l+t['项目端数']*7.49106117>=target*l-1e-4
  cost+=(purchased*16.57333333333333+(1223 if third else 0))*factor(20,.01)+n*21.0456262*bs*factor(10,.03)
  capacity+=S
 cost+=M*106.8*ls*factor(20,.01)
 assert abs(capacity/p-r['推荐容载比'])<1e-7
 assert 2.001-1e-6<=capacity/p<=2.6+1e-6
 deviation=abs(cost-r['全寿命费用万元']);worstcost=max(worstcost,deviation);assert deviation<1e-3
report={'状态':'通过','计算组合':len(rows),'站级复核':5*len(rows),'最小容量余量MW':minimum,'最大费用偏差万元':worstcost,'复核内容':'由导出的容量、柜数、转接和端点数量重新计算正常/退出/反向容量、负荷守恒、能力预算、容载比及现金流；不使用求解约束矩阵'}
(OUT/'外推独立复核.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(report)
