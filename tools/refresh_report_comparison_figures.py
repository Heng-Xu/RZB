"""从当前锁定案例与参数库刷新正文图件，不修改源稿或锁定结果。"""
from pathlib import Path
import json, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager, FontProperties
from matplotlib.ticker import StrMethodFormatter

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from 实验.研究.rebuild_2026.case_parameters_20261012 import transfer_diagnostic as case
A=ROOT/'研究报告/02图表/当前版'
R=ROOT/'研究报告/05_review/当前版/1016研究报告结果同步'
LOCK=json.loads((ROOT/'研究报告/01研究推荐/当前版/报告数据采用版本.json').read_text())
fontManager.addfont('/usr/share/fonts/wps-office/FZFSK.TTF')
plt.rcParams.update({'font.family':['Times New Roman',FontProperties(fname='/usr/share/fonts/wps-office/FZFSK.TTF').get_name()],
    'axes.unicode_minus':False,'font.size':11})
def save(fig,name):
    fig.tight_layout();fig.savefig(A/(name+'.png'),dpi=240,bbox_inches='tight');plt.close(fig)
summaries={};loading={};names={}
for line in case.MAPPING.read_text().splitlines()[1:]:
    row=line.split()
    if len(row)>=3:names[row[-1]]=row[1]
for region,cn in [('pizhou','邳州'),('city','市区')]:
    entry=next(x for x in LOCK['方案采用'] if x['地区代码']==region and x['起点代码']=='compressed')
    inp=json.loads((ROOT/entry['输入']['path']).read_text())
    ids=list(inp['stations']);show=[j for j,sid in enumerate(ids) if not sid.startswith('SIM-')]
    scenes=case.base.load_scenes(case.base.OUT/region,inp)
    caps=np.array([sum(inp['stations'][sid]['initial_units']) for sid in ids])
    frame=pd.DataFrame({str(y):np.max(np.abs(power),axis=0)[show]/(.95*caps[show])*100
        for y,power in scenes.items()},index=[names[ids[j]] for j in show])
    frame.to_csv(R/(cn+'负载率绘图值.csv'));loading[cn]=frame
    fig,ax=plt.subplots(figsize=(8,max(5,len(frame)*.23)))
    im=ax.imshow(frame.values,aspect='auto',cmap='YlOrRd',vmin=0,vmax=180)
    ax.set_yticks(range(len(frame)),frame.index,fontsize=8);ax.set_xticks(range(4),frame.columns);ax.set_xlabel('年份')
    cb=fig.colorbar(im,ax=ax,label='站级负载率/%');cb.ax.yaxis.set_major_formatter(StrMethodFormatter('{x:.0f}'))
    save(fig,region+'_modeled_peaks')
    for code,label in [('rigid','刚性'),('elastic_free','弹性')]:
        entry=next(x for x in LOCK['方案采用'] if x['地区代码']==region and x['方案代码']==code and x['起点代码']=='compressed')
        summaries[cn,label]=json.loads((ROOT/entry['方案汇总']['path']).read_text())
fig,ax=plt.subplots(figsize=(8,4))
for cn,frame in loading.items():
    ax.plot([2022,2023,2024,2025],frame.max(),marker='o',label=cn+'最大值')
    ax.plot([2022,2023,2024,2025],frame.median(),ls='--',label=cn+'中位数')
ax.set_xticks([2022,2023,2024,2025]);ax.set_ylabel('站级负载率/%');ax.legend();save(fig,'annual_model_pressure')
fig,ax=plt.subplots(figsize=(8,4))
for (cn,label),summary in summaries.items():
    ax.plot([r['year'] for r in summary['annual']],[r['clr'] for r in summary['annual']],
        marker='o',ls='--' if label=='刚性' else '-',label=cn+label)
ax.axhline(2,color='#777777',ls=':',lw=.8);ax.set_xticks([2022,2023,2024,2025]);ax.set_ylabel('容载比');ax.legend(ncol=2);save(fig,'annual_clr')
labels=[cn+label for cn,label in summaries];x=np.arange(4)
fig,ax=plt.subplots(figsize=(8,4));bottom=np.zeros(4)
for field,label in [('transformer_npv_10k','主变'),('storage_npv_10k','储能'),('line_npv_10k','联络')]:
    values=np.array([sum(r[field] for r in s['annual']) for s in summaries.values()])
    ax.bar(x,values,bottom=bottom,label=label);bottom+=values
ax.set_xticks(x,labels);ax.set_ylabel('费用现值/万元');ax.legend();save(fig,'lifecycle_components')
fig,axes=plt.subplots(1,2,figsize=(9,4))
axes[0].bar(x,[sum(r['purchased_transformer_mva'] for r in s['annual']) for s in summaries.values()])
axes[1].bar(x,[s['annual'][-1]['storage_mwh'] for s in summaries.values()])
for ax in axes:ax.set_xticks(x,labels,rotation=15);ax.spines[['top','right']].set_visible(False)
axes[0].set_ylabel('累计新购主变容量/MVA');axes[1].set_ylabel('2025年储能额定能量/MWh');save(fig,'measure_comparison')
d=pd.read_csv(ROOT/'研究报告/01研究推荐/当前版/参数联合情景_20261012/统一有效样本.csv')
mask=np.isclose(d['电缆长度占比'],.1)&np.isclose(d['初始转供率'],.4)&np.isclose(d['储能支撑持续时间_h'],4)&np.isclose(d['负荷分散系数'],1.1)
p=d[mask].pivot(index='分布式电源装机渗透率',columns='年最大净负荷平均增长率',values='容载比')
fig,ax=plt.subplots(figsize=(8,5));im=ax.imshow(p,origin='lower',aspect='auto',cmap='YlOrRd')
ax.set_yticks(range(len(p)),[f'{v:.2f}' for v in p.index]);ax.set_xticks(range(len(p.columns)),[f'{v*100:g}%' for v in p.columns])
ax.set_xlabel('年最大净负荷平均增长率');ax.set_ylabel('分布式电源装机渗透率');fig.colorbar(im,ax=ax,label='容载比');save(fig,'planning_tier_heatmap')
nodes=pd.read_csv(ROOT/'研究报告/01研究推荐/当前版/静态联合替代_20261015/典型场景完整节点.csv')
fig,axes=plt.subplots(1,2,figsize=(10,4))
for i,((growth,kd),group) in enumerate(nodes.groupby(['年最大净负荷平均增长率','负荷分散系数']),1):
    group=group.sort_values('初始转供率');x=group['初始转供率']*100
    label=f'场景{i}（增长率{growth:.3f}，分散系数{kd:.2f}）'
    axes[0].plot(x,group['容载比'],marker='o',label=label)
    axes[1].plot(x,group['费用现值_万元'],marker='o',label=label)
for ax in axes:ax.set_xlabel('初始转供率/%');ax.set_xticks([10,30,50,70,90]);ax.grid(alpha=.2)
axes[0].set_ylabel('容载比');axes[1].set_ylabel('费用现值/万元');axes[0].legend(fontsize=8)
save(fig,'typical_transfer_response')
print('当前案例及推广图件刷新通过：8幅')
