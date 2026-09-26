"""用原始加工输入独立复核年度参数、推荐路径选择和成本。"""
import json,math
from .baseline_2021 import read_csv
from .hourly_source_profile import OUTPUT_DIR
from .simulation_reserve_policy import OUTPUT
from .annual_recommendation_matrix import DEST


def audit():
    rows=read_csv(DEST/'annual_indicator_recommendation.csv');problems=[]
    peaks={(r['study_region_id'],int(r['voltage_kv']),int(r['year'])):float(r['estimated_synchronous_forward_peak_mw']) for r in read_csv(OUTPUT_DIR/'annual_forward_layer_scenes_2021_2025.csv')}
    reverse=read_csv(OUTPUT_DIR/'annual_reverse_station_proxy_2021_2025.csv')
    durations=read_csv(OUTPUT_DIR/'static_storage_need_screen_2025.csv')
    sums=read_csv(OUTPUT/'summary.csv')
    for r in rows:
        layer=r['study_region_id'],int(r['voltage_kv']);year=int(r['year']);prefix=f'{layer}-{year}'
        def check(key,value,tol=1e-6):
            if not math.isclose(float(r[key]),value,abs_tol=tol,rel_tol=1e-8):problems.append(f'{prefix}: {key}')
        p=peaks[*layer,year]
        check('forward_reference_peak_mw',p)
        check('net_peak_cagr_since_2021',(p/peaks[*layer,2021])**(1/(year-2021))-1)
        check('net_peak_yoy_growth',p/peaks[*layer,year-1]-1)
        proxy=[x for x in reverse if (x['study_region_id'],int(x['voltage_kv']))==layer and int(x['year'])==year and x['variant']=='night_central']
        check('source_load_output_proxy_ratio',sum(float(x['annual_pv_scale'])*float(x['pv_output_proxy_mw_2025']) for x in proxy)/sum(float(x['annual_load_scale'])*float(x['gross_load_proxy_mw_2025']) for x in proxy))
        ds=[x for x in durations if (x['study_region_id'],int(x['voltage_kv']))==layer and x['capacity_case']=='hold_2021_simulation_capacity']
        for d in ('forward','reverse'):check(f'{d}_d95_max_template_hours',max(int(x[f'{d}_d95_max_run_hours']) for x in ds))
        costs={s['scheme']:float(s['objective_npv_10k_cny']) for s in sums if (s['study_region_id'],int(s['voltage_kv']))==layer}
        chosen='elastic' if costs['elastic']<=costs['rigid']+1e-5 else 'rigid'
        if r['recommended_scheme']!=chosen:problems.append(f'{prefix}: cost choice')
        yy=next(x for x in read_csv(OUTPUT/f'{chosen}_{layer[0]}_{layer[1]}_years.csv') if int(x['year'])==year)
        check('recommended_capacity_mva',float(yy['selected_capacity_mva']))
        check('recommended_clr',float(yy['selected_capacity_mva'])/p)
        check('year_investment_lifecycle_npv_10k_cny',float(yy['year_lifecycle_npv_10k_cny']))
    if len(rows)!=12 or len({(r['study_region_id'],r['voltage_kv'],r['year']) for r in rows})!=12:problems.append('expected 12 unique annual cases')
    result={'status':'PASS' if not problems else 'FAIL','annual_cases':len(rows),'problems':problems}
    (DEST/'independent_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    if problems:raise ValueError(problems)
    return result

if __name__=='__main__':print(audit())
