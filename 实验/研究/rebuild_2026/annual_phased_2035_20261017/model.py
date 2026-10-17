"""共同年度建设限额，控制总容量投运节奏。"""
import numpy as np
from ..annual_bounded_transfer_2035_20261017 import model as parent

arcs, layout, block_limit, verify = parent.arcs, parent.layout, parent.block_limit, parent.verify


def schedule_limits(inp,y,case,old):
    actual='rigid' if case.startswith('rigid') else 'elastic_capacity'
    target=inp['capacity_schedule_target_mva'][actual][str(y)];slack=inp['schedule_allowance_mva']
    final=float(np.array(inp['terminal_transformer_portfolios'][actual]).sum())
    lower=max(inp['initial_capacity_mva'],target-slack)
    if actual=='rigid':lower=min(lower,max(inp['initial_capacity_mva'],2*inp['annual_observed_peak_mw'][str(y)]-slack))
    lower=max(lower,final/(1+inp['annual_capacity_addition_limit_rate'])**(2035-y))
    upper=min(final,target+slack,float(old.sum())*(1+inp['annual_capacity_addition_limit_rate']))
    if y==2035:lower=final
    return lower,upper


def build(inp,power,y,case,old,oldn,built,replaced,selected):
    native,meta,one=parent.build(inp,power,y,case,old,oldn,built,replaced,selected)
    actual='rigid' if case.startswith('rigid') else 'elastic_capacity'
    portfolio=np.array(inp['terminal_transformer_portfolios'][actual]);ids=list(inp['stations'])
    for (sid,slot,yy,r),v in meta['x'].items():
        j=ids.index(sid)
        if abs(r-old[j,slot])>1e-7 and abs(r-portfolio[j,slot])>1e-7:native.upper_bounds[v]=0.
    for (sid,yy),v in meta['third'].items():
        if portfolio[ids.index(sid),2]<1:native.upper_bounds[v]=0.
    capacity={v:r for (sid,slot,yy,r),v in meta['x'].items() if yy==y}
    capacity.update({v:50. for (sid,yy),v in meta['third'].items() if yy==y})
    lower,upper=schedule_limits(inp,y,case,old)
    native.constraint(capacity,lower=lower,upper=upper)
    return native,meta,one
