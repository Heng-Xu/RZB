"""后期仅扩容/扩容加联络的能力上界检验，保留上年储能。"""
import json

import numpy as np

from ..annual_demand_driven_2035_20261017.solver import solve
from . import model as m, prepare as p


def run():
    rows, sources = [], []
    for region, name in p.REGIONS.items():
        inp, powers = p.load(region)
        for y in range(2031, 2036):
            previous = json.loads((p.RAW/region/'elastic'/str(y)/'previous_assets.json').read_text())
            current = json.loads((p.RAW/region/'elastic'/str(y)/'adopted.json').read_text())
            old, oldn = np.array(previous['units']), np.array(previous['modules'])
            built, last = set(previous['built']), np.array(previous['last_replacement_year'])
            for mode in ('transformer_only', 'transformer_and_ties'):
                out = p.RAW/region/'late_probes'/str(y)/mode
                out.mkdir(parents=True, exist_ok=True)
                selected = {tuple(v) for v in current['selected_pairs']}
                for iteration in range(1, 21):
                    native, meta, one = m.build(inp,powers[y],y,'elastic',old,oldn,built,last,selected)
                    # 弹性容量上界为物理上界，增加可用设备只扩大静态可行域。
                    # 全部可更换位置取可行最大值，保留原位置大小顺序约束。
                    for sid in inp['stations']:
                        ceiling = float('inf')
                        for slot in (1, 0):
                            choices = [(r,v) for (s,k,yy,r),v in meta['x'].items()
                                       if s==sid and k==slot and native.upper_bounds[v]>.5 and r<=ceiling+1e-8]
                            ceiling = max(r for r,v in choices)
                            for (s,k,yy,r),v in meta['x'].items():
                                if s==sid and k==slot:
                                    native.lower_bounds[v] = native.upper_bounds[v] = float(abs(r-ceiling)<1e-8)
                    for v in meta['third'].values():
                        native.lower_bounds[v] = native.upper_bounds[v] = 1.
                    for v in meta['modules'].values():
                        native.upper_bounds[v] = native.lower_bounds[v]
                    if mode=='transformer_only':
                        for (eid, yy),v in meta['edgevars'].items():
                            native.lower_bounds[v] = native.upper_bounds[v] = float(eid in built)
                    # 开放新线时保留候选二元选择，不强制全部建设。
                    # 全部建齐会违反站内可用间隔约束，不能作为能力上界。
                    native.costs = [0.]*len(native.costs)
                    z, solver = solve(native,out,f'feasibility_{iteration:02}',20.,.001,one,meta,out/'no_warm')
                    if solver['proven_infeasible']:
                        status = '不可行'
                        check = None
                        break
                    if not solver.get('feasible_incumbent'):
                        raise RuntimeError(('后期能力检验未决，不将限时当不可行',region,y,mode,solver))
                    u,n,bs,normal,extra = m.layout(inp,z,meta)
                    check,bad = m.verify(inp,powers[y],y,u,n,bs,normal,extra)
                    if not bad:
                        status = '可行'
                        break
                    assert bad-selected
                    selected |= bad
                else:
                    raise RuntimeError(('后期能力检验全年校核未闭合',region,y,mode))
                result = dict(verified=True,region=region,year=y,mode=mode,status=status,solver=solver,check=check,
                    selected_pairs=sorted(selected),previous_assets_sha256=p.sha(p.RAW/region/'elastic'/str(y)/'previous_assets.json'),
                    scope='继承本轮上年资产，保持上年储能不变，主变取四年间隔允许的最大规格；第二种另开放全部候选新线。仅检验能力，不比较此极限配置费用。')
                p.dump(out/'result.json',result)
                if mode=='transformer_and_ties' and status=='不可行':
                    fixed_result = json.loads((out.parent/'transformer_only/result.json').read_text())
                    assert fixed_result['status']=='不可行', '开放候选不能使固定已有线路的可行配置失效'
                rows.append(dict(地区=name,年份=y,检验='只新增主变' if mode=='transformer_only' else '新增主变及联络',
                    新增储能_MW=0.,结论=status,全年可行校核=check is not None,
                    求解状态=solver['status'],原始记录=str((out/'result.json').relative_to(p.ROOT))))
                sources.append(dict(path=str((out/'result.json').relative_to(p.ROOT)),sha256=p.sha(out/'result.json')))
                print('LATE_PROBE',name,y,mode,status,flush=True)
    p.write_csv(p.REVIEW/'后期停止新增储能能力检验.csv',rows)
    p.dump(p.REVIEW/'后期能力检验.json',dict(verified=True,rows=rows,sources=sources,
        caveat='各年度以上一年度本轮采用资产为起点；单年反事实，非一条连续无新增储能链。可行表示存在配置，非采用方案或费用最优。'))


if __name__ == '__main__':
    run()
