"""从已核验数据形成结果汇总及图件。"""
import json
import os
from decimal import Decimal, ROUND_HALF_UP

import numpy as np
import pandas as pd

from ..review_20261015.memo import table
from . import model as m


def number(x):
    return str(Decimal(str(x)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))


def main():
    result=json.loads((m.REVIEW/'最终推荐核验.json').read_text());assert result['verified']
    a=pd.read_csv(m.PUBLIC/'逐年推荐结果.csv');fees=pd.read_csv(m.PUBLIC/'费用及条件.csv')
    r=a[a['方案']=='刚性方案'].set_index('年份');e=a[a['方案']=='弹性增容替代方案'].set_index('年份')
    seq=pd.read_csv(m.PUBLIC/'五参数固定背景序列.csv');stats=pd.read_csv(m.PUBLIC/'五参数响应统计.csv')
    rows=[]
    for y in r.index:
        rows.append([y,f'{number(r.loc[y,"年末主变_MVA"])} / {number(e.loc[y,"年末主变_MVA"])}',
            f'{number(r.loc[y,"容载比"])} / {number(e.loc[y,"容载比"])}',
            f'{number(r.loc[y,"年末储能_MWh"])} / {number(e.loc[y,"年末储能_MWh"])}',
            f'{int(r.loc[y,"累计新增联络_条"])} / {int(e.loc[y,"累计新增联络_条"])}'])
    fr=fees[fees['方案']=='刚性方案'].iloc[0];fe=fees[fees['方案']=='弹性增容替代方案'].iloc[0]
    summary=['# 推荐方案结果汇总（2026年10月15日）',
        '建议采用“主变增容替代部分储能与新增联络”的逐年方案。两方案保留共同初始设备、年度负荷和逐站转供能力，正常及事故网络约束采用相同口径。为体现增容优先的规划取向，弹性方案另设：各年容量至少为刚性105%、储能不超过刚性50%、累计新增联络不多于刚性且末年至少少2条。这些是本次方案选择条件。工作簿同时保留仅按费用寻优的弹性经济参考。',
        '## 邳州逐年结果',
        '下表均按“刚性 / 弹性增容替代”列示；储能为年末累计能量，联络为截至该年累计新建条数。',
        table(['年份','主变容量/MVA','容载比','储能/MWh','累计新增联络/条'],rows),
        f'2025年主变增加{number(e.loc[2025,"年末主变_MVA"]-r.loc[2025,"年末主变_MVA"])} MVA（{(e.loc[2025,"年末主变_MVA"]/r.loc[2025,"年末主变_MVA"]-1):.0%}），容载比由{number(r.loc[2025,"容载比"])}提高到{number(e.loc[2025,"容载比"])}；储能减少{number(Decimal(str(r.loc[2025,"年末储能_MWh"]))-Decimal(str(e.loc[2025,"年末储能_MWh"])))} MWh（{1-e.loc[2025,"年末储能_MWh"]/r.loc[2025,"年末储能_MWh"]:.0%}），新增联络少4条。',
        '2022年先增容形成1788 MVA配置，2023年沿用已建设备，负荷回落使容载比升至2.35。2024年新增2条联络应对负荷增长。2025年更换一台31.5 MVA主变为50 MVA，净增18.50 MVA，并新增6.02 MWh储能和3条联络；四年方案累计新购主变617.50 MVA，扣除同期更换退出设备后的净增容量为343 MVA。',
        f'两具体可行方案的费用现值分别为{number(fr["费用现值_万元"])}和{number(fe["费用现值_万元"])}万元，后者减少{number(fr["费用现值_万元"]-fe["费用现值_万元"])}万元（{1-fe["费用现值_万元"]/fr["费用现值_万元"]:.0%}）。求解间隙分别约{fr["相对间隙"]:.0%}、{fe["相对间隙"]:.0%}，费用比较对应这两组配置。',
        '## 供电及反向承载如何支撑',
        '本方案正常工况由主变承担站级净负荷；允许按年优化正常转供比例，所选弹性方案最终无需正常转供。故障时，10 kV联络将受压站的部分负荷转至相连站，逐项受既有逐站能力、通道容量、馈线共享余量和接收站主变余量限制。储能按事故备用能量与规定持续时间提供支撑。',
        '替代主要发生在局部薄弱站。戴庄由2×31.5 MVA增至2×50 MVA，最大一台停运后的主变有功能力由29.93增至47.50 MW，本站储能由37.84 MWh减至0；二庙由31.5+80 MVA增至50+80 MVA，事故主变有功能力同样由29.93增至47.50 MW；铁富由2×63 MVA增至2×80 MVA，事故主变有功能力由59.85增至76 MW。新增主变的位置与事故剩余容量共同支撑措施替代。',
        f'三组方案共{result["static_pairs"]}个同期正常及N−1工况、{result["normal_station_hours"]}个补齐时序站时点通过复核，正常反向功率控制在主变有功能力的80%以内。各年原规划负荷保持，时序按年度规划峰值缩放并保留补值标记。当前结论限于净负荷与静态反向承载，全年新能源利用率、上级反送接纳及电压尚需相应资料。',
        '## 五项推广参数的结果',
        '采用设备重新选配模板，保留全部2916个设计节点，其中2673个有效、243个不可行。推荐矩阵按2、4、6小时分别列示，共27张，减少不同时长汇总掩盖节点变化的情况。相邻转供节点仅在设备配置和费用均相同时合并。',
        '下表固定装机渗透率1.5、年最大净负荷平均增长率4%、电缆长度占比10%、初始转供率40%、支撑时间4小时和负荷分散系数1.10，每行只改变相应参数。',
    ]
    response=[]
    for parameter in seq['参数'].unique():
        subset=seq[seq['参数']==parameter].sort_values('参数值')
        def label(v):return f'{v*100:g}%' if parameter in ['年最大净负荷平均增长率','电缆长度占比','初始转供率'] else f'{v:g}'
        response.append([parameter,' → '.join(label(v) for v in subset['参数值']),
            ' → '.join(number(v) for v in subset['容载比'])])
    summary += [table(['参数','参数节点','对应容载比'],response),
        '增长率同时改变规划负荷与所需容量。0%至4%时主变由378增至420.50 MVA，负荷增幅高于容量增幅，容载比由1.51降至1.44；随后设备跨档增加，容载比回升。各参数的作用按容量、负荷及措施共同判断。',
        '初始转供率由10%提高至70%时，主变容量依次为570.50、570.50、446.50、420.50、420.50、415、383.50 MVA；70%—90%保持383.50 MVA及相同配置。40%—50%容量虽保持420.50 MVA，新增联络由10减至4条，储能由0增至0.43 MWh，费用继续下降。主变减量与通道、储能替代分别发生在不同节点。',
        '平台仍有设备与经济依据。模板采用31.5、50、63、80 MVA，每站至少双主变，五站组合下限315 MVA，这是设备菜单和站型假设。上述70%—90%的383.50 MVA平台高于该下限，属于局部约束与费用组合形成的阶段性配置。',
        '五参数完整序列中，相邻容载比保持的比例分别为装机19%、增长0%、电缆67%、转供54%、分散56%。电缆占比平台仍较多：当前占比通过线路投资价格影响设备替代；收资中三档电缆占比线路的允许电流中位数均为595 A，因此保留价格映射。该参数的物理承载力效应需要型号、截面与阻抗的配套映射。',
        '## 结果文件',
        '- `邳州逐年推荐方案.xlsx`：三方案逐年结果、逐站设备、当年及累计建设、费用、联络项目和工况收支。\n- `五参数推荐矩阵与响应.xlsx`：27张条件矩阵、完整响应统计、固定背景序列及相同配置节点合并表。\n- `图件/邳州逐年配置比较.png`、`图件/五参数固定背景响应.png`：可直接查看的结果图。',
        '本轮先交付独立结果包。正式研究报告及讨论稿尚未同步采用本轮数据。']
    (m.PUBLIC/'推荐方案结果汇总.md').write_text('\n\n'.join(summary)+'\n')
    plots(r,e,seq)
    print('RECOMMEND_MEMO',m.PUBLIC/'推荐方案结果汇总.md',flush=True)


def plots(r,e,seq):
    os.environ.setdefault('MPLCONFIGDIR','/tmp/xuzhou110kv-review-matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import fontManager,FontProperties
    fontManager.addfont('/usr/share/fonts/wps-office/FZFSK.TTF')
    font=FontProperties(fname='/usr/share/fonts/wps-office/FZFSK.TTF').get_name()
    plt.rcParams.update({'font.family':['Times New Roman',font],'axes.unicode_minus':False,'font.size':11})
    out=m.PUBLIC/'图件';out.mkdir(exist_ok=True)
    fig,axes=plt.subplots(1,3,figsize=(13,4));x=np.arange(4)
    for ax,key,ylabel in zip(axes,['年末主变_MVA','年末储能_MWh','累计新增联络_条'],['主变容量/MVA','储能/MWh','累计新增联络/条']):
        for shift,frame,name,color in [(-.19,r,'刚性方案','#5485A2'),(.19,e,'弹性增容替代','#D88344')]:
            bars=ax.bar(x+shift,frame[key],width=.36,label=name,color=color)
            ax.bar_label(bars,labels=[number(v) if key=='年末储能_MWh' else f'{v:g}' for v in frame[key]],padding=3,fontsize=8)
        ax.set_xticks(x,list(r.index));ax.set_ylabel(ylabel);ax.set_ylim(0,max(r[key].max(),e[key].max())*1.18)
        ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
    handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='upper center',ncol=2,fontsize=10)
    fig.tight_layout(rect=(0,0,1,.91))
    fig.savefig(out/'邳州逐年配置比较.png',dpi=220);fig.savefig(out/'邳州逐年配置比较.pdf');plt.close(fig)
    fig,axes=plt.subplots(1,5,figsize=(16,3.6))
    for ax,parameter in zip(axes,seq['参数'].unique()):
        part=seq[seq['参数']==parameter].sort_values('参数值');xx=part['参数值'].to_numpy()
        ax.plot(xx,part['容载比'],'o-',color='#5485A2',linewidth=1.6)
        ax.set_title(parameter,fontsize=10);ax.set_xticks(xx)
        ax.set_xticklabels([f'{v*100:g}%' if parameter in ['年最大净负荷平均增长率','电缆长度占比','初始转供率'] else f'{v:g}' for v in xx],fontsize=8,rotation=45 if len(xx)>4 else 0)
        ax.grid(alpha=.2);ax.set_ylim(1.2,2.4)
    axes[0].set_ylabel('容载比');fig.tight_layout()
    fig.savefig(out/'五参数固定背景响应.png',dpi=220);fig.savefig(out/'五参数固定背景响应.pdf');plt.close(fig)


if __name__=='__main__':main()
