"""从原表和原结果生成审查资料，不写模型结果。"""
from pathlib import Path
import ast,csv,json,hashlib,math,sys,subprocess,html,re,zipfile,xml.etree.ElementTree as ET
from collections import defaultdict,Counter
import openpyxl
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.utils import get_column_letter

ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'研究报告/00审查';EVID=OUT/'证据'
STUDY=ROOT/'实验/研究';CODE=STUDY/'rebuild_2026';AUDIT=CODE/'source_audit'
RESULT=AUDIT/'capacity_release_simulation/reserve_policy_v4';REC=RESULT/'recommendation_matrix';SENS=REC/'cost_sensitivity'
sys.path.insert(0,str(STUDY))
REGIONS={f'QX-{i:05}':n for i,n in enumerate(['丰县','鼓楼','贾汪','沛县','邳州','泉山','市区','睢宁','铜山','新沂','徐州直属'],1)}
SCHEMES={'rigid':'刚性','elastic':'弹性'}
CASES={'base':'基准','transformer_0_7':'主变价格乘0.7','storage_1_5':'储能价格乘1.5','line_1_5':'线路价格乘1.5'}
def rel(p): return str(Path(p).relative_to(ROOT))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csvrows(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def mapped(text):
    for k,v in REGIONS.items():text=text.replace(k,v)
    return text
def code_loc(p,word):
    lines=Path(p).read_text().splitlines()
    return next((f'L{i}: {line.strip()}' for i,line in enumerate(lines,1) if word in line),None)
def compare_reproduction():
    reproduced=EVID/'隔离重求结果'
    if not reproduced.is_dir():reproduced=Path('/tmp/rzb-stage0-review/reproduced')
    checks=0;bad=[];different_station=[]
    files=['summary.csv','annual_matrix.csv']+[p.name for p in RESULT.glob('*_years.csv')]+[p.name for p in RESULT.glob('*_ties.csv')]
    for name in files:
        if not (reproduced/name).exists():bad.append('重求缺文件 '+name);continue
        old=csvrows(RESULT/name);new=csvrows(reproduced/name)
        if len(old)!=len(new):bad.append('重求行数 '+name);continue
        for a,b in zip(old,new):
            for key,original in a.items():
                if key not in b:bad.append('重求缺字段 '+key);continue
                try:
                    expected=float(original);actual=float(b[key]);ok=math.isclose(expected,actual,rel_tol=1e-8,abs_tol=1e-5)
                except (ValueError,TypeError):ok=original==b[key]
                checks+=1
                if not ok:bad.append(name+':'+key)
    for p in RESULT.glob('*_stations.csv'):
        if p.name=='baseline_stations.csv':continue
        q=reproduced/p.name
        if q.exists() and p.read_bytes()!=q.read_bytes():different_station.append(p.name)
    result={'status':'PASS' if not bad else 'FAIL','checks':checks,'problems':bad,'compared_files':files,'equal_cost_station_layout_differences':different_station,'rule':'逐站等价解不替换原版；区域年度及成本按1e-5绝对容差、1e-8相对容差核对','isolated_directory':str(reproduced)}
    dump(EVID/'本阶段完整重求对账.json',result)
    if bad:raise ValueError(result)
    return result

LABELS={
 'reference_peak_mw':('年度参考正向净峰','P̂⁺','MW','F05'),
 'synchronous_forward_peak_mw':('年度参考正向净峰','P̂⁺','MW','F05'),
 'forward_reference_peak_mw':('年度参考正向净峰','P̂⁺','MW','F05'),
 'policy_control_peak_mw':('容载比控制参考净峰','P̂⁺','MW','F05'),
 'station_count':('样本站数','N站','座','输入样本计数'),
 'source_load_output_proxy_ratio':('非同时源荷出力代理比','ρ','比例','F13'),
 'source_proxy_output_sum_mw':('站级光伏出力代理合计','ΣbV','MW','F13'),
 'gross_proxy_sum_mw':('站级毛负荷代理合计','ΣaG','MW','F13'),
 'net_peak_cagr_since_2021':('参考净峰自基期年均增长率','g','比例','F14'),
 'net_peak_yoy_growth':('参考净峰同比增长率','g同比','比例','F14'),
 'reverse_station_peak_max_mw':('最大站级反向峰值','max L⁻','MW','F13'),
 'reverse_station_peak_sum_upper_proxy_mw':('站级反向峰值之和上包络','ΣL⁻','MW','F13'),
 'forward_d95_max_template_hours':('正向最长持续时间模板的站间最大值','max D⁺₉₅','h','F09'),
 'reverse_d95_max_template_hours':('反向最长持续时间模板的站间最大值','max D⁻₉₅','h','F09'),
 'initial_capacity_mva':('共同起点主变容量','S₂₀₂₁','MVA','基期离散分配'),
 'target_capacity_mva':('基期区域容量分配目标','S目标','MVA','基期离散分配'),
 'proxy_capacity_mva':('基期离散容量分配结果','S₂₀₂₁','MVA','基期离散分配'),
 'allocation_gap_mva':('基期离散分配差额','ΔS','MVA','离散分配结果减目标'),
 'estimated_station_peak_sum_mw':('基期非同时站级峰值之和','ΣL⁺','MW','站级峰值加总；不是区域同步峰'),
 'reported_or_sample_scaled_2021_peak_mw':('基期原表降压负荷','P⁺₂₀₂₁','MW','原表单元格'),
 'recommended_clr':('推荐规划参考容载比','R推荐','MVA/MW','F05'),
 'selected_planning_clr':('推荐规划参考容载比','R推荐','MVA/MW','F05'),
 'recommended_capacity_mva':('推荐主变容量','S推荐','MVA','完整路径最优解'),
 'selected_capacity_mva':('选定主变容量','S','MVA','离散主变组合加总'),
 'capacity_mva':('主变总容量','S','MVA','离散组合或原表'),
 'capacity_2025_mva':('2025年主变容量','S₂₀₂₅','MVA','完整路径末年结果'),
 'actual_clr':('规划参考容载比','R','MVA/MW','F05'),
 'clr':('规划参考容载比','R','MVA/MW','F05'),
 'clr_2025':('2025年规划参考容载比','R₂₀₂₅','MVA/MW','F05'),
 'clr_cap':('容载比研究控制上限','R上限','MVA/MW','F10'),
 'max_actual_clr':('路径年度参考容载比最大值','max R','MVA/MW','F05后取最大'),
 'max_clr':('路径年度参考容载比最大值','max R','MVA/MW','F05后取最大'),
 'policy_control_clr':('年度控制口径参考容载比','R控制','MVA/MW','F05'),
 'storage_modules_in_service':('在役储能柜数','n','柜','完整路径整数解'),
 'storage_modules':('在役储能柜数','n','柜','完整路径整数解'),
 'storage_2025_modules':('2025年在役储能柜数','n₂₀₂₅','柜','完整路径整数解'),
 'new_storage_modules':('当年新增储能柜数','Δn','柜','本年在役数量减上一年'),
 'existing_tie_mw':('既有联络转供功率代理','x既有','MW','F11'),
 'new_line_transfer_mw':('候选新线转供功率代理','x新线','MW','F11'),
 'transfer_mw':('转供功率代理','x','MW','F11'),
 'transfer_2025_mw':('2025年总转供功率代理','x₂₀₂₅','MW','F11转供量加总'),
 'line_built':('候选新线建成状态','u','0或1','完整路径二元解'),
 'new_line_built_2025':('2025年新线建成状态','u₂₀₂₅','0或1','完整路径二元解'),
 'year_lifecycle_npv_10k_cny':('本年投运措施评价期费用现值','C投运年','万元','F15e'),
 'year_investment_lifecycle_npv_10k_cny':('本年投运措施评价期费用现值','C投运年','万元','F15e'),
 'path_npv_10k_cny':('完整路径增量费用现值','C','万元','F15e'),
 'cost_npv_10k_cny':('完整路径增量费用现值','C','万元','F15e'),
 'objective_npv_10k_cny':('完整路径增量费用现值','C','万元','F15e'),
 'discount_rate':('年折现率','r','比例','F15e'),
 'transformer_life_years':('主变计算寿命','L主变','年','F15d'),
 'line_life_years':('线路计算寿命','L线路','年','F15d'),
 'storage_life_years':('储能计算寿命','L储能','年','F15d'),
 'network_fixed_om_rate':('主变及新线固定运维费率','μ网','1/年','F15d'),
 'storage_fixed_om_rate':('储能固定运维费率','μ储','1/年','F15d'),
 'contingency_fraction':('停运恢复比例假设','f','比例','F08'),
 'contingency_service_fraction':('停运恢复比例假设','f','比例','F08'),
 'contingency_fraction_assumption':('停运恢复比例假设','f','比例','F08'),
 'rigid_budget_fraction':('刚性累计增配预算比例','γ','比例','F10'),
 'rigid_expansion_budget_fraction':('刚性累计增配预算比例','γ','比例','F10'),
 'rigid_budget_assumption':('刚性累计增配预算比例','γ','比例','F10'),
 'capacity_growth_budget_fraction':('累计正增配预算比例','γ','比例','F10'),
 'gross_budget_fraction':('累计正增配预算比例','γ','比例','F10'),
 'transformer_cost_scale':('主变价格系数','κ主变','倍','价格情景输入'),
 'transformer_scale':('主变价格系数','κ主变','倍','价格情景输入'),
 'transformer_price_scale':('主变价格系数','κ主变','倍','价格情景输入'),
 'storage_cost_scale':('储能价格系数','κ储能','倍','价格情景输入'),
 'storage_scale':('储能价格系数','κ储能','倍','价格情景输入'),
 'storage_price_scale':('储能价格系数','κ储能','倍','价格情景输入'),
 'line_cost_scale':('线路价格系数','κ线路','倍','价格情景输入'),
 'line_scale':('线路价格系数','κ线路','倍','价格情景输入'),
 'cost_ratio_transformer_to_storage_multiplier':('主变对储能价格系数比','κ主变/κ储能','倍','价格系数相除，非异量纲单价相除'),
 'transformer_storage_relative_cost_multiplier':('主变对储能价格系数比','κ主变/κ储能','倍','价格系数相除，非异量纲单价相除'),
 'cost_ratio_line_to_storage_multiplier':('线路对储能价格系数比','κ线路/κ储能','倍','价格系数相除，非异量纲单价相除'),
 'line_storage_relative_cost_multiplier':('线路对储能价格系数比','κ线路/κ储能','倍','价格系数相除，非异量纲单价相除'),
 'max_storage_modules_per_station':('单站储能决策上限','n上限','柜','研究场景输入'),
 'replaced_unit_credit_fraction':('旧主变回收抵扣比例','λ','比例','本版本取0；不等于真实残值为0'),
 'tie_transfer_limit_scale':('转供上限缩放系数','κ转供','倍','研究场景输入'),
 'new_line_section_coincidence':('新线区段负荷同时系数假设','κ区段','倍','研究场景输入'),
 'prior_unit_1_mva':('上一年第一台主变容量','s₁旧','MVA','连续路径状态'),
 'prior_unit_2_mva':('上一年第二台主变容量','s₂旧','MVA','连续路径状态'),
 'selected_unit_1_mva':('本年第一台主变容量','s₁','MVA','离散主变选择'),
 'selected_unit_2_mva':('本年第二台主变容量','s₂','MVA','离散主变选择'),
 'released_capacity_mva':('本年仿真净退出容量','ΔS退出','MVA','max(0,上一年站容量减本年)'),
 'net_capacity_change_mva':('本年主变容量净变化','ΔS','MVA','本年容量减上一年'),
 'forward_screen_mw':('站级正向峰值静态需求','L⁺','MW','年度站级场景'),
 'reverse_screen_mw':('站级反向峰值静态需求','L⁻','MW','F13及2025全年极值合并'),
 'transformer_capex_10k_cny':('当年主变购置投资','K主变','万元','F15a'),
 'storage_capex_10k_cny':('当年储能新增投资','K储能','万元','F15b'),
 'new_line_capex_10k_cny':('当年新线投资','K新线','万元','F15c'),
 'transformer_lifecycle_npv_10k_cny':('主变投运批次费用现值','C主变','万元','F15d、F15e'),
 'storage_lifecycle_npv_10k_cny':('储能投运批次费用现值','C储能','万元','F15d、F15e'),
 'pearson':('Pearson描述性相关系数','r','无量纲','F16'),
 'spearman':('Spearman描述性相关系数','rₛ','无量纲','F16'),
 'sample_count':('相关性样本行数','N','行','按统计组计数')}

FORMULAS={
 'F05':'同边界主变额定容量合计除以固定年度参考正向净峰；不扣本规划储能动作',
 'F08':'较小一台主变容量乘0.95，加储能有效功率及恢复比例乘净送出，覆盖恢复比例乘站级正向峰值',
 'F09':'站级峰值95%阈值最长连续小时；历史年沿用2025模板；单柜有效功率=min(0.1,0.215/持续小时)',
 'F10':'区域年度容量≤研究上限乘参考净峰；四年逐台正增配之和≤基期区域容量乘预算比例',
 'F11':'区段负荷种子乘供端当年/2025峰值比，受供端功率、受端余量及通道上限限制',
 'F13':'同月光伏比例缩放出力代理，年度负荷比例缩放毛负荷；两者相减求反向代理，分子分母分别合计求源荷比',
 'F14':'年均=(本年参考净峰/2021参考净峰)^(1/年数)-1；同比=本年/上一年-1',
 'F15a':'同电压替换案例静态总投资之和/新购容量之和；升档按新购完整容量计价',
 'F15b':'十柜整包重复计价+剩余一至九柜线性插值；本年投资为在役数量成本函数差分',
 'F15c':'候选长度3km×44.543万元/km×当年新建状态',
 'F15d':'投运年首次投资，次年起固定运维，寿命届满且更新年<2041时按原投资更新',
 'F15e':'首次投资、更新投资及固定运维按(1.06)^(现金流年-2021)折现后加总，评价期2022至2041',
 'F16':'对12行或单元内4行计算Pearson和含并列秩的Spearman；常量列不定义'}
def label(key):
    if key in LABELS:return LABELS[key]
    for scheme,prefix in [('rigid','刚性'),('elastic','弹性')]:
        if key.startswith(scheme+'_'):
            short=key[len(scheme)+1:]
            if short=='cost_npv_10k_cny' or short=='path_npv_10k_cny':return prefix+'路径费用现值','C'+prefix,'万元','F15e'
            if short=='clr':return prefix+'规划参考容载比','R'+prefix,'MVA/MW','F05'
            if short=='capacity_mva':return prefix+'主变容量','S'+prefix,'MVA','离散组合加总'
            if short=='storage_modules':return prefix+'在役储能柜数','n'+prefix,'柜','完整路径整数解'
            if short=='new_line_built':return prefix+'候选新线建成状态','u'+prefix,'0或1','完整路径二元解'
            if short=='existing_tie_mw':return prefix+'既有联络转供代理','x既有'+prefix,'MW','F11'
            if short=='new_line_transfer_mw':return prefix+'新线转供代理','x新线'+prefix,'MW','F11'
    return None

def main():
    OUT.mkdir(parents=True,exist_ok=True);EVID.mkdir(exist_ok=True)
    if (EVID/'阶段0冻结清单.json').exists():raise SystemExit('本阶段已经封存，资料生成须在单独复核副本内进行。')
    independent=json.loads((EVID/'本阶段独立核查.json').read_text());assert independent['status']=='PASS'
    reproduction=compare_reproduction()
    # 初次隔离副本漏拷根目录四个非模型文件。保留失败日志，追加补齐后的实际核验。
    # 哈希核验只读，可从当前工作区执行；不依赖临时隔离目录留存。
    check=subprocess.run([sys.executable,'-m','rebuild_2026.verify_frozen_v4'],cwd=STUDY,capture_output=True,text=True)
    (EVID/'原冻结哈希_补齐副本复核.log').write_text(check.stdout+check.stderr)
    assert check.returncode==0
    execution=json.loads((EVID/'执行检查.json').read_text());assert all(r['returncode']==0 for r in execution if r['name']!='原冻结哈希')
    version=json.loads((EVID/'版本核验.json').read_text())
    raw=list((STUDY/'data/tuomin').rglob('*'))
    raw=[p for p in raw if p.is_file() and '__pycache__' not in p.parts]
    records=[];nodes={};source_ids={};formula_gaps=[]
    source_files=[]
    def node(p,parents=(),process=None):
        p=Path(p);key=rel(p)
        if key not in nodes:
            sid=f'S{len(nodes)+1:04}';source_ids[key]=sid
            nodes[key]={'id':sid,'path':key,'sha256':sha(p),'bytes':p.stat().st_size,'parents':[rel(x) for x in parents],'process':process or '原始交付或原文件；只读保留'}
        elif parents:nodes[key]['parents']=[rel(x) for x in parents];nodes[key]['process']=process
        return key
    for p in raw:node(p)
    for p in CODE.glob('*.py'):node(p,process='冻结代码；计算方法及研究参数的实现依据')
    # 显式记录模块依赖，使价格函数、馈线筛查及拓扑子模型也可追溯。
    for p in CODE.glob('*.py'):
        parents=[]
        for item in ast.walk(ast.parse(p.read_text())):
            if isinstance(item,ast.ImportFrom) and item.module:
                local=item.module.split('.')[-1]
                candidate=CODE/(local+'.py')
                if (item.level or item.module.startswith('rebuild_2026.')) and candidate.exists() and candidate!=p:parents.append(candidate)
        if parents:node(p,sorted(set(parents)), '冻结模块及其显式本地导入；实际计算的数据父节点另列')
    for p in (ROOT/'参考政策').rglob('*'):
        if p.is_file():node(p)
    # 文件级计算血缘只使用实际存在的原文件和中间输入，源表坐标另在记录中登记。
    official=STUDY/'data/tuomin/电网建模数据_Agent整合版_V1.2/近5年容载比.xlsx'
    hourly=STUDY/'data/tuomin/电网建模数据_Agent整合版_V1.2/邳州主变负载率.xlsx'
    city=STUDY/'data/tuomin/补充数据/徐州市区脱敏.zip'
    asset=STUDY/'data/tuomin/电网建模数据_Agent整合版_V1.2/110（35）kv设备明细.xlsx'
    project_cost=STUDY/'data/tuomin/电网建模数据_Agent整合版_V1.2/江苏徐州邢楼110千伏变电站主变扩建等工程建设规模及投资汇总表(1).xlsx'
    pv=STUDY/'data/tuomin/电网建模数据_Agent整合版_V1.2/逐月分县分布式光伏.xlsx'
    prices=ROOT/'参考政策/储能成本依据/sources.csv'
    price_evidence=[]
    for row in csvrows(prices):
        if row['source_id'] in ['SZ_TENDER','LY_AWARD']:
            for field in ['local_html','local_pdf']:
                p=prices.parent/row[field]
                if p.is_file():price_evidence.append(p)
    node(prices,price_evidence,'金额登记源于招标与中标公告本地存档；苏州限价与浏阳中标价性质分别保留')
    for name,parents,process in [
      ('official_annual.csv',[official,CODE/'official_annual.py'],'逐行提取年度原表，万单位乘十'),
      ('asset_transformers_2025.csv',[asset,CODE/'asset_2025.py'],'按同电压设备台账提取额定容量'),
      ('pizhou_2025_mapping_evidence.csv',[hourly,asset,STUDY/'data/tuomin/电网建模数据_Agent整合版_V1.2/2025设备负载统计表.xlsx',CODE/'pizhou_mapping_evidence.py'],'逐列跨源映射；保留原表头和审批后对象'),
      ('pizhou_2025_station_scenarios_evidence.csv',[hourly,AUDIT/'pizhou_2025_mapping_evidence.csv',CODE/'pizhou_station_scenarios.py'],'同站主变时序汇总；求正反向峰值及持续时间'),
      ('pizhou_2025_station_values_at_district_scenes.csv',[hourly,AUDIT/'pizhou_2025_mapping_evidence.csv',CODE/'pizhou_station_scenarios.py'],'区域同步模板时刻提取各站净负荷'),
      ('pizhou_2025_scenarios_evidence.csv',[hourly,AUDIT/'pizhou_2025_mapping_evidence.csv',CODE/'pizhou_scenarios.py'],'同电压同步汇总；缺值小时只作敏感性，不改原序列'),
      ('city_2025_mapping_audit.csv',[city,CODE/'city_mapping_audit.py',CODE/'city_2025_mapping_supplement.csv'],'市区时序去重，排除220kV及不明全零序列，保留29站'),
      ('city_2025_scenario_sensitivity.csv',[city,AUDIT/'city_2025_mapping_audit.csv',CODE/'city_scenarios.py',ROOT/'memory/current.md'],'已观测与周类比补值分列，年度分母用已观测同步峰；净负荷MW单位按原项目确认解释'),
      ('city_2025_station_values_at_district_scenes.csv',[city,AUDIT/'city_2025_mapping_audit.csv',CODE/'city_scenarios.py'],'市区29站同步模板时刻提取'),
      ('model_station_inputs_2025.csv',[AUDIT/'pizhou_2025_station_scenarios_evidence.csv',AUDIT/'city_2025_scenario_sensitivity.csv',asset,CODE/'model_station_inputs.py'],'合并站级负荷与设备容量；三站设备容量缺口单列'),
      ('annual_forward_layer_scenes_2021_2025.csv',[AUDIT/'official_annual.csv',AUDIT/'pizhou_2025_scenarios_evidence.csv',AUDIT/'city_2025_scenario_sensitivity.csv',CODE/'annual_forward_scenes.py'],'邳州按原年度峰值校准；市区29站按官方年度比例缩放'),
      ('annual_forward_station_scenes_2021_2025.csv',[AUDIT/'annual_forward_layer_scenes_2021_2025.csv',AUDIT/'pizhou_2025_station_values_at_district_scenes.csv',AUDIT/'city_2025_station_values_at_district_scenes.csv',CODE/'annual_forward_scenes.py'],'保留2025站级空间分布，按同层年度比例缩放'),
      ('baseline_2021_station_candidates.csv',[AUDIT/'model_station_inputs_2025.csv',AUDIT/'official_annual.csv',asset,CODE/'baseline_2021.py'],'早期候选用于构造场景，不作为最终容量总量'),
      ('planning_2021_common_baseline_stations.csv',[AUDIT/'baseline_2021_station_candidates.csv',CODE/'planning_scheme_package.py'],'当前基期分配所需中间站表，虽含planning名称仍保留'),
      ('annual_reverse_station_proxy_2021_2025.csv',[hourly,city,pv,AUDIT/'annual_forward_layer_scenes_2021_2025.csv',AUDIT/'baseline_2021_station_candidates.csv',CODE/'annual_reverse_proxy.py'],'春秋日间窗口、夜间代理和同月比例缩放；早期年回推'),
      ('transformer_only_path_station_2021_2025.csv',[AUDIT/'annual_forward_station_scenes_2021_2025.csv',AUDIT/'annual_reverse_station_proxy_2021_2025.csv',AUDIT/'model_station_inputs_2025.csv',CODE/'transformer_only_path_2021_2025.py'],'为最终优化提供站级正向和反向场景；旧容量路径不可作为最终结果'),
      ('static_storage_need_screen_2025.csv',[AUDIT/'pizhou_2025_station_scenarios_evidence.csv',AUDIT/'city_2025_scenario_sensitivity.csv',CODE/'static_storage_screen_2025.py'],'最终优化只取基期保留分支的站级D95模板'),
      ('transformer_replacement_cost_coefficients.csv',[project_cost,CODE/'cost_references.py',CODE/'incremental_cost.py'],'同电压替换案例静态投资除以新购容量'),
      ('transformer_project_cost_references.csv',[project_cost,CODE/'cost_references.py'],'投资原表指定案例行摘录')]:
        if (AUDIT/name).exists():node(AUDIT/name,parents,process)
    baseparents=[AUDIT/'planning_2021_common_baseline_stations.csv',AUDIT/'model_station_inputs_2025.csv',AUDIT/'official_annual.csv',asset,CODE/'baseline_historical_proxy.py']
    for p in [RESULT/'baseline_layers.csv',RESULT/'baseline_stations.csv']:node(p,baseparents,'区域2021容量按2025站级容量份额分配，再选择本地离散规格')
    inputs=[RESULT/'baseline_stations.csv',AUDIT/'transformer_only_path_station_2021_2025.csv',AUDIT/'static_storage_need_screen_2025.csv',AUDIT/'annual_forward_layer_scenes_2021_2025.csv',asset,project_cost,prices,STUDY/'data/tuomin/电网建模数据_Agent整合版_V1.2/邳州10kV线路基础数据表.xlsx',CODE/'simulation_reserve_policy.py',CODE/'joint_lifecycle_optimizer.py',CODE/'incremental_cost.py',CODE/'annual_no_tie_investment_submodel.py']
    inputs+=[p for p in (STUDY/'data/tuomin/10kv_case').rglob('*') if p.is_file() and p.suffix in ['.csv','.xlsx','.7z']]
    for p in inputs:
        if rel(p) not in nodes:node(p)
    for p in list(RESULT.glob('*_stations.csv'))+list(RESULT.glob('*_years.csv'))+list(RESULT.glob('*_ties.csv')):
        if p.name=='baseline_stations.csv':continue
        node(p,inputs,'冻结MILP三阶段完整四年路径求解；原逐站解保留')
    node(RESULT/'summary.csv',list(RESULT.glob('*_years.csv'))+[CODE/'simulation_reserve_policy.py'],'按完整路径汇总费用与研究设置')
    node(RESULT/'annual_matrix.csv',[RESULT/'summary.csv']+list(RESULT.glob('*_years.csv'))+list(RESULT.glob('*_ties.csv'))+[CODE/'simulation_reserve_policy.py'],'逐年刚弹对照；按完整路径成本选择，不逐年拼接')
    node(REC/'annual_indicator_recommendation.csv',[RESULT/'annual_matrix.csv',AUDIT/'annual_reverse_station_proxy_2021_2025.csv',AUDIT/'static_storage_need_screen_2025.csv',AUDIT/'annual_forward_layer_scenes_2021_2025.csv',CODE/'annual_recommendation_matrix.py'],'年度指标代理及派生增长率，与完整路径推荐关联')
    for name in ['indicator_correlations.csv','indicator_applicability_ranges.csv']:node(REC/name,[REC/'annual_indicator_recommendation.csv',CODE/'annual_recommendation_matrix.py'],'样本描述；不解释为独立验证或通用连续可行域')
    for p in SENS.glob('*.csv'):node(p,inputs+[CODE/'annual_cost_sensitivity.py'],'单项价格系数变化后完整重求；基准沿用冻结原路径')
    node(RESULT/'sensitivity.csv',inputs+[CODE/'simulation_reserve_sensitivity.py'],'历史预算及恢复比例情景，仅有汇总；非本阶段正文准入')

    def add(name,variable,value,unit,p,location,formula,chapter,status='已冻结；条件研究结果',scope='',raw_value=None,formula_ref=None,limitation=''):
        p=Path(p);key=node(p)
        rid=f'D{len(records)+1:06}'
        records.append({'id':rid,'name':mapped(name),'variable':variable,'value':value,'unit':unit,'source':key,'source_location':location,'source_sha256':nodes[key]['sha256'],'formula':formula,'formula_ref':formula_ref,'chapter':chapter,'status':status,'scope':mapped(scope),'raw_value':raw_value if raw_value is not None else value,'lineage_node':key,'limitation':limitation})
    primary=[];technical=[];history=[]
    def table(p,chapter,detail=False,status=None):
        for rownum,row in enumerate(csvrows(p),2):
            region=row.get('study_region_id','');year=row.get('year','');v=row.get('voltage_kv','')
            if not region and 'case_id' in row:region='QX-00005';v='110'
            scope=' '.join(x for x in [REGIONS.get(region,region)+(('29站样本' if region=='QX-00007' else '')),v+'kV' if v else '',year+'年' if year else '',SCHEMES.get(row.get('scheme',''),''),CASES.get(row.get('case_id',''),row.get('case_id','')),row.get('model_station_id','') if detail else ''] if x)
            if row.get('scope'):scope+=' '+mapped(row['scope'])
            for key,value in row.items():
                spec=label(key)
                if not spec:continue
                if value in ('','None'):
                    if key not in ['pearson','spearman','cost_npv_10k_cny','clr_2025','capacity_2025_mva','storage_2025_modules','transfer_2025_mw']:continue
                    numeric=None
                else:
                    try:numeric=float(value)
                    except ValueError:continue
                    if not math.isfinite(numeric):raise ValueError('非有限数字 '+str(p)+key)
                    if numeric.is_integer():numeric=int(numeric)
                title,symbol,unit,ref=spec
                flag=status or ('仅技术附录；保留原站级解' if detail else '已冻结；条件研究结果')
                if numeric is None:flag='不可引用数值；原值空缺或系数不定义'
                note='市区29站样本；历史年模板代理；不是全市区实际值；原时序表头kV误标，依项目确认按MW解释' if region=='QX-00007' else '历史年站级分布为2025模板；非逐站历史实测'
                if key in ['pearson','spearman']:note='小样本、模板共用；常量指标不定义，空值不填零'
                add(scope+' '+title,symbol,numeric,unit,p,f'CSV物理行{rownum}；字段{key}',FORMULAS.get(ref,ref),chapter,flag,scope,value,ref,note)
                records[-1]['internal_field']=key
                (history if status else technical if detail else primary).append(records[-1]['id'])
    table(RESULT/'annual_matrix.csv','拟第五章：年度刚弹方案及推荐')
    table(RESULT/'summary.csv','拟第四、五章：完整路径费用及设置')
    table(RESULT/'baseline_layers.csv','拟第三、五章：基期资产与统计边界')
    table(REC/'annual_indicator_recommendation.csv','拟第三、五章：源荷特征与年度推荐')
    for name in ['summary.csv','annual_schemes.csv','annual_recommendations.csv']:table(SENS/name,'拟第五章：独立价格敏感性')
    table(REC/'indicator_correlations.csv','拟技术附录：描述性相关性')
    # 范围表沿用指标本身的单位。
    for rn,row in enumerate(csvrows(REC/'indicator_applicability_ranges.csv'),2):
        spec=label(row['indicator']);assert spec
        title,symbol,unit,ref=spec
        for field,display in [('minimum','样本最小'),('maximum','样本最大')]:
            add(REGIONS[row['study_region_id']]+' '+row['voltage_kv']+'kV '+title+display,symbol,float(row[field]),unit,REC/'indicator_applicability_ranges.csv',f'CSV物理行{rn}；字段{field}','对本单元四行年度案例取'+display,'拟技术附录：已有案例范围',limitation='不是任意指标组合的共同可行域')
            primary.append(records[-1]['id'])
    for p in sorted(RESULT.glob('*_years.csv')):table(p,'拟第五、六章：年度措施与费用')
    for p in sorted(RESULT.glob('*_stations.csv')):
        if p.name!='baseline_stations.csv':table(p,'拟技术附录：原逐站规划明细',True)
    for p in sorted(RESULT.glob('*_ties.csv')):table(p,'拟第六章：分段联络候选',True)
    for p in sorted(SENS.glob('*_stations.csv')):table(p,'拟技术附录：价格情景逐站明细',True)
    for p in sorted(SENS.glob('*_ties.csv')):table(p,'拟技术附录：价格情景转供明细',True)
    table(RESULT/'sensitivity.csv','历史证据台账；正文暂不准入',status='仅历史汇总；未取得本阶段完整路径对账')
    # 年度原始统计扩展至全部交付地区；未补充其优化推荐值。
    wb=openpyxl.load_workbook(official,read_only=True,data_only=True);region=None
    for rn,cells in enumerate(wb['Sheet1'].iter_rows(min_row=4,values_only=True),4):
        if cells[0] is not None:region=str(cells[0]).strip()
        vt=str(cells[1] or '')
        if region not in REGIONS or not vt.startswith(('110','35')):continue
        voltage=110 if vt.startswith('110') else 35
        for year in range(2021,2026):
            off=2+3*(year-2021)
            for j,(title,symbol,unit,mult) in enumerate([('原表主变容量','S原表','MVA',10),('原表降压负荷','P原表','MW',10),('原表容载比','R原表','MVA/MW',1)]):
                if cells[off+j] is None:continue
                add(f'{REGIONS[region]} {voltage}kV {year}年 {title}',symbol,float(cells[off+j])*mult,unit,official,f'Sheet1!{get_column_letter(off+j+1)}{rn}',('原表万千伏安或万千瓦乘十转换' if mult==10 else '直接取原表比值；保留原表舍入，不覆盖为重算值'),'拟第三章：地区年度现状','原始统计；不代表本版优化覆盖',f'{REGIONS[region]} {voltage}kV {year}',cells[off+j],limitation='原表舍入比值与容量除以负荷可能存在差额；事实值及计算值分别列示')
                primary.append(records[-1]['id'])
    wb.close()
    # 参数取实际函数及常量，出处是代码行或来源表，不以经验补值。
    from rebuild_2026.incremental_cost import replacement_cost_coefficients,storage_anchors
    from rebuild_2026.joint_lifecycle_optimizer import cost_factors,DESIGNED_NEW_LINE_KM,DESIGNED_NEW_LINE_LIMIT_MW,EXISTING_PATH_CAP_MW,LINE_BASE_10K_PER_KM
    factors=cost_factors()
    for key in ['discount_rate','transformer_life_years','line_life_years','storage_life_years','network_fixed_om_rate','storage_fixed_om_rate']:
        title,symbol,unit,ref=label(key);p=CODE/'joint_lifecycle_optimizer.py'
        word={'discount_rate':'def cost_factors','transformer_life_years':'def cost_factors','line_life_years':'line_life:','storage_life_years':'line_life:','network_fixed_om_rate':'network_om:','storage_fixed_om_rate':'network_om:'}[key]
        add(title,symbol,factors[key],unit,p,code_loc(p,word),FORMULAS[ref],'拟第四章：经济参数','研究假设；原函数默认值',formula_ref=ref);primary.append(records[-1]['id'])
    for value,title,symbol,unit,p,word,formula in [
       (DESIGNED_NEW_LINE_KM,'候选新线长度','ℓ','km',CODE/'joint_lifecycle_optimizer.py','DESIGNED_NEW_LINE_KM =','无测绘规划假设'),
       (LINE_BASE_10K_PER_KM,'新线单位投资','c线路','万元/km',CODE/'incremental_cost.py','LINE_BASE_10K_PER_KM =','项目90%架空和10%电缆折算假设，非报价'),
       (DESIGNED_NEW_LINE_KM*LINE_BASE_10K_PER_KM,'新线首次投资','K新线','万元',CODE/'joint_lifecycle_optimizer.py','DESIGNED_NEW_LINE_KM =','F15c：长度乘单位投资'),
       (DESIGNED_NEW_LINE_LIMIT_MW,'候选新线静态通道上界','T新线','MW',CODE/'joint_lifecycle_optimizer.py','DESIGNED_NEW_LINE_LIMIT_MW =','同型导线容量折算研究上界'),
       (EXISTING_PATH_CAP_MW,'既有联络保守通道包络','T既有','MW',CODE/'joint_lifecycle_optimizer.py','EXISTING_PATH_CAP_MW =','已登记旧局部案例最弱热限包络'),
       (.1,'单柜额定功率','P柜','MW/柜',CODE/'incremental_cost.py','MODULE_POWER_MW =','冻结设备规格'),
       (.215,'单柜额定能量','E柜','MWh/柜',CODE/'incremental_cost.py','MODULE_ENERGY_MWH =','冻结设备规格'),
       (.95,'容量折算功率因数','cosθ','无量纲',CODE/'baseline_2021.py','POWER_FACTOR =','导则6.3允许值；本模型取该基准'),
       (.8,'站级反向聚合初筛系数','β代理','无量纲',CODE/'joint_lifecycle_optimizer.py','factor = 0.95','宽松代理；未替代实际运行方式校核'),
       (50,'单站储能决策上限','n上限','柜',CODE/'simulation_reserve_policy.py','max_storage_modules=50','研究措施集合上限，非已确认站址容量')]:
        assert code_loc(p,word)
        add(title,symbol,value,unit,p,code_loc(p,word),formula,'拟第四、五、六章：措施参数','研究假设或规格；已冻结');primary.append(records[-1]['id'])
    for sid,value,title in [('SZ_TENDER',storage_anchors()[0],'苏州单柜招标最高限价'),('LY_AWARD',storage_anchors()[1],'浏阳十柜等效实际中标价')]:
        rn=next(i for i,r in enumerate(csvrows(prices),2) if r['source_id']==sid)
        add(title,'K₁' if sid=='SZ_TENDER' else 'K₁₀',value,'万元',prices,f'CSV物理行{rn}；amount_yuan','原始公告金额元除以10000','拟第四章：储能价格来源','历史价格案例；性质不得互换');primary.append(records[-1]['id'])
    for r in replacement_cost_coefficients():
        add(f"{r['voltage_kv']}kV主变新购容量折算系数",'c主变',r['base_coefficient_10k_cny_per_purchased_mva'],'万元/MVA',project_cost,'Sheet1!P'+',P'.join(r['source_case_rows'].split(';'))+'；C列工程规模','F15a；案例总投资之和/新购容量之和，保留九位小数','拟第四章：主变价格来源','案例范围差异；仿真系数');primary.append(records[-1]['id'])
    # 独立现金流及六路径成本分项，来源直接指向已复算的可执行证据。
    evidence_path=EVID/'本阶段独立核查.json';node(evidence_path,list(RESULT.glob('*_stations.csv'))+list(RESULT.glob('*_years.csv'))+[OUT/'审计工具/独立核查.py'],'按设备事件独立重建现金流，不修改原解')
    costtable=['| 单元 | 方案 | 首次投资现值 | 更新投资现值 | 固定运维现值 | 总费用现值 |','| --- | --- | ---: | ---: | ---: | ---: |']
    for ix,row in enumerate(independent['cost_breakdown']):
        prefix=REGIONS[row['region']]+('29站' if row['region']=='QX-00007' else '')+' '+str(row['voltage_kv'])+'kV '+SCHEMES[row['scheme']]
        costtable.append(f"| {prefix.rsplit(' ',1)[0]} | {SCHEMES[row['scheme']]} | {row['initial_capex_npv']:.2f} | {row['renewal_capex_npv']:.2f} | {row['fixed_om_npv']:.2f} | {row['total_npv']:.2f} |")
        for key,title in [('initial_capex_npv','首次投资现值'),('renewal_capex_npv','更新投资现值'),('fixed_om_npv','固定运维现值'),('total_npv','总费用现值')]:
            add(prefix+title,'C分项',row[key],'万元',evidence_path,f'JSON $.cost_breakdown[{ix}].{key}','F15a至F15e；逐站投资事件现金流按科目折现加总','拟第四、五章：费用分解','本阶段独立派生；原结果未改',formula_ref='F15e');primary.append(records[-1]['id'])
    for i,event in enumerate(independent['cashflow_events']):
        scope=REGIONS[event['region']]+' '+str(event['voltage_kv'])+'kV '+SCHEMES[event['scheme']]+' '+event['measure']+' '+str(event['commissioning_year'])+'年投运 '+str(event['year'])+'年'+event['component']
        for key,suffix in [('amount_10k_cny','现金流'),('npv_10k_cny','现值')]:
            add(scope+suffix,'A(t)' if key=='amount_10k_cny' else 'PV(t)',event[key],'万元',evidence_path,f'JSON $.cashflow_events[{i}].{key}','F15d' if key=='amount_10k_cny' else FORMULAS['F15e'],'拟技术附录：逐事件现金流','本阶段独立派生；原结果未改',scope,formula_ref='F15d' if key=='amount_10k_cny' else 'F15e');technical.append(records[-1]['id'])

    # 历史材料全部登记文本与数值扫描；不把其数字自动准入。
    materials=[]
    for p in sorted((ROOT/'研究报告').rglob('*')):
        if not p.is_file() or '00审查' in p.parts or p.name in ['data_source.json','数据来源审查.pdf']:continue
        extracted='';method='元数据登记'
        if p.suffix=='.md':extracted=p.read_text();method='全文读取'
        elif p.suffix=='.docx':
            with zipfile.ZipFile(p) as z:
                if 'word/document.xml' in z.namelist():extracted='\n'.join(e.text or '' for e in ET.fromstring(z.read('word/document.xml')).iter() if e.tag.endswith('}t'))
            method='正文及表格XML全文提取'
        elif p.suffix=='.pdf':
            import pymupdf
            doc=pymupdf.open(p);extracted='\n'.join(page.get_text() for page in doc);doc.close();method='文本提取；图片内容不自动认定已审核'
        if extracted:
            terms=['EAC','年化','等年','NSGA','AHP','弃光','N-1','N−1','DL/T 2041','DL/T 5729','容载比','成本','苏州','XX','5.3亿']
            hits={t:len(re.findall(re.escape(t),extracted)) for t in terms if t in extracted}
            # 摘录实际上下文以便复查，不自动把旧值变为冻结事实。
            samples=[line.strip()[:350] for line in extracted.splitlines() if any(t in line for t in ['等年','年化','5.3亿','增长率不大于','NSGA','弃光','XX公司'])][:15]
        else:hits={};samples=[]
        materials.append({'path':rel(p),'sha256':sha(p),'method':method,'characters':len(extracted),'numeric_tokens':len(re.findall(r'\d+(?:\.\d+)?',extracted)),'terms':hits,'review_contexts':samples,'admission':'仅背景、任务沿革及文风；旧数值不自动准入；正文引用需重新核验登记'})
    dump(EVID/'历史材料审查索引.json',materials)
    while True:
        missing={parent for n in list(nodes.values()) for parent in n['parents'] if parent not in nodes}
        if not missing:break
        for parent in sorted(missing):node(ROOT/parent)
    dump(EVID/'数据来源图.json',{'nodes':list(nodes.values()),'note':'文件级父节点及计算过程；记录级源位置在data_source.json，代码与数据终点均附SHA256'})
    # 已注册路径组成明确引用名单，未登记数字禁止写入报告。
    data={'schema_version':'1.0','freeze_date':'2026-09-27','baseline':{'local_commit':version['local_commit'],'remote_main_commit':version['remote_main_commit'],'user_confirmed':'本地v4','model_result_unchanged':True},'chapter_status':'拟引用章节；不代表已生成正文或最终图表号','records':records,'source_graph':list(nodes.values()),'region_mapping':REGIONS,'admitted_record_ids':primary,'technical_appendix_record_ids':technical,'historical_evidence_record_ids':history,'unresolved_items':['非完整DL/T2041系统及设备承载力评估','市区三站设备容量缺口和421小时共同缺测','固定参考净峰未计规划储能动作','储能无逐时SOC及损耗','网损、退出拆改、残值及新线配套费用未评估','背景统计及文献阈值需另行核验','GitHub main尚未同步本地v4']}
    dump(OUT/'data_source.json',data)
    source_dir=ROOT/'研究报告/数据来源';source_dir.mkdir(exist_ok=True)
    (source_dir/'data_source.json').write_bytes((OUT/'data_source.json').read_bytes())
    workbook=openpyxl.Workbook();workbook.remove(workbook.active)
    headers=['编号','数据名称','变量名称','数值','单位','来源文件','来源位置','计算方式','报告章节位置','引用资格','适用边界','原始值表示','来源SHA256']
    def sheet(name,selected):
        ws=workbook.create_sheet(name);ws.append(headers)
        for r in selected:ws.append([r['id'],r['name'],r['variable'],r['value'],r['unit'],r['source'],r['source_location'],r['formula'],r['chapter'],r['status'],r['limitation'],r['raw_value'],r['source_sha256']])
        ws.freeze_panes='D2';ws.auto_filter.ref=ws.dimensions
        for c in ws[1]:c.font=Font(bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor='244862');c.alignment=Alignment(wrap_text=True)
        widths=[13,55,22,21,16,72,56,80,47,43,70,23,68]
        for i,w in enumerate(widths,1):ws.column_dimensions[get_column_letter(i)].width=w
        for row in ws.iter_rows(min_row=2):
            row[3].number_format='0.###############'
        return ws
    pset=set(primary);tset=set(technical);hset=set(history)
    sheet('报告准入数据',[r for r in records if r['id'] in pset])
    sheet('技术附录明细',[r for r in records if r['id'] in tset])
    sheet('历史汇总限制引用',[r for r in records if r['id'] in hset])
    mapping=workbook.create_sheet('内部地区映射');mapping.append(['中文名称','内部编码','正文规则'])
    for k,v in REGIONS.items():mapping.append([v,k,'正文仅使用中文名称；本版本仅两地区三个研究单元有优化结果'])
    sources=workbook.create_sheet('来源与计算图');sources.append(['来源编号','文件','SHA256','父级来源文件','计算过程'])
    for n in nodes.values():sources.append([n['id'],n['path'],n['sha256'],'\n'.join(n['parents']),n['process']])
    metadata=workbook.create_sheet('冻结口径');metadata.append(['事项','说明'])
    for k,v in [('版本',version['local_commit']),('远端main',version['remote_main_commit']),('经济目标','2022至2041增量费用折现到2021年的现值；不是累计等年成本'),('章号','拟引用位置；正文未生成'),('空值','不表示零；常量相关性不定义或无已证明最优解'),('精度','按原值保存；显示时统一舍入；不得手工改值'),('引用规则','准入数据带研究条件；技术明细限技术附录；历史汇总暂不进入正文'),('重复字段','同一结果可能在汇总、矩阵、明细重复登记，不得把重复记录再相加'),('禁止项','不得生成终稿Word、改模型或结果、补造数字或AHP权重')]:metadata.append([k,v])
    workbook.save(OUT/'最终数据字典.xlsx')
    admitted=[r for r in records if r['id'] in pset]
    numeric_count=sum(r['value'] is not None for r in records)
    stats={'status':'PASS','records':len(records),'report_admitted_records':len(primary),'technical_records':len(technical),'historical_records':len(history),'numeric_records':numeric_count,'source_nodes':len(nodes),'historical_materials':len(materials),'independent_checks':independent['checks'],'reproduction_checks':reproduction['checks']}
    dump(EVID/'交付统计.json',stats)
    costmd='\n'.join(costtable)
    freeze=f'''# 结果冻结报告\n\n冻结日期：2026-09-27。用户已确认采用本地 v4。代码与原结果只读核验，输出冻结资料未改模型参数及求解结果。\n\n## 冻结范围\n\n冻结三个研究单元的六条基准路径、12行年度推荐，及邳州110kV基准与三项价格敏感性的八条路径、16行年度推荐。原逐站结果保留，同费用等价分配不替换。其他地区只有年度事实统计，本版本没有优化推荐值。\n\n原冻结清单409文件通过核验；新增原件快照491文件保持一致。当前模型72项测试通过，4条提示均为原Excel缺默认样式。隔离副本中的基础六路径、12行年度指标和价格敏感性2731项检查通过；本阶段额外从源表及原事件完成{independent['checks']}项独立检查。六路径完整重求后进行了{reproduction['checks']}项字段对账，区域年度结果和费用通过容差核验；存在{len(reproduction['equal_cost_station_layout_differences'])}份逐站等价分配差异，保留原版。\n\n初次隔离核验因副本漏拷根目录四个非模型文件失败，补齐后409文件通过。失败日志和复核日志均保留，不作为原项目数据缺陷。\n\n## 成本分项\n\n下表金额单位万元，均为评价期2022至2041年折现至2021年的现值。首次投资、更新投资和固定运维由原逐站事件独立重建，不能当作当年现金投资或等年成本。\n\n{costmd}\n\n## 数据引用范围\n\n原409文件清单没有覆盖根目录储能价格登记及公告。本阶段扩展快照、来源图及新清单已补齐实际依赖；隔离复现按扩展快照复制，不改模型或价格。\n\n数据字典登记{len(records)}条记录，其中报告准入{len(primary)}条、技术附录{len(technical)}条、历史汇总限制引用{len(history)}条。来源图登记{len(nodes)}个文件节点，含原表、代码和加工输入。每项数据均有源位置、数值、单位、计算说明、来源哈希及拟使用章节。重复出现在不同结果表的数值分别定位，不重复统计经济总量。\n\n报告只引用准入名单，且保留每项适用条件。技术明细只能在相应附录使用。旧方案、预算/恢复比例历史汇总、尚无完整证据的情景及旧报告数字不自动进入正文。背景统计和文献参数须另行核验登记；本阶段没有完成外部背景文献的逐条真实性复核。\n\n## 标准与研究假设\n\n推荐容载比是本课题对导则未给出数值的规划指标开展的研究。刚性上限2.0、弹性上限3.2、增配预算及停运恢复比例均为情景假设。反向容量是站级初筛，未区分实际并列/分列运行，未完成系统级承载力、备案容量及上级约束；不得声称完整DL/T2041评估通过。研究结论可在这些条件下引用，工程实施还需相应核查。\n\n## 资料整理\n\n历史结果清理见《废弃结果清理清单》及相应压缩包。原输入及409文件冻结清单中的中间证据保留，部分planning文件仍为当前依赖，不能按名称批量删除。历史报告只作任务沿革、背景和文风参照，审查索引见证据目录。\n\n## 后续使用\n\n本阶段未生成研究报告正文或最终Word。章号均为拟引用位置，后续写作必须补充最终图表和段落定位，保留数据编号。代码字段不进入正文，地区编码仅用于内部映射。所有数值由字典读取并统一舍入，无法从名单追溯的数值先登记核查，不以经验补足。\n\n现有研究报告目录规则仍含前版成本及容载比表述；用户本次确认的v4及本审查口径优先，后续生成正文前应同步目录写作规则。GitHub main尚未上传本地更新，本阶段没有提交或推送。\n'''
    (OUT/'结果冻结报告.md').write_text(freeze)
    stage=f'''# 阶段0完成报告\n\n本阶段已完成本地v4模型、原始资料、结果及报告输入审查，形成七项主交付文件。未生成研究报告正文及最终Word，没有改模型结果、手工调数或补造结果。\n\n## 已冻结内容\n\n基线为本地提交`{version['local_commit']}`。冻结三个研究单元的六条基准路径、12行年度推荐，以及邳州110kV独立价格情景的八条路径和16行年度推荐。数据字典共{len(records)}条记录，每条包含来源、位置、计算、单位、引用资格与拟使用章节。源表、代码和结果的文件级计算血缘已建立，人工审查PDF与机器JSON从同一登记表生成。\n\n409文件原冻结清单通过核验；72项当前模型测试通过。六路径在隔离目录完整重求并与原表对账，新增{independent['checks']}项独立检查通过，价格敏感性2731项检查通过。原输入及原结果快照一致，原逐站方案保留。\n\n## 未解决问题\n\n原409文件清单没有覆盖根目录储能价格登记及公告。本阶段扩展快照、来源图及新清单已补齐实际依赖；隔离复现按扩展快照复制，不改模型或价格。\n\n1. 市区29站与全市区不是同一边界，三站缺少设备容量原件；共同缺测421小时，补值不作为实测。历史站级场景和持续时间使用2025模板。\n2. 当前参考容载比使用固定年度净峰，没有计入规划储能动作后的同边界逐时净负荷；不能称措施后实测物理容载比。\n3. 反向条件为站级容量初筛，缺实际主变运行方式、系统级承载力、有效备案未并网容量和上下级校核，尚不能发布完整标准承载力或颜色等级。\n4. 储能没有逐时荷电状态、转换损耗、衰减和站址检查；候选新线没有测绘及完整工程造价、电压、短路和保护校核。\n5. 未评估网损、容量退出拆改、残值和部分新线配套费用；旧投资批次运维未随后续容量退出注销。当前现值是既定简化费用边界内的比选结果。\n6. 背景统计数、文献阈值和旧报告的数字未自动准入；DL/T 5729-2023 配电网规划导则正文尚缺，不能把修订稿分档当作现行条款。历史汇总中只有总量、无完整路径的情景暂不进入正文。\n7. GitHub main仍停留在8月27日，本地领先133个提交。用户已确认本地为基准，本阶段没有上传。研究报告目录写作规则含前版口径，正式写作前需同步。\n\n## 后续报告生成注意事项\n\n研究任务是探究导则未给出推荐值的容载比方案，结论应说明源荷、存量容量、转供候选、预算及成本条件。推荐值是条件研究成果，不是导则规定值；导则未给出推荐值本身不属于模型缺陷。两个方案同时改变容载比上限及增配预算，费用差不能全部归因于单独放宽容载比。\n\n正文只采用字典准入数据，技术明细限附录，历史汇总暂不引用。35kV与110kV分别呈现，市区保留29站样本说明。经济目标统一写2022至2041年增量费用现值，折现基年2021；不能沿用累计在役等年成本。地区名称使用中文，内部编码不进入正文。\n\n正式章节形成后，将数据编号关联到实际图表号和段落，补充外部引用核查；不要改现有字典数值来迎合正文。新增数据或模型范围变更另建版本并重审。文字按humanizer和电网工程报告文风复查，保证润色不改变条件、量纲或证据强度。\n\n七项主文件位于本目录；数据来源审查PDF和JSON在`研究报告/数据来源/`也保存同版副本。复核代码与已执行的笔记本位于审计工具目录，检查日志、来源图、版本记录和哈希清单位于证据目录。\n'''
    (OUT/'阶段0完成报告.md').write_text(stage)
    # PDF面向人工阅读：关键矩阵、费用分解、逐项准入登记，技术逐事件数据由字典承接。
    es=lambda x:html.escape(str(x))
    def display(v):
        if v is None:return '未定义/缺失，不填零'
        if isinstance(v,(int,float)):return f'{v:.12g}'
        return str(v)
    body=['<h1>数据来源审查</h1>','<p>徐州地区容载比弹性指标研究。阶段0，2026年9月27日。</p>',
          '<p>本册核对已登记数据的来源、计算和拟引用章节，未生成研究报告正文。推荐值来自本地最终模型的完整四年路径，属于已有样本及工程假设下的研究结果。</p>',
          '<p>邳州分35kV与110kV计算，市区保留29站样本边界。费用为2022至2041年增量费用折现至2021年的现值，单位万元。未计费用不得当作真实零费用。</p>',
          '<h2>人工审查方法</h2><p>按数据编号在最终数据字典中查找完整数值及来源位置；本册的来源编号对应原文件或计算证据。技术附录包含逐站和逐事件明细，按同一来源及公式登记，不把其重复字段累计为新的总量。章号为拟引用位置，后续正文需登记最终图表和段落。</p>',
          '<h2>基础年度推荐</h2><table><tr><th>研究单元</th><th>年</th><th>参考净峰MW</th><th>推荐容量MVA</th><th>推荐比值</th><th>储能柜数</th></tr>']
    for r in csvrows(RESULT/'annual_matrix.csv'):
        body.append('<tr>'+''.join('<td>'+es(x)+'</td>' for x in [REGIONS[r['study_region_id']]+('29站' if r['study_region_id']=='QX-00007' else '')+' '+r['voltage_kv']+'kV',r['year'],f"{float(r['reference_peak_mw']):.3f}",r['elastic_capacity_mva'],f"{float(r['elastic_clr']):.3f}",r['elastic_storage_modules']])+'</tr>')
    body+=['</table><h2>费用边界及分项</h2><p>首次投资、更新投资和运维单独折现加总。源数据和原方案保持不变。本版未计算网损、储能效率、拆改、残值和全部新线配套工程费用。</p><table><tr><th>研究单元及方案</th><th>首次投资现值</th><th>更新现值</th><th>运维现值</th><th>总费用现值</th></tr>']
    for r in independent['cost_breakdown']:
        body.append('<tr>'+''.join('<td>'+es(x)+'</td>' for x in [REGIONS[r['region']]+' '+str(r['voltage_kv'])+'kV '+SCHEMES[r['scheme']]]+[f'{r[k]:.2f}' for k in ['initial_capex_npv','renewal_capex_npv','fixed_om_npv','total_npv']])+'</tr>')
    body.append('</table><h2>逐项准入数据</h2><p>以下逐项列明数据名称、数值、单位、来源、计算方式和拟引用位置。空值表示未定义，不作为零引用。所有报告准入记录均列入，技术逐站与现金流明细见字典附录。</p>')
    for i in range(0,len(admitted),12):
        body.append('<table><tr><th>编号及数据名称</th><th>值及单位</th><th>来源及位置</th><th>计算方式、章节及边界</th></tr>')
        for r in admitted[i:i+12]:
            loc=r['source_location'];loc=re.sub(r'；字段\w+','',loc)
            if 'L' in loc and ': ' in loc:loc=loc.split(': ',1)[0]
            body.append('<tr><td>'+es(r['id'])+'<br>'+es(r['name'])+'</td><td>'+es(display(r['value']))+' '+es(r['unit'])+'</td><td>'+es(source_ids[r['source']])+'<br>'+es(loc)+'</td><td>'+es(r['formula'])+'<br>'+es(r['chapter'])+'<br>'+es(r['limitation'])+'</td></tr>')
        body.append('</table>')
    used={r['source'] for r in records}
    body.append('<h2>来源目录</h2><p>编号对应真实源文件；完整路径、计算父节点和文件校验值保存在数据字典及机器审查文件。本册只显示便于阅读的来源名称。</p><table><tr><th>编号</th><th>来源名称</th><th>计算及使用说明</th></tr>')
    for key in sorted(used):
        n=nodes[key];body.append('<tr><td>'+es(n['id'])+'</td><td>'+es(mapped(Path(key).name))+'</td><td>'+es(n['process'])+'</td></tr>')
    body.append('</table><h2>限制及后续引用</h2><p>主变运行方式、系统级承载力及备案资料尚未闭合，不能声称完整导则评估通过。停运恢复比例、容量预算和容载比上限为研究假设。市区设备容量缺口、历史模板、静态储能与未测绘新线条件需要在报告相应章节保留。其他地区尚无本版本推荐值。</p><p>引用时按原值统一舍入，保留样本边界及研究假设。新增数据须登记来源并重新核查。</p>')
    text='<html><head><meta charset="utf-8"></head><body>'+''.join(body)+'</body></html>'
    # 使用完整原字体；拉丁数字独立字体保证数据编号可检索。
    css="""@page{size:A4;margin:16mm 12mm}body{font-family:'DejaVu Serif','Noto Serif CJK SC',serif;font-size:9pt;line-height:1.4;color:#222}h1{font-size:21pt;color:#244862}h2{font-size:14pt;color:#244862;margin-top:16pt}table{border-collapse:collapse;width:100%;font-size:7.8pt;margin:8pt 0}td,th{border:0.5pt solid #ccd6dd;padding:4pt;vertical-align:top}th{background:#e8eff4}tr{break-inside:avoid;page-break-inside:avoid}p{margin:6pt 0}thead{display:table-header-group}"""
    text=text.replace('</head>','<style>'+css+'</style></head>')
    text=re.sub(r'(<table>)<tr>(.*?)</tr>',r'\1<thead><tr>\2</tr></thead><tbody>',text,flags=re.S).replace('</table>','</tbody></table>')
    # 该HTML是同源PDF的打印中间件，不是研究报告正文。
    (EVID/'数据来源审查打印.html').write_text(text)
    import pymupdf
    import tempfile
    raw_pdf=EVID/'数据来源审查_浏览器打印.pdf'
    if '--skip-print' not in sys.argv:
        with tempfile.TemporaryDirectory(prefix='rzb-stage0-print-') as profile:
            command=['google-chrome','--headless','--no-sandbox','--disable-gpu','--disable-background-networking','--disable-extensions','--disable-sync','--no-pdf-header-footer','--user-data-dir='+profile,'--print-to-pdf='+str(raw_pdf),(EVID/'数据来源审查打印.html').as_uri()]
            printing=subprocess.run(command,capture_output=True,text=True,timeout=180)
            (EVID/'PDF打印.log').write_text(printing.stdout+printing.stderr)
            if printing.returncode:raise RuntimeError('PDF打印失败，请查看日志；可单独打印HTML后使用--skip-print')
    page_rect=pymupdf.paper_rect('a4')
    document=pymupdf.open(raw_pdf)
    for i,page in enumerate(document):page.insert_text((35,page_rect.height-22),f'{i+1} / {len(document)}',fontsize=8,color=(.3,.3,.3))
    document.save(str(EVID/'数据来源审查_带页码.pdf'),garbage=4,deflate=True);document.close()
    (OUT/'数据来源审查.pdf').write_bytes((EVID/'数据来源审查_带页码.pdf').read_bytes())
    (source_dir/'数据来源审查.pdf').write_bytes((OUT/'数据来源审查.pdf').read_bytes())
    # 笔记本直接执行只读核查程序的关键核查，不在笔记本中调用求解或覆盖原结果。
    import nbformat
    notebook=nbformat.v4.new_notebook()
    cells=[nbformat.v4.new_markdown_cell('# 阶段0只读核查\n\n本笔记本复核冻结哈希、完整路径费用及参考比值，供技术人员重复检查。原结果不修改。完整约束与源表复算程序为同目录的独立核查.py。'),nbformat.v4.new_markdown_cell('## 数据与方法\n\n采用项目专用环境。研究范围为三个单元；费用口径为增量现金流现值，固定年度分母不含规划储能动作。'),nbformat.v4.new_code_cell("from pathlib import Path\nimport json,hashlib,csv,math\naudit_dir=Path.cwd()\nif not (audit_dir/'证据').is_dir():\n    audit_dir=Path('研究报告/00审查').resolve()\nroot=audit_dir.parents[1]\nsnapshot=json.loads((audit_dir/'证据/输入与原结果快照.json').read_text())\nassert all(hashlib.sha256((root/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in snapshot)\nprint('原输入及原结果快照核验：',len(snapshot),'文件通过')"),nbformat.v4.new_markdown_cell('## 结果\n\n从原CSV重算年度比值和路径费用加总，不引入新的模型解。'),nbformat.v4.new_code_cell("result=root/'实验/研究/rebuild_2026/source_audit/capacity_release_simulation/reserve_policy_v4'\ndef read(p):\n    with p.open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))\nsummary=read(result/'summary.csv')\nfor r in summary:\n    year=read(result/f\"{r['scheme']}_{r['study_region_id']}_{r['voltage_kv']}_years.csv\")\n    assert math.isclose(sum(float(y['year_lifecycle_npv_10k_cny']) for y in year),float(r['objective_npv_10k_cny']),abs_tol=1e-3)\n    for y in year:\n        assert math.isclose(float(y['selected_capacity_mva'])/float(y['synchronous_forward_peak_mw']),float(y['actual_clr']),abs_tol=1e-7)\nprint('六路径费用与24行方案年度比值通过')"),nbformat.v4.new_code_cell("evidence=json.loads((audit_dir/'证据/本阶段独立核查.json').read_text())\nassert evidence['status']=='PASS'\nprint('源表、约束与现金流独立检查：',evidence['checks'],'项通过')\nreproduction=json.loads((audit_dir/'证据/本阶段完整重求对账.json').read_text())\nassert reproduction['status']=='PASS'\nprint('完整重求对账：',reproduction['checks'],'项通过')"),nbformat.v4.new_markdown_cell('## 使用范围\n\n核查通过表示当前数据与实现一致。推荐值仍受模型假设约束，不能代替完整标准承载力评估及工程实施校核。')]
    notebook.cells=cells;notebook.metadata.kernelspec={'display_name':'Python 3','language':'python','name':'python3'}
    # 按序实际执行并记录输出，采用当前专用解释器；不依赖另外注册的内核。
    namespace={};import contextlib,io
    for i,cell in enumerate(cells):
        if cell.cell_type=='code':
            stream=io.StringIO()
            with contextlib.redirect_stdout(stream):exec(compile(cell.source,'stage0_notebook','exec'),namespace)
            cell.execution_count=sum(c.cell_type=='code' for c in cells[:i+1]);cell.outputs=[nbformat.v4.new_output('stream',name='stdout',text=stream.getvalue())]
    nbformat.validate(notebook);nbformat.write(notebook,OUT/'审计工具/阶段0只读核查.ipynb')
    dump(EVID/'笔记本执行记录.json',{'status':'PASS','method':'nbformat生成并按顺序在项目专用Python逐代码单元执行；非伪造输出','executable':sys.executable,'code_cells':sum(c.cell_type=='code' for c in cells)})
    print(json.dumps(stats,ensure_ascii=False))

if __name__=='__main__':main()
