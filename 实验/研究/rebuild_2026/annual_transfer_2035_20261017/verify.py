"""从原始整数解重建约束、供区矩阵和费用，不复用导出表的合计。"""
import json

import numpy as np
from scipy.sparse import coo_matrix

from . import model as m, prepare as p
from .run import annual_row

CASES=('rigid','elastic_reserve')


def run():
    results=[];sources=[];total=0;matrix_max=0.;cost_max=0.
    for region in p.REGIONS:
        inp,powers=p.load(region);ids=list(inp['stations'])
        for case in CASES:
            folder=p.RAW/region/case;summary=json.loads((folder/'summary.json').read_text())
            old=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]);oldn=np.zeros(len(ids),int)
            built=set();replaced=np.zeros((len(ids),2),bool);cumulative=0.;checks=[];transfer=[]
            assert [r['year'] for r in summary['annual']]==list(range(2021,2036))
            assert summary['annual'][0]['capacity_mva']==inp['initial_capacity_mva']
            for y in inp['years']:
                stage=folder/str(y);r=json.loads((stage/'adopted.json').read_text())
                selected={tuple(v) for v in r['selected_pairs']}
                native,meta,one=m.build(inp,powers[y],y,case,old,oldn,built,replaced,selected)
                z=np.load(stage/'chosen_solution.npz')['solution']
                assert len(z)==len(native.costs)
                rr,cc,vv=zip(*native.entries)
                A=coo_matrix((vv,(rr,cc)),shape=(len(native.constraint_lower),len(z))).tocsr()
                value=A@z;integer=np.array(native.integrality,dtype=bool)
                error=max(0.,float(np.max(np.array(native.constraint_lower)-value)),
                    float(np.max(value-np.array(native.constraint_upper))),float(np.max(np.array(native.lower_bounds)-z)),
                    float(np.max(z-np.array(native.upper_bounds))),float(np.max(abs(z[integer]-np.round(z[integer])))))
                assert error<1e-5,(region,case,y,error);matrix_max=max(matrix_max,error)
                u,n,bs,normal,extra=m.layout(inp,z,meta)
                assert np.array_equal(u,np.array(r['units'])) and np.array_equal(n,np.array(r['modules']))
                assert normal=={int(k):v for k,v in r['normal'].items()} and extra=={int(k):v for k,v in r['extra'].items()}
                checked,bad=m.verify(inp,powers[y],y,u,n,bs,normal,extra);assert not bad
                assert np.all(u>=old-1e-7) and np.all(n>=oldn) and bs>=built
                changed=u[:,:2]>old[:,:2]+1e-7;assert not np.any(changed&replaced);replaced|=changed
                row=annual_row(inp,y,u,n,bs,old,oldn,built,cumulative)
                for key,value in row.items():
                    assert abs(value-summary['annual'][y-2021][key])<1e-5,(region,case,y,key)
                cost_error=abs(float(np.array(native.costs)@z)-row['added_lifecycle_npv_10k'])
                assert cost_error<.02;cost_max=max(cost_max,cost_error)
                assert row['clr']>=inp['common_floor_by_year'][str(y)]-1e-7
                if case=='rigid':assert u.sum()<=max(old.sum(),2*row['peak_mw'])+1e-6
                else:
                    assert row['added_lifecycle_npv_10k']<=1.05*r['economic_reference']['objective']+1e-5
                    reference=json.loads((stage/'economic_reference.json').read_text())
                    assert n.sum()<=sum(reference['modules']) and len(bs)<=len(reference['built'])
                for record in checked['records']:record['verified']=record['max_deficit_mw']<1e-5
                checks.extend(checked['records']);transfer.extend(checked['transfers'])
                total+=checked['checked_hour_contingency_pairs']
                cumulative=row['cumulative_lifecycle_npv_10k'];old,oldn,built=u,n,bs
            assert abs(cumulative-summary['cost_npv_10k'])<1e-5
            # 文件名兼容项目既有核验入口，method明确本次是固定预案的直接矩阵校核。
            p.dump(folder/'independent_lp.json',dict(verified=True,method='固定供区矩阵对全年逐小时直接校核，非LP求解',
                records=checks,transfers=transfer,base_year_scope='2021是固定基线，其零切换缺口另列，不列入规划年度通过数'))
            files=['summary.json','stations.csv','projects.csv','years.csv','independent_lp.json','baseline_check.json']
            files.extend(f'{y}/{name}' for y in inp['years'] for name in
                         ['adopted.json','previous_assets.json','chosen_solution.npz','economic_reference.json','economic_solution.npz'])
            sources.append(dict(folder=str(folder.relative_to(p.ROOT)),files={f:p.sha(folder/f) for f in files}))
            results.append(dict(region=region,case=case,verified=True,years=15,cost_npv_10k=cumulative,
                                checked_pairs=sum(r['checked_hours'] for r in checks)))
            print('VERIFIED_ANNUAL',region,case,cumulative,flush=True)
    proof=dict(verified=True,artifact_kind='annual_fixed_block_planning',schemes=results,solution_sources=sources,
        full_hour_pairs=total,planning_years=[2022,2035],display_years=[2021,2035],
        max_matrix_error=matrix_max,max_cost_error_10k=cost_max,
        limitation='代理区段与候选网络的静态逐年可行方案，非真实竣工拓扑、非连续SOC调度、非全期联合全局最优；2021固定基线缺口单列')
    p.dump(p.REVIEW/'逐年方案独立核验.json',proof)
    return proof


if __name__=='__main__':run()
