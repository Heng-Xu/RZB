"""把 reserve_policy_v4 完整路径映射为逐年指标案例；不拟造通用函数。"""
from pathlib import Path
import csv,json,hashlib,itertools
import numpy as np
from scipy.stats import spearmanr
from .simulation_reserve_policy import OUTPUT, SETTINGS
from .joint_lifecycle_optimizer import load_inputs,cost_factors
from .baseline_2021 import read_csv
from .city_mapping_audit import write_csv
from .hourly_source_profile import OUTPUT_DIR

DEST=OUTPUT/'recommendation_matrix'
FEATURES=('source_load_output_proxy_ratio','net_peak_cagr_since_2021','forward_reference_peak_mw','reverse_station_peak_max_mw','forward_d95_max_template_hours','reverse_d95_max_template_hours')

def build(output_dir=DEST):
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    _,scenes,durations,peaks,_,coeffs=load_inputs()
    reverse={(r['study_region_id'],int(r['voltage_kv']),r['model_station_id'],int(r['year'])):r for r in read_csv(OUTPUT_DIR/'annual_reverse_station_proxy_2021_2025.csv') if r['variant']=='night_central'}
    base={(r['study_region_id'],int(r['voltage_kv'])):float(r['proxy_capacity_mva']) for r in read_csv(OUTPUT/'baseline_layers.csv')}
    rows=[]
    for m in read_csv(OUTPUT/'annual_matrix.csv'):
        layer=m['study_region_id'],int(m['voltage_kv']);y=int(m['year'])
        ss=[s for s in durations if s[:2]==layer]
        proxies=[reverse[(*s,y)] for s in ss]
        gross=sum(float(r['annual_load_scale'])*float(r['gross_load_proxy_mw_2025']) for r in proxies)
        pv=sum(float(r['annual_pv_scale'])*float(r['pv_output_proxy_mw_2025']) for r in proxies)
        fw=max(int(durations[s]['forward_d95_max_run_hours']) for s in ss)
        rv=max(int(durations[s]['reverse_d95_max_run_hours']) for s in ss)
        actual=[float(scenes[s,y]['reverse_screen_mw']) for s in ss]
        p=float(m['reference_peak_mw']);chosen=m['selected_scheme_by_incremental_cost']
        chosen_year=next(r for r in read_csv(OUTPUT/f'{chosen}_{layer[0]}_{layer[1]}_years.csv') if int(r['year'])==y)
        row={'study_region_id':layer[0],'voltage_kv':layer[1],'year':y,'station_count':len(ss),
             'source_load_output_proxy_ratio':pv/gross,'source_proxy_output_sum_mw':pv,'gross_proxy_sum_mw':gross,
             'source_load_ratio_basis':'noncoincident_station_reverse_templates_output_over_gross_proxy_not_installed_capacity_ratio',
             'net_peak_cagr_since_2021':(p/peaks[*layer,2021])**(1/(y-2021))-1,
             'net_peak_yoy_growth':p/peaks[*layer,y-1]-1,'forward_reference_peak_mw':p,
             'reverse_station_peak_max_mw':max(actual),'reverse_station_peak_sum_upper_proxy_mw':sum(actual),
             'reverse_peak_basis':'station_extrema_not_synchronous_regional_reverse_peak',
             'forward_d95_max_template_hours':fw,'reverse_d95_max_template_hours':rv,
             'duration_basis':'2025_station_templates_held_for_2022_2025_not_observed_annual_durations',
             'transformer_cost_scale':1.0,'line_cost_scale':1.0,'storage_cost_scale':1.0,
             'cost_ratio_transformer_to_storage_multiplier':1.0,'cost_ratio_line_to_storage_multiplier':1.0,
             'initial_capacity_mva':base[layer],'contingency_service_fraction':SETTINGS[layer]['contingency_fraction'],
             'rigid_expansion_budget_fraction':SETTINGS[layer]['rigid_budget'],'transfer_scope':'T01_and_designed_new_line' if layer==('QX-00005',110) else 'no_station_tie_candidates',
             'rigid_clr':float(m['rigid_clr']),'elastic_clr':float(m['elastic_clr']),
             'recommended_scheme':chosen,'recommended_clr':float(m['selected_planning_clr']),
             'recommended_capacity_mva':float(m[chosen+'_capacity_mva']),
             'storage_modules_in_service':int(m[chosen+'_storage_modules']),
             'existing_tie_mw':float(m[chosen+'_existing_tie_mw']),'new_line_transfer_mw':float(m[chosen+'_new_line_transfer_mw']),
             'year_investment_lifecycle_npv_10k_cny':float(chosen_year['year_lifecycle_npv_10k_cny']),
             'rigid_path_npv_10k_cny':float(m['rigid_cost_npv_10k_cny']),'elastic_path_npv_10k_cny':float(m['elastic_cost_npv_10k_cny']),
             'recommendation_basis':'minimum_full_path_cost_given_station_distribution_initial_assets_and_network_scope',
             'application_status':'annual_case_lookup_reference_reoptimization_required_for_new_region'}
        rows.append(row)
    write_csv(rows,output_dir/'annual_indicator_recommendation.csv')
    correlations=[]
    groups=[('all_12_rows',rows)]+[(f'{a}_{b}',[r for r in rows if (r['study_region_id'],r['voltage_kv'])==(a,b)]) for a,b in SETTINGS]
    for scope,data in groups:
        for a,b in itertools.combinations(FEATURES,2):
            x=np.array([r[a] for r in data]);z=np.array([r[b] for r in data]);constant=np.ptp(x)==0 or np.ptp(z)==0
            pearson='' if constant else float(np.corrcoef(x,z)[0,1]);spearman='' if constant else float(spearmanr(x,z).statistic)
            correlations.append({'scope':scope,'sample_count':len(data),'indicator_a':a,'indicator_b':b,'pearson':pearson,'spearman':spearman,'high_correlation_abs_0_8':not constant and (abs(pearson)>=.8 or abs(spearman)>=.8),'interpretation':'constant_indicator_not_identifiable' if constant else 'descriptive_small_nonindependent_sample_not_causal_or_generalizable'})
    write_csv(correlations,output_dir/'indicator_correlations.csv')
    ranges=[{'study_region_id':a,'voltage_kv':b,'indicator':f,'minimum':min(r[f] for r in rows if (r['study_region_id'],r['voltage_kv'])==(a,b)),'maximum':max(r[f] for r in rows if (r['study_region_id'],r['voltage_kv'])==(a,b)),'scope':'observed_model_case_envelope_not_joint_feasibility_box'} for a,b in SETTINGS for f in FEATURES]
    write_csv(ranges,output_dir/'indicator_applicability_ranges.csv')
    problems=[]
    if len(rows)!=12 or len({(r['study_region_id'],r['voltage_kv'],r['year']) for r in rows})!=12:problems.append('row keys')
    for r in rows:
        if abs(r['recommended_capacity_mva']/r['forward_reference_peak_mw']-r['recommended_clr'])>1e-6:problems.append('ratio reconciliation')
        if r['rigid_clr']>2+1e-8:problems.append('rigid cap')
        if not all(np.isfinite(float(r[k])) for k in FEATURES):problems.append('finite features')
    audit={'status':'PASS' if not problems else 'FAIL','annual_rows':len(rows),'correlation_rows':len(correlations),'problems':problems,'definition_limitations':['source_load_ratio_is_proxy','regional_synchronous_reverse_peak_unavailable','historical_D95_held_as_2025_template','features_do_not_uniquely_identify_optimal_clr_without_assets_topology_and_full_path']}
    (output_dir/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
    write_report(rows,correlations,output_dir)
    if problems:raise ValueError(problems)
    return audit

def write_report(rows,corr,out):
    lines=['# 年度指标—推荐容载比矩阵（reserve_policy_v4）','','2022—2025 每个研究单元每年一组参数，共 12 组。推荐值来自当前完整四年成本最优路径；跨区域使用须保留资产与网络条件并重新优化。','','## 指标与计算口径','','- 源荷代理比：各站反向模板时刻的光伏出力代理之和 / 毛负荷代理之和。各站时刻可能不同，既不是同步区域源荷比，也不是装机/负荷峰值比。2021—2022 的光伏比例含回推假设。','- 平均增长率：从 2021 到该年的正向参考净峰 CAGR；另提供同比增长率。它是净峰增长率，不代表全年平均净负荷增长率。','- 净负荷极值：正向参考净峰；反向采用最大站峰，另列站峰之和上包络，禁止称为同步区域反向峰。','- D95：站级 95% 峰值最长连续持续时间的最大值；沿用 2025 年逐时模板，2022—2024 不作为实测持续时间。','- 成本：主变、线路、储能分别以基准价格系数 1 归一化；成本比为价格系数之比，不把不同计价单位的原始单价直接相除。','- 辅助条件：电压等级、基期容量、负荷空间分布、恢复比例和可转供线路集合。仅凭汇总指标不能确定唯一最优容载比。','','## 年度推荐矩阵','','| 单元 | 年 | 源荷代理比 | 净峰CAGR | 正向参考净峰 MW | 反向最大站峰 MW | 正/反D95 h | 推荐 R | 推荐容量 MVA |','| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in rows:
        name='邳州' if r['study_region_id']=='QX-00005' else '市区29站'
        lines.append(f"| {name} {r['voltage_kv']}kV | {r['year']} | {r['source_load_output_proxy_ratio']:.3f} | {r['net_peak_cagr_since_2021']:.2%} | {r['forward_reference_peak_mw']:.3f} | {r['reverse_station_peak_max_mw']:.3f} | {r['forward_d95_max_template_hours']}/{r['reverse_d95_max_template_hours']} | {r['recommended_clr']:.3f} | {r['recommended_capacity_mva']:g} |")
    lines+=['','## 相关性与使用方法','','使用 Pearson 和 Spearman 两种描述统计，绝对值 ≥0.8 标记较高相关。总样本仅12行、单元内仅4行；年度共用2025模板，样本不是独立抽样，不能据此宣称统计显著、因果关系或普遍规律。持续时间在同一单元中不变，其相关系数不定义。跨单元的极值、D95相关可能来自电压等级和统计规模差异。源荷比、增长率和极值共用年度缩放及代理构造，敏感性应联动生成物理一致场景，不能任意独立拼接。','','较高相关的全样本指标对：']
    lines += [f"- {r['indicator_a']} 与 {r['indicator_b']}：Pearson={r['pearson']:.3f}，Spearman={r['spearman']:.3f}。" for r in corr if r['scope']=='all_12_rows' and r['high_correlation_abs_0_8']]
    lines+=['','成本系数独立敏感性在相同源荷参数、初始资产和网络条件下重新优化完整路径；年度容载比不能沿用后仅乘成本系数。结果与逐年推荐见独立敏感性文件。','','适用范围表只描述已有案例的边界，不能把各指标最小/最大值笛卡尔组合解释为已验证可行域。当前成果为可追溯年度案例矩阵，不提供未经验证的区间内插值或全徐州通用阈值。']
    (out/'年度指标与推荐容载比说明.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':print(json.dumps(build(),ensure_ascii=False))
