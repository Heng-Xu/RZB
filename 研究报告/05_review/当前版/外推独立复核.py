"""从导出的设备和路径逐项复核外推；不复用求解器约束矩阵。"""
from pathlib import Path
import argparse,json,sys,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from 实验.研究.rebuild_2026.current_economic_assumptions import LINE_TYPES,line_capex
R=Path(__file__).resolve().parents[2];HERE=Path(__file__).parent
INC=7.49106117

def factor(life,q):
 return 1/1.06**4+sum(q/1.06**(y-2021) for y in range(2026,2042))+sum(1/1.06**(y-2021) for y in range(2025+life,2041,life))

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--data',type=Path,default=R/'01研究推荐/当前版');parser.add_argument('--output',type=Path,default=HERE/'外推独立复核.json');args=parser.parse_args()
 rows=json.loads((args.data/'外推逐点结果.json').read_text());details=[json.loads(l) for l in (args.data/'外推站级方案.jsonl').read_text().splitlines()]
 assert len(rows)==len(details)==25200
 minimum=1e9;worstcost=0
 def check(margin,context):
  nonlocal minimum
  minimum=min(minimum,margin)
  assert margin>=-1e-4,(context,margin)
 for r,d in zip(rows,details):
  eta,g,h,area,ls,bs,shape,line_type=d['参数'];a=d['站级'];p=d['目标负荷MW'];M=d['项目数'];rho=0.0;limit=.7 if area=='A' else .5
  assert d['线路基价万元']==line_capex(LINE_TYPES[line_type])
  assert abs(sum(t['转出MW']-t['转入MW'] for t in a))<1e-4
  built={(x['起点'],x['终点']):x['项目数'] for x in d['新增联络站对']}
  assert all(0<=i<j<5 and n>=1 and n==round(n) for (i,j),n in built.items())
  assert sum(built.values())==M and sum(t['项目端数'] for t in a)==2*M
  normal={(x['起点'],x['终点']):x for x in d['正常转接路径']}
  contingency={(x['停运站'],x['承接站']):x for x in d['单台主变停运转供']}
  assert len(contingency)==20
  cost=0;capacity=0
  for i,t in enumerate(a):
   S,N,purchased,third=t['规格MVA'];n=t['储能柜'];qo=t['转出MW'];qi=t['转入MW'];l=t['负荷MW'];rev=t['反向MW'];B=n*.215/max(2.15,h)
   assert n>=0 and abs(n-round(n))<1e-5 and third in (0,50)
   assert S>=2*t['原单台MVA']+third-1e-5
   check(.95*S+B-(l-qo+qi),'正常容量');check(.95*S+B-(rev+qo),'反向容量')
   assert t['项目端数']==sum(v for pair,v in built.items() if i in pair)
   for direction,actual in [('起点',qo),('终点',qi)]:
    assert abs(sum(x['既有MW']+x['新增MW'] for x in normal.values() if x[direction]==i)-actual)<1e-4
   cost+=(purchased*16.57333333333333+(1223 if third else 0))*factor(40,.042)+n*21.0456262*bs*factor(25,.03);capacity+=S
  for k in range(5):
   tf=sum(contingency[k,j]['总转供MW'] for j in range(5) if j!=k)
   for i,t in enumerate(a):
    S,N,*_=t['规格MVA'];B=t['储能柜']*.215/max(2.15,h);net=t['负荷MW']-t['转出MW']+t['转入MW']
    transfer=tf if i==k else contingency[k,i]['总转供MW']
    additional=sum(contingency[k,j]['新增线路转供MW'] for j in range(5) if j!=k) if i==k else contingency[k,i]['新增线路转供MW']
    check(.95*(N if i==k else S)+B-net+(transfer if i==k else -transfer),'单台主变停运容量')
    movement=t['转出MW']+t['转入MW']+transfer
    check(limit*t['负荷MW']-movement,'站级转供上限')
    check(rho*t['负荷MW']+t['项目端数']*INC-movement,'安装端点能力')
    old=sum(x['既有MW'] for pair,x in normal.items() if i in pair)
    check(rho*t['负荷MW']-old-transfer+additional,'既有联络共用能力')
   for i in range(5):
    for j in range(i+1,5):
     normal_new=sum(normal.get(pair,{}).get('新增MW',0) for pair in [(i,j),(j,i)])
     fault_new=contingency[k,j if k==i else i]['新增线路转供MW'] if k in (i,j) else 0
     check(built.get((i,j),0)*INC-normal_new-fault_new,'新增线路共用能力')
   for j in range(5):
    if j==k:continue
    x=contingency[k,j];check(x['新增线路转供MW'],'新线转供非负');check(x['总转供MW']-x['新增线路转供MW'],'既有转供非负')
  cost+=M*line_capex(LINE_TYPES[line_type])*ls*factor(40,.022)
  assert abs(capacity/p-r['推荐容载比'])<1e-7 and (1.5 if g<=.02 else 1.6 if g<=.04 else 1.7 if g<=.07 else 1.8)-1e-6<=capacity/p<=2.6+1e-6
  deviation=abs(cost-r['全寿命费用万元']);worstcost=max(worstcost,deviation);assert deviation<1e-3
  assert r['最优性间隙']<=1.01e-8
 report={'状态':'通过','模型版本':'1008新增联络专项外推','计算组合':len(rows),'站级复核':5*len(rows),'单台主变停运场景':5*len(rows),'最小约束余量MW':minimum,'最大费用偏差万元':worstcost,'最大最优性间隙':max(r['最优性间隙'] for r in rows),'数据SHA256':hashlib.sha256((args.data/'外推逐点结果.json').read_bytes()).hexdigest(),'复核内容':'独立复算正常及反向容量、各站单台主变停运和承接站容量、既有联络及逐站对新建线路在正常与事故转供下的共用能力、端点及项目数量、容载比和费用现值。'}
 args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2));print(report)
if __name__=='__main__':main()
