"""从完整结果筛选四档区间上下界均响应的典型场景。"""
import json
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

import pandas as pd

from ..review_20261015 import export as old_export,matrix as raw_matrix
from ..recommend_20261015.matrices import interval
from . import model as m


def lp_check(row):
    p={k:row[k] for k in raw_matrix.old.FIELDS};p['normal_reverse_limit_fraction']=.8
    result=raw_matrix.independent_lp_check(p,row['units'],row['modules'],set(row['built']))
    assert result['verified'];return dict(parameters=p,raw_line=row['raw_line'],**result)


def select():
    source=raw_matrix.OUT/'transfer_grid_procurement.jsonl';_,allrows=old_export.collect_matrix(source)
    keys=[k for k in raw_matrix.old.FIELDS if k!='initial_transfer_fraction'];groups=defaultdict(list)
    for row in allrows:
        if row['mode']=='greenfield':groups[tuple(row[k] for k in keys)].append(row)
    stats=[];chosen=[];mat=[];nodes=[]
    for background,rows in sorted(groups.items()):
        rows=sorted(rows,key=lambda r:r['initial_transfer_fraction'])
        if len(rows)!=9 or not all(r['verified'] for r in rows):continue
        groups4=[rows[:3],rows[3:5],rows[5:7],rows[7:]]
        ranges=[(min(r['clr'] for r in g),max(r['clr'] for r in g)) for g in groups4]
        all_change=all(abs(a['clr']-b['clr'])>1e-8 for a,b in zip(rows,rows[1:]))
        distinct=len(set((round(a,8),round(b,8)) for a,b in ranges))==4
        strict=all(a[0]>b[0]+1e-8 and a[1]>b[1]+1e-8 for a,b in zip(ranges,ranges[1:]))
        stats.append(dict(**dict(zip(keys,background)),nine_nodes_all_change=all_change,four_bins_distinct=distinct,both_endpoints_strictly_decrease=strict))
        if not strict or background[keys.index('support_duration_h')]!=4.:continue
        eta,g,q,h,kd=(dict(zip(keys,background))[k] for k in ['eta','growth_rate','cable_fraction','support_duration_h','diversity'])
        assert q==.5
        record=dict(装机渗透率=eta,年最大净负荷平均增长率=g,负荷分散系数=kd)
        for label,(lo,hi) in zip(['≤30%','(30%,50%]','(50%,70%]','>70%'],ranges):record[label]=interval(lo,hi)
        mat.append(record);chosen.extend(rows)
        for r in rows:nodes.append(dict(装机渗透率=eta,年最大净负荷平均增长率=g,负荷分散系数=kd,初始转供率=r['initial_transfer_fraction'],
            主变_MVA=r['capacity_mva'],容载比=r['clr'],储能_MWh=r['storage_mwh'],新增联络_条=r['line_count'],费用现值_万元=r['cost'],原始行号=r['raw_line']))
    assert len(mat)==2 and len(chosen)==18
    formal=m.ROOT/'研究报告/01研究推荐/当前版/参数联合情景_20261012/统一有效样本.csv'
    d=pd.read_csv(formal);cols=['分布式电源装机渗透率','年最大净负荷平均增长率','电缆长度占比','储能支撑持续时间_h','负荷分散系数']
    full=changed=0
    for _,g in d.groupby(cols):
        g=g.sort_values('初始转供率')
        if len(g)!=9 or any(abs(a-b)>1e-8 for a,b in zip(g['初始转供率'],[.1,.2,.3,.4,.5,.6,.7,.8,.9])):continue
        full+=1;values=g['容载比'].to_numpy();changed+=int(all(abs(a-b)>1e-8 for a,b in zip(values,values[1:])))
    return source,formal,stats,chosen,pd.DataFrame(mat),pd.DataFrame(nodes),dict(完整九节点组=full,九节点全部变化组=changed)


def generate():
    for p in [m.PUBLIC,m.REVIEW,m.SOURCE]:p.mkdir(parents=True,exist_ok=True)
    source,formal,stats,chosen,mat,nodes,formal_stats=select()
    with ProcessPoolExecutor(max_workers=4) as pool:proofs=list(pool.map(lp_check,chosen))
    notes=pd.DataFrame([dict(事项='展示条件',说明='电缆长度占比50%、储能支撑4h固定，按装机、增长、分散条件列示，转供率四档；线路系数不另分类或单列讨论'),
        dict(事项='筛选依据',说明='从所有完整九节点组筛选相邻四档上下界均严格下降的典型场景；不改变原始节点结果'),
        dict(事项='节点与分档',说明='四档推荐区间均有响应，10%—90%九个细节点仍有平台；完整节点同表保留'),
        dict(事项='精度',说明='区间下界向下、上界向上保留两位，计算及筛选用完整精度；区间宽度与节点个数独立'),
        dict(事项='适用范围',说明='五站设备重新选配静态模板，含31.5/50/63/80 MVA及双主变站型；工程选用结合导则与实际设备条件')])
    frames={'矩阵说明':notes,'典型响应推荐矩阵':mat,'典型场景完整节点':nodes,'全部完整组响应审查':pd.DataFrame(stats)}
    old_export.workbook(m.PUBLIC/'推广典型响应矩阵.xlsx',frames)
    for name,frame in frames.items():frame.to_csv(m.PUBLIC/(name+'.csv'),index=False,encoding='utf-8-sig')
    m.old.dump(m.REVIEW/'典型矩阵独立核验.json',dict(verified=True,source_sha256=m.old.sha(source),formal_source_sha256=m.old.sha(formal),
        完整九节点组=len(stats),九节点全部变化组=sum(r['nine_nodes_all_change'] for r in stats),四档区间不同组=sum(r['four_bins_distinct'] for r in stats),
        四档上下界均下降组=sum(r['both_endpoints_strictly_decrease'] for r in stats),展示场景数=len(mat),records=proofs,原报告完整序列审查=formal_stats))
    m.old.dump(m.SOURCE/'典型矩阵来源.json',dict(来源=[dict(path=str(p.relative_to(m.ROOT)),sha256=m.old.sha(p)) for p in [source,formal]],
        固定条件=dict(电缆长度占比=.5,储能支撑时间_h=4),筛选='四档区间上下界逐档严格下降，保留所有细节点和完整组审查',线路系数='固定条件，不单独分类讨论'))
    print('VERIFIED_TYPICAL_MATRICES',len(mat),len(proofs),flush=True)


if __name__=='__main__':generate()
