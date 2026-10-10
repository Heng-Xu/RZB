from pathlib import Path
import sys,json,copy
from concurrent.futures import ProcessPoolExecutor
import numpy as np
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from 实验.研究.rebuild_2026.static_actual_20261010 import run as a
from 实验.研究.rebuild_2026.network_case_20261010.solver import solve
O=ROOT/'研究报告/试算/20261010_案例敏感性'
def fixed_limits(inp,p,y):
 ids=list(inp['stations']);idx={s:j for j,s in enumerate(ids)};ref=inp['feeder_reference_peak_2025_mw'];annual=inp['annual_observed_peak_mw'][str(y)]/ref;scale=ref/inp['initial_peak_mw'];donor={};receive={}
 for f,r in inp['network']['feeders'].items():
  peak=inp['stations'][r['station']]['base_forward_mw']*scale
  donor[f]=r['maximum_load_proxy_2025_mw']*max(0.,float(p[idx[r['station']]]))/peak
  receive[f]=max(0.,r['thermal_mw']-r['maximum_load_proxy_2025_mw']*annual)
 return donor,receive

def one(path):
 r=json.loads(path.read_text());out=path.parent;inp=json.loads((out/'inputs.json').read_text());sc={int(k):v for k,v in np.load(out/'scenes.npz').items()};a.network.limits=fixed_limits if "feeder_reference_peak_2025_mw" in inp else a.actual_limits;m,meta=a.build(inp,sc,'elastic_storage');m.constraint({i:c for i,c in enumerate(m.costs) if c},upper=r['solver']['objective']+1e-5)
 warm=copy.deepcopy(inp);warm['storage_usable_energy_fraction']=1
 z,res=solve(m,out,'refine',300,.01,warm,meta,out)
 old=copy.deepcopy(r);(out/'before_refine.json').write_text(json.dumps(old,ensure_ascii=False,indent=2))
 if res.get('feasible_incumbent') and res['objective']<=r['solver']['objective']+1e-5:
  checks=[]
  for y in inp['years']:
   units,n,_,_=a.assets_model.assets(inp,z,meta,y);built={e for (e,yy),v in meta['edgevars'].items() if yy==y and z[v]>.5};check,violations=a.network.check_year(inp,sc[y],y,units,n,built);assert not violations;checks.append(check)
  res['dual_bound']=max(res['dual_bound'],r['solver']['dual_bound']);res['mip_gap']=(res['objective']-res['dual_bound'])/res['objective']
  summary,stations,projects=a.network.extract(inp,None,'elastic_storage',z,meta,res,[],checks)
  r.update(solver=res,summary=summary,checks=checks,verified=True);a.write_csv(out/'stations.csv',stations);a.write_csv(out/'projects.csv',projects);path.write_text(json.dumps(r,ensure_ascii=False,indent=2))
 print('REFINED',r['region'],r['parameter'],r['value'],r['solver']['mip_gap'],flush=True)
if __name__=='__main__':
 paths=[p for p in O.glob('*/*/summary.json') if json.loads(p.read_text())['solver']['mip_gap']>.1]
 with ProcessPoolExecutor(max_workers=2) as pool:list(pool.map(one,paths))
 (O/'汇总.json').write_text(json.dumps([json.loads(p.read_text()) for p in sorted(O.glob('*/*/summary.json'))],ensure_ascii=False,indent=2))
