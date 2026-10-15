"""同条件五参数响应与分时长矩阵，合并真正相同的设备结果。"""
import json
import math
from collections import defaultdict

import pandas as pd

from ..review_20261015 import matrix as old_matrix,export as old_export
from ..review_20261015 import cases as old
from ..review_20261015_followup import matrix_audit
from . import model as m

LABEL=matrix_audit.LABEL
FIELDS=matrix_audit.FIELDS
FIVE=matrix_audit.FIVE


def interval(lo,hi):return f'{math.floor((lo+1e-10)*100)/100:.2f}～{math.ceil((hi-1e-10)*100)/100:.2f}'


def generate():
    for p in (m.PUBLIC,m.REVIEW,m.SOURCE):p.mkdir(parents=True,exist_ok=True)
    raw,records=old_export.collect_matrix(old_matrix.OUT/'transfer_grid_procurement.jsonl')
    rows=[r for r in records if r['mode']=='greenfield'];assert len(rows)==2916
    summary,adjacent=matrix_audit.summarize_sequences(rows,'主变重新选配')
    oldrows=[r for r in records if r['mode']=='stock'];oldsummary,_=matrix_audit.summarize_sequences(oldrows,'同节点存量改造')
    summary=pd.concat([oldsummary,summary],ignore_index=True)
    v=pd.DataFrame([{k:r[k] for k in FIELDS}|dict(容量=r['capacity_mva'],容载比=r['clr'],储能=r['storage_mwh'],
        线路=r['line_count'],费用=r['cost'],间隙=r['relative_gap']) for r in rows if r['verified']])
    conditions=[];matrices={};cells=[]
    for (q,kd,h),group in v.groupby(['cable_fraction','diversity','support_duration_h']):
        output=[]
        for eta in [.5,1.5,2.5]:
            for growth in [0.,.04,.055,.08]:
                row={'装机渗透率':eta,'年最大净负荷平均增长率':growth}
                subset=group[(group.eta==eta)&(group.growth_rate==growth)]
                for lo,hi,label in [(0.,.3,'≤30%'),(.3,.5,'(30%,50%]'),(.5,.7,'(50%,70%]'),(.7,1.,'>70%')]:
                    sub=subset[(subset.initial_transfer_fraction>lo+1e-9)&(subset.initial_transfer_fraction<=hi+1e-9)]
                    row[label]='无有效节点' if sub.empty else interval(sub['容载比'].min(),sub['容载比'].max())
                    cells.append(dict(电缆长度占比=q,负荷分散系数=kd,储能支撑持续时间_h=h,装机渗透率=eta,
                        年最大净负荷平均增长率=growth,转供分档=label,有效节点数=len(sub),
                        容载比下界=None if sub.empty else sub['容载比'].min(),容载比上界=None if sub.empty else sub['容载比'].max(),
                        展示区间=row[label]))
                output.append(row)
        matrices[f'电缆{q:.0%}_KD{kd:.2f}_{h:g}h']=pd.DataFrame(output)
    # 合并仅限相邻转供节点的全部设备、功率和费用一致，保留所有原始节点。
    groups=defaultdict(list)
    for r in rows:groups[tuple(r[k] for k in FIELDS if k!='initial_transfer_fraction')].append(r)
    merged=[]
    for background,group in sorted(groups.items()):
        current=None
        for r in sorted(group,key=lambda x:x['initial_transfer_fraction']):
            sig=matrix_audit.signature(r) if r['verified'] else r['status']
            if current and current['_signature']==sig and (not r['verified'] or abs(current['费用现值_万元']-r['cost'])<1e-4):
                current['转供率上节点']=r['initial_transfer_fraction'];current['合并节点数']+=1;continue
            if current:merged.append({k:v for k,v in current.items() if not k.startswith('_')})
            current={LABEL[k]:r[k] for k in FIELDS if k!='initial_transfer_fraction'}
            current.update(转供率下节点=r['initial_transfer_fraction'],转供率上节点=r['initial_transfer_fraction'],合并节点数=1,
                容载比=r.get('clr'),主变_MVA=r.get('capacity_mva'),储能_MWh=r.get('storage_mwh'),
                新增联络_条=r.get('line_count'),费用现值_万元=r.get('cost'),状态='有效' if r['verified'] else r['status'],_signature=sig)
        if current:merged.append({k:v for k,v in current.items() if not k.startswith('_')})
    frames={'五参数响应统计':summary,'同配置节点合并':pd.DataFrame(merged),'分时长区间明细':pd.DataFrame(cells)}
    base=dict(eta=1.5,growth_rate=.04,cable_fraction=.1,initial_transfer_fraction=.4,support_duration_h=4.,diversity=1.1)
    samples=[]
    for field in FIVE:
        selected=[r for r in rows if all(abs(r[k]-value)<1e-9 for k,value in base.items() if k!=field)]
        for r in sorted(selected,key=lambda x:x[field]):
            samples.append(dict(参数=LABEL[field],参数值=r[field],状态='有效' if r['verified'] else r['status'],
                主变_MVA=r.get('capacity_mva'),容载比=r.get('clr'),储能_MWh=r.get('storage_mwh'),
                新增联络_条=r.get('line_count'),费用现值_万元=r.get('cost'),求解间隙=r.get('relative_gap')))
    frames['五参数固定背景序列']=pd.DataFrame(samples)
    notes=pd.DataFrame([dict(事项='节点范围',说明='装机0.5/1.5/2.5，增长0/4/5.5/8%，电缆10/30/50%，转供10%—90%，时长2/4/6h，分散1/1.10/1.15；2916个新配节点'),
        dict(事项='主变规格',说明='31.5/50/63/80 MVA；五站每站至少双主变，组合下限315 MVA，为设备菜单和站型假设'),
        dict(事项='矩阵条件',说明='每张表固定电缆、分散和支撑时长，保留实际装机/增长节点；转供分档汇总有效离散节点，不跨时长取包络'),
        dict(事项='平台说明',说明='离散设备档位、局部供电约束及费用门槛共同形成平台。相同设备且费用相同的相邻转供节点合并，其他变化保留'),
        dict(事项='电缆作用',说明='当前占比只映射线路投资价格。收资三类电缆占比线路的允许电流中位数均595A，不凭占比人为增加输送容量'),
        dict(事项='结果范围',说明='静态正反向/N-1及费用配置结果；有限节点低于导则建议范围时，结合地区条件选择，未作为全地区统一指标'),
        dict(事项='固定背景',说明='装机1.5、增长4%、电缆10%、转供40%、时长4h、分散1.10；每次仅改变一个参数')])
    old_export.workbook(m.PUBLIC/'五参数推荐矩阵与响应.xlsx',{'说明':notes,**frames,**matrices})
    for name,df in {**frames,**matrices}.items():df.to_csv(m.PUBLIC/(name+'.csv'),index=False,encoding='utf-8-sig')
    source=old_matrix.OUT/'transfer_grid_procurement.jsonl'
    old.dump(m.SOURCE/'矩阵来源及设备条件.json',dict(path=str(source.relative_to(m.ROOT)),sha256=old.sha(source),
        原始节点数=len(rows),有效节点数=sum(r['verified'] for r in rows),候选规格=[31.5,50,63,80],组合下限_MVA=315,
        作用='有限节点矩阵按2/4/6小时分别展示；有效结果不改写'))
    old.dump(m.REVIEW/'矩阵归纳核验.json',dict(verified=True,total_nodes=len(rows),valid_nodes=sum(r['verified'] for r in rows),
        matrix_sheets=len(matrices),cells=len(cells),merged_rows=len(merged),represented_nodes=sum(r['合并节点数'] for r in merged),
        stats=summary.to_dict('records'),source_sha256=old.sha(source)))
    assert sum(r['合并节点数'] for r in merged)==2916
    return frames,matrices,rows


if __name__=='__main__':
    frames,matrices,rows=generate();print('MATRICES_DONE',len(matrices),len(rows),flush=True)
