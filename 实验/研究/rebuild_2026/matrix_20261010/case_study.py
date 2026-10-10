"""在独立目录比较两地4h静态方案，保留已归档模型及原始结果。"""
import argparse
import copy
import json
import shutil
from pathlib import Path

from ..static_actual_20261010 import run as actual
from ..network_case_20261010.solver import solve as solver

BASE=actual.OUT
OUT=BASE.parent/'20261010_四小时案例'


def prepare(region):
    root=OUT/region;root.mkdir(parents=True,exist_ok=True)
    inp=json.loads((BASE/region/'inputs.json').read_text())
    for s in inp['stations'].values():s['forward_duration_h']=4.
    inp['support_duration_basis']='正向统一4h，反向沿用原静态工况的方向持续时间；原2/6h结果另存对照'
    inp['scope']='实际年度负荷、原候选网络及共同仿真起点；正向储能支撑时间统一4h'
    actual.dump(root/'inputs.json',inp)
    shutil.copy2(BASE/region/'静态工况.csv',root/'静态工况.csv')
    return inp


def run(region,case,seconds):
    inp=prepare(region);actual.OUT=OUT
    # 给求解器原方案的设备和联络作为初始候选；时长改变不继承原费用下界。
    def warmed(m,out,stage,secs,gap,input_data,meta,warmroot):
        if not (warmroot/'stations.csv').exists():warmroot=BASE/region/case
        return solver(m,out,stage,secs,gap,input_data,meta,warmroot)
    actual.solve=warmed
    actual.run(region,case,seconds)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--region',choices=['city','pizhou'],required=True)
    p.add_argument('--case',default='rigid_storage');p.add_argument('--seconds',type=int,default=300)
    a=p.parse_args();run(a.region,a.case,a.seconds)
