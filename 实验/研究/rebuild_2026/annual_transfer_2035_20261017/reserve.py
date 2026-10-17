"""配套设施不增加，在同一年度费用包络内优选采购容量并逐年保留。"""
import argparse
import copy
import json
import math
from itertools import product

import numpy as np

from . import model as m, prepare as p
from .run import annual_row, asset_rows, write_warm


def prefer_ratings(inp,u,purchase_mask,budget,y):
    """只提高本年原已采购位置的铭牌规格，按0.5MVA整格做多重选择背包。"""
    capprice=inp['transformer_price_10k_per_purchased_mva']*inp['cost_factors']['transformer'][str(y)]
    limit=max(0,math.floor((budget+1e-7)/capprice*2))
    base=u.copy();groups=[]
    for j in range(len(u)):
        pools=[]
        for slot in (0,1):
            bought=purchase_mask[j,slot]
            pools.append(sorted({u[j,slot],*[r for r in inp['new_ratings'] if r>=u[j,slot]]}) if bought else [u[j,slot]])
        options=[]
        for a,b in product(*pools):
            if a>b:continue
            delta=a+b-u[j,:2].sum();key=round(delta*2)
            survive=a+b+u[j,2]-max(a,b,u[j,2])-(u[j].sum()-u[j].max())
            options.append((key,survive,a,b))
        groups.append(options)
    states={0:(0.,[])}
    for options in groups:
        after={}
        for already,(score,chosen) in states.items():
            for key,survive,a,b in options:
                target=already+key
                if target>limit:continue
                value=(score+survive,chosen+[(a,b)])
                if target not in after or value[0]>after[target][0]+1e-8:after[target]=value
        states=after
    best=max(states);chosen=states[best][1]
    for j,(a,b) in enumerate(chosen):base[j,:2]=[a,b]
    return base,dict(extra_capacity_mva=best/2.,incremental_npv_10k=best/2.*capprice,
                     budget_npv_10k=budget,secondary_n1_surviving_gain_mva=states[best][0])


def certify(inp,power,y,old,oldn,oldbuilt,replaced,units,n,built,normal,extra,selected,folder,tag):
    native,meta,one=m.build(inp,power,y,'elastic_reserve',old,oldn,oldbuilt,replaced,selected)
    def fix(v,value):native.lower_bounds[v]=native.upper_bounds[v]=float(value)
    ids=list(inp['stations']);index={s:j for j,s in enumerate(ids)}
    for (s,slot,yy,r),v in meta['x'].items():fix(v,abs(units[index[s],slot]-r)<1e-8)
    for (s,yy),v in meta['third'].items():fix(v,units[index[s],2]/50.)
    for (s,yy),v in meta['modules'].items():fix(v,n[index[s]])
    for (eid,yy),v in meta['edgevars'].items():fix(v,eid in built)
    for k,v in meta['normal_blocks'].items():fix(v,normal.get(k,0))
    for k,v in meta['extra_blocks'].items():fix(v,extra.get(k,0))
    warm=folder/(tag+'_warm');write_warm(inp,warm,y,units,n,built)
    z,solver=p.base.old.old.base.parameters.solve(native,folder,tag,20.,.00001,
        dict(one,storage_usable_energy_fraction=1.),meta,warm)
    assert z is not None and solver['feasible_incumbent']
    u,nn,bs,norm,ext=m.layout(inp,z,meta)
    checked,bad=m.verify(inp,power,y,u,nn,bs,norm,ext);assert not bad
    solver.update(fixed_layout_bound=solver['dual_bound'],source_status=solver['status'],dual_bound=0.,
                  mip_gap=1. if solver['objective']>1e-6 else 0.,accepted=False,
                  status='固定设备及预案可行性复核；规划问题只登记非负费用的零下界')
    return z,solver,checked


def run(region):
    inp,powers=p.load(region);parent=p.RAW/region/'elastic_balanced'
    original=json.loads((parent/'summary.json').read_text());out=p.RAW/region/'elastic_reserve';out.mkdir(exist_ok=True)
    ids=list(inp['stations']);old=np.array([s['initial_units']+[0.] for s in inp['stations'].values()])
    source_old=old.copy();oldn=np.zeros(len(ids),int);oldbuilt=set();replaced=np.zeros((len(ids),2),bool)
    annual=[original['annual'][0]];stations=asset_rows(inp,2021,old,oldn);projects=[];history=[];checks=[];transfers=[];cumulative=0.
    basecheck,_=m.verify(inp,powers[2021],2021,old,oldn,set(),{},{});p.dump(out/'baseline_check.json',basecheck)
    for y in inp['years']:
        source=json.loads((parent/str(y)/'adopted.json').read_text())
        reference=json.loads((parent/str(y)/'economic_reference.json').read_text())
        source_units=np.array(source['units']);units=np.maximum(source_units,old)
        n=np.array(source['modules']);built=set(source['built'])
        normal={int(k):v for k,v in source['normal'].items()};extra={int(k):v for k,v in source['extra'].items()}
        reference_units=np.maximum(np.array(reference['units']),old)
        reference_cost=annual_row(inp,y,reference_units,np.array(reference['modules']),set(reference['built']),old,oldn,oldbuilt,0.)['added_lifecycle_npv_10k']
        cost=annual_row(inp,y,units,n,built,old,oldn,oldbuilt,0.)['added_lifecycle_npv_10k']
        budget=1.05*reference_cost-cost;assert budget>-1e-5,(region,y,budget)
        chosen,selection=prefer_ratings(inp,units,source_units[:,:2]>source_old[:,:2]+1e-6,max(0.,budget),y)
        assert np.all(chosen>=units) and np.all(n>=oldn) and built>=oldbuilt
        stage=out/str(y);stage.mkdir(exist_ok=True)
        p.dump(stage/'previous_assets.json',dict(year=y,units=old.tolist(),modules=oldn.tolist(),built=sorted(oldbuilt),
            replaced=replaced.tolist(),input_sha256=p.sha(p.RAW/region/'inputs.json')))
        selected={tuple(v) for v in source['selected_pairs']}
        rz,rs,rc=certify(inp,powers[y],y,old,oldn,oldbuilt,replaced,reference_units,np.array(reference['modules']),
            set(reference['built']),{int(k):v for k,v in reference['normal'].items()},
            {int(k):v for k,v in reference['extra'].items()},selected,stage,'reference_fixed')
        assert abs(rs['objective']-reference_cost)<.02
        ref=dict(reference,units=reference_units.tolist(),solver=rs,check=rc,
            method='父方案本年费用参考在追加容量后的既有资产上保持原配置及预案的可行费用基准；未重新寻优',
            parent_solver=reference['solver'],parent_source_sha256=p.sha(parent/str(y)/'economic_reference.json'))
        p.dump(stage/'economic_reference.json',ref);np.savez_compressed(stage/'economic_solution.npz',solution=rz)
        z,solver,checked=certify(inp,powers[y],y,old,oldn,oldbuilt,replaced,chosen,n,built,normal,extra,selected,stage,'reserve_fixed')
        row=annual_row(inp,y,chosen,n,built,old,oldn,oldbuilt,cumulative)
        assert abs(row['added_lifecycle_npv_10k']-solver['objective'])<.02
        assert row['added_lifecycle_npv_10k']<=1.05*reference_cost+1e-5
        assert n.sum()<=sum(reference['modules']) and len(built)<=len(reference['built'])
        solver['reference_cost_npv_10k']=reference_cost
        choice=dict(rule='配套设施均不高于本年费用参考，5%费用包络内提高本年采购位置的额定容量并跨年保留；同容量增量优先增加N-1剩余容量',
            tolerance=.05,premium=row['added_lifecycle_npv_10k']/reference_cost-1 if reference_cost>1e-6 else 0.,
            capacity_selection=selection,reference_scope=ref['method'])
        result=dict(year=y,units=chosen.tolist(),modules=n.tolist(),built=sorted(built),normal=normal,extra=extra,
            solver=solver,economic_reference=rs,selected_pairs=sorted(selected),check=checked,annual=row,
            previous_assets_sha256=p.sha(stage/'previous_assets.json'),selection=choice,
            parent_adopted_sha256=p.sha(parent/str(y)/'adopted.json'))
        p.dump(stage/'adopted.json',result);np.savez_compressed(stage/'chosen_solution.npz',solution=z)
        changed=chosen[:,:2]>old[:,:2]+1e-7;assert not np.any(changed&replaced);replaced|=changed
        cumulative=row['cumulative_lifecycle_npv_10k'];annual.append(row);stations.extend(asset_rows(inp,y,chosen,n))
        projects.extend(dict(year=y,id=e) for e in sorted(built-oldbuilt));checks.extend(checked['records']);transfers.extend(checked['transfers'])
        history.append(dict(year=y,solver=solver,economic_reference=rs,selection=choice))
        source_old=source_units;old,oldn,oldbuilt=chosen,n,built
        print('RESERVE_YEAR',region,y,'C',chosen.sum(),'extra',selection['extra_capacity_mva'],'cost',row['added_lifecycle_npv_10k'],flush=True)
    p.write_csv(out/'stations.csv',stations);p.write_csv(out/'projects.csv',projects);p.write_csv(out/'years.csv',annual)
    p.dump(out/'summary.json',dict(region=region,case='elastic_reserve',annual=annual,cost_npv_10k=cumulative,
        cost_scope=original['cost_scope'],planning_method='逐年继承的工程可行方案；在原费用包络内优选已采购位置的额定容量，非全期联合最优',
        history=history,baseline_verified=basecheck['verified'],input_sha256=p.sha(p.RAW/region/'inputs.json'),scope=inp['scope'],
        checked_hour_contingency_pairs=sum(r['checked_hours'] for r in checks),verified=True,
        parent_plan_sha256=p.sha(parent/'summary.json')))
    p.dump(out/'independent_full_year.json',dict(verified=True,records=checks,transfers=transfers,
        scope='固定代理接线及预案，补齐后8760小时逐项静态检查；非SOC优化'))
    print('RESERVE_DONE',region,cumulative,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--region',choices=p.REGIONS,required=True)
    args=parser.parse_args();run(args.region)
