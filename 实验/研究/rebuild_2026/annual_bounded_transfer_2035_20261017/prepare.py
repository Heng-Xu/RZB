"""沿用已核验源荷输入，只增加共同的转供边界。"""
import copy
import json
import shutil

import numpy as np

from ..annual_transfer_2035_20261017 import prepare as parent

base = parent.base
ROOT = parent.ROOT
RAW = ROOT/'研究报告/试算/20261017_远景定容站级限额逐年2035'
PUBLIC = ROOT/'研究报告/01研究推荐/当前版/站级限额逐年2035_20261017'
SOURCE = ROOT/'研究报告/数据来源/当前版/站级限额逐年2035_20261017'
REVIEW = ROOT/'研究报告/05_review/当前版/1017站级限额逐年2035'
REGIONS = parent.REGIONS
dump, write_csv, sha, forecasts = parent.dump, parent.write_csv, parent.sha, parent.forecasts
TRANSFER_FRACTION = .20


def prepare(region):
    for folder in (RAW,PUBLIC,SOURCE,REVIEW):folder.mkdir(parents=True,exist_ok=True)
    inp,powers=parent.load(region);inp=copy.deepcopy(inp)
    envelope=np.maximum(powers[2035].max(axis=0),-powers[2035].min(axis=0))/.95
    targets={sid:next((r for r in inp['new_ratings'] if r>=q-1e-9),max(inp['new_ratings']))
             for sid,q in zip(inp['stations'],envelope)}
    inp.update(normal_transfer_policy='正常运行固定本站供区，正常跨站区段切换为零',
        combined_transfer_fraction=TRANSFER_FRACTION,
        combined_transfer_policy='每站事故转出的既有与新增联络区段合计不超过全站区段数20%，向下取整；既有J列、路径和接收余量继续约束',
        transfer_fraction_basis='本轮偏增容研究情景的工程假设，非标准强制数值、非实测转供率；两个方案一致',
        replacement_rating_target_mva=targets,
        replacement_rating_policy='发生原主变替换时，新购额定容量不低于本站2035正反向峰值除0.95后对应可选规格，最高按80MVA；保留原机不触发采购。两方案一致，允许第三台仍按原50MVA。远景定容为研究规则，并非承诺本站2035可脱离配套独立供电。',
        scope='2021固定实际地区总容量，2022—2035逐年滚动；正常本站供电、事故站级20%合并转供限额')
    folder=RAW/region;folder.mkdir(exist_ok=True)
    dump(folder/'inputs.json',inp)
    for name in ('hourly.npz','base_components.npz'):shutil.copy2(parent.RAW/region/name,folder/name)
    write_csv(SOURCE/f'{region}_预测增长率.csv',forecasts(region))
    dump(SOURCE/f'{region}_来源与约束.json',dict(parent_input=str((parent.RAW/region/'inputs.json').relative_to(ROOT)),
        parent_input_sha256=sha(parent.RAW/region/'inputs.json'),inputs_sha256=sha(folder/'inputs.json'),
        hourly_sha256=sha(folder/'hourly.npz'),parent_hourly_sha256=sha(parent.RAW/region/'hourly.npz'),
        changed_constraints=['正常跨站转供为零','既有与新增事故转供共用站级20%区段限额','原主变替换按2035负荷选择规格'],
        unchanged=['逐年负荷与光伏输入','地区起点容量','两方案共同容载比下限','额定容量及单次更换规则','费用参数','局部事故预案及馈线共享余量'],
        assumption=inp['transfer_fraction_basis'],forecast_basis=inp['forecast_basis']))
    return inp,powers


def load(region):
    folder=RAW/region
    if not (folder/'inputs.json').exists():return prepare(region)
    inp=json.loads((folder/'inputs.json').read_text())
    assert inp['combined_transfer_fraction']==TRANSFER_FRACTION
    assert sha(folder/'hourly.npz')==sha(parent.RAW/region/'hourly.npz')
    data=np.load(folder/'hourly.npz')
    return inp,{int(y):data[y] for y in data.files}


if __name__=='__main__':
    for region in REGIONS:prepare(region)
