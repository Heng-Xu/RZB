"""生成可用于报告的年度指标矩阵、成本敏感性说明及中文工作簿。"""
import json
from pathlib import Path
import pandas as pd
from openpyxl.styles import Font,PatternFill,Alignment
from .annual_recommendation_matrix import DEST,FEATURES,build
from .annual_recommendation_audit import audit as audit_annual
from .annual_cost_sensitivity import DEST as COST
from .annual_cost_sensitivity_audit import audit as audit_cost

LABELS={
'study_region_id':'研究单元编号','voltage_kv':'电压等级_kV','year':'年份','station_count':'站数',
'source_load_output_proxy_ratio':'源荷出力代理比','source_proxy_output_sum_mw':'光伏代理出力和_MW','gross_proxy_sum_mw':'毛负荷代理和_MW',
'source_load_ratio_basis':'源荷比计算边界','net_peak_cagr_since_2021':'净峰年均增长率_CAGR','net_peak_yoy_growth':'净峰同比增长率',
'forward_reference_peak_mw':'正向参考净峰_MW','reverse_station_peak_max_mw':'反向最大站峰_MW','reverse_station_peak_sum_upper_proxy_mw':'反向站峰和上包络_MW',
'reverse_peak_basis':'反向极值计算边界','forward_d95_max_template_hours':'正向最长连续D95_h','reverse_d95_max_template_hours':'反向最长连续D95_h','duration_basis':'持续时间来源',
'transformer_cost_scale':'主变价格系数','line_cost_scale':'线路价格系数','storage_cost_scale':'储能价格系数','cost_ratio_transformer_to_storage_multiplier':'主变相对储能成本比系数','cost_ratio_line_to_storage_multiplier':'线路相对储能成本比系数',
'initial_capacity_mva':'2021起点容量_MVA','contingency_service_fraction':'停运恢复负荷比例','rigid_expansion_budget_fraction':'刚性累计增配预算比例','transfer_scope':'转供候选范围',
'rigid_clr':'刚性容载比','elastic_clr':'弹性容载比','recommended_scheme':'推荐方案','recommended_clr':'推荐容载比','recommended_capacity_mva':'推荐容量_MVA',
'storage_modules_in_service':'在役储能柜数','existing_tie_mw':'既有线路转供_MW','new_line_transfer_mw':'新线路转供_MW','year_investment_lifecycle_npv_10k_cny':'该年新增措施全寿命现值_万元','rigid_path_npv_10k_cny':'刚性全路径现值_万元','elastic_path_npv_10k_cny':'弹性全路径现值_万元','recommendation_basis':'推荐依据','application_status':'适用状态',
'case_id':'情景','scheme':'方案','transformer_scale':'主变价格系数','storage_scale':'储能价格系数','line_scale':'线路价格系数','status':'求解状态','cost_npv_10k_cny':'全路径成本现值_万元','detail':'补充说明','capacity_mva':'容量_MVA','clr':'容载比','storage_modules':'在役储能柜数','line_built':'新线路在役','year_lifecycle_npv_10k_cny':'该年新增措施全寿命现值_万元','path_npv_10k_cny':'全路径成本现值_万元','scope':'统计范围','sample_count':'样本数','indicator_a':'指标A','indicator_b':'指标B','pearson':'Pearson相关系数','spearman':'Spearman相关系数','high_correlation_abs_0_8':'高相关标记_绝对值0.8','interpretation':'解释边界','indicator':'指标','minimum':'最小值','maximum':'最大值'}
CASE_LABELS={'base':'基准','transformer_0_7':'主变价格×0.7','storage_1_5':'储能价格×1.5','line_1_5':'线路价格×1.5'}

def finalize():
    build();audit_annual();audit_cost()
    rows=pd.read_csv(DEST/'annual_indicator_recommendation.csv');corr=pd.read_csv(DEST/'indicator_correlations.csv')
    summary=pd.read_csv(COST/'summary.csv');rec=pd.read_csv(COST/'annual_recommendations.csv')
    definition=[{'指标':'源荷比','定义':'光伏出力代理和/毛负荷代理和；站级反向模板时刻可能不同','来源':'annual_reverse_station_proxy_2021_2025.csv, night_central','边界':'不是实测同步源荷比或装机容量比'},
        {'指标':'净峰平均增长率','定义':'(该年正向参考净峰/2021参考净峰)^(1/(年-2021))-1；另列同比','来源':'annual_forward_layer_scenes_2021_2025.csv','边界':'净峰CAGR，不是全年平均净负荷增长率'},
        {'指标':'净负荷极值','定义':'正向参考净峰；反向最大站峰及站峰和上包络','来源':'甲方年度降压负荷；transformer_only_path_station_2021_2025.csv','边界':'市区为29站代理；反向不是同步区域峰'},
        {'指标':'95%峰值持续时间','定义':'站级≥95%峰值的最长连续时长D95，汇总取最大；另提供各站原始模板','来源':'static_storage_need_screen_2025.csv','边界':'2025模板沿用至各年，不是2022—2024实测'},
        {'指标':'成本比系数','定义':'各技术价格/各自基准价格；相对比为kT/kS、kL/kS','来源':'本地工程案例与储能价格表','边界':'单位不同的原始单价不可直接相除；独立变动一项后全路径重求'},
        {'指标':'推荐容载比','定义':'最低全路径成本方案该年容量/该年正向参考净峰','来源':'reserve_policy_v4完整四年路径','边界':'需要基期资产、站级分布、网络候选和停运比例等条件'}]
    datasets=[(rows,'年度参数及推荐'),(pd.read_csv(COST/'annual_recommendations.csv'),'价格敏感性年度推荐'),(summary,'价格敏感性成本'),(pd.read_csv(COST/'annual_schemes.csv'),'价格敏感性刚弹明细'),(corr,'指标相关性'),(pd.read_csv(DEST/'indicator_applicability_ranges.csv'),'案例参数范围'),(pd.DataFrame(definition),'指标口径及来源')]
    book=DEST/'年度指标与推荐容载比矩阵.xlsx'
    with pd.ExcelWriter(book,engine='openpyxl') as writer:
        for frame,sheet in datasets:
            f=frame.copy()
            if 'scheme' in f:f['scheme']=f['scheme'].replace({'rigid':'刚性','elastic':'弹性'})
            if 'recommended_scheme' in f:f['recommended_scheme']=f['recommended_scheme'].replace({'rigid':'刚性','elastic':'弹性'})
            if 'case_id' in f:f['case_id']=f['case_id'].replace(CASE_LABELS)
            for col in ['indicator','indicator_a','indicator_b']:
                if col in f:f[col]=f[col].replace(LABELS)
            f=f.rename(columns=LABELS);f.to_excel(writer,sheet_name=sheet,index=False)
        for sheet in writer.book:
            sheet.freeze_panes='D2';sheet.auto_filter.ref=sheet.dimensions;sheet.row_dimensions[1].height=34
            for cell in sheet[1]:cell.fill=PatternFill('solid',fgColor='24476A');cell.font=Font(color='FFFFFF',bold=True);cell.alignment=Alignment(wrap_text=True,vertical='center')
            for col in sheet.columns:
                name=str(col[0].value);sheet.column_dimensions[col[0].column_letter].width=min(35,max(14,len(name)*1.4))
                for cell in col[1:]:
                    if isinstance(cell.value,(int,float)):
                        cell.number_format='0.00%' if ('增长率' in name or '比例' in name) else '0.000' if ('比' in name or '相关系数' in name) else '#,##0.00'
    lines=['# 年度参数—推荐容载比与独立成本敏感性','','更新：2026-09-27。以最新认可的 reserve_policy_v4 作为基础；三个研究单元各年一组参数，共12组。价格敏感性选取邳州110kV，基准加3个独立价格情景，共8条完整路径、16行年度推荐。','','## 已核验结论','','原六路径成本和年度矩阵在专用环境完整复现。保持成本优先、同费用最大容量裕度、最少转供三阶段流程。原逐站解存在等价分配，继续采用原版作为报告方案明细。','','## 指标口径与使用','','年度参数矩阵和口径说明见 `年度指标与推荐容载比说明.md`；机器表 `annual_indicator_recommendation.csv` 保留完整参数、措施与成本。Excel提供中文列名、相关性、适用范围和敏感性。源荷比为代理量，反向极值为站级量，历史D95沿用2025模板，不能宣称都是年度实测。','','## 成本系数独立敏感性（邳州110kV）','','各技术基准系数均为1。一次只改变一项价格，源荷、初始资产、停运比例和转供候选保持相同，完整重求四年路径。费用为2022—2041增量全寿命现值，单位万元。','','| 情景 | 主变/储能/线路系数 | 刚性成本 | 弹性成本 | 推荐2025 R | 推荐2025储能柜数 |','| --- | --- | ---: | ---: | ---: | ---: |']
    for case in CASE_LABELS:
        s=summary[summary.case_id==case];r=rec[(rec.case_id==case)&(rec.year==2025)].iloc[0];rig=s[s.scheme=='rigid'].iloc[0];ela=s[s.scheme=='elastic'].iloc[0]
        lines.append(f"| {CASE_LABELS[case]} | {r.transformer_scale:g}/{r.storage_scale:g}/{r.line_scale:g} | {rig.cost_npv_10k_cny:,.2f} | {ela.cost_npv_10k_cny:,.2f} | {r.recommended_clr:.3f} | {int(r.storage_modules)} |")
    lines+=['','主变降价或储能涨价时，弹性方案2025容量由2096增至2113 MVA，储能由35降至3柜，推荐R由2.191升至2.209。线路涨价50%后仍选择候选新线，推荐容量和储能数量保持基准值；这只证明该情景内方案稳定，不代表任意线路价格下都建新线。全部情景仍推荐弹性完整路径。','','## 参数相关性','','相关性同时报告Pearson、Spearman及单元内结果；|r|≥0.8作描述标记。全样本12行，单元内4行，模板共用，不能进行因果或显著性结论。单元内D95恒定，其相关系数不定义。','','单元内较高相关的源荷代理比与反向最大站峰：']
    for _,r in corr.iterrows():
        if r.scope!='all_12_rows' and {r.indicator_a,r.indicator_b}=={'source_load_output_proxy_ratio','reverse_station_peak_max_mw'}:
            lines.append(f"- {r.scope}：Pearson={r.pearson:.3f}，Spearman={r.spearman:.3f}。两项共用光伏/毛负荷代理构造，有结构性联系，不应当作独立输入任意组合。")
    lines+=['','全样本正向净峰与正向D95的Pearson约0.983，主要反映单元规模与模板差异，不能推断峰值上升导致持续时间变长。净峰CAGR也由年度极值计算，属于派生指标。跨区域推广时应匹配电压、起点容量、负荷空间分布、停运恢复比例及可转供线路；参数范围表是已有案例范围，不是笛卡尔组合的通用可行域。','','## 质量验证','','- 年度参数12行独立核对通过。','- 成本敏感性8路径、2731项独立约束与现金流核对通过。','- 未将超时误判为无解，未将单年成本低的措施拼接成推荐路径。','- 保持原始数据、现行v4结果和建模过程可追溯。','','## 复现','','在 `实验/研究/` 使用 `xuzhou110kv_clr` 环境：','','```bash','python -m rebuild_2026.simulation_reserve_policy_audit','python -m rebuild_2026.annual_recommendation_matrix','python -m rebuild_2026.annual_recommendation_audit','XUZHOU_MILP_BACKEND=highspy python -m rebuild_2026.annual_cost_sensitivity','python -m rebuild_2026.annual_cost_sensitivity_audit','python -m rebuild_2026.finalize_recommendation_artifacts','```']
    (DEST/'推荐矩阵成果说明.md').write_text('\n'.join(lines)+'\n')
    return str(book)

if __name__=='__main__':print(finalize())
