"""对10月1日同措施、同起点联合模型作两价格比及物理参数外推。

不改冻结模型及原始收资；每情景保存完整年度、站级和转接结果。
"""
import argparse
import copy
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from 实验.研究.rebuild_2026 import joint_shared_measure as joint
from 实验.研究.rebuild_2026 import regional_static_milp_v2 as regional
from 实验.研究.rebuild_2026 import regional_static_milp_v2_audit as audit_module
from 实验.研究.rebuild_2026.planning_load_profile import weighted_annual_growth

OUT = ROOT / '研究报告/01研究推荐/2026-10-01条件矩阵'
BASE = ROOT / '实验/研究/rebuild_2026/outputs/joint_shared_measure/transfer_10pct_all_years_load_reallocation'
SOURCE = {
 ('QX-00005',110): {'C':1559.638,'eta':1.630652935,'energy':.402778151},
 ('QX-00007',110): {'C':491.180,'eta':.317875803,'energy':.086939913},
}
CASES = [
 {'id':'价格_线路较贵','line':1.25},
 {'id':'价格_线路较低','line':.75},
 {'id':'价格_储能降价25','storage':.75},
 {'id':'价格_储能降价50','storage':.50},
 {'id':'价格_储能较贵25','storage':1.25},
 {'id':'联合_线路贵储能低','line':1.25,'storage':.50},
 {'id':'源荷_光伏规模减20','pv':.80},
 {'id':'源荷_光伏规模增20','pv':1.20},
 {'id':'持续时间_缩短1h','duration_delta':-1},
 {'id':'持续时间_延长1h','duration_delta':1},
 {'id':'增长_四年加权','smooth':True},
 {'id':'增长_加权增2个百分点','smooth':True,'growth_delta':.02},
]

def configure(case):
 original_input = regional.input_data
 original_audit_input=audit_module.input_data
 original_source_audit=joint.source_audit
 original_problem = joint.optimization_problem
 def scenario_input(load_scenario, region=regional.REGION, city_baseline_cap_mva=None):
  baseline, scenes, durations, peaks, catalog, price = original_input(load_scenario,region,city_baseline_cap_mva)
  scenes, durations, peaks = copy.deepcopy(scenes),copy.deepcopy(durations),dict(peaks)
  observed={y:peaks[region+(y,)] for y in (2021,2022,2023,2024,2025)}
  if case.get('smooth'):
   g=weighted_annual_growth(observed)[0]+case.get('growth_delta',0)
   for y in (2022,2023,2024,2025):
    target=observed[2021]*(1+g)**(y-2021)
    scale=target/observed[y]
    peaks[region+(y,)]=target
    for s in baseline:
     scenes[s,y]['estimated_station_forward_peak_mw']=float(scenes[s,y]['estimated_station_forward_peak_mw'])*scale
  for s in baseline:
   for field in ['forward_d95_max_run_hours','reverse_d95_max_run_hours']:
    durations[s][field]=max(1,int(durations[s][field])+case.get('duration_delta',0))
  # 用原反送压力与光伏装机构造非负用户负荷的反送典型场景。
  # φ=1是额定出力包络假定；源荷空间权重在已反送量上优先分配，
  # 余量按站级正向需求分配。原PV情景严格恢复原反送极值。
  if case.get('pv',1)!=1:
   for y in (2022,2023,2024,2025):
    rev={s:float(scenes[s,y]['reverse_screen_mw']) for s in baseline}
    forward={s:float(scenes[s,y]['estimated_station_forward_peak_mw']) for s in baseline}
    c=SOURCE[region]['C']
    assert c+1e-6>=sum(rev.values()),'反送场景需要额外装机台账'
    remainder=c-sum(rev.values())
    for s in baseline:
     injection=rev[s]+remainder*forward[s]/sum(forward.values())
     gross=injection-rev[s]
     scenes[s,y]['reverse_screen_mw']=max(0,case['pv']*injection-gross)
  return baseline,scenes,durations,peaks,catalog,price
 def scenario_problem(*args,**kwargs):
  kwargs.update(line_scale=case.get('line',1),storage_scale=case.get('storage',1))
  return original_problem(*args,**kwargs)
 regional.input_data=scenario_input
 audit_module.input_data=scenario_input
 joint.optimization_problem=scenario_problem
 def scenario_source_audit(directory_names,output_file):
  if not case.get('smooth'):return original_source_audit(directory_names,output_file)
  checks=[]
  for label,region in joint.DISTRICTS.items():
   folder=Path(directory_names[0 if label=='pizhou' else 1])
   summaries=json.loads((folder/'summary.json').read_text())
   _,_,_,expected,_,_=scenario_input('observed_annual',region,summaries[0].get('city_baseline_cap_mva'))
   for summary in summaries:
    data=joint.read_csv(folder/(summary['scheme']+'_years.csv'))
    for row in data:
     y=int(row['year']);assert abs(float(row['net_peak_proxy_mw'])-expected[region+(y,)])<1e-5
   checks.append({'region':label,'status':'PASS','source_scope':'original_2021_anchor_plus_explicit_weighted_growth_scenario','growth_delta':case.get('growth_delta',0)})
  Path(output_file).write_text(json.dumps(checks,ensure_ascii=False,indent=2));return checks
 joint.source_audit=scenario_source_audit
 return original_input,original_problem,original_audit_input,original_source_audit

def main():
 p=argparse.ArgumentParser();p.add_argument('--index',type=int);args=p.parse_args()
 cases=CASES if args.index is None else [CASES[args.index]]
 for case in cases:
  folder=OUT/case['id'];folder.mkdir(parents=True,exist_ok=True)
  if (folder/'report_scenario.json').exists() and json.loads((folder/'report_scenario.json').read_text()).get('status')=='solved':continue
  original_input,original_problem,original_audit_input,original_source_audit=configure(case)
  try:
   resume=(folder/'minimum_cost_checkpoint.npz').exists()
   joint.solve('transfer_10pct','all_years',folder,resume,900,'load_reallocation',
    str(BASE/'minimum_cost_checkpoint.npz') if not any(k in case for k in ('pv','duration_delta','smooth')) else None,
    1e-7,1e-7,'global_joint','bc_min_service_static',None)
   case['status']='solved'
  except Exception as e:
   import traceback
   case['status']='infeasible_or_unproved';case['error']=repr(e)
   (folder/'error_trace.txt').write_text(traceback.format_exc())
  finally:
   regional.input_data=original_input;joint.optimization_problem=original_problem
   audit_module.input_data=original_audit_input;joint.source_audit=original_source_audit
  case['k_TL_relative']=1/case.get('line',1)
  case['k_TB_relative']=1/case.get('storage',1)
  (folder/'report_scenario.json').write_text(json.dumps(case,ensure_ascii=False,indent=2))
  print(json.dumps(case,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
