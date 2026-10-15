"""五参数完整序列与推荐区间重复审查，容量、设备和区间分别统计。"""
import hashlib
import itertools
import json
import math
from collections import defaultdict

import numpy as np
import pandas as pd

from ..review_20261015 import export as previous_export
from ..review_20261015 import matrix as previous_matrix
from .cases import RAW,PUBLIC,REVIEW,SOURCE,ROOT,prior

FIELDS=previous_matrix.old.FIELDS
FIVE=[f for f in FIELDS if f!='support_duration_h']
LABEL=dict(zip(FIELDS,['装机渗透率','年最大净负荷平均增长率','电缆长度占比','初始转供率','储能支撑持续时间','负荷分散系数']))


def signature(row):
    return json.dumps([row['units'],row['modules'],sorted(row['built'])],sort_keys=True)


def cost_bounds_check():
    old=previous_export.records(ROOT/'研究报告/试算/20261012_参数联合情景锁定/统一原始求解记录.jsonl')
    _,new=previous_export.collect_matrix(previous_matrix.OUT/'transfer_grid_procurement.jsonl')
    sources=[('现报告',old)]+[(mode,[r for r in new if r['mode']==mode]) for mode in ['stock','greenfield']]
    checks=[]
    for name,rows in sources:
        for f,direction in [('initial_transfer_fraction',-1),('cable_fraction',1)]:
            groups=defaultdict(list)
            for row in rows:groups[tuple(row[k] for k in FIELDS if k!=f)].append(row)
            count=0;maximum=0.
            for group in groups.values():
                group.sort(key=lambda r:r[f])
                for a,b in zip(group,group[1:]):
                    if a['verified'] and f=='initial_transfer_fraction':assert b['status']!='Infeasible'
                    if not a['verified'] or not b['verified']:continue
                    count+=1
                    delta=b['cost_lower']-a['cost'] if direction==-1 else a['cost_lower']-b['cost']
                    assert delta<1e-4,(name,f,delta)
                    maximum=max(maximum,delta)
            checks.append(dict(dataset=name,parameter=f,pairs=count,max_bound_contradiction=maximum,verified=True))
    return dict(verified=True,records=checks)


def summarize_sequences(rows,version):
    d=pd.DataFrame([{k:r.get(k) for k in [*FIELDS,'verified','capacity_mva','clr','cost']} for r in rows])
    d['configuration']=[signature(r) if r['verified'] else '' for r in rows]
    summary=[];details=[]
    for f in FIVE:
        fixed=[k for k in FIELDS if k!=f];groups=0;constant_capacity=0;constant_clr=0;constant_all=0
        pairs=0;same_capacity=0;same_clr=0;same_configuration=0;only_cost=0
        for background,g in d.sort_values(f).groupby(fixed,sort=False):
            valid=g[g.verified]
            if len(valid)<2:continue
            groups+=1
            constant_capacity+=int(np.ptp(valid.capacity_mva)<1e-7)
            constant_clr+=int(np.ptp(valid.clr)<1e-9)
            constant_all+=int(valid.configuration.nunique()==1)
            records=g.to_dict('records')
            for a,b in zip(records,records[1:]):
                if not a['verified'] or not b['verified']:continue
                pairs+=1;sc=abs(a['capacity_mva']-b['capacity_mva'])<1e-7;sr=abs(a['clr']-b['clr'])<1e-9
                sk=a['configuration']==b['configuration'];so=sk and abs(a['cost']-b['cost'])>1e-5
                same_capacity+=int(sc);same_clr+=int(sr);same_configuration+=int(sk);only_cost+=int(so)
                details.append(dict(数据集=version,参数=LABEL[f],参数字段=f,起点=a[f],终点=b[f],
                    **{k:a[k] for k in fixed},容量不变=sc,容载比不变=sr,设备全不变=sk,仅费用改变=so,
                    起点容量_MVA=a['capacity_mva'],终点容量_MVA=b['capacity_mva'],
                    起点容载比=a['clr'],终点容载比=b['clr'],费用变化_万元=b['cost']-a['cost']))
        summary.append(dict(数据集=version,参数=LABEL[f],受控组数=groups,整组容量不变占比=constant_capacity/groups,
            整组容载比不变占比=constant_clr/groups,整组设备不变占比=constant_all/groups,
            有效相邻对数=pairs,相邻容量不变占比=same_capacity/pairs,相邻容载比不变占比=same_clr/pairs,
            相邻设备全不变占比=same_configuration/pairs,仅费用改变占比=only_cost/pairs))
    return pd.DataFrame(summary),pd.DataFrame(details)


def old_cells(rows):
    d=pd.DataFrame([r for r in rows if r['verified']]);cuts={'eta':[1,2],'growth_rate':[.02,.04,.07],
        'cable_fraction':[.1,.3],'initial_transfer_fraction':[.3,.5,.7]}
    for f,values in cuts.items():d['b_'+f]=d[f].map(lambda x:sum(x>v+1e-9 for v in values))
    fields=['b_cable_fraction','diversity','b_growth_rate','b_eta','b_initial_transfer_fraction']
    cells=[]
    for background,g in d.groupby(fields):
        lo,hi=float(g.clr.min()),float(g.clr.max())
        cells.append(dict(zip(['cable','diversity','growth','eta','transfer'],background),lower=lo,upper=hi,
            display=f'{math.floor((lo+1e-10)*100)/100:.2f}～{math.ceil((hi-1e-10)*100)/100:.2f}',samples=len(g)))
    assert len(cells)==432 and sum(r['samples'] for r in cells)==32112
    current=json.loads((ROOT/'研究报告/05_review/当前版/1013正文与矩阵修订/定值展示矩阵.json').read_text())
    actual=current if isinstance(current,list) else current['单元']
    bykey={tuple(r[k] for k in ['cable','diversity','growth','eta','transfer']):r for r in cells}
    for row in actual:
        match=bykey[tuple(row[k] for k in ['电缆档','负荷分散系数','增长档','渗透率档','转供档'])]
        assert match['display']==row['展示区间']
        assert abs(match['lower']-row['下界'])<1e-9 and abs(match['upper']-row['上界'])<1e-9
    return pd.DataFrame(cells)


def cell_pairs(cells,version):
    summary=[];details=[];dimensions=dict(zip(['eta','growth','cable','transfer','diversity'],FIVE))
    for f in dimensions:
        fixed=[k for k in dimensions if k!=f];pairs=exact=rounded=overlap=0
        for _,g in cells.groupby(fixed):
            rows=g.sort_values(f).to_dict('records')
            for a,b in zip(rows,rows[1:]):
                pairs+=1;eq=abs(a['lower']-b['lower'])<1e-9 and abs(a['upper']-b['upper'])<1e-9
                er=a['display']==b['display'];eo=max(a['lower'],b['lower'])<=min(a['upper'],b['upper'])+1e-9
                exact+=eq;rounded+=er;overlap+=eo
                details.append(dict(数据集=version,参数=LABEL[dimensions[f]],分档起=a[f],分档止=b[f],
                    **{k:a[k] for k in fixed},起区间=a['display'],止区间=b['display'],原始上下界全相同=eq,
                    展示区间相同=er,两区间有交集=eo))
        summary.append(dict(数据集=version,参数=LABEL[dimensions[f]],相邻区间对数=pairs,
            原始上下界相同占比=exact/pairs,展示区间相同占比=rounded/pairs,区间有交集占比=overlap/pairs,
            仅显示精度产生相同对数=rounded-exact))
    return pd.DataFrame(summary),pd.DataFrame(details)


def main():
    for p in (RAW,PUBLIC,REVIEW,SOURCE):p.mkdir(parents=True,exist_ok=True)
    oldpath=ROOT/'研究报告/试算/20261012_参数联合情景锁定/统一原始求解记录.jsonl'
    old=previous_export.records(oldpath);_,new=previous_export.collect_matrix(previous_matrix.OUT/'transfer_grid_procurement.jsonl')
    sources=[dict(path=str(p.relative_to(ROOT)),sha256=prior.sha(p)) for p in [oldpath,previous_matrix.OUT/'transfer_grid_procurement.jsonl']]
    seqs=[];detail=[];ranges=[];rdetail=[];floors=[];allcells=[]
    for name,records in [('现报告存量模型',old),('本轮存量改造',[r for r in new if r['mode']=='stock']),
                         ('本轮全部重新选配',[r for r in new if r['mode']=='greenfield'])]:
        a,b=summarize_sequences(records,name);seqs.append(a);detail.append(b)
        if name=='现报告存量模型':cells=old_cells(records)
        else:
            _,_,_,c,_=previous_export.matrix_data(records)
            cells=c.rename(columns={'电缆长度占比':'cable','负荷分散系数':'diversity','年增长率节点':'growth',
                '装机渗透率节点':'eta','转供分档':'transfer','容载比下界':'lower','容载比上界':'upper'})
            cells['display']=[f'{math.floor((r.lower+1e-10)*100)/100:.2f}～{math.ceil((r.upper-1e-10)*100)/100:.2f}' for r in cells.itertuples()]
        cells=cells.copy();cells['数据集']=name;allcells.append(cells)
        a,b=cell_pairs(cells,name);ranges.append(a);rdetail.append(b)
        valid=[r for r in records if r['verified']];minimum=315. if '全部重新' in name else 500.
        floors.append(dict(数据集=name,设备组合容量下限_MVA=minimum,有效节点数=len(valid),
            命中地区容量下限节点数=sum(abs(r['capacity_mva']-minimum)<1e-7 for r in valid),
            命中地区容量下限占比=sum(abs(r['capacity_mva']-minimum)<1e-7 for r in valid)/len(valid),
            至少一台主变为最小档占比=sum(any(abs(v-(31.5 if minimum==315 else 50))<1e-8 for u in r['units'] for v in u[:2]) for r in valid)/len(valid)))
    frames={'五参数完整序列统计':pd.concat(seqs),'五参数推荐区间统计':pd.concat(ranges),'容量下限命中':pd.DataFrame(floors),
        '相邻节点明细':pd.concat(detail),'相邻区间明细':pd.concat(rdetail),'推荐单元原始上下界':pd.concat(allcells)}
    for name,d in frames.items():d.to_csv(PUBLIC/(name+'.csv'),index=False,encoding='utf-8-sig')
    previous_export.workbook(PUBLIC/'五参数平台完整审查.xlsx',{k:v for k,v in frames.items() if k!='相邻节点明细'})
    prior.dump(SOURCE/'推广原始来源.json',sources)
    prior.dump(REVIEW/'转供及价格费用边界核验.json',cost_bounds_check())
    prior.dump(REVIEW/'五参数平台核验.json',dict(verified=True,sources=sources,sequence_rows=len(frames['相邻节点明细']),
        cell_pairs=len(frames['相邻区间明细']),statistics=frames['五参数完整序列统计'].to_dict('records'),
        intervals=frames['五参数推荐区间统计'].to_dict('records'),floors=floors))
    print(frames['五参数完整序列统计'].to_string(index=False));print(frames['五参数推荐区间统计'].to_string(index=False))


if __name__=='__main__':main()
