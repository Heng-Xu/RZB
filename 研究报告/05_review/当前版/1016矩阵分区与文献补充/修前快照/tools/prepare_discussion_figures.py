"""从锁定有效样本生成讨论稿补充热图及逐点绘图数据。"""
from pathlib import Path
import pandas as pd,numpy as np,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager,FontProperties
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'研究报告/02图表/当前版';AUDIT=ROOT/'研究报告/05_review/当前版/1013讨论稿扩充'
fontManager.addfont('/usr/share/fonts/wps-office/FZFSK.TTF')
plt.rcParams.update({'font.family':['Times New Roman',FontProperties(fname='/usr/share/fonts/wps-office/FZFSK.TTF').get_name()],'axes.unicode_minus':False,'font.size':11})
d=pd.read_csv(ROOT/'研究报告/01研究推荐/当前版/参数联合情景_20261012/统一有效样本.csv')
eta='分布式电源装机渗透率';g='年最大净负荷平均增长率';a='电缆长度占比';r='初始转供率';h='储能支撑持续时间_h';k='负荷分散系数'
specs=[('discussion_cable_transfer',r,a,{eta:2.5,g:.04,h:4,k:1.1}),('discussion_hours_eta',eta,h,{g:.04,a:.1,r:.4,k:1.1}),('discussion_dispersion_transfer',r,k,{eta:1.5,g:.04,a:.1,h:4})]
records=[]
for name,x,y,fixed in specs:
 mask=np.ones(len(d),dtype=bool)
 for col,v in fixed.items():mask&=np.isclose(d[col],v)
 if name=='discussion_cable_transfer':mask&=(d[r]>=.5)
 if name=='discussion_dispersion_transfer':mask&=(d[r]>=.2)
 data=d[mask];assert not data.duplicated([x,y]).any()
 p=data.pivot(index=y,columns=x,values='容载比');assert p.notna().all().all()
 assert p.max().max()>p.min().min(),'无响应切片不得重复绘图'
 fig,ax=plt.subplots(figsize=(8,4.3));im=ax.imshow(p,origin='lower',aspect='auto',cmap='YlOrRd',vmin=1.36,vmax=3.15)
 fmt=lambda col,v:f'{v*100:.0f}%' if col in [a,r,g] else f'{v:.0f}' if col==h else f'{v:.2f}'
 ax.set_xticks(range(len(p.columns)),[fmt(x,v) for v in p.columns]);ax.set_yticks(range(len(p.index)),[fmt(y,v) for v in p.index])
 ax.set_xlabel(x);ax.set_ylabel('储能支撑持续时间/h' if y==h else y)
 for j in range(len(p)):
  for i in range(len(p.columns)):ax.text(i,j,f'{p.iloc[j,i]:.2f}',ha='center',va='center',fontsize=8)
 fig.colorbar(im,ax=ax,label='容载比');fig.tight_layout()
 for ext in ['png','pdf']:fig.savefig(OUT/(name+'.'+ext),dpi=240,bbox_inches='tight')
 plt.close(fig);data.to_csv(AUDIT/(name+'.csv'),index=False)
 records.append({'图件':name,'横轴':x,'纵轴':y,'固定条件':fixed,'节点数':len(data),'范围':[float(p.min().min()),float(p.max().max())]})
(AUDIT/'绘图来源.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print(records)
