"""逐年承接资产，保存经济参考、工程选择及全年独立校核。"""
import argparse
import copy
import json
import math

import numpy as np

from . import model as m, prepare as p


def asset_rows(inp,y,u,n):
    return [dict(year=y,station=s,unit_1_mva=u[j,0],unit_2_mva=u[j,1],unit_3_mva=u[j,2],storage_modules=int(n[j]))
            for j,s in enumerate(inp['stations'])]


def write_warm(inp,folder,y,u,n,built):
    folder.mkdir(exist_ok=True)
    p.write_csv(folder/'stations.csv',asset_rows(inp,y,u,n))
    p.write_csv(folder/'projects.csv',[dict(year=y,id=e) for e in sorted(built)])
    if not built:(folder/'projects.csv').write_text('year,id\n',encoding='utf-8-sig')


def annual_row(inp,y,u,n,built,old,oldn,oldbuilt,cumulative):
    bought=np.where(u[:,:2]>old[:,:2]+1e-6,u[:,:2],0.).sum()
    thirds=int(np.round((u[:,2]-old[:,2]).sum()/50.))
    tc=bought*inp['transformer_price_10k_per_purchased_mva']+thirds*inp['third_50mva_capex_10k']
    bc=int((n-oldn).sum())*inp['storage_module_capex_10k'];lc=len(built-oldbuilt)*inp['line_capex_10k']
    costs={k:v*inp['cost_factors'][k][str(y)] for k,v in [('transformer',tc),('storage',bc),('line',lc)]}
    return dict(year=y,peak_mw=inp['annual_observed_peak_mw'][str(y)],capacity_mva=float(u.sum()),
        clr=float(u.sum()/inp['annual_observed_peak_mw'][str(y)]),common_floor=inp['common_floor_by_year'][str(y)],
        purchased_transformer_mva=float(bought+50*thirds),net_capacity_increment_mva=float(u.sum()-old.sum()),
        replaced_capacity_mva=float(bought+50*thirds-u.sum()+old.sum()),new_third_count=thirds,
        storage_nameplate_mw=float(n.sum()*.1),storage_mwh=float(n.sum()*.215),
        new_storage_mwh=float((n-oldn).sum()*.215),new_lines=len(built-oldbuilt),cumulative_lines=len(built),
        transformer_capex_10k=float(tc),storage_capex_10k=float(bc),line_capex_10k=float(lc),
        construction_capex_10k=float(tc+bc+lc),added_lifecycle_npv_10k=float(sum(costs.values())),
        cumulative_lifecycle_npv_10k=float(cumulative+sum(costs.values())),
        **{k+'_npv_10k':float(v) for k,v in costs.items()})


def get_stage(inp,power,y,case,old,oldn,built,replaced,folder,seconds):
    state=folder/'adopted.json'
    if state.exists():
        r=json.loads(state.read_text())
        assert r['previous_assets_sha256']==p.sha(folder/'previous_assets.json')
        return np.array(r['units']),np.array(r['modules']),set(r['built']),{int(k):v for k,v in r['normal'].items()},\
            {int(k):v for k,v in r['extra'].items()},r
    # 无转供即足额的安全起点；不把此起点作为工程结果。
    survive=.95*(old.sum(axis=1)-old.max(axis=1));reverse=np.minimum(survive,.8*.95*old.sum(axis=1))
    bp=np.array([min(.1,.215*.76/max(1,s['forward_duration_h'])) for s in inp['stations'].values()])
    bn=np.array([min(.1,.215*.76/max(1,s['reverse_duration_h'])) for s in inp['stations'].values()])
    warmn=np.maximum(oldn,np.ceil(np.maximum(0.,np.maximum((power.max(axis=0)-survive)/bp,(-power.min(axis=0)-reverse)/bn))+1e-8).astype(int))
    warm=folder/'warm';write_warm(inp,warm,y,old,warmn,built)
    selected={(int(np.argmax(power[:,j])),j) for j in range(power.shape[1])}
    selected|={(int(np.argmin(power[:,j])),j) for j in range(power.shape[1])}
    selected|={(int(np.argmax(power[:,j])),-1) for j in range(power.shape[1])}
    selected|={(int(np.argmin(power[:,j])),-1) for j in range(power.shape[1])}
    prior=folder.parent/str(y-1)/'adopted.json'
    if prior.exists():selected.update(tuple(v) for v in json.loads(prior.read_text())['selected_pairs'])
    progress=folder/'separation_progress.json'
    if progress.exists():selected.update(tuple(v) for v in json.loads(progress.read_text())['selected_pairs'])
    bounds=[];economic_history=[]
    for iteration in range(1,31):
        native,meta,one=m.build(inp,power,y,case,old,oldn,built,replaced,selected)
        z,solver=p.base.old.old.base.parameters.solve(native,folder,f'economic_{iteration:02}',seconds,.02,
            dict(one,storage_usable_energy_fraction=1.),meta,warm)
        assert z is not None and solver['feasible_incumbent'],(y,case,solver)
        if solver['dual_bound'] is not None:bounds.append(solver['dual_bound'])
        u,n,bs,normal,extra=m.layout(inp,z,meta)
        check,bad=m.verify(inp,power,y,u,n,bs,normal,extra)
        economic_history.append(dict(iteration=iteration,solver=solver,verified=check['verified'],selected_pairs=len(selected)))
        print('ANNUAL_ECON',inp['region_name'],case,y,iteration,'bad',len(bad),'cost',solver['objective'],flush=True)
        if bad:
            assert bad-selected
            selected|=bad;p.dump(progress,dict(selected_pairs=sorted(selected)))
            write_warm(inp,warm,y,u,n,bs);continue
        solver['dual_bound']=max(bounds)
        solver['mip_gap']=max(0.,(solver['objective']-solver['dual_bound'])/max(1.,abs(solver['objective'])))
        p.dump(folder/'economic_reference.json',dict(solver=solver,units=u.tolist(),modules=n.tolist(),built=sorted(bs),
            normal=normal,extra=extra,check=check,history=economic_history))
        np.savez_compressed(folder/'economic_solution.npz',solution=z)
        reference=copy.deepcopy(solver);cost_vector=np.array(native.costs)
        reference_z=z.copy()
        break
    else:raise RuntimeError((case,y,'经济参考全时段未闭合'))
    selection_history=[]
    if case in ('elastic_engineering','elastic_balanced') and reference['objective']>1e-6:
        cost_limit=reference['objective']*1.05
        write_warm(inp,warm,y,u,n,bs)
        for iteration in range(1,31):
            native,meta,one=m.build(inp,power,y,case,old,oldn,built,replaced,selected)
            cost_vector=np.array(native.costs)
            native.constraint({j:float(c) for j,c in enumerate(cost_vector) if c},upper=cost_limit)
            native.costs=(cost_vector/max(1.,cost_limit)*1e-4).tolist()
            if case=='elastic_balanced':
                native.constraint({v:1. for v in meta['edgevars'].values()},upper=len(bs))
                native.constraint({v:1. for v in meta['modules'].values()},upper=int(n.sum()))
                for v in meta['edgevars'].values():native.costs[v]+=.5/max(1,len(bs))
                for v in meta['modules'].values():native.costs[v]+=.5/max(10,int(n.sum()))
            else:
                for v in meta['edgevars'].values():native.costs[v]+=1.
            # 相同联络数下压低费用，最后消除不必要的区段切换。
            for v in list(meta['normal_blocks'].values())+list(meta['extra_blocks'].values()):native.costs[v]+=1e-9
            zz,search=p.base.old.old.base.parameters.solve(native,folder,f'engineering_{iteration:02}',seconds,.0001,
                dict(one,storage_usable_energy_fraction=1.),meta,warm)
            if zz is None or not search.get('feasible_incumbent'):
                # 已验证的费用参考自身满足5%及配套设施上限，限时工程搜索无解时保留该可行候选。
                zz=reference_z.copy();search['fallback']='采用已通过全年校核的本年度经济参考整数解'
            uu,nn,bbs,norm,ext=m.layout(inp,zz,meta)
            checked,bad=m.verify(inp,power,y,uu,nn,bbs,norm,ext)
            selection_history.append(dict(iteration=iteration,search=search,verified=checked['verified']))
            print('ANNUAL_SELECT',inp['region_name'],y,iteration,'bad',len(bad),'lines',len(bbs),flush=True)
            if bad:
                assert bad-selected
                selected|=bad;p.dump(progress,dict(selected_pairs=sorted(selected)))
                write_warm(inp,warm,y,uu,nn,bbs);continue
            real_cost=float(cost_vector@zz)
            assert real_cost<=cost_limit+1e-5
            u,n,bs,normal,extra,check,z=uu,nn,bbs,norm,ext,checked,zz
            solver=dict(search,construction_search=copy.deepcopy(search),objective=real_cost,
                dual_bound=reference['dual_bound'],mip_gap=max(0.,(real_cost-reference['dual_bound'])/max(1.,real_cost)),
                feasible_incumbent=True,accepted=False,
                status='本年度经济参考5%费用容差内配套设施工程优选可行方案' if not search.get('fallback')
                       else '工程搜索限时，采用已通过全年校核的本年度费用参考候选')
            break
        else:raise RuntimeError((y,'工程选择全时段未闭合'))
    row=annual_row(inp,y,u,n,bs,old,oldn,built,0.)
    assert abs(row['added_lifecycle_npv_10k']-solver['objective'])<.02,(y,row,solver)
    result=dict(year=y,units=u.tolist(),modules=n.tolist(),built=sorted(bs),normal=normal,extra=extra,
        solver=solver,economic_reference=reference,economic_history=economic_history,selection_history=selection_history,
        selected_pairs=sorted(selected),check=check,annual=row,previous_assets_sha256=p.sha(folder/'previous_assets.json'),
        selection=dict(rule=('固定上年采用资产，本年度经济参考费用5%以内，储能与联络均不高于本方案费用参考，等权最小化两项相对规模'
                if case=='elastic_balanced' else '固定上年采用资产，本年度经济参考费用5%以内优先简化联络'
                if case=='elastic_engineering' else '年度费用参考'),
            tolerance=.05 if case in ('elastic_engineering','elastic_balanced') else 0.,
            premium=(solver['objective']/reference['objective']-1) if reference['objective']>1e-6 else 0.))
    p.dump(state,result);np.savez_compressed(folder/'chosen_solution.npz',solution=z)
    return u,n,bs,normal,extra,result


def run(region,case,seconds=15.):
    inp,powers=p.load(region);ids=list(inp['stations']);folder=p.RAW/region/case;folder.mkdir(exist_ok=True)
    old=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]);oldn=np.zeros(len(ids),int)
    built=set();replaced=np.zeros((len(ids),2),bool);annual=[];stations=[];projects=[];checks=[];transfer=[];history=[]
    basecheck,_=m.verify(inp,powers[2021],2021,old,oldn,built,{},{});p.dump(folder/'baseline_check.json',basecheck)
    baseline=dict(year=2021,peak_mw=inp['annual_observed_peak_mw']['2021'],capacity_mva=float(old.sum()),
        clr=float(old.sum()/inp['annual_observed_peak_mw']['2021']),common_floor=inp['common_floor_by_year']['2021'],
        purchased_transformer_mva=0.,net_capacity_increment_mva=0.,replaced_capacity_mva=0.,new_third_count=0,
        storage_nameplate_mw=0.,storage_mwh=0.,new_storage_mwh=0.,new_lines=0,cumulative_lines=0,
        transformer_capex_10k=0.,storage_capex_10k=0.,line_capex_10k=0.,construction_capex_10k=0.,
        added_lifecycle_npv_10k=0.,cumulative_lifecycle_npv_10k=0.,transformer_npv_10k=0.,storage_npv_10k=0.,line_npv_10k=0.)
    annual.append(baseline);stations.extend(asset_rows(inp,2021,old,oldn));cumulative=0.
    for y in inp['years']:
        stage=folder/str(y);stage.mkdir(exist_ok=True)
        previous=dict(year=y,units=old.tolist(),modules=oldn.tolist(),built=sorted(built),replaced=replaced.tolist(),input_sha256=p.sha(p.RAW/region/'inputs.json'))
        if (stage/'previous_assets.json').exists():assert json.loads((stage/'previous_assets.json').read_text())==previous
        else:p.dump(stage/'previous_assets.json',previous)
        u,n,bs,normal,extra,result=get_stage(inp,powers[y],y,case,old,oldn,built,replaced,stage,seconds)
        assert np.all(u>=old-1e-7) and np.all(n>=oldn) and bs>=built
        changed=u[:,:2]>old[:,:2]+1e-7;assert not np.any(changed&replaced);replaced|=changed
        row=annual_row(inp,y,u,n,bs,old,oldn,built,cumulative);cumulative=row['cumulative_lifecycle_npv_10k']
        assert row['clr']>=row['common_floor']-1e-7
        if case=='rigid':assert u.sum()<=max(old.sum(),2*row['peak_mw'])+1e-6
        annual.append(row);stations.extend(asset_rows(inp,y,u,n));projects.extend(dict(year=y,id=e) for e in sorted(bs-built))
        checks.extend(result['check']['records']);transfer.extend(result['check']['transfers'])
        history.append(dict(year=y,solver=result['solver'],economic_reference=result['economic_reference'],selection=result['selection']))
        old,oldn,built=u,n,bs
        p.write_csv(folder/'years.csv',annual);p.write_csv(folder/'stations.csv',stations)
        p.write_csv(folder/'projects.csv',projects)
        print('YEAR_DONE',region,case,y,'C',u.sum(),'E',n.sum()*.215,'L',len(bs),flush=True)
    p.dump(folder/'summary.json',dict(region=region,case=case,annual=annual,cost_npv_10k=cumulative,
        cost_scope='2022—2035新增工程至2041的费用现值，2021折现基年；既有资产不重复采购',
        planning_method='固定上年采用资产的逐年费用寻优，非全期联合全局最优',history=history,
        baseline_verified=basecheck['verified'],input_sha256=p.sha(p.RAW/region/'inputs.json'),
        scope=inp['scope'],checked_hour_contingency_pairs=sum(r['checked_hours'] for r in checks),verified=True))
    p.dump(folder/'independent_full_year.json',dict(verified=True,records=checks,transfers=transfer,
        scope='固定代理接线及事故预案对补齐后8760小时逐项静态检查，原始缺测标识保留；无SOC优化'))
    print('PLAN_DONE',region,case,cumulative,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--region',choices=p.REGIONS,required=True)
    parser.add_argument('--case',choices=['rigid','elastic_economic','elastic_engineering','elastic_balanced'],required=True)
    parser.add_argument('--seconds',type=float,default=15.);args=parser.parse_args();run(args.region,args.case,args.seconds)
