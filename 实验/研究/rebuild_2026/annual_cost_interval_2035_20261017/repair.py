"""为已满足接线资源约束的候选补足静态储能，形成真实可行热启动。"""
import numpy as np
from scipy.sparse import coo_matrix

from . import model as m


def complete_storage(inp,power,z,meta,native):
    units,n,built,normal,extra = m.layout(inp,z,meta)
    ids,aa = list(inp['stations']),meta['arcs']
    count = len(ids)
    base = np.eye(count)
    def shift(matrix,k,num):
        a = aa[k]
        fraction = num/inp['block_count'][a['source']]
        matrix[a['sa'],a['sa']] -= fraction
        matrix[a['sa'],a['sb']] += fraction
    for k,num in normal.items():
        shift(base,k,num)
    bp = np.array([min(.1,.215*.76/max(1,s['forward_duration_h'])) for s in inp['stations'].values()])
    bn = np.array([min(.1,.215*.76/max(1,s['reverse_duration_h'])) for s in inp['stations'].values()])
    required = n.astype(float)
    for failed in range(-1,count):
        matrix = base.copy()
        if failed>=0:
            for k,num in extra.items():
                if aa[k]['sa']==failed:
                    shift(matrix,k,num)
        served = power@matrix
        cap = .95*units.sum(1)
        if failed>=0:
            cap[failed] -= .95*units[failed].max()
        reverse = .8*cap.copy()
        if failed>=0:
            reverse[failed] = cap[failed]
        required = np.maximum(required,np.maximum((served.max(0)-cap)/bp,(-served.min(0)-reverse)/bn))
    nn = np.maximum(n,np.ceil(required-1e-8).astype(int))
    result = z.copy()
    for j,sid in enumerate(ids):
        v = meta['modules'][sid,meta['year']]
        if nn[j]>native.upper_bounds[v]:
            return None
        result[v] = nn[j]
    rr,cc,vv = zip(*native.entries)
    lhs = coo_matrix((vv,(rr,cc)),shape=(len(native.constraint_lower),len(result))).tocsr()@result
    integers = np.array(native.integrality,dtype=bool)
    if np.any(result<np.array(native.lower_bounds)-1e-5) or np.any(result>np.array(native.upper_bounds)+1e-5):
        return None
    if np.any(abs(result[integers]-np.round(result[integers]))>1e-5):
        return None
    if np.any(lhs<np.array(native.constraint_lower)-1e-5) or np.any(lhs>np.array(native.constraint_upper)+1e-5):
        return None
    checked,bad = m.verify(inp,power,meta['year'],units,nn,built,normal,extra)
    assert not bad
    return result
