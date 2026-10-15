"""两地区经济方案、固定基期对照和转供响应矩阵结果汇报。"""
import json
import os
from decimal import Decimal,ROUND_HALF_UP

import numpy as np
import pandas as pd

from ..review_20261015.memo import table
from . import model as m


def num(v):
    if pd.isna(v):return '—'
    return str(Decimal(str(v)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))


def gap(v):
    if pd.isna(v):return '—'
    if 0<v<.01:return '<1%'
    return f'{v:.0%}'


def main():
    proof=json.loads((m.REVIEW/'最终经济方案核验.json').read_text());assert proof['verified']
    a=pd.read_csv(m.PUBLIC/'逐年方案.csv');fees=pd.read_csv(m.PUBLIC/'费用及精度.csv');base=pd.read_csv(m.PUBLIC/'固定2021起点.csv')
    matrix=pd.read_csv(m.PUBLIC/'典型响应推荐矩阵.csv');parts=['# 两区县弹性经济方案结果汇总（2026年10月15日）',
        '本轮采用已确认的弹性经济参考作为主方案，名称统一为“弹性经济优化方案”。2021年固定两方案共同起点，2022—2025年逐年优化；正常按年固定比例转供、储能作为事故备用、事故仅直接相连通道转接。市区正向储能支撑6小时，邳州2小时。弹性以费用为目标选配主变、储能和联络。',
        '## 1. 固定2021基期',
        table(['地区','起点设置','容量/MVA','基期负荷/MW','基期容载比'],
            [[r.地区,r.起点,num(r.固定容量_MVA),num(r.基期负荷_MW),num(r.基期容载比)] for r in base.itertuples()]),
        '主组沿用原共同仿真设备。补充组保留2021年原表地区总容量，逐站双主变组合继承已冻结的比例标定；原表总容量与逐站研究设置分别保留来源。两组均保持2021年容量不参与寻优。',
        '## 2. 共同仿真起点的逐年结果',
        '下表数值按“刚性 / 弹性经济优化”列示；储能为年末在役能量，联络为累计新增。2021行为固定基期。']
    for region in ['邳州','市区']:
        parts += ['### '+region,annual_table(a,region,'共同仿真起点')]
    parts += ['邳州弹性在2022年形成1727 MVA主变配置，前三年无需新增储能，2025年补充7.74 MWh。末年刚性1710 MVA、47.95 MWh、15条联络，弹性1727 MVA、7.74 MWh、15条联络。储能按2小时及76%可用能量折算，减少40.21 MWh对应约15.28 MW支撑；站级配置和转供收支共同验证其替代关系。',
        '市区弹性在2022年完成翟山、统一、西郊三站增容，主变净增63 MVA，后续保持2963 MVA，储能与新联络均为零。刚性末年2927 MVA、91.38 MWh、5条联络。翟山小台由40升至63 MVA，最大一台停运后的主变有功能力由38增至59.85 MW；统一增容提高健康站接收余量。市区储能按6小时支撑折算，91.38 MWh对应约11.57 MW有效功率。',
        '## 3. 保留2021原表容量的补充结果']
    for region in ['邳州','市区']:
        parts += ['### '+region,annual_table(a,region,'2021原表容量起点')]
    parts += ['邳州补充组：弹性主变由2021固定2027 MVA增至2022年2148.50 MVA，随后保持，末年储能4.09 MWh、新联络4条。刚性在该冻结逐站组合下，2022—2025联合规划无可行解：四年负荷对应的2.0容量均低于2027 MVA，保留在役容量的控制使各站主变均无法增容。邢楼初始2×20 MVA，正常反向限值30.40 MW，2025局部极值反向净负荷35.38 MW；即使放开全部候选线路，仍有4.98 MW反向缺口。该结论对应标定设备与既定运行条件。',
        '市区补充组：刚性四年保留3113.50 MVA，2023年负荷增长后储能累计增至141.90 MWh；弹性首年增至3140.50 MVA，四年储能和新联络均为零。',
        '## 4. 具体方案费用现值',
        table(['地区','起点','方案','费用/万元','下界/万元','相对间隙'],
            [[r.地区,r.起点,r.方案,num(r.费用现值_万元),num(r.费用下界_万元),gap(r.相对间隙)] for r in fees.itertuples()]),
        '费用比较在同一起点内进行，历史设备成本由两方案共用，新增工程按相同费用参数和2041年评价截止年计取。所列费用为已通过运行校核的具体配置费用，求解下界与间隙随原始解保存。',
        '## 5. 后续展示的转供响应矩阵',
        '已从全部完整序列中筛出四个转供分档上下界均依次下降的典型场景。下表统一固定电缆长度占比50%、储能支撑4小时和装机渗透率0.50，线路系数作为固定条件，不独立分类讨论。',
        table(['年最大净负荷平均增长率','负荷分散系数','≤30%','(30%,50%]','(50%,70%]','>70%'],
            [[f'{r[1]*100:g}%',num(r[2]),*list(r[3:])] for r in matrix.itertuples(index=False,name=None)]),
        '增长率4%、分散系数1.10这一行可优先用于正文展示，四档区间均发生变化。10%—90%的细节点仍有离散设备平台，完整节点与设备结果保留。原报告和重新选配库均未发现九个细节点每一步容载比都变化的完整组。区间对应给定静态模板的有效设备节点，工程选用结合导则建议和实际设备条件。',
        '## 6. 核验与结果文件',
        f'7组可行方案通过{proof["static_pairs"]}个同期正常及N−1工况、{proof["normal_station_hours"]}个补齐时序站时点的正常运行校核。另1组不可行结论经放宽候选网络的独立LP验证。18个典型矩阵节点独立LP通过，原解变量、设备、费用及工作簿逐格复核通过。',
        '结果采用既有等效网络及年度负荷缩放形态，保留补值标记；2021原表组保留地区总量，逐站历史档案仍有缺口。全年SOC、新能源利用率、上级反送接纳与完整电压尚未计算。',
        '两份工作簿为《两区县逐年经济方案.xlsx》《推广典型响应矩阵.xlsx》，同目录保存全部逐年、逐站、项目、收支及核验CSV。本轮交付独立结果，正式研究报告和讨论稿尚未同步新结果。']
    (m.PUBLIC/'两区县经济方案结果汇总.md').write_text('\n\n'.join(parts)+'\n')
    plots(a,matrix)
    print('WROTE_TWO_DISTRICTS_MEMO',m.PUBLIC/'两区县经济方案结果汇总.md',flush=True)


def annual_table(a,region,baseline):
    g=a[(a['地区']==region)&(a['起点']==baseline)];r=g[g['方案']=='刚性方案'].set_index('年份');e=g[g['方案']=='弹性经济优化方案'].set_index('年份')
    rows=[]
    for y in r.index:
        failed=r.loc[y,'状态']=='不可行'
        rows.append([str(y)+('（基期）' if y==2021 else ''),
            ('不可行' if failed else num(r.loc[y,'年末主变_MVA']))+' / '+num(e.loc[y,'年末主变_MVA']),
            num(r.loc[y,'容载比'])+' / '+num(e.loc[y,'容载比']),num(r.loc[y,'年末储能_MWh'])+' / '+num(e.loc[y,'年末储能_MWh']),
            ('—' if failed else str(int(r.loc[y,'累计新增联络_条'])))+' / '+str(int(e.loc[y,'累计新增联络_条']))])
    return table(['年份','主变/MVA','容载比','储能/MWh','累计新增联络/条'],rows)


def plots(a,matrix):
    os.environ.setdefault('MPLCONFIGDIR','/tmp/xuzhou110kv-review-matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import fontManager,FontProperties
    fontManager.addfont('/usr/share/fonts/wps-office/FZFSK.TTF');font=FontProperties(fname='/usr/share/fonts/wps-office/FZFSK.TTF').get_name()
    plt.rcParams.update({'font.family':['Times New Roman',font],'axes.unicode_minus':False,'font.size':11})
    out=m.PUBLIC/'图件';out.mkdir(exist_ok=True)
    fig,axes=plt.subplots(2,2,figsize=(11,7),sharey=True)
    for row,region in enumerate(['邳州','市区']):
        for col,baseline in enumerate(m.BASELINES.values()):
            ax=axes[row,col]
            for case,color in [('刚性方案','#5485A2'),('弹性经济优化方案','#D88344')]:
                part=a[(a['地区']==region)&(a['起点']==baseline)&(a['方案']==case)].sort_values('年份')
                ax.plot(part['年份'],part['容载比'],'o-',color=color,label=case)
            ax.set_title(region+'：'+baseline);ax.set_xticks(range(2021,2026));ax.set_ylim(1.5,3.1);ax.grid(alpha=.2)
            if col==0:ax.set_ylabel('容载比')
            if region=='邳州' and col==1:ax.text(.04,.05,'刚性：该标定组合下不可行',transform=ax.transAxes,fontsize=10)
    handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='upper center',ncol=2)
    fig.tight_layout(rect=(0,0,1,.94));fig.savefig(out/'两地区逐年容载比.png',dpi=220);fig.savefig(out/'两地区逐年容载比.pdf');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4),sharey=True);xx=np.arange(4)
    for ax,values in zip(axes,matrix.itertuples(index=False,name=None)):
        ranges=[tuple(map(float,s.split('～'))) for s in values[3:]];lo=[r[0] for r in ranges];hi=[r[1] for r in ranges]
        ax.fill_between(xx,lo,hi,color='#5485A2',alpha=.2);ax.plot(xx,lo,'o-',color='#5485A2',label='下界');ax.plot(xx,hi,'s-',color='#D88344',label='上界')
        for x,l,h in zip(xx,lo,hi):ax.annotate(f'{l:.2f}～{h:.2f}',(x,h),xytext=(0,8),textcoords='offset points',ha='center',fontsize=9)
        ax.set_title(f'增长率{values[1]*100:g}%，分散系数{values[2]:g}');ax.set_xticks(xx,['≤30%','(30%,50%]','(50%,70%]','>70%']);ax.set_xlim(-.4,3.4);ax.set_ylim(1.15,2.1);ax.set_xlabel('初始转供率');ax.grid(alpha=.2)
    axes[0].set_ylabel('容载比');axes[0].legend(loc='upper right',fontsize=9);fig.tight_layout()
    fig.savefig(out/'转供分档典型响应.png',dpi=220);fig.savefig(out/'转供分档典型响应.pdf');plt.close(fig)


if __name__=='__main__':main()
