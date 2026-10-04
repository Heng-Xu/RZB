"""使用本版完整精度数值及四年案例绘图，无历史报告目录依赖。"""
from pathlib import Path
import argparse,csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import FormatStrFormatter
HERE=Path(__file__).resolve().parent;R=HERE.parents[1];ASSETS=R/'02图表/当前版'
BASE=R/'01研究推荐/当前版/统一起点基准'
C=['#29465b','#9b4b39','#778f68'];REG={'pizhou':'邳州','city':'市区'};SC={'rigid':'刚性','elastic':'弹性'}
def rows(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def cash(y,life,om):
 return np.array([1/1.06**(y-2021),sum(om/1.06**(t-2021) for t in range(y+1,2042)),sum(1/1.06**(t-2021) for t in range(y+life,2041,life))])
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ASSETS);out=parser.parse_args().output;out.mkdir(parents=True,exist_ok=True)
 font_manager.fontManager.addfont('/usr/share/fonts/wps-office/FZFSK.TTF')
 for f in ['Times_New_Roman.ttf','Times_New_Roman_Bold.ttf']:font_manager.fontManager.addfont('/usr/share/fonts/truetype/msttcorefonts/'+f)
 family=font_manager.FontProperties(fname='/usr/share/fonts/wps-office/FZFSK.TTF').get_name()
 plt.rcParams.update({'font.family':['Times New Roman',family],'font.size':11,'axes.unicode_minus':False})
 d=json.loads((ASSETS/'图件原始数值.json').read_text())
 portfolio={(c,s):(rows(BASE/c/(s+'_years.csv')),rows(BASE/c/(s+'_stations.csv'))) for c in REG for s in SC}
 def save(name):
  for ax in plt.gcf().axes:ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
  plt.tight_layout();plt.savefig(out/(name+'.png'),dpi=300,bbox_inches='tight');plt.close()
 plt.figure(figsize=(6.5,3.6))
 for n,col in zip(REG.values(),C):plt.plot(range(2021,2026),[d['年度容量与负荷'][n][str(y)][1] for y in range(2021,2026)],'o-',label=n,color=col)
 plt.xticks(range(2021,2026));plt.ylabel('年网供最大负荷 / MW');plt.legend();plt.grid(alpha=.2);save('annual_load')
 fig,axes=plt.subplots(2,1,figsize=(6.7,4.8),sharex=True)
 for k,(rid,n) in enumerate([('QX-00005','邳州'),('QX-00007','市区')]):
  vals=np.array([d['光伏月末装机'][rid][str(y)] for y in range(2021,2026)]).flatten();x=np.arange(60);ax=axes[k]
  ax.plot(x[:25],vals[:25],ls='--',color=C[k],label='2021—2022年回推');ax.plot(x[24:],vals[24:],color=C[k],label='2023—2025年月末记录')
  ax.set_ylabel(n+'装机容量 / MW');ax.legend(fontsize=10);ax.grid(alpha=.2)
 axes[-1].set_xticks([0,12,24,36,48,59],['2021年1月','2022年1月','2023年1月','2024年1月','2025年1月','2025年12月']);save('pv_monthly')
 plt.figure(figsize=(6,3.6));plt.boxplot([d['设备最大负载率'][n] for n in REG.values()],tick_labels=list(REG.values()))
 plt.axhline(80,color=C[1],ls='--',lw=.8);plt.ylabel('逐台最大负载率 / %');save('loading_distribution')
 plt.figure(figsize=(6.5,3.8))
 for k,(c,n) in enumerate(REG.items()):
  vals=[x for x in portfolio[c,'elastic'][1] if x['year']=='2025']
  plt.scatter([float(x['forward_duration_h']) for x in vals],[float(x['reverse_duration_h']) for x in vals],label=n,alpha=.65,color=C[k])
 plt.xlabel('正向H95 / h');plt.ylabel('反向H95 / h');plt.legend();plt.grid(alpha=.2);save('duration_distribution')
 monthly=d['月度指标'];fig,axes=plt.subplots(1,2,figsize=(7,3.3))
 for ax,j,lab in [(axes[0],2,'容载比（月度分析）'),(axes[1],3,'主变负载率估计 / %')]:
  ax.scatter([x[1]*100 for x in monthly],[x[j] for x in monthly],color=C[0]);ax.set_xlabel('月电量渗透率 / %');ax.set_ylabel(lab)
  for x in monthly:ax.annotate(str(x[0]),(x[1]*100,x[j]),fontsize=7,xytext=(3,2),textcoords='offset points')
 save('monthly_correlation')
 plt.figure(figsize=(6.5,3.5));x=np.linspace(1,12,100);plt.plot(x,210.456262/np.minimum(1,2.15/x),color=C[0]);plt.xlabel('持续时间 / h');plt.ylabel('初始投资 / 万元 / 有效MW');plt.grid(alpha=.2);save('storage_effective_cost')
 pressure={}
 for c,n in REG.items():
  st=portfolio[c,'elastic'][1];pressure[c]=[[sum(float(x[key]) for x in st if int(x['year'])==y) for key in ['forward_mw','reverse_mw']] for y in range(2022,2026)]
  ids=[x['station'] for x in st if x['year']=='2025'];matrix=np.array([[max(float(x['forward_mw']),float(x['reverse_mw'])) for x in st if x['station']==sid] for sid in ids])
  fig,ax=plt.subplots(figsize=(6.4,5.8 if c=='pizhou' else 7.6));im=ax.imshow(matrix,aspect='auto',cmap='YlOrRd')
  ax.set_xticks(range(4),['第1年','第2年','第3年','第4年']);ax.set_yticks(range(len(ids)),ids,fontsize=9);fig.colorbar(im,ax=ax,label='净负荷最大绝对值 / MW');save(c+'_modeled_peaks')
 fig,axes=plt.subplots(1,2,figsize=(7,3.5))
 for k,(c,n) in enumerate(REG.items()):
  for ax,j in zip(axes,[0,1]):ax.plot(range(1,5),[x[j] for x in pressure[c]],'o-',label=n,color=C[k])
 for ax,lab in zip(axes,['最大正向净负荷合计 / MW','最大反向净负荷合计 / MW']):ax.set_ylabel(lab);ax.set_xticks(range(1,5));ax.legend();ax.grid(alpha=.2)
 save('annual_model_pressure')
 plt.figure(figsize=(6.6,3.8))
 for (c,s),(years,_) in portfolio.items():plt.plot(range(1,5),[float(x['clr']) for x in years],marker='o',ls='-' if s=='elastic' else '--',color=C[list(REG).index(c)],label=REG[c]+SC[s])
 plt.axhline(2,color='gray',lw=.8);plt.xticks(range(1,5));plt.xlabel('仿真年');plt.ylabel('容载比');plt.legend(ncol=2);plt.grid(alpha=.2);save('annual_clr')
 components=[];purchases=[];energies=[];labels=[]
 for (c,s),(years,_) in portfolio.items():
  parts=np.zeros((3,3))
  for y in years:
   for j,(kind,life,om) in enumerate([('transformer',20,.01),('storage',10,.03),('line',20,.01)]):parts[j]+=float(y[kind+'_capex_10k'])*cash(int(y['year']),life,om)
  components.append(parts.sum(axis=1));purchases.append(sum(float(y['new_transformer_purchase_mva']) for y in years));energies.append(float(years[-1]['installed_storage_energy_mwh']));labels.append(REG[c]+SC[s])
 plt.figure(figsize=(6.7,3.8));bottom=np.zeros(4)
 for j,lab in enumerate(['主变','储能','线路']):
  vals=[x[j] for x in components];plt.bar(labels,vals,bottom=bottom,label=lab,color=C[j]);bottom+=vals
 plt.ylabel('全寿命费用现值 / 万元');plt.legend();save('lifecycle_components')
 fig,axes=plt.subplots(1,2,figsize=(7,3.8));axes[0].bar(labels,purchases,color=C[0]);axes[0].set_ylabel('主变采购容量 / MVA')
 axes[1].bar(labels,energies,color=C[1]);axes[1].set_ylabel('第4年储能能量 / MWh')
 for ax in axes:ax.tick_params(axis='x',labelrotation=30)
 save('measure_comparison');print('当前版12幅数值图件已生成')
if __name__=='__main__':main()
