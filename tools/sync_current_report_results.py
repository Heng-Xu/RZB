"""从已确认案例和参数库更新报告资产；不求解、不改锁定库或经济参数。"""
from pathlib import Path
import argparse, hashlib, json, math, sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from 实验.研究.rebuild_2026.case_parameters_20261012 import transfer_diagnostic as case

REPORT = ROOT/'研究报告'
A = REPORT/'02图表/当前版'
REVIEW = REPORT/'05_review/当前版/1013正文与矩阵修订'
PUBLIC = REPORT/'01研究推荐/当前版/参数联合情景_20261012'
CASE = REPORT/'01研究推荐/当前版/既有转供约束诊断_20261012'
LOCK = REPORT/'05_review/当前版/1012既有转供约束诊断/报告采用版本锁定清单.json'
FIELDS = ['分布式电源装机渗透率','年最大净负荷平均增长率','电缆长度占比',
          '初始转供率','储能支撑持续时间_h','负荷分散系数']
SHORT = ['装机渗透率','平均增长率','电缆长度占比','初始转供率','支撑持续时间','负荷分散系数']
SYMBOL = ['ηC','ḡ','α','r₀','H','KD']
CUTS = [[1,2],[.02,.04,.07],[.1,.3],[.3,.5,.7]]
LABELS = [['≤1','(1,2]','>2'],['≤2%','(2%,4%]','(4%,7%]','>7%'],
          ['≤10%','(10%,30%]','>30%'],['≤30%','(30%,50%]','(50%,70%]','>70%']]

def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def f(x): return f'{0.0 if abs(float(x))<.005 else float(x):.2f}'
def pct(x): return f'{float(x)*100:.0f}%'
def table(title, headers, rows, note=''):
    result=title+'\n\n| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'
    result+=''.join('| '+' | '.join(map(str,row))+' |\n' for row in rows)
    return result+('\n注：'+note+'\n' if note else '')
def interval(lo,hi):
    return f'{math.floor((lo+1e-10)*100)/100:.2f}～{math.ceil((hi-1e-10)*100)/100:.2f}'

def controlled_sequences(d):
    controls={
        'eta':(0,[1.5,.04,.1,.4,4,1.1]),
        'growth':(1,[1.5,.04,.1,.4,4,1.1]),
        'cable':(2,[2.5,.04,.1,.7,4,1.1]),
        'transfer':(3,[1.5,.04,.1,.4,4,1.1]),
        'duration':(4,[2.5,.04,.1,.4,4,1.1]),
        'diversity':(5,[0,.04,.1,.4,4,1.1])}
    results={}
    for name,(index,base) in controls.items():
        mask=np.ones(len(d),dtype=bool)
        for i,field in enumerate(FIELDS):
            if i!=index:mask&=np.isclose(d[field],base[i],atol=1e-10,rtol=0)
        results[name]=d.loc[mask].sort_values(FIELDS[index])
    return results

def parameter_assets():
    d=pd.read_csv(PUBLIC/'统一有效样本.csv')
    corr=pd.read_csv(PUBLIC/'固定其余五项后的组内相关.csv')
    t={};s={}
    t['current_controlled_correlations']=table('表3-0 六项参数与容载比的组内相关',
        ['参数','有效组数','有效节点数','Pearson','容量响应组占比'],
        [[r['参数'],r['有效受控组数'],r['有效节点数'],f(r['组内Pearson']),pct(r['主变容量响应组占比'])]
         for r in corr.to_dict('records')])
    # 与锁定六参数输入相关表逐项复算，保留全部六项。
    cm=d[FIELDS].corr();saved=pd.read_csv(PUBLIC/'六参数输入相关.csv',index_col=0)
    np.testing.assert_allclose(cm,saved,atol=1e-12)
    t['current_input_correlations']=table('表3-0 六项输入参数的Pearson相关矩阵',
        ['参数']+SYMBOL, [[SHORT[i]]+[f(v) for v in cm.iloc[i]] for i in range(6)])
    nodes=[['分布式电源装机渗透率','0～3.00，步长0.25','≤1；(1,2]；>2'],
        ['年最大净负荷平均增长率','0、2%、3%、4%、5.5%、7%、8%、10%','≤2%；(2%,4%]；(4%,7%]；>7%'],
        ['电缆长度占比','10%、30%、50%、80%、90%','≤10%；(10%,30%]；>30%'],
        ['初始转供率','10%～90%，步长10%','≤30%；(30%,50%]；(50%,70%]；>70%'],
        ['储能支撑持续时间','2、4、6 h','2 h；4 h；6 h'],
        ['负荷分散系数','1.00、1.10、1.15','1.00；1.10；1.15']]
    t['new_parameter_bins']=table('表3-0 六项参数采样节点与矩阵分类',['参数','采样节点','矩阵分类'],nodes)
    # 展示层将分散系数的三个定值分别列示；不改锁定18表及原始节点。
    b=d.copy()
    for i,(field,cuts) in enumerate(zip(FIELDS[:4],CUTS)):
        b['b'+str(i)]=b[field].map(lambda x,cuts=cuts:sum(x>c+1e-9 for c in cuts))
    cells=[];matrix_sections=[];index=[]
    for (q,h,kd),g in b.groupby(['b2',FIELDS[4],FIELDS[5]],sort=True):
        key=f'current_matrix_{q}_{int(h)}_{kd:.2f}'
        title=f'电缆长度占比{LABELS[2][q]}，储能支撑{int(h)} h，负荷分散系数{kd:.2f}'
        rows=[]
        for (growth,eta),row in g.groupby(['b1','b0'],sort=True):
            values=[]
            for r in range(4):
                sub=row[row.b3.eq(r)]
                assert len(sub)>=2,(q,h,kd,growth,eta,r)
                lo,hi=sub['容载比'].min(),sub['容载比'].max()
                values.append(interval(lo,hi))
                cells.append(dict(电缆档=int(q),支撑时间_h=int(h),负荷分散系数=kd,
                    增长档=int(growth),渗透率档=int(eta),转供档=r,有效样本数=len(sub),
                    下界=lo,上界=hi,展示区间=values[-1],
                    下界参数=list(sub.loc[sub['容载比'].idxmin(),FIELDS]),
                    上界参数=list(sub.loc[sub['容载比'].idxmax(),FIELDS])))
            rows.append([LABELS[1][growth],LABELS[0][eta]]+values)
        t[key]=table('表5-0 '+title,['平均增长率','装机渗透率']+LABELS[3],rows)
        matrix_sections.append('[[TABLE:'+key+']]')
        index.append(dict(key=key,title=title))
    assert len(index)==27 and len(cells)==1296
    assert sum(c['有效样本数'] for c in cells)==32112
    s['new_matrix_tables']='\n\n'.join(matrix_sections)+'\n'
    s['new_matrix_summary']=(f'六项参数共设置34686个组合，其中32112个有效组合形成容载比区间。'
        f'按电缆长度占比三档、储能支撑持续时间三个定值和负荷分散系数三个定值分为27张表，'
        f'每表以平均增长率和装机渗透率构成12行、初始转供率构成4列，共1296个单元。'
        f'每个单元包含2～60个有效样本，容载比区间总体为{interval(d["容载比"].min(),d["容载比"].max())}。\n')
    # 给出同一组背景下的完整转供序列，表后按设备切换解释。
    sample=d[np.isclose(d[FIELDS[0]],1.5)&np.isclose(d[FIELDS[1]],.04)&
             np.isclose(d[FIELDS[2]],.1)&np.isclose(d[FIELDS[4]],4)&np.isclose(d[FIELDS[5]],1.1)].sort_values(FIELDS[3])
    assert len(sample)==9
    sample_rows=[]
    for r in sample.to_dict('records'):
        values=[f(r['主变容量_MVA']),f(r['容载比']),f(r['储能额定功率_MW']),
                int(r['新增联络合计_条']),f(r['费用现值_万元'])]
        if sample_rows and sample_rows[-1][1:]==values:
            sample_rows[-1][0]+='、'+pct(r[FIELDS[3]])
        else:sample_rows.append([pct(r[FIELDS[3]])]+values)
    t['current_transfer_sequence']=table('表5-0 固定源荷和线路条件下的转供率比较',
        ['初始转供率','主变/MVA','容载比','储能/MW','新增联络/条','费用现值/万元'],sample_rows)
    seq=controlled_sequences(d)
    heads=['参数节点','主变/MVA','容载比','储能额定功率/MW','新增联络/条','费用现值/万元']
    def show_node(r,label):return [label,f(r['主变容量_MVA']),f(r['容载比']),f(r['储能额定功率_MW']),int(r['新增联络合计_条']),f(r['费用现值_万元'])]
    eta_rows=[]
    for r in seq['eta'].to_dict('records'):
        if r[FIELDS[0]]<1.5:continue
        eta_rows.append(show_node(r,'0～1.50' if r[FIELDS[0]]==1.5 else f(r[FIELDS[0]])))
    t['current_eta_sequence']=table('表5-0 装机渗透率对应的设备配置变化',heads,eta_rows,
        '0～1.50合并表示该范围内步长0.25的采样节点采用相同方案。')
    t['current_growth_sequence']=table('表5-0 平均增长率对应的容量及工程变化',heads,
        [show_node(r,f'{100*r[FIELDS[1]]:g}%') for r in seq['growth'].to_dict('records')])
    cable=seq['cable'];fixed=cable[cable[FIELDS[2]]<.9];r=cable[cable[FIELDS[2]].eq(.9)].iloc[0]
    t['current_cable_sequence']=table('表5-0 电缆长度占比对应的造价与设备切换',heads,
        [show_node(fixed.iloc[0],'10%、30%、50%、80%')[:-1]+[f(fixed['费用现值_万元'].min())+'～'+f(fixed['费用现值_万元'].max())],
         show_node(r,'90%')], '首行四个节点配置相同，费用范围对应四个已计算节点。')
    t['current_duration_sequence']=table('表5-0 固定主变及联络配置下的储能持续时间比较',
        ['储能支撑持续时间/h','储能额定功率/MW','储能额定能量/MWh','费用现值/万元'],
        [[int(r[FIELDS[4]]),f(r['储能额定功率_MW']),f(r['储能额定能量_MWh']),f(r['费用现值_万元'])]
         for r in seq['duration'].to_dict('records')])
    t['current_diversity_sequence']=table('表5-0 局部峰值分散程度对应的设备配置',heads,
        [show_node(r,f(r[FIELDS[5]])) for r in seq['diversity'].to_dict('records')])
    t['new_template_assumptions']=table('表5-0 五站推广模板', ['项目','设置'],[
        ['初始设备','5站，每站2×50 MVA；按位置允许升档和扩建第三台50 MVA'],
        ['基期网供峰值/目标时点','250 MW/基期后第4年'],
        ['负荷权重','0.10、0.15、0.20、0.25、0.30'],['光伏权重','0.08、0.14、0.18、0.25、0.35'],
        ['日间负荷系数/光伏出力系数','0.30/0.75'],
        ['既有网络','相邻站环网；按基期可实现转供率标定通道和馈线余量'],
        ['新增联络','单项3 km、7.49 MW；允许独立接收馈线，备用间隔按站限制'],
        ['经济参数','第四章统一工程价格与评价期费用'],['容载比','由满足正常及N-1约束、按费用目标比选的可行设备方案计算']])
    return t,s,cells,index,d

def case_assets():
    lock=read(LOCK);t={};s={};evidence=[];costrows=[];measures=[];costparts=[];decomp=[];mix=[]
    names={}
    for line in case.MAPPING.read_text().splitlines()[1:]:
        row=line.split()
        if len(row)>=3:names[row[-1]]=row[1]
    profile_count=0;loading=[];directions=[];rank=[]
    selected={}
    for region in ['pizhou','city']:
        entries=[r for r in lock['main'] if r['region']==region]
        inp=read((case.OUT/entries[0]['result_folder']).parent/'inputs.json')
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
        lp=case.DiagnosticLP(inp)
        hs=[next(i for i,r in enumerate(inp['station_snapshot_roles']) if role in r['roles'])
            for role in ['地区正向峰值','地区最低净负荷']]
        group={};yearrows=[];construction=[];transfer=[];paragraphs=[]
        for label,code in [('刚性','rigid_storage'),('弹性','elastic_no_floor')]:
            entry=next(x for x in entries if x['case']==code);folder=case.OUT/entry['result_folder']
            assert sha(folder/'chosen_solution.npz')==entry['solution_sha256']
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
                group[label][yr]=dict(units=units,n=n,built=built,normal=normal)
                yearrows.append([label,yr,f(y['peak_mw']),f(y['capacity_mva']),f(y['clr']),f(y['storage_nameplate_mw']),y['cumulative_lines']])
                construction.append([label,yr,f(y['net_capacity_increment_mva']),f(y['purchased_transformer_mva']),
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
            action='；'.join(actions)+'。' if actions else '四年保留初始主变组合。'
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
            storage_text='；'.join(storage_actions)+'。' if storage_actions else '弹性方案四年均由主变及网络承担供电任务。'
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
                f'转接前为{f(power[j])} MW，主要表现为'+('正向受电需求。' if power[j]>=0 else '反向输送需求。')+
                f'按该年设备扣除最大单台主变后，剩余容量{f(critical_remain)} MVA。')
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
            para=(f'#### {name}规划分析\n\n该站初始主变组合为'+ '+'.join(f'{u:g}' for u in initial)+' MVA。'+action+storage_text+'\n\n'+
                f'2025年本站最大正向、反向净负荷分别为{f(pplus[j])} MW、{f(pminus[j])} MW。'+
                f'刚性方案当年主变容量为{f(rcap)} MVA、储能额定功率{f(rigid["n"][j]*.1)} MW；'
                f'弹性方案分别为{f(capacity)} MVA和{f(z["n"][j]*.1)} MW。'+difference+
                f'弹性方案按当年各站局部极值计算的站级负载率为{pct(rate)}。\n\n[[TABLE:{key}]]\n\n'
                f'2025年区域正向峰值正常工况下，本站转出{f(normal[0]["out"][j])} MW、承接{f(normal[0]["inc"][j])} MW，'
                f'转接后净负荷为{f(normal[0]["net"][j])} MW；区域最低净负荷工况下为{f(normal[1]["net"][j])} MW。\n\n'
                f'本站最大单台主变停运后剩余容量为{f(capacity-z["units"][j].max())} MVA。'
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
            ['方案','年份','工况','转出站数','承接站数','转接合计/MW','既有边/MW','新增边/MW','单站最大转出/MW','单站最大承接/MW'],transfer)
        final=selected[region,'弹性']['annual'][-1]
        first=selected[region,'弹性']['annual'][0]
        s[f'new_{region}_results']=(f'{cn}弹性方案2022年完成{f(first["net_capacity_increment_mva"])} MVA净增容量，'
            f'主变总容量达到{f(first["capacity_mva"])} MVA，之后三年保持该容量。'
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
        '储能费用减少是该地区费用差的主要来源。两类方案2024年起总容量相同，但主变采购及配套措施的时序不同。\n\n'
        f'市区弹性方案以{f(c_diff[0])}万元主变费用现值替代刚性方案'
        f'{f(-c_diff[2])}万元联络费用，合计减少{f(-c_diff.sum())}万元。'
        '既有转供在两类方案中均提供支援，费用优势来自新增补强方式的不同。'
        '两地区合计降幅由上述分项变化形成，区域容量变化与费用变化分别按设备及工程项目解释。')
    s['restore_equipment_mix']=('2025年邳州两类方案均有1座三台主变站，但配储站数及储能规模不同；'
        '市区两类方案均保持两台主变的站内结构，弹性方案通过翟山变单台升档提高故障后剩余容量。'
        '主变台数只反映设备结构的一部分，同样为两台主变的站，额定规格和最大单台停运后的可用容量仍有差异。'
        '各年的具体组合、支援方向和投运变化需结合逐站表确定。')
    t['new_case_assumptions']=table('表5-0 两地区共同计算条件',['参数','设置','依据'],[
        ['年度负荷','2022—2025年逐年统计','同范围110 kV年度记录'],
        ['静态截面','邳州26个、市区45个','地区和各站局部极值同期截面'],
        ['正向储能支撑持续时间','邳州2 h、市区6 h','地区95%峰值持续时间'],
        ['储能规格及可用电量系数','100 kW/215 kWh；0.76','采购资料及静态折算'],
        ['新购主变规格','31.50、50、63、80 MVA','按站限制'],
        ['第三台主变','有预留条件时50 MVA','按站限制'],
        ['既有转供能力','逐站MW上限与网络能力共同限制','全停全转统计及馈线资料'],
        ['新增联络费用','邳州128.38、市区452.40万元/项','地区电缆长度占比'],
        ['供电安全及功率因数','正常及最大单台主变N-1；0.95','逐工况校核']])
    t['line_cost_components']=table('表4-0 电缆长度占比与项目费用',
        ['电缆长度占比','长度/km','单位长度费用/万元·km⁻¹','固定接入费/万元','项目投资/万元'],
        [[pct(q),'3.00',f(24*(1-q)+180*q),'6.00',f(3*(24*(1-q)+180*q)+6)] for q in [.1,.3,.5,.8,.9]])
    amounts=pd.read_csv(CASE/'报告主方案转供量.csv')
    t['current_necessary_transfers']=table('表5-0 逐年最大必要既有转供功率',
        ['地区','方案','年份','正常最大/MW','N-1最大/MW'],
        [[r['地区'], '弹性' if r['方案']=='弹性无下限' else r['方案'],r['年份'],
          f(r['正常最大既有转供_MW']),f(r['N1最大既有转供_MW'])] for r in amounts.to_dict('records')])
    return t,s,evidence

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true');args=ap.parse_args()
    pt,ps,cells,index,data=parameter_assets();ct,cs,evidence=case_assets()
    tables=read(A/'计算表.json');sections=read(A/'生成段落.json')
    newt=pt|ct;news=ps|cs
    if args.check:
        for k,v in newt.items(): assert tables[k]==v,'计算表.json:'+k
        for k,v in news.items(): assert sections[k]==v,'生成段落.json:'+k
    else:
        tables.update(newt);sections.update(news)
        for path,value in [(A/'计算表.json',tables),(A/'生成段落.json',sections),
            (REVIEW/'定值展示矩阵.json',dict(说明='从锁定32112节点按三个分散系数定值重分组，保留锁定18表原件',索引=index,单元=cells)),
            (REVIEW/'逐站展示复算.json',evidence)]:
            path.write_text(json.dumps(value,ensure_ascii=False,indent=2,default=lambda x:x.item())+'\n')
        (REVIEW/'六参数受控完整序列.json').write_text(json.dumps(
            {k:v.to_dict('records') for k,v in controlled_sequences(data).items()},ensure_ascii=False,indent=2)+'\n')
    print('报告资产核验通过：六参数、32112节点、27张定值矩阵、1296单元、46座站')

if __name__=='__main__':main()
