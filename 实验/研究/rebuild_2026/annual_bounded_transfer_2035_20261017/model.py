"""对既有与新增联络合并计入站级转供限额，禁止正常跨站卸载。"""
import math

from ..annual_transfer_2035_20261017 import model as parent

arcs, layout = parent.arcs, parent.layout


def block_limit(inp,sid):
    return math.floor(inp['block_count'][sid]*inp['combined_transfer_fraction']+1e-9)


def build(inp,power,y,case,old,oldn,built,replaced,selected):
    actual_case='rigid' if case.startswith('rigid') else case
    native,meta,one=parent.build(inp,power,y,actual_case,old,oldn,built,replaced,selected)
    ids=list(inp['stations'])
    for (sid,slot,yy,r),v in meta['x'].items():
        if r>old[ids.index(sid),slot]+1e-7 and r<inp['replacement_rating_target_mva'][sid]-1e-7:
            native.upper_bounds[v]=0.
    for v in meta['normal_blocks'].values():native.lower_bounds[v]=native.upper_bounds[v]=0.
    for sid in inp['stations']:
        terms={v:1. for k,v in meta['extra_blocks'].items() if meta['arcs'][k]['source']==sid}
        native.constraint(terms,upper=block_limit(inp,sid))
    return native,meta,one


def verify(inp,power,y,units,n,built,normal,extra):
    assert not any(normal.values()),'正常跨站卸载必须为零'
    aa=arcs(inp);counts={s:0 for s in inp['stations']}
    for k,count in extra.items():counts[aa[k]['source']]+=count
    for sid,count in counts.items():assert count<=block_limit(inp,sid),(y,sid,count,block_limit(inp,sid))
    checked,bad=parent.verify(inp,power,y,units,n,built,normal,extra)
    checked['station_transfer_limits']=[dict(station=sid,blocks=count,block_limit=block_limit(inp,sid),
        fraction=count/inp['block_count'][sid]) for sid,count in counts.items()]
    return checked,bad
