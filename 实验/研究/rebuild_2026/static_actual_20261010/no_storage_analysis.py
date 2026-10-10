"""刚性无储能专题：扩容+联络、固定基期及固定刚性布局三种边界。

原推荐输入、约束和成果不改。全部边免费可用的检查只用于不可行旁证。
"""
import argparse
import copy
import itertools
import json

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import maximum_flow

from .run import OUT, ROOT, PF, rows, dump, write_csv, sha, load_scenes, build, network, actual_limits
from ..network_case_20261010.solver import solve

DEST=OUT/'刚性无储能专项分析'
VARIANTS={'expansion_ties':'主变扩容及联络共同优化',
          'baseline_ties':'主变固定为仿真起点，仅优化联络',
          'rigid_layout_ties':'主变固定为刚性含储能候选布局，仅优化联络'}


def fixed_units(inp, region, variant, year):
    if variant=='baseline_ties':
        return np.array([list(s['initial_units'])+[0.] for s in inp['stations'].values()])
    data={r['station']:r for r in rows(OUT/region/'rigid_storage/stations.csv') if int(r['year'])==year}
    return np.array([[float(data[s][f'unit_{k}_mva']) for k in (1,2,3)] for s in inp['stations']])


def solve_variant(region,variant):
    inp=json.loads((OUT/region/'inputs.json').read_text());scenes=load_scenes(OUT/region,inp)
    directory=DEST/region/variant;directory.mkdir(parents=True,exist_ok=True)
    network.limits=actual_limits
    m,meta=build(inp,scenes,'rigid_no_storage')
    if variant!='expansion_ties':
        idx={s:j for j,s in enumerate(inp['stations'])}
        units={y:fixed_units(inp,region,variant,y) for y in inp['years']}
        for (sid,slot,y,r),v in meta['x'].items():
            value=float(abs(units[y][idx[sid],slot]-r)<1e-7)
            m.lower_bounds[v]=value;m.upper_bounds[v]=value
        for (sid,y),v in meta['third'].items():
            value=units[y][idx[sid],2]/50
            m.lower_bounds[v]=value;m.upper_bounds[v]=value
    z,result=solve(m,directory,'no_storage',90,.01,inp,meta,directory/'no_warm_start')
    sources={str((OUT/region/'inputs.json').relative_to(ROOT)):sha(OUT/region/'inputs.json'),
             str((OUT/region/'静态工况.csv').relative_to(ROOT)):sha(OUT/region/'静态工况.csv')}
    if variant=='rigid_layout_ties':
        sources[str((OUT/region/'rigid_storage/stations.csv').relative_to(ROOT))]=sha(OUT/region/'rigid_storage/stations.csv')
    dump(directory/'summary.json',dict(region=region,variant=variant,description=VARIANTS[variant],solver=result,sources=sources,
                                      scope='原模型完整四年静态约束，储能强制为零；不可行时不报告费用或工程数量'))


def optimistic_transfer(inp,p,y,j,sign):
    built={e['id'] for e in inp['network']['edges']}
    n,arcs=network.network_arcs(inp,p,y,built)
    # 汇点/源点连接其他站，忽略其主变容量限制，形成转供能力上界。
    arcs.extend((k,n,1000.) if sign==1 else (n,k,1000.) for k in range(len(inp['stations'])) if k!=j)
    rr,cc,vv=zip(*arcs)
    graph=coo_matrix((np.ceil(np.array(vv)*network.SCALE).astype(np.int64),(rr,cc)),shape=(n+1,n+1)).tocsr()
    answer=maximum_flow(graph,j,n) if sign==1 else maximum_flow(graph,n,j)
    return float(answer.flow_value/network.SCALE)


def diagnose():
    DEST.mkdir(parents=True,exist_ok=True);network.limits=actual_limits
    station=[];fixed=[];annual=[]
    for region in ('city','pizhou'):
        inp=json.loads((OUT/region/'inputs.json').read_text());scenes=load_scenes(OUT/region,inp)
        ids=list(inp['stations']);rolling_upper=inp['initial_capacity_mva']
        for y,power in scenes.items():
            minimum=[]
            allbuilt={e['id'] for e in inp['network']['edges']}
            for variant in ('baseline_ties','rigid_layout_ties'):
                u=fixed_units(inp,region,variant,y)
                c,violations=network.check_year(inp,power,y,u,np.zeros(len(ids)),allbuilt)
                h,f=c['worst'] if c['worst'] is not None else (None,None)
                fixed.append({'地区':inp['region_name'],'年份':y,'试验':VARIANTS[variant],
                              '固定容量_MVA':float(u.sum()),'全部候选免费开放仍不满足':bool(violations),
                              '最大网络平衡缺口_MW':c['max_network_deficit_mw'],
                              '最不利工况':'区县正向峰值' if h==0 else ('区县最低净负荷' if h==1 else ''),
                              '最不利N-1站':ids[f] if f is not None and f>=0 else '正常',
                              '违反工况数':c['violating_pairs']})
            for j,sid in enumerate(ids):
                s=inp['stations'][sid];original=list(s['initial_units'])+[0.]
                surviving=PF*(sum(original)-max(original))
                options=[]
                for h,p in enumerate(power):
                    for sign in (1,-1):
                        transfer=optimistic_transfer(inp,p,y,j,sign)
                        need=max(0.,sign*p[j]-transfer)
                        options.append((need,h,sign,float(p[j]),transfer))
                need,h,sign,p,transfer=max(options)
                ratings=[sorted({old,*[r for r in (31.5,50,63,80) if r>=old]}) for old in s['initial_units']]
                feasible=[(a+b+t,a,b,t) for a,b,t in itertools.product(*ratings,(0,50) if s['allow_third'] else (0,))
                          if a<=b and PF*(a+b+t-max(a,b,t))>=need-1e-5]
                best=min(feasible) if feasible else None
                minimum.append(best[0] if best else None)
                station.append({'地区':inp['region_name'],'年份':y,'站点':sid,'基期容量_MVA':sum(original),
                                '基期主变组合':'+'.join(f'{v:g}' for v in original if v),
                                '最不利工况':'区县正向峰值' if h==0 else '区县最低净负荷',
                                '受限方向':'正向' if sign==1 else '反向','原工况净负荷_MW':p,
                                '宽松转供能力上界_MW':transfer,'必要剩余承载力_MW':need,
                                '基期N-1剩余承载力_MW':surviving,'基期最少承载缺口_MW':max(0.,need-surviving),
                                '必要容量下界_MVA':best[0] if best else None,
                                '必要容量净增下界_MVA':best[0]-sum(original) if best else None,
                                '下界对应主变组合':'+'.join(f'{v:g}' for v in best[1:] if v) if best else '无候选'})
            total=sum(minimum) if all(v is not None for v in minimum) else None
            rolling_upper=max(rolling_upper,2*inp['annual_observed_peak_mw'][str(y)])
            annual.append({'地区':inp['region_name'],'年份':y,'实际最大负荷_MW':inp['annual_observed_peak_mw'][str(y)],
                           '刚性宽松容量上界_MVA':rolling_upper,'无储能必要容量下界_MVA':total,
                           '超出上界_MVA':max(0.,total-rolling_upper) if total else None,
                           '单年必要条件可独立证明无解':total is None or total>rolling_upper+1e-5})
    write_csv(DEST/'各站必要承载能力.csv',station);write_csv(DEST/'逐年容量必要条件.csv',annual)
    write_csv(DEST/'固定主变全部候选开放.csv',fixed)
    dump(DEST/'独立诊断.json',{'annual':annual,'fixed_layout_checks':fixed,
                              'relaxation':'全部候选免费投运，放松备用间隔和新增费用；站容量下界还放松邻站主变限制。',
                              'meaning':'缺口为静态约束余量，不是预计失负荷；容量下界对应组合不构成可实施方案。'})
    print(json.dumps(annual,ensure_ascii=False,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--region',choices=['city','pizhou']);p.add_argument('--variant',choices=list(VARIANTS));p.add_argument('--diagnose',action='store_true');a=p.parse_args()
    if a.region and a.variant:solve_variant(a.region,a.variant)
    if a.diagnose:diagnose()
