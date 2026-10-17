"""固定2021容量、无新建与储能，检验既有供区校准可行性。"""
import argparse

import numpy as np

from . import model as m,prepare as p
from ..annual_bounded_transfer_2035_20261017.run import write_warm


def run(region):
    inp,powers=p.load(region);power=powers[2021];root=p.RAW/region/'baseline';root.mkdir(exist_ok=True)
    ids=list(inp['stations']);old=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]);oldn=np.zeros(len(ids),int)
    selected={(int(h),f) for j in range(len(ids)) for h in (np.argmax(power[:,j]),np.argmin(power[:,j])) for f in (-1,j)}
    warm=root/'warm';write_warm(inp,warm,2021,old,oldn,set())
    for iteration in range(1,46):
        native,meta,one=m.build(inp,power,2021,'baseline',old,oldn,set(),np.ones((len(ids),2),bool),selected)
        for v in meta['third'].values():native.upper_bounds[v]=0.
        for v in meta['modules'].values():native.upper_bounds[v]=0.
        for v in meta['edgevars'].values():native.upper_bounds[v]=0.
        native.costs=[0.]*len(native.costs)
        for k,v in meta['normal_blocks'].items():native.costs[v]=1000.
        for k,v in meta['extra_blocks'].items():native.costs[v]=1.
        z,solver=p.base.old.old.base.parameters.solve(native,root,f'base_{iteration:02}',20.,.001,
            dict(one,storage_usable_energy_fraction=1.),meta,warm)
        if z is None or not solver.get('feasible_incumbent'):
            p.dump(root/'status.json',dict(verified=False,solver=solver,scope='固定2021容量、已有转供证据及代理网络未完成基期可行校准'))
            print('BASELINE_NOT_FEASIBLE',region,solver['status'],flush=True);return False
        u,n,built,normal,extra=m.layout(inp,z,meta);checked,bad=m.verify(inp,power,2021,u,n,built,normal,extra)
        print('BASELINE_CHECK',region,iteration,'bad',len(bad),'normal',sum(normal.values()),flush=True)
        if bad:
            assert bad-selected;selected|=bad;continue
        assert np.array_equal(u,old) and n.sum()==0 and not built
        inp['baseline_normal_blocks']={str(k):v for k,v in normal.items()}
        p.dump(p.RAW/region/'inputs.json',inp)
        p.dump(root/'adopted.json',dict(verified=True,units=u.tolist(),normal=normal,extra=extra,selected_pairs=sorted(selected),
            check=checked,solver=solver,scope='代理网络的固定容量既有供区校准，非实际历史接线认定'))
        np.savez_compressed(root/'chosen_solution.npz',solution=z)
        p.dump(root/'status.json',dict(verified=True,normal_blocks=sum(normal.values()),check=checked))
        print('BASELINE_VERIFIED',region,sum(normal.values()),flush=True);return True
    raise RuntimeError((region,'基期全年校准未闭合'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--region',choices=p.REGIONS,required=True)
    a=parser.parse_args();run(a.region)
