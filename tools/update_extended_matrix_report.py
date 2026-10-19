"""扩展数据独立核验通过后，局部同步当前六章、表格及维护规则。"""
from pathlib import Path
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from extend_matrix_scenarios import PUBLIC,REVIEW,SOURCE,write


def replace(path,old,new):
    source=path.read_text()
    assert source.count(old)==1,(str(path),old[:100],source.count(old))
    path.write_text(source.replace(old,new))


def main():
    proof=json.loads((REVIEW/'扩展数据独立核验.json').read_text())
    assert proof['状态']=='通过' and proof['设计节点数']==127578
    assert hashlib.sha256((PUBLIC/'统一有效样本.csv').read_bytes()).hexdigest()==proof['有效样本SHA256']
    policy_path=ROOT/'tools/report_policy.json';policy=json.loads(policy_path.read_text())
    policy.update(version='2026-10-19-eleven-diversity-nodes-windows',plain_delivery_review=str(REVIEW.relative_to(ROOT)),target_body_pages=169)
    policy['matrix_display'].update(diversity_values=[round(1.05+.02*i,2) for i in range(11)],diversity_cut=1.15,
        diversity_bins=['≤1.15','>1.15'],cells=288,
        output_kind='fixed_width_sliding_windows',window_width=.2,window_step=.05,
        band_boundary_method='选最接近样本中位数的实际节点，同距时取较大值，中心取最近0.05网格，宽0.20；同值保留同窗',
        source_csv=str((PUBLIC/'统一有效样本.csv').relative_to(ROOT)))
    policy['forbidden_body_patterns']['删除指定源荷补值与规划峰值重复说明']='历史回算与未来预测均保留所采用的补值'
    policy['forbidden_body_patterns']['推广矩阵采用11点两档']='1[.]15为本研究情景范围的上端|三个分散系数定值|九张表432个单元'
    write(policy_path,policy)
    write(REVIEW/'交付模式.json',dict(修订模式=False,基线='研究报告/04_word/研究报告终稿.docx',
        基线原件='修前原件/研究报告/04_word/研究报告终稿.docx',批注原件='修前原件/研究报告/04_word/研究报告终稿.docx',
        全市光伏单位换算系数=1,用户依据='五项最新反馈；分散系数最终确认为1.05—1.25、间隔0.02，共11点；先数据后报告。',
        允许更新图件=['研究报告/02图表/当前版/lookup_matrix_bounds.png','研究报告/02图表/当前版/diversity_device_response.png'],
        允许替换表键前缀=['lookup_matrix_'],允许更新表键=['new_parameter_bins','new_template_assumptions','current_diversity_sequence','typical_transfer_matrix'],
        允许更新生成段落=['new_matrix_summary','new_matrix_tables','typical_matrix_summary'],
        矩阵批注锚点='电缆长度占比≤10%、负荷分散系数≤1.15的容载比分档建议矩阵'))
    chapter=ROOT/'研究报告/03_MD/当前版'
    files={p.name[:2]:p for p in chapter.glob('0[1-6] *.md')}
    replace(files['05'],
        '2021—2024年小时源荷根据2025年站级模板及各年光伏规模回算，负荷按原年度区域正向峰值标定；2025年沿用站级小时样本。2026—2035年未来源荷按区域负荷预测及全市光伏装机相对2025年的比例缩放，站点空间分配继承基准模板。历史回算与未来预测均保留所采用的补值，年度规划峰值继续使用同范围年度统计及其预测外推值。',
        '2021—2024年小时源荷根据2025年站级模板及各年光伏规模回算，负荷按原年度区域正向峰值标定。2026—2035年未来源荷按区域负荷预测及全市光伏装机相对2025年的比例缩放，站点空间分配继承基准模板，未来源荷的预测数据详见第3.2节和第3.3节。')
    replace(files['03'],
        '既有通道与新增候选分别记录馈线端点和有效容量，各通道共同校核源端可切负荷、共享馈线余量和接收站容量。新增联络单项参考能力以墩振线23—24杆拟设分段点下游的可转供区段为测算对象。根据已有配电变压器资料，该区段配电变压器额定容量合计占全馈线已识别总容量的90.97%。以该馈线2025年最大有功负荷8.23 MW为计算依据，按上述容量比例估算，区段负荷为7.49 MW。新增路径按550 A允许电流及0.95功率因数折算的有功容量为9.05 MW，因此取区段负荷7.49 MW作为单项新增联络的参考转供能力。',
        '既有通道与新增候选分别记录馈线端点和有效容量，各通道共同校核源端可切负荷、共享馈线余量和接收站容量。邳州403条10 kV线路中，最大允许电流为416 A的有4条、455 A的有1条，其余398条均不低于485 A。485 A对应视在容量8.40 MVA，新增联络的工程计算限值取8.00 MVA，按0.95功率因数折算有功上限为7.60 MW。具体可转功率还受可切换区段负荷限制。墩振线23—24杆拟设分段点下游配电变压器额定容量占全馈线已识别容量的90.97%，按该馈线2025年最大有功负荷8.23 MW分配，区段负荷为7.49 MW，作为该区段的有效转供功率。')
    replace(files['03'],
        r'F_{\mathrm{new}}=\frac{\sqrt3\,U I_{\mathrm{allow}}\cos\varphi}{1000}=\frac{\sqrt3\times10\times550\times0.95}{1000}'+'\n'+r'\approx9.05\ \mathrm{MW},',
        r'F_{\mathrm{new}}=S_{\mathrm{new}}\cos\varphi=8.00\times0.95=7.60\ \mathrm{MW},')
    replace(files['03'],
        '$U$为线电压，取10 kV，$I_{\\mathrm{allow}}$为新增路径的研究允许电流，取550 A，$\\cos\\varphi$取0.95；',
        '$S_{\\mathrm{new}}$为新增联络的工程视在容量限值，取8.00 MVA，$\\cos\\varphi$取0.95；')
    replace(files['04'],
        '新增联络能力的取值依据邳州局部六条10 kV馈线的结构化资料、联络关系及区段明细。先按开关位置识别可切换区段，再核对区段负荷、线路允许电流和接收侧余量。墩振线23—24杆下游区段的2025年压力场景负荷汇总为7.49 MW，作为新增独立接收馈线的候选转移规模，低于按允许电流及0.95功率因数折算的有功容量9.05 MW，计算过程见第3.6.2节。7.49 MW是该区段场景计算的参考规模，实际可转功率还受送受端馈线、路径共享和邻站主变余量共同限制。模型按具体送受端设置候选联络通道，既有工程不重复计原建设费，新增联络按投运年计费。',
        '新增联络能力的取值依据邳州10 kV线路允许电流、联络关系及区段明细。工程计算限值取8.00 MVA，按0.95功率因数折算有功上限为7.60 MW，依据见第3.6.2节。具体候选通道按开关位置识别可切换区段，并共同核对区段负荷、路径共享及接收侧余量。墩振线23—24杆下游区段的参考转移规模为7.49 MW，低于上述线路限值。模型按具体送受端设置候选联络，既有工程不重复计原建设费，新增联络按投运年计费。')
    replace(files['03'],
        '两地区样本为1.00、1.10、1.15三个推广节点提供参照，其中1.15为本研究情景范围的上端。站间峰值越不同步，系数还可能高于1.15，实际取值应由同范围同期曲线计算。',
        '推广仿真在1.05—1.25内按0.02间隔取11个节点，以1.15为界分为两档，考察较大局部高峰差异下的设备需求。实际取值由同范围同期曲线计算。')
    replace(files['01'],
        '分别给出三个负荷分散系数下的完整源荷与转供区间',
        '按负荷分散系数≤1.15和>1.15两档给出完整源荷与转供区间')
    replace(files['05'],
        '同一行以各转供档可行配置的容载比下界作为分档界值，首档上界取该档最大值，后续各档上界与前一档下界相接，形成连续的规划推荐带；下界相同的档位保留相同定值。推荐带用于初步容量比选，具体设备仍需按源荷与网络条件校核。',
        '每个单元取最接近样本容载比中位数的实际仿真节点为代表，同距时采用较大值。推荐窗口宽度统一为0.20，中心取最接近该代表值的0.05网格值。窗口随各单元的代表容量水平移动，表示中部配置的容量初选范围。实际设备按片区源荷与网络条件校核。')
    replace(files['05'],
        '以电缆长度占比≤10%、负荷分散系数1.10、年最大净负荷平均增长率>7%、装机渗透率(1,2]这一行为例，初始转供率四档的推荐带依次为1.91～2.09、1.76～1.91、1.50～1.76、1.36～1.50，相邻档共用1.91、1.76、1.50三个分界值。较强转供条件对应较低的本地容量推荐范围。第5.6.4节固定其余条件，以完整节点说明具体主变组合及费用。',
        example_paragraph())
    replace(files['05'],
        '推荐带端点图以电缆长度占比>30%、负荷分散系数1.10为例，按与矩阵相同的行列次序展示下界和上界，两图采用相同色阶。装机渗透率较高的行具有较大的反向容量任务，年最大净负荷平均增长率改变负荷规模及既有容量储备，转供条件则影响局部支援。图中端点采用上述分档界值，读取推荐带后，按实际参数和设备条件确定对应方案。',
        '推荐窗口端点图以电缆长度占比>30%、负荷分散系数>1.15为例，按与矩阵相同的行列次序展示下界和上界，两图采用相同色阶。装机渗透率较高的行具有较大的反向容量任务，年最大净负荷平均增长率改变负荷规模及既有容量储备，转供条件则影响局部支援。读取推荐窗口后，按实际参数和设备条件确定对应方案。')
    replace(files['05'],'图5-0 电缆长度占比>30%、负荷分散系数1.10下的矩阵端点','图5-0 电缆长度占比>30%、负荷分散系数>1.15下的矩阵端点')
    replace(files['05'],
        '两组均在四档转供率间形成不同的推荐区间，说明既有网络改善能够在各档体现为区域容量需求下降，同时改变新增工程组合。',
        '两组完整节点显示，既有网络改善总体降低本地容量需求，同时改变新增工程组合。局部平台和回升对应具体设备替代。')
    update_sensitivity(files['05'])
    replace(files['06'],
        '区间矩阵按电缆长度占比≤10%、(10%,30%]、>30%分区，每档分别列示负荷分散系数1.00、1.10、1.15，年最大净负荷平均增长率四档、装机渗透率三档与初始转供率四档组成九张表432个单元，同一行按各转供档容量下界划定首尾相接的规划推荐带。另以两组设备重新选配的典型源荷条件分析18个细节点及8个转供区间，四档推荐带逐档衔接，细节点保留实际设备组合的平台和局部回升。',
        '负荷分散系数在1.05—1.25内按0.02间隔取11个节点，并以1.15分为两档。区间矩阵按电缆长度占比≤10%、(10%,30%]、>30%分区，结合年最大净负荷平均增长率四档、装机渗透率三档与初始转供率四档形成六张表288个单元。各单元由中位代表节点定位宽度0.20的推荐窗口，按0.05步长随条件移动。另以两组设备重新选配的典型源荷条件分析18个细节点及8个转供区间，完整保留设备组合的平台和局部回升。')
    # 参数表只更新授权的四项及矩阵键，不调用案例同步以免写入无关历史登记。
    from sync_current_report_results import parameter_assets
    tables_path=ROOT/'研究报告/02图表/当前版/计算表.json';sections_path=tables_path.with_name('生成段落.json')
    tables=json.loads(tables_path.read_text());sections=json.loads(sections_path.read_text())
    pt,ps,*_=parameter_assets()
    tables={k:v for k,v in tables.items() if not k.startswith('lookup_matrix_')}
    for k,v in pt.items():
        if k.startswith('lookup_matrix_') or k in ['new_parameter_bins','new_template_assumptions','current_diversity_sequence','typical_transfer_matrix']:tables[k]=v
        else:assert tables[k]==v,('非授权参数表出现变化',k)
    sections.update(ps);write(tables_path,tables);write(sections_path,sections)
    update_rules()
    print('扩展数据已核验，六章源及指定表格已最小化同步。')


def example_paragraph():
    cells=json.loads((PUBLIC/'窗口与原始节点依据.json').read_text())
    row=sorted([r for r in cells if r['电缆档']==0 and r['分散档']==0 and r['增长档']==3 and r['装机档']==1],key=lambda r:r['转供档'])
    return '以电缆长度占比≤10%、负荷分散系数≤1.15、年最大净负荷平均增长率>7%、装机渗透率(1,2]这一行为例，初始转供率四档的推荐窗口依次为'+'、'.join(r['推荐窗口'] for r in row)+'。各窗口宽度相同，位置反映相应档位的中部容量需求。第5.6.4节固定其余条件，以完整节点说明具体主变组合及费用。'


def update_sensitivity(path):
    import pandas as pd
    data=pd.read_csv(PUBLIC/'负荷分散系数11点完整序列.csv')
    source=path.read_text();start=source.index('固定装机渗透率2.50、年最大净负荷平均增长率7%、电缆长度占比10%和初始转供率50%，比较负荷分散系数1.00')
    end=source.index('\n## 5.7 ',start)
    changes=[];capacity_steps=[]
    for a,b in zip(data.to_dict('records'),data.iloc[1:].to_dict('records')):
        if abs(b['主变容量_MVA']-a['主变容量_MVA'])>1e-7:
            changes.append(f'{b["负荷分散系数"]:.2f}时主变{b["主变容量_MVA"]:.2f} MVA、联络{int(b["新增联络合计_条"])}项')
            capacity_steps.append((b['负荷分散系数'],b['主变容量_MVA']-a['主变容量_MVA'],b['新增联络合计_条']))
    first,last=data.iloc[0],data.iloc[-1]
    cost_delta=[last[k]-first[k] for k in ['主变费用现值_万元','储能费用现值_万元','线路费用现值_万元','费用现值_万元']]
    description='。'.join(changes)+'。' if changes else '11个节点主变容量保持相同，局部高峰差异通过配套措施调整承担。'
    if capacity_steps:
        description='主变补强发生在'+'和'.join(f'{k:.2f}' for k,delta,n in capacity_steps)+'两个节点，分别增加'+' MVA和'.join(f'{delta:.2f}' for k,delta,n in capacity_steps)+' MVA。新增联络相应由'+str(int(first['新增联络合计_条']))+'项减少至'+str(int(capacity_steps[-1][2]))+'项，站内容量与配储共同替代部分联络支援。'
    for a,b in zip(data.to_dict('records'),data.iloc[1:].to_dict('records')):
        if b['新增联络合计_条']>a['新增联络合计_条'] and abs(b['主变容量_MVA']-a['主变容量_MVA'])<1e-7:
            description+=f'分散系数达到{b["负荷分散系数"]:.2f}时，主变容量保持{b["主变容量_MVA"]:.2f} MVA，新增联络由{int(a["新增联络合计_条"])}项增加至{int(b["新增联络合计_条"])}项，网络支援承担新增局部高峰任务。'
    tail=data.iloc[-3:]
    if len(tail)==3 and all(tail[k].max()-tail[k].min()<1e-7 for k in ['主变容量_MVA','容载比','储能额定功率_MW','新增联络合计_条','费用现值_万元']):
        description+=f'{tail.iloc[0]["负荷分散系数"]:.2f}—{tail.iloc[-1]["负荷分散系数"]:.2f}三个节点采用相同设备规模，容载比与费用形成平台。'
    paragraph=(
        '固定装机渗透率2.50、年最大净负荷平均增长率7%、电缆长度占比10%和初始转供率50%，比较负荷分散系数1.05—1.25、间隔0.02的11个节点。各工况区域负荷合计相同，分散系数改变局部高峰在各站之间的分布，反映相同区域供电任务下站级容量配置的差异。\n\n'
        '[[TABLE:current_diversity_sequence]]\n\n'+description+'\n\n'
        '[[FIG:diversity_device_response|图5-0 负荷分散系数对应的容载比与局部支撑配置]]\n\n'
        f'从1.05至1.25，储能额定功率由{first["储能额定功率_MW"]:.2f} MW调整至{last["储能额定功率_MW"]:.2f} MW，'
        f'容载比由{first["容载比"]:.2f}调整至{last["容载比"]:.2f}。主变、储能及线路费用现值的差额分别为'
        f'{cost_delta[0]:.2f}万元、{cost_delta[1]:.2f}万元、{cost_delta[2]:.2f}万元，合计{cost_delta[3]:.2f}万元。'
        '费用增量主要来自储能配置增加。\n\n'
        '矩阵以1.15划分负荷分散系数区间，将局部高峰条件归入对应推荐窗口。片区应用以同范围站级峰值及区域同时峰值核定该参数，再结合站间支援条件选择容量和配套措施。\n')
    path.write_text(source[:start]+paragraph+source[end:])


def update_rules():
    path=ROOT/'研究报告/AGENTS.md';source=path.read_text()
    old='正文矩阵按各转供档原始容量下界划定相邻档共用界值的规划推荐带，原始节点和设备结果保持；正文矩阵按电缆长度占比≤10%、(10%,30%]、>30%三档与三个负荷分散系数分表，以年最大净负荷平均增长率、装机渗透率选行，初始转供率选列，共432单元。'
    new='正文矩阵采用1.05—1.25、步长0.02的11个负荷分散系数节点，以1.15分为≤1.15和>1.15两档，结合三档电缆长度占比列为六表288单元。单元按最接近中位数的真实节点定位宽0.20、中心步长0.05的推荐窗口，同距取较大容载比，真实平台保留相同窗口；原始极值、代表节点、设备及费用单独核验。'
    assert old in source;path.write_text(source.replace(old,new))
    path=ROOT/'docs/CURRENT-WORKFLOW.md';source=path.read_text()
    source=source.replace('推荐带由`tools/report_matrix_display.py`按原容量下界衔接，原始节点包络另行归档。','推广扩展由`tools/extend_matrix_scenarios.py`独立补算，`tools/verify_extended_matrix.py --lp`先完成任务、费用和独立LP核验，`tools/matrix_planning_windows.py`据有效节点中位数生成固定宽度推荐窗口，原始节点包络另行归档。')
    source=source.replace('正文查表矩阵按电缆长度占比≤10%、(10%,30%]、>30%分区，再按三个负荷分散系数列示完整源荷与转供区间。','正文查表矩阵按电缆长度占比≤10%、(10%,30%]、>30%分区，负荷分散系数1.05—1.25以0.02间隔取11点，再以1.15分两档，形成六表288单元的滑动窗口。')
    source=source.replace('本轮记录集中于`1019公式排版与学者称谓`','本轮记录集中于`1019推广矩阵扩展`').replace('当前普通模式稿及WPS证据集中在`1019公式排版与学者称谓`','当前普通模式稿及WPS证据集中在`1019推广矩阵扩展`')
    path.write_text(source)


if __name__=='__main__':main()
