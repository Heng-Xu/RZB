"""复用已核验源荷与转供证据，仅变更年度工程选择规则。"""
import copy
import json
import shutil

import numpy as np

from ..annual_demand_driven_2035_20261017 import prepare as parent

ROOT = parent.ROOT
RAW = ROOT / '研究报告/试算/20261017_四年间隔总费用2035'
PUBLIC = ROOT / '研究报告/01研究推荐/当前版/四年间隔总费用2035_20261017'
SOURCE = ROOT / '研究报告/数据来源/当前版/四年间隔总费用2035_20261017'
REVIEW = ROOT / '研究报告/05_review/当前版/1017四年间隔总费用2035'
REGIONS = parent.REGIONS
dump, write_csv, sha = parent.dump, parent.write_csv, parent.sha
CASES = ('rigid', 'elastic')
INTERVAL = 4


def prepare(region):
    for directory in (RAW, PUBLIC, SOURCE, REVIEW):
        directory.mkdir(parents=True, exist_ok=True)
    inp, _ = parent.load(region)
    inp = copy.deepcopy(inp)
    refs = {name: dict(path=str((parent.RAW / region / name).relative_to(ROOT)),
                       sha256=sha(parent.RAW / region / name))
            for name in ('inputs.json', 'hourly.npz', 'base_components.npz')}
    inp.update(model_version='annual_cost_interval_2035_20261017',
               replacement_interval_years=INTERVAL,
               replacement_policy='任意连续四个规划年度内同一原主变位置最多更换一次；两次更换年份之差至少为4。为研究工程实施假设，不冒称规范条款。基期设备既往更换年份缺失，2022年起登记。',
               selection_policy='按当年新增主变、储能和联络全费用现值直接寻优，无配套费用20%容差及少建联络优先阶段，无刚弹结果排序约束',
               third_policy='仅原有允许位置可增第三台，整台50MVA；暂无扩大第三台规格或新增站址的工程证据',
               inherited_data=refs)
    out = RAW / region
    out.mkdir(exist_ok=True)
    dump(out / 'inputs.json', inp)
    (out / 'baseline').mkdir(exist_ok=True)
    shutil.copy2(parent.RAW / region / 'baseline/adopted.json', out / 'baseline/adopted.json')
    dump(SOURCE / f'{region}_输入及变更依据.json', dict(
        inherited_data=refs, interval_years=INTERVAL,
        reference='研究报告/AGENTS.md中四年内最多更换一次的工程实施假设，用户本轮同意重新定义长周期更换间隔并按总费用比较',
        policies={k: inp[k] for k in ('replacement_policy', 'selection_policy', 'third_policy')},
        unchanged='源荷、年度统计峰值、逐站转供MW上限、通道/端口/受端条件、初始容量和锁定经济参数沿用前版'))


def load(region):
    out = RAW / region / 'inputs.json'
    if not out.exists():
        prepare(region)
    inp = json.loads(out.read_text())
    for ref in inp['inherited_data'].values():
        assert sha(ROOT / ref['path']) == ref['sha256']
    data = np.load(ROOT / inp['inherited_data']['hourly.npz']['path'])
    return inp, {int(y): data[y] for y in data.files}


if __name__ == '__main__':
    for region in REGIONS:
        prepare(region)
