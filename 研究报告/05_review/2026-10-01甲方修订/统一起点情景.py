"""采用离散设备共同初态，将负荷标定至R0=2；后续为增长情景。

原始年度表和历史冻结结果不改。仿真年1—4使用2022—2025标签供折现。
"""
import copy, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from 实验.研究.rebuild_2026 import regional_static_milp_v2 as reg
from 实验.研究.rebuild_2026 import regional_static_milp_v2_audit as audit
from 实验.研究.rebuild_2026 import joint_shared_measure as joint
from 实验.研究.rebuild_2026.planning_load_profile import weighted_annual_growth

ORIGINAL=reg.input_data
TRACE={}
def inputs(load_scenario,region=reg.REGION,city_baseline_cap_mva=None):
    baseline,scenes,durations,peaks,catalog,price=ORIGINAL(load_scenario,region,city_baseline_cap_mva)
    baseline,scenes,durations,peaks=copy.deepcopy(baseline),copy.deepcopy(scenes),copy.deepcopy(durations),dict(peaks)
    observed={y:float(peaks[region+(y,)]) for y in range(2021,2026)}
    g=weighted_annual_growth(observed)[0]
    capacity=sum(float(r['simulation_capacity_mva_2021']) for r in baseline.values())
    anchor=capacity/2
    for st in baseline:
        baseline[st]['estimated_forward_peak_mw_2021']=float(baseline[st]['estimated_forward_peak_mw_2021'])*anchor/observed[2021]
        template=copy.deepcopy(scenes[st,2025])
        for y in range(2022,2026):
            scale=anchor*(1+g)**(y-2021)/observed[2025]
            scenes[st,y]['estimated_station_forward_peak_mw']=float(template['estimated_station_forward_peak_mw'])*scale
            scenes[st,y]['reverse_screen_mw']=float(template['reverse_screen_mw'])*scale
    for y in range(2021,2026):peaks[region+(y,)]=anchor*(1+g)**(y-2021)
    TRACE[region[0]]={'基期主变容量MVA':capacity,'基期年网供最大负荷MW':anchor,'基期容载比':2.0,'年负荷平均增长率':g,'负荷构造':'2025站级分布按仿真年度规模缩放','年份性质':'基期及后续四年增长情景；2022—2025仅作折现时点标签'}
    return baseline,scenes,durations,peaks,catalog,price

def source_check(directories,output):
    checks=[]
    for p in map(Path,directories):
        summaries=json.loads((p/'summary.json').read_text())
        for summary in summaries:
            region=(summary['region_id'],int(summary['voltage_kv']))
            _,_,_,peaks,_,_=inputs('observed_annual',region,summary.get('city_baseline_cap_mva'))
            assert abs(summary['baseline_2021_clr']-2)<1e-8
            for row in joint.read_csv(p/(summary['scheme']+'_years.csv')):
                assert abs(float(row['net_peak_proxy_mw'])-peaks[region+(int(row['year']),)])<1e-5
        checks.append({'地区':p.name,'统一起点与增长情景核对':'通过'})
    Path(output).write_text(json.dumps(checks,ensure_ascii=False,indent=2))
    return checks

def main():
    out=ROOT/'研究报告/01研究推荐/2026-10-01甲方修订/统一起点基准'
    reg.input_data=inputs;audit.input_data=inputs;joint.source_audit=source_check
    seed=out/'solver_logs/joint_four_paths_minimum_cost_unproven_candidate.npz'
    joint.solve('station_rate','all_years',out,False,1800,'load_reallocation',str(seed) if seed.exists() else None,.01,.005,'selected_rigid_layout','full','A')
    (out/'统一起点输入说明.json').write_text(json.dumps(TRACE,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
