"""从已确认案例和参数库更新报告资产；不求解、不改锁定库或经济参数。"""
from pathlib import Path
import argparse, hashlib, json, math, sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from 实验.研究.rebuild_2026.case_parameters_20261012 import transfer_diagnostic as case
from 实验.研究.rebuild_2026.static_joint_20261015.model import OperatingLP

REPORT = ROOT/'研究报告'
A = REPORT/'02图表/当前版'
REVIEW = REPORT/'05_review/当前版/1018五项局部修正'
PUBLIC = REPORT/'01研究推荐/当前版/参数联合情景_20261012'
CASE = REPORT/'01研究推荐/当前版/静态联合替代_20261015'
LOCK = REPORT/'01研究推荐/当前版/报告数据采用版本.json'
FIELDS = ['分布式电源装机渗透率','年最大净负荷平均增长率','电缆长度占比',
          '初始转供率','储能支撑持续时间_h','负荷分散系数']
SHORT = ['装机渗透率','年最大净负荷平均增长率','电缆长度占比','初始转供率','支撑持续时间','负荷分散系数']
SYMBOL = ['ηC','ḡ','α','r₀','H','KD']
CUTS = [[1,2],[.02,.04,.07],[.1,.3],[.3,.5,.7]]
LABELS = [['≤1','(1,2]','>2'],['≤2%','(2%,4%]','(4%,7%]','>7%'],
          ['≤10%','(10%,30%]','>30%'],['≤30%','(30%,50%]','(50%,70%]','>70%']]

def display_text(value):
    import re
    value=value.replace('原表容量','实际容量')
    value=value.replace('年最大净负荷平均增长率','__CORE_GROWTH__')
    value=re.sub(r'(?:四年复合平均|复合平均|复合|年平均|平均|负荷)?增长率','年最大净负荷平均增长率',value)
    return value.replace('__CORE_GROWTH__','年最大净负荷平均增长率')


def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def f(x):
    from decimal import Decimal, ROUND_HALF_UP
    return str(Decimal(str(round(float(x),9))).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
def pct(x): return f'{float(x)*100:.0f}%'
def table(title, headers, rows, note=''):
    result=title+'\n\n| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'
    result+=''.join('| '+' | '.join(map(str,row))+' |\n' for row in rows)
    return result+('\n注：'+note+'\n' if note else '')
def interval(lo,hi):
    return f'{math.floor((lo+1e-10)*100)/100:.2f}～{math.ceil((hi-1e-10)*100)/100:.2f}'

def economic_assumptions_table():
    from 实验.研究.rebuild_2026 import current_economic_assumptions as economic
    return table('表4-1 统一经济评价参数',['参数','取值','计算依据与用途'],[
        ['评价基准年/截止年','2021/2041','共同评价期费用比较'],
        ['折现率',f(economic.DISCOUNT_RATE*100)+'%','现值法；统一资金时间价值参数[20—22]'],
        ['主变/线路使用年限',f'{economic.TRANSFORMER_LIFE}/{economic.LINE_LIFE}年','设备更新间隔；本评价期内无更新'],
        ['储能使用年限',f'{economic.STORAGE_LIFE}年','设备更新间隔；本评价期内无更新'],
        ['变电固定运维费率','初始投资'+f(economic.TRANSFORMER_OM*100)+'%/年','按初始投资比例估算年度运维[21]'],
        ['线路固定运维费率','初始投资'+f(economic.LINE_OM*100)+'%/年','按初始投资比例估算年度运维[22]'],
        ['储能固定运维费率','初始投资'+f(economic.STORAGE_OM*100)+'%/年','按初始投资比例估算年度运维[20]']],
        '文献支持费用构成和折现方法，所列年限与费率为本研究统一经济比较取值。')

def controlled_sequences(d):
    controls={
        'eta':(0,[1.5,.04,.1,.4,4,1.1]),
        'growth':(1,[1.5,.04,.1,.4,4,1.1]),
        'cable':(2,[2.75,.055,.1,.6,2,1.15]),
        'transfer':(3,[1.5,.04,.1,.4,4,1.1]),
        'duration':(4,[2.5,.04,.1,.4,4,1.1]),
        'diversity':(5,[2.,.04,.1,.4,4,1.1])}
    results={}
    for name,(index,base) in controls.items():
        mask=np.ones(len(d),dtype=bool)
        for i,field in enumerate(FIELDS):
            if i!=index:mask&=np.isclose(d[field],base[i],atol=1e-10,rtol=0)
        results[name]=d.loc[mask].sort_values(FIELDS[index])
    return results

def matrix_source():
    policy=read(ROOT/'tools/report_policy.json')['matrix_display']
    return ROOT/policy['source_csv'] if 'source_csv' in policy else PUBLIC/'统一有效样本.csv'

def diversity_sequence():
    return controlled_sequences(pd.read_csv(matrix_source()))['diversity']

def parameter_assets():
    d=pd.read_csv(PUBLIC/'统一有效样本.csv')
    from report_parameter_selection import assets as selection_assets
    t=selection_assets();s={}
    adopted=read(LOCK)
    matrix=pd.read_csv(CASE/'典型响应推荐矩阵.csv')
    nodes=pd.read_csv(CASE/'典型场景完整节点.csv')
    cells=[];index=[];rows=[]
    from report_matrix_display import adjoining_bands
    window_mode=read(ROOT/'tools/report_policy.json')['matrix_display'].get('output_kind')=='adaptive_sliding_windows'
    from matrix_planning_windows import adjoining_windows,middle_node
    for i,r in enumerate(matrix.to_dict('records'),1):
        key=f'typical_transfer_{i}'
        bands=adjoining_bands([r[k] for k in LABELS[3]])
        rows.append([pct(r['装机渗透率']),f"{100*r['年最大净负荷平均增长率']:g}%",f(r['负荷分散系数'])]+bands)
        index.append(dict(key=key,装机渗透率=r['装机渗透率'],年最大净负荷平均增长率=r['年最大净负荷平均增长率'],负荷分散系数=r['负荷分散系数']))
        group=nodes[np.isclose(nodes['年最大净负荷平均增长率'],r['年最大净负荷平均增长率'])&np.isclose(nodes['负荷分散系数'],r['负荷分散系数'])].sort_values('初始转供率')
        assert len(group)==9
        for j,label in enumerate(LABELS[3]):
            sub=group[group['初始转供率'].map(lambda x:sum(x>c+1e-9 for c in CUTS[3]))==j]
            lo,hi=sub['容载比'].min(),sub['容载比'].max()
            assert interval(lo,hi)==r[label]
            cells.append(dict(场景=i,转供档=j,下界=float(lo),上界=float(hi),展示区间=r[label],推荐带=bands[j],有效样本数=len(sub)))
            if window_mode:
                bands[j]=middle_node(sub['容载比'])
                cells[-1].update(原推荐带=cells[-1]['推荐带'],推荐带=bands[j],推荐窗口=bands[j],中位数=float(sub['容载比'].median()),代表节点容载比=middle_node(sub['容载比']))
        if window_mode:
            bands=adjoining_windows(bands)
            rows[-1][-4:]=bands
            for cell,band in zip(cells[-4:],bands):cell.update(推荐带=band,推荐窗口=band)
        t['current_transfer_sequence' if i==1 else 'current_transfer_sequence_second']=table(
            f'表5-0 场景{i}的完整转供率节点及设备方案',
            ['初始转供率','主变/MVA','容载比','储能/MWh','新增联络/条','费用现值/万元'],
            [[pct(x['初始转供率']),f(x['主变_MVA']),f(x['容载比']),f(x['储能_MWh']),int(x['新增联络_条']),f(x['费用现值_万元'])] for x in group.to_dict('records')])
    t['typical_transfer_matrix']=table('表5-0 典型源荷条件下随初始转供率变化的容载比推荐范围',
        ['装机渗透率','年最大净负荷平均增长率','负荷分散系数']+LABELS[3],rows,
        '两组均采用电缆长度占比50%和五站设备重新选配条件；按第5.6.2节的局部接续窗口方法归纳。' if window_mode else
        '两组均采用电缆长度占比50%和五站设备重新选配条件；按第5.6.2节的相邻档共用界值方法划定推荐带。')
    if window_mode:
        from matrix_planning_windows import assets as matrix_assets
        mt,ms,lookup_cells,lookup_index=matrix_assets(pd.read_csv(matrix_source()),table)
    else:
        from report_matrix_display import assets as matrix_assets
        mt,ms,lookup_cells,lookup_index=matrix_assets(d,table,interval)
    t.update(mt);s.update(ms)
    s['typical_matrix_summary']='在电缆长度占比50%的共同条件下，选取装机渗透率50%的两组典型源荷场景。每组包含10%～90%的九个初始转供率节点，按各档容量下界划定首尾相接的四档容载比推荐带，共形成8个区间单元。具体节点的设备配置与费用分别列示。\n'
    if window_mode:
        s['typical_matrix_summary']='在电缆长度占比50%的共同条件下，选取装机渗透率50%的两组典型源荷场景。每组包含10%～90%的九个初始转供率节点，按各档中位代表节点定位四个推荐窗口，共形成8个区间单元。具体节点的设备配置与费用分别列示。\n'
    seq=controlled_sequences(d)
    if window_mode:seq['diversity']=diversity_sequence()
    heads=['参数节点','主变/MVA','容载比','储能额定功率/MW','新增联络/条','费用现值/万元']
    def show_node(r,label):return [label,f(r['主变容量_MVA']),f(r['容载比']),f(r['储能额定功率_MW']),int(r['新增联络合计_条']),f(r['费用现值_万元'])]
    eta_rows=[]
    for r in seq['eta'].to_dict('records'):
        if r[FIELDS[0]]<1.5:continue
        eta_rows.append(show_node(r,'0～1.50' if r[FIELDS[0]]==1.5 else f(r[FIELDS[0]])))
    t['current_eta_sequence']=table('表5-0 装机渗透率对应的设备配置变化',heads,eta_rows,
        '0～1.50合并表示该范围内步长0.25的采样节点采用相同方案。')
    t['current_growth_sequence']=table('表5-0 年最大净负荷平均增长率对应的容量及工程变化',heads,
        [show_node(r,f'{100*r[FIELDS[1]]:g}%') for r in seq['growth'].to_dict('records')])
    cable=seq['cable'];cable_rows=[]
    # 仅费用变化的相邻节点合并，保留每次设备切换及其真实费用范围。
    for _, group in cable.groupby((cable[['主变容量_MVA','储能额定功率_MW','新增联络合计_条']]
                                   .ne(cable[['主变容量_MVA','储能额定功率_MW','新增联络合计_条']].shift()).any(axis=1)).cumsum(), sort=False):
        labels='、'.join(pct(v) for v in group[FIELDS[2]])
        prices=sorted(group['费用现值_万元'])
        cable_rows.append(show_node(group.iloc[0],labels)[:-1]+[f(prices[0]) if len(group)==1 else f(prices[0])+'～'+f(prices[-1])])
    t['current_cable_sequence']=table('表5-0 电缆长度占比对应的造价与设备切换',heads,
        cable_rows, '同列多个电缆占比表示配置相同，费用范围对应所列采样节点。')
    t['current_duration_sequence']=table('表5-0 固定主变及联络配置下的储能持续时间比较',
        ['储能支撑持续时间/h','储能额定功率/MW','储能额定能量/MWh','费用现值/万元'],
        [[int(r[FIELDS[4]]),f(r['储能额定功率_MW']),f(r['储能额定能量_MWh']),f(r['费用现值_万元'])]
         for r in seq['duration'].to_dict('records')])
    diversity=seq['diversity'];diversity_rows=[]
    values=diversity['主变容量_MVA'].round(7)
    for _,group in diversity.groupby(values.ne(values.shift()).cumsum(),sort=False):
        def span(field,integer=False):
            lo,hi=group[field].min(),group[field].max()
            fmt=(lambda v:str(int(v))) if integer else f
            return fmt(lo) if abs(hi-lo)<1e-8 else fmt(lo)+'～'+fmt(hi)
        labels='、'.join(f(v) for v in group[FIELDS[5]])
        if len(group)>2:labels=f(group[FIELDS[5]].iloc[0])+'—'+f(group[FIELDS[5]].iloc[-1])
        diversity_rows.append([labels,f(group.iloc[0]['主变容量_MVA']),f(group.iloc[0]['容载比']),
                               span('储能额定功率_MW'),span('新增联络合计_条',True),span('费用现值_万元')])
    t['current_diversity_sequence']=table('表5-0 负荷分散系数对应的容量平台及配套措施',heads,
        diversity_rows,'同一行合并主变容量相同的相邻采样节点；储能、联络和费用列为这些节点的取值范围。')
    t['new_template_assumptions']=table('表5-0 五站推广模板', ['项目','设置'],[
        ['区间矩阵设备','5站，每站保留2×50 MVA，允许更换63、80 MVA，并可扩建第三台50 MVA主变，初始总容量500 MVA'],
        ['典型转供对照设备','5站，每站两台在31.50、50、63、80 MVA中重新选配，基础最小总容量315 MVA'],
        ['基期网供峰值/目标时点','250 MW/基期后第4年'],
        ['负荷权重','0.10、0.15、0.20、0.25、0.30'],['光伏权重','0.08、0.14、0.18、0.25、0.35'],
        ['日间负荷系数/光伏出力系数','0.30/0.75'],
        ['既有网络','相邻站环网；按基期可实现转供率标定通道和馈线余量'],
        ['新增联络','单项3 km；有功上限8.00 MW，区段有效转供7.49 MW；允许独立接收馈线，备用间隔按站限制' if window_mode else '单项3 km、7.49 MW；允许独立接收馈线，备用间隔按站限制'],
        ['经济参数','第四章统一工程价格与评价期费用'],['容载比','由满足正常及N-1约束、按费用目标比选的可行设备方案计算']])
    return {k:display_text(v) for k,v in t.items()},{k:display_text(v) for k,v in s.items()},cells,index,d

def case_assets():
    if (ROOT/'研究报告/05_review/当前版/1017甲方批注与逐年案例更新/修前哈希.json').exists():
        from report_annual_update import assets as annual_assets
        return annual_assets()
    lock=read(LOCK);t={};s={};evidence=[];costrows=[];measures=[];costparts=[];decomp=[];mix=[]
    names={}
    for line in case.MAPPING.read_text().splitlines()[1:]:
        row=line.split()
        if len(row)>=3:names[row[-1]]=row[1]
    profile_count=0;loading=[];directions=[];rank=[]
    selected={};necessary=[]
    for region in ['pizhou','city']:
        entries=[r for r in lock['方案采用'] if r['地区代码']==region and r['起点代码']=='compressed']
        inp=read(ROOT/entries[0]['输入']['path'])
        cn=inp['region_name'];ids=list(inp['stations']);show=[sid for sid in ids if not sid.startswith('SIM-')]
        scenes=case.base.load_scenes(case.base.OUT/region,inp)
        show_indices=[ids.index(sid) for sid in show]
        initial_caps=np.array([sum(inp['stations'][sid]['initial_units']) for sid in ids])
        pplus=np.maximum(scenes[2025].max(axis=0),0);pminus=np.maximum(-scenes[2025].min(axis=0),0)
        rates=np.maximum(pplus,pminus)/(.95*initial_caps)
        for yr,power in scenes.items():
            values=np.max(np.abs(power),axis=0)[show_indices]/(.95*initial_caps[show_indices])
            loading.append([cn,yr,f'{np.median(values)*100:.0f}',f'{values.max()*100:.0f}'])
        directions.append([cn,len(show),sum(pplus[j]>=pminus[j] for j in show_indices),
            sum(pplus[j]<pminus[j] for j in show_indices),sum(rates[j]>1 for j in show_indices)])
        for j in sorted(show_indices,key=lambda j:-rates[j])[:8]:
            rank.append([cn,names[ids[j]],f(initial_caps[j]),f(pplus[j]),f(pminus[j]),pct(rates[j]),
                         '正向' if pplus[j]>=pminus[j] else '反向'])
        lp=OperatingLP(inp)
        hs=[next(i for i,r in enumerate(inp['station_snapshot_roles']) if role in r['roles'])
            for role in ['地区正向峰值','地区最低净负荷']]
        group={};yearrows=[];construction=[];transfer=[];paragraphs=[]
        for label,code in [('刚性','rigid'),('弹性','elastic_free')]:
            entry=next(x for x in entries if x['方案代码']==code);folder=ROOT/entry['结果目录']
            assert sha(folder/'summary.json')==entry['方案汇总']['sha256']
            summary=read(folder/'summary.json');group[label]={};selected[region,label]=summary
            costrows.append([cn,label,f(summary['cost_npv_10k'])])
            sums=[sum(y[k] for y in summary['annual']) for k in ['transformer_npv_10k','storage_npv_10k','line_npv_10k']]
            costparts.append([cn,label]+list(map(f,sums))+[f(sum(sums))])
            final=summary['annual'][-1]
            measures.append([cn,label,f(final['capacity_mva']),f(sum(y['purchased_transformer_mva'] for y in summary['annual'])),
                f(final['storage_nameplate_mw']),f(final['storage_mwh']),final['cumulative_lines']])
            prev_s,prev_p=inp['initial_capacity_mva'],inp['initial_peak_mw']
            for y in summary['annual']:
                yr=y['year'];units,n,built=case.assets_from_csv(inp,folder,yr)
                normal=[]
                for h in hs:
                    power=scenes[yr][h];prepared=lp.prepared(power,yr,units,n,built)
                    dispatch=lp.dispatch(power,prepared,-1);out=np.zeros(len(ids));inc=out.copy()
                    for arc,amount in dispatch['flow']:
                        *_,a,b=lp.arcs[arc];out[a]+=amount;inc[b]+=amount
                    net=power-out+inc;normal.append(dict(power=power,net=net,out=out,inc=inc))
                    transfer.append([label,yr,'区域正向峰值' if h==hs[0] else '区域最低净负荷',
                        int((out>1e-7).sum()),int((inc>1e-7).sum()),f(dispatch['total_mw']),
                        f(dispatch['existing_mw']),f(dispatch['new_mw']),f(out.max()),f(inc.max())])
                maxima=np.zeros(4)
                for power in scenes[yr]:
                    ready=lp.prepared(power,yr,units,n,built)
                    for failed in range(-1,len(ids)):
                        run=lp.dispatch(power,ready,failed)
                        j=0 if failed<0 else 2
                        maxima[j]=max(maxima[j],run['total_mw']);maxima[j+1]=max(maxima[j+1],run['existing_mw'])
                necessary.append(dict(地区=cn,方案=label,年份=yr,正常总量=maxima[0],正常既有=maxima[1],故障总量=maxima[2],故障既有=maxima[3]))
                group[label][yr]=dict(units=units,n=n,built=built,normal=normal)
                yearrows.append([label,yr,f(y['peak_mw']),f(y['capacity_mva']),f(y['clr']),f(y['storage_nameplate_mw']),y['cumulative_lines']])
                construction.append([label,yr,f(y['capacity_mva']-prev_s),f(y['purchased_transformer_mva']),
                    y['new_third_count'],f(y['new_storage_mwh']),y['new_lines'],f(y['added_lifecycle_npv_10k'])])
                capacity=(y['capacity_mva']-prev_s)/y['peak_mw'];load=prev_s*(1/y['peak_mw']-1/prev_p)
                decomp.append([cn,label,yr,f(capacity),f(load),f(capacity+load)])
                prev_s,prev_p=y['capacity_mva'],y['peak_mw']
            end=group[label][2025];idx=[ids.index(sid) for sid in show];units=end['units'][idx];n=end['n'][idx]
            third=int((units[:,2]>0).sum());storage=int((n>0).sum())
            mix.append([cn,label,len(show),len(show)-third,third,pct(third/len(show)),storage,f(n.sum()*.1)])
        for sid in show:
            j=ids.index(sid);name=names[sid];initial=inp['stations'][sid]['initial_units'];rows=[]
            for label in ['刚性','弹性']:
                for yr in inp['years']:
                    z=group[label][yr];normal=z['normal'][0]
                    combo='+'.join(f'{u:g}' for u in z['units'][j] if u>0)
                    rows.append([label,yr,combo,f(z['units'][j].sum()),f(z['n'][j]*.1),
                        f(normal['out'][j]),f(normal['inc'][j]),f(normal['net'][j])])
            key=f'restore_{region}_{sid}_profile'
            t[key]=table(f'表5-0 {name}年度配置与正向峰值正常转接',
                ['方案','年份','主变组合/MVA','总容量/MVA','储能额定功率/MW','转出/MW','承接/MW','转接后净负荷/MW'],rows)
            z=group['弹性'][2025];rigid=group['刚性'][2025];capacity=z['units'][j].sum();rcap=rigid['units'][j].sum()
            actions=[];previous=np.r_[initial,0.]
            for yr in inp['years']:
                u=group['弹性'][yr]['units'][j]
                changed=[f'{previous[k]:g} MVA更换为{u[k]:g} MVA' for k in (0,1) if u[k]>previous[k]+1e-7]
                if u[2]>previous[2]+1e-7:changed.append(f'扩建第三台{u[2]:g} MVA主变')
                if changed:actions.append(str(yr)+'年'+ '，'.join(changed))
                previous=u
            action='，随后'.join(actions)+'。' if actions else '四年均保留该组合。'
            bp=min(.1,.215*.76/max(1,inp['stations'][sid]['forward_duration_h']))*z['n'][j]
            bn=min(.1,.215*.76/max(1,inp['stations'][sid]['reverse_duration_h']))*z['n'][j]
            remain=.95*(capacity-z['units'][j].max());faults=[];margins=[]
            for h in hs:
                power=scenes[2025][h];prepared=lp.prepared(power,2025,z['units'],z['n'],z['built'])
                dispatch=lp.dispatch(power,prepared,j);net=power.copy()
                for arc,amount in dispatch['flow']:
                    *_,a,b=lp.arcs[arc];net[a]-=amount;net[b]+=amount
                faults.append(float(net[j]));margins.append(min(remain+bp-net[j],remain+bn+net[j]))
            normal=z['normal'];peak=max(abs(scenes[2025][:,j]));rate=peak/(.95*capacity)
            storage_actions=[];previous_n=0
            for yr in inp['years']:
                new_n=group['弹性'][yr]['n'][j]
                if new_n>previous_n+.5:storage_actions.append(f'{yr}年新增{f((new_n-previous_n)*.1)} MW储能')
                previous_n=new_n
            storage_text=('，并于'+ '，随后'.join(storage_actions)+'。') if storage_actions else '，供电任务由主变及网络承担。'
            critical_year,critical_h=max(((yr,h) for yr in inp['years'] for h in range(len(scenes[yr]))),
                key=lambda pair:abs(scenes[pair[0]][pair[1],j]))
            critical=group['弹性'][critical_year];power=scenes[critical_year][critical_h]
            prepared=lp.prepared(power,critical_year,critical['units'],critical['n'],critical['built'])
            fault=lp.dispatch(power,prepared,j);critical_out=critical_in=0.;routes=[]
            for arc,amount in fault['flow']:
                *_,a,b=lp.arcs[arc]
                if a==j:critical_out+=amount;routes.append(('转出',names.get(ids[b],ids[b]),amount))
                if b==j:critical_in+=amount;routes.append(('承接',names.get(ids[a],ids[a]),amount))
            critical_net=power[j]-critical_out+critical_in
            critical_remain=critical['units'][j].sum()-critical['units'][j].max()
            main_route=max(routes,key=lambda x:x[2]) if routes else None
            annual_analysis=(f'四年校核截面中，本站绝对功率最大的工况出现在{critical_year}年，'
                f'转接前为{f(power[j])} MW，主要表现为'+('正向受电需求，' if power[j]>=0 else '反向输送需求，')+
                f'该年设备在最大单台主变N-1后剩余容量为{f(critical_remain)} MVA。')
            if main_route:
                annual_analysis+=(f'故障方式下本站转出{f(critical_out)} MW、承接{f(critical_in)} MW，'
                    f'其中与{main_route[1]}之间的主要{main_route[0]}功率为{f(main_route[2])} MW，'
                    f'转接后净负荷为{f(critical_net)} MW。')
                annual_analysis+=('这一工况通过邻站分担本站故障后的正向负荷。' if power[j]>0 and critical_out>critical_in else
                    '在反向工况承接可切换用电负荷，可减少本站需经主变反送的功率。' if power[j]<0 and critical_in>critical_out else
                    '该工况的站间任务随局部功率方向和接收余量安排。')
            else:
                critical_bp=min(.1,.215*.76/max(1,inp['stations'][sid]['forward_duration_h']))*critical['n'][j]
                critical_bn=min(.1,.215*.76/max(1,inp['stations'][sid]['reverse_duration_h']))*critical['n'][j]
                if critical['n'][j]>.5:
                    support=critical_bp if power[j]>=0 else critical_bn
                    annual_analysis+=f'该工况本站未发生站间转接，储能相应方向有效支撑{f(support)} MW，与剩余主变共同满足承载要求。'
                else:annual_analysis+='该工况本站由剩余主变满足承载要求。'
            difference=(f'弹性方案本站增加{f(capacity-rcap)} MVA容量。' if capacity>rcap+1e-7 else
                        f'弹性方案本站容量减少{f(rcap-capacity)} MVA。' if capacity<rcap-1e-7 else
                        '两类方案本站主变总容量相同。')
            para=(f'#### {name}规划分析\n\n该站初始主变组合为'+ '+'.join(f'{u:g}' for u in initial)+' MVA，弹性方案'+action.rstrip('。')+storage_text+'\n\n'+
                f'2025年本站最大正向、反向净负荷分别为{f(pplus[j])} MW、{f(pminus[j])} MW。'+
                f'在同一需求下，刚性方案当年主变容量为{f(rcap)} MVA、储能额定功率{f(rigid["n"][j]*.1)} MW，'
                f'弹性方案分别为{f(capacity)} MVA和{f(z["n"][j]*.1)} MW，'+difference.rstrip('。')+'。'+
                f'弹性方案按当年各站局部极值计算的站级负载率为{pct(rate)}。\n\n[[TABLE:{key}]]\n\n'
                f'2025年区域正向峰值正常工况下，本站转出{f(normal[0]["out"][j])} MW、承接{f(normal[0]["inc"][j])} MW，'
                f'转接后净负荷为{f(normal[0]["net"][j])} MW，区域最低净负荷工况下为{f(normal[1]["net"][j])} MW。\n\n'
                f'按最大单台主变N-1校核，本站剩余容量为{f(capacity-z["units"][j].max())} MVA，'
                f'两代表工况重新转供后的本站净负荷分别为{f(faults[0])} MW、{f(faults[1])} MW，'
                f'两方向最小容量余量为{f(max(0,min(margins)))} MW，正向储能有效支撑功率为{f(bp)} MW。\n\n'+annual_analysis+'\n')
            paragraphs.append(para);profile_count+=1
            evidence.append(dict(地区=cn,站名=name,station=sid,正常净负荷=[float(x['net'][j]) for x in normal],
                故障净负荷=faults,最小余量_MW=min(margins),储能正向有效功率_MW=bp,局部极值负载率=rate,
                四年最大绝对功率工况=dict(年份=critical_year,截面=critical_h,转接前_MW=float(power[j]),
                    转出_MW=critical_out,承接_MW=critical_in,转接后_MW=critical_net,剩余容量_MVA=critical_remain,主要通道=main_route)))
        s[f'restore_{region}_profiles']='\n'.join(paragraphs)
        t[f'new_{region}_years']=table(f'表5-0 {cn}逐年容量及措施',
            ['方案','年份','年网供最大负荷/MW','主变容量/MVA','容载比','储能额定功率/MW','累计新线/条'],yearrows)
        t[f'restore_{region}_construction']=table(f'表5-0 {cn}逐年新增工程与费用',
            ['方案','年份','主变净增容量/MVA','主变新购容量/MVA','扩建主变/台','新增储能额定能量/MWh','新增联络/条','当年措施现值/万元'],construction)
        t[f'restore_{region}_transfer']=table(f'表5-0 {cn}正常方式下的分工况转接任务',
            ['方案','年份','工况','转出站数','承接站数','转接合计/MW','既有联络/MW','新增联络/MW','单站最大转出/MW','单站最大承接/MW'],transfer)
        final=selected[region,'弹性']['annual'][-1]
        first=selected[region,'弹性']['annual'][0]
        s[f'new_{region}_results']=(f'{cn}弹性方案2022年完成{f(first["capacity_mva"]-inp["initial_capacity_mva"])} MVA净增容量，'
            f'主变总容量达到{f(first["capacity_mva"])} MVA，2025年为{f(final["capacity_mva"])} MVA。'
            f'各年储能和联络工程按当年供电需求安排，具体在役规模及新增建设分别列于下表。\n')
        s[f'restore_{region}_transfer']=''
    assert profile_count==46
    t['new_cost_comparison']=table('表5-0 两地区方案费用比较',['地区','方案','评价期费用现值/万元'],costrows)
    t['new_annual_loading']=table('表3-0 两地区站级负载率',['地区','年份','中位数/%','最大值/%'],loading)
    t['restore_direction']=table('表3-0 站级展示范围内的功率方向及相对压力',
        ['地区','站数','正向幅值较大站数','反向幅值较大站数','站级负载率超过100%的站数'],directions)
    t['restore_station_loading_rank']=table('表3-0 2025年站级负载率较高的站',
        ['地区','变电站','初始公用主变总容量/MVA','最大正向净负荷/MW','最大反向净负荷/MW','站级负载率','主导方向'],rank)
    t['new_case_measures']=table('表5-0 2025年在役措施及累计建设规模',
        ['地区','方案','在役主变/MVA','累计新购主变/MVA','储能功率/MW','储能能量/MWh','新增联络/条'],measures)
    t['restore_cost_components']=table('表5-0 主变、储能及联络费用现值',['地区','方案','主变/万元','储能/万元','联络/万元','合计/万元'],costparts)
    t['restore_clr_decomposition']=table('表5-0 规划容载比年度变化分解',
        ['地区','方案','年份','容量变化贡献','负荷变化贡献','容载比净变化'],decomp)
    t['restore_equipment_mix']=table('表5-0 2025年站级展示范围内主变台数与配储站数',
        ['地区','方案','站数','两台主变站数','三台主变站数','三台主变站占比','配储站数','储能额定功率/MW'],mix)
    rigid=sum(selected[r,'刚性']['cost_npv_10k'] for r in ['pizhou','city'])
    elastic=sum(selected[r,'弹性']['cost_npv_10k'] for r in ['pizhou','city'])
    s['new_case_comparison']=f'两地区刚性可行方案费用现值合计{f(rigid)}万元，弹性为{f(elastic)}万元，减少{f(rigid-elastic)}万元，降幅约{pct(1-elastic/rigid)}。'
    def components(region,label):
        return np.array([sum(y[k] for y in selected[region,label]['annual'])
            for k in ['transformer_npv_10k','storage_npv_10k','line_npv_10k']])
    p_diff=components('pizhou','弹性')-components('pizhou','刚性')
    c_diff=components('city','弹性')-components('city','刚性')
    s['restore_cost_components']=(f'邳州弹性方案主变费用现值增加{f(p_diff[0])}万元，'
        f'储能和联络分别减少{f(-p_diff[1])}万元、{f(-p_diff[2])}万元，'
        f'合计减少{f(-p_diff.sum())}万元。首年较充分的主变补强降低了后续配储需求，'
        '储能费用减少是该地区费用差的主要来源。2024年弹性方案进一步补强八义集，主变总容量较刚性多11.50 MVA，站内容量分配与配套措施的时序共同形成费用差。\n\n'
        f'市区弹性方案以{f(c_diff[0])}万元主变费用现值替代刚性方案'
        f'{f(-c_diff[2])}万元联络费用，合计减少{f(-c_diff.sum())}万元。'
        '既有转供在两类方案中均提供支援，费用优势来自新增补强方式的不同。'
        '两地区合计降幅由上述分项变化形成，区域容量变化与费用变化分别按设备及工程项目解释。')
    s['restore_equipment_mix']=('2025年邳州两类方案均有1座三台主变站，但配储站数及储能规模不同。'
        '市区两类方案均保持两台主变的站内结构，弹性方案通过翟山变单台升档提高故障后剩余容量。'
        '主变台数只反映设备结构的一部分，同样为两台主变的站，额定规格和最大单台停运后的可用容量仍有差异。'
        '各年的具体组合、支援方向和投运变化需结合逐站表确定。')
    t['new_case_assumptions']=table('表5-0 两地区共同计算条件',['参数','设置','依据'],[
        ['年度负荷','2022—2025年逐年统计','同范围110 kV年度记录'],
        ['静态截面','邳州26个、市区45个','地区和各站局部极值同期截面'],
        ['正向储能支撑持续时间','邳州2.00 h、市区6.00 h','地区95%峰值持续时间'],
        ['储能规格','100.00 kW/215.00 kWh','采购资料'],
        ['可用电量系数','0.76','SOC可用窗口与放电效率的研究取值[122]'],
        ['新购主变规格','31.50、50、63、80 MVA','按站限制'],
        ['第三台主变','有预留条件时50 MVA','按站限制'],
        ['既有转供能力','逐站MW上限与网络能力共同限制','全停全转统计及馈线资料'],
        ['新增联络费用','邳州128.38、市区452.40万元/项','地区电缆长度占比'],
        ['供电安全及功率因数','正常及最大单台主变N-1；0.95','逐工况校核']])
    t['new_case_assumptions']=t['new_case_assumptions'].rstrip()+'\n'+''.join([
        '| 反向承载 | 正常及健康站80%，故障站按剩余主变能力 | 导则反向限值与N-1静态校核 |\n',
        '| 主变采购组织 | 四年内同一位置最多更换一次 | 两类方案共同的工程实施假设 |\n',
        '| 弹性工程优选 | 经济参考费用5%以内优先简化联络 | 本研究费用容差 |\n'])
    t['line_cost_components']=table('表4-0 电缆长度占比与项目费用',
        ['电缆长度占比','长度/km','单位长度费用/万元·km⁻¹','固定接入费/万元','项目投资/万元'],
        [[pct(q),'3.00',f(24*(1-q)+180*q),'6.00',f(3*(24*(1-q)+180*q)+6)] for q in [.1,.3,.5,.8,.9]])
    amounts=pd.DataFrame(necessary)
    t['current_necessary_transfers']=table('表5-0 全部静态工况中的最大必要转供功率',
        ['地区','方案','年份','正常总量/MW','正常既有联络/MW','N-1总量/MW','N-1既有联络/MW'],
        [[r['地区'],r['方案'],r['年份'],f(r['正常总量']),f(r['正常既有']),f(r['故障总量']),f(r['故障既有'])] for r in necessary],
        '固定设备后逐工况最小化通道转供功率，分别取正常及N-1工况最大值；总量与既有边列分别取最大值。')
    annual=pd.read_csv(CASE/'逐年方案.csv');fees=pd.read_csv(CASE/'费用及精度.csv');rows=[]
    for entry in lock['方案采用']:
        if entry['起点代码']!='annual_2021':continue
        sub=annual[(annual['地区']==entry['地区'])&(annual['起点']=='保留2021原表容量')&(annual['方案']==entry['方案'])].query('年份>2021').sort_values('年份')
        for r in sub.to_dict('records'):
            rows.append([entry['地区'],'刚性' if entry['方案代码']=='rigid' else '弹性',int(r['年份']),f(r['年末主变_MVA']),f(r['容载比']),f(r['年末储能_MWh']),int(r['累计新增联络_条'])])
    t['uncompressed_annual_summary']=table('表5-0 保留2021原表容量的逐年规划汇总',
        ['地区','方案','年份','年末主变/MVA','容载比','年末储能/MWh','累计新联络/条'],rows)
    sub=fees[fees['起点']=='保留2021原表容量']
    t['uncompressed_cost_summary']=table('表5-0 保留2021原表容量的方案费用',
        ['地区','方案','评价期费用现值/万元'],[[r['地区'],'刚性' if r['方案']=='刚性方案' else '弹性',f(r['费用现值_万元'])] for r in sub.to_dict('records')])
    from report_storage_display import storage_duration_table
    t['storage_duration_cost'] = storage_duration_table()
    t['economic_assumptions'] = economic_assumptions_table()
    return {k:display_text(v) for k,v in t.items()},{k:display_text(v) for k,v in s.items()},evidence

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true');args=ap.parse_args()
    pt,ps,cells,index,data=parameter_assets();ct,cs,evidence=case_assets()
    policy=read(ROOT/'tools/report_policy.json')
    window_mode=policy['matrix_display'].get('output_kind')=='adaptive_sliding_windows'
    target_review=ROOT/policy['plain_delivery_review'] if window_mode else REVIEW
    tables=read(A/'计算表.json');sections=read(A/'生成段落.json')
    newt=pt|ct;news=ps|cs
    if args.check:
        for k,v in newt.items(): assert tables[k]==v,'计算表.json:'+k
        for k,v in news.items(): assert sections[k]==v,'生成段落.json:'+k
    else:
        tables.update(newt);sections.update(news)
        tables={k:display_text(v) for k,v in tables.items()};sections={k:display_text(v) for k,v in sections.items()}
        for path,value in [(A/'计算表.json',tables),(A/'生成段落.json',sections),
            (target_review/('推荐窗口展示矩阵.json' if window_mode else '定值展示矩阵.json'),dict(说明='典型转供18节点8单元；完整查表由11点扩展库归纳六表288单元' if window_mode else '典型转供对照18节点8单元；区间查表另由锁定参数库归纳9表432单元',索引=index,单元=cells)),
            (target_review/'逐站展示复算.json',evidence)]:
            path.write_text(json.dumps(value,ensure_ascii=False,indent=2,default=lambda x:x.item())+'\n')
        sequences=controlled_sequences(data)
        if window_mode:sequences['diversity']=diversity_sequence()
        (target_review/'六参数受控完整序列.json').write_text(json.dumps(
            {k:v.to_dict('records') for k,v in sequences.items()},ensure_ascii=False,indent=2)+'\n')
    print('报告资产核验通过：十三项指标筛选五参数、典型转供18节点8单元、46座站')

if __name__=='__main__':main()
