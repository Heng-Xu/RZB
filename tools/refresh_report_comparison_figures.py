"""仅从当前表格与绘图数据刷新负载率和敏感性图，不覆盖正文。"""
from pathlib import Path
from io import StringIO
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager, FontProperties
from matplotlib.ticker import StrMethodFormatter

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'研究报告/02图表/当前版'
D=ROOT/'研究报告/05_review/当前版/1010统一修订'
T=json.loads((A/'计算表.json').read_text())
fontManager.addfont('/usr/share/fonts/wps-office/FZFSK.TTF')
plt.rcParams.update({'font.family':['Times New Roman',FontProperties(fname='/usr/share/fonts/wps-office/FZFSK.TTF').get_name()],'axes.unicode_minus':False,'font.size':11})
def rows(k):
    lines=[l for l in T[k].splitlines() if l.startswith('|')]
    return [[v.strip() for v in l.strip('|').split('|')] for l in lines[2:]]
def save(fig,name):
    fig.tight_layout();fig.savefig(A/(name+'.png'),dpi=240,bbox_inches='tight');plt.close(fig)
for reg,cn in [('pizhou','邳州'),('city','市区')]:
    ld=pd.read_csv(D/(cn+'负载率绘图值.csv'),index_col=0)
    ld=ld[~ld.index.str.contains('补充仿真')]
    fig,ax=plt.subplots(figsize=(8,max(5,len(ld)*.23)))
    im=ax.imshow(ld.values,aspect='auto',cmap='YlOrRd',vmin=0,vmax=180)
    ax.set_yticks(range(len(ld)),ld.index,fontsize=8);ax.set_xticks(range(4),ld.columns);ax.set_xlabel('年份')
    cb=fig.colorbar(im,ax=ax,label='站级负载率/%');cb.ax.yaxis.set_major_formatter(StrMethodFormatter('{x:.0f}'))
    save(fig,reg+'_modeled_peaks')
fig,ax=plt.subplots(figsize=(8,4))
for cn in ['邳州','市区']:
    data=[r for r in rows('new_annual_loading') if r[0]==cn]
    ax.plot([int(r[1]) for r in data],[float(r[3]) for r in data],marker='o',label=cn+'最大值')
    ax.plot([int(r[1]) for r in data],[float(r[2]) for r in data],ls='--',label=cn+'中位数')
ax.set_xticks([2022,2023,2024,2025]);ax.set_ylabel('站级负载率/%');ax.legend();save(fig,'annual_model_pressure')
fig,axes=plt.subplots(3,2,figsize=(9,9))
for j,(key,label) in enumerate([('growth','年最大净负荷平均增长率'),('line','线路成本系数'),('duration','储能支撑持续时间')]):
    for cn,color,marker in [('邳州','#315c78','o'),('市区','#aa563c','s')]:
        data=[r for r in rows('case_sensitivity_'+key) if r[0]==cn]
        # 两地区各自的三点扰动，实际参数取值写在横轴。
        x=np.arange(3)
        axes[j,0].plot(x,[float(r[4]) for r in data],marker=marker,color=color,label=cn)
        axes[j,1].plot(x,[float(r[7]) for r in data],marker=marker,color=color,label=cn)
    values=rows('case_sensitivity_'+key)
    ticklabels=[values[i][1]+' / '+values[i+3][1] for i in range(3)]
    for ax in axes[j]:
        ax.set_xticks(x,ticklabels,fontsize=8);ax.set_xlabel(label+'（邳州 / 市区）',fontsize=10)
        ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.15);ax.legend(fontsize=9)
    axes[j,0].set_ylabel('容载比');axes[j,1].set_ylabel('评价期费用现值/万元')
save(fig,'case_sensitivity')
