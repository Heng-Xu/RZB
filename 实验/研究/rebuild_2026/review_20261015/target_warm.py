"""在自由寻优解上构造并核验少一条联络的具体可行起点。"""
import argparse
import json
import math

import numpy as np

from . import cases as c


def cost(inp, states, built_by_year):
    old=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]);oldn=np.zeros(len(old));oldbuilt=set();total=0.
    for y in inp['years']:
        units,n=states[y];built=built_by_year[y]
        bought=np.where(units[:,:2]>old[:,:2]+1e-7,units[:,:2],0.).sum()
        third=(units[:,2]-old[:,2]).sum()/50.
        raw=dict(transformer=bought*inp['transformer_price_10k_per_purchased_mva']+third*inp['third_50mva_capex_10k'],
                 storage=(n-oldn).sum()*inp['storage_module_capex_10k'],line=len(built-oldbuilt)*inp['line_capex_10k'])
        total+=sum(v*inp['cost_factors'][k][str(y)] for k,v in raw.items());old,oldn,oldbuilt=units,n,built
    return float(total)


def run(region='pizhou',baseline='compressed'):
    inp,scenes,root=c.prepare(region,baseline);free=c.best_folder(root,'elastic_free');rigid=c.best_folder(root,'rigid')
    target={r['year']:r for r in json.loads((rigid/'summary.json').read_text())['annual']};ids=list(inp['stations']);lp=c.StationLP(inp)
    initial={y:c.old.assets_from_csv(inp,free,y) for y in inp['years']}
    last=inp['years'][-1];projects=c.old.base.previous.rows(free/'projects.csv')
    removals=[r['id'] for r in projects if int(r['year'])==last]
    first_need=next((y for y in inp['years'] if initial[y][0].sum()<target[y]['capacity_mva']+.5-1e-7),last)
    upgrades=[];u=initial[first_need][0]
    for j,sid in enumerate(ids):
        for slot in (0,1):
            nxt=next((r for r in (31.5,50.,63.,80.) if r>u[j,slot]+1e-7),None)
            if nxt is not None:
                upgrades.append((nxt*inp['transformer_price_10k_per_purchased_mva'],j,slot,nxt))
    # 同一造价下优先补小台，使N-1剩余容量增加。
    upgrades=sorted(upgrades,key=lambda x:(x[0],x[2],ids[x[1]]))
    assert upgrades
    chosen_upgrades=[upgrades[0]]
    out=root/'target_warm_search';out.mkdir(exist_ok=True);found=[]
    for eid in removals:
        for _,j,slot,nxt in chosen_upgrades:
            states={};built_by_year={};previous_n=np.zeros(len(ids),dtype=int);failed=False
            for y in inp['years']:
                units,n,built=initial[y];units=units.copy();n=np.maximum(n,previous_n);built=set(built)
                if y>=first_need:
                    units[j,slot]=max(units[j,slot],nxt);units[:,:2].sort(axis=1)
                    # 新方案可用增容替代尚未采购的储能，已投运部分继续保留。
                    n[j]=previous_n[j]
                if y==last:built.discard(eid)
                for p in scenes[y]:
                    ready=lp.prepared(p,y,units,n,built)
                    for f in range(-1,len(ids)):
                        r=lp.check(p,ready,f)
                        if not r['verified']:
                            for sid,deficit in r['station_deficits'].items():
                                k=ids.index(sid);s=inp['stations'][sid]
                                coefficient=min(.1,.215*.76/max(1,s['forward_duration_h']),.215*.76/max(1,s['reverse_duration_h']))
                                n[k]+=math.ceil((deficit+1e-7)/coefficient)
                            ready=lp.prepared(p,y,units,n,built)
                limit=max(0,target[y]['cumulative_lines']-int(y==last and target[y]['cumulative_lines']>0))
                if units.sum()<target[y]['capacity_mva']+.5-1e-7 or n.sum()*.215>target[y]['storage_mwh']+1e-7 or len(built)>limit:
                    failed=True;break
                states[y]=(units,n.copy());built_by_year[y]=built;previous_n=n.copy()
            if failed:continue
            value=cost(inp,states,built_by_year);folder=out/eid;folder.mkdir(exist_ok=True);rows=[]
            for y,(units,n) in states.items():
                for k,sid in enumerate(ids):rows.append(dict(year=y,station=sid,unit_1_mva=units[k,0],unit_2_mva=units[k,1],
                    unit_3_mva=units[k,2],storage_modules=int(n[k]),storage_mwh=float(n[k]*.215)))
            c.write_csv(folder/'stations.csv',rows);c.write_csv(folder/'projects.csv',[r for r in projects if r['id']!=eid])
            c.dump(folder/'proof.json',dict(verified=True,cost_npv_10k=value,removed_line=eid,upgrade_station=ids[j],
                upgrade_slot=slot,upgrade_to_mva=nxt,first_upgrade_year=first_need,
                source_free=str(free.relative_to(c.ROOT)),source_rigid=str(rigid.relative_to(c.ROOT))))
            found.append((value,folder));print('TARGET_WARM',eid,value,flush=True)
    assert found,'尚未构造满足指定对照的起点'
    best=min(found,key=lambda x:x[0]);c.dump(out/'selected.json',dict(cost_npv_10k=best[0],folder=str(best[1].relative_to(c.ROOT))))
    print('BEST_TARGET_WARM',best[0],best[1],flush=True)


def certify(region='pizhou',baseline='compressed',attempt=None):
    inp,scenes,root=c.prepare(region,baseline);choice=json.loads((root/'target_warm_search/selected.json').read_text())
    warm=c.ROOT/choice['folder'];rigid=c.best_folder(root,'rigid');free=c.best_folder(root,'elastic_free')
    target={r['year']:r for r in json.loads((rigid/'summary.json').read_text())['annual']}
    selected={tuple(r) for r in json.loads((free/'selected_pairs.json').read_text())}
    m,meta=c.build(inp,scenes,'elastic_target',selected,target)
    rows={(int(r['year']),r['station']):r for r in c.old.base.previous.rows(warm/'stations.csv')}
    projects=c.old.base.previous.rows(warm/'projects.csv')
    def fix(v,value):m.lower_bounds[v]=m.upper_bounds[v]=value
    for (sid,slot,y,r),v in meta['x'].items():fix(v,float(abs(float(rows[y,sid][f'unit_{slot+1}_mva'])-r)<1e-7))
    for (sid,y),v in meta['third'].items():fix(v,float(rows[y,sid]['unit_3_mva'])/50.)
    for (sid,y),v in meta['modules'].items():fix(v,int(rows[y,sid]['storage_modules']))
    for (eid,y),v in meta['edgevars'].items():fix(v,float(any(p['id']==eid and int(p['year'])<=y for p in projects)))
    out=root/('elastic_target_witness'+('_'+attempt if attempt else ''));out.mkdir(exist_ok=True)
    z,result=c.old.base.parameters.solve(m,out,'fixed_layout',45.,.0001,dict(inp,storage_usable_energy_fraction=1.),meta,warm)
    assert z is not None and result['feasible_incumbent']
    checks,violations,detail=c.old.base.check_all(inp,scenes,z,meta,c.StationLP(inp));assert not violations
    free_summary=json.loads((free/'summary.json').read_text());bounds=[free_summary['solver']['dual_bound']]
    for path in (root/'elastic_target').glob('iteration_*_solver.json'):
        value=json.loads(path.read_text()).get('dual_bound')
        if value is not None:bounds.append(value)
    result['fixed_layout_dual_bound']=result['dual_bound'];result['dual_bound']=max(bounds)
    result['mip_gap']=max(0.,(result['objective']-result['dual_bound'])/result['objective'])
    result['status']='Feasible enumerated layout; valid lower bound from relaxed/free search'
    result['accepted']=False
    summary,station_rows,project_rows=c.old.base.network.extract(inp,None,'elastic_target',z,meta,result,[],checks)
    summary.update(region=region,baseline=baseline,case='elastic_target',solver=result,checks=checks,
        scope='地区及各站极值同期静态截面，正常及最大单台主变N-1；正常反向80%；完整逐年设备和费用复核',
        scenario_constraint='指定对照：弹性容量逐年大于刚性至少0.5 MVA，储能及联络累计不多于刚性，末年在刚性联络非零时至少少1条',
        construction_method='在自由寻优解上逐项枚举末年新线删减、局部主变升档及储能补缺，保留费用最低的已核验布局；未声称全局最优',
        target_reference=str(rigid.relative_to(c.ROOT)),target_annual=list(target.values()),input_sha256=c.sha(root/'inputs.json'),
        bound_sources=['弹性自由寻优的费用下界','同一指定对照已完成求解阶段的费用下界'])
    summary.pop('full_hour_network_checks',None);previous=inp['initial_capacity_mva']
    for row in summary['annual']:row['net_capacity_increment_mva']=row['capacity_mva']-previous;previous=row['capacity_mva']
    c.dump(out/'summary.json',summary);c.write_csv(out/'years.csv',summary['annual']);c.write_csv(out/'stations.csv',station_rows)
    c.write_csv(out/'projects.csv',project_rows);c.dump(out/'selected_pairs.json',sorted(selected))
    c.dump(out/'independent_lp.json',dict(verified=True,checks=checks,records=detail));np.savez_compressed(out/'chosen_solution.npz',solution=z)
    print('CERTIFIED_TARGET',summary['cost_npv_10k'],result['mip_gap'],[(a['year'],a['capacity_mva'],a['storage_mwh'],a['cumulative_lines']) for a in summary['annual']],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--region',default='pizhou');p.add_argument('--baseline',default='compressed')
    p.add_argument('--certify',action='store_true');p.add_argument('--attempt')
    a=p.parse_args();certify(a.region,a.baseline,a.attempt) if a.certify else run(a.region,a.baseline)
