"""从冻结基准输出独立重建价格、峰段、光伏和加权增长条件。"""
from pathlib import Path
import json,csv,math
ROOT=Path(__file__).resolve().parents[3];DATA=ROOT/'研究报告/01研究推荐/2026-10-01条件矩阵';REVIEW=Path(__file__).parent
REG={'pizhou':1559.638,'city':491.180};SCHEMES=['rigid','elastic']
def rows(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def read(p):return json.loads(p.read_text())
def close(a,b):assert abs(float(a)-float(b))<1e-6,(a,b)
def main():
 base={};check=[];pricegrid=set()
 for r in REG:
  st=rows(DATA/'基准'/r/'rigid_stations.csv');yr=rows(DATA/'基准'/r/'rigid_years.csv');s=read(DATA/'基准'/r/'summary.json')[0]
  peaks={2021:float(s['baseline_2021_load_mw']),**{int(x['year']):float(x['net_peak_proxy_mw']) for x in yr}}
  g=sum(w*(peaks[y]/peaks[y-1]-1) for w,y in enumerate(range(2022,2026),1))/10
  base[r]={'st':{(x['station'],int(x['year'])):x for x in st},'peaks':peaks,'g':g}
 for folder in sorted(DATA.iterdir()):
  if not folder.is_dir() or not (folder/'report_scenario.json').exists():continue
  m=read(folder/'report_scenario.json');physical=m
  analytic='dominance_proof' in m.get('method','')
  if analytic:physical=read(DATA/m.get('reference_layout','基准')/'report_scenario.json')
  if not any(k in physical for k in ['pv','duration_delta','smooth']):pricegrid.add((m.get('line',1),m.get('storage',1)))
  count=0
  for reg in REG:
   b=base[reg]
   for scheme in SCHEMES:
    ys=rows(folder/reg/(scheme+'_years.csv'));st=rows(folder/reg/(scheme+'_stations.csv'));forward={}
    for yrow in ys:
     y=int(yrow['year']);target=b['peaks'][y]
     if physical.get('smooth'):target=b['peaks'][2021]*(1+b['g']+physical.get('growth_delta',0))**(y-2021)
     close(yrow['net_peak_proxy_mw'],target)
     for key,x in b['st'].items():
      if key[1]==y:forward[key]=float(x['forward_mw'])*target/b['peaks'][y]
    for row in st:
     key=row['station'],int(row['year']);orig=b['st'][key];y=key[1]
     close(row['forward_mw'],forward[key]);rev=float(orig['reverse_mw'])
     if physical.get('pv',1)!=1:
      source=[x for k,x in b['st'].items() if k[1]==y];B=sum(float(x['reverse_mw']) for x in source);L=sum(float(x['forward_mw']) for x in source)
      G=rev+(REG[reg]-B)*float(orig['forward_mw'])/L;U=G-rev;rev=max(0,physical['pv']*G-U)
     close(row['reverse_mw'],rev)
     for field in ['forward_duration_h','reverse_duration_h']:
      h=int(orig[field])
      if folder.name!='基准' and not (analytic and m.get('reference_layout','基准')=='基准'):h=max(1,h+physical.get('duration_delta',0))
      close(row[field],h)
     if y==2022:close(row['prior_unit_1_mva'],orig['prior_unit_1_mva']);close(row['prior_unit_2_mva'],orig['prior_unit_2_mva'])
     assert row['area_class']==orig['area_class'];assert row['source_available_third_slots']==orig['source_available_third_slots'];count+=1
   summaries=read(folder/reg/'summary.json')
   for s in summaries:
    close(s.get('line_scale',1),m.get('line',1));close(s.get('storage_scale',1),m.get('storage',1))
  check.append({'情景':folder.name,'构造方式':'正费用支配及参考情景' if analytic else '独立输入计算','核对站年':count,'输入与冻结基准的关系':'通过'})
 assert len(check)==18,len(check);assert pricegrid=={(a,b) for a in [.75,1,1.25] for b in [.5,.75,1,1.25]},pricegrid
 (REVIEW/'情景输入独立复核.json').write_text(json.dumps({'价格网格':sorted(pricegrid),'情景':check,'总核对站年':sum(x['核对站年'] for x in check)},ensure_ascii=False,indent=2))
 print('输入核对：18情景、12价格交叉条件、',sum(x['核对站年'] for x in check),'站年通过')
if __name__=='__main__':main()
