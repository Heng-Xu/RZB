"""沿用上一版输入，新增共同年度建设上限。"""
import copy
import json
import shutil

import numpy as np

from ..annual_bounded_transfer_2035_20261017 import prepare as parent

base = parent.base
ROOT = parent.ROOT
RAW = ROOT/'研究报告/试算/20261017_分期建设排程逐年2035'
PUBLIC = ROOT/'研究报告/01研究推荐/当前版/分期增容逐年2035_20261017'
SOURCE = ROOT/'研究报告/数据来源/当前版/分期增容逐年2035_20261017'
REVIEW = ROOT/'研究报告/05_review/当前版/1017分期增容逐年2035'
REGIONS = parent.REGIONS
dump, write_csv, sha, forecasts = parent.dump, parent.write_csv, parent.sha, parent.forecasts
BUILD_RATE = .05


def prepare(region):
    for folder in (RAW,PUBLIC,SOURCE,REVIEW):folder.mkdir(parents=True,exist_ok=True)
    inp,powers=parent.load(region);inp=copy.deepcopy(inp)
    ff=forecasts(region);values={r['year']:r['forecast_load_mw'] for r in ff}
    growth1=(values[2030]/values[2025])**.2-1;growth2=(values[2035]/values[2030])**.2-1
    trend={2021:1.}
    for y in inp['years']:trend[y]=trend[y-1]*(1+(growth1 if y<=2030 else growth2))
    portfolios={};schedule={};references=[]
    for case in ('rigid','elastic_capacity'):
        source=parent.RAW/region/case/'2035/adopted.json';ref=json.loads(source.read_text())
        portfolios[case]=ref['units'];final=float(np.array(ref['units']).sum())
        schedule[case]={str(y):inp['initial_capacity_mva']+(final-inp['initial_capacity_mva'])*(trend[y]-1)/(trend[2035]-1)
                        for y in inp['years']}
        references.append(dict(case=case,path=str(source.relative_to(ROOT)),sha256=sha(source),terminal_capacity_mva=final))
    inp.update(annual_capacity_addition_limit_rate=BUILD_RATE,
        terminal_transformer_portfolios=portfolios,capacity_schedule_target_mva=schedule,schedule_allowance_mva=50.,
        capacity_schedule_policy='保留上一版2035主变工程清单，以五年预测负荷增长趋势分配累计建设进度，各年容许50MVA整台工程余量；终年匹配原清单。刚性进度同时服从2.0新增容量控制。仅调整建设排程，储能与联络逐年重新选配。',
        annual_construction_policy='同地区两方案每年净增主变铭牌容量不超过上年容量5%；采购仍按整台实施，未使用的额度不跨年累积',
        annual_construction_basis='预测期负荷年均增长约3.8%—4.1%，取5%作为包含整台工程余量的建设节奏研究假设，非规范强制限值',
        scope='2021固定实际地区容量，2022—2035保留远景主变清单的逐年分期建设；年度净增5%上限及50MVA进度余量，20%站级事故转供限额')
    folder=RAW/region;folder.mkdir(exist_ok=True);dump(folder/'inputs.json',inp)
    for name in ('hourly.npz','base_components.npz'):shutil.copy2(parent.RAW/region/name,folder/name)
    write_csv(SOURCE/f'{region}_预测增长率.csv',ff)
    dump(SOURCE/f'{region}_来源与约束.json',dict(parent_input=str((parent.RAW/region/'inputs.json').relative_to(ROOT)),
        parent_input_sha256=sha(parent.RAW/region/'inputs.json'),inputs_sha256=sha(folder/'inputs.json'),
        hourly_sha256=sha(folder/'hourly.npz'),parent_hourly_sha256=sha(parent.RAW/region/'hourly.npz'),
        change=inp['annual_construction_policy'],basis=inp['annual_construction_basis'],
        schedule_policy=inp['capacity_schedule_policy'],terminal_references=references,
        forecast_growth_2025_2030=(values[2030]/values[2025])**.2-1,
        forecast_growth_2030_2035=(values[2035]/values[2030])**.2-1,
        retained=['2021起点','负荷与光伏逐小时序列','同年共同下限','整台采购与远景选型','站级20%转供上限','原费用与储能口径']))
    return inp,powers


def load(region):
    folder=RAW/region
    if not (folder/'inputs.json').exists():return prepare(region)
    inp=json.loads((folder/'inputs.json').read_text());assert inp['annual_capacity_addition_limit_rate']==BUILD_RATE
    assert sha(folder/'hourly.npz')==sha(parent.RAW/region/'hourly.npz')
    data=np.load(folder/'hourly.npz');return inp,{int(y):data[y] for y in data.files}


if __name__=='__main__':
    for region in REGIONS:prepare(region)
