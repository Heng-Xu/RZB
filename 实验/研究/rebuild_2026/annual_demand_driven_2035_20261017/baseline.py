"""固定2021容量、无新建与储能，检验既有供区校准可行性。"""
import argparse

import numpy as np

from . import model as m,prepare as p
from ..annual_bounded_transfer_2035_20261017.run import write_warm
from .solver import solve


def diagnose(inp,power,old,normal,root):
    """允许辅助缺口变量选事故预案，最后清零辅助量再报告基期缺口。"""
    out=root/'全年缺口诊断';out.mkdir(exist_ok=True)
    ids=list(inp['stations']);zero=np.zeros(len(ids),int)
    selected={(int(h),f) for j in range(len(ids)) for h in (np.argmax(power[:,j]),np.argmin(power[:,j])) for f in (-1,j)}
    warm=out/'warm';write_warm(inp,warm,2021,old,zero,set())
    for iteration in range(1,46):
        native,meta,one=m.build(inp,power,2021,'baseline',old,zero,set(),np.ones((len(ids),2),bool),selected)
        for v in meta['third'].values():native.upper_bounds[v]=0.
        for v in meta['edgevars'].values():native.upper_bounds[v]=0.
        for k,v in meta['normal_blocks'].items():native.lower_bounds[v]=native.upper_bounds[v]=normal.get(k,0)
        native.costs=[0.]*len(native.costs)
        for v in meta['modules'].values():native.costs[v]=1e6
        for v in meta['extra_blocks'].values():native.costs[v]=1.
        z,solver=solve(native,out,f'diagnostic_{iteration:02}',20.,.00001,
            dict(one,storage_usable_energy_fraction=1.),meta,warm)
        assert z is not None and solver['feasible_incumbent']
        np.savez_compressed(warm/'full_solution.npz',solution=z)
        u,n,built,norm,extra=m.layout(inp,z,meta)
        checked,bad=m.verify(inp,power,2021,u,n,built,norm,extra)
        if bad:
            assert bad-selected;selected|=bad;write_warm(inp,warm,2021,u,n,built);continue
        actual,_=m.verify(inp,power,2021,old,zero,set(),normal,extra)
        p.dump(out/'diagnostic.json',dict(auxiliary_modules=n.tolist(),normal=normal,extra=extra,solver=solver,
            check_with_auxiliary=checked,check_without_auxiliary=actual,
            scope='辅助柜数仅用于量化缺口和选择既有事故预案，不作为已投运储能，不传入2022资产'))
        np.savez_compressed(out/'chosen_solution.npz',solution=z)
        return extra,actual
    raise RuntimeError('基期辅助缺口诊断未闭合')


def run(region,normal_only=False):
    inp,powers=p.load(region);power=powers[2021];root=p.RAW/region/'baseline';root.mkdir(exist_ok=True)
    ids=list(inp['stations']);old=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]);oldn=np.zeros(len(ids),int)
    selected={(int(h),f) for j in range(len(ids)) for h in (np.argmax(power[:,j]),np.argmin(power[:,j])) for f in ((-1,) if normal_only else (-1,j))}
    warm=root/'warm';write_warm(inp,warm,2021,old,oldn,set())
    for iteration in range(1,46):
        native,meta,one=m.build(inp,power,2021,'baseline',old,oldn,set(),np.ones((len(ids),2),bool),selected)
        for v in meta['third'].values():native.upper_bounds[v]=0.
        for v in meta['modules'].values():native.upper_bounds[v]=0.
        for v in meta['edgevars'].values():native.upper_bounds[v]=0.
        native.costs=[0.]*len(native.costs)
        for k,v in meta['normal_blocks'].items():native.costs[v]=1000.
        for k,v in meta['extra_blocks'].items():native.costs[v]=1.
        z,solver=p.base.old.old.base.parameters.solve(native,root,f'{"normal" if normal_only else "base"}_{iteration:02}',20.,.001,
            dict(one,storage_usable_energy_fraction=1.),meta,warm)
        if z is None or not solver.get('feasible_incumbent'):
            p.dump(root/('normal_status.json' if normal_only else 'status.json'),dict(verified=False,solver=solver,scope='固定2021容量、已有转供证据及代理网络未完成基期可行校准'))
            print('BASELINE_NOT_FEASIBLE',region,solver['status'],flush=True)
            if not normal_only:return run(region,normal_only=True)
            raise RuntimeError((region,'基期正常供区校准不可行，需核查输入'))
        u,n,built,normal,extra=m.layout(inp,z,meta);checked,bad=m.verify(inp,power,2021,u,n,built,normal,extra)
        print('BASELINE_CHECK',region,iteration,'bad',len(bad),'normal',sum(normal.values()),flush=True)
        if normal_only:bad={v for v in bad if v[1]==-1}
        if bad:
            assert bad-selected;selected|=bad;continue
        assert np.array_equal(u,old) and n.sum()==0 and not built
        if normal_only:extra,checked=diagnose(inp,power,old,normal,root)
        inp['baseline_normal_blocks']={str(k):v for k,v in normal.items()}
        p.dump(p.RAW/region/'inputs.json',inp)
        p.dump(root/'adopted.json',dict(verified=checked['verified'],normal_verified=all(v['violating_hours']==0 for v in checked['records'] if v['failed']=='正常'),units=u.tolist(),normal=normal,extra=extra,selected_pairs=sorted(selected),
            check=checked,solver=solver,contingency_plan_source='全年缺口诊断/diagnostic.json' if normal_only else 'chosen_solution.npz',
            scope='代理网络的固定容量既有供区校准；基期N1缺口逐项保留，2022起补强。非实际历史接线认定'))
        np.savez_compressed(root/('normal_calibration_solution.npz' if normal_only else 'chosen_solution.npz'),solution=z)
        p.dump(root/'status.json',dict(verified=checked['verified'],normal_verified=True,normal_blocks=sum(normal.values()),check=checked))
        print('BASELINE_VERIFIED' if checked['verified'] else 'BASELINE_NORMAL_ONLY',region,sum(normal.values()),flush=True);return True
    raise RuntimeError((region,'基期全年校准未闭合'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--region',choices=p.REGIONS,required=True)
    a=parser.parse_args();run(a.region)
