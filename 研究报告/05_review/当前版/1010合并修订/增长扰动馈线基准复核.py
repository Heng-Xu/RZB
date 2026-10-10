"""增长扰动时固定2025馈线负荷代理对应的原始地区峰值，热限不变。"""
from pathlib import Path
import sys,json,copy
from concurrent.futures import ProcessPoolExecutor
import numpy as np
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from 实验.研究.rebuild_2026.static_actual_20261010 import run as a
from 实验.研究.rebuild_2026.network_case_20261010.solver import solve
C=ROOT/'研究报告/试算/20261010_四小时案例';OLD=ROOT/'研究报告/试算/20261010_案例敏感性';O=ROOT/'研究报告/试算/20261010_案例增长敏感性_馈线基准固定';O.mkdir(exist_ok=True)
def fixed_limits(inp,p,y):
 ids=list(inp['stations']);idx={s:j for j,s in enumerate(ids)};ref=inp['feeder_reference_peak_2025_mw'];annual=inp['annual_observed_peak_mw'][str(y)]/ref;scale=ref/inp['initial_peak_mw'];donor={};receive={}
 for f,r in inp['network']['feeders'].items():
  peak=inp['stations'][r['station']]['base_forward_mw']*scale
  donor[f]=r['maximum_load_proxy_2025_mw']*max(0.,float(p[idx[r['station']]]))/peak
  receive[f]=max(0.,r['thermal_mw']-r['maximum_load_proxy_2025_mw']*annual)
 return donor,receive
def one(task):
 reg,delta=task;out=O/reg/str(delta);out.mkdir(parents=True,exist_ok=True)
 inp=json.loads((C/reg/'inputs.json').read_text());sc=a.load_scenes(C/reg,inp);g=inp['growth_rate'];inp['feeder_reference_peak_2025_mw']=inp['annual_observed_peak_mw']['2025']
 for y in inp['years']:
  ratio=((1+g+delta)/(1+g))**(y-2021);sc[y]*=ratio;inp['annual_observed_peak_mw'][str(y)]*=ratio
 inp['growth_rate']=g+delta;(out/'inputs.json').write_text(json.dumps(inp,ensure_ascii=False,indent=2));np.savez_compressed(out/'scenes.npz',**{str(y):v for y,v in sc.items()})
 a.network.limits=fixed_limits;m,meta=a.build(inp,sc,'elastic_storage');warm=copy.deepcopy(inp);warm['storage_usable_energy_fraction']=1.
 z,res=solve(m,out,'fixed_reference',210,.01,warm,meta,OLD/reg/('growth_delta_'+str(delta)))
 r={'region':reg,'parameter':'growth_delta','value':delta,'growth_baseline':g,'solver':res,'verified':False,'feeder_reference':'原始2025地区峰值固定，馈线热限固定，馈线负荷随扰动同步变化'}
 if res.get('feasible_incumbent'):
  checks=[]
  for y in inp['years']:
   units,n,_,_=a.assets_model.assets(inp,z,meta,y);built={e for (e,yy),v in meta['edgevars'].items() if yy==y and z[v]>.5};check,violations=a.network.check_year(inp,sc[y],y,units,n,built);assert not violations;checks.append(check)
  summary,stations,projects=a.network.extract(inp,None,'elastic_storage',z,meta,res,[],checks);r.update(summary=summary,checks=checks,verified=True);a.write_csv(out/'stations.csv',stations);a.write_csv(out/'projects.csv',projects)
 (out/'summary.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print('FIXED',reg,delta,r['verified'],res['mip_gap'],flush=True)
if __name__=='__main__':
 with ProcessPoolExecutor(max_workers=4) as pool:list(pool.map(one,[(r,d) for r in ['pizhou','city'] for d in [-.02,.02]]))
