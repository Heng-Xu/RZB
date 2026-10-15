import copy
import hashlib
import json
import math
import sys
from pathlib import Path
from collections import Counter
import numpy as np
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from 实验.研究.rebuild_2026.review_20261015 import cases as first, matrix as matrix15
from 实验.研究.rebuild_2026.recommend_20261015 import model as latest
from 实验.研究.rebuild_2026.economic_two_districts_20261015 import model as economic
from 实验.研究.rebuild_2026.matrix_20261012 import model as matrix12
out=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'研究报告/05_review/当前版/1015静态替代机制检查'
out.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def source(p):return dict(path=str(p.relative_to(ROOT)),sha256=sha(p))
root=first.OUT/'pizhou/annual_2021_reverse80';ip=root/'inputs.json';inp=json.loads(ip.read_text())
scenes=first.old.base.load_scenes(first.old.base.OUT/'pizhou',inp)
paths=[p.parent for p in root.glob('rigid*/summary.json') if json.loads(p.read_text()).get('case')=='rigid']
folder=min(paths,key=lambda p:json.loads((p/'summary.json').read_text())['cost_npv_10k'])
summary=json.loads((folder/'summary.json').read_text())
current_input=economic.RAW/'pizhou/annual_2021/inputs.json'
current=json.loads(current_input.read_text())
shared_keys=['years','stations','network','initial_capacity_mva','annual_observed_peak_mw',
             'existing_transfer_budget_by_year_mw','cost_factors']
assert all(inp[k]==current[k] for k in shared_keys)

class GateLP(first.StationLP):
    def __init__(self,inp,standby,direct):
        super().__init__(inp);self.standby=standby;self.direct=direct
    def bounds_for(self,prepared,failed):
        common,bounds,full,largest,bp,bn=super().bounds_for(prepared,failed)
        if failed<0 and self.standby:
            bp=np.zeros_like(bp);bn=-(1-self.inp['normal_reverse_limit_fraction'])*full
        if failed>=0 and self.direct:
            bounds=[bound if failed in (arc[5],arc[6]) else (0.,0.) for arc,bound in zip(self.arcs,bounds)]
        return common,bounds,full,largest,bp,bn

records=[]
for standby,direct in [(False,False),(True,False),(False,True),(True,True)]:
    lp=GateLP(inp,standby,direct);checks=0;bad=[];normal=0
    for y in inp['years']:
        u,n,built=first.old.assets_from_csv(inp,folder,y)
        for h,p in enumerate(scenes[y]):
            ready=lp.prepared(p,y,u,n,built)
            for f in range(-1,len(u)):
                r=lp.check(p,ready,f);checks+=1
                if f<0:normal+=1
                if not r['verified']:bad.append(dict(year=y,scenario=h,failed=f,deficit_mw=r['deficit_mw'],station_deficits=r['station_deficits']))
    record=dict(normal_storage_allowed=not standby,fault_incident_edges_only=direct,checked_pairs=checks,
                normal_pairs=normal,violating_pairs=len(bad),normal_violations=sum(r['failed']<0 for r in bad),
                fault_violations=sum(r['failed']>=0 for r in bad),max_deficit_mw=max((r['deficit_mw'] for r in bad),default=0),failures=bad)
    records.append(record);print('REPLAY',standby,direct,checks,len(bad),record['max_deficit_mw'],flush=True)
assert records[0]['violating_pairs']==0
assert records[1]['normal_violations']>0

# Isolate the storage mechanism on a real station asset, without alternate paths.
probe_inp=copy.deepcopy(inp)
for e in probe_inp['network']['edges']:e['capacity_mw']=0.
ids=list(inp['stations']);sid='BDZ-00162';j=ids.index(sid);u=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]);full=.95*u[j].sum()
probes=[]
for direction,demand,coef in [('forward',full+5,min(.1,.215*.76/inp['stations'][sid]['forward_duration_h'])),
                              ('reverse',-(.8*full+5),min(.1,.215*.76/inp['stations'][sid]['reverse_duration_h']))]:
    p=np.zeros(len(ids));p[j]=demand;n=np.zeros(len(ids));n[j]=math.ceil(5/coef)
    row=dict(direction=direction,station=sid,transformer_mva=float(u[j].sum()),net_demand_mw=demand,
             storage_modules=int(n[j]),effective_support_mw=float(n[j]*coef),meaning='受控机制试验，通道全部置零；非工程配置建议')
    for label,klass in [('first_review',first.StationLP),('latest',latest.OperatingLP)]:
        lp=klass(probe_inp);r=lp.check(p,lp.prepared(p,2025,u,n,set()),-1)
        row[label]=r
    assert row['first_review']['verified'] and not row['latest']['verified']
    assert abs(row['latest']['deficit_mw']-5)<1e-6
    probes.append(row)

# Static matrix allows normal/fault support. Check complete selected sequences, not only endpoints.
p12=ROOT/'研究报告/试算/20261012_参数联合情景锁定/统一原始求解记录.jsonl'
p15=matrix15.OUT/'transfer_grid_procurement.jsonl'
target=dict(eta=1.5,growth_rate=.04,cable_fraction=.1,support_duration_h=4.,diversity=1.1)
matrices=[]
for file,ver,fn in [(p12,'formal_stock_20261012',matrix12.independent_lp_check),(p15,'review_20261015',matrix15.independent_lp_check)]:
    rows=[json.loads(line) for line in file.open()]
    chosen=[r for r in rows if all(abs(r[k]-v)<1e-8 for k,v in target.items())]
    seq=[]
    for r in sorted(chosen,key=lambda r:(r.get('mode','stock'),r['initial_transfer_fraction'])):
        pars={k:r[k] for k in matrix12.FIELDS}
        if ver=='review_20261015':pars['normal_reverse_limit_fraction']=.8
        proof=fn(pars,r['units'],r['modules'],set(r['built']));assert proof['verified'],(pars,proof)
        seq.append({**{k:r.get(k) for k in ['mode','initial_transfer_fraction','capacity_mva','clr','storage_mwh','line_count','relative_gap']},'independent_check':proof})
    matrices.append(dict(version=ver,source=source(file),total_rows=len(rows),valid_rows=sum(r['verified'] for r in rows),controlled_sequence=seq))
    print('MATRIX',ver,'checked_nodes',len(seq),flush=True)

net_cal=[]
for rho in [.1,.3,.5,.7,.9]:
    pars=dict(target,initial_transfer_fraction=rho)
    mi=matrix12.make_input(pars)
    net_cal.append(dict(initial_transfer_fraction=rho,realized_reference_rate=mi['initial_transfer_audit']['weighted_rate'],
        network_scale=mi['initial_network_scale'],thermal_mw=mi['thermal'].tolist(),
        receiver_headroom_mw=mi['receiver_headroom'].tolist(),existing_budget_mw=mi['existing_budget'].tolist(),
        number_of_static_scenes=len(mi['gross']),number_of_checks=len(mi['gross'])*6,
        stock_capacity_floor_mva=500.,greenfield_capacity_floor_mva=315.))

# Keep all source hashes tied to this audit; do not rewrite frozen results.
files=[Path(__file__),Path(first.__file__),Path(latest.__file__),Path(economic.__file__),Path(matrix12.__file__),Path(matrix15.__file__),
       ROOT/'实验/研究/rebuild_2026/review_20261015_followup/cases.py',
       ROOT/'实验/研究/rebuild_2026/case_parameters_20261012/capacity_run.py',
       ROOT/'实验/研究/rebuild_2026/case_parameters_20261012/transfer_diagnostic.py',
       ROOT/'实验/研究/rebuild_2026/network_case_20261010/run.py',
       ROOT/'实验/研究/rebuild_2026/synchronous_20261009/model.py']
result=dict(verified=True,scope='静态扩容替代机制审查，不引入SOC，不修改历史模型或重算最优值',
    sources=[source(p) for p in files+[ip,current_input,folder/'stations.csv',folder/'projects.csv',folder/'summary.json']],
    identical_planning_inputs=shared_keys,
    first_review_original_start_rigid=dict(folder=str(folder.relative_to(ROOT)),annual=summary['annual'],cost_npv_10k=summary['cost_npv_10k'],solver=summary['solver']),
    replay=records,isolated_storage_probes=probes,matrix_checks=matrices,transfer_network_calibration=net_cal,
    limits=['复核只证明规定静态工况可行；不将静态有效功率称为全年调度结果',
            '事故直接通道限制与正常储能禁用分开试验；年度固定转供比例未在本次GateLP对照中施加',
            '恢复替代机制后各方案数值及排序须按共同模型重新比选，不能由本核验推定所有旧方案均最优'])
dump(out/'静态替代机制核验.json',result)
print('AUDIT_SAVED',out,flush=True)
