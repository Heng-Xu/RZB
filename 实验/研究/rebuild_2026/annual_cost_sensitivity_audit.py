"""价格敏感性独立复核：逐站约束、费用、年度选择及成本单调性。"""
import json,math
from .annual_cost_sensitivity import DEST
from .baseline_2021 import read_csv
from .simulation_reserve_policy import OUTPUT
from .hourly_source_profile import OUTPUT_DIR


def audit():
    summary=read_csv(DEST/'summary.csv');annual=read_csv(DEST/'annual_schemes.csv');recommend=read_csv(DEST/'annual_recommendations.csv')
    durations={r['model_station_id']:r for r in read_csv(OUTPUT_DIR/'static_storage_need_screen_2025.csv') if r['study_region_id']=='QX-00005' and int(r['voltage_kv'])==110 and r['capacity_case']=='hold_2021_simulation_capacity'}
    peaks={int(r['year']):float(r['reported_downward_load_mw']) for r in read_csv(OUTPUT_DIR/'official_annual.csv') if r['region_id']=='QX-00005' and int(r['voltage_kv'])==110}
    initial=sum(float(r['simulation_capacity_mva_2021']) for r in read_csv(OUTPUT/'baseline_stations.csv') if r['study_region_id']=='QX-00005' and int(r['voltage_kv'])==110)
    problems=[];checks=0
    def check(ok,message):
        nonlocal checks
        checks+=1
        if not ok:problems.append(message)
    def factor(year,life,om):
        return sum((1 if t==year or (t>year and (t-year)%life==0 and t<2041) else 0)/(1.06**(t-2021))+(om/(1.06**(t-2021)) if t>year else 0) for t in range(year,2042))
    costs={(r['case_id'],r['scheme']):float(r['cost_npv_10k_cny']) for r in summary}
    for s in summary:
        case,scheme=s['case_id'],s['scheme'];stem=f'{case}_{scheme}'
        if case=='base':p=OUTPUT;prefix=f'{scheme}_QX-00005_110'
        else:p=DEST;prefix=stem
        stations=read_csv(p/f'{prefix}_stations.csv');years=read_csv(p/f'{prefix}_years.csv');ties=read_csv(p/f'{prefix}_ties.csv')
        check(len(stations)==80 and len(years)==4,f'{stem} dimensions')
        gross=0
        for r in stations:
            station=r['model_station_id'];year=int(r['year']);units=[float(r[f'selected_unit_{i}_mva']) for i in [1,2]]
            gross+=sum(max(0,float(r[f'selected_unit_{i}_mva'])-float(r[f'prior_unit_{i}_mva'])) for i in [1,2])
            modules=int(r['storage_modules_in_service']);d=durations[station]
            for direction in ['forward','reverse']:
                h=int(d[f'{direction}_d95_max_run_hours']);effect=modules*(min(.1,.215/h) if h>0 else .1)
                out=sum(float(t['transfer_mw'])*((t['donor_station_id']==station)-(t['receiver_station_id']==station)) for t in ties if int(t['year'])==year and t['scenario']==direction)
                demand=float(r[f'{direction}_screen_mw']);f=.95 if direction=='forward' else .76
                check(f*sum(units)+effect+out>=demand-1e-5,f'{stem} {station} {year} {direction} supply')
                if direction=='forward':check(.95*min(units)+effect+.6*out>=.6*demand-1e-5,f'{stem} {station} {year} contingency')
            expected=(float(r['transformer_capex_10k_cny'])*factor(year,20,.01)+float(r['storage_capex_10k_cny'])*factor(year,10,.03))
            declared=float(r['transformer_lifecycle_npv_10k_cny'])+float(r['storage_lifecycle_npv_10k_cny'])
            check(abs(expected-declared)<1e-4,f'{stem} {station} {year} discounted cashflows')
        if scheme=='rigid':check(gross<=.03*initial+1e-5,f'{stem} gross expansion budget')
        for y in years:
            yy=int(y['year']);capacity=sum(float(r['selected_capacity_mva']) for r in stations if int(r['year'])==yy)
            check(abs(capacity-float(y['selected_capacity_mva']))<1e-5,f'{stem} {yy} capacity sum')
            check(abs(capacity/peaks[yy]-float(y['actual_clr']))<1e-6,f'{stem} {yy} clr')
            if scheme=='rigid':check(capacity/peaks[yy]<=2+1e-8,f'{stem} {yy} rigid cap')
            declared=sum(float(r['transformer_lifecycle_npv_10k_cny'])+float(r['storage_lifecycle_npv_10k_cny']) for r in stations if int(r['year'])==yy)+float(y['new_line_capex_10k_cny'])*factor(yy,20,.01)
            check(abs(declared-float(y['year_lifecycle_npv_10k_cny']))<1e-4,f'{stem} {yy} year NPV')
        check(abs(sum(float(y['year_lifecycle_npv_10k_cny']) for y in years)-costs[case,scheme])<1e-3,f'{stem} path NPV')
    for r in recommend:
        case=r['case_id'];chosen='elastic' if costs[case,'elastic']<=costs[case,'rigid']+1e-5 else 'rigid'
        check(r['recommended_scheme']==chosen,f'{case} selected cheapest complete path')
        a=next(x for x in annual if x['case_id']==case and x['scheme']==chosen and x['year']==r['year'])
        check(abs(float(r['recommended_clr'])-float(a['clr']))<1e-8,f'{case} recommendation ratio')
    for scheme in ['rigid','elastic']:
        check(costs['transformer_0_7',scheme]<=costs['base',scheme]+1e-3,f'{scheme} cheaper transformers cannot raise optimal cost')
        for case in ['storage_1_5','line_1_5']:check(costs[case,scheme]>=costs['base',scheme]-1e-3,f'{case} {scheme} price monotonicity')
    check(len(summary)==8 and len(annual)==32 and len(recommend)==16,'complete matrix dimensions')
    result={'status':'PASS' if not problems else 'FAIL','checks':checks,'paths':len(summary),'problems':problems,'cashflow_discount_origin':2021,'period':'2022-2041'}
    (DEST/'independent_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    if problems:raise ValueError(problems)
    return result

if __name__=='__main__':print(audit())
