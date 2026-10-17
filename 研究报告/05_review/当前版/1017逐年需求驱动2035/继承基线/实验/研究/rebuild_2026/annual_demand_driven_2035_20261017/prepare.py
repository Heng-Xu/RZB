"""逐年容量由当年需求决定；收资既有转供按固定MW封顶。"""
import copy
import json
import math
import shutil

import numpy as np

from ..annual_transfer_2035_20261017 import prepare as parent

base=parent.base;ROOT=parent.ROOT
RAW=ROOT/'研究报告/试算/20261017_逐年需求驱动2035'
PUBLIC=ROOT/'研究报告/01研究推荐/当前版/逐年需求驱动2035_20261017'
SOURCE=ROOT/'研究报告/数据来源/当前版/逐年需求驱动2035_20261017'
REVIEW=ROOT/'研究报告/05_review/当前版/1017逐年需求驱动2035'
REGIONS=parent.REGIONS
dump,write_csv,sha,forecasts=parent.dump,parent.write_csv,parent.sha,parent.forecasts


def prepare(region):
    for folder in (RAW,PUBLIC,SOURCE,REVIEW):folder.mkdir(parents=True,exist_ok=True)
    inp,powers=parent.load(region);inp=copy.deepcopy(inp);ids=list(inp['stations'])
    components=np.load(parent.RAW/region/'base_components.npz');demand=components['demand_proxy'];generation=components['generation_proxy']
    pv={2021:52.,2022:116.,2023:277.,2024:510.,2025:709.};historical=[]
    for y in range(2021,2026):
        factor=pv[y]/pv[2025];target=inp['annual_observed_peak_mw'][str(y)];lo,hi=0.,2.
        for _ in range(65):
            mid=(lo+hi)/2;peak=(demand.sum(axis=1)*mid-generation.sum(axis=1)*factor).max()
            if peak<target:lo=mid
            else:hi=mid
        scale=(lo+hi)/2;powers[y]=demand*scale-generation*factor
        assert abs(powers[y].sum(axis=1).max()-target)<1e-6
        historical.append(dict(year=y,pv_factor=factor,demand_factor=scale,planning_peak_mw=target))
    evidence={r['station']:r['transferable_mw'] for r in inp['station_transfer_evidence']}
    inp['existing_transfer_budget_by_year_mw']={str(y):evidence.copy() for y in range(2021,2036)}
    groups={}
    for fid,r in inp['network']['feeders'].items():
        if not r.get('equivalent_existing'):groups[fid]=1;continue
        sid=r['station'];j=ids.index(sid);block=max(1e-8,float(abs(powers[2021][:,j]).max())/inp['block_count'][sid])
        groups[fid]=max(1,math.ceil(evidence[sid]/(2*5*block)))
    for kind in ('transformer','storage','line'):inp['cost_factors'][kind]['2021']=1.
    inp.update(port_group_count=groups,new_transfer_fraction=.20,baseline_normal_blocks={},
        normal_transfer_policy='2021既有供区一次校准并全期固定；以后新增付费联络可安排固定供区调整',
        existing_transfer_policy='收资既有转供能力以原MW固定封顶，各年不随负荷自动放大；馈线共享、路径、受端及整区段约束同时校核',
        group_policy='EQ为聚合端口，按收资能力及基期区段峰值计算所代表馈线组数；每组5段/3端点/2邻站，非把全站聚合端口当单条馈线',
        annual_capacity_policy='只用当年负荷、光伏、共同容载比下限及正常/N1工况选择当年工程，继承上年设备；无2035规格下限、无5%建设上限、无终期清单或反推进度约束',
        historical_profile_policy='2021—2024用本年光伏相对2025比例回算，负荷系数以原年度正向峰值标定；2025逐点还原，2026—2035沿用原预测。历史为源荷模板回算，非历史实测曲线',
        scope='2021固定容量及既有供区可行性校准；2022—2035按当年需求逐年规划')
    out=RAW/region;out.mkdir(exist_ok=True);dump(out/'inputs.json',inp)
    np.savez_compressed(out/'hourly.npz',**{str(y):v for y,v in powers.items()})
    shutil.copy2(parent.RAW/region/'base_components.npz',out/'base_components.npz')
    write_csv(SOURCE/f'{region}_预测增长率.csv',forecasts(region))
    dump(SOURCE/f'{region}_来源与年度约束.json',dict(parent_input_sha256=sha(parent.RAW/region/'inputs.json'),
        hourly_sha256=sha(out/'hourly.npz'),existing_source='原站级转供收资证据，J列能力为全站上限，不向任何一条路径重复赋值',
        caveat='既有EQ连接仍为研究代理，端口分组是聚合模型修正；不冒称实际馈线竣工拓扑',
        historical=historical,policies={k:inp[k] for k in ('normal_transfer_policy','existing_transfer_policy','group_policy','annual_capacity_policy','historical_profile_policy')}))
    return inp,powers


def load(region):
    out=RAW/region
    if not (out/'inputs.json').exists():return prepare(region)
    inp=json.loads((out/'inputs.json').read_text())
    data=np.load(out/'hourly.npz');return inp,{int(y):data[y] for y in data.files}


if __name__=='__main__':
    for region in REGIONS:prepare(region)
