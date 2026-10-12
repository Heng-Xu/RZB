"""用已有站级记录的静态截面核查首年承载力，不新增SOC仿真。"""
import json
from collections import defaultdict

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix,hstack,eye,vstack,csr_matrix

from .run import ROOT,OUT,REVIEW,PF,limits,previous,dump,write_csv,sha

PROFILES=ROOT/'研究报告/数据来源/当前版/区域时序'


def snapshots(region,inp):
    """保留同期站级矢量，不把各站各自峰值相加成同时负荷。"""
    z=np.load(PROFILES/f'{region}_stations.npz')
    ids=list(inp['stations']); source_ids=list(z['station_ids'])
    order=[source_ids.index(s) for s in ids]
    power=z['power_mw'][:,order]; observed=z['observed'][:,order]
    selected={int(np.argmax(power.sum(axis=1))),int(np.argmin(power.sum(axis=1)))}
    selected.update(map(int,np.argmax(power,axis=0)));selected.update(map(int,np.argmin(power,axis=0)))
    hours=sorted(selected)
    # 2025样本区域正向峰值标定原年度统计；其他年份沿用同一空间分配形态。
    scale=inp['initial_peak_mw']/power.sum(axis=1).max()
    base=power[hours]*scale
    records=[]
    for h in hours:
        roles=[]
        if h==int(np.argmax(power.sum(axis=1))):roles.append('地区正向峰值')
        if h==int(np.argmin(power.sum(axis=1))):roles.append('地区最低净负荷')
        roles.extend(s+'正向峰值' for j,s in enumerate(ids) if h==int(np.argmax(power[:,j])))
        roles.extend(s+'最低净负荷' for j,s in enumerate(ids) if h==int(np.argmin(power[:,j])))
        records.append(dict(source_hour=h,roles='；'.join(roles),all_stations_observed=bool(observed[h].all()),
                            raw_region_net_mw=float(power[h].sum()),baseline_region_net_mw=float(power[h].sum()*scale)))
    return base,records


class FlowLP:
    """设备固定后的独立网络LP；每条边容量、每条馈线余量各自共享。"""
    def __init__(self,inp):
        self.inp=inp;self.ids=list(inp['stations']);index={s:j for j,s in enumerate(self.ids)}
        self.feeders=list(inp['network']['feeders']);fi={f:j for j,f in enumerate(self.feeders)}
        self.edges=inp['network']['edges'];self.arcs=[]
        for k,e in enumerate(self.edges):
            for d in range(2 if e['bidirectional'] else 1):
                a,b=(e['a'],e['b']) if d==0 else (e['b'],e['a'])
                sa=index[inp['network']['feeders'][a]['station']];sb=index[inp['network']['feeders'][b]['station']]
                self.arcs.append((k,e,d,a,b,sa,sb))
        nf=len(self.feeders);ne=len(self.edges);ns=len(self.ids)
        offsets=[0,ne,ne+nf,ne+2*nf,ne+2*nf+ns,ne+2*nf+2*ns,ne+2*nf+3*ns]
        self.station_row=offsets[5];rr=[];cc=[];vv=[]
        for j,(k,e,d,a,b,sa,sb) in enumerate(self.arcs):
            entries=[(k,1),(offsets[1]+fi[a],1),(offsets[2]+fi[b],1),
                     (offsets[3]+sa,1),(offsets[5]+sa,-1),(offsets[5]+sb,1),
                     (offsets[6]+sa,1),(offsets[6]+sb,-1)]
            if e['existing']:entries.append((offsets[4]+sa,1))
            for row,value in entries:rr.append(row);cc.append(j);vv.append(value)
        self.matrix=coo_matrix((vv,(rr,cc)),shape=(offsets[6]+ns,len(self.arcs))).tocsr()

    def prepared(self,p,y,units,n,built):
        inp=self.inp;donor,receive=limits(inp,p,y)
        edgecap=np.array([e['capacity_mw'] if e['existing'] or e['id'] in built else 0. for e in self.edges])
        bounds=[(0,min(edgecap[k],donor[a]*e['source_section_fraction']) if e['existing'] else edgecap[k])
                for k,e,d,a,b,sa,sb in self.arcs]
        common=np.r_[edgecap,[donor[f] for f in self.feeders],[receive[f] for f in self.feeders],
                     np.maximum(p,0),[inp['existing_transfer_budget_mw'][s] for s in self.ids]]
        usable=inp['storage_usable_energy_fraction']
        bp=np.array([min(.1,.215*usable/max(1,inp['stations'][s]['forward_duration_h'])) for s in self.ids])*n
        bn=np.array([min(.1,.215*usable/max(1,inp['stations'][s]['reverse_duration_h'])) for s in self.ids])*n
        return common,bounds,PF*units.sum(axis=1),PF*units.max(axis=1),bp,bn

    def check(self,p,prepared,failed,with_deficit=True):
        common,bounds,full,largest,bp,bn=prepared
        available=full.copy()
        if failed>=0:available[failed]-=largest[failed]
        if np.all(p<=available+bp+1e-7) and np.all(-p<=available+bn+1e-7):
            return dict(verified=True,deficit_mw=0.,direct=True)
        rhs=np.r_[common,available+bp-p,available+bn+p]
        r=linprog(np.zeros(len(self.arcs)),A_ub=self.matrix,b_ub=rhs,bounds=bounds,method='highs')
        if r.success:
            return dict(verified=True,deficit_mw=0.,direct=False,
                        max_violation_mw=max(0.,float((self.matrix@r.x-rhs).max())))
        assert r.status==2, r.message
        if not with_deficit:return dict(verified=False,deficit_mw=None,direct=False)
        # 每站正反向承载约束加入共同的非负MW松弛，只用于定位容量缺口。
        ns=len(self.ids)
        slack=vstack([csr_matrix((self.station_row,ns)),-eye(ns),-eye(ns)],format='csr')
        relaxed=hstack([self.matrix,slack],format='csr')
        r=linprog(np.r_[np.zeros(len(self.arcs)),np.ones(ns)],A_ub=relaxed,b_ub=rhs,
                  bounds=bounds+[(0,None)]*ns,method='highs')
        assert r.success,r.message
        return dict(verified=False,deficit_mw=float(r.fun),direct=False,
                    station_deficits={s:float(v) for s,v in zip(self.ids,r.x[-ns:],strict=True) if v>1e-6})


def audit_first_year():
    REVIEW.mkdir(parents=True,exist_ok=True)
    details=[];summary=[]
    for region in ('city','pizhou'):
        root=OUT/region;inp=json.loads((root/'inputs.json').read_text());base,records=snapshots(region,inp)
        lp=FlowLP(inp);ids=list(inp['stations'])
        cases=[('压缩起点_2021',2021,None),('压缩设备直接用于首年_2022',2022,None),
               ('首版无下限首年方案_2022',2022,root/'no_floor')]
        for label,y,folder in cases:
            units=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]);n=np.zeros(len(ids));built=set()
            if folder:
                rows={r['station']:r for r in previous.rows(folder/'stations.csv') if int(r['year'])==y}
                units=np.array([[float(rows[s][f'unit_{k}_mva']) for k in (1,2,3)] for s in ids])
                n=np.array([int(rows[s]['storage_modules']) for s in ids])
                built={r['id'] for r in previous.rows(folder/'projects.csv') if int(r['year'])<=y}
            power=base*inp['annual_observed_peak_mw'][str(y)]/inp['initial_peak_mw']
            failures=[];count=0
            for h,p in enumerate(power):
                prepared=lp.prepared(p,y,units,n,built)
                for failed in range(-1,len(ids)):
                    result=lp.check(p,prepared,failed)
                    count+=1
                    if not result['verified']:
                        row=dict(地区=inp['region_name'],方案=label,年份=y,截面=h,
                                 原始小时=records[h]['source_hour'],工况=records[h]['roles'],
                                 故障站=ids[failed] if failed>=0 else '正常',承载缺口_MW=result['deficit_mw'],
                                 缺口站=json.dumps(result['station_deficits'],ensure_ascii=False))
                        details.append(row);failures.append(row)
            summary.append(dict(地区=inp['region_name'],方案=label,年份=y,容量_MVA=float(units.sum()),
                                地区负荷_MW=inp['annual_observed_peak_mw'][str(y)],
                                容载比=float(units.sum()/inp['annual_observed_peak_mw'][str(y)]),
                                静态截面数=len(power),检查工况数=count,失败工况数=len(failures),
                                最大承载缺口_MW=max((r['承载缺口_MW'] for r in failures),default=0.)))
            print('AUDITED',region,label,'failures',len(failures),'of',count,flush=True)
    write_csv(REVIEW/'压缩起点与首年承载力.csv',summary)
    write_csv(REVIEW/'首年承载力缺口.csv',details)
    dump(REVIEW/'首年承载力审查.json',dict(summary=summary,failures=details,
        meaning='缺口为静态网络承载约束的最小松弛量；非预计失负荷统计',
        profile_sha256={r:sha(PROFILES/f'{r}_stations.npz') for r in ('city','pizhou')}))


if __name__=='__main__':audit_first_year()
