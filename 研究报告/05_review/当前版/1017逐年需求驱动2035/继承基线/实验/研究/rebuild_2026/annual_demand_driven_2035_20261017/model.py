"""固定源荷区段、年内一致接线及故障站局部追加切换。"""
import copy
import math
from collections import defaultdict

import numpy as np

from . import prepare as p


def arcs(inp):
    ids=list(inp['stations']);index={s:j for j,s in enumerate(ids)};result=[]
    feeders=inp['network']['feeders']
    totals={s:sum(r['maximum_load_proxy_2025_mw'] for r in feeders.values()
                 if r['station']==s and not r.get('equivalent_existing')) for s in ids}
    for edge in inp['network']['edges']:
        for d in range(2 if edge['bidirectional'] else 1):
            a,b=(edge['a'],edge['b']) if d==0 else (edge['b'],edge['a'])
            sa,sb=feeders[a]['station'],feeders[b]['station'];r=feeders[a]
            fraction=.5 if r.get('equivalent_existing') else r['maximum_load_proxy_2025_mw']/max(1e-9,totals[sa])
            if edge['existing']:fraction*=edge['source_section_fraction']
            limit=min(inp['max_blocks_per_feeder_group']*inp['port_group_count'].get(a,1),math.floor(inp['block_count'][sa]*fraction+1e-8))
            if limit<1:continue
            result.append(dict(id=edge['id'],direction=d,a=a,b=b,source=sa,target=sb,
                sa=index[sa],sb=index[sb],existing=edge['existing'],limit=limit,capacity_mw=edge['capacity_mw']))
    return result


def one_input(inp,y,old):
    one=copy.deepcopy(inp);one['years']=[y];one['initial_capacity_mva']=float(old.sum())
    for j,s in enumerate(one['stations'].values()):s['initial_units']=old[j,:2].tolist()
    return one


def cap_terms(inp,meta,sid,y,failed):
    full={v:p.base.old.old.PF*r for (s,slot,yy,r),v in meta['x'].items() if s==sid and yy==y}
    third=meta['third'].get((sid,y))
    if third is not None:full[third]=.95*50.
    if failed!=list(inp['stations']).index(sid):return [full]
    left={v:.95*r for (s,slot,yy,r),v in meta['x'].items() if s==sid and yy==y and slot==0}
    if third is not None:left[third]=.95*50.
    variants=[left]
    if third is not None and inp['stations'][sid]['initial_units'][1]<50.:
        # 第三台失效仅在其投运时生效。常数项由独立固定1变量承载。
        other={v:.95*r for (s,slot,yy,r),v in meta['x'].items() if s==sid and yy==y}
        other[third]=-.95*50.;other[meta['one']]=.95*50.;variants.append(other)
    return variants


def build(inp,power,y,case,old,oldn,built,replaced,selected):
    one=one_input(inp,y,old)
    # 只复用设备、费用与单次采购约束；旧自由转供工况不创建。
    native,meta=p.base.build(one,{y:power},'elastic_free',set())
    const=native.variable(0);native.lower_bounds[const]=1.;meta['one']=const
    total=p.base.old.old.base.previous.capacity_terms(one,meta,y)
    peak=inp['annual_observed_peak_mw'][str(y)]
    native.constraint(total,lower=inp['common_floor_by_year'][str(y)]*peak,
        upper=max(float(old.sum()),2*peak) if case=='rigid' else inp['physical_capacity_upper_mva'])
    ids=list(inp['stations']);index={s:j for j,s in enumerate(ids)}
    for (s,slot,yy,r),v in meta['x'].items():
        if replaced[index[s],slot]:native.lower_bounds[v]=native.upper_bounds[v]=float(abs(r-old[index[s],slot])<1e-8)
    for (s,yy),v in meta['third'].items():
        if old[index[s],2]>0:native.lower_bounds[v]=native.upper_bounds[v]=1.
    for (s,yy),v in meta['modules'].items():
        native.lower_bounds[v]=int(oldn[index[s]])
        native.upper_bounds[v]=max(native.upper_bounds[v],native.lower_bounds[v],
            math.ceil(abs(power[:,index[s]]).max()*max(inp['stations'][s]['forward_duration_h'],inp['stations'][s]['reverse_duration_h'])/(.215*.76))+1)
    for (eid,yy),v in meta['edgevars'].items():
        if eid in built:native.lower_bounds[v]=native.upper_bounds[v]=1.
    factors=inp['cost_factors'];c0=float(oldn.sum())*inp['storage_module_capex_10k']*factors['storage'][str(y)]
    c0+=len(built)*inp['line_capex_10k']*factors['line'][str(y)]
    c0+=sum(old[:,2]>0)*inp['third_50mva_capex_10k']*factors['transformer'][str(y)]
    native.costs[const]=-c0
    aa=arcs(inp);normal={};extra={};uses={};neighbor={}
    sourcepeak=abs(power).max(axis=0)
    weight=np.array([sourcepeak[a['sa']]/inp['block_count'][a['source']] for a in aa])
    for k,a in enumerate(aa):
        normal[k]=native.variable(0,upper=a['limit'])
        if a['existing'] and y>2021:
            native.lower_bounds[normal[k]]=native.upper_bounds[normal[k]]=inp['baseline_normal_blocks'].get(str(k),0)
        extra[k]=native.variable(0,upper=a['limit'])
        use=native.variable(0);uses[k]=use
        terms={extra[k]:1.,use:-a['limit']}
        if k in normal:terms[normal[k]]=1.
        native.constraint(terms,upper=0.)
        if not a['existing']:native.constraint({use:1.,meta['edgevars'][a['id'],y]:-1.},upper=0.)
        key=(a['a'],a['target'])
        if key not in neighbor:neighbor[key]=native.variable(0)
        native.constraint({use:1.,neighbor[key]:-1.},upper=0.)
    byfeeder=defaultdict(list)
    for k,a in enumerate(aa):byfeeder[a['a']].append(k)
    for fid,ks in byfeeder.items():
        native.constraint({uses[k]:1. for k in ks},upper=3.*inp['port_group_count'].get(fid,1))
        native.constraint({v:1. for (f,s),v in neighbor.items() if f==fid},upper=2.*inp['port_group_count'].get(fid,1))
        terms={}
        for k in ks:
            terms[extra[k]]=1.
            if k in normal:terms[normal[k]]=1.
        native.constraint(terms,upper=max(aa[k]['limit'] for k in ks))
    for j,s in enumerate(ids):
        terms={v:1. for k,v in normal.items() if aa[k]['sa']==j}
        terms.update({v:1. for k,v in extra.items() if aa[k]['sa']==j})
        native.constraint(terms,upper=inp['block_count'][s])
        existing={extra[k]:weight[k] for k,a in enumerate(aa) if a['sa']==j and a['existing']}
        existing.update({normal[k]:weight[k] for k,a in enumerate(aa) if a['sa']==j and a['existing']})
        native.constraint(existing,upper=inp['existing_transfer_budget_by_year_mw'][str(y)][s])
        paid={extra[k]:1. for k,a in enumerate(aa) if a['sa']==j and not a['existing']}
        paid.update({normal[k]:1. for k,a in enumerate(aa) if a['sa']==j and not a['existing']})
        native.constraint(paid,upper=math.floor(inp['block_count'][s]*inp['new_transfer_fraction']+1e-9))
    # 同期占用采用各源端峰值绝对功率上界；接收余量不通过健康站转出而增加。
    receive={}
    yearfactor=inp['annual_observed_peak_mw'][str(y)]/inp['annual_observed_peak_mw']['2025']
    for fid,r in inp['network']['feeders'].items():
        receive[fid]=max(0.,r['thermal_mw']-r['maximum_load_proxy_2025_mw']*yearfactor)
    for field,limits in [('id',{e['id']:e['capacity_mw'] for e in inp['network']['edges']}),('b',receive)]:
        groups=defaultdict(list)
        for k,a in enumerate(aa):groups[a[field]].append(k)
        for key,ks in groups.items():
            terms={normal[k]:weight[k] for k in ks if k in normal}
            native.constraint(terms,upper=limits[key])
            for j in {aa[k]['sa'] for k in ks}:
                more={extra[k]:weight[k] for k in ks if aa[k]['sa']==j}
                native.constraint({**terms,**more},upper=limits[key])
    meta.update(arcs=aa,normal_blocks=normal,extra_blocks=extra,source_weight=weight,receive=receive,
                fixed_asset_cost_offset_10k=c0,year=y)
    for h,f in sorted(selected):
        net=[{} for _ in ids]
        for k,v in normal.items():
            a=aa[k];co=float(power[h,a['sa']])/inp['block_count'][a['source']]
            net[a['sa']][v]=co;net[a['sb']][v]=-co
        if f>=0:
            for k,v in extra.items():
                a=aa[k]
                if a['sa']!=f:continue
                co=float(power[h,f])/inp['block_count'][a['source']]
                net[f][v]=co;net[a['sb']][v]=-co
        for j,s in enumerate(ids):
            station=inp['stations'][s]
            for cap in cap_terms(one,meta,s,y,f):
                for sign,key in ((1,'forward_duration_h'),(-1,'reverse_duration_h')):
                    beta=.8 if sign<0 and j!=f else 1.
                    terms={v:beta*c for v,c in cap.items()}
                    terms[meta['modules'][s,y]]=min(.1,.215*.76/max(1,station[key]))
                    terms.update({v:sign*c for v,c in net[j].items()})
                    native.constraint(terms,lower=sign*float(power[h,j]))
    return native,meta,one


def layout(inp,z,meta):
    y=meta['year'];u,n,_,_=p.base.old.old.base.assets.assets(inp,z,meta,y)
    built={eid for (eid,yy),v in meta['edgevars'].items() if z[v]>.5}
    normal={k:int(round(z[v])) for k,v in meta['normal_blocks'].items() if z[v]>.5}
    extra={k:int(round(z[v])) for k,v in meta['extra_blocks'].items() if z[v]>.5}
    return u,n,built,normal,extra


def verify(inp,power,y,units,n,built,normal,extra):
    """独立重建供区矩阵；固定预案对8760小时全检，不复用主模型约束行。"""
    aa=arcs(inp);ids=list(inp['stations']);N=len(ids);T=np.eye(N)
    if y>2021:
        for k,a in enumerate(aa):
            if a['existing']:assert normal.get(k,0)==inp['baseline_normal_blocks'].get(str(k),0)
    for sid in ids:
        paid=sum(normal.get(k,0)+extra.get(k,0) for k,a in enumerate(aa) if a['source']==sid and not a['existing'])
        assert paid<=math.floor(inp['block_count'][sid]*inp['new_transfer_fraction']+1e-9)
    def shift(matrix,k,count):
        a=aa[k];fraction=count/inp['block_count'][a['source']]
        matrix[a['sa'],a['sa']]-=fraction;matrix[a['sa'],a['sb']]+=fraction
    for k,count in normal.items():shift(T,k,count)
    allrecords=[];bad=set();maxerror=0.;counter=[]
    peak=abs(power).max(axis=0)
    factor=inp['annual_observed_peak_mw'][str(y)]/inp['annual_observed_peak_mw']['2025']
    receive={f:max(0.,r['thermal_mw']-r['maximum_load_proxy_2025_mw']*factor)
             for f,r in inp['network']['feeders'].items()}
    for f in range(-1,N):
        matrix=T.copy();active=dict(normal)
        if f>=0:
            for k,count in extra.items():
                if aa[k]['sa']==f:shift(matrix,k,count);active[k]=active.get(k,0)+count
        assert np.min(matrix)>-1e-7 and np.max(abs(matrix.sum(axis=1)-1))<1e-7
        served=power@matrix
        cap=.95*units.sum(axis=1)
        if f>=0:cap[f]-=.95*units[f].max()
        reverse=.8*cap.copy()
        if f>=0:reverse[f]=cap[f]
        bp=np.array([min(.1,.215*.76/max(1,s['forward_duration_h'])) for s in inp['stations'].values()])*n
        bn=np.array([min(.1,.215*.76/max(1,s['reverse_duration_h'])) for s in inp['stations'].values()])*n
        margin=np.minimum(cap+bp-served,reverse+bn+served)
        wh,wj=np.unravel_index(np.argmin(margin),margin.shape)
        worst=max(0.,float(-margin[wh,wj]));maxerror=max(maxerror,worst)
        for j in range(N):
            for h in np.argsort(margin[:,j])[:3]:
                if margin[h,j]<-1e-5:bad.add((int(h),f))
        allrecords.append(dict(year=y,failed=ids[f] if f>=0 else '正常',checked_hours=len(power),
            violating_hours=int(np.any(margin < -1e-5,axis=1).sum()),max_deficit_mw=worst,
            worst_hour=int(wh),worst_station=ids[wj],minimum_margin_mw=float(margin.min())))
        edgeuse=defaultdict(float);inuse=defaultdict(float);sourceuse=defaultdict(int);portuse=defaultdict(int)
        for k,count in active.items():
            a=aa[k];q=count*peak[a['sa']]/inp['block_count'][a['source']]
            assert (not a['existing'] and a['id'] in built) or (a['existing'] and (normal.get(k,0)>0 or f==a['sa']))
            assert count<=a['limit']
            edgeuse[a['id']]+=q;inuse[a['b']]+=q;sourceuse[a['source']]+=count;portuse[a['a']]+=count
        for s,count in sourceuse.items():assert count<=inp['block_count'][s]
        for fid,count in portuse.items():assert count<=max(a['limit'] for a in aa if a['a']==fid)
        for key,value in edgeuse.items():
            limit=next(e['capacity_mw'] for e in inp['network']['edges'] if e['id']==key)
            assert value<=limit+1e-5,(y,f,key,value,limit)
        for fid,value in inuse.items():assert value<=receive[fid]+1e-5,(y,f,fid,value,receive[fid])
        for sid in ids:
            existing=sum(count*peak[aa[k]['sa']]/inp['block_count'][sid] for k,count in active.items()
                         if aa[k]['source']==sid and aa[k]['existing'])
            assert existing<=inp['existing_transfer_budget_by_year_mw'][str(y)][sid]+1e-5
        counter.append(dict(year=y,failed=ids[f] if f>=0 else '正常',switched_blocks=sum(active.values()),
            existing_transfer_peak_upper_mw=sum(count*peak[aa[k]['sa']]/inp['block_count'][aa[k]['source']]
                                              for k,count in active.items() if aa[k]['existing']),
            new_transfer_peak_upper_mw=sum(count*peak[aa[k]['sa']]/inp['block_count'][aa[k]['source']]
                                         for k,count in active.items() if not aa[k]['existing'])))
    for fid in {a['a'] for a in aa}:
        used=[a for k,a in enumerate(aa) if a['a']==fid and (normal.get(k,0)+extra.get(k,0)>0)]
        assert len(used)<=3*inp['port_group_count'].get(fid,1) and len({a['target'] for a in used})<=2*inp['port_group_count'].get(fid,1)
    return dict(verified=not bad,year=y,checked_hour_contingency_pairs=len(power)*(N+1),
                max_deficit_mw=maxerror,records=allrecords,transfers=counter),bad
