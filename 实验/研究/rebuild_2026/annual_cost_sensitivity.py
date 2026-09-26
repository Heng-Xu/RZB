"""独立价格系数敏感性：同一 v4 约束、源荷和网络，完整重求四年路径。"""
from pathlib import Path
import json
from .baseline_historical_proxy import build
from .baseline_2021 import read_csv
from .simulation_reserve_policy import OUTPUT, SETTINGS
from .joint_lifecycle_optimizer import load_inputs, solve_layer, cost_factors, DESIGNED_NEW_LINE_KM, LINE_BASE_10K_PER_KM
from .city_mapping_audit import write_csv

DEST=OUTPUT/'recommendation_matrix/cost_sensitivity'
CASES=[('transformer_0_7',.7,1.,1.),('storage_1_5',1.,1.5,1.),('line_1_5',1.,1.,1.5)]

def run(output_dir=DEST):
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    stations,_=build();baseline={(r['study_region_id'],int(r['voltage_kv']),r['model_station_id']):r for r in stations}
    _,scenes,durations,peaks,catalog,coefficients=load_inputs()
    layer=('QX-00005',110);setting=SETTINGS[layer];results=[];annual=[];recommend=[]
    for case,tp,sp,lp in [('base',1.,1.,1.)]+CASES:
        pair={}
        for scheme in ('rigid','elastic'):
            rigid=scheme=='rigid';stem=f'{case}_{scheme}'
            print('START',stem,flush=True)
            if case=='base':
                years=read_csv(OUTPUT/f'{scheme}_{layer[0]}_{layer[1]}_years.csv')
                summary=next(r for r in read_csv(OUTPUT/'summary.csv') if r['study_region_id']==layer[0] and int(r['voltage_kv'])==layer[1] and r['scheme']==scheme)
                for row in years:row['year']=int(row['year'])
            else:
                try:
                    selected,years,ties,summary=solve_layer(layer,baseline,scenes,durations,peaks,catalog,coefficients,cost_factors(),2. if rigid else 3.2,rigid,
                        include_new_line=True,new_line_variant='designed_bus',line_km=DESIGNED_NEW_LINE_KM,line_unit_cost=LINE_BASE_10K_PER_KM*lp,
                        tie_allowed=True,transformer_cost_scale=tp,storage_cost_scale=sp,policy_peak_basis='annual',max_storage_modules=50,
                        allow_capacity_release=True,capacity_growth_budget_fraction=setting['rigid_budget'] if rigid else None,
                        prefer_reserve_at_equal_cost=True,contingency_service_fraction=setting['contingency_fraction'],require_existing_tie_operation=False,
                        tie_year_basis='annual_station_scaled',canonicalize_tie_dispatch=True)
                    write_csv(selected,out/f'{stem}_stations.csv');write_csv(years,out/f'{stem}_years.csv');write_csv(ties,out/f'{stem}_ties.csv')
                except ValueError as e:
                    results.append({'case_id':case,'scheme':scheme,'transformer_scale':tp,'storage_scale':sp,'line_scale':lp,'status':'infeasible' if 'infeasible' in str(e).lower() else 'unproven_solver_result','cost_npv_10k_cny':'','detail':str(e)})
                    write_csv(results,out/'summary.csv')
                    raise RuntimeError(f'{stem} 未完整求得最优路径，停止敏感性: {e}') from e
            cost=float(summary['objective_npv_10k_cny'])
            results.append({'case_id':case,'scheme':scheme,'transformer_scale':tp,'storage_scale':sp,'line_scale':lp,'status':'optimal','cost_npv_10k_cny':cost,'detail':''})
            pair[scheme]=(years,cost)
            for row in years:
                annual.append({'case_id':case,'scheme':scheme,'year':int(row['year']),'transformer_scale':tp,'storage_scale':sp,'line_scale':lp,
                    'transformer_storage_relative_cost_multiplier':tp/sp,'line_storage_relative_cost_multiplier':lp/sp,
                    'capacity_mva':float(row['selected_capacity_mva']),'clr':float(row['actual_clr']),'storage_modules':int(row['storage_modules_in_service']),
                    'line_built':int(row['line_built']),'year_lifecycle_npv_10k_cny':float(row['year_lifecycle_npv_10k_cny']),'path_npv_10k_cny':cost})
            write_csv(results,out/'summary.csv');write_csv(annual,out/'annual_schemes.csv')
            print('DONE',stem,cost,flush=True)
        chosen='elastic' if pair['elastic'][1]<=pair['rigid'][1]+1e-5 else 'rigid'
        for r in pair[chosen][0]:recommend.append({'case_id':case,'study_region_id':layer[0],'voltage_kv':layer[1],'year':int(r['year']),
             'transformer_scale':tp,'storage_scale':sp,'line_scale':lp,'recommended_scheme':chosen,'recommended_clr':float(r['actual_clr']),
             'recommended_capacity_mva':float(r['selected_capacity_mva']),'storage_modules':int(r['storage_modules_in_service']),
             'rigid_path_npv_10k_cny':pair['rigid'][1],'elastic_path_npv_10k_cny':pair['elastic'][1],'scope':'pizhou_110_representative_case_not_all_regions'})
        write_csv(recommend,out/'annual_recommendations.csv')
    audit={'status':'PASS','case_count':4,'proven_path_count':len(results),'annual_scheme_rows':len(annual),'recommendation_rows':len(recommend),'scope':'one_factor_at_a_time_same_physical_inputs_complete_path_cost_comparison'}
    assert len(results)==8 and len(annual)==32 and len(recommend)==16
    for r in results:
        total=sum(x['year_lifecycle_npv_10k_cny'] for x in annual if x['case_id']==r['case_id'] and x['scheme']==r['scheme'])
        assert abs(total-r['cost_npv_10k_cny'])<1e-3
    (out/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
    return audit

if __name__=='__main__':print(run())
