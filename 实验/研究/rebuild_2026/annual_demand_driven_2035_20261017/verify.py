"""重建年度整数解，独立核对8760小时、原始转供证据与费用。"""
import json

import numpy as np
from openpyxl import load_workbook
from scipy.sparse import coo_matrix

from . import model as m, prepare as p
from .. import current_economic_assumptions as econ
from ..case_parameters_20261012.run import TRANSFER_FILE

CASES=('rigid','elastic_capacity','elastic_engineering')


def independent_cost(inp,y,old,oldn,built,u,n,bs):
    purchased=sum(u[j,k] for j in range(len(u)) for k in (0,1) if u[j,k]>old[j,k]+1e-7)
    thirds=int(np.sum(u[:,2]>old[:,2]+1e-7))
    capex=[purchased*inp['transformer_price_10k_per_purchased_mva']+thirds*inp['third_50mva_capex_10k'],
           int(np.sum(n-oldn))*inp['storage_module_capex_10k'],len(bs-built)*inp['line_capex_10k']]
    npvs=[]
    for kind,cost,life,om in zip(('transformer','storage','line'),capex,
            (econ.TRANSFORMER_LIFE,econ.STORAGE_LIFE,econ.LINE_LIFE),
            (econ.TRANSFORMER_OM,econ.STORAGE_OM,econ.LINE_OM)):
        factor=(1+econ.DISCOUNT_RATE)**(2021-y)
        renewal=y+life
        while renewal<2041:
            factor+=(1+econ.DISCOUNT_RATE)**(2021-renewal);renewal+=life
        factor+=sum(om/(1+econ.DISCOUNT_RATE)**(t-2021) for t in range(y+1,2042))
        assert abs(factor-inp['cost_factors'][kind][str(y)])<1e-10
        npvs.append(cost*factor)
    return purchased+50*thirds,capex,npvs


def run():
    wb=load_workbook(TRANSFER_FILE,read_only=True,data_only=True)
    original=list(wb.worksheets[0].values);wb.close()
    sources=[];results=[];total=0;primary_total=0;matrix_max=0.;cost_max=0.;evidence_rows=[];cost_rows=[]
    for region in p.REGIONS:
        inp,powers=p.load(region);ids=list(inp['stations'])
        assert inp['forecast_basis']['sha256']==p.sha(p.ROOT/inp['forecast_basis']['source'])
        assert len(powers)==15 and all(v.shape==(8760,len(ids)) for v in powers.values())
        for record in inp['station_transfer_evidence']:
            sid=record['station'];jmw=record['transferable_mw']
            if record['matched']:
                raw=original[record['source_row']-1]
                assert raw[2]==record['name'] and abs(raw[9]-jmw)<1e-9
                assert abs(raw[10]-record['unserved_mw'])<1e-9
            else:assert jmw==0.
            assert all(inp['existing_transfer_budget_by_year_mw'][str(y)][sid]==jmw for y in powers)
            evidence_rows.append(dict(地区=p.REGIONS[region],变电站=sid,站名=record['name'],
                原表行号=record['source_row'],原表能力_MW=jmw,有原表对应=record['matched']))
        for case in CASES:
            root=p.RAW/region/case;summary=json.loads((root/'summary.json').read_text())
            assert summary['input_sha256']==p.sha(p.RAW/region/'inputs.json')
            assert [r['year'] for r in summary['annual']]==list(range(2021,2036))
            old=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]);oldn=np.zeros(len(ids),int)
            built=set();replaced=np.zeros((len(ids),2),bool);cumulative=0.;records=[];transfers=[]
            assert old.sum()==inp['initial_capacity_mva']==summary['annual'][0]['capacity_mva']
            baseline=json.loads((p.RAW/region/'baseline/adopted.json').read_text())
            baseline_check,_=m.verify(inp,powers[2021],2021,old,oldn,built,
                {int(k):v for k,v in baseline['normal'].items()},{int(k):v for k,v in baseline['extra'].items()})
            assert baseline_check['verified']==summary['baseline_verified']
            p.dump(root/'baseline_check.json',baseline_check)
            for y in inp['years']:
                stage=root/str(y);r=json.loads((stage/'adopted.json').read_text())
                previous=json.loads((stage/'previous_assets.json').read_text())
                assert previous==dict(year=y,units=old.tolist(),modules=oldn.tolist(),built=sorted(built),
                    replaced=replaced.tolist(),input_sha256=p.sha(p.RAW/region/'inputs.json'))
                assert r['previous_assets_sha256']==p.sha(stage/'previous_assets.json')
                native,meta,_=m.build(inp,powers[y],y,case,old,oldn,built,replaced,{tuple(v) for v in r['selected_pairs']})
                z=np.load(stage/'chosen_solution.npz')['solution'];assert len(z)==len(native.costs)
                rr,cc,vv=zip(*native.entries)
                lhs=coo_matrix((vv,(rr,cc)),shape=(len(native.constraint_lower),len(z))).tocsr()@z
                ints=np.array(native.integrality,dtype=bool)
                err=max(0.,float(np.max(np.array(native.constraint_lower)-lhs)),float(np.max(lhs-np.array(native.constraint_upper))),
                    float(np.max(np.array(native.lower_bounds)-z)),float(np.max(z-np.array(native.upper_bounds))),
                    float(np.max(abs(z[ints]-np.round(z[ints])))))
                assert err<1e-5,(region,case,y,err);matrix_max=max(matrix_max,err)
                u,n,bs,normal,extra=m.layout(inp,z,meta)
                np.testing.assert_array_equal(u,r['units']);np.testing.assert_array_equal(n,r['modules'])
                assert bs==set(r['built']) and normal=={int(k):v for k,v in r['normal'].items()}
                assert extra=={int(k):v for k,v in r['extra'].items()}
                checked,bad=m.verify(inp,powers[y],y,u,n,bs,normal,extra);assert not bad
                assert np.all(u>=old) and np.all(n>=oldn) and bs>=built
                changed=u[:,:2]>old[:,:2]+1e-7;assert not np.any(changed&replaced)
                replaced|=changed
                a=summary['annual'][y-2021]
                purchased,capex,npvs=independent_cost(inp,y,old,oldn,built,u,n,bs)
                cumulative+=sum(npvs)
                expected=dict(capacity_mva=float(u.sum()),clr=float(u.sum()/inp['annual_observed_peak_mw'][str(y)]),
                    purchased_transformer_mva=float(purchased),net_capacity_increment_mva=float(u.sum()-old.sum()),
                    replaced_capacity_mva=float(purchased-u.sum()+old.sum()),storage_nameplate_mw=float(n.sum()*.1),
                    storage_mwh=float(n.sum()*.215),new_storage_mwh=float((n-oldn).sum()*.215),
                    new_lines=len(bs-built),cumulative_lines=len(bs),construction_capex_10k=sum(capex),
                    added_lifecycle_npv_10k=sum(npvs),cumulative_lifecycle_npv_10k=cumulative)
                expected.update(dict(zip(('transformer_capex_10k','storage_capex_10k','line_capex_10k'),capex)))
                expected.update(dict(zip(('transformer_npv_10k','storage_npv_10k','line_npv_10k'),npvs)))
                for key,value in expected.items():assert abs(value-a[key])<1e-5,(region,case,y,key)
                err=abs(float(np.array(native.costs)@z)-sum(npvs));cost_max=max(cost_max,err)
                assert err<1e-5 and abs(r['solver']['objective']-sum(npvs))<1e-5
                if case=='elastic_capacity':
                    reference=json.loads((stage/'support_reference.json').read_text())
                    assert npvs[1]+npvs[2]<=r['support_limit_npv_10k']*(1+r['support_tolerance'])+1e-4
                    assert len(bs)<=r['line_limit']
                    lower=r['solver']['dual_bound']
                    ref_cost=None
                    assert reference['solver']['dual_bound']<=reference['support_limit_npv_10k']+1e-5
                else:
                    reference=r['economic_reference'];lower=reference['dual_bound'];ref_cost=reference['objective']
                    assert lower<=ref_cost+1e-5 and lower<=sum(npvs)+1e-5
                    if case=='elastic_engineering':assert sum(npvs)<=max(0.,ref_cost)*1.05+1e-5
                assert a['clr']>=a['common_floor']-1e-8
                if case=='rigid':assert u.sum()<=max(old.sum(),2*a['peak_mw'])+1e-6
                cost_rows.append(dict(地区=p.REGIONS[region],方案=case,年份=y,采用费用现值_万元=sum(npvs),
                    年度经济参考_万元=ref_cost,年度条件下界_万元=lower,
                    采用费用距下界比例=max(0.,(sum(npvs)-lower)/max(1.,abs(sum(npvs)))),
                    主变费用_万元=npvs[0],储能费用_万元=npvs[1],联络费用_万元=npvs[2]))
                for item in checked['records']:item['verified']=item['max_deficit_mw']<1e-5
                records.extend(checked['records']);transfers.extend(checked['transfers'])
                total+=checked['checked_hour_contingency_pairs'];old,oldn,built=u,n,bs
                if case!='elastic_engineering':primary_total+=checked['checked_hour_contingency_pairs']
            assert abs(cumulative-summary['cost_npv_10k'])<1e-5
            p.dump(root/'independent_lp.json',dict(verified=True,records=records,transfers=transfers,
                method='固定预案矩阵逐小时直接计算；另重建全部整数约束和独立资产差量费用'))
            files=['summary.json','years.csv','stations.csv','projects.csv','baseline_check.json','independent_lp.json']
            refs=('support_reference.json','support_solution.npz') if case=='elastic_capacity' else ('economic_reference.json','economic_solution.npz')
            files.extend(f'{y}/{name}' for y in inp['years'] for name in ('adopted.json','previous_assets.json','chosen_solution.npz',*refs))
            sources.append(dict(folder=str(root.relative_to(p.ROOT)),files={f:p.sha(root/f) for f in files}))
            results.append(dict(region=region,case=case,verified=True,cost_npv_10k=cumulative,
                baseline_verified=summary['baseline_verified']))
            print('VERIFIED_DEMAND',region,case,cumulative,flush=True)
    p.write_csv(p.REVIEW/'年度费用独立复算.csv',cost_rows)
    p.write_csv(p.SOURCE/'既有转供逐站原表核对.csv',evidence_rows)
    p.dump(p.SOURCE/'转供证据来源.json',dict(path=str(TRANSFER_FILE.relative_to(p.ROOT)),sha256=p.sha(TRANSFER_FILE),
        matched_stations=sum(r['有原表对应'] for r in evidence_rows),
        unmatched_policy='三个模拟站既有能力均按零；原表为2025收资上限，早期年度可用性仍是回算假设'))
    proof=dict(verified=True,artifact_kind='annual_demand_driven_planning',schemes=results,solution_sources=sources,full_hour_pairs=total,
        primary_hour_pairs=primary_total,planning_years=[2022,2035],display_years=[2021,2035],max_matrix_error=matrix_max,max_cost_error_10k=cost_max,
        limitation='2021基期事故缺口单列；2025收资能力用于早期回算，EQ路径为代理；储能静态时长，无连续SOC；逐年条件费用下界不能相加称全期最优下界')
    p.dump(p.REVIEW/'逐年方案独立核验.json',proof)
    return proof


if __name__=='__main__':run()
