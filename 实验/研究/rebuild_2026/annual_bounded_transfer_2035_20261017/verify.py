"""重建整数解约束，另按8760小时直接核对固定事故预案。"""
import json

import numpy as np
from scipy.sparse import coo_matrix

from . import model as m, prepare as p
from .run import annual_row

CASES=('rigid','elastic_capacity')


def run():
    results=[];sources=[];total=0;matrix_max=0.;cost_max=0.;max_fraction=0.
    for region in p.REGIONS:
        inp,powers=p.load(region);ids=list(inp['stations'])
        for case in CASES:
            root=p.RAW/region/case;summary=json.loads((root/'summary.json').read_text())
            old=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]);oldn=np.zeros(len(ids),int)
            built=set();replaced=np.zeros((len(ids),2),bool);cumulative=0.;checks=[];transfers=[];limits=[]
            assert [r['year'] for r in summary['annual']]==list(range(2021,2036))
            assert summary['annual'][0]['capacity_mva']==inp['initial_capacity_mva']
            for y in inp['years']:
                stage=root/str(y);r=json.loads((stage/'adopted.json').read_text())
                native,meta,one=m.build(inp,powers[y],y,case,old,oldn,built,replaced,{tuple(v) for v in r['selected_pairs']})
                z=np.load(stage/'chosen_solution.npz')['solution'];assert len(z)==len(native.costs)
                rr,cc,vv=zip(*native.entries)
                value=coo_matrix((vv,(rr,cc)),shape=(len(native.constraint_lower),len(z))).tocsr()@z
                integer=np.array(native.integrality,dtype=bool)
                error=max(0.,float(np.max(np.array(native.constraint_lower)-value)),float(np.max(value-np.array(native.constraint_upper))),
                    float(np.max(np.array(native.lower_bounds)-z)),float(np.max(z-np.array(native.upper_bounds))),
                    float(np.max(abs(z[integer]-np.round(z[integer])))))
                assert error<1e-5,(region,case,y,error);matrix_max=max(matrix_max,error)
                u,n,bs,normal,extra=m.layout(inp,z,meta)
                assert np.array_equal(u,np.array(r['units'])) and np.array_equal(n,np.array(r['modules']))
                assert bs==set(r['built']) and normal=={int(k):v for k,v in r['normal'].items()} and extra=={int(k):v for k,v in r['extra'].items()}
                checked,bad=m.verify(inp,powers[y],y,u,n,bs,normal,extra);assert not bad
                assert np.all(u>=old) and np.all(n>=oldn) and bs>=built
                changed=u[:,:2]>old[:,:2]+1e-7;assert not np.any(changed&replaced);replaced|=changed
                for j,sid in enumerate(ids):
                    assert all(u[j,slot]>=inp['replacement_rating_target_mva'][sid] for slot in (0,1) if changed[j,slot])
                # 独立必要条件：本站事故至多转出20%源荷，不能靠别站无条件承担剩余部分。
                for j,sid in enumerate(ids):
                    fraction=sum(c for k,c in extra.items() if meta['arcs'][k]['source']==sid)/inp['block_count'][sid]
                    assert fraction<=.2+1e-9;max_fraction=max(max_fraction,fraction)
                    firm=.95*(u[j].sum()-u[j].max())
                    for sign,duration in ((1,'forward_duration_h'),(-1,'reverse_duration_h')):
                        need=max(0.,float((sign*powers[y][:,j]).max()))*(1-fraction)
                        support=min(.1,.215*.76/max(1,inp['stations'][sid][duration]))*n[j]
                        assert firm+support>=need-1e-5,(region,case,y,sid,need,firm+support)
                row=annual_row(inp,y,u,n,bs,old,oldn,built,cumulative)
                for key,value in row.items():assert abs(value-summary['annual'][y-2021][key])<1e-5,(region,case,y,key)
                cost_error=abs(float(np.array(native.costs)@z)-row['added_lifecycle_npv_10k'])
                assert cost_error<.02;cost_max=max(cost_max,cost_error)
                assert row['clr']>=inp['common_floor_by_year'][str(y)]-1e-7
                if case=='rigid':assert u.sum()<=max(old.sum(),2*row['peak_mw'])+1e-6
                else:
                    support_cost=row['storage_npv_10k']+row['line_npv_10k']
                    assert support_cost<=r['support_limit_npv_10k']*(1+r['support_tolerance'])+1e-4 and len(bs)<=r['line_limit']
                for record in checked['records']:record['verified']=record['max_deficit_mw']<1e-5
                checks.extend(checked['records']);transfers.extend(checked['transfers'])
                limits.extend(dict(year=y,**record) for record in checked['station_transfer_limits'])
                total+=checked['checked_hour_contingency_pairs'];cumulative=row['cumulative_lifecycle_npv_10k'];old,oldn,built=u,n,bs
            assert abs(cumulative-summary['cost_npv_10k'])<1e-5
            p.dump(root/'independent_lp.json',dict(verified=True,method='固定供区矩阵对全年逐小时直接校核，非LP求解',
                records=checks,transfers=transfers,limits=limits,base_year_scope='2021固定起点缺口单列；规划年度为2022—2035'))
            files=['summary.json','stations.csv','projects.csv','years.csv','independent_lp.json','baseline_check.json']
            files.extend(f'{y}/{name}' for y in inp['years'] for name in ['adopted.json','previous_assets.json','chosen_solution.npz'])
            refs=['support_reference.json','support_solution.npz'] if case=='elastic_capacity' else ['economic_reference.json','economic_solution.npz']
            files.extend(f'{y}/{name}' for y in inp['years'] for name in refs)
            sources.append(dict(folder=str(root.relative_to(p.ROOT)),files={f:p.sha(root/f) for f in files}))
            results.append(dict(region=region,case=case,verified=True,years=15,cost_npv_10k=cumulative))
            print('VERIFIED_BOUNDED',region,case,cumulative,flush=True)
    proof=dict(verified=True,artifact_kind='annual_bounded_transfer_planning',schemes=results,solution_sources=sources,
        full_hour_pairs=total,planning_years=[2022,2035],display_years=[2021,2035],max_matrix_error=matrix_max,
        max_cost_error_10k=cost_max,max_transfer_fraction=max_fraction,
        limitation='20%为共同研究情景限额，正常不跨站；采购按远景选型。代理接线及静态储能，非真实竣工方案、非连续SOC调度、非全期联合最优。2021固定基线缺口单列。')
    p.dump(p.REVIEW/'逐年方案独立核验.json',proof)
    return proof


if __name__=='__main__':run()
