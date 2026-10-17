"""为当前六章增加可复现的证据图；只读取原始资料和已锁定结果。"""
from pathlib import Path
import hashlib
import json
import math
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.font_manager import fontManager, FontProperties

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'tools'))
from sync_current_report_results import case, controlled_sequences, PUBLIC, LOCK, f as show_number
from 实验.研究.rebuild_2026.current_economic_assumptions import cost_factors

A = ROOT/'研究报告/02图表/当前版'
REVIEW = ROOT/'研究报告/05_review/当前版/1016矩阵分区与文献补充'
SOURCE = ROOT/'研究报告/数据来源/当前版/图文扩充_20261016'
SOURCE.mkdir(parents=True, exist_ok=True)
fontManager.addfont('/usr/share/fonts/wps-office/FZFSK.TTF')
plt.rcParams.update({'font.family': ['Times New Roman', FontProperties(fname='/usr/share/fonts/wps-office/FZFSK.TTF').get_name()],
                     'font.size': 12, 'axes.unicode_minus': False, 'axes.spines.top': False,
                     'axes.spines.right': False, 'pdf.fonttype': 42, 'svg.fonttype': 'path'})
BLUE, GOLD, INK, GRAY = '#32698c', '#b18a3c', '#333333', '#d7dadd'
MAP = []


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def frame(key):
    tables = json.loads((A/'计算表.json').read_text())
    rows = [[x.strip() for x in l.strip('|').split('|')] for l in tables[key].splitlines() if l.startswith('|')]
    return pd.DataFrame(rows[2:], columns=rows[0])


def numeric(series):
    return pd.to_numeric(series.astype(str).str.replace('%', '', regex=False))


def save(fig, key, data, sources, question, family, takeaway):
    for ax in fig.axes:
        ax.tick_params(labelsize=11)
        ax.set_axisbelow(True)
    fig.tight_layout(pad=1.1)
    fig.savefig(A/(key+'.png'), dpi=360, facecolor='white')
    fig.savefig(SOURCE/(key+'.pdf'), facecolor='white')
    fig.savefig(SOURCE/(key+'.svg'), facecolor='white')
    data.to_csv(SOURCE/(key+'.csv'), index=False)
    MAP.append(dict(图键=key, 分析问题=question, 图形=family, 支持结论=takeaway,
                    颜色='蓝、金及灰阶；两类方案以空心、实心或线型共同区分',
                    绘图数据=str((SOURCE/(key+'.csv')).relative_to(ROOT)),
                    原始依据={str(p.relative_to(ROOT)): sha(p) for p in sources},
                    图件SHA256=sha(A/(key+'.png'))))
    plt.close(fig)


def technical_route():
    fig, ax = plt.subplots(figsize=(6.8, 8.4)); ax.set_xlim(0, 10); ax.set_ylim(0, 12); ax.axis('off')
    def box(x, y, w, h, title, body):
        ax.add_patch(patches.Rectangle((x, y), w, h, facecolor='#f5f7f8', edgecolor=BLUE, lw=1.25))
        ax.text(x+w/2, y+h-.27, title, ha='center', va='center', fontsize=13.8)
        ax.text(x+w/2, y+h/2-.12, body, ha='center', va='center', fontsize=12, linespacing=1.55)
    def arrow(a, b):
        ax.annotate('', xy=b, xytext=a, arrowprops=dict(arrowstyle='-|>', color=BLUE, lw=1.25, mutation_scale=13))
    box(.15, 10.45, 9.7, 1.35, '研究问题与规范依据', '分布式新能源改变双向功率任务\n区域容量储备与站级承载需求协调')
    box(.15, 7.85, 4.65, 2.0, '运行特征与参数筛选（第三章）', '容量、负荷、光伏及设备统计\n正反向净负荷与95%峰值持续时间\n十三项候选指标筛选五项参数')
    box(5.2, 7.85, 4.65, 2.0, '工程费用模型（第四章）', '主变更换与扩建、储能、联络\n采购规模及投运年份计费\n共同评价期现金流折现')
    arrow((2.5, 10.45), (2.5, 9.85)); arrow((7.5, 10.45), (7.5, 9.85))
    box(.15, 4.7, 4.65, 2.5, '地区逐年规划（第五章）', '共同初态及实际年度负荷\n正常与主变N-1联合约束\n主变、储能与联络共同配置\n刚性与弹性方案及逐站解释')
    box(5.2, 4.7, 4.65, 2.5, '五站参数推广（第五章）', '明确设备与源荷、网络条件\n年最大净负荷平均增长率\n装机、转供及负荷分散条件\n容载比区间与完整节点响应')
    arrow((2.5, 7.85), (2.5, 7.2)); arrow((7.5, 7.85), (7.5, 7.2))
    # 两类分析共同使用运行约束与费用，交叉箭头在框间留白汇合。
    ax.plot([2.5, 2.5, 7.5, 7.5], [7.85, 7.52, 7.52, 7.2], color=BLUE, lw=.8)
    box(.15, 2.45, 9.7, 1.5, '配置与费用核验', '年度设备连续在役、转接守恒、逐工况容量校核\n按新购主变、储能及联络投运批次复算费用')
    arrow((2.5, 4.7), (2.5, 3.95)); arrow((7.5, 4.7), (7.5, 3.95))
    box(.15, .25, 9.7, 1.5, '研究结论与规划应用（第六章）', '解释容量与费用差异，形成条件推荐范围\n结合片区实际设备与网络落实建设方案')
    arrow((5, 2.45), (5, 1.75))
    save(fig, 'technical_route', pd.DataFrame({'阶段':['问题与依据','运行特征','工程费用','地区规划','参数推广','核验','应用']}),
         list((ROOT/'研究报告/03_MD/当前版').glob('0[1-6] *.md')), '方法与成果如何衔接', '流程框图', '地区规划与参数推广分别组织，并共同核验')


def history():
    path = ROOT/'研究报告/数据来源/当前版/实际案例相关性/年度样本.csv'
    d = pd.read_csv(path)
    fig, axes = plt.subplots(2, 1, figsize=(6.8, 6.8))
    for ax, cn in zip(axes, ['邳州', '市区']):
        sub = d[d.region.eq(cn)]; x=np.arange(len(sub))
        ax.bar(x-.19, sub.capacity_mva, .36, label='主变容量/MVA', color=BLUE)
        ax.bar(x+.19, sub.peak_mw, .36, label='年网供最大负荷/MW', facecolor='white', edgecolor=GOLD, hatch='//')
        ax.set_xticks(x,sub.year);ax.set_title(cn+'年度容量与负荷', fontsize=14);ax.set_ylabel('MVA / MW');ax.legend(fontsize=10,loc='upper left');ax.set_ylim(0,sub.capacity_mva.max()*1.3)
    save(fig,'historical_capacity_load',d,[path],'容量和负荷是否同步变化','分面分组柱图','两地区容量与负荷增长关系不同')
    rows=[]
    fig,axes=plt.subplots(2,1,figsize=(6.8,6.4))
    for ax,cn in zip(axes,['邳州','市区']):
        sub=d[d.region.eq(cn)].sort_values('year');capacity=sub.capacity_mva.to_numpy();load=sub.peak_mw.to_numpy()
        c=np.diff(capacity)/load[1:];p=capacity[:-1]*(1/load[1:]-1/load[:-1]);x=np.arange(4)
        ax.bar(x-.19,c,.36,color=BLUE,label='容量变化贡献');ax.bar(x+.19,p,.36,facecolor='white',edgecolor=GOLD,hatch='//',label='负荷变化贡献')
        ax.plot(x,c+p,'D',color=INK,label='容载比净变化',ms=5);ax.axhline(0,color=INK,lw=.7)
        ax.set_xticks(x,sub.year.iloc[1:]);ax.set_title(cn+'年度容载比变化分解',fontsize=14);ax.set_ylabel('容载比变化量');ax.legend(fontsize=9,ncol=2)
        rows.extend(dict(地区=cn,年份=int(y),容量贡献=float(a),负荷贡献=float(b),净变化=float(a+b)) for y,a,b in zip(sub.year.iloc[1:],c,p))
    save(fig,'historical_clr_contribution',pd.DataFrame(rows),[path],'比值变化由容量还是负荷引起','分组柱与净变化点','负荷回落和容量建设分别影响比值')
    d=frame('quarterly_energy');fig,axes=plt.subplots(2,1,figsize=(6.8,6.2));x=np.arange(4)
    pv=numeric(d.iloc[:,1]);load=numeric(d.iloc[:,2]);ratio=pv/load*100
    axes[0].bar(x-.18,pv/1e4,.35,color=BLUE,label='光伏发电量估计');axes[0].bar(x+.18,load/1e4,.35,facecolor='white',edgecolor=GOLD,hatch='//',label='用户用电量估计')
    axes[0].set_ylabel('电量/万MWh');axes[0].legend(fontsize=10);axes[0].set_title('邳州2025年季度电量与渗透率',fontsize=14)
    axes[1].bar(x,ratio,color=BLUE,width=.45);axes[1].set_ylabel('电量渗透率/%');axes[1].set_ylim(0,70)
    for i,v in enumerate(ratio):axes[1].text(i,v+1,f'{v:.0f}%',ha='center',fontsize=11)
    for ax in axes:ax.set_xticks(x,d.iloc[:,0])
    save(fig,'quarterly_energy_comparison',d,[A/'计算表.json'],'季节电量比值如何受供用电规模影响','分面柱图','二季度比值高于三季度，分母规模不同')


def station_inputs():
    lock=json.loads(LOCK.read_text());names={}
    for line in case.MAPPING.read_text().splitlines()[1:]:
        r=line.split()
        if len(r)>=3:names[r[-1]]=r[1]
    raw=[]
    for region,cn in [('pizhou','邳州'),('city','市区')]:
        entry=next(e for e in lock['方案采用'] if e['地区代码']==region and e['起点代码']=='compressed')
        path=ROOT/entry['输入']['path'];inp=json.loads(path.read_text());ids=list(inp['stations'])
        scenes=case.base.load_scenes(case.base.OUT/region,inp);power=scenes[2025]
        show=[(j,sid) for j,sid in enumerate(ids) if not sid.startswith('SIM-')]
        d=pd.DataFrame([dict(站号=sid,变电站=names[sid],初始容量_MVA=sum(inp['stations'][sid]['initial_units']),
              最大正向净负荷_MW=max(0,power[:,j].max()),最大反向净负荷_MW=max(0,-power[:,j].min())) for j,sid in show])
        fig,ax=plt.subplots(figsize=(6.8, max(6,len(d)*.245)));y=np.arange(len(d))
        ax.barh(y-.17,d['最大正向净负荷_MW'],.31,color=BLUE,label='正向极值幅值')
        ax.barh(y+.17,d['最大反向净负荷_MW'],.31,facecolor='white',edgecolor=GOLD,hatch='//',label='反向极值幅值')
        ax.set_yticks(y,d['变电站']);ax.invert_yaxis();ax.set_xlabel('净负荷极值幅值/MW');ax.set_title(cn+'2025年逐站正反向净负荷',fontsize=14);ax.legend(fontsize=10)
        save(fig,region+'_station_direction',d,[path,ROOT/'研究报告/01研究推荐/当前版/静态联合替代_20261015/逐年方案.csv'],
             '各站主要承受哪个方向的容量任务','逐站分组条形图','两方向极值分别展示；各站极值时刻可以不同')
        # 逐站初始与两类方案最大单台N-1剩余能力。
        base={sid:np.array(inp['stations'][sid]['initial_units']+[0.]) for _,sid in show}
        cols={'初始':base};sources=[path]
        for code,label in [('rigid','刚性'),('elastic_free','弹性')]:
            e=next(e for e in lock['方案采用'] if e['地区代码']==region and e['起点代码']=='compressed' and e['方案代码']==code)
            sp=ROOT/e['结果目录']/'stations.csv';f=pd.read_csv(sp).query('year==2025').set_index('station');sources.append(sp)
            cols[label]={sid:f.loc[sid,['unit_1_mva','unit_2_mva','unit_3_mva']].to_numpy(dtype=float) for _,sid in show}
        n=pd.DataFrame([dict(站号=sid,变电站=names[sid],**{label:.95*(u[sid].sum()-u[sid].max()) for label,u in cols.items()}) for _,sid in show])
        fig,ax=plt.subplots(figsize=(6.8,max(6,len(n)*.245)));y=np.arange(len(n))
        for label,offset,color,marker in [('初始',-.17,'#777777','x'),('刚性',0,GOLD,'o'),('弹性',.17,BLUE,'s')]:
            ax.scatter(n[label],y+offset,s=28,marker=marker,edgecolors=color if marker!='x' else None,facecolors='none' if label=='刚性' else color,label=label,zorder=3)
        ax.set_yticks(y,n['变电站']);ax.invert_yaxis();ax.set_xlabel('最大单台主变N-1后剩余有功能力/MW');ax.set_xlim(left=0);ax.set_title(cn+'逐站剩余主变能力',fontsize=14);ax.legend(fontsize=10,ncol=3);ax.grid(axis='x',alpha=.2)
        save(fig,region+'_station_n1',n,sources,'总容量变化怎样落实到故障剩余能力','分组点图','相同总容量下设备台数和规格影响N-1剩余能力')
        # 输入逐站年度转供预算直接读取输入与模型函数，保持模型约束一致。
        raw.append(d)
    return raw


def correlations():
    d=frame('current_controlled_correlations');v=numeric(d.Pearson);fig,ax=plt.subplots(figsize=(6.8,6.7));y=np.arange(len(d))
    ax.barh(y,v,color=[BLUE if abs(x)>=.4 else '#c4cbd0' for x in v],edgecolor=INK,lw=.35)
    ax.set_yticks(y,d['指标'].str.replace('主变与线路单位功率投资比','主变与线路\n单位功率投资比').str.replace('主变与储能单位功率投资比','主变与储能\n单位功率投资比'));ax.invert_yaxis();ax.set_xlim(-1.05,1.12)
    ax.axvline(0,color=INK,lw=.7)
    for x in [-.4,.4]:ax.axvline(x,color=INK,ls='--',lw=.8)
    for i,x in enumerate(v):ax.text(x+(.025 if x>=0 else -.025),i,f'{x:.2f}',va='center',ha='left' if x>=0 else 'right',fontsize=10)
    ax.set_xlabel('组内Pearson相关系数');ax.set_title('十三项候选指标与容载比的组内相关',fontsize=14)
    save(fig,'indicator_correlation_strength',d,[A/'计算表.json'],'哪些指标达到研究相关强度要求','带参考线的相关系数条形图','九项达到绝对值0.40要求；灰色为其余四项')
    d=frame('current_input_correlations');values=d.iloc[:,1:].astype(float).to_numpy();names=[s.replace('分布式电源装机渗透率','装机渗透率').replace('年最大净负荷平均增长率','年最大净负荷\n平均增长率') for s in d.iloc[:,0]]
    fig,ax=plt.subplots(figsize=(6.8,5.7));im=ax.imshow(values,vmin=-1,vmax=1,cmap=LinearSegmentedColormap.from_list('report_correlation',[GOLD,'#ffffff',BLUE]));ax.set_xticks(range(5),names,rotation=25,ha='right');ax.set_yticks(range(5),names)
    for i in range(5):
        for j in range(5):ax.text(j,i,f'{values[i,j]:.2f}',ha='center',va='center',color='white' if abs(values[i,j])>.6 else INK,fontsize=12)
    ax.set_title('五项推广参数的Pearson相关',fontsize=14);fig.colorbar(im,ax=ax,label='Pearson系数',shrink=.8)
    save(fig,'five_parameter_correlation_map',d,[PUBLIC/'五参数输入相关.csv'],'五项代表参数保留多少线性重叠信息','相关矩阵热图','有效情景库中最大非对角绝对值0.29')


def engineering():
    d=frame('transformer_projects');names=['邢楼扩建','墩集扩建','王庄更换','鲁庙更换'];x=np.arange(4)
    buy=numeric(d.iloc[:,1]);removed=numeric(d.iloc[:,2]);net=numeric(d.iloc[:,3]);cost=numeric(d.iloc[:,4]);d=d.assign(简名=names,单位新购投资=cost/buy,单位净增投资=cost/net)
    fig,ax=plt.subplots(figsize=(6.8,4.8));ax.bar(x,net,color=BLUE,label='容量净增');ax.bar(x,removed,bottom=net,facecolor='white',edgecolor=GOLD,hatch='//',label='同期替换容量')
    for i,v in enumerate(buy):ax.text(i,v+2,f'新购{v:.0f}',ha='center',fontsize=11)
    ax.set_xticks(x,names);ax.set_ylim(0,125);ax.set_ylabel('容量/MVA');ax.set_title('主变工程新购、替换与净增容量',fontsize=14);ax.legend(fontsize=10)
    save(fig,'transformer_capacity_balance',d,[A/'计算表.json'],'采购规模与容量增量怎样对应','容量构成堆积柱图','更换工程需要采购被替换的原有容量')
    fig,ax=plt.subplots(figsize=(6.8,4.8));ax.bar(x-.18,cost/buy,.35,color=BLUE,label='按新购容量');ax.bar(x+.18,cost/net,.35,facecolor='white',edgecolor=GOLD,hatch='//',label='按净增容量')
    for i,(a,b) in enumerate(zip(cost/buy,cost/net)):
        ax.text(i-.18,a+.7,f'{a:.2f}',ha='center',fontsize=10);ax.text(i+.18,b+.7,f'{b:.2f}',ha='center',fontsize=10)
    ax.set_xticks(x,names);ax.set_ylim(0,46);ax.set_ylabel('单位容量投资/（万元/MVA）');ax.set_title('主变工程投资的两种容量分母',fontsize=14);ax.legend(fontsize=10)
    save(fig,'transformer_unit_cost_basis',d,[A/'计算表.json'],'费用系数分母选择如何影响单位值','分组柱图','王庄和鲁庙按净增折算的系数高于按新购折算')
    q=np.array([.1,.3,.5,.8,.9]);d=pd.DataFrame({'电缆长度占比':q,'架空部分':3*24*(1-q),'电缆部分':3*180*q,'固定接入费':6.});fig,ax=plt.subplots(figsize=(6.8,4.8));bottom=np.zeros(5)
    for k,c,h in [('架空部分',BLUE,''),('电缆部分',GOLD,'//'),('固定接入费','#9da4aa','..')]:
        ax.bar(range(5),d[k],bottom=bottom,label=k,color=c,hatch=h,edgecolor=INK,lw=.4);bottom+=d[k]
    for i,v in enumerate(bottom):ax.text(i,v+5,f'{v:.2f}',ha='center',fontsize=10)
    ax.set_xticks(range(5),[f'{v:.0%}' for v in q]);ax.set_xlabel('电缆长度占比');ax.set_ylabel('3 km联络项目投资/万元');ax.set_ylim(0,570);ax.set_title('不同敷设组成的联络项目投资',fontsize=14);ax.legend(fontsize=10)
    save(fig,'line_investment_components',d,[ROOT/'实验/研究/rebuild_2026/current_economic_assumptions.py'],'敷设组成怎样改变单项联络价格','投资构成堆积柱图','固定接入费保持6万元，线长部分随电缆占比改变')
    h=np.array([1,2,4,6,8]);n=np.ceil(1/np.minimum(.1,.215*.76/h)).astype(int);d=pd.DataFrame({'支撑持续时间_h':h,'柜数':n,'额定功率_MW':n*.1,'额定能量_MWh':n*.215,'有效支撑功率_MW':n*np.minimum(.1,.215*.76/h)})
    fig,axes=plt.subplots(2,1,figsize=(6.8,6.2));axes[0].bar(range(5),n,color=BLUE,width=.5);axes[0].set_ylabel('所需储能柜数/柜');axes[0].set_title('1 MW持续支撑任务的成套柜配置',fontsize=14)
    for i,v in enumerate(n):axes[0].text(i,v+.5,str(v),ha='center',fontsize=11)
    axes[1].bar(np.arange(5)-.18,n*.1,.35,color=BLUE,label='额定功率/MW');axes[1].bar(np.arange(5)+.18,n*.215,.35,facecolor='white',edgecolor=GOLD,hatch='//',label='额定能量/MWh');axes[1].set_ylabel('MW / MWh');axes[1].legend(fontsize=10)
    for ax in axes:ax.set_xticks(range(5),h);ax.set_xlabel('支撑持续时间/h')
    save(fig,'storage_support_modules',d,[ROOT/'实验/研究/rebuild_2026/current_economic_assumptions.py'],'同一缺口需要多少功率和电量','分面柱图','支撑时间延长增加所需柜数和额定能量')
    rows=[];fig,axes=plt.subplots(1,3,figsize=(6.8,4.8),sharey=True)
    for ax,key,label,q in zip(axes,['transformer','line','storage'],['主变','线路','储能'],[.042,.022,.03]):
        years=np.arange(2022,2026);investment=1/1.06**(years-2021);om=np.array([sum(q/1.06**(t-2021) for t in range(y+1,2042)) for y in years])
        ax.bar(years,investment,color=BLUE,label='建设投资现值');ax.bar(years,om,bottom=investment,facecolor='white',edgecolor=GOLD,hatch='//',label='固定运维现值');ax.set_xticks(years,[str(y)[2:] for y in years]);ax.set_title(label,fontsize=14);ax.set_xlabel('投运年（20XX）')
        rows.extend(dict(类型=label,年份=int(y),建设现值=float(a),运维现值=float(b),合计=float(a+b)) for y,a,b in zip(years,investment,om))
    axes[0].set_ylabel('每1万元初始投资的现值/万元');axes[0].legend(fontsize=9,loc='upper left');axes[0].set_ylim(0,1.65)
    save(fig,'lifecycle_investment_maintenance',pd.DataFrame(rows),[ROOT/'实验/研究/rebuild_2026/current_economic_assumptions.py'],'不同措施与投运年如何形成现值因子','分面堆积柱图','共同评价期内建设和固定运维形成费用现值')


def planning():
    lock=json.loads(LOCK.read_text());sources=[];records=[]
    for e in lock['方案采用']:
        p=ROOT/e['方案汇总']['path'];s=json.loads(p.read_text());sources.append(p)
        for row in s['annual']:
            records.append(dict(地区=e['地区'],起点=e['起点代码'],方案='刚性' if e['方案代码']=='rigid' else '弹性',**row))
    d=pd.DataFrame(records)
    for cn,code in [('邳州','pizhou'),('市区','city')]:
        sub=d[d.地区.eq(cn)&d.起点.eq('compressed')]
        fields=['purchased_transformer_mva','new_storage_mwh','new_lines'] if code=='pizhou' else ['purchased_transformer_mva','new_lines']
        units=['当年新购主变/MVA','当年新增储能/MWh','当年新增联络/条'] if code=='pizhou' else ['当年新购主变/MVA','当年新增联络/条']
        fig,axes=plt.subplots(len(fields),1,figsize=(6.8,7.0 if code=='pizhou' else 5.5))
        for label,offset,c,hatch in [('刚性',-.18,GOLD,'//'),('弹性',.18,BLUE,'')]:
            g=sub[sub.方案.eq(label)].sort_values('year');x=np.arange(4)+offset
            for ax,key in zip(axes,fields):ax.bar(x,g[key],.34,label=label,facecolor='white' if label=='刚性' else c,edgecolor=c,hatch=hatch)
        for ax,unit in zip(axes,units):
            ax.set_xticks(range(4),[2022,2023,2024,2025]);ax.set_ylabel(unit);ax.set_ylim(bottom=0);ax.grid(axis='y',alpha=.15)
        axes[0].set_title(cn+'逐年新增工程',fontsize=14);axes[0].legend(fontsize=10,ncol=2)
        save(fig,code+'_annual_new_measures',sub,sources,'建设措施集中在哪些年份','分面分组柱图','当年新购与新增工程对应投运时点')
    end=d[d.起点.eq('compressed')].groupby(['地区','方案'])[['transformer_npv_10k','storage_npv_10k','line_npv_10k']].sum();rows=[]
    for cn in ['邳州','市区']:
        for key,label in [('transformer_npv_10k','主变'),('storage_npv_10k','储能'),('line_npv_10k','联络')]:
            rows.append(dict(地区=cn,措施=label,费用节省=end.loc[(cn,'刚性'),key]-end.loc[(cn,'弹性'),key]))
    f=pd.DataFrame(rows);fig,ax=plt.subplots(figsize=(6.8,4.8));y=np.arange(6);v=f.费用节省
    ax.barh(y,v,color=[BLUE if x>=0 else GOLD for x in v],edgecolor=INK,lw=.4);ax.axvline(0,color=INK,lw=.8);ax.set_yticks(y,f.地区+' '+f.措施);ax.invert_yaxis();ax.set_xlim(-2300,6200)
    for i,x in enumerate(v):ax.text(x+(65 if x>=0 else -65),i,f'{x:+.2f}',va='center',ha='left' if x>=0 else 'right',fontsize=10)
    ax.set_xlabel('刚性费用－弹性费用/万元');ax.set_title('弹性方案费用差的措施构成',fontsize=14)
    save(fig,'plan_cost_difference',f,sources,'费用降低由哪些措施贡献','带零基准的有符号条形图','主变费用增加与储能、联络费用节省共同形成合计差')
    fig,axes=plt.subplots(2,1,figsize=(6.8,6.4));rows=[]
    for ax,cn in zip(axes,['邳州','市区']):
        sub=d[d.地区.eq(cn)&d.year.eq(2025)];labels=[];values=[]
        for start in ['compressed','annual_2021']:
            for label in ['刚性','弹性']:
                allrows=d[d.地区.eq(cn)&d.起点.eq(start)&d.方案.eq(label)];row=sub[sub.起点.eq(start)&sub.方案.eq(label)].iloc[0]
                total=allrows.added_lifecycle_npv_10k.sum();labels.append(('共同起点' if start=='compressed' else '实际容量起点')+'\n'+label);values.append(total);rows.append(dict(地区=cn,起点=start,方案=label,费用现值=total,末年主变=row.capacity_mva,末年储能=row.storage_mwh))
        ax.bar(range(4),values,color=[GOLD,BLUE,GOLD,BLUE],edgecolor=INK,lw=.4);ax.set_xticks(range(4),labels,fontsize=10);ax.set_ylabel('费用现值/万元');ax.set_title(cn+'两种初始容量条件',fontsize=14);ax.set_ylim(0,max(values)*1.22)
        for i,v in enumerate(values):ax.text(i,v+max(values)*.025,f'{v:.2f}',ha='center',fontsize=10)
    save(fig,'initial_capacity_cost_comparison',pd.DataFrame(rows),sources,'初始资产条件如何影响新增费用','分面柱图','起点与逐站结构共同影响新增工程，地区比较使用同一已定稿输入')
    # 兴塘反向工况：原文已有同一截面数据；从冻结逐站配置重算剩余能力。
    rows=[]
    for e in lock['方案采用']:
        if e['地区代码']!='pizhou' or e['起点代码']!='compressed':continue
        p=ROOT/e['结果目录']/'stations.csv';row=pd.read_csv(p).query('year==2025 and station=="BDZ-00164"').iloc[0]
        u=row[['unit_1_mva','unit_2_mva','unit_3_mva']].to_numpy(dtype=float);remain=.95*(u.sum()-u.max())
        rows.append(dict(方案='刚性' if e['方案代码']=='rigid' else '弹性',剩余有功能力_MW=remain,所需充电吸收_MW=30.663566-remain,额定能量_MWh=row.storage_mwh))
    f=pd.DataFrame(rows);fig,ax=plt.subplots(figsize=(6.8,4.8));ax.bar(range(2),f.剩余有功能力_MW,color=BLUE,label='剩余主变有功能力');ax.bar(range(2),f.所需充电吸收_MW,bottom=f.剩余有功能力_MW,facecolor='white',edgecolor=GOLD,hatch='//',label='所需充电吸收')
    for i,r in f.iterrows():
        ax.text(i,r.剩余有功能力_MW/2,show_number(r.剩余有功能力_MW)+' MW',ha='center',color='white',fontsize=12);ax.text(i,32.3,f'配储{r.额定能量_MWh:.2f} MWh',ha='center',fontsize=11)
    ax.axhline(30.663566,color=INK,ls='--',lw=.8);ax.set_ylim(0,39);ax.set_xticks(range(2),f.方案);ax.set_ylabel('反向功率幅值/MW');ax.set_title('兴塘变2025年同一反向截面功率分担',fontsize=14);ax.legend(fontsize=10,loc='upper center',bbox_to_anchor=(.5,-.1),ncol=2)
    save(fig,'xingtang_reverse_capacity',f,sources,'主变补强如何减少反向吸收任务','功率分担堆积柱图','剩余主变能力增加，对应储能吸收需求减少')


def parameter_responses():
    path=PUBLIC/'统一有效样本.csv';d=pd.read_csv(path);seq=controlled_sequences(d)
    f=seq['eta'];x=f['分布式电源装机渗透率'];fig,axes=plt.subplots(2,1,figsize=(6.8,6.3),sharex=True)
    axes[0].plot(x,f['主变容量_MVA'],'o-',color=BLUE);axes[0].set_ylabel('主变容量/MVA');axes[0].set_title('装机渗透率对应的设备配置',fontsize=14)
    axes[1].bar(x,f['储能额定功率_MW'],width=.15,color=GOLD);axes[1].set_ylabel('储能额定功率/MW');axes[1].set_xlabel('装机渗透率');axes[1].set_xticks(np.arange(0,3.01,.5))
    for ax in axes:ax.grid(alpha=.18)
    save(fig,'eta_device_response',f,[path],'反向任务何时触发主变与储能变化','容量曲线与储能柱图','0至1.50配置保持，之后出现储能及主变组合切换')
    f=seq['growth'];x=np.arange(len(f));labels=[f'{v*100:g}%' for v in f['年最大净负荷平均增长率']];fig,axes=plt.subplots(2,1,figsize=(6.8,6.3),sharex=True)
    axes[0].bar(x-.18,f['主变容量_MVA'],.35,color=BLUE,label='主变容量/MVA');peak=250*(1+f['年最大净负荷平均增长率'])**4;axes[0].bar(x+.18,peak,.35,facecolor='white',edgecolor=GOLD,hatch='//',label='规划负荷/MW');axes[0].set_ylabel('MVA / MW');axes[0].legend(fontsize=10);axes[0].set_title('负荷发展与容量储备消耗',fontsize=14)
    axes[1].plot(x,f['容载比'],'o-',color=BLUE);axes[1].set_ylabel('容载比');axes[1].set_xlabel('年最大净负荷平均增长率');axes[1].set_xticks(x,labels);axes[1].grid(alpha=.18)
    save(fig,'growth_capacity_reserve',f,[path],'容量增量与负荷增长怎样共同改变比值','分面分组柱与比值点线','固定容量段负荷消耗储备，整台主变增容改变比值')


def duration_and_storage_distribution():
    paths=[];rows=[];fig,axes=plt.subplots(2,2,figsize=(6.8,6.8))
    for i,(region,cn) in enumerate([('pizhou','邳州'),('city','市区')]):
        p=ROOT/f'研究报告/数据来源/当前版/区域时序/{region}_8760.csv';paths.append(p)
        d=pd.read_csv(p);values=np.sort(d.abs_mw.to_numpy())[::-1];hours=np.arange(1,len(d)+1);threshold=.95*values[0]
        for j in [0,1]:
            ax=axes[i,j];limit=len(d) if j==0 else 24
            ax.plot(hours[:limit],values[:limit],color=BLUE,lw=1.4)
            ax.axhline(threshold,color=INK,ls='--',lw=.8,label='95%峰值')
            ax.set_title(cn+('全年排序' if j==0 else '前24个排序小时'),fontsize=12)
            ax.set_xlabel('净负荷绝对值排序小时');ax.set_ylabel('净负荷绝对值/MW');ax.grid(alpha=.15)
            if j==0:ax.set_ylim(bottom=0);ax.set_xticks([1,4380,8760])
            else:ax.set_xticks([1,6,12,18,24]);ax.legend(fontsize=9)
        rows.extend(dict(地区=cn,排序小时=int(h),净负荷绝对值_MW=float(v),峰值95百分比_MW=float(threshold)) for h,v in zip(hours,values))
    save(fig,'regional_load_duration',pd.DataFrame(rows),paths,'全年高功率时段的累计占用有多长','全时段与近峰段分面持续曲线','排序用于累计占用分析，连续时长由原时间顺序统计')
    lock=json.loads(LOCK.read_text());sources=[];frames=[];names={}
    for line in case.MAPPING.read_text().splitlines()[1:]:
        r=line.split()
        if len(r)>=3:names[r[-1]]=r[1]
    for code,label in [('rigid','刚性'),('elastic_free','弹性')]:
        e=next(e for e in lock['方案采用'] if e['地区代码']=='pizhou' and e['起点代码']=='compressed' and e['方案代码']==code)
        p=ROOT/e['结果目录']/'stations.csv';sources.append(p);f=pd.read_csv(p).query('year==2025').set_index('station')
        frames.append(f['storage_mwh'].rename(label))
    d=pd.concat(frames,axis=1);d=d[(d>0).any(axis=1)];d['变电站']=[names[x] for x in d.index];d=d.reset_index()
    fig,ax=plt.subplots(figsize=(6.8,5.1));y=np.arange(len(d))
    for label,offset,color in [('刚性',-.18,GOLD),('弹性',.18,BLUE)]:
        ax.barh(y+offset,d[label],.33,facecolor='white' if label=='刚性' else color,edgecolor=color,hatch='//' if label=='刚性' else '',label=label)
        for yy,v in zip(y+offset,d[label]):ax.text(v+.15,yy,show_number(v),va='center',fontsize=10)
    ax.set_yticks(y,d['变电站']);ax.invert_yaxis();ax.set_xlabel('2025年在役储能额定能量/MWh');ax.set_xlim(0,d[['刚性','弹性']].to_numpy().max()*1.2);ax.set_title('邳州末年储能的站点分布',fontsize=14);ax.legend(fontsize=10)
    save(fig,'pizhou_storage_distribution',d,sources,'配储减少集中在哪些站点','逐站分组条形图','储能变化集中于兴塘、邳城等站，部分站保留或新增局部支撑')
    from report_matrix_figures import lookup_bounds
    lookup_bounds(save)


def main():
    technical_route();history();station_inputs();correlations();engineering();planning();parameter_responses();duration_and_storage_distribution()
    from report_matrix_figures import parameter_devices
    parameter_devices(save)
    (REVIEW/'新增图件来源与图形选择.json').write_text(json.dumps(MAP,ensure_ascii=False,indent=2)+'\n')
    print('可复现图件',len(MAP),'（含重绘图1-1）')


if __name__=='__main__':main()
