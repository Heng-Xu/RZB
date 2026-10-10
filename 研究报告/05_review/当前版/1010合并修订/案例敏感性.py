"""两地区实际年度序列与具体网络上的弹性方案单参数扰动。"""
from pathlib import Path
import sys,json,copy
from concurrent.futures import ProcessPoolExecutor
import numpy as np
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from 实验.研究.rebuild_2026.static_actual_20261010 import run as a
from 实验.研究.rebuild_2026.network_case_20261010.solver import solve
C=ROOT/'研究报告/试算/20261010_四小时案例';O=ROOT/'研究报告/试算/20261010_案例敏感性';O.mkdir(exist_ok=True)
def fixed_limits(inp,p,y):
 ids=list(inp['stations']);idx={s:j for j,s in enumerate(ids)};ref=inp['feeder_reference_peak_2025_mw'];annual=inp['annual_observed_peak_mw'][str(y)]/ref;scale=ref/inp['initial_peak_mw'];donor={};receive={}
 for f,r in inp['network']['feeders'].items():
  peak=inp['stations'][r['station']]['base_forward_mw']*scale
  donor[f]=r['maximum_load_proxy_2025_mw']*max(0.,float(p[idx[r['station']]]))/peak
  receive[f]=max(0.,r['thermal_mw']-r['maximum_load_proxy_2025_mw']*annual)
 return donor,receive

def one(task):
 reg,key,value=task;out=O/reg/(key+'_'+str(value));out.mkdir(parents=True,exist_ok=True)
 if (out/'summary.json').exists():return json.loads((out/'summary.json').read_text())
 inp=json.loads((C/reg/'inputs.json').read_text());scenes=a.load_scenes(C/reg,inp)
 g=inp['growth_rate'];inp['feeder_reference_peak_2025_mw']=inp['annual_observed_peak_mw']['2025']
 if key=='growth_delta':
  for y in inp['years']:
   ratio=((1+g+value)/(1+g))**(y-2021);scenes[y]*=ratio;inp['annual_observed_peak_mw'][str(y)]*=ratio
  inp['growth_rate']=g+value
 elif key=='line_factor':inp['line_capex_10k']=(inp['line_capex_10k']-6)*value+6
 elif key=='duration':
  for st in inp['stations'].values():st['forward_duration_h']=value
 (out/'inputs.json').write_text(json.dumps(inp,ensure_ascii=False,indent=2))
 np.savez_compressed(out/'scenes.npz',**{str(y):v for y,v in scenes.items()})
 a.network.limits=fixed_limits;m,meta=a.build(inp,scenes,'elastic_storage')
 warm=copy.deepcopy(inp);warm['storage_usable_energy_fraction']=1
 z,res=solve(m,out,'sensitivity',150,.01,warm,meta,C/reg/'elastic_storage')
 record={'region':reg,'parameter':key,'value':value,'growth_baseline':g,'solver':res,'verified':False}
 if res.get('feasible_incumbent'):
  checks=[]
  for y in inp['years']:
   units,n,_,_=a.assets_model.assets(inp,z,meta,y);built={e for (e,yy),v in meta['edgevars'].items() if yy==y and z[v]>.5}
   check,violations=a.network.check_year(inp,scenes[y],y,units,n,built);assert not violations;checks.append(check)
  summary,stations,projects=a.network.extract(inp,None,'elastic_storage',z,meta,res,[],checks)
  record.update(verified=True,summary=summary,checks=checks)
  a.write_csv(out/'stations.csv',stations);a.write_csv(out/'projects.csv',projects)
 (out/'summary.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print('COMPLETE',task,record['verified'],flush=True);return record
if __name__=='__main__':
 tasks=[(reg,k,v) for reg in ['pizhou','city'] for k,vs in [('baseline',[0]),('growth_delta',[-.02,.02]),('line_factor',[.75,1.25]),('duration',[2.,6.])] for v in vs]
 with ProcessPoolExecutor(max_workers=3) as pool:results=list(pool.map(one,tasks))
 (O/'汇总.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
