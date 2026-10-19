"""从锁定的逐年方案更新报告案例图；原值、绘图表和矢量原件一并保存。"""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager,FontProperties

from report_annual_update import ROOT,ASSET,REVIEW,SOURCE,PUBLIC,load

fontManager.addfont('/usr/share/fonts/wps-office/FZFSK.TTF')
plt.rcParams.update({'font.family':['Times New Roman',FontProperties(fname='/usr/share/fonts/wps-office/FZFSK.TTF').get_name()],
    'font.size':11,'axes.unicode_minus':False,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'path'})
BLUE,GOLD,GRAY='#32698c','#b18a3c','#68747b'
COLORS={'刚性':BLUE,'弹性':GOLD}
MAP=[]

def save(fig,key,data,question,family):
    before=ASSET/(key+'.png');backup=REVIEW/'修前原件'/before.relative_to(ROOT)
    if before.exists() and not backup.exists():
        backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(before,backup)
    SOURCE.mkdir(parents=True,exist_ok=True)
    fig.tight_layout(pad=1.2)
    for suffix in ['png','pdf','svg']:
        fig.savefig((ASSET if suffix=='png' else SOURCE)/(key+'.'+suffix),dpi=300,facecolor='white')
    data.to_csv(SOURCE/(key+'.csv'),index=False)
    MAP.append({'图键':key,'分析问题':question,'图形':family,'交付容器':'原生Word及WPS PDF','调色':'蓝/金；空心与实心或线型共同区分','绘图数据':str((SOURCE/(key+'.csv')).relative_to(ROOT)),'数据行数':len(data),'SHA256':hashlib.sha256(before.read_bytes()).hexdigest()})
    plt.close(fig)

def main():
    names,inputs,powers,plans,fixed=load()
    annual=pd.read_csv(PUBLIC/'逐年新增及费用.csv');annual=annual[annual['方案'].isin(['刚性','弹性'])]
    costs=pd.read_csv(PUBLIC/'费用分项汇总.csv');costs=costs[costs['方案'].isin(['刚性','弹性'])]
    stations=pd.read_csv(PUBLIC/'逐站逐年配置.csv');stations=stations[stations['方案'].isin(['刚性','弹性'])]
    fig,axes=plt.subplots(2,1,figsize=(7,6.5),sharex=True)
    for ax,cn in zip(axes,['邳州','市区']):
        for lab in ['刚性','弹性']:
            d=annual[(annual['地区']==cn)&(annual['方案']==lab)]
            ax.plot(d['年份'],d['容载比'],color=COLORS[lab],marker='o' if lab=='刚性' else 's',ms=3.5,mfc='white' if lab=='刚性' else GOLD,ls='--' if lab=='刚性' else '-',label=lab)
        ax.set_title(cn,fontsize=12);ax.set_ylabel('容载比');ax.grid(axis='y',alpha=.18);ax.legend(ncol=2)
    axes[-1].set_xticks(list(range(2021,2036,2)));axes[-1].set_xlabel('年份')
    save(fig,'annual_clr',annual,'年度容量与负荷共同怎样形成容载比','分面年度折线')
    labels=[cn+lab for cn in ['邳州','市区'] for lab in ['刚性','弹性']]
    ordered=costs.set_index(['地区','方案']).loc[[(cn,lab) for cn in ['邳州','市区'] for lab in ['刚性','弹性']]].reset_index()
    fig,ax=plt.subplots(figsize=(7,4));bottom=np.zeros(4)
    for key,label,color,hatch in [('主变费用现值_万元','主变',BLUE,''),('储能费用现值_万元','储能',GOLD,'//'),('联络费用现值_万元','联络',GRAY,'..')]:
        values=ordered[key].to_numpy();ax.bar(range(4),values,bottom=bottom,color=color,edgecolor='#333333',lw=.6,hatch=hatch,label=label);bottom+=values
    ax.set_xticks(range(4),labels);ax.set_ylabel('2022—2035新增费用现值/万元');ax.legend(ncol=3)
    save(fig,'lifecycle_components',ordered,'各措施怎样组成共同评价期费用','堆积柱图')
    fig,axes=plt.subplots(1,2,figsize=(8,4))
    purchases=[];energies=[]
    for r in ['pizhou','city']:
        for lab in ['刚性','弹性']:
            a=plans[r,lab]['annual'];purchases.append(sum(x['purchased_transformer_mva'] for x in a));energies.append(a[-1]['storage_mwh'])
    for ax,values,title in zip(axes,[purchases,energies],['累计新购主变/MVA','2035年储能/MWh']):
        ax.bar(range(4),values,color=[BLUE,GOLD,BLUE,GOLD],edgecolor='#333333',lw=.6);ax.set_xticks(range(4),labels,rotation=15);ax.set_ylabel(title)
    save(fig,'measure_comparison',annual,'主变采购与储能存量怎样对应方案','分面柱图')
    for region,cn in [('pizhou','邳州'),('city','市区')]:
        d=annual[(annual['地区']==cn)&(annual['年份']>2021)]
        fig,axes=plt.subplots(3,1,figsize=(7,7),sharex=True)
        for ax,key,title in zip(axes,['当年新购主变_MVA','当年新增储能_MWh','当年新增联络_条'],['新购主变/MVA','新增储能/MWh','新增联络/条']):
            for offset,lab in [(-.18,'刚性'),(.18,'弹性')]:
                sub=d[d['方案']==lab];ax.bar(sub['年份']+offset,sub[key],.34,color='white' if lab=='刚性' else GOLD,edgecolor=COLORS[lab],hatch='//' if lab=='刚性' else '',label=lab)
            ax.set_ylabel(title);ax.grid(axis='y',alpha=.15)
        axes[0].legend(ncol=2);axes[-1].set_xticks(list(range(2022,2036,2)));axes[-1].set_xlabel('年份')
        save(fig,region+'_annual_new_measures',d,'每年新增工程怎样随需求形成','三分面分组柱图')
        ids=list(inputs[region]['stations']);show=[j for j,s in enumerate(ids) if s in names]
        initial=np.array([s['initial_units']+[0.] for s in inputs[region]['stations'].values()])
        n1=pd.DataFrame({'站名':[names[ids[j]] for j in show],'初始':[(initial[j].sum()-initial[j].max())*.95 for j in show]})
        for lab in ['刚性','弹性']:
            units=np.array(fixed[region,lab][2035]['units']);n1[lab]=[(units[j].sum()-units[j].max())*.95 for j in show]
        fig,ax=plt.subplots(figsize=(7,max(4,len(show)*.25)))
        for key,offset,color,marker in [('初始',-.2,GRAY,'x'),('刚性',0,BLUE,'o'),('弹性',.2,GOLD,'s')]:
            ax.scatter(n1[key],np.arange(len(show))+offset,color=color,marker=marker,s=23,label=key)
        ax.set_yticks(range(len(show)),n1['站名'],fontsize=9);ax.set_xlabel('2035年N-1剩余主变有功能力/MW');ax.legend(ncol=3);ax.grid(axis='x',alpha=.15)
        save(fig,region+'_station_n1',n1,'各站主变补强怎样改变故障剩余能力','分组点图')
        frame=pd.DataFrame({'站名':[names[ids[j]] for j in show]})
        for year in range(2022,2026):frame[str(year)]=abs(powers[region][year]).max(axis=0)[show]/(.95*initial.sum(axis=1)[show])*100
        fig,ax=plt.subplots(figsize=(7,max(4,len(show)*.24)));im=ax.imshow(frame.iloc[:,1:].to_numpy(),aspect='auto',cmap='YlOrBr');ax.set_yticks(range(len(show)),frame['站名'],fontsize=9);ax.set_xticks(range(4),[2022,2023,2024,2025]);ax.set_xlabel('年份');fig.colorbar(im,ax=ax,label='站级负载率/%')
        save(fig,region+'_modeled_peaks',frame,'基期设备在历史回算源荷下的压力如何分布','热图')
    fig,ax=plt.subplots(figsize=(7,4));rows=[]
    for region,cn in [('pizhou','邳州'),('city','市区')]:
        inp=inputs[region];ids=list(inp['stations']);show=[j for j,s in enumerate(ids) if s in names];cap=np.array([sum(s['initial_units']) for s in inp['stations'].values()])
        medians=[];maxima=[]
        for year in range(2022,2026):
            rate=abs(powers[region][year]).max(axis=0)[show]/(.95*cap[show])*100;medians.append(np.median(rate));maxima.append(max(rate));rows.append({'地区':cn,'年份':year,'中位数':medians[-1],'最大值':maxima[-1]})
        for values,stat,ls in [(maxima,'最大值','-'),(medians,'中位数','--')]:ax.plot(range(2022,2026),values,marker='o',color=BLUE if region=='pizhou' else GOLD,ls=ls,label=cn+stat)
    ax.set_xticks(range(2022,2026));ax.set_ylabel('站级负载率/%');ax.set_xlabel('年份');ax.legend(ncol=2)
    save(fig,'annual_model_pressure',pd.DataFrame(rows),'历史回算工况下局部压力怎样变化','两地区统计点线图；仅四个历史年度，保留直接比较')
    fig,axes=plt.subplots(1,2,figsize=(8,4));difference=[]
    for ax,cn in zip(axes,['邳州','市区']):
        d=costs[costs['地区']==cn].set_index('方案');fields=['主变费用现值_万元','储能费用现值_万元','联络费用现值_万元'];values=[d.loc['刚性',k]-d.loc['弹性',k] for k in fields]
        ax.barh(['主变','储能','联络'],values,color=[BLUE if x>=0 else GOLD for x in values],edgecolor='#333333',lw=.5);ax.axvline(0,color='#333333',lw=.8);ax.set_title(cn);ax.set_xlabel('刚性减弹性费用现值/万元')
        difference.extend({'地区':cn,'措施':name,'费用差_万元':v} for name,v in zip(['主变','储能','联络'],values))
    save(fig,'plan_cost_difference',pd.DataFrame(difference),'累计费用差由哪些措施形成','有符号条形图')
    fig,axes=plt.subplots(2,1,figsize=(7,6),sharex=True)
    for ax,cn in zip(axes,['邳州','市区']):
        for lab in ['刚性','弹性']:
            d=annual[(annual['地区']==cn)&(annual['方案']==lab)];ax.plot(d['年份'],d['累计费用现值_万元'],color=COLORS[lab],ls='--' if lab=='刚性' else '-',marker='o',ms=3,label=lab)
        ax.set_title(cn);ax.set_ylabel('累计费用现值/万元');ax.legend(ncol=2);ax.grid(axis='y',alpha=.15)
    axes[-1].set_xlabel('年份');axes[-1].set_xticks(range(2021,2036,2))
    save(fig,'initial_capacity_cost_comparison',annual,'实际起点下逐年费用差如何累积','两地区累计费用折线')
    d=stations[(stations['地区']=='邳州')&(stations['年份']==2035)].copy();d['站名']=d['变电站'].map(names)
    pivot=d.pivot(index='站名',columns='方案',values='储能电量_MWh').fillna(0);pivot=pivot[pivot.max(axis=1)>0]
    fig,ax=plt.subplots(figsize=(7,max(4,len(pivot)*.3)));y=np.arange(len(pivot))
    for lab,offset in [('刚性',-.18),('弹性',.18)]:ax.barh(y+offset,pivot[lab],.34,color='white' if lab=='刚性' else GOLD,edgecolor=COLORS[lab],hatch='//' if lab=='刚性' else '',label=lab)
    ax.set_yticks(y,pivot.index);ax.set_xlabel('2035年储能额定能量/MWh');ax.legend();save(fig,'pizhou_storage_distribution',d,'地区储能规模怎样落实到各站','逐站分组横条图')
    sid=next(s for s,n in names.items() if n=='兴塘变');j=list(inputs['pizhou']['stations']).index(sid);rows=[]
    for lab in ['刚性','弹性']:
        u=np.array(fixed['pizhou',lab][2035]['units'])[j];rows.append({'方案':lab,'总容量_MVA':u.sum(),'最大单台_MVA':u.max(),'剩余有功能力_MW':.95*(u.sum()-u.max())})
    d=pd.DataFrame(rows);fig,ax=plt.subplots(figsize=(7,3.6));ax.bar(d['方案'],d['剩余有功能力_MW'],color=[BLUE,GOLD],edgecolor='#333333');ax.set_ylabel('N-1剩余有功能力/MW')
    for i,v in enumerate(d['剩余有功能力_MW']):ax.text(i,v+1,f'{v:.2f}',ha='center')
    ax.set_ylim(0,d['剩余有功能力_MW'].max()*1.2);save(fig,'xingtang_reverse_capacity',d,'兴塘主变组合怎样对应故障剩余能力','两方案直接标值柱图')
    (REVIEW/'本轮图件及绘图数据.json').write_text(json.dumps(MAP,ensure_ascii=False,indent=2)+'\n')
    print('已更新案例图件',len(MAP))

if __name__=='__main__':main()
